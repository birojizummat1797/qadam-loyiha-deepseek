"""Batch 2 — Discovery testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import DiscoverySession, DiscoveryAnswer, DiscoverySignal
from data_loader import load_discovery_questions
from services.discovery_service import (
    get_next_question, compute_signals_from_discovery, _extract_constraints,
)


def test_questions_count():
    q = load_discovery_questions()
    assert len(q["questions"]) == 13


def test_next_question():
    questions = load_discovery_questions()["questions"]
    nq = get_next_question({"current_q_index": 0}, questions)
    assert nq is not None
    assert nq["id"] == "DISC_Q01"
    assert nq["total"] == 13
    assert nq["index"] == 0


def test_next_question_at_end():
    questions = load_discovery_questions()["questions"]
    nq = get_next_question({"current_q_index": 13}, questions)
    assert nq is None


def test_signals_computation_choice():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q02", "answer_id": "DISC_Q02_A01", "answer_value": 4},
    ]
    signals = compute_signals_from_discovery(answers, questions)
    # technical_interest = 1.5 * 7.5 = 11.25 → weighted avg 11.25
    ti = signals["technical_interest"]
    assert ti["value"] is not None
    assert ti["value"] == 11.25 or ti["value"] > 8
    assert ti["coverage"] == 1
    assert ti["evidence_state"] == "insufficient"


def test_signals_likert():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q03", "answer_id": "x", "answer_value": 5},
    ]
    signals = compute_signals_from_discovery(answers, questions)
    ps = signals["problem_solving"]
    assert ps["value"] == 10.0  # 10 * 1.0
    assert ps["evidence_state"] == "insufficient"


def test_constraints_extraction():
    answers = [
        {"question_id": "DISC_Q11", "answer_id": "DISC_Q11_A03", "answer_value": 3},
        {"question_id": "DISC_Q12", "answer_id": "DISC_Q12_A01", "answer_value": 4},
        {"question_id": "DISC_Q13", "answer_id": "DISC_Q13_A03", "answer_value": 3},
    ]
    c = _extract_constraints(answers)
    assert c["time"] == "2_3h"
    assert c["device"] == "laptop"
    assert c["english"] == "b1"


def test_model_columns_discovery():
    cols = {c.name for c in DiscoverySession.__table__.columns}
    for f in ("user_id", "status", "current_q_index", "question_version"):
        assert f in cols

    cols = {c.name for c in DiscoveryAnswer.__table__.columns}
    for f in ("session_id", "question_id", "answer_id", "answer_value"):
        assert f in cols

    cols = {c.name for c in DiscoverySignal.__table__.columns}
    for f in ("session_id", "signal_key", "value", "trust", "evidence_state"):
        assert f in cols
