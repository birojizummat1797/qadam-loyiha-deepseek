# -*- coding: utf-8 -*-
"""QADAM - barcha backend fayllarini qayta yozadi."""
from pathlib import Path

BASE = Path("qadam/backend")
FILES = {}


def add(path, content):
    FILES[path] = content.strip() + "\n"


# ═══ data_loader.py ═══
add("data_loader.py", '''
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load(name):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_taxonomy():
    return _load("taxonomy_v1.json")


def load_questions():
    return _load("questions_v1.json")


def load_signals():
    return _load("signals_v1.json")


def load_roadmap_kb():
    return _load("roadmap_kb_v1.json")


def get_versions():
    return {
        "taxonomy": "v1.0",
        "questions": "v1.0",
        "signals": "v1.0",
        "roadmap_kb": "v1.1",
        "ai_prompt": "v1.0",
    }
''')

# ═══ engine/signals.py ═══
add("engine/signals.py", '''
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
''')

# ═══ engine/fit.py ═══
add("engine/fit.py", '''
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
''')

# ═══ engine/readiness.py ═══
add("engine/readiness.py", '''
ENGLISH_ORDER = {"none": 0, "a2": 1, "b1": 2, "b2": 3, "c1": 4}


def calculate_readiness(constraints, prerequisites):
    barriers = []
    score = 100

    dev = constraints.get("device")
    req_dev = prerequisites.get("device")
    if req_dev == "required" and dev in ("smartphone_only", "none"):
        level = "hard" if dev == "none" else "soft"
        barriers.append({
            "type": "device", "level": level,
            "path": "Noutbuk topish yollari - grantlar, kutubxona",
        })
        score -= 30 if dev == "none" else 15

    req_en = prerequisites.get("english", "none")
    user_en = constraints.get("english", "none")
    if ENGLISH_ORDER.get(user_en, 0) < ENGLISH_ORDER.get(req_en, 0):
        gap = ENGLISH_ORDER.get(req_en, 0) - ENGLISH_ORDER.get(user_en, 0)
        barriers.append({
            "type": "language", "level": "soft",
            "path": "Ingliz tilini " + req_en.upper() + " darajaga kotarish (3-6 oy)",
        })
        score -= 10 * gap

    t = constraints.get("time")
    if t in ("lt_1h", "1h"):
        barriers.append({
            "type": "time", "level": "soft",
            "path": "Haftalik jadval tuzish",
        })
        score -= 10

    return {
        "readiness": max(0, score),
        "barriers": barriers,
        "has_hard_barrier": any(b["level"] == "hard" for b in barriers),
    }
''')

# ═══ engine/ranking.py ═══
add("engine/ranking.py", '''
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
''')

# ═══ engine/roadmap.py ═══
add("engine/roadmap.py", '''
import json
from pathlib import Path

KB_PATH = Path(__file__).parent.parent / "data" / "roadmap_kb_v1.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    ROADMAP_KB = json.load(f)


def build_roadmap(career_id, readiness_result, user_constraints):
    kb = ROADMAP_KB["careers"].get(career_id)

    if not kb:
        barriers = readiness_result.get("barriers", [])
        barrier_actions = []
        for b in barriers:
            if b.get("path"):
                barrier_actions.append({
                    "barrier_type": b["type"], "level": b["level"],
                    "action": b["path"],
                    "priority": "high" if b["level"] == "hard" else "medium",
                })
        return {
            "career_id": career_id,
            "career_uz": career_id,
            "why_this_path": "Bu yonalish signallaringizga mos, roadmap tez orada.",
            "gaps": [],
            "phases": [],
            "first_3_actions": [ba["action"] for ba in barrier_actions[:3]] or ["Roadmap tayyorlanmoqda..."],
            "barrier_resolutions": barrier_actions,
            "milestones": [],
            "risks": [],
            "resources": [],
            "projects": [],
            "market_context": {},
            "is_placeholder": True,
        }

    barriers = readiness_result.get("barriers", [])
    barrier_actions = []
    for b in barriers:
        if b.get("path"):
            barrier_actions.append({
                "barrier_type": b["type"], "level": b["level"],
                "action": b["path"],
                "priority": "high" if b["level"] == "hard" else "medium",
            })

    first_3 = []
    for ba in barrier_actions[:2]:
        first_3.append("[Tosiqni hal qilish] " + ba["action"])
    for step in kb["roadmap"]["first_steps"]:
        if len(first_3) >= 3:
            break
        first_3.append(step)

    return {
        "career_id": career_id,
        "career_uz": kb["uz"],
        "why_this_path": kb["why"],
        "gaps": kb["skill_gap"],
        "phases": kb["roadmap"]["phases"],
        "first_3_actions": first_3[:3],
        "barrier_resolutions": barrier_actions,
        "milestones": kb["roadmap"]["milestones"],
        "risks": kb.get("risks", []),
        "resources": kb.get("resources", []),
        "projects": kb.get("projects", []),
        "market_context": kb.get("market_context", {}),
        "is_placeholder": False,
    }


def build_full_report(ranked, constraints, taxonomy):
    reports = []
    for item in ranked:
        rr = {"readiness": item["readiness"], "barriers": item["barriers"]}
        rm = build_roadmap(item["career_id"], rr, constraints)
        reports.append({
            "career": {
                "id": item["career_id"], "uz": item["career_uz"],
                "cluster": item["cluster"], "cluster_uz": item["cluster_uz"],
                "pathway_type": item["pathway_type"],
                "learning_months": item["learning_months"],
            },
            "fit": item["fit"], "readiness": item["readiness"],
            "coverage": item["coverage"],
            "barriers": item["barriers"],
            "has_hard_barrier": item["has_hard_barrier"],
            "roadmap": rm,
        })
    return {"careers": reports}
''')


def main():
    print("=" * 60)
    print("QADAM fix: backend fayllari qayta yozilmoqda")
    print("=" * 60)
    for path, content in FILES.items():
        full = BASE / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] " + str(full.relative_to(BASE.parent)))
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yangilandi!")
    print()
    print("Keyingi qadam: __pycache__ tozalash va serverni qayta ishga tushirish")


if __name__ == "__main__":
    main()