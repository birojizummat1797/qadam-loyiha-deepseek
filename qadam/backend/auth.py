"""
Telegram initData tekshiruvi.
Master § 49: Telegram WebApp authentication must be verified server-side.

There is no test or local-mode bypass (PM 2026-10-04): every request needs initData
signed with BOT_TOKEN, in every environment. Security does not depend on ENV.
Tests patch `verify_init_data` explicitly instead.
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


def verify_init_data(init_data: str) -> dict | None:
    """
    initData'ni HMAC-SHA256 bilan tekshiradi. Noto'g'ri yoki eskirgan bo'lsa — None.
    """
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