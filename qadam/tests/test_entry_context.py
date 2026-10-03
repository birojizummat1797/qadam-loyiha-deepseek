"""Server-side validation of website entry context (deep-link spec v2)."""
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.entry_context import (  # noqa: E402
    ENTRY_CONTEXT_WINDOW, ENTRY_STATES, WEB_SOURCES,
    pick_entry_context, validate_entry_context,
)

NOW = datetime(2026, 10, 3, 12, 0, tzinfo=timezone.utc)
GOOD = {"channel": "web", "v": 2, "src": "hr", "placement": "hero", "state": "start"}


def test_valid_v2_payload_is_kept():
    assert validate_entry_context(GOOD) == GOOD


def test_valid_v1_payload_has_no_state():
    p = {"channel": "web", "v": 1, "src": "cd", "career": "data_analytics"}
    assert validate_entry_context(p) == {
        "channel": "web", "v": 1, "src": "cd", "placement": "career_detail", "career": "data_analytics",
    }


@pytest.mark.parametrize("payload", [
    None, "w2-hr-bs", [], {},
    {**GOOD, "channel": "ads"},
    {**GOOD, "src": "zz"},
    {**GOOD, "v": 3},
    {**GOOD, "v": "2"},
])
def test_invalid_payloads_are_rejected(payload):
    assert validate_entry_context(payload) is None


def test_unknown_state_and_career_are_dropped_not_passed_through():
    dirty = {**GOOD, "state": "admin", "career": "<script>", "user_phone": "+998", "placement": "spoofed"}
    clean = validate_entry_context(dirty)
    assert clean == {"channel": "web", "v": 2, "src": "hr", "placement": "hero"}


def test_states_are_the_three_homepage_situations():
    assert ENTRY_STATES == {"bs": "start", "al": "switch", "os": "grow"}


def test_pick_newest_valid_entry_within_window():
    rows = [
        (NOW - timedelta(minutes=5), {"channel": "web", "v": 2, "src": "zz"}),  # invalid → skipped
        (NOW - timedelta(minutes=10), GOOD),
        (NOW - timedelta(minutes=20), {**GOOD, "state": "grow"}),
    ]
    assert pick_entry_context(rows, now=NOW)["state"] == "start"


def test_entries_outside_window_are_ignored():
    old = NOW - ENTRY_CONTEXT_WINDOW - timedelta(seconds=1)
    assert pick_entry_context([(old, GOOD)], now=NOW) is None
    assert pick_entry_context([(None, GOOD)], now=NOW) is None


def test_naive_sqlite_timestamps_are_treated_as_utc():
    naive = (NOW - timedelta(hours=1)).replace(tzinfo=None)
    assert pick_entry_context([(naive, GOOD)], now=NOW) == GOOD


def test_bot_uses_the_same_whitelists():
    from bot import deeplink

    assert deeplink.WEB_SOURCES is WEB_SOURCES
    assert deeplink.ENTRY_STATES is ENTRY_STATES


def test_full_flow_bot_start_to_discovery_session(tmp_path):
    """Real SQLite, real handlers: /start w2 → events → discovery session meta.

    Runs in a subprocess because other test modules import the models under a
    different module name, which would register the tables twice.
    """
    script = Path(__file__).parent / "flows" / "entry_context_flow.py"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'flow.db'}"}
    result = subprocess.run(
        [sys.executable, str(script)], cwd=Path(__file__).parent.parent,
        env=env, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "FLOW OK" in result.stdout
