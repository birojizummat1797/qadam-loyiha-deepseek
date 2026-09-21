"""
Ranking Engine v3 — FAQAT roadmap'da mavjud bo'lgan career'larni qaytaradi.
Bu MAJBURIY — foydalanuvchi premium to'lab, "tayyorlanmoqda" ko'rmasligi uchun.
"""
import json
from pathlib import Path
from .fit import calculate_fit
from .readiness import calculate_readiness

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_all_roadmap_careers():
    """Barcha roadmap KB fayllaridan career'larni birlashtirish."""
    careers = set()

    # v2 (asosiy)
    for name in ["roadmap_kb_v2.json", "roadmap_kb_v2_part_a.json",
                 "roadmap_kb_v2_part_b.json", "roadmap_kb_v1.json"]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass

    print(f"[ranking] KB careers yuklandi: {len(careers)} ta -> {sorted(careers)}")
    return careers


KB_CAREERS = _load_all_roadmap_careers()


def rank_careers(signals, taxonomy, constraints, min_coverage=0.5, top_n=3):
    """
    FAQAT roadmap'da mavjud bo'lgan career'lardan Top-N.
    Agar roadmap'li 3 tadan kam bo'lsa — mavjudlarini qaytaradi.
    """
    candidates = []
    excluded = []

    for cluster_key, cluster in taxonomy["clusters"].items():
        for career_key, career in cluster["careers"].items():
            # ⚠️ MAJBURIY FILTR — roadmap'siz career'lar HECH QACHON ko'rinmaydi
            if career_key not in KB_CAREERS:
                excluded.append({"career_id": career_key, "reason": "no_roadmap"})
                continue

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
                "has_roadmap": True,
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
        "total_candidates": len(candidates),
        "kb_careers_count": len(KB_CAREERS),
    }
