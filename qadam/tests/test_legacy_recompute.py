"""Legacy results strategy: recompute stored signals from stored answers (dry run by default)."""
import os
import subprocess
import sys
from pathlib import Path


def test_recompute_finds_and_fixes_out_of_range_signals(tmp_path):
    script = Path(__file__).parent / "flows" / "legacy_recompute_flow.py"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'legacy.db'}"}
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env,
                            timeout=120, cwd=Path(__file__).parent.parent)
    assert result.returncode == 0, result.stdout[-2000:] + result.stderr[-3000:]
    assert "LEGACY OK" in result.stdout
