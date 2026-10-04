"""BL-14 read-only threshold audit."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from threshold_audit import count_at, count_histogram, quantiles, summarize  # noqa: E402


def test_five_is_a_ceiling_not_a_quota():
    assert count_at([90, 80, 70, 60, 55, 52, 51], 50) == 5
    assert count_at([90, 40, 30], 50) == 1
    assert count_at([45, 40], 50) == 0
    assert count_at([], 50) == 0
    assert count_at([50.0], 50) == 1  # threshold is inclusive (score >= T)


def test_histogram_counts_every_session_once():
    h = count_histogram([[90, 80], [40], [], [70, 65, 60, 58, 56, 54]], 50)
    assert h == {"0": 2, "1": 0, "2": 1, "3": 0, "4": 0, "5": 1}


def test_quantiles_and_empty():
    assert quantiles([]) is None
    q = quantiles([10, 20, 30, 40, 50])
    assert (q["min"], q["median"], q["max"], q["n"]) == (10, 30, 50, 5)


def test_summarize_reports_both_bases_without_choosing():
    cands = [[{"fit": 70, "composite_score": 60}, {"fit": 50, "composite_score": 45}], []]
    s = summarize(cands)
    assert set(s["thresholds"]) == {"fit", "composite_score"}
    assert s["thresholds"]["fit"]["50"] == {"0": 1, "1": 0, "2": 1, "3": 0, "4": 0, "5": 0}
    assert s["thresholds"]["composite_score"]["50"] == {"0": 1, "1": 1, "2": 0, "3": 0, "4": 0, "5": 0}
    assert s["eligible_careers_per_session"] == {"0": 1, "2": 1}


def test_threshold_audit_on_seeded_db(tmp_path):
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 't.db'}", "QADAM_DB_READ_ONLY": "1"}
    r = subprocess.run([sys.executable, "tests/flows/threshold_audit_flow.py"], capture_output=True, text=True,
                       env=env, timeout=180, cwd=ROOT)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-4000:]
    assert "THRESHOLD AUDIT OK" in r.stdout


def test_refuses_without_read_only_flag(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "QADAM_DB_READ_ONLY"}
    env["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_path / 'x.db'}"
    r = subprocess.run([sys.executable, "scripts/threshold_audit.py"], capture_output=True, text=True, env=env,
                       timeout=60, cwd=ROOT)
    assert r.returncode != 0 and "refused" in (r.stderr + r.stdout)
