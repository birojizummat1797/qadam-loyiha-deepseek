"""auth.py has no development bypass; only correctly signed, fresh initData passes (PM 2026-10-04)."""
import hashlib
import hmac
import importlib
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest

from backend import auth

TOKEN = "123456:TEST-token-for-hmac"
AUTH_SRC = Path(auth.__file__).read_text(encoding="utf-8")


def signed(user: dict, auth_date: int | None = None, token: str = TOKEN) -> str:
    fields = {"auth_date": str(auth_date or int(time.time())), "user": json.dumps(user), "query_id": "q1"}
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setattr(auth, "BOT_TOKEN", TOKEN)


def test_no_bypass_code_left():
    for marker in ("DEV_AUTH", "dev_user", "999999999", "development", 'getenv("ENV"'):
        assert marker not in AUTH_SRC, marker


@pytest.mark.parametrize("env", [
    {}, {"ENV": "development"}, {"ENV": "development", "DEV_AUTH": "1"}, {"ENV": "dev", "DEV_AUTH": "1"},
])
@pytest.mark.parametrize("init_data", ["", "short", "x" * 50])
def test_unsigned_input_is_refused_in_every_environment(monkeypatch, token, env, init_data):
    for k in ("ENV", "DEV_AUTH", "RENDER"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    importlib.reload(auth)
    monkeypatch.setattr(auth, "BOT_TOKEN", TOKEN)
    assert auth.verify_init_data(init_data) is None


def test_valid_signature_passes(token):
    assert auth.verify_init_data(signed({"id": 42, "first_name": "A"}))["id"] == 42


def test_tampered_user_is_refused(token):
    data = signed({"id": 42}).replace("42", "43")
    assert auth.verify_init_data(data) is None


def test_other_bot_token_is_refused(token):
    assert auth.verify_init_data(signed({"id": 42}, token="999:other")) is None


def test_expired_auth_date_is_refused(token):
    old = int(time.time()) - auth.AUTH_MAX_AGE - 60
    assert auth.verify_init_data(signed({"id": 42}, auth_date=old)) is None


def test_missing_bot_token_refuses_everything(monkeypatch):
    monkeypatch.setattr(auth, "BOT_TOKEN", "")
    assert auth.verify_init_data(signed({"id": 42})) is None
