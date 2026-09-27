"""
Fit & Coverage & Confidence — PM spec (PHASE G).

Fit(c) = (Σ W_c,s · V_s · T_s) / (Σ W_c,s · 10) × 100
Coverage(c) = Σ W_c,s (measured) / Σ W_c,s (all)
Confidence(c) = Coverage × avg(T_s)
"""


def calculate_fit(signals, career):
    weights = career["signals"]  # {signal_key: weight 1-5}

    total_weight = sum(weights.values())

    # ─── Fit numerator / denominator ───
    num = 0.0
    measured_weight = 0.0
    trust_sum = 0.0
    measured_count = 0
    missing = []

    for sig, w in weights.items():
        s = signals.get(sig, {})
        if s.get("evidence_state") == "unmeasured" or s.get("value") is None:
            missing.append(sig)
            continue

        v = s["value"]           # [0, 10]
        t = s["trust"]           # 0.0 - 1.0

        num += w * v * t
        measured_weight += w
        trust_sum += t
        measured_count += 1

    # ─── Coverage ───
    coverage = (measured_weight / total_weight) if total_weight else 0.0

    # ─── Fit ───
    if measured_weight == 0 or measured_count == 0:
        fit = None
    else:
        fit = (num / (measured_weight * 10.0)) * 100.0

    # ─── Confidence ───
    if measured_count == 0:
        confidence = 0.0
    else:
        avg_trust = trust_sum / measured_count
        confidence = coverage * avg_trust

    # ─── Status ───
    if fit is None:
        status = "no_evidence"
    elif coverage < 0.5:
        status = "insufficient_coverage"
    else:
        status = "ok"

    return {
        "fit": round(fit, 2) if fit is not None else None,
        "coverage": round(coverage, 3),
        "confidence": round(confidence, 3),
        "measured_signals": measured_count,
        "missing_signals": missing,
        "status": status,
    }
