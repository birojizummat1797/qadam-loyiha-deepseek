"""Payment invariants, one scenario per run (PM requirement #10, 2026-10-04).

    python tests/flows/payment_invariants.py <scenario>

Each scenario runs on its own fresh SQLite database (see tests/test_payment_invariants.py).
"""
import asyncio
import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
os.environ["ADMIN_IDS"] = "900"
os.environ["WEBAPP_URL"] = "https://miniapp.test"

from fastapi import HTTPException, UploadFile  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

from backend.api import payments  # noqa: E402
from backend.api.v1 import deep_diagnostic as dd_api  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Payment  # noqa: E402
from backend.models_v2 import Entitlement, PaymentEvent  # noqa: E402
from backend.services import manual_payment_service as mps  # noqa: E402
from backend.services.entitlement_service import PREMIUM_KEY, has_active_entitlement  # noqa: E402
from bot.handlers import payment as bot_pay  # noqa: E402

ADMIN, USER = 900, 4001
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fake_verify(init_data):
    return {"id": int(init_data), "first_name": "T", "username": "t"}


async def upload(user=USER):
    return await payments.manual_upload_v2(str(user), None, UploadFile(file=io.BytesIO(PNG), filename="s.png"))


def click(action, pid):
    return SimpleNamespace(
        from_user=SimpleNamespace(id=ADMIN, first_name="Admin"), data=f"pay:{action}:{pid}",
        answer=AsyncMock(), bot=SimpleNamespace(send_message=AsyncMock()),
        message=SimpleNamespace(caption="c", edit_caption=AsyncMock()),
    )


async def access(user=USER) -> bool:
    return await has_active_entitlement(user, PREMIUM_KEY)


async def deep_start(user=USER) -> int:
    try:
        await dd_api.start(dd_api.StartPayload(init_data=str(user)))
        return 200
    except HTTPException as e:
        return e.status_code


async def count(model, *where) -> int:
    async with SessionLocal() as s:
        return (await s.execute(select(func.count()).select_from(model).where(*where))).scalar_one()


# ── scenarios ────────────────────────────────────────────────────────────

async def confirmed_then_rejected_closes_access():
    pid = (await upload())["payment_id"]
    await bot_pay.cb_decide(click("approve", pid))
    check(await access() and await deep_start() == 200, "approve did not open access")
    c = click("reject", pid)
    await bot_pay.cb_decide(c)
    check(not await access(), "access still open after confirmed → rejected")
    check(await deep_start() == 402, "deep diagnostic still starts after revoke")
    check(await count(Entitlement, Entitlement.payment_reference == str(pid), Entitlement.status == "active") == 0,
          "active entitlement left")
    check("bekor qilindi" in c.bot.send_message.await_args.args[1], "user not told about revoke")


async def duplicate_confirmation_grants_once():
    pid = (await upload())["payment_id"]
    clicks = [click("approve", pid) for _ in range(3)]
    for c in clicks:
        await bot_pay.cb_decide(c)
    check(await count(Entitlement, Entitlement.payment_reference == str(pid)) == 1, "granted more than once")
    sent = sum(c.bot.send_message.await_count for c in clicks)
    check(sent == 1, f"user got {sent} approval messages")
    check(await count(PaymentEvent, PaymentEvent.payment_id == pid, PaymentEvent.event_type == "approved") == 1,
          "duplicate audit rows")
    # Same via text command after the button.
    m = SimpleNamespace(from_user=SimpleNamespace(id=ADMIN), text=f"/approve {pid}",
                        answer=AsyncMock(), bot=SimpleNamespace(send_message=AsyncMock()))
    await bot_pay.cmd_approve(m)
    check("allaqachon" in m.answer.await_args.args[0], "command did not report no-op")
    m.bot.send_message.assert_not_awaited()


async def admin_unavailable_leaves_nothing_pending():
    payments._send_to_admin = AsyncMock(side_effect=RuntimeError("telegram down"))
    try:
        await upload()
        raise AssertionError("upload succeeded while admin unreachable")
    except HTTPException as e:
        check(e.status_code == 503 and e.detail["code"] == "admin_unreachable", e.detail)
    check(await count(Payment, Payment.user_id == USER, Payment.status == "pending") == 0, "ghost pending payment")
    check(await count(Payment, Payment.user_id == USER, Payment.status == "failed") == 1, "failure not recorded")
    check((await mps.my_status(USER))["state"] == "none", "user blocked from retrying")
    check(not await access(), "access opened without approval")


async def retry_is_idempotent():
    # Retry after admin failure creates exactly one new pending payment.
    payments._send_to_admin = AsyncMock(side_effect=RuntimeError("down"))
    try:
        await upload()
    except HTTPException:
        pass
    payments._send_to_admin = AsyncMock()
    first = (await upload())["payment_id"]
    # Retrying while pending does not create another payment or another admin message.
    for _ in range(3):
        try:
            await upload()
            raise AssertionError("second pending payment created")
        except HTTPException as e:
            check(e.status_code == 409 and e.detail["code"] == "pending_exists", e.detail)
    check(payments._send_to_admin.await_count == 1, "admin spammed by retries")
    check(await count(Payment, Payment.user_id == USER, Payment.status == "pending") == 1, "pending count")
    # Reject twice → one transition, one user message.
    clicks = [click("reject", first), click("reject", first)]
    for c in clicks:
        await bot_pay.cb_decide(c)
    check(sum(c.bot.send_message.await_count for c in clicks) == 1, "reject notified twice")
    # Resubmit after reject → one new pending; approve → access; paying again → 409.
    second = (await upload())["payment_id"]
    check(second != first, "rejected payment reused")
    await bot_pay.cb_decide(click("approve", second))
    check(await access(), "no access after approve")
    try:
        await upload()
        raise AssertionError("paid twice")
    except HTTPException as e:
        check(e.detail["code"] == "already_unlocked", e.detail)


async def non_admin_cannot_decide():
    pid = (await upload())["payment_id"]
    c = click("approve", pid)
    c.from_user.id = USER
    await bot_pay.cb_decide(c)
    check(not await access(), "non-admin approved a payment")
    check((await mps.my_status(USER))["state"] == "pending", "state changed by non-admin")


SCENARIOS = {f.__name__: f for f in (
    confirmed_then_rejected_closes_access,
    duplicate_confirmation_grants_once,
    admin_unavailable_leaves_nothing_pending,
    retry_is_idempotent,
    non_admin_cannot_decide,
)}


async def main(name):
    await init_db()
    payments.verify_init_data = fake_verify
    dd_api.verify_init_data = fake_verify
    payments._send_to_admin = AsyncMock()
    await SCENARIOS[name]()
    print("SCENARIO OK", name)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
