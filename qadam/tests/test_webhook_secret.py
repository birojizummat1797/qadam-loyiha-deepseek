"""Webhook secret is fail-closed (forged updates could approve payments)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from bot import webhook_secret as ws

MAIN = Path(__file__).parent.parent / "bot" / "main.py"


@pytest.mark.parametrize("raw", [None, "", "   ", "qadam-secret", "change-me-to-random-string", "a" * 31])
def test_weak_or_public_secret_is_refused(raw):
    with pytest.raises(ws.WeakWebhookSecret):
        ws.telegram_token(raw)


def test_strong_secret_gives_telegram_safe_token():
    token = ws.telegram_token("Zx9" * 14)
    assert re.fullmatch(r"[0-9a-f]{64}", token)
    # Any generated value works, even with characters Telegram rejects.
    assert re.fullmatch(r"[A-Za-z0-9_-]{1,256}", ws.telegram_token("+/=" * 11 + "k"))


def test_token_is_stable_and_secret_specific():
    a, b = "A" * 40, "B" * 40
    assert ws.telegram_token(a) == ws.telegram_token(a)
    assert ws.telegram_token(a) != ws.telegram_token(b)
    assert ws.telegram_token(a) != a


def test_main_has_no_default_secret_and_uses_one_token_for_both_sides():
    src = MAIN.read_text(encoding="utf-8")
    assert "qadam-secret" not in src
    assert 'os.getenv("WEBHOOK_SECRET",' not in src
    # set_webhook and the request handler must use the same derived token.
    assert src.count("secret_token=secret_token") == 2
