# -*- coding: utf-8 -*-
"""Batch 6 — Deep Diagnostic (18 savol, premium)."""
from pathlib import Path

BACKEND = Path("qadam/backend")
FE = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. deep_diagnostic_questions_v1.json — 18 savol
# ═══════════════════════════════════════════════════════════
(BACKEND / "data/deep_diagnostic_questions_v1.json").write_text(r'''{
  "version": "v1.0",
  "title": "Chuqur diagnostika",
  "duration_minutes": 7,
  "dimensions": {
    "goal": {
      "uz": "Maqsad",
      "questions": [
        {"id": "DD_Q01", "type": "likert", "text": "Keyingi 3 yilda aniq bir kasbda professional bo'lishni xohlayman.", "signals": {"persistence": 1.0}},
        {"id": "DD_Q02", "type": "likert", "text": "Tanlagan soham uzoq muddatli istiqbolga ega bo'lishi men uchun muhim.", "signals": {"business_sense": 1.0}}
      ]
    },
    "interest": {
      "uz": "Qiziqish",
      "questions": [
        {"id": "DD_Q03", "type": "likert", "text": "Murakkab texnikani yig'ish yoki tizimni sozlash menga zavq beradi.", "signals": {"technical_interest": 1.5, "problem_solving": 0.5}},
        {"id": "DD_Q04", "type": "likert", "text": "Ilmiy tadqiqot, tahlil qilish va naqsh topish menga qiziqarli.", "signals": {"analytical": 1.5, "math_logic": 0.5}}
      ]
    },
    "aptitude": {
      "uz": "Qobiliyat",
      "questions": [
        {"id": "DD_Q05", "type": "likert", "text": "Raqamlar va formulalar bilan ishlaganda o'zimni erkin his qilaman.", "signals": {"math_logic": 1.5, "analytical": 0.5}},
        {"id": "DD_Q06", "type": "likert", "text": "Noma'lum muammoga duch kelganda, uni qismlarga bo'lib yechaman.", "signals": {"problem_solving": 1.5, "logical_thinking": 0.8}}
      ]
    },
    "skills": {
      "uz": "Ko'nikmalar",
      "questions": [
        {"id": "DD_Q07", "type": "likert", "text": "Ko'p qismli tizimni (masalan, sayt tuzilmasi) tasavvur qila olaman.", "signals": {"system_design": 1.5, "logical_thinking": 0.5}},
        {"id": "DD_Q08", "type": "likert", "text": "Biror sohada amaliy ko'nikmaga egaman va uni yanada rivojlantirmoqchiman.", "signals": {"persistence": 1.0, "attention_to_detail": 0.5}}
      ]
    },
    "values": {
      "uz": "Qadriyatlar",
      "questions": [
        {"id": "DD_Q09", "type": "likert", "text": "Ishim jamiyatga real foyda keltirishi men uchun muhim.", "signals": {"user_empathy": 1.0, "business_sense": 0.3}},
        {"id": "DD_Q10", "type": "likert", "text": "Men erkin, nostandart ish uslubini afzal ko'raman.", "signals": {"innovation": 1.2, "creative_design": 0.5}}
      ]
    },
    "work_style": {
      "uz": "Ish uslubi",
      "questions": [
        {"id": "DD_Q11", "type": "likert", "text": "Yakka, chuqur fokusda ishlash menga mos.", "signals": {"system_design": 0.8, "analytical": 0.6}},
        {"id": "DD_Q12", "type": "likert", "text": "Tez o'zgaruvchan va yangi narsalarga to'la muhitda ishlashni yaxshi ko'raman.", "signals": {"innovation": 1.2, "persistence": 0.4}}
      ]
    },
    "constraints": {
      "uz": "Cheklovlar",
      "questions": [
        {"id": "DD_Q13", "type": "likert", "text": "Hozir o'rganish uchun jiddiy moliyaviy cheklovim bor.", "signals": {}, "constraint": "finance", "inverse": true},
        {"id": "DD_Q14", "type": "likert", "text": "Yaqin 6 oy ichida ishimni almashtirishim shart.", "signals": {"persistence": 0.5}, "constraint": "urgency"}
      ]
    },
    "resilience": {
      "uz": "Qat'iyat / fidoyilik",
      "questions": [
        {"id": "DD_Q15", "type": "likert", "text": "Maqsadga erishish uchun qiyinchilikka chidashga tayyorman.", "signals": {"persistence": 1.5}},
        {"id": "DD_Q16", "type": "likert", "text": "Uzoq muddatli mashaqqatli yo'lni bosib o'tishga tayyorman (masalan, 1-2 yil o'qish).", "signals": {"persistence": 1.5, "attention_to_detail": 0.3}}
      ]
    },
    "career_preferences": {
      "uz": "Kasbga moyillik",
      "questions": [
        {"id": "DD_Q17", "type": "likert", "text": "Rasm chizish, dizayn qilish yoki hikoya yozish — mening tabiiy ifodam.", "signals": {"creative_design": 1.5, "visual_logic": 0.8}},
        {"id": "DD_Q18", "type": "likert", "text": "Odamlarga yordam berish, o'qitish, ular bilan ishlash menga yoqadi.", "signals": {"user_empathy": 1.5, "business_sense": 0.3}}
      ]
    }
  }
}
''', encoding="utf-8")
print("[OK] deep_diagnostic_questions_v1.json (18 savol)")

# ═══════════════════════════════════════════════════════════
# 2. models_v2.py — Deep Diagnostic jadvallar
# ═══════════════════════════════════════════════════════════
MODELS = BACKEND / "models_v2.py"
m = MODELS.read_text(encoding="utf-8")

if "DeepDiagnosticSession" not in m:
    m += '''

# ═══════════════════════════════════════════════════════════
# DEEP DIAGNOSTIC — Premium (18 savol)
# ═══════════════════════════════════════════════════════════
class DeepDiagnosticSession(Base):
    __tablename__ = "deep_diagnostic_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    discovery_session_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="active")
    current_q_index: Mapped[int] = mapped_column(Integer, default=0)
    answers_count: Mapped[int] = mapped_column(Integer, default=0)
    question_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    started_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped["DateTime | None"] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DeepDiagnosticAnswer(Base):
    __tablename__ = "deep_diagnostic_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    answer_value: Mapped[int] = mapped_column(Integer)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_dd_session_question"),
    )


class DeepDiagnosticSignal(Base):
    __tablename__ = "deep_diagnostic_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    trust: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_state: Mapped[str] = mapped_column(String(24), default="unmeasured")
    coverage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "signal_key", name="uq_dd_session_signal"),
    )
'''
    MODELS.write_text(m, encoding="utf-8")
    print("[OK] models_v2.py — Deep Diagnostic jadvallar")
else:
    print("[SKIP] models_v2.py — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 3. data_loader.py — loader qo'shish
# ═══════════════════════════════════════════════════════════
DL = BACKEND / "data_loader.py"
dl = DL.read_text(encoding="utf-8")

if "load_deep_diagnostic" not in dl:
    dl += '''

def load_deep_diagnostic():
    return _load("deep_diagnostic_questions_v1.json")
'''
    DL.write_text(dl, encoding="utf-8")
    print("[OK] data_loader.py — deep diagnostic loader")

# ═══════════════════════════════════════════════════════════
# 4. deep_diagnostic_service.py
# ═══════════════════════════════════════════════════════════
(BACKEND / "services/deep_diagnostic_service.py").write_text(r'''"""Deep Diagnostic Service — 18 savol (premium)."""
from backend.data_loader import load_deep_diagnostic


def flatten_questions(data: dict) -> list:
    """Dimensions → flat savollar ro'yxati."""
    out = []
    for dim_key, dim in data["dimensions"].items():
        for q in dim["questions"]:
            out.append({**q, "_dim": dim_key, "_dim_uz": dim["uz"]})
    return out


def get_next_question(session_state: dict, questions: list):
    idx = session_state.get("current_q_index", 0)
    if idx >= len(questions):
        return None
    q = questions[idx]
    return {
        "id": q["id"],
        "type": q.get("type", "likert"),
        "text": q["text"],
        "index": idx,
        "total": len(questions),
        "dimension_uz": q.get("_dim_uz", ""),
    }


def compute_signals(answers: list, questions: list) -> dict:
    """Likert 1-5 → [0,10] shkalada, trust factor bilan."""
    from backend.engine.signals import SIGNAL_KEYS, LIKERT_TO_10, _classify_trust

    qmap = {q["id"]: q for q in questions}
    raw = {k: [] for k in SIGNAL_KEYS}

    for a in answers:
        q = qmap.get(a["question_id"])
        if not q:
            continue
        v = LIKERT_TO_10.get(int(a["answer_value"]), 5.0)
        for sig, w in (q.get("signals") or {}).items():
            if sig in raw:
                raw[sig].append(v * w)

    out = {}
    for k in SIGNAL_KEYS:
        contribs = raw[k]
        trust, state, count = _classify_trust(contribs)
        if state == "unmeasured" or not contribs:
            out[k] = {"value": None, "trust": 0.0, "evidence_state": "unmeasured", "coverage": 0}
        else:
            out[k] = {
                "value": round(sum(contribs) / len(contribs), 2),
                "trust": trust,
                "evidence_state": state,
                "coverage": count,
            }
    return out


def extract_evidence(answers: list, questions: list) -> list:
    """Har signal uchun dalil."""
    from backend.engine.signals import LIKERT_TO_10

    qmap = {q["id"]: q for q in questions}
    out = []
    for a in answers:
        q = qmap.get(a["id"]) or qmap.get(a["question_id"])
        if not q:
            continue
        v10 = LIKERT_TO_10.get(int(a["answer_value"]), 5.0)
        for sig, w in (q.get("signals") or {}).items():
            out.append({
                "signal_key": sig,
                "question_id": a["question_id"],
                "answer_id": "",
                "contribution": round(v10 * w, 3),
                "evidence_type": "direct",
            })
    return out


def extract_constraints(answers: list, questions: list) -> dict:
    """DD_Q13, DD_Q14 dan constraints."""
    qmap = {q["id"]: q for q in questions}
    constraints = {}

    dd_q13 = next((a for a in answers if a["question_id"] == "DD_Q13"), None)
    if dd_q13:
        # 1 (yo'q) → 5 (kuchli cheklov). Yuqoriroq = cheklov kuchli
        constraints["finance_level"] = dd_q13["answer_value"]

    dd_q14 = next((a for a in answers if a["question_id"] == "DD_Q14"), None)
    if dd_q14:
        constraints["urgency_level"] = dd_q14["answer_value"]

    return constraints


def merge_signals(discovery_signals: dict, deep_signals: dict) -> dict:
    """
    Discovery + Deep signallarini birlashtirish.
    Deep ustuvor (ko'proq coverage).
    """
    from backend.engine.signals import SIGNAL_KEYS

    merged = {}
    for k in SIGNAL_KEYS:
        d = discovery_signals.get(k) or {}
        deep = deep_signals.get(k) or {}

        deep_measured = deep.get("value") is not None
        disc_measured = d.get("value") is not None

        if deep_measured:
            # Deep bor — u ustuvor, lekin Disc'ni ham hisobga olamiz
            if disc_measured:
                # O'rtacha (deep 70%, disc 30%)
                merged[k] = {
                    "value": round(deep["value"] * 0.7 + d["value"] * 0.3, 2),
                    "trust": max(deep["trust"], d["trust"]),
                    "evidence_state": deep["evidence_state"],
                    "coverage": deep["coverage"] + d["coverage"],
                }
            else:
                merged[k] = deep
        elif disc_measured:
            merged[k] = d
        else:
            merged[k] = {"value": None, "trust": 0.0, "evidence_state": "unmeasured", "coverage": 0}

    return merged
''', encoding="utf-8")
print("[OK] services/deep_diagnostic_service.py")

# ═══════════════════════════════════════════════════════════
# 5. api/v1/deep_diagnostic.py
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1/deep_diagnostic.py").write_text(r'''"""Deep Diagnostic API v1 — premium."""
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

    # Discovery constraints (agar mavjud)
    base_constraints = {"time": "2_3h", "device": "laptop", "english": "b1"}

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
''', encoding="utf-8")
print("[OK] api/v1/deep_diagnostic.py")

# ═══════════════════════════════════════════════════════════
# 6. main.py — router
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "v1_dd_router" not in main:
    main = main.replace(
        "from backend.api.v1.career_intelligence import router as v1_career_intel_router",
        "from backend.api.v1.career_intelligence import router as v1_career_intel_router\n"
        "from backend.api.v1.deep_diagnostic import router as v1_dd_router",
    )
    main = main.replace(
        "app.include_router(v1_career_intel_router)",
        "app.include_router(v1_career_intel_router)\n"
        "app.include_router(v1_dd_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — deep diagnostic router")

# ═══════════════════════════════════════════════════════════
# 7. FRONTEND — /deep-diagnostic page
# ═══════════════════════════════════════════════════════════
(FE / "app/deep-diagnostic").mkdir(exist_ok=True)

(FE / "app/deep-diagnostic/page.tsx").write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { api, getInitData } from "@/lib/api";

const LIKERT = [
  { value: 1, label: "Umuman yo'q" },
  { value: 2, label: "Kam" },
  { value: 3, label: "O'rtacha" },
  { value: 4, label: "Ko'p" },
  { value: 5, label: "To'liq ha" },
];

export default function DeepDiagnosticPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState<any>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const discoverySessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("discovery_session_id")) || null
    : null;

  useEffect(() => {
    api.post("/api/v1/deep-diagnostic", {
      init_data: getInitData(),
      discovery_session_id: discoverySessionId,
    })
      .then((r) => {
        setSessionId(r.data.session_id);
        setQuestion(r.data.current_question);
        setLoading(false);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e.message);
        setLoading(false);
      });
  }, [discoverySessionId]);

  const handleNext = async () => {
    if (!sessionId || !question || selected === null) return;
    setSubmitting(true);
    try {
      const r = await api.post(`/api/v1/deep-diagnostic/${sessionId}/answers`, {
        init_data: getInitData(),
        question_id: question.id,
        answer_value: selected,
      });
      if (r.data.next_question) {
        setQuestion(r.data.next_question);
        setSelected(null);
      } else {
        // Complete
        const completeRes = await api.post(`/api/v1/deep-diagnostic/${sessionId}/complete`, {
          init_data: getInitData(),
        });
        sessionStorage.setItem("dd_result", JSON.stringify(completeRes.data));
        sessionStorage.setItem("dd_session_id", String(sessionId));
        router.push("/career-intelligence");
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!question) return <Loader />;

  const progress = ((question.index + 1) / question.total) * 100;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        <div className="pt-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            <span className="t-caption text-subtle">
              {question.dimension_uz || "Chuqur tahlil"}
            </span>
            <span className="t-caption text-subtle">
              {question.index + 1} / {question.total}
            </span>
          </div>
          <div className="h-px bg-[var(--color-border)] relative overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25 }}
            className="flex-1 flex flex-col"
          >
            <h2 className="t-title mb-8 mt-4">{question.text}</h2>
            <div className="flex flex-col gap-2.5 mb-6">
              {LIKERT.map((o, idx) => {
                const isSel = selected === o.value;
                return (
                  <motion.button
                    key={o.value}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03, duration: 0.2 }}
                    onClick={() => setSelected(o.value)}
                    className={`option-btn ${isSel ? "selected" : ""}`}
                  >
                    <span>{o.label}</span>
                    <span className="option-indicator">
                      {isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>

        <div className="pb-6">
          <button
            onClick={handleNext}
            disabled={selected === null || submitting}
            className="btn btn-primary"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
            ) : question.index === question.total - 1 ? (
              "Natijani ko'rish"
            ) : (
              "Keyingisi"
            )}
          </button>
        </div>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-6">
        <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />
      </div>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-8">
        <div className="card-clean border-[var(--color-danger)]/40">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/deep-diagnostic/page.tsx")

# ═══════════════════════════════════════════════════════════
# 8. /career-intelligence — haqiqiy natija
# ═══════════════════════════════════════════════════════════
(FE / "app/career-intelligence/page.tsx").write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, AlertCircle } from "lucide-react";

const SIGNAL_UZ: Record<string, string> = {
  logical_thinking: "Mantiqiy fikrlash",
  problem_solving: "Muammo hal qilish",
  technical_interest: "Texnikaga qiziqish",
  creative_design: "Ijodiy dizayn",
  visual_logic: "Vizual mantiq",
  user_empathy: "Empatiya",
  system_design: "Tizimli fikrlash",
  analytical: "Tahliliy fikrlash",
  persistence: "Qat'iyat",
  math_logic: "Matematik mantiq",
  attention_to_detail: "Detallarga e'tibor",
  business_sense: "Biznes hissi",
  innovation: "Innovatsiya",
};

export default function CareerIntelligencePage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("dd_result");
    if (!raw) {
      router.push("/deep-diagnostic");
      return;
    }
    try {
      setData(JSON.parse(raw));
    } catch {
      router.push("/deep-diagnostic");
    }
  }, [router]);

  if (!data) return null;

  const ranked = data.ranked || [];
  const signals = data.signals || {};

  // Top measured signals
  const measuredSignals = Object.entries(signals)
    .filter(([_, v]: any) => v.value !== null)
    .sort(([_, a]: any, [__, b]: any) => -(a.value * a.trust) + (b.value * b.trust))
    .slice(0, 6);

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <p className="t-caption text-primary mb-2">Chuqur tahlil</p>
          <h1 className="t-display mb-3">Sizning natijangiz</h1>
          <p className="t-small text-muted">
            {ranked.length} ta yo&apos;nalish tahlil qilindi. Ishonch:{" "}
            <span className="text-primary font-medium">{data.confidence}</span>
          </p>
        </motion.div>

        {/* Top signallar */}
        {measuredSignals.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
            <div className="space-y-2.5">
              {measuredSignals.map(([key, v]: any, i: number) => (
                <div key={key} className="flex items-center gap-3">
                  <span className="t-small flex-1 truncate">
                    {SIGNAL_UZ[key] ?? key}
                  </span>
                  <div className="w-24 h-1.5 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(v.value / 10) * 100}%` }}
                      transition={{ delay: 0.1 + i * 0.05, duration: 0.6 }}
                      className="h-full bg-primary"
                    />
                  </div>
                  <span className="t-caption text-subtle tabular-nums w-8 text-right">
                    {Math.round(v.value)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Ranked careers */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mb-6"
        >
          <p className="t-caption text-subtle mb-3">
            Sizga eng mos yo&apos;nalishlar
          </p>
          <div className="space-y-4">
            {ranked.map((c: any, i: number) => (
              <div key={c.career_id} className="card-clean">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <p className="t-caption text-primary mb-1">#{i + 1}</p>
                    <p className="t-heading">{c.career_uz}</p>
                    <p className="t-caption text-subtle">{c.cluster_uz}</p>
                  </div>
                  <div className="text-right shrink-0 pl-3">
                    <p className="t-metric text-primary leading-none">
                      {Math.round(c.fit)}
                      <span className="text-base">%</span>
                    </p>
                    <p className="t-caption text-subtle mt-1">Fit</p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
                  <span className="t-caption text-subtle">Readiness</span>
                  <span className="t-small text-success font-medium tabular-nums">
                    {Math.round(c.readiness)}%
                  </span>
                </div>

                {c.has_hard_barrier && (
                  <div className="flex items-start gap-2 mt-3 pt-3 border-t border-[var(--color-border)]">
                    <AlertCircle className="w-3.5 h-3.5 text-danger shrink-0 mt-0.5" />
                    <p className="t-caption text-danger">
                      Jiddiy to&apos;siq — yechim pastda
                    </p>
                  </div>
                )}

                {c.barriers?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-[var(--color-border)]">
                    <p className="t-caption text-subtle mb-2">To&apos;siqlar va yechim:</p>
                    {c.barriers.map((b: any, j: number) => (
                      <p key={j} className="t-caption text-muted mb-1">
                        • {b.path}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {ranked.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card-clean"
          >
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-subtle shrink-0 mt-0.5" />
              <div>
                <p className="t-heading mb-2">Yetarli dalil yo&apos;q</p>
                <p className="t-small text-muted">
                  Hozircha sizning javoblaringiz asosida yetarli mos yo&apos;nalish
                  topilmadi. Iltimos, savollarga samimiyroq javob bering.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/career-intelligence/page.tsx")

# ═══════════════════════════════════════════════════════════
# 9. /premium page — CTA'ni yangilash (deep-diagnostic)
# ═══════════════════════════════════════════════════════════
PREMIUM = FE / "app/premium/page.tsx"
p = PREMIUM.read_text(encoding="utf-8")

# "Botga qaytish" dan keyin "Boshlash" qo'shish
p = p.replace(
    '''                <button
                  onClick={() => {
                    const tg = (window as any).Telegram?.WebApp;
                    if (tg?.close) tg.close();
                  }}
                  className="btn btn-primary"
                >
                  Botga qaytish
                </button>''',
    '''                <button
                  onClick={() => router.push("/deep-diagnostic")}
                  className="btn btn-primary"
                >
                  Chuqur tahlilni boshlash
                </button>
                <button
                  onClick={() => {
                    const tg = (window as any).Telegram?.WebApp;
                    if (tg?.close) tg.close();
                  }}
                  className="btn btn-ghost mt-2"
                >
                  Botga qaytish
                </button>''',
)

# router import (allaqachon bor)
PREMIUM.write_text(p, encoding="utf-8")
print("[OK] app/premium — deep-diagnostic CTA")

# ═══════════════════════════════════════════════════════════
# 10. Tests
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch6_dd.py").write_text(r'''"""Batch 6 — Deep Diagnostic testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import (
    DeepDiagnosticSession, DeepDiagnosticAnswer, DeepDiagnosticSignal,
)
from data_loader import load_deep_diagnostic
from services.deep_diagnostic_service import (
    flatten_questions, get_next_question, compute_signals, merge_signals,
)


def test_dd_questions_count():
    data = load_deep_diagnostic()
    flat = flatten_questions(data)
    assert len(flat) == 18


def test_dd_dimensions():
    data = load_deep_diagnostic()
    assert len(data["dimensions"]) == 9


def test_dd_next_question():
    flat = flatten_questions(load_deep_diagnostic())
    nq = get_next_question({"current_q_index": 0}, flat)
    assert nq["id"] == "DD_Q01"
    assert nq["total"] == 18
    assert nq["dimension_uz"] == "Maqsad"


def test_dd_signals_computation():
    flat = flatten_questions(load_deep_diagnostic())
    answers = [
        {"question_id": "DD_Q03", "answer_value": 5},
    ]
    signals = compute_signals(answers, flat)
    ti = signals["technical_interest"]
    assert ti["value"] == 15.0  # 10 * 1.5
    assert ti["evidence_state"] == "insufficient"


def test_dd_merge_with_discovery():
    disc = {"analytical": {"value": 8.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    deep = {"analytical": {"value": 9.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    merged = merge_signals(disc, deep)
    # 9*0.7 + 8*0.3 = 6.3 + 2.4 = 8.7
    assert abs(merged["analytical"]["value"] - 8.7) < 0.1
    assert merged["analytical"]["coverage"] == 6


def test_dd_merge_only_discovery():
    disc = {"analytical": {"value": 8.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    deep = {"analytical": {"value": None, "trust": 0.0, "evidence_state": "unmeasured", "coverage": 0}}
    merged = merge_signals(disc, deep)
    assert merged["analytical"]["value"] == 8.0


def test_dd_models():
    cols = {c.name for c in DeepDiagnosticSession.__table__.columns}
    for f in ("user_id", "discovery_session_id", "status", "current_q_index"):
        assert f in cols

    cols = {c.name for c in DeepDiagnosticAnswer.__table__.columns}
    for f in ("session_id", "question_id", "answer_value"):
        assert f in cols
''', encoding="utf-8")
print("[OK] tests/test_batch6_dd.py (7 test)")

print()
print("=" * 60)
print("Batch 6 (Deep Diagnostic) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • deep_diagnostic_questions_v1.json (18 savol, 9 dimension)")
print("  • DeepDiagnosticSession/Answer/Signal jadvallari")
print("  • deep_diagnostic_service.py")
print("  • /api/v1/deep-diagnostic POST/GET/answers/complete")
print("  • /deep-diagnostic frontend page (18 savol)")
print("  • /career-intelligence — real natija (Fit/Readiness/Ranking)")
print("  • /premium → deep-diagnostic CTA")
print("  • 7 test")
print()
print("KEYINGI:")
print("  cd qadam")
print("  ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch6_dd.py -v")
print("  cd ..")
print("  git add -A")
print('  git commit -m "Batch 6: Deep Diagnostic (18 savol)"')
print("  git push")
print("  Render Manual Deploy (backend) + Vercel auto")