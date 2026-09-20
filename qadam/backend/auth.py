"""
Telegram initData tekshiruvi.
Master § 49: Telegram WebApp authentication must be verified server-side.

DEV mode: ENV=development bo'lsa - mock user qaytaradi (brauzerda test uchun).
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
ENV = os.getenv("ENV", "development")


def verify_init_data(init_data: str) -> dict | None:
    """
    initData'ni HMAC-SHA256 bilan tekshiradi.
    DEV mode: initData bo'sh bo'lsa - mock user qaytaradi.
    """
    # DEV MODE - brauzerda test uchun
    if ENV == "development" and (not init_data or len(init_data) < 10):
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