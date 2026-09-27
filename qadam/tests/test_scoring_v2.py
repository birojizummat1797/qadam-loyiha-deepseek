"""Scoring v2 — PM spec tekshiruvlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.signals import signals_from_answers
from engine.fit import calculate_fit
from engine.readiness import calculate_readiness
from data_loader import load_questions


def test_likert_converts_to_10_scale():
    """Likert 5 → 10.0, 1 → 0.0, 3 → 5.0"""
    from engine.signals import LIKERT_TO_10
    assert LIKERT_TO_10[1] == 0.0
    assert LIKERT_TO_10[3] == 5.0
    assert LIKERT_TO_10[5] == 10.0


def test_unmeasured_not_zero():
    """O'lchanmagan signal → value=None, state='unmeasured'."""
    questions = load_questions()
    signals = signals_from_answers({}, questions)
    for k, v in signals.items():
        assert v["value"] is None
        assert v["evidence_state"] == "unmeasured"
        assert v["trust"] == 0.0


def test_insufficient_with_few_answers():
    """1-2 javob → insufficient, trust=0.6."""
    questions = load_questions()
    # faqat 1 ta javob
    signals = signals_from_answers({"s2_q3": 4}, questions)
    s = signals["technical_interest"]
    assert s["evidence_state"] == "insufficient"
    assert s["trust"] == 0.6
    assert s["value"] is not None  # value bor, lekin trust past


def test_measured_with_3plus_answers():
    """3+ javob → measured, trust=1.0."""
    questions = load_questions()
    # 3 ta javob bir signalga
    answers = {"s2_q1": 4, "s2_q11": 4, "s2_q12": 4, "s2_q18": 4}
    signals = signals_from_answers(answers, questions)
    s = signals["persistence"]
    assert s["evidence_state"] == "measured"
    assert s["trust"] == 1.0
    assert s["coverage"] == 4


def test_fit_formula_100_percent():
    """Signal=10, trust=1.0, weight teng → Fit=100."""
    signals = {
        "logical_thinking": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "persistence": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
    }
    career = {"signals": {"logical_thinking": 5, "problem_solving": 5, "persistence": 5}}
    r = calculate_fit(signals, career)
    assert r["fit"] == 100.0
    assert r["coverage"] == 1.0
    assert r["confidence"] == 1.0


def test_fit_formula_50_percent():
    """Signal=5, trust=1.0 → Fit=50."""
    signals = {
        "logical_thinking": {"value": 5.0, "trust": 1.0, "evidence_state": "measured"},
    }
    career = {"signals": {"logical_thinking": 5}}
    r = calculate_fit(signals, career)
    assert r["fit"] == 50.0


def test_fit_coverage_below_half():
    """Coverage < 0.5 → status='insufficient_coverage'."""
    signals = {
        "logical_thinking": {"value": 8.0, "trust": 1.0, "evidence_state": "measured"},
    }
    # 5 ta signal kerak, faqat 1 ta o'lchangan → coverage=0.2
    career = {"signals": {
        "logical_thinking": 5, "problem_solving": 5, "persistence": 5,
        "attention_to_detail": 5, "analytical": 5,
    }}
    r = calculate_fit(signals, career)
    assert r["coverage"] < 0.5
    assert r["status"] == "insufficient_coverage"


def test_fit_unmeasured_excluded():
    """Unmeasured signal hisobga olinmaydi (0 emas)."""
    signals = {
        "logical_thinking": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": None, "trust": 0.0, "evidence_state": "unmeasured"},
    }
    career = {"signals": {"logical_thinking": 5, "problem_solving": 5}}
    r = calculate_fit(signals, career)
    # faqat logical_thinking hisobga olinadi → Fit=100, coverage=0.5
    assert r["fit"] == 100.0
    assert r["coverage"] == 0.5
    assert r["measured_signals"] == 1
    assert "problem_solving" in r["missing_signals"]


def test_readiness_base_100():
    """Barcha shartlar bajarilsa → Readiness=100."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "b2", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["readiness"] == 100.0
    assert r["p_computer"] == 1.0
    assert r["p_english"] == 1.0
    assert r["p_time"] == 1.0


def test_readiness_no_computer():
    """Device yo'q → P_computer=0.5."""
    r = calculate_readiness(
        constraints={"device": "none", "english": "b1", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_computer"] == 0.5
    assert r["readiness"] == 50.0


def test_readiness_english_gap():
    """English A2 vs B1 kerak → 1 gap → 0.85."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "a2", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_english"] == 0.85
    assert abs(r["readiness"] - 85.0) < 0.01


def test_readiness_time_ratio():
    """User 1h, kerak 2h → 0.5."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "b1", "time": "1h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_time"] == 0.5
    assert r["readiness"] == 50.0
