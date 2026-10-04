"""User context (constraints) for readiness — always from the user's own answers.

Readiness must never be computed from invented defaults (PM P0-5/6, 2026-10-03).
If the user's context is unknown, readiness is reported as unknown, not guessed.
"""
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models_v2 import DiscoveryAnswer, DiscoverySession

CONSTRAINT_KEYS = ("time", "device", "english")


def is_complete(constraints) -> bool:
    return isinstance(constraints, dict) and all(constraints.get(k) for k in CONSTRAINT_KEYS)


async def discovery_constraints(discovery_session_id) -> dict | None:
    """Constraints of a discovery session: stored meta first, else rebuilt from answers. None if unknown."""
    from backend.services.discovery_service import extract_known_constraints

    if not discovery_session_id:
        return None
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, discovery_session_id)
        if not sess:
            return None
        stored = (sess.meta or {}).get("constraints")
        if is_complete(stored):
            return {k: stored[k] for k in CONSTRAINT_KEYS}
        rows = (await s.execute(
            select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == discovery_session_id)
        )).scalars().all()
    rebuilt = extract_known_constraints(
        [{"question_id": r.question_id, "answer_id": r.answer_id} for r in rows]
    )
    return rebuilt if is_complete(rebuilt) else None
