"""P0 — signal/fit/readiness invariants (PM direction 2026-10-03).

- Signal value is a weighted mean Σ(v·w)/Σw and always stays in [0, 10].
- Fit and readiness are computed independently and stay in [0, 100].
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest

from backend.data_loader import load_deep_diagnostic, load_discovery_questions, load_taxonomy
from backend.engine.fit import calculate_fit
from backend.engine.readiness import calculate_readiness
from backend.engine.signals import SIGNAL_KEYS, aggregate_signal
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions, merge_signals
from backend.services.discovery_service import _extract_constraints, compute_signals_from_discovery

DISCOVERY = load_discovery_questions()["questions"]
DEEP = flatten_questions(load_deep_diagnostic())
CAREERS = [c for cl in load_taxonomy()["clusters"].values() for c in cl["careers"].values()]


def discovery_answers(rng=None, likert=None):
    out = []
    for q in DISCOVERY:
        if q["type"] == "likert":
            v = likert if likert is not None else rng.randint(1, 5)
            out.append({"question_id": q["id"], "answer_id": f"likert_{v}", "answer_value": v})
        else:
            o = rng.choice(q["options"]) if rng else q["options"][0]
            out.append({"question_id": q["id"], "answer_id": o["id"], "answer_value": o.get("value", 3)})
    return out


def deep_answers(rng=None, likert=None):
    return [
        {"question_id": q["id"], "answer_value": likert if likert is not None else rng.randint(1, 5)}
        for q in DEEP
    ]


def assert_signals_in_range(signals):
    assert set(signals) == set(SIGNAL_KEYS)
    for key, s in signals.items():
        if s["value"] is None:
            assert s["evidence_state"] == "unmeasured", key
            continue
        assert 0.0 <= s["value"] <= 10.0, (key, s["value"])
        assert 0.0 <= s["trust"] <= 1.0, (key, s["trust"])


def test_weighted_mean_formula():
    # Σ(v·w)/Σw = (10·1.5 + 0·0.5) / 2.0 = 7.5
    assert aggregate_signal([(10.0, 1.5), (0.0, 0.5)])["value"] == 7.5
    # A single max answer is the max value whatever its weight (was 15 before the fix).
    assert aggregate_signal([(10.0, 1.5)])["value"] == 10.0
    assert aggregate_signal([(10.0, 0.5)])["value"] == 10.0
    assert aggregate_signal([])["evidence_state"] == "unmeasured"
    assert aggregate_signal([(10.0, 0.0)])["evidence_state"] == "unmeasured"


@pytest.mark.parametrize("likert", [1, 5])
def test_extreme_answers_stay_in_range(likert):
    rng = random.Random(likert)
    disc = compute_signals_from_discovery(discovery_answers(rng, likert), DISCOVERY)
    deep = compute_signals(deep_answers(likert=likert), DEEP)
    for signals in (disc, deep, merge_signals(disc, deep)):
        assert_signals_in_range(signals)


def test_all_max_deep_answers_give_max_values():
    deep = compute_signals(deep_answers(likert=5), DEEP)
    for key, s in deep.items():
        if s["value"] is not None:
            assert s["value"] == 10.0, key


@pytest.mark.parametrize("seed", range(200))
def test_random_full_flow_invariants(seed):
    rng = random.Random(seed)
    d_ans = discovery_answers(rng)
    disc = compute_signals_from_discovery(d_ans, DISCOVERY)
    merged = merge_signals(disc, compute_signals(deep_answers(rng), DEEP))
    assert_signals_in_range(disc)
    assert_signals_in_range(merged)
    constraints = _extract_constraints(d_ans)
    for career in CAREERS:
        fit = calculate_fit(merged, career)
        if fit["fit"] is not None:
            assert 0.0 <= fit["fit"] <= 100.0
        assert 0.0 <= fit["coverage"] <= 1.0
        assert 0.0 <= fit["confidence"] <= 1.0
        r = calculate_readiness(constraints, career.get("prerequisites", {}))
        assert 0.0 <= r["readiness"] <= 100.0


def test_fit_clamps_legacy_out_of_range_values():
    # Sessions stored before the fix may hold values above 10 in the DB.
    career = {"signals": {"technical_interest": 5, "logical_thinking": 5}}
    legacy = {
        "technical_interest": {"value": 15.0, "trust": 1.0, "evidence_state": "measured"},
        "logical_thinking": {"value": 12.5, "trust": 1.0, "evidence_state": "measured"},
    }
    assert calculate_fit(legacy, career)["fit"] == 100.0


def test_fit_and_readiness_are_independent():
    """Ability (fit) and conditions (readiness) must not be mixed (PM P0-4)."""
    import inspect

    assert "constraints" not in inspect.signature(calculate_fit).parameters
    assert "signals" not in inspect.signature(calculate_readiness).parameters
    career = next(c for c in CAREERS if c["prerequisites"].get("device") == "required")
    ready = calculate_readiness({"device": "laptop", "english": "c1", "time": "full_time"}, career["prerequisites"])
    blocked = calculate_readiness({"device": "none", "english": "none", "time": "lt_1h"}, career["prerequisites"])
    assert ready["readiness"] == 100.0
    assert blocked["readiness"] < ready["readiness"]
    assert blocked["has_hard_barrier"] is True
