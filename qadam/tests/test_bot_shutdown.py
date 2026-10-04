"""Webhook lifecycle regression (incidents 2026-10-03/04, PM requirement #9).

Render deploys and restarts overlap two instances: the new one starts (sets
the webhook), then the old one stops. Shutdown must never remove the webhook,
startup must always (re)register it with the same secret token the request
handler checks, and waiting updates must not be dropped.
"""
import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")

import pytest  # noqa: E402

import bot.main as bot_main  # noqa: E402

URL = "https://bot.test/webhook"
TOKEN = "a" * 64


class FakeTelegram:
    """One shared Telegram-side webhook, as seen by every instance of the bot."""

    def __init__(self):
        self.url = None
        self.secret = None
        self.pending = ["/start from a user while the instance was asleep"]

    def instance(self):
        tg = self

        async def set_webhook(url, secret_token=None, drop_pending_updates=None, **_):
            tg.url, tg.secret = url, secret_token
            if drop_pending_updates:
                tg.pending.clear()
            return True

        async def delete_webhook(**_):
            tg.url = None
            return True

        async def get_webhook_info():
            return SimpleNamespace(url=tg.url, pending_update_count=len(tg.pending), last_error_message=None)

        bot = MagicMock()
        bot.set_webhook = AsyncMock(side_effect=set_webhook)
        bot.delete_webhook = AsyncMock(side_effect=delete_webhook)
        bot.get_webhook_info = AsyncMock(side_effect=get_webhook_info)
        bot.session.close = AsyncMock()
        return bot


@pytest.fixture(autouse=True)
def no_commands(monkeypatch):
    monkeypatch.setattr(bot_main, "_set_commands", AsyncMock())


def start(bot):
    asyncio.run(bot_main.register_webhook(bot, URL, TOKEN))


def stop(bot):
    asyncio.run(bot_main.on_shutdown(bot))


def test_deploy_overlap_keeps_webhook():
    tg = FakeTelegram()
    old, new = tg.instance(), tg.instance()
    start(old)
    start(new)   # Render starts the new instance first …
    stop(old)    # … then stops the old one.
    assert tg.url == URL and tg.secret == TOKEN
    old.delete_webhook.assert_not_called()


def test_restart_reregisters_webhook():
    tg = FakeTelegram()
    first = tg.instance()
    start(first)
    tg.url = None  # e.g. removed by an old release during the last deploy
    second = tg.instance()
    start(second)
    stop(first)
    assert tg.url == URL


def test_startup_keeps_waiting_updates():
    tg = FakeTelegram()
    start(tg.instance())
    assert tg.pending, "the update that woke the instance was dropped"


def test_shutdown_only_closes_session():
    bot = FakeTelegram().instance()
    stop(bot)
    bot.delete_webhook.assert_not_called()
    bot.session.close.assert_awaited_once()


def test_real_wiring_uses_one_token_and_safe_handlers(monkeypatch):
    """run_webhook registers exactly these startup/shutdown handlers and one secret token."""
    import aiohttp.web
    from aiogram.webhook import aiohttp_server

    seen = {}

    class Handler:
        def __init__(self, dispatcher, bot, secret_token):
            seen["handler_token"] = secret_token

        def register(self, app, path):
            seen["path"] = path

    monkeypatch.setattr(aiohttp.web, "run_app", lambda *a, **k: None)
    monkeypatch.setattr(aiohttp_server, "SimpleRequestHandler", Handler)
    monkeypatch.setattr(aiohttp_server, "setup_application", lambda *a, **k: None)
    monkeypatch.setattr(bot_main, "WEBHOOK_BASE", "https://bot.test")
    before_up = len(bot_main.dp.startup.handlers)
    before_down = len(bot_main.dp.shutdown.handlers)

    bot_main.run_webhook(TOKEN)

    assert seen == {"handler_token": TOKEN, "path": "/webhook"}
    down = [h.callback for h in bot_main.dp.shutdown.handlers[before_down:]]
    assert down == [bot_main.on_shutdown]
    up = bot_main.dp.startup.handlers[before_up:]
    assert len(up) == 1

    tg = FakeTelegram()
    asyncio.run(up[0].callback(tg.instance()))
    assert tg.url == URL and tg.secret == TOKEN and tg.pending


def test_no_delete_webhook_in_webhook_mode():
    src = Path(bot_main.__file__).read_text(encoding="utf-8")
    webhook_part = src[src.index("async def on_shutdown"):src.index("def main")]
    assert "delete_webhook" not in webhook_part
    assert "drop_pending_updates=True" not in webhook_part
