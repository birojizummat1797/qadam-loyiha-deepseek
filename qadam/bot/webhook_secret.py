"""Webhook secret: fail-closed validation and a Telegram-safe token.

Telegram puts the secret in the `X-Telegram-Bot-Api-Secret-Token` header of
every update; it is the only proof an update really came from Telegram. With a
known secret anyone can POST a forged update — including a forged admin
"✅ Tasdiqlash" callback, because `from_user.id` comes from the update body.

The old code defaulted to "qadam-secret" (public in git), so this module:
- refuses a missing, short or known-public value (the bot does not start);
- derives the header token as sha256 hex, so any generated value works even if
  it contains characters Telegram does not allow (only A-Z a-z 0-9 _ -).
"""
import hashlib

MIN_LENGTH = 32

# Values that are public (code default, .env.example placeholder).
KNOWN_PUBLIC = frozenset({"qadam-secret", "change-me-to-random-string"})


class WeakWebhookSecret(ValueError):
    pass


def validate(raw: str | None) -> str:
    value = (raw or "").strip()
    if not value:
        raise WeakWebhookSecret("WEBHOOK_SECRET is not set")
    if value in KNOWN_PUBLIC:
        raise WeakWebhookSecret("WEBHOOK_SECRET is a public placeholder value")
    if len(value) < MIN_LENGTH:
        raise WeakWebhookSecret(f"WEBHOOK_SECRET must be at least {MIN_LENGTH} characters")
    return value


def telegram_token(raw: str | None) -> str:
    """Validated secret → 64-char hex token (always within Telegram's allowed charset)."""
    return hashlib.sha256(validate(raw).encode()).hexdigest()
