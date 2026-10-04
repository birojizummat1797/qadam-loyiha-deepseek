"""PM Q4 (2026-10-03): /career-intelligence/compare removed after a dependency audit.

Audit: no caller in the website, Mini App, bot, PDF, backend or tests (all
branches), and the route was unreachable — /{career_slug} was declared first
and served every /compare request. See docs/reviews (P0 final report).
"""
import subprocess
import sys
from pathlib import Path

CHECK = """
from starlette.routing import Match
from backend.main import app

paths = {getattr(r, "path", "") for r in app.router.routes}
assert "/api/v1/career-intelligence/compare" not in paths, "compare route still registered"
scope = {"type": "http", "path": "/api/v1/career-intelligence/compare", "method": "GET",
         "root_path": "", "query_string": b"", "headers": []}
first = next(r for r in app.router.routes if r.matches(scope)[0] == Match.FULL)
assert first.endpoint.__name__ == "get_career_detail", first.endpoint.__name__
print("OK")
"""


def test_compare_route_is_gone_and_path_goes_to_career_detail():
    # Subprocess: other test modules import the models under another package path.
    root = Path(__file__).parent.parent
    result = subprocess.run([sys.executable, "-c", CHECK], cwd=root, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and "OK" in result.stdout, result.stderr[-2000:]
