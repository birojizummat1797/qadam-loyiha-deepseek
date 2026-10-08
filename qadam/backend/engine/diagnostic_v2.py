"""Diagnostic v2 — 9×25 catalog (draft, founder review pending).

Pure functions only (no DB, no I/O besides loading the JSON data once).

Sources (claude-qadamio):
  docs/decisions/2026-10-05-catalog-9x25.md, docs/decisions/2026-10-07-p2-catalog-first.md,
  docs/specs/2026-10-05-discovery-v2-draft.md, docs/specs/2026-10-05-deep-v2-draft.md,
  golden samples (2026-10-05, 2026-10-07 batch 1–2),
  docs/methodology/qadam-metodologiyasi-v0.1.md.

Methodology locks applied here:
  - Snapshot, not a verdict ("Qadam insonni bir kunda hukm qilmaydi").
  - No percentages or scores shown to the user; only evidence statements.
  - "Bilmayman" = unmeasured: it adds nothing and takes nothing away.
  - A wrong task answer never produces a negative conclusion.
"""
import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# Discovery rule (founder, 2026-10-05): a clear catalog needs ≥ 3 points and
# a lead of ≥ 1 over the next catalog.
DISCOVERY_MIN_POINTS = 3
DISCOVERY_MIN_LEAD = 1

# Deep rule (spec proposal, founder confirmation pending): a clear career needs
# ≥ 4 picks and a higher picks-per-appearance share than the next career.
DEEP_MIN_PICKS = 4

# Two-catalog split for part A (spec): 6 questions from the first catalog, 5 from the second.
SPLIT_FIRST, SPLIT_SECOND = 6, 5
A_QUESTIONS = 11

# Discovery condition questions reused from v1 (life stage, daily time, device, English).
CONDITION_QUESTION_IDS = ("DISC_Q01", "DISC_Q11", "DISC_Q12", "DISC_Q13")

SNAPSHOT_NOTE = (
    "Bu bugungi holatning surati — yakuniy hukm emas. Qadam insonni bir kunda hukm qilmaydi: "
    "signallar vaqt o‘tib, amaliy ish bilan tasdiqlanadi yoki o‘zgaradi. Qarorni siz qilasiz."
)


@lru_cache(maxsize=1)
def load_data() -> dict:
    return json.loads((DATA_DIR / "diagnostic_v2.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_condition_questions() -> list:
    v1 = json.loads((DATA_DIR / "discovery_questions_v1.json").read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in v1["questions"]}
    return [by_id[qid] for qid in CONDITION_QUESTION_IDS]


@lru_cache(maxsize=1)
def load_roadmap_ids() -> frozenset:
    ids = set()
    for name in ("roadmap_kb_v2.json", "roadmap_kb_v3_draft.json"):
        kb = json.loads((DATA_DIR / name).read_text(encoding="utf-8"))
        ids.update(kb["careers"].keys())
    return frozenset(ids)


@lru_cache(maxsize=1)
def _roadmap_kb() -> tuple[dict, frozenset]:
    """Merged KB (v3 draft + live v2; v2 wins on overlap) and the set of live v2 IDs."""
    v2 = json.loads((DATA_DIR / "roadmap_kb_v2.json").read_text(encoding="utf-8"))["careers"]
    v3 = json.loads((DATA_DIR / "roadmap_kb_v3_draft.json").read_text(encoding="utf-8"))["careers"]
    return {**v3, **v2}, frozenset(v2)


def build_roadmap(career_id: str) -> dict | None:
    """Public roadmap for one career (no salary, no unsupported claims); None if there is none."""
    from backend.engine.public_output import strip_unsupported
    from backend.engine.roadmap import _build_v2

    kb, live = _roadmap_kb()
    if career_id not in kb:
        return None
    rm = _build_v2(career_id, kb[career_id], {}, {}, None)
    rm["version"] = "v2.0" if career_id in live else "v3.0-draft"
    return strip_unsupported(rm)


def catalogs_by_id() -> dict:
    return {c["id"]: c for c in load_data()["catalogs"]}


# ── Public question payloads (no correct answers, no catalog/career tags) ──

def _public_options(options):
    return [{"id": o["id"], "label": o["label"]} for o in options]


def discovery_questions_public() -> dict:
    data = load_data()
    questions = [
        {"id": q["id"], "text": q["text"], "options": _public_options(q["options"]), "kind": "direction"}
        for q in data["discovery"]["questions"]
    ]
    conditions = [
        {"id": q["id"], "text": q["text"], "options": _public_options(q["options"]), "kind": "condition"}
        for q in load_condition_questions()
    ]
    return {"version": data["version"], "questions": questions + conditions}


def deep_question_ids(catalog_ids: list) -> list:
    """Part A question IDs served for one catalog (11) or two tied catalogs (6 + 5)."""
    cats = catalogs_by_id()
    if len(catalog_ids) == 1:
        return [q["id"] for q in cats[catalog_ids[0]]["questions"][:A_QUESTIONS]]
    first, second = catalog_ids
    return ([q["id"] for q in cats[first]["questions"][:SPLIT_FIRST]]
            + [q["id"] for q in cats[second]["questions"][:SPLIT_SECOND]])


def validate_catalog_ids(catalog_ids) -> list:
    cats = catalogs_by_id()
    ids = list(dict.fromkeys(catalog_ids or []))
    if not 1 <= len(ids) <= 2 or any(c not in cats for c in ids):
        raise ValueError("catalogs: 1 or 2 valid catalog IDs required")
    return ids


def deep_questions_public(catalog_ids: list) -> dict:
    data = load_data()
    cats = catalogs_by_id()
    ids = validate_catalog_ids(catalog_ids)
    qmap = {q["id"]: q for c in ids for q in cats[c]["questions"]}
    a_part = [{"id": qid, "text": qmap[qid]["text"], "options": _public_options(qmap[qid]["options"])}
              for qid in deep_question_ids(ids)]
    main = cats[ids[0]]
    tasks = [{"id": t["id"], "title": t["title"], "text": t["text"], "options": _public_options(t["options"])}
             for t in main["tasks"]]
    lesson = {
        "text": main["lesson"]["text"],
        "questions": [{"id": q["id"], "text": q["text"], "options": _public_options(q["options"])}
                      for q in main["lesson"]["questions"]],
    }
    return {
        "version": data["version"],
        "catalogs": [{"id": c, "uz": cats[c]["uz"]} for c in ids],
        "a_part": a_part,
        "style": [{"id": q["id"], "text": q["text"], "options": _public_options(q["options"])} for q in data["style"]],
        "readiness": [{"id": q["id"], "text": q["text"], "options": _public_options(q["options"])} for q in data["readiness"]],
        "tasks": tasks,
        "lesson": lesson,
        "ease": data["ease"],
    }


# ── Discovery scoring ──

def score_discovery(answers: dict) -> dict:
    """answers: {question_id: option_id}. Unknown IDs are rejected by the API before this."""
    data = load_data()
    points = {c["id"]: 0 for c in data["catalogs"]}
    answered = unmeasured = 0
    for q in data["discovery"]["questions"]:
        oid = answers.get(q["id"])
        if oid is None:
            continue
        answered += 1
        opt = next((o for o in q["options"] if o["id"] == oid), None)
        if opt is None or opt["catalog"] is None:
            unmeasured += 1
            continue
        points[opt["catalog"]] += 1

    order = [c["id"] for c in data["catalogs"]]
    ranked = sorted(points.items(), key=lambda kv: (-kv[1], order.index(kv[0])))
    (top_id, top), (second_id, second) = ranked[0], ranked[1]
    cats = catalogs_by_id()

    if top >= DISCOVERY_MIN_POINTS and top - second >= DISCOVERY_MIN_LEAD:
        status, chosen = "clear", [top_id]
    elif top >= DISCOVERY_MIN_POINTS and top == second:
        status, chosen = "two", [top_id, second_id]
    else:
        status, chosen = "unclear", []

    return {
        "status": status,
        "catalogs": [{"id": c, "uz": cats[c]["uz"], "careers": [x["uz"] for x in cats[c]["careers"]]} for c in chosen],
        "answered": answered,
        "unmeasured": unmeasured,
        # Internal counts for analysis; the UI must not show them as scores.
        "_points": points,
    }


def extract_conditions(answers: dict) -> dict:
    """Labels of the condition answers (for the result's 'sharoit' block)."""
    out = {}
    for q in load_condition_questions():
        oid = answers.get(q["id"])
        opt = next((o for o in q["options"] if o["id"] == oid), None)
        if opt:
            out[q["id"]] = {"question": q["text"], "answer": opt["label"]}
    return out


# ── Deep scoring ──

def score_deep(catalog_ids: list, answers: dict, ease: dict | None = None) -> dict:
    """answers: {question_id: option_id} for part A, B, C, tasks and lesson questions.
    ease: {task_id: ease_option_id}."""
    data = load_data()
    cats = catalogs_by_id()
    ids = validate_catalog_ids(catalog_ids)
    served = deep_question_ids(ids)
    qmap = {q["id"]: q for c in ids for q in cats[c]["questions"]}

    careers = {car["id"]: {"uz": car["uz"], "catalog": c, "picks": 0, "appearances": 0}
               for c in ids for car in cats[c]["careers"]}
    unmeasured = 0
    for qid in served:
        q = qmap[qid]
        for o in q["options"]:
            if o["career"]:
                careers[o["career"]]["appearances"] += 1
        opt = next((o for o in q["options"] if o["id"] == answers.get(qid)), None)
        if opt is None or opt["career"] is None:
            unmeasured += 1
            continue
        careers[opt["career"]]["picks"] += 1

    def share(c):
        return c["picks"] / c["appearances"] if c["appearances"] else 0.0

    order = [cid for c in ids for cid in (x["id"] for x in cats[c]["careers"])]
    ranked = sorted(careers.items(), key=lambda kv: (-share(kv[1]), -kv[1]["picks"], order.index(kv[0])))
    top_id, top = ranked[0]
    second_id, second = ranked[1]

    if top["picks"] >= DEEP_MIN_PICKS and share(top) > share(second):
        status, chosen = "clear", [top_id]
    elif top["picks"] >= DEEP_MIN_PICKS and share(top) == share(second):
        status, chosen = "two", [top_id, second_id]
    else:
        status, chosen = "unclear", []

    roadmaps = load_roadmap_ids()
    career_out = [{"id": cid, "uz": careers[cid]["uz"], "catalog": careers[cid]["catalog"],
                   "has_roadmap": cid in roadmaps} for cid in chosen]

    evidence = _task_evidence(cats[ids[0]], answers, ease or {})
    return {
        "status": status,
        "catalogs": [{"id": c, "uz": cats[c]["uz"]} for c in ids],
        "careers": career_out,
        "evidence": evidence,
        "style": _labels(data["style"], answers),
        "readiness": _labels(data["readiness"], answers),
        "unmeasured": unmeasured,
        "snapshot_note": SNAPSHOT_NOTE,
        # Internal counts for analysis; the UI must not show them as scores.
        "_career_picks": {cid: {"picks": c["picks"], "appearances": c["appearances"]} for cid, c in careers.items()},
    }


def _labels(questions, answers):
    out = []
    for q in questions:
        opt = next((o for o in q["options"] if o["id"] == answers.get(q["id"])), None)
        if opt and not opt["id"].endswith("_E"):
            out.append({"question": q["text"], "answer": opt["label"]})
    return out


INTEREST_EASE = ("easy_interesting", "hard_interesting")


def _task_evidence(catalog: dict, answers: dict, ease: dict) -> dict:
    """Evidence statements only — never a score, never a negative conclusion."""
    ease_labels = {o["id"]: o["label"] for o in load_data()["ease"]["options"]}
    done, items = 0, []
    for t in catalog["tasks"]:
        chosen = answers.get(t["id"])
        state = "unmeasured" if chosen in (None, f"{t['id']}_E") else ("done" if chosen == t["correct"] else "not_yet")
        if state == "done":
            done += 1
        items.append({
            "id": t["id"],
            "title": t["title"],
            "state": state,
            "ease": ease.get(t["id"]) if ease.get(t["id"]) in ease_labels else None,
            "ease_label": ease_labels.get(ease.get(t["id"])),
        })
    lesson_done = sum(1 for q in catalog["lesson"]["questions"] if answers.get(q["id"]) == q["correct"])
    lesson_total = len(catalog["lesson"]["questions"])

    statements = []
    for it in items:
        if it["state"] == "done":
            statements.append(f"“{it['title']}” topshirig‘ini to‘g‘ri bajardingiz.")
    if lesson_done == lesson_total:
        statements.append("Yangi qoidani qisqa darsdan keyin darhol to‘g‘ri qo‘lladingiz — o‘rganish signali.")
    elif lesson_done:
        statements.append("Yangi qoidani qisqa darsdan keyin qisman qo‘lladingiz.")
    if done < 2 and lesson_done == 0:
        statements.append("Amaliy topshiriqlar bo‘yicha hali yetarli dalil yo‘q — bu ko‘nikmalar o‘rganish bilan rivojlanadi.")

    ease_interest = sum(1 for it in items if it["ease"] in INTEREST_EASE)
    if ease_interest >= 3:
        statements.append("Topshiriqlarning ko‘pi sizga qiziq bo‘ldi — bu yo‘nalishga qiziqish signali.")

    # Language ladder, step 1 (methodology v0.1): ≥ 2 correct tasks = first evidence.
    level = "first_evidence" if done >= 2 else "not_enough"
    return {"level": level, "statements": statements, "tasks": items}


def public_result(result: dict) -> dict:
    """Strip internal counts before sending to the client."""
    return {k: v for k, v in result.items() if not k.startswith("_")}
