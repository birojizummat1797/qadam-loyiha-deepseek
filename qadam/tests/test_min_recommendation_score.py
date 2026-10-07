"""BL-14 — minimum recommendation score (Founder decision 2026-10-04).

- top_n (5) is a ceiling, not a quota: a list is never padded with careers below the score.
- fit >= 51.0 is recommended; 50.99 is not.
- careers measured but none reaching the score → no_clear_direction (honest message).
- applied to recommendation lists only; the roadmap of an opened career is unaffected.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from backend.data_loader import load_taxonomy
from backend.engine import ranking
from backend.engine.ranking import KB_CAREERS, MIN_RECOMMENDATION_SCORE, rank_careers
from backend.services.discovery_service import build_preliminary_insight

TAXONOMY = load_taxonomy()
KB = sorted(c for cl in TAXONOMY["clusters"].values() for c in cl["careers"] if c in KB_CAREERS)
SIGNAL_KEYS = sorted({k for cl in TAXONOMY["clusters"].values() for car in cl["careers"].values() for k in car["signals"]})


def profile(value):
    return {k: {"value": value, "trust": 1.0, "evidence_state": "measured", "coverage": 3} for k in SIGNAL_KEYS}


def with_fits(monkeypatch, fits: dict):
    """Fix each career's fit; every career is otherwise fully measured."""
    def fake(signals, career):
        cid = next(k for cl in TAXONOMY["clusters"].values() for k, v in cl["careers"].items() if v is career)
        return {"fit": fits.get(cid, 10.0), "coverage": 1.0, "confidence": 1.0,
                "measured_signals": len(career["signals"]), "missing_signals": [], "status": "ok"}
    monkeypatch.setattr(ranking, "calculate_fit", fake)


def test_founder_value():
    assert MIN_RECOMMENDATION_SCORE == 51.0
    assert len(KB) == 5


def test_boundary_is_inclusive_at_51(monkeypatch):
    with_fits(monkeypatch, {KB[0]: 51.0, KB[1]: 50.99, KB[2]: 50.5, KB[3]: 80.0, KB[4]: 51.01})
    r = rank_careers(profile(5), TAXONOMY, {}, top_n=5, min_score=MIN_RECOMMENDATION_SCORE)
    assert {c["career_id"] for c in r["ranked"]} == {KB[0], KB[3], KB[4]}
    below = {e["career_id"] for e in r["excluded"] if e["reason"] == "below_min_score"}
    assert below == {KB[1], KB[2]}
    assert r["no_clear_direction"] is False


def test_five_is_a_ceiling_not_a_quota(monkeypatch):
    with_fits(monkeypatch, {KB[0]: 70.0, KB[1]: 40.0, KB[2]: 30.0, KB[3]: 20.0, KB[4]: 10.0})
    r = rank_careers(profile(5), TAXONOMY, {}, top_n=5, min_score=MIN_RECOMMENDATION_SCORE)
    assert [c["career_id"] for c in r["ranked"]] == [KB[0]]


def test_none_reaching_the_score_is_an_honest_no_clear_direction(monkeypatch):
    with_fits(monkeypatch, {k: 50.99 for k in KB})
    r = rank_careers(profile(5), TAXONOMY, {}, top_n=5, min_score=MIN_RECOMMENDATION_SCORE)
    assert r["ranked"] == [] and r["no_clear_direction"] is True and r["confidence"] == "none"
    assert r["total_candidates"] == 5


def test_nothing_measured_is_not_a_no_clear_direction():
    empty = {k: {"value": None, "trust": 0.0, "evidence_state": "unmeasured", "coverage": 0} for k in SIGNAL_KEYS}
    r = rank_careers(empty, TAXONOMY, {}, top_n=5, min_score=MIN_RECOMMENDATION_SCORE)
    assert r["ranked"] == [] and r["no_clear_direction"] is False  # "not enough data", a different message


@pytest.mark.parametrize("value", [0, 3, 5, 7, 10])
def test_every_recommended_career_reaches_the_score(value):
    r = rank_careers(profile(value), TAXONOMY, {}, top_n=5, min_score=MIN_RECOMMENDATION_SCORE)
    assert all(c["fit"] >= MIN_RECOMMENDATION_SCORE for c in r["ranked"])
    assert len(r["ranked"]) <= 5
    assert r["no_clear_direction"] == (not r["ranked"])


def test_without_min_score_behaviour_is_unchanged():
    """Roadmap (career the user opened) calls rank_careers without min_score."""
    r = rank_careers(profile(1), TAXONOMY, {}, top_n=25)
    assert len(r["ranked"]) == 5 and r["no_clear_direction"] is False
    assert not any(e["reason"] == "below_min_score" for e in r["excluded"])


def test_preliminary_applies_the_score():
    low = build_preliminary_insight(profile(1), [], TAXONOMY)
    assert low["pathways"] == [] and low["no_clear_direction"] is True
    high = build_preliminary_insight(profile(10), [], TAXONOMY)
    assert 1 <= len(high["pathways"]) <= 3 and high["no_clear_direction"] is False
    assert all(p["fit"] >= MIN_RECOMMENDATION_SCORE for p in high["pathways"])


def test_roadmap_endpoint_does_not_pass_min_score():
    src = (Path(__file__).parent.parent / "backend/api/v1/roadmap.py").read_text()
    assert "rank_careers(signals, taxonomy, base, top_n=25)" in src and "min_score" not in src


@pytest.mark.parametrize("path", ["backend/api/v1/career_intelligence.py", "backend/api/v1/deep_diagnostic.py",
                                  "backend/services/discovery_service.py"])
def test_recommendation_surfaces_pass_min_score(path):
    src = (Path(__file__).parent.parent / path).read_text()
    assert src.count("rank_careers(") == src.count("min_score=MIN_RECOMMENDATION_SCORE")
