"""Diagnostic v2 (9×25 catalog, draft): data integrity, scoring rules, API flow."""
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.engine import diagnostic_v2 as dv2  # noqa: E402

DATA = dv2.load_data()
CATS = {c["id"]: c for c in DATA["catalogs"]}
NONE = DATA["none_label"]


# ── Data integrity ──

def test_nine_catalogs_twenty_five_careers():
    assert len(CATS) == 9
    careers = [car["id"] for c in CATS.values() for car in c["careers"]]
    assert len(careers) == 25 and len(set(careers)) == 25


def test_every_career_has_a_roadmap():
    roadmaps = dv2.load_roadmap_ids()
    missing = [car["id"] for c in CATS.values() for car in c["careers"] if car["id"] not in roadmaps]
    assert missing == []


def test_discovery_questions_five_options_none_last_each_catalog_four_times():
    qs = DATA["discovery"]["questions"]
    assert len(qs) == 9
    counts = Counter()
    for q in qs:
        assert len(q["options"]) == 5
        assert q["options"][-1]["label"] == NONE and q["options"][-1]["catalog"] is None
        cats_here = [o["catalog"] for o in q["options"][:4]]
        assert len(set(cats_here)) == 4, q["id"]
        counts.update(cats_here)
    assert set(counts.values()) == {4} and len(counts) == 9


def test_discovery_question_texts_are_all_different():
    texts = [q["text"] for q in DATA["discovery"]["questions"]]
    assert len(set(texts)) == len(texts)


@pytest.mark.parametrize("cid", list(CATS))
def test_catalog_part_a_balanced(cid):
    c = CATS[cid]
    assert len(c["questions"]) == 11
    own = {car["id"] for car in c["careers"]}
    counts = Counter()
    for q in c["questions"]:
        assert len(q["options"]) == 5 and q["options"][-1]["career"] is None
        assert all(o["career"] in own for o in q["options"][:4]), q["id"]
        counts.update(o["career"] for o in q["options"][:4])
    assert set(counts) == own
    assert max(counts.values()) - min(counts.values()) <= 1


@pytest.mark.parametrize("cid", list(CATS))
def test_tasks_and_lesson_have_one_correct_answer_and_bilmayman(cid):
    c = CATS[cid]
    assert len(c["tasks"]) == 4 and len(c["lesson"]["questions"]) == 2 and c["lesson"]["text"]
    for t in c["tasks"] + c["lesson"]["questions"]:
        ids = [o["id"] for o in t["options"]]
        assert len(ids) == 5 and t["options"][-1]["label"] == "Bilmayman"
        assert t["correct"] in ids[:4]


def test_style_and_readiness_have_none_option():
    assert len(DATA["style"]) == 5 and len(DATA["readiness"]) == 3
    for q in DATA["style"] + DATA["readiness"]:
        assert q["options"][-1]["label"] == NONE


def test_public_payloads_hide_correct_answers_and_tags():
    blob = json.dumps(dv2.discovery_questions_public()) + json.dumps(
        [dv2.deep_questions_public([c]) for c in CATS])
    assert '"correct"' not in blob and '"catalog":' not in blob and '"career":' not in blob


def test_no_percent_or_money_in_user_facing_statements():
    for cid in CATS:
        r = dv2.score_deep([cid], {q["id"]: q["correct"] for q in CATS[cid]["tasks"]})
        text = json.dumps(dv2.public_result(r), ensure_ascii=False)
        assert not re.search(r"\d+\s*%", text)


# ── Discovery scoring ──

def _discovery(picks):
    """picks: list of catalog IDs (or None) in question order."""
    out = {}
    for q, cat in zip(DATA["discovery"]["questions"], picks):
        opt = next(o for o in q["options"] if o["catalog"] == cat)
        out[q["id"]] = opt["id"]
    return out


def _cat_order_for(target):
    """For each discovery question, pick target when present, else None."""
    return [target if any(o["catalog"] == target for o in q["options"]) else None
            for q in DATA["discovery"]["questions"]]


def test_discovery_clear_when_one_catalog_has_four():
    r = dv2.score_discovery(_discovery(_cat_order_for("software")))
    assert r["status"] == "clear" and [c["id"] for c in r["catalogs"]] == ["software"]
    assert r["_points"]["software"] == 4 and r["unmeasured"] == 5


def test_discovery_all_bilmayman_is_unclear_not_zero_verdict():
    r = dv2.score_discovery(_discovery([None] * 9))
    assert r["status"] == "unclear" and r["catalogs"] == [] and r["unmeasured"] == 9


def test_discovery_tie_at_three_gives_two_catalogs():
    qs = DATA["discovery"]["questions"]
    for a in CATS:
        for b in CATS:
            if a >= b:
                continue
            only_a = [q for q in qs if a in {o["catalog"] for o in q["options"]} and b not in {o["catalog"] for o in q["options"]}]
            only_b = [q for q in qs if b in {o["catalog"] for o in q["options"]} and a not in {o["catalog"] for o in q["options"]}]
            if len(only_a) >= 3 and len(only_b) >= 3:
                pick_a = {q["id"] for q in only_a[:3]}
                pick_b = {q["id"] for q in only_b[:3]}
                picks = [a if q["id"] in pick_a else b if q["id"] in pick_b else None for q in qs]
                r = dv2.score_discovery(_discovery(picks))
                assert r["status"] == "two" and {c["id"] for c in r["catalogs"]} == {a, b}
                return
    raise AssertionError("no catalog pair without shared questions")


# ── Deep scoring ──

def _deep_answers(cid, career, tasks_correct=True):
    c = CATS[cid]
    ans = {}
    for q in c["questions"]:
        opt = next((o for o in q["options"] if o["career"] == career), q["options"][-1])
        ans[q["id"]] = opt["id"]
    for q in DATA["style"] + DATA["readiness"]:
        ans[q["id"]] = q["options"][0]["id"]
    for t in c["tasks"] + c["lesson"]["questions"]:
        ans[t["id"]] = t["correct"] if tasks_correct else t["options"][-1]["id"]
    return ans


@pytest.mark.parametrize("cid", list(CATS))
def test_deep_consistent_person_gets_their_career(cid):
    for car in CATS[cid]["careers"]:
        r = dv2.score_deep([cid], _deep_answers(cid, car["id"]))
        assert r["status"] == "clear" and r["careers"][0]["id"] == car["id"], (cid, car["id"])
        assert r["careers"][0]["has_roadmap"] is True


def test_deep_all_bilmayman_is_unclear_and_no_negative_conclusion():
    cid = "software"
    ans = _deep_answers(cid, None, tasks_correct=False)
    r = dv2.score_deep([cid], ans)
    assert r["status"] == "unclear" and r["careers"] == []
    assert all(t["state"] == "unmeasured" for t in r["evidence"]["tasks"])
    text = " ".join(r["evidence"]["statements"]).lower()
    assert "rivojlanadi" in text
    assert not any(w in text for w in ("zaif", "past", "qobiliyatingiz yo‘q", "mos emas"))


def test_deep_task_evidence_ladder():
    cid = "data_ai"
    ans = _deep_answers(cid, "data_analytics")
    r = dv2.score_deep([cid], ans, {t["id"]: "easy_interesting" for t in CATS[cid]["tasks"]})
    assert r["evidence"]["level"] == "first_evidence"
    assert any("qiziqish signali" in s for s in r["evidence"]["statements"])
    wrong = {**ans, **{t["id"]: next(o["id"] for o in t["options"][:4] if o["id"] != t["correct"]) for t in CATS[cid]["tasks"]}}
    r2 = dv2.score_deep([cid], wrong)
    assert r2["evidence"]["level"] == "not_enough"
    assert all(t["state"] == "not_yet" for t in r2["evidence"]["tasks"])


def test_two_catalogs_serve_six_plus_five():
    ids = dv2.deep_question_ids(["software", "data_ai"])
    assert len(ids) == 11
    assert sum(i.startswith("software_") for i in ids) == 6
    assert sum(i.startswith("data_ai_") for i in ids) == 5


def test_invalid_catalogs_rejected():
    for bad in ([], ["nope"], ["software", "data_ai", "seo"]):
        with pytest.raises(ValueError):
            dv2.validate_catalog_ids(bad)


# ── API flow (real SQLite DB, subprocess) ──

def test_diagnostic_v2_api_flow(tmp_path):
    script = Path(__file__).parent / "flows" / "diagnostic_v2_flow.py"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'dv2.db'}", "BOT_TOKEN": ""}
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=120,
                       cwd=Path(__file__).parent.parent)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert "DIAGNOSTIC V2 OK" in r.stdout
