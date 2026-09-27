"""
Roadmap Engine — KB + template fallback.

Oqim:
1. KB'da batafsil roadmap bormi? → uni ishlatamiz
2. Aks holda → cluster template + career info
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_kb():
    for name in ["roadmap_kb_v2.json", "roadmap_kb_v1.json"]:
        p = DATA_DIR / name
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {"careers": {}}


def _load_templates():
    p = DATA_DIR / "roadmap_templates_v1.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"templates": {}}


KB = _load_kb()
TEMPLATES = _load_templates()


def build_roadmap(career_slug: str, career_data: dict, ranked_item: dict) -> dict:
    """
    Shaxsiy roadmap qurish.
    """
    # 1. KB'da batafsil roadmap bormi?
    kb_career = KB.get("careers", {}).get(career_slug)
    if kb_career:
        return _from_kb(career_slug, kb_career, ranked_item)

    # 2. Template fallback
    cluster = career_data.get("cluster", "")
    template = TEMPLATES.get("templates", {}).get(cluster)
    if template:
        return _from_template(career_slug, career_data, template, ranked_item)

    # 3. Bo'sh placeholder
    return _placeholder(career_slug, career_data, ranked_item)


def _from_kb(slug: str, kb: dict, ranked: dict) -> dict:
    """KB'dan to'liq roadmap."""
    stages = []
    for s in kb.get("stages", []):
        stages.append({
            "period": f"{s.get('weeks', 0)} hafta",
            "goal": s.get("name_uz", ""),
            "role": s.get("role", ""),
            "skills": s.get("skills_gained", []),
            "actions": s.get("daily_focus", [])[:4],
            "proof": "",
            "milestone": s.get("graduate_by", ""),
        })

    first_3 = kb.get("first_3_actions", [])[:3]
    if not first_3 and stages:
        first_3 = stages[0].get("actions", [])[:3]

    return {
        "career_id": slug,
        "career_uz": kb.get("uz", ""),
        "why": kb.get("why", ""),
        "source": "kb",
        "phases": stages,
        "next_3_actions": first_3,
        "resources": kb.get("resources", []),
        "b_point": kb.get("b_point", {}),
        "milestones": kb.get("milestones", []),
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": _first_step_reasoning(ranked, stages),
    }


def _from_template(slug: str, career: dict, template: dict, ranked: dict) -> dict:
    """Template'dan roadmap."""
    phases = []
    for p in template.get("phases", []):
        phases.append({
            "period": p.get("period", ""),
            "goal": p.get("goal", ""),
            "role": "",
            "skills": p.get("skills", []),
            "actions": p.get("actions", []),
            "proof": p.get("proof", ""),
            "milestone": p.get("milestone", ""),
        })

    first_3 = phases[0]["actions"][:3] if phases else []
    return {
        "career_id": slug,
        "career_uz": career.get("title_uz") or career.get("uz", ""),
        "why": f"Bu yo'nalish sizning signallaringizga mos keladi.",
        "source": "template",
        "phases": phases,
        "next_3_actions": first_3,
        "resources": [],
        "b_point": career.get("salary_usd") and {"salary_usd": career["salary_usd"]} or {},
        "milestones": [p.get("milestone", "") for p in phases if p.get("milestone")],
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": _first_step_reasoning(ranked, phases),
    }


def _placeholder(slug: str, career: dict, ranked: dict) -> dict:
    return {
        "career_id": slug,
        "career_uz": career.get("title_uz", slug),
        "why": "Bu yo'nalish uchun batafsil roadmap tez orada qo'shiladi.",
        "source": "placeholder",
        "phases": [],
        "next_3_actions": [],
        "resources": [],
        "b_point": {},
        "milestones": [],
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": "",
    }


def _barrier_resolutions(barriers: list) -> list:
    """Barrier'larni action'ga aylantirish."""
    out = []
    for b in barriers:
        if b.get("path"):
            out.append({
                "level": b.get("level", "soft"),
                "action": b["path"],
            })
    return out


def _first_step_reasoning(ranked: dict, stages: list) -> str:
    """Nega birinchi qadam muhim."""
    if not stages:
        return ""
    return (
        f"Birinchi qadam — {stages[0].get('goal', 'asoslar')}. "
        "Bu bosqichsiz keyingi qadamlar samarasiz bo'ladi."
    )
