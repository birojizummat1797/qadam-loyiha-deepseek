"""
Ranking — PM spec (PHASE G).

Qoidalar:
- Coverage < 0.5 → tavsiya qilinmaydi
- Top 3-5, lekin dalil yetmasa — kamroq
- Confidence = Coverage × avg(T_s)
"""

import json
from pathlib import Path
from .fit import calculate_fit
from .readiness import calculate_readiness
from .levels import context_status, evidence_level

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_roadmap_careers():
    careers = set()
    for name in [
        "roadmap_kb_v3.json", "roadmap_kb_v2.json",
        "roadmap_kb_v2_part_a.json", "roadmap_kb_v2_part_b.json",
        "roadmap_kb_v1.json",
    ]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass
    return careers


KB_CAREERS = _load_roadmap_careers()

MIN_COVERAGE = 0.5
TOP_N = 5

# Founder decision 2026-10-04 (BL-14): a career is recommended only if its fit
# is at least this score; top_n is a ceiling, not a quota. When careers were
# measured but none reaches it, the user gets an honest "no clear direction"
# message instead of a filled-up list. Applied to recommendation lists
# (preliminary, career intelligence, deep result, PDF) — not to the roadmap of
# a career the user opened. Audit: claude-qadamio docs/reviews/2026-10-04-threshold-audit-report.md
MIN_RECOMMENDATION_SCORE = 51.0


def rank_careers(signals, taxonomy, constraints, top_n=TOP_N, min_score=None):
    candidates = []
    excluded = []

    for cluster_key, cluster in taxonomy["clusters"].items():
        for career_key, career in cluster["careers"].items():
            if career_key not in KB_CAREERS:
                excluded.append({"career_id": career_key, "reason": "no_roadmap"})
                continue

            fit_result = calculate_fit(signals, career)

            if fit_result["status"] == "no_evidence":
                excluded.append({"career_id": career_key, "reason": "no_evidence"})
                continue
            if fit_result["status"] == "insufficient_coverage":
                excluded.append({
                    "career_id": career_key,
                    "reason": "coverage_below_0.5",
                    "coverage": fit_result["coverage"],
                })
                continue

            readiness_result = calculate_readiness(
                constraints, career.get("prerequisites", {})
            )

            # Composite score (Fit ustuvor, Readiness modifikator).
            # Sharoit noma'lum bo'lsa, modifikator qo'llanmaydi (taxmin qilinmaydi).
            readiness_value = readiness_result["readiness"]
            modifier = 1.0 if readiness_value is None else 0.7 + 0.3 * (readiness_value / 100.0)
            composite = fit_result["fit"] * modifier

            candidates.append({
                "career_id": career_key,
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                "career_uz": career["uz"],
                "fit": fit_result["fit"],
                "coverage": fit_result["coverage"],
                "confidence": fit_result["confidence"],
                "measured_signals": fit_result["measured_signals"],
                "missing_signals": fit_result["missing_signals"],
                "readiness": readiness_result["readiness"],
                "p_computer": readiness_result["p_computer"],
                "p_english": readiness_result["p_english"],
                "p_time": readiness_result["p_time"],
                "barriers": readiness_result["barriers"],
                "has_hard_barrier": readiness_result["has_hard_barrier"],
                "learning_months": career.get("learning_months"),
                "pathway_type": career.get("pathway_type"),
                "composite_score": round(composite, 2),
                # User-facing (no percentages): see engine/levels.py
                "evidence_level": evidence_level(fit_result["coverage"]),
                "context_status": context_status(readiness_result),
            })

    candidates.sort(key=lambda x: -x["composite_score"])
    eligible = len(candidates)
    if min_score is not None:
        for c in candidates:
            if c["fit"] < min_score:
                excluded.append({"career_id": c["career_id"], "reason": "below_min_score"})
        candidates = [c for c in candidates if c["fit"] >= min_score]
    top = candidates[:top_n]

    # Global confidence
    if not top:
        confidence = "none"
    else:
        avg_cov = sum(c["coverage"] for c in top) / len(top)
        if avg_cov >= 0.75:
            confidence = "high"
        elif avg_cov >= 0.55:
            confidence = "medium"
        else:
            confidence = "low"

    return {
        "ranked": top,
        "excluded": excluded,
        "confidence": confidence,
        "total_candidates": eligible,
        "kb_careers_count": len(KB_CAREERS),
        "min_score": min_score,
        # Careers were measured, but none reached the minimum score → honest message.
        "no_clear_direction": min_score is not None and eligible > 0 and not top,
    }
