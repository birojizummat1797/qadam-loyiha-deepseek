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
