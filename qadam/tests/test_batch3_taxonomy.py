"""Batch 3 — Taxonomy + Evidence testlari (DB'siz)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import SignalEvidence, TaxonomyVersion, Career
from data_loader import load_discovery_questions
from services.discovery_service import extract_evidence


def test_signal_evidence_columns():
    cols = {c.name for c in SignalEvidence.__table__.columns}
    for f in ("session_id", "signal_key", "question_id", "answer_id",
              "contribution", "evidence_type"):
        assert f in cols


def test_taxonomy_version_columns():
    cols = {c.name for c in TaxonomyVersion.__table__.columns}
    for f in ("version", "notes", "is_active", "published_at"):
        assert f in cols


def test_career_columns():
    cols = {c.name for c in Career.__table__.columns}
    for f in ("taxonomy_version_id", "slug", "title_uz", "cluster",
              "required_signals", "prerequisites", "salary_usd"):
        assert f in cols


def test_extract_evidence_likert():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q03", "answer_id": "", "answer_value": 5},
    ]
    ev = extract_evidence(answers, questions)
    # DISC_Q03 → problem_solving (1.0), logical_thinking (0.8)
    sigs = {e["signal_key"] for e in ev}
    assert "problem_solving" in sigs
    assert "logical_thinking" in sigs
    # Contribution tekshirish
    ps = next(e for e in ev if e["signal_key"] == "problem_solving")
    assert ps["contribution"] == 10.0  # 10 * 1.0
    assert ps["evidence_type"] == "direct"


def test_extract_evidence_choice():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q02", "answer_id": "DISC_Q02_A01", "answer_value": 4},
    ]
    ev = extract_evidence(answers, questions)
    sigs = {e["signal_key"] for e in ev}
    assert "technical_interest" in sigs
    assert "logical_thinking" in sigs


def test_extract_evidence_empty():
    questions = load_discovery_questions()["questions"]
    assert extract_evidence([], questions) == []
