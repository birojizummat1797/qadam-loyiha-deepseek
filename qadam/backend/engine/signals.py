LIKERT = {1: 0.0, 2: 0.25, 3: 0.5, 4: 0.75, 5: 1.0}

SIGNAL_KEYS = [
    "logical_thinking", "problem_solving", "technical_interest",
    "creative_design", "visual_logic", "user_empathy",
    "system_design", "analytical", "persistence", "math_logic",
    "attention_to_detail", "business_sense", "innovation",
]


def _collect_all_questions(questions):
    out = []
    for q in questions.get("stage_1", {}).get("questions", []):
        out.append(q)
    for dim in questions.get("stage_2", {}).get("dimensions", {}).values():
        out.extend(dim.get("questions", []))
    return out


def signals_from_answers(answers, questions):
    buckets = {k: {"sum": 0.0, "weight_sum": 0.0, "n": 0} for k in SIGNAL_KEYS}

    for q in _collect_all_questions(questions):
        qid = q["id"]
        if qid not in answers:
            continue
        raw = answers[qid]
        if raw is None:
            continue
        maps = q.get("maps_to", {}) or {}
        signal = maps.get("signal")
        if not signal:
            continue
        w = float(maps.get("weight", 1.0))
        if isinstance(raw, (int, float)) and 1 <= int(raw) <= 5:
            norm = LIKERT[int(raw)]
        else:
            norm = 0.5
        buckets[signal]["sum"] += norm * w
        buckets[signal]["weight_sum"] += w
        buckets[signal]["n"] += 1

    out = {}
    for k, b in buckets.items():
        measured = b["n"] > 0
        score = (b["sum"] / b["weight_sum"]) if (measured and b["weight_sum"] > 0) else None
        out[k] = {
            "score": score,
            "measured": measured,
            "coverage": b["n"],
            "confidence": min(1.0, b["n"] / 3.0),
        }
    return out
