"""Hotfix 2026-10-04: bot shutdown must never delete the Telegram webhook."""
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")

import bot.main as bot_main  # noqa: E402


def test_shutdown_keeps_the_webhook():
    fake = MagicMock()
    fake.delete_webhook = AsyncMock()
    fake.session.close = AsyncMock()
    asyncio.run(bot_main.on_shutdown(fake))
    fake.delete_webhook.assert_not_called()
    fake.session.close.assert_awaited_once()


def test_no_delete_webhook_in_webhook_mode():
    src = (Path(bot_main.__file__)).read_text(encoding="utf-8")
    webhook_part = src[src.index("def run_webhook"):src.index("def main")]
    assert "delete_webhook" not in webhook_part
