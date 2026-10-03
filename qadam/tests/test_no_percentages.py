"""P0-1 — no percentages or verdicts in user-facing output (PM direction 2026-10-03)."""
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest
from pydantic import ValidationError

from backend.ai.personalizer import AIExplanation, _build_user_prompt, _fallback, contains_forbidden_text
from backend.data_loader import load_discovery_questions, load_taxonomy
from backend.engine.levels import evidence_level
from backend.engine.ranking import rank_careers
from backend.services.discovery_service import compute_signals_from_discovery

DISCOVERY = load_discovery_questions()["questions"]
BOT_START = Path(__file__).parent.parent / "bot" / "handlers" / "start.py"


def ranked(constraints):
    rng = random.Random(1)
    answers = []
    for q in DISCOVERY:
        if q["type"] == "likert":
            answers.append({"question_id": q["id"], "answer_id": "likert_5", "answer_value": 5})
        else:
            o = rng.choice(q["options"])
            answers.append({"question_id": q["id"], "answer_id": o["id"], "answer_value": o.get("value", 3)})
    signals = compute_signals_from_discovery(answers, DISCOVERY)
    return rank_careers(signals, load_taxonomy(), constraints, top_n=5)["ranked"]


CTX = {"time": "1h", "device": "smartphone_only", "english": "a2"}


def test_ranked_items_carry_levels():
    items = ranked(CTX)
    assert items
    for item in items:
        assert item["evidence_level"] in {"enough", "partial", "insufficient"}
        assert item["context_status"] in {"clear", "barriers", "unknown"}
        assert item["evidence_level"] == evidence_level(item["coverage"])


@pytest.mark.parametrize("ctx", [CTX, None])
def test_fallback_explanation_has_no_percentages_or_verdicts(ctx):
    out = _fallback(ranked(ctx))
    texts = [out["summary"], out["next_step_emphasis"], *out["why_this_fits"], *out["risks"]]
    for t in texts:
        assert not contains_forbidden_text(t), t


def test_ai_output_with_percentages_is_rejected():
    good = {
        "summary": "Javoblaringizga ko'ra signallaringiz SMM yo'nalishiga yaqinroq ko'rinadi.",
        "why_this_fits": ["Odamlarni tushunish signali kuchli.", "Ijodiy ish yoqadi."],
        "risks": [],
        "next_step_emphasis": "Bugun bitta kichik post tayyorlab ko'ring.",
    }
    AIExplanation.model_validate(good)
    for bad in ("SMM sizga 100% mos keladi va bu aniq.", "Fit: 87, readiness yuqori, eng mos yo'nalish."):
        with pytest.raises(ValidationError):
            AIExplanation.model_validate({**good, "summary": bad})


def test_ai_prompt_contains_no_scores():
    items = ranked(CTX)
    profile = {"user_empathy": {"score": 0.9}, "analytical": {"score": 0.4}}
    prompt = _build_user_prompt(profile, items, "medium")
    assert '"fit"' not in prompt and '"readiness"' not in prompt
    assert "0.9" not in prompt and "%" not in prompt


def test_pdf_has_no_percentages():
    from backend.engine.roadmap import build_full_report
    from backend.pdf_report import _build_career_html

    report = build_full_report(ranked(CTX), CTX, load_taxonomy())
    for idx, c in enumerate(report["careers"], 1):
        html = _build_career_html({**c, "_idx": idx})
        header = html.split("</div>", 1)[0]
        # Score percentages only; roadmap editorial text (e.g. "20% funksiya") is content, not a score.
        assert "%" not in re.sub(r'width="\d+%"', "", header), header
        assert "FIT" not in html and "Ready:" not in html
        assert not re.search(r"</b> — \d+%</li>", html)


def test_bot_texts_make_no_fit_claims():
    text = BOT_START.read_text(encoding="utf-8")
    for pattern in (r"Fit va Readiness", r"Top-5 mos", r"Sizga mos", r"eng mos"):
        assert not re.search(pattern, text), pattern


MINIAPP = Path(__file__).parent.parent.parent / "qadam-miniapp"


def test_miniapp_shows_no_score_numbers():
    """Mini App must not render fit/readiness/signal numbers (admin screens excluded)."""
    files = [
        p for d in ("app", "components") for p in (MINIAPP / d).rglob("*.tsx")
        if "admin" not in p.parts
    ]
    assert files
    patterns = [
        r"Math\.round\([^)]*\b(fit|readiness|score|value)\b",
        r">\s*(Fit|Readiness)\s*<",
        r"Top-\{?[^}]*\}? mos|eng mos|Sizga mos|Fit \+ Readiness|Fit va Readiness",
    ]
    for f in files:
        text = f.read_text(encoding="utf-8")
        for pattern in patterns:
            assert not re.search(pattern, text), f"{f.relative_to(MINIAPP)}: {pattern}"


# ── PM Q3: no unsupported salary in user-facing output ──────────────────────

from backend.engine.public_output import UNSUPPORTED_KEYS, strip_unsupported

SALARY_RE = re.compile(r"salary|maosh|so'm/oy|\$\d|income_factors|junior_salary|remote_salary", re.IGNORECASE)


def test_strip_unsupported_is_deep():
    data = {"b_point": {"junior_salary_uzs": "3-6 mln", "outcomes": ["x"]},
            "careers": [{"salary_usd": {"junior": 1}, "uz": "SMM"}], "income_factors": [1]}
    assert strip_unsupported(data) == {"b_point": {"outcomes": ["x"]}, "careers": [{"uz": "SMM"}]}


def test_report_and_pdf_carry_no_salary():
    from backend.engine.roadmap import build_full_report
    from backend.pdf_report import _build_career_html

    report = build_full_report(ranked(CTX), CTX, load_taxonomy())
    assert not (UNSUPPORTED_KEYS & set(json_keys(report)))
    for idx, c in enumerate(report["careers"], 1):
        assert not SALARY_RE.search(_build_career_html({**c, "_idx": idx}))


def test_miniapp_shows_no_salary():
    for f in (p for d in ("app", "components") for p in (MINIAPP / d).rglob("*.tsx") if "admin" not in p.parts):
        text = f.read_text(encoding="utf-8")
        assert not re.search(r"salary|IncomeSection|Daromad salohiyati", text), f.relative_to(MINIAPP)


def json_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from json_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from json_keys(v)


def test_money_inside_editorial_lists_is_removed():
    stage = {"constraints": [["Narx qancha?", "Mahalliy bozor: 3-6 mln"], ["Reject", "Davom eting"]],
             "outcomes": ["Junior lavozim", "$300-600/oy remote"]}
    assert strip_unsupported(stage) == {"constraints": [["Reject", "Davom eting"]], "outcomes": ["Junior lavozim"]}


# ── PM gate: catalog ≠ recommendation ───────────────────────────────────────

def test_no_promise_to_rank_all_catalog_careers():
    """Ranking covers only careers with a roadmap KB; texts must not promise 25 or a fixed top-5."""
    texts = [BOT_START.read_text(encoding="utf-8")] + [
        p.read_text(encoding="utf-8")
        for d in ("app", "components") for p in (MINIAPP / d).rglob("*.tsx") if "admin" not in p.parts
    ]
    for text in texts:
        assert not re.search(r"25\+? ta kasb|25\+? kasbiy|5 ta yo'nalish|Top-5", text)
    for page in ("preliminary", "career-intelligence"):
        src = (MINIAPP / "app" / page / "page.tsx").read_text(encoding="utf-8")
        assert "yo&apos;l xaritasi tayyor bo&apos;lgan yo&apos;nalishlar ko&apos;rib chiqiladi" in src, page


# ── PM gate: evidence-less factual claims from the roadmap KB ───────────────

from backend.engine.public_output import CLAIMS_AUDIT


def _kb_strings():
    import json as _json
    data = Path(__file__).parent.parent / "backend" / "data"
    for name in CLAIMS_AUDIT["scope"]:
        stack = [_json.loads((data / name).read_text(encoding="utf-8"))]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
            elif isinstance(o, str):
                yield o


def test_audit_entries_exist_in_the_kb():
    texts = set(_kb_strings())
    for claim in CLAIMS_AUDIT["claims"]:
        assert claim["text"] in texts, claim["text"]


def test_no_statistic_ratio_or_percent_claim_left_unaudited():
    audited = {c["text"] for c in CLAIMS_AUDIT["claims"]}
    risky = re.compile(r"\d+\s*%|→\s*\d|\d[\d\s-]*(mln|so'm)|\$\d|→ 1 |\d.*— normal")
    for text in set(_kb_strings()):
        if risky.search(text) and "salary" not in text:
            assert text in audited or text.startswith("$") or "mln so'm" in text, text


def test_user_facing_roadmaps_carry_no_audited_claims():
    from backend.engine.roadmap import build_full_report
    from backend.engine.roadmap_engine import build_roadmap as build_v1
    import json as _json

    report = build_full_report(ranked(CTX), CTX, load_taxonomy())
    blobs = [_json.dumps(report, ensure_ascii=False)]
    tax = load_taxonomy()
    for cluster_key, cluster in tax["clusters"].items():
        for slug, career in cluster["careers"].items():
            blobs.append(_json.dumps(strip_unsupported(build_v1(slug, {**career, "cluster": cluster_key}, {})), ensure_ascii=False))
    text = "\n".join(blobs)
    for claim in CLAIMS_AUDIT["claims"]:
        assert claim["text"] not in text, claim["text"]


def test_filtering_never_drops_a_whole_career_or_stage():
    """Regression: an earlier recursive money check removed a whole career (SMM Manager)
    from the PDF because one nested line quoted money. Only that line may go."""
    from backend.engine.roadmap import build_full_report

    items = ranked(CTX)
    report = build_full_report(items, CTX, load_taxonomy())
    assert [c["career"]["id"] for c in report["careers"]] == [i["career_id"] for i in items]
    stripped = strip_unsupported(report)
    assert [c["career"]["id"] for c in stripped["careers"]] == [i["career_id"] for i in items]
    for before, after in zip(report["careers"], stripped["careers"]):
        stages = (before["roadmap"].get("path") or {}).get("stages", [])
        assert len(stages) == len((after["roadmap"].get("path") or {}).get("stages", []))
    smm = {"stages": [{"name": "JOB READY", "constraints": [{"problem": "Narx qancha?", "solution": "Mahalliy bozor: 3-6 mln"},
                                                             {"problem": "Reject", "solution": "Davom eting"}]}]}
    assert strip_unsupported(smm) == {"stages": [{"name": "JOB READY", "constraints": [{"problem": "Reject", "solution": "Davom eting"}]}]}
