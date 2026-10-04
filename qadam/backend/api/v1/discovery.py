"""Discovery API v1."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc

from backend.db import SessionLocal
from backend.models_v2 import (
    DiscoverySession, DiscoveryAnswer, DiscoverySignal, SignalEvidence,
)
from backend.auth import verify_init_data
from backend.entry_context import latest_web_entry
from backend.data_loader import load_discovery_questions
from backend.services.discovery_service import (
    get_next_question, compute_signals_from_discovery, build_preliminary_insight,
)
from backend.services.taxonomy_service import load_taxonomy_from_db

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery-v1"])


class StartSessionPayload(BaseModel):
    init_data: str


class AnswerPayload(BaseModel):
    init_data: str
    question_id: str
    answer_id: str
    answer_value: int  # 1-5


@router.post("")
async def start_session(payload: StartSessionPayload):
    """Yangi Discovery session."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        # Eski aktiv sessiyani yopish
        old = (await s.execute(
            select(DiscoverySession)
            .where(DiscoverySession.user_id == user["id"],
                   DiscoverySession.status == "active")
        )).scalars().all()
        for o in old:
            o.status = "abandoned"

        # Website entry (state/source/career) from the user's recent bot_start,
        # re-validated server-side. Missing or invalid → no context, flow unchanged.
        entry_context = await latest_web_entry(user["id"])
        session = DiscoverySession(
            user_id=user["id"],
            status="active",
            meta={"entry_context": entry_context} if entry_context else None,
        )
        s.add(session)
        await s.commit()
        await s.refresh(session)

    questions = load_discovery_questions()["questions"]
    first_q = get_next_question({"current_q_index": 0}, questions)

    return {
        "session_id": session.id,
        "status": "active",
        "total_questions": len(questions),
        "current_question": first_q,
        # Optional hint for the Mini App UI; None when the user did not come from the website.
        "entry_state": (entry_context or {}).get("state"),
    }


@router.get("/{session_id}")
async def get_session(session_id: int, init_data: str = Query(...)):
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

        answers = (await s.execute(
            select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == session_id)
        )).scalars().all()

    questions = load_discovery_questions()["questions"]
    next_q = get_next_question({"current_q_index": sess.current_q_index}, questions)

    return {
        "session_id": sess.id,
        "status": sess.status,
        "current_q_index": sess.current_q_index,
        "answers_count": sess.answers_count,
        "total_questions": len(questions),
        "current_question": next_q,
        "is_complete": sess.status == "completed",
    }


@router.post("/{session_id}/answers")
async def submit_answer(session_id: int, payload: AnswerPayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if payload.answer_value < 1 or payload.answer_value > 5:
        raise HTTPException(400, "answer_value 1-5 orasida bo'lishi kerak")

    questions = load_discovery_questions()["questions"]
    q_ids = {q["id"] for q in questions}
    if payload.question_id not in q_ids:
        raise HTTPException(400, "Noto'g'ri question_id")

    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")
        if sess.status != "active":
            raise HTTPException(400, "Session aktiv emas")

        # Eski javob bo'lsa yangilash
        existing = (await s.execute(
            select(DiscoveryAnswer).where(
                DiscoveryAnswer.session_id == session_id,
                DiscoveryAnswer.question_id == payload.question_id,
            )
        )).scalar_one_or_none()

        if existing:
            existing.answer_id = payload.answer_id
            existing.answer_value = payload.answer_value
        else:
            a = DiscoveryAnswer(
                session_id=session_id,
                question_id=payload.question_id,
                answer_id=payload.answer_id,
                answer_value=payload.answer_value,
            )
            s.add(a)
            sess.answers_count += 1

        # Keyingi savol index
        idx = next(
            (i for i, q in enumerate(questions) if q["id"] == payload.question_id),
            -1,
        )
        if idx >= 0:
            sess.current_q_index = idx + 1

        await s.commit()

    # Keyingi savol
    next_q = get_next_question({"current_q_index": sess.current_q_index}, questions)

    return {
        "ok": True,
        "next_question": next_q,
        "current_q_index": sess.current_q_index,
        "total_questions": len(questions),
    }


@router.post("/{session_id}/complete")
async def complete_session(session_id: int, payload: StartSessionPayload):
    """Discovery'ni yakunlash — signallarni hisoblash + preliminary insight."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

        answers = (await s.execute(
            select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == session_id)
        )).scalars().all()

    questions = load_discovery_questions()["questions"]
    if len(answers) < len(questions):
        raise HTTPException(400, f"Barcha savollarga javob bering ({len(answers)}/{len(questions)})")

    # Signal hisoblash
    answers_list = [
        {"question_id": a.question_id, "answer_id": a.answer_id, "answer_value": a.answer_value}
        for a in answers
    ]
    signals = compute_signals_from_discovery(answers_list, questions)

    # DB taxonomy
    taxonomy = await load_taxonomy_from_db()

    # Preliminary insight
    insight = build_preliminary_insight(signals, answers_list, taxonomy)

    # Constraints
    from backend.services.discovery_service import _extract_constraints
    constraints = _extract_constraints(answers_list)

    # Saqlash
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        sess.status = "completed"
        sess.completed_at = datetime.now(timezone.utc)
        # Merge, don't overwrite: keeps entry_context attached at session start.
        sess.meta = {
            **(sess.meta or {}),
            "confidence": insight.get("confidence"),
            "constraints": constraints,
        }

        # Signallarni saqlash
        for k, v in signals.items():
            sig = DiscoverySignal(
                session_id=session_id,
                signal_key=k,
                value=v["value"],
                trust=v["trust"],
                evidence_state=v["evidence_state"],
                coverage=v["coverage"],
            )
            s.add(sig)

        # Evidence yozuvlarini saqlash
        from backend.services.discovery_service import extract_evidence
        evidences = extract_evidence(answers_list, questions)
        for ev in evidences:
            e = SignalEvidence(
                session_id=session_id,
                session_type="discovery",
                signal_key=ev["signal_key"],
                question_id=ev["question_id"],
                answer_id=ev["answer_id"],
                contribution=ev["contribution"],
                evidence_type=ev["evidence_type"],
            )
            s.add(e)

        await s.commit()

    return {
        "session_id": session_id,
        "signals": signals,
        "insight": insight,
    }
