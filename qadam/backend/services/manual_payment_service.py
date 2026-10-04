"""Manual card payment — the single place where payment state changes.

States and transitions (admin decides from the bot):

    pending ──approve──▶ paid       (premium entitlement granted, same transaction)
    pending ──reject───▶ rejected
    rejected ─approve──▶ paid       (admin correcting a mistake)
    paid ─────reject───▶ rejected   (money did not arrive: entitlement revoked)
    paid ─────approve──▶ no-op      (double click / second admin: nothing granted twice)
    rejected ─reject───▶ no-op

The payment row is locked (SELECT … FOR UPDATE) for the whole decision, so two
admins pressing buttons at the same moment cannot both grant access.
Every real transition is written to `payment_events` (who, when, from → to).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select

from backend.db import SessionLocal
from backend.models import Payment
from backend.models_v2 import Entitlement, PaymentEvent
from backend.services.entitlement_service import PREMIUM_KEY, has_active_entitlement

PROVIDER = "manual_v2"
ENTITLEMENT_SOURCE = "manual_card"

PENDING, PAID, REJECTED = "pending", "paid", "rejected"


class PaymentError(Exception):
    """Expected business outcome the caller turns into a user message."""

    code = "error"


class AlreadyUnlocked(PaymentError):
    code = "already_unlocked"


class PendingExists(PaymentError):
    code = "pending_exists"

    def __init__(self, payment_id: int):
        super().__init__(payment_id)
        self.payment_id = payment_id


@dataclass(frozen=True)
class Decision:
    outcome: str  # approved | already_approved | rejected | already_rejected | approval_revoked | not_found
    payment_id: int
    user_id: int | None = None

    @property
    def changed(self) -> bool:
        return self.outcome in ("approved", "rejected", "approval_revoked")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _event(payment_id: int, event_type: str, payload: dict) -> PaymentEvent:
    return PaymentEvent(
        payment_id=payment_id,
        provider=PROVIDER,
        event_type=event_type,
        idempotency_key=f"{PROVIDER}:{payment_id}:{event_type}:{uuid.uuid4().hex}",
        payload=payload,
    )


async def _locked_payment(s, payment_id: int) -> Payment | None:
    q = select(Payment).where(Payment.id == payment_id).with_for_update()
    return (await s.execute(q)).scalar_one_or_none()


async def _payment_entitlements(s, payment: Payment) -> list[Entitlement]:
    q = select(Entitlement).where(
        Entitlement.user_id == payment.user_id,
        Entitlement.entitlement_key == PREMIUM_KEY,
        Entitlement.payment_reference == str(payment.id),
        Entitlement.status == "active",
    )
    return list((await s.execute(q)).scalars().all())


async def create_pending(user_id: int, discovery_session_id: int | None, amount_uzs: int) -> int:
    """New pending payment. Refuses if access is already open or a check is in progress."""
    if await has_active_entitlement(user_id, PREMIUM_KEY):
        raise AlreadyUnlocked()
    async with SessionLocal() as s:
        pending = (await s.execute(
            select(Payment.id).where(
                Payment.user_id == user_id,
                Payment.provider == PROVIDER,
                Payment.status == PENDING,
            ).limit(1)
        )).scalar_one_or_none()
        if pending is not None:
            raise PendingExists(pending)
        p = Payment(
            user_id=user_id,
            # Legacy column name; holds the discovery session id for manual_v2 (0 = unknown).
            stage1_result_id=discovery_session_id or 0,
            provider=PROVIDER,
            amount_uzs=amount_uzs,
            status=PENDING,
        )
        s.add(p)
        await s.flush()
        s.add(_event(p.id, "created", {"user_id": user_id}))
        await s.commit()
        return p.id


async def cancel_undelivered(payment_id: int, reason: str) -> None:
    """The admin never saw the screenshot: do not leave the user waiting on a ghost payment."""
    async with SessionLocal() as s:
        p = await _locked_payment(s, payment_id)
        if p and p.status == PENDING:
            p.status = "failed"
            s.add(_event(p.id, "failed", {"reason": reason[:200]}))
            await s.commit()


async def approve(payment_id: int, admin_id: int) -> Decision:
    async with SessionLocal() as s:
        p = await _locked_payment(s, payment_id)
        if p is None:
            return Decision("not_found", payment_id)
        if p.status == PAID:
            return Decision("already_approved", p.id, p.user_id)
        previous = p.status
        p.status = PAID
        if not await _payment_entitlements(s, p):
            s.add(Entitlement(
                user_id=p.user_id,
                entitlement_key=PREMIUM_KEY,
                source=ENTITLEMENT_SOURCE,
                status="active",
                activated_at=_now(),
                payment_reference=str(p.id),
                meta={"approved_by": admin_id},
            ))
        s.add(_event(p.id, "approved", {"admin_id": admin_id, "from": previous}))
        await s.commit()
        return Decision("approved", p.id, p.user_id)


async def reject(payment_id: int, admin_id: int) -> Decision:
    async with SessionLocal() as s:
        p = await _locked_payment(s, payment_id)
        if p is None:
            return Decision("not_found", payment_id)
        if p.status == REJECTED:
            return Decision("already_rejected", p.id, p.user_id)
        previous = p.status
        p.status = REJECTED
        revoked = await _payment_entitlements(s, p)
        for e in revoked:
            e.status = "revoked"
            e.cancelled_at = _now()
        s.add(_event(p.id, "rejected", {
            "admin_id": admin_id, "from": previous, "revoked_entitlements": [e.id for e in revoked],
        }))
        await s.commit()
        return Decision("approval_revoked" if previous == PAID else "rejected", p.id, p.user_id)


async def my_status(user_id: int) -> dict:
    """What the Mini App shows: free_beta, unlocked, or the state of the latest manual payment."""
    from backend.services.entitlement_service import DEEP_DIAGNOSTIC_FREE_BETA

    if DEEP_DIAGNOSTIC_FREE_BETA:
        return {"state": "free_beta"}
    if await has_active_entitlement(user_id, PREMIUM_KEY):
        return {"state": "unlocked"}
    async with SessionLocal() as s:
        p = (await s.execute(
            select(Payment).where(Payment.user_id == user_id, Payment.provider == PROVIDER)
            .order_by(Payment.id.desc()).limit(1)
        )).scalar_one_or_none()
    if p is None or p.status not in (PENDING, REJECTED):
        return {"state": "none"}
    return {"state": p.status, "payment_id": p.id}
