"""18+ age gate and consent (PM decision 2026-10-04, P0)."""
import os
import subprocess
import sys
from pathlib import Path


def test_age_gate_flow(tmp_path):
    script = Path(__file__).parent / "flows" / "age_gate_flow.py"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'age.db'}", "BOT_TOKEN": ""}
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=120,
                       cwd=Path(__file__).parent.parent)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert "AGE GATE OK" in r.stdout
