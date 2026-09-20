import json
from pathlib import Path
from .fit import calculate_fit
from .readiness import calculate_readiness

KB_PATH = Path(__file__).parent.parent / "data" / "roadmap_kb_v1.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    _KB = json.load(f)
    KB_CAREERS = set(_KB["careers"].keys())


def rank_careers(signals, taxonomy, constraints, min_coverage=0.5, top_n=5):
    candidates = []
    excluded = []

    for cluster_key, cluster in taxonomy["clusters"].items():
        for career_key, career in cluster["careers"].items():
            fit_result = calculate_fit(signals, career)
            if fit_result["fit"] is None:
                excluded.append({"career_id": career_key, "reason": "insufficient_data"})
                continue
            if fit_result["coverage"] < min_coverage:
                excluded.append({
                    "career_id": career_key, "reason": "low_coverage",
                    "coverage": fit_result["coverage"], "fit": fit_result["fit"],
                })
                continue

            readiness_result = calculate_readiness(
                constraints, career.get("prerequisites", {})
            )
            composite = fit_result["fit"] * (
                0.7 + 0.3 * (readiness_result["readiness"] / 100)
            )
            has_roadmap = career_key in KB_CAREERS
            if has_roadmap:
                composite += 10

            candidates.append({
                "career_id": career_key,
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                "career_uz": career["uz"],
                "fit": fit_result["fit"],
                "coverage": fit_result["coverage"],
                "readiness": readiness_result["readiness"],
                "barriers": readiness_result["barriers"],
                "has_hard_barrier": readiness_result["has_hard_barrier"],
                "missing_signals": fit_result["missing"],
                "learning_months": career.get("learning_months"),
                "pathway_type": career.get("pathway_type"),
                "has_roadmap": has_roadmap,
                "composite_score": round(composite, 1),
            })

    candidates.sort(key=lambda x: -x["composite_score"])
    top = candidates[:top_n]

    if len(top) >= 2:
        gap = top[0]["composite_score"] - top[1]["composite_score"]
    else:
        gap = 100
    avg_coverage = sum(c["coverage"] for c in top) / len(top) if top else 0

    if avg_coverage >= 0.75 and gap >= 5:
        confidence = "high"
    elif avg_coverage >= 0.55:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "ranked": top,
        "excluded_low_coverage": excluded,
        "confidence": confidence,
        "total_candidates": len(candidates) + len(excluded),
    }
