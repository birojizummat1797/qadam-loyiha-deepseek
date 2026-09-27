"""Deep Diagnostic Service — 18 savol (premium)."""
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
        q = qmap.get(a.get("question_id") or a.get("id", ""))
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
