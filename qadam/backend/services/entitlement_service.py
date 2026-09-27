"""Entitlement Service — grant, check, revoke."""
from datetime import datetime, timezone
from sqlalchemy import select
from backend.db import SessionLocal
from backend.models_v2 import Entitlement, PaymentEvent


PREMIUM_KEY = "premium_career_intelligence"


async def get_active_entitlement(user_id: int, entitlement_key: str):
    """Aktiv entitlement qaytaradi (yoki None)."""
    async with SessionLocal() as s:
        q = (
            select(Entitlement)
            .where(
                Entitlement.user_id == user_id,
                Entitlement.entitlement_key == entitlement_key,
                Entitlement.status == "active",
            )
            .order_by(Entitlement.activated_at.desc())
            .limit(1)
        )
        r = (await s.execute(q)).scalar_one_or_none()
        return r


async def has_active_entitlement(user_id: int, entitlement_key: str) -> bool:
    e = await get_active_entitlement(user_id, entitlement_key)
    if not e:
        return False
    # Muddati tekshirish
    if e.expires_at and e.expires_at < datetime.now(timezone.utc):
        return False
    return True


async def grant_entitlement(
    user_id: int,
    entitlement_key: str,
    source: str,
    payment_reference: str | None = None,
    plan_code: str | None = None,
    expires_at=None,
    meta: dict | None = None,
):
    """Yangi aktiv entitlement yaratadi."""
    async with SessionLocal() as s:
        e = Entitlement(
            user_id=user_id,
            entitlement_key=entitlement_key,
            source=source,
            status="active",
            activated_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            payment_reference=payment_reference,
            plan_code=plan_code,
            meta=meta or {},
        )
        s.add(e)
        await s.commit()
        await s.refresh(e)
        return e


async def revoke_entitlement(entitlement_id: int):
    async with SessionLocal() as s:
        e = await s.get(Entitlement, entitlement_id)
        if e:
            e.status = "revoked"
            e.cancelled_at = datetime.now(timezone.utc)
            await s.commit()


async def record_payment_event(
    provider: str,
    event_type: str,
    idempotency_key: str,
    payment_id: int | None = None,
    payload: dict | None = None,
) -> bool:
    """
    Idempotency: agar key mavjud bo'lsa — False qaytaradi (takroriy).
    Yangi bo'lsa — yozadi, True qaytaradi.
    """
    async with SessionLocal() as s:
        existing = (await s.execute(
            select(PaymentEvent).where(PaymentEvent.idempotency_key == idempotency_key)
        )).scalar_one_or_none()
        if existing:
            return False

        ev = PaymentEvent(
            payment_id=payment_id,
            provider=provider,
            event_type=event_type,
            idempotency_key=idempotency_key,
            payload=payload or {},
        )
        s.add(ev)
        await s.commit()
        return True
