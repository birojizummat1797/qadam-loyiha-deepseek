"""
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
    from backend.engine.signals import (
        SIGNAL_KEYS, LIKERT_TO_10, aggregate_signal,
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
                    raw[sig].append((v10, w))
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
                raw[sig].append((v10, w))

    return {k: aggregate_signal(raw[k]) for k in SIGNAL_KEYS}


def build_preliminary_insight(signals: dict, answers: list, taxonomy: dict) -> dict:
    """
    Free Discovery natijasi — PRELIMINARY.
    Bu Premium Deep Diagnostic emas — yuzaki.
    """
    from backend.engine.ranking import rank_careers
    # taxonomy tashqaridan beriladi (async)

    # Constraints (Q11, Q12, Q13)
    constraints = _extract_constraints(answers)

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


# ═══════════════════════════════════════════════════════════
# EVIDENCE EXTRACTION — har signal uchun alohida yozuv
# ═══════════════════════════════════════════════════════════
def extract_evidence(answers: list, questions: list) -> list:
    """
    Returns: [
        {"signal_key", "question_id", "answer_id", "contribution", "evidence_type"}
    ]
    """
    from backend.engine.signals import LIKERT_TO_10

    qmap = {q["id"]: q for q in questions}
    out = []

    for a in answers:
        q = qmap.get(a["question_id"])
        if not q:
            continue

        # Likert
        if q.get("type") == "likert":
            v10 = LIKERT_TO_10.get(a["answer_value"], 5.0)
            for sig, w in q.get("signals", {}).items():
                out.append({
                    "signal_key": sig,
                    "question_id": a["question_id"],
                    "answer_id": a.get("answer_id", ""),
                    "contribution": round(v10 * w, 3),
                    "evidence_type": "direct",
                })
            continue

        # Choice
        opt = next((o for o in q.get("options", []) if o["id"] == a["answer_id"]), None)
        if not opt:
            continue
        v10 = LIKERT_TO_10.get(int(opt.get("value", 3)), 5.0)
        for sig, w in opt.get("signals", {}).items():
            out.append({
                "signal_key": sig,
                "question_id": a["question_id"],
                "answer_id": a["answer_id"],
                "contribution": round(v10 * w, 3),
                "evidence_type": "direct" if w >= 0.8 else "indirect",
            })

    return out
