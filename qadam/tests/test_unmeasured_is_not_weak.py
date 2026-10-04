"""Invariant: missing / unmeasured ≠ low ability (PM 2026-10-04, after the phone-test finding).

Applies to every diagnostic version: discovery (free), deep diagnostic, fit,
ranking and anything listed to the user as an area to develop. An unmeasured
signal may only ever be shown as "not measured yet" — never as weak, low or a gap.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest

from backend.data_loader import load_deep_diagnostic, load_discovery_questions, load_taxonomy
from backend.engine.fit import calculate_fit
from backend.engine.ranking import rank_careers
from backend.engine.signals import aggregate_signal
from backend.services.discovery_service import build_preliminary_insight, compute_signals_from_discovery
from backend.services import deep_diagnostic_service as dd

TAXONOMY = load_taxonomy()
SIGNAL_KEYS = sorted({k for c in TAXONOMY["clusters"].values() for car in c["careers"].values() for k in car["signals"]})
CAREERS = [car for c in TAXONOMY["clusters"].values() for car in c["careers"].values()]


def measured(v, t=1.0):
    return {"value": v, "trust": t, "evidence_state": "measured"}


UNMEASURED = {"value": None, "trust": 0.0, "evidence_state": "unmeasured"}


def random_profiles(n=200, seed=7):
    rng = random.Random(seed)
    for _ in range(n):
        yield {k: (UNMEASURED if rng.random() < 0.4 else measured(rng.uniform(0, 10), rng.uniform(0.3, 1)))
               for k in SIGNAL_KEYS}


def test_no_answers_means_unmeasured_not_zero():
    assert aggregate_signal([])["value"] is None
    disc = compute_signals_from_discovery([], load_discovery_questions()["questions"])
    assert all(s.get("value") is None for s in disc.values()), "discovery: no answers became a number"
    deep = dd.compute_signals([], dd.flatten_questions(load_deep_diagnostic()))
    assert all(s.get("value") is None for s in deep.values()), "deep: no answers became a number"


@pytest.mark.parametrize("career", CAREERS[:25], ids=lambda c: c.get("uz", "?"))
def test_fit_ignores_unmeasured_signals(career):
    base = {k: measured(6.0) for k in career["signals"]}
    for key in career["signals"]:
        with_gap = {**base, key: UNMEASURED}
        without = {k: v for k, v in base.items() if k != key}
        a, b = calculate_fit(with_gap, career), calculate_fit(without, career)
        assert a["fit"] == b["fit"], f"unmeasured {key} changed fit"
        assert key in a["missing_signals"]


def test_unmeasured_never_ranks_below_measured_low():
    """A career must not drop because a signal is unmeasured instead of measured-low."""
    for profile in random_profiles(50):
        for key in SIGNAL_KEYS:
            if profile[key] is UNMEASURED:
                continue
            low = {**profile, key: measured(0.0)}
            gap = {**profile, key: UNMEASURED}
            for career in CAREERS:
                if key not in career["signals"]:
                    continue
                f_low, f_gap = calculate_fit(low, career)["fit"], calculate_fit(gap, career)["fit"]
                if f_low is not None and f_gap is not None:
                    assert f_gap >= f_low - 1e-9, f"{key}: unmeasured scored below measured 0"


def test_development_areas_contain_only_measured_signals():
    for profile in random_profiles():
        areas = build_preliminary_insight(profile, [], TAXONOMY)["development_areas"]
        for key in areas:
            assert profile[key]["value"] is not None, f"unmeasured {key} listed as development area"


def test_all_unmeasured_profile_gets_no_verdicts():
    profile = {k: UNMEASURED for k in SIGNAL_KEYS}
    insight = build_preliminary_insight(profile, [], TAXONOMY)
    assert insight["development_areas"] == []
    assert insight["signals_top"] == []
    ranked = rank_careers(signals=profile, taxonomy=TAXONOMY, constraints={}, top_n=5)
    for item in ranked["ranked"]:
        assert item.get("fit") is None, "fit invented without evidence"
        assert item["evidence_level"] == "insufficient"
