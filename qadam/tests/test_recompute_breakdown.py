"""Dry-run breakdown: aggregate categories of signal changes (no user data).

Runs in a subprocess: importing the script registers the models under another
package path than other test modules (same reason as test_full_flow).
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CODE = """
import importlib.util, sys
sys.path.insert(0, ".")
spec = importlib.util.spec_from_file_location("rs", "scripts/recompute_signals.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)
old = {"a": {"value": 15.0}, "b": {"value": 0.0}, "c": {"value": 4.0}, "d": {"value": 6.0}, "f": {"value": 7.0}}
new = {"a": {"value": 10.0}, "b": {"value": None}, "c": {"value": 6.5}, "d": {"value": 5.6},
       "e": {"value": 3.0}, "f": {"value": 7.0}}
changed = rs._changed(old, new)
assert changed == ["a", "b", "c", "d", "e"]
b = rs._new_breakdown()
rs._classify(b, old, new, changed)
out = rs._finish(b)
assert out["sessions"] == 1 and out["sessions_changed"] == 1 and out["signals_changed"] == 5
assert out["was_above_10"] == 1
assert out["number_to_unmeasured"] == 1 and out["of_which_stored_zero"] == 1
assert out["unmeasured_to_number"] == 1
assert out["value_shift"] == 2 and out["shift_up"] == 1 and out["shift_down"] == 1
assert out["shift_abs_le_0_5"] == 1 and out["shift_abs_gt_2"] == 1
assert out["shift_abs_max"] == 2.5 and out["shift_abs_mean"] == 1.45
assert "shift_abs_sum" not in out
print("BREAKDOWN OK")
"""


def test_classify_categories():
    r = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, cwd=ROOT, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "BREAKDOWN OK" in r.stdout
