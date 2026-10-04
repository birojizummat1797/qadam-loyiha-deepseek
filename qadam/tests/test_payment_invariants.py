"""Payment invariants — each scenario on its own fresh database (PM requirement #10)."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "flows" / "payment_invariants.py"
SCENARIOS = [
    "confirmed_then_rejected_closes_access",
    "duplicate_confirmation_grants_once",
    "admin_unavailable_leaves_nothing_pending",
    "retry_is_idempotent",
    "non_admin_cannot_decide",
]


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_payment_invariant(tmp_path, scenario):
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'p.db'}", "BOT_TOKEN": "", "ADMIN_CHAT_ID": ""}
    r = subprocess.run([sys.executable, str(SCRIPT), scenario], capture_output=True, text=True, env=env,
                       timeout=120, cwd=Path(__file__).parent.parent)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert f"SCENARIO OK {scenario}" in r.stdout
