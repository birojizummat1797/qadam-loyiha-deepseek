"""Unmeasured ≠ weak: "Rivojlantirish mumkin" lists measured low signals only (phone test 2026-10-04)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.data_loader import load_taxonomy
from backend.services.discovery_service import build_preliminary_insight

MINIAPP_HOME = Path(__file__).parent.parent.parent / "qadam-miniapp" / "app" / "page.tsx"


def sig(value, trust=1.0):
    return {"value": value, "trust": trust}


def test_unmeasured_signals_are_not_development_areas():
    signals = {
        "logical_thinking": sig(8.0),
        "technical_interest": sig(None, 0.0),
        "attention_to_detail": sig(None, 0.0),
        "user_empathy": sig(3.0),
        "persistence": sig(4.0),
    }
    insight = build_preliminary_insight(signals, [], load_taxonomy())
    assert insight["development_areas"] == ["user_empathy"]


def test_all_unmeasured_gives_no_development_areas():
    signals = {k: sig(None, 0.0) for k in ("logical_thinking", "technical_interest", "analytical")}
    insight = build_preliminary_insight(signals, [], load_taxonomy())
    assert insight["development_areas"] == []


def test_miniapp_home_states_real_discovery_length():
    from backend.data_loader import load_discovery_questions

    n = len(load_discovery_questions()["questions"])
    text = MINIAPP_HOME.read_text(encoding="utf-8")
    assert f'"{n} savol"' in text
    assert "8 savol" not in text
