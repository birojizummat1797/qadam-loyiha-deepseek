"""Age gate + consent (PM decision 2026-10-04, P0).

Policy (until a legal review defines anything else):
- Under 18: not accepted. Nothing about the person is stored; their existing
  rows (the `bot_start` event) are deleted; only an anonymous counter remains.
- 18+: accepted after explicit consent. Age, consent version and the Telegram
  name are stored.
- Over 35: a warning is shown, the user may continue. Age never enters signal,
  fit, readiness or ranking — it is a gate, not an ability signal.

Age is self-reported; it is not verified.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import delete

from backend.db import SessionLocal
from backend.models import Event, User
from backend.models_v2 import Profile

MIN_AGE = 18
WARN_AGE = 35
AGE_RANGE = (5, 120)  # plausible input; anything else is a typo
CONSENT_VERSION = "2026-10-04"

GATE_REQUIRED = {"code": "age_gate_required", "message": "Avval yosh va rozilikni tasdiqlang."}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _passed(profile: Profile | None) -> bool:
    if profile is None or profile.age is None or profile.age < MIN_AGE:
        return False
    return (profile.meta or {}).get("consent_version") == CONSENT_VERSION


async def status(user_id: int) -> dict:
    async with SessionLocal() as s:
        p = await s.get(Profile, user_id)
    if not _passed(p):
        return {"status": "required"}
    warning = p.age > WARN_AGE
    # "Keyinroq" on the 35+ warning is not agreement: ask again until the user continues.
    return {"status": "ok", "age_warning": warning,
            "warning_ack": (not warning) or bool((p.meta or {}).get("age_warning_ack_at"))}


async def ack_warning(user_id: int) -> dict:
    """The 35+ user chose "Ha, davom etaman"."""
    async with SessionLocal() as s:
        p = await s.get(Profile, user_id)
        if not _passed(p):
            raise HTTPException(403, GATE_REQUIRED)
        p.meta = {**(p.meta or {}), "age_warning_ack_at": _now()}
        await s.commit()
    return await status(user_id)


async def submit(user: dict, consent: bool, age: int) -> dict:
    if not consent:
        raise HTTPException(400, {"code": "consent_required", "message": "Davom etish uchun rozilik kerak."})
    if not (AGE_RANGE[0] <= age <= AGE_RANGE[1]):
        raise HTTPException(400, {"code": "age_invalid", "message": "Yoshni to'g'ri kiriting."})

    uid = user["id"]
    async with SessionLocal() as s:
        if age < MIN_AGE:
            # Store nothing about a minor; remove what /start already logged.
            await s.execute(delete(Event).where(Event.user_id == uid))
            p = await s.get(Profile, uid)
            if p is not None:
                await s.delete(p)
            s.add(Event(user_id=None, event_name="age_gate_blocked", payload={"band": "under_18"}))
            await s.commit()
            return {"status": "under_age"}

        p = await s.get(Profile, uid)
        if p is None:
            p = Profile(user_id=uid)
            s.add(p)
        p.age = age
        p.meta = {**(p.meta or {}), "consent_version": CONSENT_VERSION, "consented_at": _now(), "age_asked_at": _now()}

        u = await s.get(User, uid)
        if u is None:
            u = User(id=uid)
            s.add(u)
        u.first_name = (user.get("first_name") or None) and user["first_name"][:128]
        u.last_name = (user.get("last_name") or None) and user["last_name"][:128]
        u.username = (user.get("username") or None) and user["username"][:64]
        u.language_code = (user.get("language_code") or None) and user["language_code"][:8]
        await s.commit()

    return {"status": "ok", "age_warning": age > WARN_AGE}


async def require_adult(user_id: int) -> None:
    """403 unless the user passed the 18+ gate with the current consent version."""
    async with SessionLocal() as s:
        p = await s.get(Profile, user_id)
    if not _passed(p):
        raise HTTPException(403, GATE_REQUIRED)
