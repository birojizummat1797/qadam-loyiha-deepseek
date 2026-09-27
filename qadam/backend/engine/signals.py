"""
Signal Engine — PM spec (PHASE G).

Qoidalar:
- Likert 1-5 → value [0, 10] shkalada
- Trust Factor: measured=1.0, insufficient=0.6, conflicting=0.4
- Unmeasured signallar hisobga OLINMAYDI (0 emas!)
- Har bir signal uchun: value, trust, coverage (n ta answer), confidence
"""

LIKERT_TO_10 = {
    1: 0.0,
    2: 2.5,
    3: 5.0,
    4: 7.5,
    5: 10.0,
}

SIGNAL_KEYS = [
    "logical_thinking", "problem_solving", "technical_interest",
    "creative_design", "visual_logic", "user_empathy",
    "system_design", "analytical", "persistence", "math_logic",
    "attention_to_detail", "business_sense", "innovation",
]

# Trust Factor chegaralari
TRUST_MEASURED = 1.0
TRUST_INSUFFICIENT = 0.6
TRUST_CONFLICTING = 0.4
CONFLICT_STD_THRESHOLD = 3.0   # [0,10] shkalada std threshold
MIN_MEASURED_ANSWERS = 3        # measured bo'lish uchun kamida


def _collect_all_questions(questions):
    out = []
    for q in questions.get("stage_1", {}).get("questions", []):
        out.append(q)
    for dim in questions.get("stage_2", {}).get("dimensions", {}).values():
        out.extend(dim.get("questions", []))
    return out


def _classify_trust(contributions):
    """
    Har bir answer'dan kelgan normalized qiymatlar ro'yxati.
    - coverage: nechta javob keldi
    - std: qanchalik ziddiyatli
    """
    n = len(contributions)
    if n == 0:
        return None, "unmeasured", 0
    if n < MIN_MEASURED_ANSWERS:
        return TRUST_INSUFFICIENT, "insufficient", n

    # Std Dev hisoblash
    mean = sum(contributions) / n
    variance = sum((x - mean) ** 2 for x in contributions) / n
    std = variance ** 0.5

    if std > CONFLICT_STD_THRESHOLD:
        return TRUST_CONFLICTING, "conflicting", n
    return TRUST_MEASURED, "measured", n


def signals_from_answers(answers, questions):
    """
    Returns: {
        signal_key: {
            "value": float [0,10] | None,   # None = unmeasured
            "trust": float,                  # 0.0 - 1.0
            "evidence_state": str,           # measured|insufficient|conflicting|unmeasured
            "coverage": int,                 # measured answers soni
            "contributions": list[float],    # har answer'dan [0,10]
        }
    }
    """
    # Signal uchun xom qiymatlar
    raw = {k: [] for k in SIGNAL_KEYS}

    for q in _collect_all_questions(questions):
        qid = q["id"]
        if qid not in answers:
            continue
        a = answers[qid]
        if a is None:
            continue

        maps = q.get("maps_to", {}) or {}
        signal = maps.get("signal")
        if not signal or signal not in raw:
            continue

        w = float(maps.get("weight", 1.0))

        # Likert: 1-5 → [0, 10]
        if isinstance(a, (int, float)) and 1 <= int(a) <= 5:
            v = LIKERT_TO_10[int(a)]
        else:
            # Choice savol — neytral 5.0
            v = 5.0

        # Weighted contribution (weight bilan ko'paytirilgan)
        raw[signal].append(v * w)

    out = {}
    for k in SIGNAL_KEYS:
        contribs = raw[k]
        trust, state, count = _classify_trust(contribs)

        if state == "unmeasured" or not contribs:
            out[k] = {
                "value": None,
                "trust": 0.0,
                "evidence_state": "unmeasured",
                "coverage": 0,
                "contributions": [],
            }
            continue

        # Weighted average → [0, 10] shkalada
        avg = sum(contribs) / len(contribs)

        out[k] = {
            "value": round(avg, 2),
            "trust": trust,
            "evidence_state": state,
            "coverage": count,
            "contributions": [round(c, 2) for c in contribs],
        }

    return out
