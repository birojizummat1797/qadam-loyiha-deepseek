"""
Telegram initData tekshiruvi.
Master § 49: Telegram WebApp authentication must be verified server-side.

DEV mode (fail-closed): a mock user is returned only when ALL hold:
ENV=development, DEV_AUTH=1, and not running on Render (RENDER unset).
A missing or mistyped ENV means production (incident review 2026-10-03:
ENV used to default to "development", so a missing variable opened the mock).
"""
import hmac
import hashlib
import json
import time
import os
from urllib.parse import parse_qsl
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
AUTH_MAX_AGE = 86400  # 24 soat
ENV = os.getenv("ENV", "production")


def dev_auth_enabled(env: dict | None = None) -> bool:
    """True only for an explicit local dev setup; any doubt → False."""
    e = os.environ if env is None else env
    return (
        e.get("ENV", "production") == "development"
        and e.get("DEV_AUTH") == "1"
        and not e.get("RENDER")
    )


def verify_init_data(init_data: str) -> dict | None:
    """
    initData'ni HMAC-SHA256 bilan tekshiradi.
    DEV mode: initData bo'sh bo'lsa - mock user qaytaradi.
    """
    # DEV MODE - brauzerda test uchun (fail-closed, see dev_auth_enabled)
    if dev_auth_enabled() and (not init_data or len(init_data) < 10):
        return {
            "id": 999999999,
            "username": "dev_user",
            "first_name": "Dev",
            "last_name": "Tester",
            "language_code": "uz",
        }

    if not init_data or not BOT_TOKEN:
        return None

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        hash_ = parsed.pop("hash", None)
        if not hash_:
            return None

        # auth_date freshness
        auth_date = int(parsed.get("auth_date", 0))
        if time.time() - auth_date > AUTH_MAX_AGE:
            return None

        # HMAC tekshiruvi
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed, hash_):
            return None

        user = json.loads(parsed.get("user", "{}"))
        if not user.get("id"):
            return None

        return user
    except Exception:
        return None