"""Read-only ranking audit (PM Variant 2, 2026-10-04)."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_ranking_audit_on_simulated_legacy_db(tmp_path):
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'r.db'}", "QADAM_DB_READ_ONLY": "1"}
    r = subprocess.run([sys.executable, "tests/flows/ranking_audit_flow.py"], capture_output=True, text=True,
                       env=env, timeout=180, cwd=ROOT)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-4000:]
    assert "RANKING AUDIT OK" in r.stdout


def test_refuses_without_read_only_flag(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "QADAM_DB_READ_ONLY"}
    env["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_path / 'x.db'}"
    r = subprocess.run([sys.executable, "scripts/ranking_audit.py"], capture_output=True, text=True, env=env,
                       timeout=60, cwd=ROOT)
    assert r.returncode != 0 and "refused" in (r.stderr + r.stdout)
