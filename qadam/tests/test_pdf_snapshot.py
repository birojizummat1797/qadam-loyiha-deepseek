"""PDF snapshot regression (PM merge gate, 2026-10-03).

The PDF is Qadam's Action Document. For a fixed set of answers its HTML must
match the committed snapshot, and must never carry score percentages, unsupported
salary or fake precision. Update the snapshot only on a reviewed content change:

    QADAM_UPDATE_SNAPSHOTS=1 pytest tests/test_pdf_snapshot.py
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.ai.personalizer import _fallback
from backend.data_loader import load_deep_diagnostic, load_discovery_questions, load_taxonomy
from backend.engine.ranking import rank_careers
from backend.engine.roadmap import build_full_report
from backend.pdf_report import build_report_html, generate_pdf
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions, merge_signals
from backend.services.discovery_service import compute_signals_from_discovery, extract_known_constraints

SNAPSHOT = Path(__file__).parent / "snapshots" / "pdf_report_v1.html"
CHOICES = {
    "DISC_Q01": "DISC_Q01_A03", "DISC_Q02": "DISC_Q02_A03", "DISC_Q09": "DISC_Q09_A02",
    "DISC_Q10": "DISC_Q10_A05", "DISC_Q11": "DISC_Q11_A02", "DISC_Q12": "DISC_Q12_A02",
    "DISC_Q13": "DISC_Q13_A02",
}


def fixed_report():
    disc_q = load_discovery_questions()["questions"]
    answers = []
    for q in disc_q:
        if q["type"] == "likert":
            answers.append({"question_id": q["id"], "answer_id": "likert_4", "answer_value": 4})
        else:
            o = next(o for o in q["options"] if o["id"] == CHOICES[q["id"]])
            answers.append({"question_id": q["id"], "answer_id": o["id"], "answer_value": o.get("value", 3)})
    deep_q = flatten_questions(load_deep_diagnostic())
    deep = compute_signals([{"question_id": q["id"], "answer_value": 4 + (i % 2)} for i, q in enumerate(deep_q)], deep_q)
    signals = merge_signals(compute_signals_from_discovery(answers, disc_q), deep)
    constraints = extract_known_constraints(answers)
    taxonomy = load_taxonomy()
    ranked = rank_careers(signals, taxonomy, constraints, top_n=3)["ranked"]
    roadmap = build_full_report(ranked, constraints, taxonomy, signals)
    return {"id": 1, "profile": {}, "roadmap": roadmap, "ai": _fallback(ranked), "created_at": ""}


def html():
    return build_report_html(fixed_report(), date_str="01.01.2026")


def test_pdf_html_matches_snapshot():
    current = html()
    if os.getenv("QADAM_UPDATE_SNAPSHOTS") == "1" or not SNAPSHOT.exists():
        SNAPSHOT.write_text(current, encoding="utf-8")
    assert current == SNAPSHOT.read_text(encoding="utf-8"), (
        "PDF content changed. Review the diff, then update with QADAM_UPDATE_SNAPSHOTS=1."
    )


def test_pdf_has_no_scores_salary_or_fake_precision():
    text = html()
    body = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
    body = re.sub(r'width="\d+%"', "", body)
    body = body.replace("01.01.2026", "")
    for pattern in (
        r"\bFIT\b", r"Ready:", r"\b\d{1,3}(?:\.\d+)?\s*%(?!\s*(funksiya|qiymat))",  # score percentages
        r"salary|so'm/oy|\$\s?\d|\bmln\b|Junior UZ|Remote</p>",                      # unsupported salary
        r"eng mos|aniq mos|kafolat|albatta|100\s*%",                                  # verdicts / fake precision
        r"\b\d+\.\d+\b",                                                             # raw decimals (scores)
    ):
        assert not re.search(pattern, body, re.IGNORECASE), pattern


def test_pdf_evidence_wording_and_action_structure():
    text = html()
    assert "Bu tavsiya, hukm emas — qarorni siz qilasiz." in text
    assert re.search(r"Ma'lumot (yetarli|qisman|yetarli emas)", text)
    for section in ("A NUQTA", "B NUQTA", "Birinchi 3 qadam", "Signallaringizga yaqinroq"):
        assert section in text, section


def test_pdf_generation_succeeds():
    pdf = generate_pdf(fixed_report())
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 5000
