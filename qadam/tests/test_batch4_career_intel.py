"""Batch 4 — Career Intelligence testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.ranking import rank_careers
from engine.fit import calculate_fit
from engine.readiness import calculate_readiness
from data_loader import load_taxonomy


def _fake_signals_top():
    """5 ta measured signal."""
    return {
        "logical_thinking": {"value": 8.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": 7.5, "trust": 1.0, "evidence_state": "measured"},
        "persistence": {"value": 8.5, "trust": 1.0, "evidence_state": "measured"},
        "technical_interest": {"value": 9.0, "trust": 1.0, "evidence_state": "measured"},
        "analytical": {"value": 7.0, "trust": 1.0, "evidence_state": "measured"},
    }


def test_ranking_returns_top5():
    taxonomy = load_taxonomy()
    r = rank_careers(
        signals=_fake_signals_top(),
        taxonomy=taxonomy,
        constraints={"device": "laptop", "english": "b1", "time": "2_3h"},
        top_n=5,
    )
    assert len(r["ranked"]) <= 5
    # Confidence
    assert r["confidence"] in ("high", "medium", "low")


def test_ranking_excludes_low_coverage():
    """Faqat 1 signal measured → coverage < 0.5 → excluded."""
    signals = {
        "logical_thinking": {"value": 9.0, "trust": 1.0, "evidence_state": "measured"},
    }
    taxonomy = load_taxonomy()
    r = rank_careers(signals, taxonomy, {"device": "laptop", "english": "b1", "time": "2_3h"})
    # backend_dev kabi 5+ signal talab qiladigan career'lar chiqmasligi kerak
    for c in r["ranked"]:
        assert c["coverage"] >= 0.5


def test_fit_and_readiness_separate():
    """Fit yuqori, Readiness past — bo'lishi mumkin."""
    signals = _fake_signals_top()
    taxonomy = load_taxonomy()
    # Backend dev
    career = taxonomy["clusters"]["software"]["careers"]["backend_development"]
    fit = calculate_fit(signals, career)
    readiness = calculate_readiness(
        {"device": "smartphone_only", "english": "none", "time": "lt_1h"},
        career.get("prerequisites", {}),
    )
    assert fit["fit"] is not None
    assert readiness["readiness"] < 100
    # Ikkalasi alohida
    assert "readiness" not in fit
    assert "fit" not in readiness


def test_readiness_p_computer_penalty():
    """Device yo'q → 0.5 penalty."""
    signals = _fake_signals_top()
    taxonomy = load_taxonomy()
    career = taxonomy["clusters"]["software"]["careers"]["frontend_development"]

    r_no_device = calculate_readiness(
        {"device": "none", "english": "b1", "time": "2_3h"},
        career["prerequisites"],
    )
    r_laptop = calculate_readiness(
        {"device": "laptop", "english": "b1", "time": "2_3h"},
        career["prerequisites"],
    )
    assert r_no_device["p_computer"] == 0.5
    assert r_laptop["p_computer"] == 1.0
    assert r_no_device["readiness"] < r_laptop["readiness"]


def test_ranking_composite_score():
    """Composite = Fit × (0.7 + 0.3 × Readiness/100)."""
    taxonomy = load_taxonomy()
    r = rank_careers(_fake_signals_top(), taxonomy,
                     {"device": "laptop", "english": "b1", "time": "2_3h"})
    if len(r["ranked"]) >= 2:
        assert r["ranked"][0]["composite_score"] >= r["ranked"][1]["composite_score"]


def test_ranking_confidence_labels():
    taxonomy = load_taxonomy()
    r = rank_careers(_fake_signals_top(), taxonomy,
                     {"device": "laptop", "english": "b1", "time": "2_3h"})
    assert r["confidence"] in ("high", "medium", "low", "none")
