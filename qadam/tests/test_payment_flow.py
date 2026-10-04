"""Manual payment flow regression (owner request 2026-10-04)."""
import os
import subprocess
import sys
from pathlib import Path


def test_manual_payment_flow(tmp_path):
    """Runs in a subprocess for a fresh database and isolated model imports."""
    script = Path(__file__).parent / "flows" / "payment_flow.py"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'pay.db'}",
        "BOT_TOKEN": "",
        "ADMIN_CHAT_ID": "",
    }
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=120,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-4000:]
    assert "PAYMENT FLOW OK" in result.stdout
