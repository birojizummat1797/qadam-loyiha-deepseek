"""P0-7 — Bot → Mini App API → PDF full-flow regression (PM direction 2026-10-03)."""
import os
import subprocess
import sys
from pathlib import Path


def test_full_diagnostic_flow(tmp_path):
    """Runs in a subprocess: other test modules import the models under a
    different package path, which would register the tables twice."""
    script = Path(__file__).parent / "flows" / "diagnostic_full_flow.py"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'flow.db'}",
        "OPENROUTER_API_KEY": "",
        "BOT_TOKEN": "",
    }
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=120,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-4000:]
    assert "FULL FLOW OK" in result.stdout
