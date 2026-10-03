"""Batch 6 — Deep Diagnostic testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import (
    DeepDiagnosticSession, DeepDiagnosticAnswer, DeepDiagnosticSignal,
)
from data_loader import load_deep_diagnostic
from services.deep_diagnostic_service import (
    flatten_questions, get_next_question, compute_signals, merge_signals,
)


def test_dd_questions_count():
    data = load_deep_diagnostic()
    flat = flatten_questions(data)
    assert len(flat) == 18


def test_dd_dimensions():
    data = load_deep_diagnostic()
    assert len(data["dimensions"]) == 9


def test_dd_next_question():
    flat = flatten_questions(load_deep_diagnostic())
    nq = get_next_question({"current_q_index": 0}, flat)
    assert nq["id"] == "DD_Q01"
    assert nq["total"] == 18
    assert nq["dimension_uz"] == "Maqsad"


def test_dd_signals_computation():
    flat = flatten_questions(load_deep_diagnostic())
    answers = [
        {"question_id": "DD_Q03", "answer_value": 5},
    ]
    signals = compute_signals(answers, flat)
    ti = signals["technical_interest"]
    assert ti["value"] == 10.0  # vaznli o'rtacha, [0, 10] dan oshmaydi
    assert ti["evidence_state"] == "insufficient"


def test_dd_merge_with_discovery():
    disc = {"analytical": {"value": 8.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    deep = {"analytical": {"value": 9.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    merged = merge_signals(disc, deep)
    # 9*0.7 + 8*0.3 = 6.3 + 2.4 = 8.7
    assert abs(merged["analytical"]["value"] - 8.7) < 0.1
    assert merged["analytical"]["coverage"] == 6


def test_dd_merge_only_discovery():
    disc = {"analytical": {"value": 8.0, "trust": 1.0, "evidence_state": "measured", "coverage": 3}}
    deep = {"analytical": {"value": None, "trust": 0.0, "evidence_state": "unmeasured", "coverage": 0}}
    merged = merge_signals(disc, deep)
    assert merged["analytical"]["value"] == 8.0


def test_dd_models():
    cols = {c.name for c in DeepDiagnosticSession.__table__.columns}
    for f in ("user_id", "discovery_session_id", "status", "current_q_index"):
        assert f in cols

    cols = {c.name for c in DeepDiagnosticAnswer.__table__.columns}
    for f in ("session_id", "question_id", "answer_value"):
        assert f in cols
