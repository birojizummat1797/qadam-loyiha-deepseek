# -*- coding: utf-8 -*-
"""Batch 2 — Discovery: 12-13 savol, session, preliminary insight."""
from pathlib import Path

BACKEND = Path("qadam/backend")

# ═══════════════════════════════════════════════════════════
# 1. models_v2.py — Discovery jadvallar qo'shish
# ═══════════════════════════════════════════════════════════
MODELS = BACKEND / "models_v2.py"
m = MODELS.read_text(encoding="utf-8")

if "DiscoverySession" not in m:
    m += '''

# ═══════════════════════════════════════════════════════════
# DISCOVERY — Free bosqich (12-13 savol)
# ═══════════════════════════════════════════════════════════
class DiscoverySession(Base):
    """Free Discovery session."""
    __tablename__ = "discovery_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    status: Mapped[str] = mapped_column(String(16), default="active")
    # active | completed | abandoned
    current_q_index: Mapped[int] = mapped_column(Integer, default=0)
    answers_count: Mapped[int] = mapped_column(Integer, default=0)
    question_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    signal_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    started_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped["DateTime | None"] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DiscoveryAnswer(Base):
    """Har savol javobi."""
    __tablename__ = "discovery_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    answer_id: Mapped[str] = mapped_column(String(64))
    answer_value: Mapped[int] = mapped_column(Integer)  # 1-5 likert yoki binary
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_session_question"),
    )


class DiscoverySignal(Base):
    """Discovery sessiyasidan olingan signallar (evidence state)."""
    __tablename__ = "discovery_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)  # [0, 10] | None
    trust: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_state: Mapped[str] = mapped_column(String(24), default="unmeasured")
    coverage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "signal_key", name="uq_session_signal_disc"),
    )
'''
    MODELS.write_text(m, encoding="utf-8")
    print("[OK] models_v2.py — Discovery jadvallar")
else:
    print("[SKIP] models_v2.py — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 2. discovery_questions_v1.json — 13 savol
# ═══════════════════════════════════════════════════════════
(BACKEND / "data/discovery_questions_v1.json").write_text(r'''{
  "version": "v1.0",
  "title": "Free Discovery",
  "duration_minutes": 3,
  "questions": [
    {
      "id": "DISC_Q01",
      "type": "single_choice",
      "text": "Hozir hayotingizning qaysi bosqichidasiz?",
      "options": [
        {"id": "DISC_Q01_A01", "label": "Maktab / litsey bitiruvchisi", "value": 3, "signals": {}},
        {"id": "DISC_Q01_A02", "label": "Talaba", "value": 3, "signals": {}},
        {"id": "DISC_Q01_A03", "label": "Ishlayapman", "value": 3, "signals": {}},
        {"id": "DISC_Q01_A04", "label": "Kasbni o'zgartirmoqchiman", "value": 3, "signals": {}},
        {"id": "DISC_Q01_A05", "label": "Ishsizman", "value": 3, "signals": {}}
      ]
    },
    {
      "id": "DISC_Q02",
      "type": "single_choice",
      "text": "Sizni eng ko'p nima qiziqtiradi?",
      "options": [
        {"id": "DISC_Q02_A01", "label": "Texnika va texnologiya", "value": 4,
         "signals": {"technical_interest": 1.5, "logical_thinking": 0.8}},
        {"id": "DISC_Q02_A02", "label": "Ijod, dizayn, san'at", "value": 4,
         "signals": {"creative_design": 1.5, "visual_logic": 0.8}},
        {"id": "DISC_Q02_A03", "label": "Odamlar bilan ishlash", "value": 4,
         "signals": {"user_empathy": 1.5, "business_sense": 0.5}},
        {"id": "DISC_Q02_A04", "label": "Tahlil, raqamlar, tadqiqot", "value": 4,
         "signals": {"analytical": 1.5, "math_logic": 0.8}},
        {"id": "DISC_Q02_A05", "label": "Biznes, savdo, boshqarish", "value": 4,
         "signals": {"business_sense": 1.5, "persistence": 0.5}},
        {"id": "DISC_Q02_A06", "label": "Hali aniq emas", "value": 2, "signals": {}}
      ]
    },
    {
      "id": "DISC_Q03",
      "type": "likert",
      "text": "Murakkab muammolarni yechish menga zavq beradi.",
      "signals": {"problem_solving": 1.0, "logical_thinking": 0.8}
    },
    {
      "id": "DISC_Q04",
      "type": "likert",
      "text": "Yangi narsani o'zim mustaqil o'rganishga odatlanganman.",
      "signals": {"persistence": 1.0}
    },
    {
      "id": "DISC_Q05",
      "type": "likert",
      "text": "Chizish, dizayn qilish yoki hikoya yozish — mening tabiiy ifodam.",
      "signals": {"creative_design": 1.0, "visual_logic": 0.5}
    },
    {
      "id": "DISC_Q06",
      "type": "likert",
      "text": "Raqamlar, statistikalar va formulalar bilan ishlash menga oson.",
      "signals": {"math_logic": 1.0, "analytical": 0.8}
    },
    {
      "id": "DISC_Q07",
      "type": "likert",
      "text": "Odamlarning muammolarini tinglab, ularga yordam berish yoqadi.",
      "signals": {"user_empathy": 1.0, "business_sense": 0.3}
    },
    {
      "id": "DISC_Q08",
      "type": "likert",
      "text": "Ko'p qismli tizimlarni (masalan, sayt tuzilmasi, jarayon) tasavvur qila olaman.",
      "signals": {"system_design": 1.0, "logical_thinking": 0.5}
    },
    {
      "id": "DISC_Q09",
      "type": "single_choice",
      "text": "Sizga mos ish muhiti qanday?",
      "options": [
        {"id": "DISC_Q09_A01", "label": "Yakka, tinch, chuqur fokus", "value": 3,
         "signals": {"system_design": 1.0, "analytical": 0.5}},
        {"id": "DISC_Q09_A02", "label": "Kichik jamoa, muloqot", "value": 3,
         "signals": {"user_empathy": 0.8}},
        {"id": "DISC_Q09_A03", "label": "Katta jamoa, dinamik", "value": 3,
         "signals": {"business_sense": 0.8, "persistence": 0.5}},
        {"id": "DISC_Q09_A04", "label": "Erkin, moslashuvchan", "value": 3,
         "signals": {"innovation": 1.0}}
      ]
    },
    {
      "id": "DISC_Q10",
      "type": "single_choice",
      "text": "Siz uchun ishda eng muhim narsa?",
      "options": [
        {"id": "DISC_Q10_A01", "label": "Yuqori daromad", "value": 3,
         "signals": {"business_sense": 1.0}},
        {"id": "DISC_Q10_A02", "label": "Barqarorlik", "value": 3,
         "signals": {"persistence": 0.8, "attention_to_detail": 0.5}},
        {"id": "DISC_Q10_A03", "label": "O'sish va rivojlanish", "value": 3,
         "signals": {"persistence": 0.8, "innovation": 0.5}},
        {"id": "DISC_Q10_A04", "label": "Erkinlik va mustaqillik", "value": 3,
         "signals": {"innovation": 0.8}},
        {"id": "DISC_Q10_A05", "label": "Jamiyatga foyda", "value": 3,
         "signals": {"user_empathy": 0.8}},
        {"id": "DISC_Q10_A06", "label": "Ijodiy o'zini ifoda", "value": 3,
         "signals": {"creative_design": 0.8}}
      ]
    },
    {
      "id": "DISC_Q11",
      "type": "single_choice",
      "text": "Kuniga qancha vaqt o'rganishga tayyorsiz?",
      "options": [
        {"id": "DISC_Q11_A01", "label": "1 soatdan kam", "value": 1, "signals": {}},
        {"id": "DISC_Q11_A02", "label": "1 soat", "value": 2, "signals": {}},
        {"id": "DISC_Q11_A03", "label": "2-3 soat", "value": 3, "signals": {}},
        {"id": "DISC_Q11_A04", "label": "4+ soat", "value": 4, "signals": {}},
        {"id": "DISC_Q11_A05", "label": "To'liq kun", "value": 5, "signals": {}}
      ]
    },
    {
      "id": "DISC_Q12",
      "type": "single_choice",
      "text": "Qaysi qurilmadan foydalanasiz?",
      "options": [
        {"id": "DISC_Q12_A01", "label": "Noutbuk / kompyuter", "value": 4, "signals": {}},
        {"id": "DISC_Q12_A02", "label": "Faqat smartfon", "value": 2, "signals": {}},
        {"id": "DISC_Q12_A03", "label": "Ikkalasi ham", "value": 4, "signals": {}},
        {"id": "DISC_Q12_A04", "label": "Hozircha yo'q", "value": 1, "signals": {}}
      ]
    },
    {
      "id": "DISC_Q13",
      "type": "single_choice",
      "text": "Ingliz tilingizni qanday baholaysiz?",
      "options": [
        {"id": "DISC_Q13_A01", "label": "Bilmayman", "value": 1, "signals": {}},
        {"id": "DISC_Q13_A02", "label": "A1-A2", "value": 2, "signals": {}},
        {"id": "DISC_Q13_A03", "label": "B1", "value": 3, "signals": {}},
        {"id": "DISC_Q13_A04", "label": "B2", "value": 4, "signals": {}},
        {"id": "DISC_Q13_A05", "label": "C1+", "value": 5, "signals": {}}
      ]
    }
  ]
}
''', encoding="utf-8")
print("[OK] backend/data/discovery_questions_v1.json (13 savol)")

# ═══════════════════════════════════════════════════════════
# 3. data_loader.py — discovery loader
# ═══════════════════════════════════════════════════════════
DL = BACKEND / "data_loader.py"
dl = DL.read_text(encoding="utf-8")

if "load_discovery_questions" not in dl:
    dl += '''

def load_discovery_questions():
    return _load("discovery_questions_v1.json")
'''
    DL.write_text(dl, encoding="utf-8")
    print("[OK] data_loader.py — discovery loader")

# ═══════════════════════════════════════════════════════════
# 4. Discovery service
# ═══════════════════════════════════════════════════════════
(BACKEND / "services/discovery_service.py").write_text(r'''"""
Discovery Service — Free bosqich.

Oqim:
1. Session yaratish
2. Savol-javob (answer_id)
3. Signals hisoblash
4. Preliminary insight
"""
from backend.data_loader import load_discovery_questions


def get_next_question(session_state: dict, questions: list) -> dict | None:
    """Keyingi savol (index bo'yicha)."""
    idx = session_state.get("current_q_index", 0)
    if idx >= len(questions):
        return None
    q = questions[idx]
    # answer_id'ni yashirish, faqat option_id va label
    return {
        "id": q["id"],
        "type": q.get("type", "single_choice"),
        "text": q["text"],
        "index": idx,
        "total": len(questions),
        "options": [
            {"id": o["id"], "label": o["label"]}
            for o in q.get("options", [])
        ] if q.get("options") else None,
    }


def compute_signals_from_discovery(answers: list, questions: list) -> dict:
    """
    answers: [{"question_id": "DISC_Q02", "answer_id": "DISC_Q02_A01", "answer_value": 4}, ...]
    Returns: {signal_key: {value, trust, evidence_state, coverage}}
    """
    from engine.signals import (
        SIGNAL_KEYS, LIKERT_TO_10, _classify_trust,
    )

    qmap = {q["id"]: q for q in questions}
    raw = {k: [] for k in SIGNAL_KEYS}

    for a in answers:
        q = qmap.get(a["question_id"])
        if not q:
            continue

        # Likert savol
        if q.get("type") == "likert":
            v10 = LIKERT_TO_10.get(a["answer_value"], 5.0)
            for sig, w in q.get("signals", {}).items():
                if sig in raw:
                    raw[sig].append(v10 * w)
            continue

        # Choice savol
        opt = next(
            (o for o in q.get("options", []) if o["id"] == a["answer_id"]),
            None,
        )
        if not opt:
            continue
        # Choice value → [0, 10]: 1→0, 5→10
        cv = opt.get("value", 3)
        v10 = LIKERT_TO_10.get(int(cv), 5.0)
        for sig, w in opt.get("signals", {}).items():
            if sig in raw:
                raw[sig].append(v10 * w)

    out = {}
    for k in SIGNAL_KEYS:
        contribs = raw[k]
        trust, state, count = _classify_trust(contribs)
        if state == "unmeasured" or not contribs:
            out[k] = {
                "value": None, "trust": 0.0,
                "evidence_state": "unmeasured", "coverage": 0,
            }
        else:
            out[k] = {
                "value": round(sum(contribs) / len(contribs), 2),
                "trust": trust,
                "evidence_state": state,
                "coverage": count,
            }
    return out


def build_preliminary_insight(signals: dict, answers: list) -> dict:
    """
    Free Discovery natijasi — PRELIMINARY.
    Bu Premium Deep Diagnostic emas — yuzaki.
    """
    from engine.ranking import rank_careers
    from data_loader import load_taxonomy

    # Constraints (Q11, Q12, Q13)
    constraints = _extract_constraints(answers)
    taxonomy = load_taxonomy()

    try:
        ranking = rank_careers(
            signals=signals,
            taxonomy=taxonomy,
            constraints=constraints,
            top_n=3,
        )
    except Exception as e:
        return {"error": str(e)[:200], "confidence": "none"}

    # Top signallar (faqat measured)
    top_signals = sorted(
        [
            {"key": k, "value": v["value"], "trust": v["trust"]}
            for k, v in signals.items()
            if v.get("value") is not None
        ],
        key=lambda x: -(x["value"] * x["trust"]),
    )[:5]

    # Development areas (unmeasured yoki low value)
    dev_areas = [
        k for k, v in signals.items()
        if v.get("value") is None or v["value"] < 4.0
    ][:3]

    return {
        "signals_top": top_signals,
        "development_areas": dev_areas,
        "pathways": ranking["ranked"],
        "confidence": ranking["confidence"],
        "disclaimer": (
            "Bu dastlabki tahlil — 13 savolga asoslangan. "
            "Chuqur tahlil 18 qo'shimcha savol bilan aniqroq natija beradi."
        ),
    }


def _extract_constraints(answers: list) -> dict:
    """Q11, Q12, Q13 dan constraints."""
    qmap = {a["question_id"]: a for a in answers}

    time_map = {
        "DISC_Q11_A01": "lt_1h", "DISC_Q11_A02": "1h",
        "DISC_Q11_A03": "2_3h", "DISC_Q11_A04": "4h_plus",
        "DISC_Q11_A05": "full_time",
    }
    device_map = {
        "DISC_Q12_A01": "laptop", "DISC_Q12_A02": "smartphone_only",
        "DISC_Q12_A03": "both", "DISC_Q12_A04": "none",
    }
    english_map = {
        "DISC_Q13_A01": "none", "DISC_Q13_A02": "a2",
        "DISC_Q13_A03": "b1", "DISC_Q13_A04": "b2",
        "DISC_Q13_A05": "c1",
    }

    return {
        "time": time_map.get(qmap.get("DISC_Q11", {}).get("answer_id"), "2_3h"),
        "device": device_map.get(qmap.get("DISC_Q12", {}).get("answer_id"), "laptop"),
        "english": english_map.get(qmap.get("DISC_Q13", {}).get("answer_id"), "b1"),
    }
''', encoding="utf-8")
print("[OK] services/discovery_service.py")

# ═══════════════════════════════════════════════════════════
# 5. API — discovery
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1/discovery.py").write_text(r'''"""Discovery API v1."""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc

from backend.db import SessionLocal
from backend.models_v2 import (
    DiscoverySession, DiscoveryAnswer, DiscoverySignal,
)
from backend.auth import verify_init_data
from backend.data_loader import load_discovery_questions
from backend.services.discovery_service import (
    get_next_question, compute_signals_from_discovery, build_preliminary_insight,
)

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

        session = DiscoverySession(user_id=user["id"], status="active")
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

    # Preliminary insight
    insight = build_preliminary_insight(signals, answers_list)

    # Saqlash
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        sess.status = "completed"
        sess.completed_at = datetime.now(timezone.utc)
        sess.meta = {"confidence": insight.get("confidence")}

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

        await s.commit()

    return {
        "session_id": session_id,
        "signals": signals,
        "insight": insight,
    }
''', encoding="utf-8")
print("[OK] api/v1/discovery.py")

# ═══════════════════════════════════════════════════════════
# 6. main.py — discovery router
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "v1_discovery_router" not in main:
    main = main.replace(
        "from backend.api.v1.entitlements import router as v1_entitlements_router",
        "from backend.api.v1.entitlements import router as v1_entitlements_router\n"
        "from backend.api.v1.discovery import router as v1_discovery_router",
    )
    main = main.replace(
        "app.include_router(v1_entitlements_router)",
        "app.include_router(v1_entitlements_router)\n"
        "app.include_router(v1_discovery_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — discovery router")

# ═══════════════════════════════════════════════════════════
# 7. Tests
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch2_discovery.py").write_text(r'''"""Batch 2 — Discovery testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import DiscoverySession, DiscoveryAnswer, DiscoverySignal
from data_loader import load_discovery_questions
from services.discovery_service import (
    get_next_question, compute_signals_from_discovery, _extract_constraints,
)


def test_questions_count():
    q = load_discovery_questions()
    assert len(q["questions"]) == 13


def test_next_question():
    questions = load_discovery_questions()["questions"]
    nq = get_next_question({"current_q_index": 0}, questions)
    assert nq is not None
    assert nq["id"] == "DISC_Q01"
    assert nq["total"] == 13
    assert nq["index"] == 0


def test_next_question_at_end():
    questions = load_discovery_questions()["questions"]
    nq = get_next_question({"current_q_index": 13}, questions)
    assert nq is None


def test_signals_computation_choice():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q02", "answer_id": "DISC_Q02_A01", "answer_value": 4},
    ]
    signals = compute_signals_from_discovery(answers, questions)
    # technical_interest = 1.5 * 7.5 = 11.25 → weighted avg 11.25
    ti = signals["technical_interest"]
    assert ti["value"] is not None
    assert ti["value"] == 11.25 or ti["value"] > 8
    assert ti["coverage"] == 1
    assert ti["evidence_state"] == "insufficient"


def test_signals_likert():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q03", "answer_id": "x", "answer_value": 5},
    ]
    signals = compute_signals_from_discovery(answers, questions)
    ps = signals["problem_solving"]
    assert ps["value"] == 10.0  # 10 * 1.0
    assert ps["evidence_state"] == "insufficient"


def test_constraints_extraction():
    answers = [
        {"question_id": "DISC_Q11", "answer_id": "DISC_Q11_A03", "answer_value": 3},
        {"question_id": "DISC_Q12", "answer_id": "DISC_Q12_A01", "answer_value": 4},
        {"question_id": "DISC_Q13", "answer_id": "DISC_Q13_A03", "answer_value": 3},
    ]
    c = _extract_constraints(answers)
    assert c["time"] == "2_3h"
    assert c["device"] == "laptop"
    assert c["english"] == "b1"


def test_model_columns_discovery():
    cols = {c.name for c in DiscoverySession.__table__.columns}
    for f in ("user_id", "status", "current_q_index", "question_version"):
        assert f in cols

    cols = {c.name for c in DiscoveryAnswer.__table__.columns}
    for f in ("session_id", "question_id", "answer_id", "answer_value"):
        assert f in cols

    cols = {c.name for c in DiscoverySignal.__table__.columns}
    for f in ("session_id", "signal_key", "value", "trust", "evidence_state"):
        assert f in cols
''', encoding="utf-8")
print("[OK] tests/test_batch2_discovery.py (7 test)")

print()
print("=" * 60)
print("Batch 2 (Discovery) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • DiscoverySession, DiscoveryAnswer, DiscoverySignal (tables)")
print("  • discovery_questions_v1.json (13 savol)")
print("  • discovery_service.py (signals + preliminary insight)")
print("  • /api/v1/discovery POST (start)")
print("  • /api/v1/discovery/{id} GET")
print("  • /api/v1/discovery/{id}/answers POST")
print("  • /api/v1/discovery/{id}/complete POST")
print("  • 7 test")
print()
print("KEYINGI:")
print("  cd qadam")
print("  ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch2_discovery.py -v")
print("  cd ..")
print("  git add -A")
print('  git commit -m "Batch 2: Discovery (13 savol, signals, insight)"')
print("  git push")
print("  Render Manual Deploy")