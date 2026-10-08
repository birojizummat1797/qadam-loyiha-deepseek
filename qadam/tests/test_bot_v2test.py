"""/v2test opens the diagnostic v2 draft for admins only."""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.handlers import start  # noqa: E402


def _msg(uid):
    return SimpleNamespace(from_user=SimpleNamespace(id=uid), answer=AsyncMock())


def test_v2test_refuses_non_admin(monkeypatch):
    monkeypatch.setenv("ADMIN_IDS", "1,2")
    m = _msg(3)
    asyncio.run(start.cmd_v2test(m))
    m.answer.assert_awaited_once_with("Ruxsat yo'q")


def test_v2test_gives_admin_the_v2_button(monkeypatch):
    monkeypatch.setenv("ADMIN_IDS", "1,2")
    m = _msg(2)
    asyncio.run(start.cmd_v2test(m))
    kb = m.answer.await_args.kwargs["reply_markup"]
    assert kb.inline_keyboard[0][0].web_app.url.endswith("/v2")
