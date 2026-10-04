"""Deep Diagnostic API v1 — premium."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models_v2 import (
    DeepDiagnosticSession, DeepDiagnosticAnswer, DeepDiagnosticSignal,
    DiscoverySession, DiscoverySignal, SignalEvidence,
)
from backend.auth import verify_init_data
from backend.services.entitlement_service import has_active_entitlement
from backend.services.taxonomy_service import load_taxonomy_from_db
from backend.services.deep_diagnostic_service import (
    flatten_questions, get_next_question, compute_signals as dd_compute,
    extract_evidence as dd_extract_ev, extract_constraints as dd_extract_cons,
    merge_signals,
)
from backend.data_loader import load_deep_diagnostic
from backend.engine.ranking import rank_careers

router = APIRouter(prefix="/api/v1/deep-diagnostic", tags=["deep-diagnostic-v1"])

PREMIUM_KEY = "premium_career_intelligence"


class StartPayload(BaseModel):
    init_data: str
    discovery_session_id: int | None = None


class AnswerPayload(BaseModel):
    init_data: str
    question_id: str
    answer_value: int


async def _require_premium(uid: int):
    from backend.services.age_gate import require_adult
    await require_adult(uid)
    ok = await has_active_entitlement(uid, PREMIUM_KEY)
    if not ok:
        raise HTTPException(402, "Premium kerak")


@router.post("")
async def start(payload: StartPayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    await _require_premium(user["id"])

    async with SessionLocal() as s:
        # Eski aktiv sessiyalarni yopish
        old = (await s.execute(
            select(DeepDiagnosticSession).where(
                DeepDiagnosticSession.user_id == user["id"],
                DeepDiagnosticSession.status == "active",
            )
        )).scalars().all()
        for o in old:
            o.status = "abandoned"

        sess = DeepDiagnosticSession(
            user_id=user["id"],
            discovery_session_id=payload.discovery_session_id,
            status="active",
        )
        s.add(sess)
        await s.commit()
        await s.refresh(sess)

    questions = flatten_questions(load_deep_diagnostic())
    first_q = get_next_question({"current_q_index": 0}, questions)

    return {
        "session_id": sess.id,
        "total_questions": len(questions),
        "current_question": first_q,
    }


@router.get("/{session_id}")
async def get_session(session_id: int, init_data: str = Query(...)):
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

    questions = flatten_questions(load_deep_diagnostic())
    nq = get_next_question({"current_q_index": sess.current_q_index}, questions)
    return {
        "session_id": sess.id,
        "status": sess.status,
        "current_q_index": sess.current_q_index,
        "total_questions": len(questions),
        "current_question": nq,
    }


@router.post("/{session_id}/answers")
async def submit_answer(session_id: int, payload: AnswerPayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if not (1 <= payload.answer_value <= 5):
        raise HTTPException(400, "answer_value 1-5 bo'lishi kerak")

    questions = flatten_questions(load_deep_diagnostic())
    q_ids = {q["id"] for q in questions}
    if payload.question_id not in q_ids:
        raise HTTPException(400, "Noto'g'ri question_id")

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")
        if sess.status != "active":
            raise HTTPException(400, "Session aktiv emas")

        existing = (await s.execute(
            select(DeepDiagnosticAnswer).where(
                DeepDiagnosticAnswer.session_id == session_id,
                DeepDiagnosticAnswer.question_id == payload.question_id,
            )
        )).scalar_one_or_none()

        if existing:
            existing.answer_value = payload.answer_value
        else:
            s.add(DeepDiagnosticAnswer(
                session_id=session_id,
                question_id=payload.question_id,
                answer_value=payload.answer_value,
            ))
            sess.answers_count += 1

        idx = next((i for i, q in enumerate(questions) if q["id"] == payload.question_id), -1)
        if idx >= 0:
            sess.current_q_index = idx + 1

        await s.commit()

    nq = get_next_question({"current_q_index": sess.current_q_index}, questions)
    return {
        "ok": True,
        "next_question": nq,
        "current_q_index": sess.current_q_index,
        "total_questions": len(questions),
    }


@router.post("/{session_id}/complete")
async def complete(session_id: int, payload: StartPayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

        dd_answers = (await s.execute(
            select(DeepDiagnosticAnswer).where(DeepDiagnosticAnswer.session_id == session_id)
        )).scalars().all()

        disc_answers_dict = {}
        disc_signals_dict = {}
        if sess.discovery_session_id:
            d_signals = (await s.execute(
                select(DiscoverySignal).where(DiscoverySignal.session_id == sess.discovery_session_id)
            )).scalars().all()
            disc_signals_dict = {
                r.signal_key: {"value": r.value, "trust": r.trust,
                               "evidence_state": r.evidence_state, "coverage": r.coverage}
                for r in d_signals
            }

    questions = flatten_questions(load_deep_diagnostic())
    if len(dd_answers) < len(questions):
        raise HTTPException(400, f"Barcha savollarga javob bering ({len(dd_answers)}/{len(questions)})")

    dd_answers_list = [
        {"question_id": a.question_id, "answer_value": a.answer_value}
        for a in dd_answers
    ]

    # Deep signals
    dd_signals = dd_compute(dd_answers_list, questions)

    # Merge
    merged = merge_signals(disc_signals_dict, dd_signals)

    # Constraints
    dd_constraints = dd_extract_cons(dd_answers_list, questions)

    # Discovery'dagi haqiqiy sharoit (default yo'q; noma'lum bo'lsa readiness = None)
    from backend.services.context_service import discovery_constraints
    base_constraints = await discovery_constraints(sess.discovery_session_id)

    # Ranking
    taxonomy = await load_taxonomy_from_db()
    ranking = rank_careers(
        signals=merged,
        taxonomy=taxonomy,
        constraints=base_constraints,
        top_n=5,
    )

    # Saqlash
    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        sess.status = "completed"
        sess.completed_at = datetime.now(timezone.utc)
        sess.meta = {
            "confidence": ranking["confidence"],
            "constraints": dd_constraints,
        }

        # Signallarni saqlash
        from sqlalchemy import delete as _del
        await s.execute(_del(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == session_id))

        for k, v in dd_signals.items():
            if v["evidence_state"] == "unmeasured":
                continue
            s.add(DeepDiagnosticSignal(
                session_id=session_id,
                signal_key=k,
                value=v["value"],
                trust=v["trust"],
                evidence_state=v["evidence_state"],
                coverage=v["coverage"],
            ))

        # Evidence
        evidences = dd_extract_ev(dd_answers_list, questions)
        for ev in evidences:
            s.add(SignalEvidence(
                session_id=session_id,
                session_type="deep",
                signal_key=ev["signal_key"],
                question_id=ev["question_id"],
                answer_id="",
                contribution=ev["contribution"],
                evidence_type="direct",
            ))

        await s.commit()

    return {
        "session_id": session_id,
        "signals": merged,
        "ranked": ranking["ranked"],
        "excluded": ranking["excluded"][:10],
        "confidence": ranking["confidence"],
        "constraints": base_constraints,
    }


@router.post("/{session_id}/pdf")
async def pdf(session_id: int, payload: StartPayload):
    """Action Document (PDF) for a completed deep diagnostic — the v1 flow's PDF.

    Rebuilt from stored signals and the user's own context (no hard-coded
    conditions, no salary, no percentages) and sent to the user via the bot.
    """
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    await _require_premium(user["id"])

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")
        if sess.status != "completed":
            raise HTTPException(400, "Diagnostika yakunlanmagan")
        deep_rows = (await s.execute(
            select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == session_id)
        )).scalars().all()
        disc_rows = []
        if sess.discovery_session_id:
            disc_rows = (await s.execute(
                select(DiscoverySignal).where(DiscoverySignal.session_id == sess.discovery_session_id)
            )).scalars().all()

    def rows(rs):
        return {r.signal_key: {"value": r.value, "trust": r.trust,
                               "evidence_state": r.evidence_state, "coverage": r.coverage} for r in rs}

    from backend.ai.personalizer import _fallback
    from backend.engine.roadmap import build_full_report
    from backend.pdf_report import generate_pdf
    from backend.services.context_service import discovery_constraints
    from backend.services.pdf_delivery import send_pdf

    signals = merge_signals(rows(disc_rows), rows(deep_rows))
    constraints = await discovery_constraints(sess.discovery_session_id)
    taxonomy = await load_taxonomy_from_db()
    ranking = rank_careers(signals=signals, taxonomy=taxonomy, constraints=constraints, top_n=5)
    if not ranking["ranked"]:
        raise HTTPException(422, "Yetarli ma'lumot yo'q")

    report = {
        "id": session_id,
        "profile": {},
        "roadmap": build_full_report(ranking["ranked"], constraints, taxonomy, signals),
        # Deterministic text: the PDF repeats nothing the user has not seen in the app.
        "ai": _fallback(ranking["ranked"]),
        "created_at": "",
    }
    pdf_bytes = generate_pdf(report)
    filename = f"QADAM-{session_id}.pdf"
    sent = await send_pdf(user, pdf_bytes, filename, ranking["ranked"][0]["career_uz"])
    return {"ok": True, "session_id": session_id, "sent_to_telegram": sent, "size_bytes": len(pdf_bytes)}
