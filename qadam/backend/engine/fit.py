def calculate_fit(signals, career):
    weights = career["signals"]
    total_weight = sum(weights.values())
    weighted_score = 0.0
    measured_weight = 0.0
    missing_signals = []

    for sig, w in weights.items():
        s = signals.get(sig, {})
        if not s.get("measured"):
            missing_signals.append(sig)
            continue
        weighted_score += s["score"] * w
        measured_weight += w

    if measured_weight == 0:
        return {
            "fit": None, "coverage": 0.0,
            "missing": missing_signals, "status": "insufficient_data",
        }

    fit = (weighted_score / measured_weight) * 100
    coverage = measured_weight / total_weight if total_weight else 0.0
    return {
        "fit": round(fit, 1),
        "coverage": round(coverage, 2),
        "missing": missing_signals,
        "status": "ok" if coverage >= 0.6 else "low_coverage",
    }
