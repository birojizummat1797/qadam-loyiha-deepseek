"""Website → bot deep-link attribution (/start w1-...)."""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot import deeplink  # noqa: E402
from bot.deeplink import (  # noqa: E402
    StartAttribution, discovery_url, parse_start_payload,
)
from bot.handlers import start as start_handlers  # noqa: E402

KNOWN = {"frontend_development", "data_analytics", "smm_manager"}
WEBAPP = "https://miniapp.example"


def run(coro):
    return asyncio.run(coro)


# ─── parse_start_payload ──────────────────────────────────────

@pytest.mark.parametrize("raw, source, career", [
    ("w1-hr", "hr", None),
    ("w1-ft", "ft", None),
    ("w1-cd-frontend_development", "cd", "frontend_development"),
    ("w1-ct-data_analytics", "ct", "data_analytics"),
])
def test_valid_payloads(raw, source, career):
    a = parse_start_payload(raw, known_careers=KNOWN)
    assert a == StartAttribution(source=source, career=career)


@pytest.mark.parametrize("raw", [
    None, "", "   ",
    "source=web&career=frontend",          # not Telegram-safe, not our format
    "w2-hr",                               # unknown version
    "w1-zz",                               # unknown source code
    "w1-HR",                               # wrong case
    "w1-hr-",                              # dangling separator
    "w1-cd-Frontend",                      # slug must be lowercase
    "w1-cd-front-end",                     # extra separator
    "w1-cd-" + "x" * 41,                   # slug too long
    "w1-cd-<script>",
    "w1-cd-../../etc",
    "w1-cd-x'; DROP TABLE events;--",
    "ref123", "premium",                   # other deep links someone may use
    "w1-hr" + "a" * 64,                    # over Telegram's 64-char limit
])
def test_invalid_payloads_are_ignored(raw):
    assert parse_start_payload(raw, known_careers=KNOWN) is None


def test_unknown_career_is_dropped_but_source_kept():
    a = parse_start_payload("w1-cd-full_stack", known_careers=KNOWN)
    assert a == StartAttribution(source="cd", career=None)


def test_empty_taxonomy_drops_career():
    a = parse_start_payload("w1-cd-frontend_development", known_careers=set())
    assert a == StartAttribution(source="cd", career=None)


def test_every_web_source_round_trips():
    for code in deeplink.WEB_SOURCES:
        assert parse_start_payload(f"w1-{code}") == StartAttribution(source=code)


# ─── payloads / URLs ─────────────────────────────────────────

def test_event_payload_has_only_whitelisted_fields():
    a = StartAttribution(source="cd", career="data_analytics")
    assert a.event_payload() == {
        "channel": "web", "v": 1, "src": "cd",
        "placement": "career_detail", "career": "data_analytics",
    }
    assert "career" not in StartAttribution(source="hr").event_payload()


def test_discovery_url_unchanged_without_attribution():
    assert discovery_url(WEBAPP) == f"{WEBAPP}/discovery"


def test_discovery_url_carries_context():
    a = StartAttribution(source="cd", career="frontend_development")
    assert discovery_url(WEBAPP, a) == f"{WEBAPP}/discovery?src=cd&career=frontend_development"
    assert discovery_url(WEBAPP, StartAttribution(source="hr")) == f"{WEBAPP}/discovery?src=hr"


# ─── resolve_attribution ─────────────────────────────────────

def test_resolve_skips_taxonomy_lookup_without_career(monkeypatch):
    lookup = AsyncMock(return_value=KNOWN)
    monkeypatch.setattr(deeplink, "known_career_slugs", lookup)
    assert run(deeplink.resolve_attribution("w1-hr")) == StartAttribution(source="hr")
    assert run(deeplink.resolve_attribution(None)) is None
    lookup.assert_not_awaited()


def test_resolve_validates_career_against_taxonomy(monkeypatch):
    monkeypatch.setattr(deeplink, "known_career_slugs", AsyncMock(return_value=KNOWN))
    assert run(deeplink.resolve_attribution("w1-cd-smm_manager")).career == "smm_manager"
    assert run(deeplink.resolve_attribution("w1-cd-not_in_taxonomy")).career is None


def _fake_taxonomy_service(monkeypatch, loader):
    # Patched via sys.modules: importing the real service here would register
    # backend.models_v2 a second time (other tests import it as `models_v2`).
    monkeypatch.setitem(
        sys.modules, "backend.services.taxonomy_service",
        SimpleNamespace(load_taxonomy_from_db=loader),
    )


def test_known_career_slugs_reads_taxonomy(monkeypatch):
    async def fake_load():
        return {"clusters": {"software": {"careers": {"frontend_development": {}}},
                             "data_ai": {"careers": {"data_analytics": {}}}}}

    _fake_taxonomy_service(monkeypatch, fake_load)
    assert run(deeplink.known_career_slugs()) == {"frontend_development", "data_analytics"}


def test_known_career_slugs_never_raises(monkeypatch):
    async def broken():
        raise RuntimeError("db down")

    _fake_taxonomy_service(monkeypatch, broken)
    assert run(deeplink.known_career_slugs()) == set()


# ─── log_bot_start ───────────────────────────────────────────

class _FakeSession:
    def __init__(self, store, fail=False):
        self.store, self.fail = store, fail

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def add(self, obj):
        self.store.append(obj)

    async def commit(self):
        if self.fail:
            raise RuntimeError("db down")


def test_log_bot_start_writes_event(monkeypatch):
    import backend.db as db

    saved = []
    monkeypatch.setattr(db, "SessionLocal", lambda: _FakeSession(saved))
    ok = run(deeplink.log_bot_start(42, StartAttribution(source="cd", career="data_analytics")))
    assert ok is True
    assert len(saved) == 1
    ev = saved[0]
    assert ev.event_name == "bot_start"
    assert ev.user_id == 42
    assert ev.payload["src"] == "cd" and ev.payload["career"] == "data_analytics"


def test_log_bot_start_never_raises(monkeypatch):
    import backend.db as db

    monkeypatch.setattr(db, "SessionLocal", lambda: _FakeSession([], fail=True))
    assert run(deeplink.log_bot_start(42, StartAttribution(source="hr"))) is False


# ─── /start handler ──────────────────────────────────────────

def _message():
    return SimpleNamespace(
        from_user=SimpleNamespace(id=777, first_name="Ali"),
        answer=AsyncMock(),
    )


def _webapp_url(markup):
    return markup.inline_keyboard[0][0].web_app.url


@pytest.fixture
def handler_env(monkeypatch):
    log = AsyncMock(return_value=True)
    monkeypatch.setattr(start_handlers, "log_bot_start", log)
    monkeypatch.setattr(deeplink, "known_career_slugs", AsyncMock(return_value=KNOWN))
    monkeypatch.setattr(start_handlers, "WEBAPP_URL", WEBAPP)
    return log


def test_plain_start_keeps_old_behaviour(handler_env):
    m = _message()
    run(start_handlers.cmd_start(m, SimpleNamespace(args=None)))
    handler_env.assert_not_awaited()
    text = m.answer.await_args.args[0]
    assert "Ali" in text
    assert _webapp_url(m.answer.await_args.kwargs["reply_markup"]) == f"{WEBAPP}/discovery"


def test_start_without_command_object_still_works(handler_env):
    m = _message()
    run(start_handlers.cmd_start(m))
    handler_env.assert_not_awaited()
    assert _webapp_url(m.answer.await_args.kwargs["reply_markup"]) == f"{WEBAPP}/discovery"


def test_invalid_payload_keeps_old_behaviour(handler_env):
    m = _message()
    run(start_handlers.cmd_start(m, SimpleNamespace(args="source=web&career=frontend")))
    handler_env.assert_not_awaited()
    assert _webapp_url(m.answer.await_args.kwargs["reply_markup"]) == f"{WEBAPP}/discovery"


def test_web_payload_logs_event_and_passes_context(handler_env):
    m = _message()
    run(start_handlers.cmd_start(m, SimpleNamespace(args="w1-cd-frontend_development")))
    handler_env.assert_awaited_once_with(
        777, StartAttribution(source="cd", career="frontend_development"),
    )
    assert _webapp_url(m.answer.await_args.kwargs["reply_markup"]) == (
        f"{WEBAPP}/discovery?src=cd&career=frontend_development"
    )


def test_welcome_is_sent_even_if_logging_fails(monkeypatch):
    import backend.db as db

    monkeypatch.setattr(db, "SessionLocal", lambda: _FakeSession([], fail=True))
    monkeypatch.setattr(deeplink, "known_career_slugs", AsyncMock(return_value=KNOWN))
    monkeypatch.setattr(start_handlers, "WEBAPP_URL", WEBAPP)
    m = _message()
    run(start_handlers.cmd_start(m, SimpleNamespace(args="w1-hr")))
    m.answer.assert_awaited_once()
    assert _webapp_url(m.answer.await_args.kwargs["reply_markup"]) == f"{WEBAPP}/discovery?src=hr"
