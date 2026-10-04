"""Audited --apply: snapshot → apply (one transaction) → dry run 0 → verify (PM approval 2026-10-04)."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_apply_cycle_on_simulated_legacy_db(tmp_path):
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'a.db'}"}
    r = subprocess.run([sys.executable, "tests/flows/apply_recompute_flow.py", str(tmp_path)], capture_output=True,
                       text=True, env=env, timeout=180, cwd=ROOT)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-4000:]
    assert "APPLY FLOW OK" in r.stdout


def test_modes_refuse_wrong_read_only_setting(tmp_path):
    base = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'x.db'}"}
    base.pop("QADAM_DB_READ_ONLY", None)
    snap = str(tmp_path / "s.json")
    for mode, ro in (("snapshot", None), ("verify", None), ("apply", "1")):
        env = dict(base)
        if ro:
            env["QADAM_DB_READ_ONLY"] = ro
        r = subprocess.run([sys.executable, "scripts/apply_recompute.py", mode, snap], capture_output=True, text=True,
                           env=env, timeout=60, cwd=ROOT)
        assert r.returncode != 0 and "refused" in r.stderr + r.stdout, (mode, r.stdout, r.stderr)
