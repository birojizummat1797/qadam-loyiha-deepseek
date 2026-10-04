"""Deep diagnostic free beta: gate-only access, no payment, beta wording everywhere (PM 2026-10-04)."""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MINIAPP = ROOT.parent / "qadam-miniapp"


def test_free_beta_flow(tmp_path):
    script = Path(__file__).parent / "flows" / "free_beta_flow.py"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{tmp_path / 'b.db'}", "BOT_TOKEN": ""}
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, env=env, timeout=120, cwd=ROOT)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-4000:]
    assert "FREE BETA OK" in r.stdout


def test_no_price_or_unmeasured_time_claims_shown():
    sys.path.insert(0, str(ROOT))
    from bot.handlers import start

    texts = [start.WELCOME_TEXT, start.PREMIUM_INTRO_TEXT, (ROOT / "bot/handlers/start.py").read_text("utf-8")]
    for t in texts:
        assert "39 000" not in t and "Stars" not in t, "price shown during free beta"
        assert not re.search(r"\d+\s*daqiqa", t), "unmeasured duration claim"
    assert "beta" in start.PREMIUM_INTRO_TEXT.lower()


def test_beta_label_on_deep_pages_and_pdf():
    assert "Beta" in (MINIAPP / "app/deep-diagnostic/page.tsx").read_text("utf-8")
    assert "Beta" in (MINIAPP / "app/career-intelligence/page.tsx").read_text("utf-8")
    prelim = (MINIAPP / "app/preliminary/page.tsx").read_text("utf-8")
    assert "39 000" not in prelim and "Beta · bepul" in prelim
    assert "ilmiy tashxis emas" in (ROOT / "backend/pdf_report.py").read_text("utf-8")
