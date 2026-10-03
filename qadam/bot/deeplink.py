"""Website → bot deep-link attribution (spec v1).

The public website opens the bot as  t.me/<bot>?start=<payload>
    payload = "w1-" + source_code [ "-" + career_slug ]
    e.g.      w1-hr                      (homepage hero)
              w1-cd-frontend_development (career page)

Rules:
- Invalid / unknown payloads are ignored: /start behaves exactly as before.
- The raw payload is never logged or stored; only the parsed, whitelisted fields.
- A career slug the taxonomy does not know is dropped (source is kept).
- No personal data travels in the payload.

Spec: claude-qadamio/docs/telegram-deeplink-spec.md
"""
import logging
import re
from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import urlencode

log = logging.getLogger("qadam.bot.deeplink")

TELEGRAM_START_MAX_LENGTH = 64
PAYLOAD_RE = re.compile(r"^w1-([a-z]{2,3})(?:-([a-z0-9_]{2,40}))?$")

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
}


@dataclass(frozen=True)
class StartAttribution:
    source: str                    # short code, e.g. "cd"
    career: Optional[str] = None   # taxonomy slug, only if known
    channel: str = "web"
    version: int = 1

    def event_payload(self) -> dict:
        data = {
            "channel": self.channel,
            "v": self.version,
            "src": self.source,
            "placement": WEB_SOURCES[self.source],
        }
        if self.career:
            data["career"] = self.career
        return data

    def webapp_query(self) -> dict:
        data = {"src": self.source}
        if self.career:
            data["career"] = self.career
        return data


def parse_start_payload(
    raw: Optional[str],
    known_careers: Optional[Iterable[str]] = None,
) -> Optional[StartAttribution]:
    """Parse a /start argument. Returns None for anything that is not a valid v1 web payload.

    known_careers: taxonomy slugs; if given, an unknown career is dropped.
    If None, career validation is skipped (format check only).
    """
    if not raw or len(raw) > TELEGRAM_START_MAX_LENGTH:
        return None
    match = PAYLOAD_RE.match(raw.strip())
    if not match:
        return None
    source, career = match.group(1), match.group(2)
    if source not in WEB_SOURCES:
        return None
    if career and known_careers is not None and career not in set(known_careers):
        career = None
    return StartAttribution(source=source, career=career)


def discovery_url(webapp_url: str, attribution: Optional[StartAttribution] = None) -> str:
    """Mini App discovery URL; carries attribution as a hint when present."""
    base = f"{webapp_url}/discovery"
    if not attribution:
        return base
    return f"{base}?{urlencode(attribution.webapp_query())}"


async def known_career_slugs() -> set:
    """Active taxonomy slugs (DB, with the service's own JSON fallback). Empty set on failure."""
    try:
        from backend.services.taxonomy_service import load_taxonomy_from_db

        data = await load_taxonomy_from_db()
        return {
            slug
            for cluster in data.get("clusters", {}).values()
            for slug in cluster.get("careers", {})
        }
    except Exception as e:  # never break /start
        log.warning(f"deeplink: taxonomy unavailable: {e}")
        return set()


async def resolve_attribution(raw: Optional[str]) -> Optional[StartAttribution]:
    if not raw:
        return None
    attribution = parse_start_payload(raw)
    if not attribution or not attribution.career:
        return attribution
    known = await known_career_slugs()
    return parse_start_payload(raw, known_careers=known)


async def log_bot_start(user_id: int, attribution: StartAttribution) -> bool:
    """Insert an `events` row (event_name="bot_start"). Returns False on failure, never raises."""
    try:
        from backend.db import SessionLocal
        from backend.models import Event

        async with SessionLocal() as s:
            s.add(Event(
                user_id=user_id,
                event_name="bot_start",
                payload=attribution.event_payload(),
            ))
            await s.commit()
        return True
    except Exception as e:
        log.error(f"deeplink: bot_start event not saved: {e}")
        return False
