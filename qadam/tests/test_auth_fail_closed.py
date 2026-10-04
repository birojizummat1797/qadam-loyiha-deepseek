"""auth.py dev mode is fail-closed (PM follow-up after the 2026-10-03 ENV finding)."""
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import pytest

from backend import auth
from backend.auth import dev_auth_enabled


@pytest.mark.parametrize("env", [
    {},                                                      # nothing set → production
    {"ENV": "development"},                                  # no explicit DEV_AUTH
    {"ENV": "Development", "DEV_AUTH": "1"},                 # typo / case
    {"ENV": "dev", "DEV_AUTH": "1"},
    {"ENV": "production", "DEV_AUTH": "1"},
    {"ENV": "development", "DEV_AUTH": "true"},              # only "1" counts
    {"ENV": "development", "DEV_AUTH": "1", "RENDER": "true"},  # never on Render
])
def test_dev_auth_disabled_unless_explicit_local(env):
    assert dev_auth_enabled(env) is False


def test_dev_auth_enabled_only_for_explicit_local_setup():
    assert dev_auth_enabled({"ENV": "development", "DEV_AUTH": "1"}) is True


@pytest.mark.parametrize("init_data", ["", "short", "x" * 50])
def test_no_mock_user_without_dev_flags(monkeypatch, init_data):
    for k in ("ENV", "DEV_AUTH", "RENDER"):
        monkeypatch.delenv(k, raising=False)
    assert auth.verify_init_data(init_data) is None


def test_mock_user_on_render_is_refused(monkeypatch):
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("DEV_AUTH", "1")
    monkeypatch.setenv("RENDER", "true")
    assert auth.verify_init_data("") is None


def test_env_defaults_to_production(monkeypatch):
    monkeypatch.delenv("ENV", raising=False)
    try:
        assert importlib.reload(auth).ENV == "production"
    finally:
        importlib.reload(auth)
