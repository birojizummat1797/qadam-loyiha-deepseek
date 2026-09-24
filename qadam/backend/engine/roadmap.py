"""
Roadmap Engine v2.0 — ACQ uslubida.
A nuqta → Yo'l (5 stage) → B nuqta + Calendar + First 3 Actions.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# v2 KB yuklash
KB_V2 = json.loads((DATA_DIR / "roadmap_kb_v2.json").read_text(encoding="utf-8"))
# v1 (fallback) — hali ham mavjud
try:
    KB_V1 = json.loads((DATA_DIR / "roadmap_kb_v1.json").read_text(encoding="utf-8"))
except Exception:
    KB_V1 = {"careers": {}}


def build_roadmap(career_id, readiness_result, user_constraints, signals=None):
    """
    Roadmap — v2 formatda (agar mavjud bo'lsa), aks holda v1 (fallback).
    """
    # v2 dan izlash
    kb2 = KB_V2["careers"].get(career_id)
    if kb2:
        return _build_v2(career_id, kb2, readiness_result, user_constraints, signals)

    # v1 fallback
    kb1 = KB_V1["careers"].get(career_id)
    if kb1:
        return _build_v1_fallback(career_id, kb1, readiness_result)

    # Hech narsa yo'q — placeholder
    return _placeholder(career_id, readiness_result)


def _build_v2(career_id, kb, readiness_result, user_constraints, signals):
    """Yangi ACQ-style format."""
    barriers = readiness_result.get("barriers", [])

    # ── A NUQTA — foydalanuvchining hozirgi holati ──
    a_point = {
        "uz": "Sizning hozirgi holatingiz",
        "constraints": [
            {"type": b["type"], "level": b["level"], "solution": b.get("path", "")}
            for b in barriers
        ],
        "existing_constraints": user_constraints,
        "signal_summary": _signal_summary(signals) if signals else {},
    }

    # ── B NUQTA ──
    b_point = kb.get("b_point", {})

    # ── YO'L — 5 stage ──
    stages = []
    for s in kb.get("stages", []):
        stages.append({
            "n": s["n"],
            "name": s["name"],
            "name_uz": s["name_uz"],
            "weeks": s["weeks"],
            "role": s["role"],
            "daily_hours": s["daily_hours"],
            "graduate_by": s["graduate_by"],
            "constraints": [{"problem": c[0], "solution": c[1]} for c in s.get("constraints", [])],
            "daily_focus": s.get("daily_focus", []),
            "signs_right": s.get("signs_right", []),
            "signs_wrong": s.get("signs_wrong", []),
            "graduate_criteria": s.get("graduate_criteria", []),
            "challenges": s.get("challenges", []),
            "skills_gained": s.get("skills_gained", []),
        })

    return {
        "career_id": career_id,
        "career_uz": kb["uz"],
        "cluster": kb.get("cluster", ""),
        "cluster_uz": kb.get("cluster_uz", ""),
        "why_this_path": kb["why"],
        "version": "v2.0",

        # ── 3 asosiy blok ──
        "a_point": a_point,
        "path": {
            "uz": "A dan B gacha yo'l",
            "total_weeks": sum(s["weeks"] for s in stages),
            "stages": stages,
        },
        "b_point": {
            **b_point,
            "salary_uzs": kb.get("salary_uzs", {}),
            "salary_usd": kb.get("salary_usd", {}),
        },
        "income_factors": KB_V2.get("income_factors", {}).get("factors", []),

        # ── Bonus bloklar ──
        "calendar_30d": kb.get("calendar_30d", []),
        "first_3_actions": kb.get("first_3_actions", []),
        "mentor_path": kb.get("mentor_path", []),
        "resources": kb.get("resources", []),
        "milestones": kb.get("milestones", []),

        "is_placeholder": False,
    }


def _signal_summary(signals):
    """Top signallar qisqa tarzda."""
    if not signals:
        return {}
    measured = [
        {"key": k, "score": round(v["score"], 3)}
        for k, v in signals.items()
        if v.get("score") is not None
    ]
    measured.sort(key=lambda x: -x["score"])
    return {
        "top_5": measured[:5],
        "total_measured": len(measured),
    }


def _build_v1_fallback(career_id, kb, readiness_result):
    """Eski v1 formatni yangi ko'rinishga moslashtirish."""
    barriers = readiness_result.get("barriers", [])
    barrier_actions = []
    for b in barriers:
        if b.get("path"):
            barrier_actions.append({
                "barrier_type": b["type"],
                "level": b["level"],
                "action": b["path"],
                "priority": "high" if b["level"] == "hard" else "medium",
            })

    # v1 stage'larni v2 ga moslashtirish
    stages = []
    for i, phase in enumerate(kb["roadmap"]["phases"]):
        stages.append({
            "n": i + 1,
            "name": phase["period"].upper(),
            "name_uz": phase["goal"],
            "weeks": 4,
            "role": "O'rganuvchi",
            "daily_hours": "2 soat",
            "graduate_by": phase["goal"],
            "constraints": [],
            "daily_focus": phase["actions"],
            "signs_right": [],
            "signs_wrong": [],
            "graduate_criteria": phase["actions"],
            "challenges": [],
            "skills_gained": [],
        })

    return {
        "career_id": career_id,
        "career_uz": kb["uz"],
        "why_this_path": kb["why"],
        "version": "v1.0",
        "a_point": {"constraints": barrier_actions},
        "path": {"total_weeks": len(stages) * 4, "stages": stages},
        "b_point": {"outcomes": kb.get("projects", [])},
        "calendar_30d": [],
        "first_3_actions": kb["roadmap"]["first_steps"],
        "mentor_path": [],
        "resources": kb.get("resources", []),
        "milestones": [{"week": (i+1)*4, "milestone": m} for i, m in enumerate(kb["roadmap"]["milestones"])],
        "is_placeholder": False,
        "fallback_from": "v1",
    }


def _placeholder(career_id, readiness_result):
    barriers = readiness_result.get("barriers", [])
    return {
        "career_id": career_id,
        "career_uz": career_id,
        "why_this_path": "Bu yo'nalish signallaringizga mos, roadmap tayyorlanmoqda.",
        "version": "placeholder",
        "a_point": {"constraints": [
            {"type": b["type"], "level": b["level"], "solution": b.get("path", "")}
            for b in barriers
        ]},
        "path": {"total_weeks": 0, "stages": []},
        "b_point": {},
        "calendar_30d": [],
        "first_3_actions": ["Roadmap tayyorlanmoqda..."],
        "mentor_path": [],
        "resources": [],
        "milestones": [],
        "is_placeholder": True,
    }


def build_full_report(ranked, constraints, taxonomy, signals=None):
    reports = []
    for item in ranked:
        rr = {"readiness": item["readiness"], "barriers": item["barriers"]}
        rm = build_roadmap(item["career_id"], rr, constraints, signals)
        reports.append({
            "career": {
                "id": item["career_id"],
                "uz": item["career_uz"],
                "cluster": item["cluster"],
                "cluster_uz": item["cluster_uz"],
                "pathway_type": item["pathway_type"],
                "learning_months": item["learning_months"],
            },
            "fit": item["fit"],
            "readiness": item["readiness"],
            "coverage": item["coverage"],
            "barriers": item["barriers"],
            "has_hard_barrier": item["has_hard_barrier"],
            "roadmap": rm,
        })
    return {"careers": reports}
