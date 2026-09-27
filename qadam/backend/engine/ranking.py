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


def rank_careers(signals, taxonomy, constraints, top_n=TOP_N):
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

            # Composite score (Fit ustuvor, Readiness modifikator)
            composite = fit_result["fit"] * (
                0.7 + 0.3 * (readiness_result["readiness"] / 100.0)
            )

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
            })

    candidates.sort(key=lambda x: -x["composite_score"])
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
        "total_candidates": len(candidates),
        "kb_careers_count": len(KB_CAREERS),
    }
