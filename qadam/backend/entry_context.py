"""Website entry context — single source of truth for bot and backend.

The public website opens the bot with a /start payload (spec: claude-qadamio
docs/telegram-deeplink-spec.md). The bot stores a *parsed, whitelisted* copy
in `events` (event_name="bot_start"); when the user then starts a discovery
session, the backend re-validates that copy server-side and attaches it to
`DiscoverySession.meta["entry_context"]`.

Pure module: stdlib only, no DB, no aiogram — safe to import anywhere.
"""
import re
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

# Placement codes used by the website (lib/telegram.ts → CTA_SOURCES).
WEB_SOURCES = {
    "hr": "hero",
    "hd": "header",
    "mn": "mobile_nav",
    "hw": "how_it_works",
    "ct": "catalog",
    "cd": "career_detail",
    "ab": "about",
    "fq": "faq",
    "fc": "final_cta",
    "ft": "footer",
    "ar": "article",
    "pq": "problem_question",  # homepage "Tanish savollar" cards
}

# Visitor situation chosen on the homepage (spec v2). Short code → stored name.
ENTRY_STATES = {
    "bs": "start",   # Boshlayapman
    "al": "switch",  # Almashtiraman
    "os": "grow",    # O'smoqchiman
}

CAREER_SLUG_RE = re.compile(r"^[a-z0-9_]{2,40}$")

# How long a web entry stays attached to the next discovery session.
ENTRY_CONTEXT_WINDOW = timedelta(hours=24)


def validate_entry_context(payload: object) -> Optional[dict]:
    """Server-side validation of a stored bot_start payload.

    Returns a clean dict with only whitelisted keys/values, or None.
    Unknown state/career values are dropped (fallback), never passed through.
    """
    if not isinstance(payload, dict) or payload.get("channel") != "web":
        return None
    src = payload.get("src")
    if src not in WEB_SOURCES:
        return None
    version = payload.get("v")
    if version not in (1, 2):
        return None

    clean = {"channel": "web", "v": version, "src": src, "placement": WEB_SOURCES[src]}
    state = payload.get("state")
    if state in ENTRY_STATES.values():
        clean["state"] = state
    career = payload.get("career")
    if isinstance(career, str) and CAREER_SLUG_RE.match(career):
        clean["career"] = career
    return clean


def _as_utc(value: datetime) -> datetime:
    # SQLite returns naive datetimes; server_default=now() is UTC.
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def pick_entry_context(
    events: Iterable[tuple[Optional[datetime], object]],
    now: Optional[datetime] = None,
    window: timedelta = ENTRY_CONTEXT_WINDOW,
) -> Optional[dict]:
    """From (created_at, payload) rows, newest first, return the first valid
    entry context inside the time window, or None."""
    now = now or datetime.now(timezone.utc)
    for created_at, payload in events:
        if created_at is None or now - _as_utc(created_at) > window:
            continue
        clean = validate_entry_context(payload)
        if clean:
            return clean
    return None


async def latest_web_entry(user_id: int, limit: int = 5) -> Optional[dict]:
    """Most recent valid web entry for this user within the window. Never raises."""
    try:
        from sqlalchemy import desc, select

        from backend.db import SessionLocal
        from backend.models import Event

        async with SessionLocal() as s:
            rows = (await s.execute(
                select(Event.created_at, Event.payload)
                .where(Event.user_id == user_id, Event.event_name == "bot_start")
                .order_by(desc(Event.id))
                .limit(limit)
            )).all()
        return pick_entry_context(rows)
    except Exception:
        return None
