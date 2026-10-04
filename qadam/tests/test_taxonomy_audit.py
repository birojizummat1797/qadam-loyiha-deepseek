"""Read-only taxonomy drift audit (DB vs taxonomy_v1.json)."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from taxonomy_audit import compare  # noqa: E402


def _tax(version, signals, cluster="software"):
    return {"version": version, "clusters": {cluster: {"uz": "Dasturlash", "careers": {
        "x": {"uz": "X", "signals": signals, "prerequisites": {}, "learning_months": 4, "pathway_type": "entry"}}}}}


def test_identical():
    r = compare(_tax("v1.0", {"a": 1}), _tax("v2.2", {"a": 1}))
    assert r["identical"] and r["careers_differing"] == 0


def test_reports_field_and_cluster_drift():
    r = compare(_tax("v1.0", {"a_typo": 1}, "old"), _tax("v2.2", {"a": 1}))
    assert not r["identical"]
    assert set(r["diffs"]["x"]) == {"signals", "cluster"}


def test_refuses_without_read_only_flag(tmp_path):
    env = {k: v for k, v in os.environ.items() if k != "QADAM_DB_READ_ONLY"}
    env["DATABASE_URL"] = f"sqlite+aiosqlite:///{tmp_path / 'x.db'}"
    r = subprocess.run([sys.executable, "scripts/taxonomy_audit.py"], capture_output=True, text=True, env=env,
                       timeout=60, cwd=ROOT)
    assert r.returncode != 0 and "refused" in (r.stderr + r.stdout)
