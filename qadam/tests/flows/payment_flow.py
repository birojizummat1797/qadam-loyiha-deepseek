"""Manual payment flow against a real SQLite database (owner request 2026-10-04).

Upload → admin reject → resubmit → approve → double click → revoke → re-approve,
plus bad uploads, a non-admin click and an admin that cannot be reached.
Invoked by tests/test_payment_flow.py in a subprocess (fresh DB, isolated imports).
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
from sqlalchemy import select  # noqa: E402

from backend.api import payments  # noqa: E402
from backend.api.v1 import deep_diagnostic as dd_api  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Payment  # noqa: E402
from backend.models_v2 import Entitlement, PaymentEvent  # noqa: E402
from backend.services import manual_payment_service as mps  # noqa: E402
from backend.services.entitlement_service import PREMIUM_KEY, has_active_entitlement  # noqa: E402
from bot.handlers import payment as bot_pay  # noqa: E402

ADMIN = 900
USER = 3001
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 64


def fake_verify(init_data):
    return {"id": int(init_data), "first_name": "Test<b>", "username": "t"}


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def upload(data: bytes, name: str = "s.png") -> UploadFile:
    return UploadFile(file=io.BytesIO(data), filename=name)


async def expect_http(coro, status, code=None):
    try:
        await coro
    except HTTPException as e:
        check(e.status_code == status, f"expected {status}, got {e.status_code} {e.detail}")
        if code:
            check(isinstance(e.detail, dict) and e.detail.get("code") == code, f"detail {e.detail}")
        return e
    raise AssertionError(f"expected HTTP {status}, got success")


def callback(action: str, payment_id: int, admin_id: int = ADMIN):
    bot = SimpleNamespace(send_message=AsyncMock())
    return SimpleNamespace(
        from_user=SimpleNamespace(id=admin_id, first_name="Admin"),
        data=f"pay:{action}:{payment_id}",
        answer=AsyncMock(),
        bot=bot,
        message=SimpleNamespace(caption="💳 Yangi to'lov <User>", edit_caption=AsyncMock()),
    )


def command(text: str, admin_id: int = ADMIN):
    return SimpleNamespace(
        from_user=SimpleNamespace(id=admin_id),
        text=text,
        answer=AsyncMock(),
        bot=SimpleNamespace(send_message=AsyncMock()),
    )


def sent_text(bot) -> str:
    return bot.send_message.await_args.args[1]


def sent_button_url(bot) -> str:
    kb = bot.send_message.await_args.kwargs["reply_markup"]
    return kb.inline_keyboard[0][0].web_app.url


async def active_entitlements(payment_id: int) -> int:
    async with SessionLocal() as s:
        rows = (await s.execute(select(Entitlement).where(
            Entitlement.payment_reference == str(payment_id), Entitlement.status == "active",
        ))).scalars().all()
    return len(rows)


async def payment_status(payment_id: int) -> str:
    async with SessionLocal() as s:
        return (await s.get(Payment, payment_id)).status


async def deep_start_status(user_id: int) -> int:
    try:
        await dd_api.start(dd_api.StartPayload(init_data=str(user_id)))
        return 200
    except HTTPException as e:
        return e.status_code


async def main():
    await init_db()
    payments.verify_init_data = fake_verify
    dd_api.verify_init_data = fake_verify
    sent_to_admin = AsyncMock()
    payments._send_to_admin = sent_to_admin

    # 0) Image sniffing ignores the client's content-type.
    check(payments.image_kind(PNG) == "png", "png")
    check(payments.image_kind(JPEG) == "jpeg", "jpeg")
    check(payments.image_kind(WEBP) == "webp", "webp")
    check(payments.image_kind(b"<html>not an image</html>") is None, "html accepted as image")

    # 1) Bad uploads create nothing.
    await expect_http(payments.manual_upload_v2(str(USER), None, upload(b"%PDF-1.4 fake")), 400)
    big = PNG + b"\x00" * (payments.MAX_SCREENSHOT_BYTES + 1)
    await expect_http(payments.manual_upload_v2(str(USER), None, upload(big)), 400)
    check(sent_to_admin.await_count == 0, "admin got a bad upload")
    check((await mps.my_status(USER))["state"] == "none", "state after bad uploads")

    # 2) Valid upload → pending; admin caption escapes the user's name.
    r = await payments.manual_upload_v2(str(USER), None, upload(PNG))
    p1 = r["payment_id"]
    check(r["status"] == "pending", r)
    caption = sent_to_admin.await_args.args[1]
    check("Test&lt;b&gt;" in caption and "<b>Test<b>" not in caption, f"caption not escaped: {caption}")
    check(await mps.my_status(USER) == {"state": "pending", "payment_id": p1}, "status pending")

    # 3) Second upload while the first is being checked → 409, no new payment.
    e = await expect_http(payments.manual_upload_v2(str(USER), None, upload(JPEG)), 409, "pending_exists")
    check(e.detail["payment_id"] == p1, e.detail)

    # 4) Non-admin pressing the button changes nothing.
    cb = callback("approve", p1, admin_id=USER)
    await bot_pay.cb_decide(cb)
    check(await payment_status(p1) == "pending", "non-admin changed state")
    cb.bot.send_message.assert_not_awaited()

    # 5) Reject → user told why and how to retry; deep diagnostic stays locked.
    cb = callback("reject", p1)
    await bot_pay.cb_decide(cb)
    check(await payment_status(p1) == "rejected", "not rejected")
    check("tasdiqlanmadi" in sent_text(cb.bot), sent_text(cb.bot))
    check(sent_button_url(cb.bot).endswith("/premium"), "retry button")
    check("RAD ETILDI" in cb.message.edit_caption.await_args.kwargs["caption"], "admin caption")
    check("&lt;User&gt;" in cb.message.edit_caption.await_args.kwargs["caption"], "old caption not escaped")
    check(await mps.my_status(USER) == {"state": "rejected", "payment_id": p1}, "status rejected")
    check(await deep_start_status(USER) == 402, "deep diagnostic opened after reject")

    # 6) Rejecting again is a no-op: no second message to the user.
    cb = callback("reject", p1)
    await bot_pay.cb_decide(cb)
    cb.bot.send_message.assert_not_awaited()
    check(cb.answer.await_args.kwargs.get("show_alert") is True, "no-op not shown as alert")

    # 7) Resubmit after reject → new pending payment.
    p2 = (await payments.manual_upload_v2(str(USER), None, upload(JPEG)))["payment_id"]
    check(p2 != p1, "resubmit reused the rejected payment")

    # 8) Approve → access opens, user gets the start button.
    cb = callback("approve", p2)
    await bot_pay.cb_decide(cb)
    check(await payment_status(p2) == "paid", "not paid")
    check(await active_entitlements(p2) == 1, "entitlement not granted")
    check(sent_button_url(cb.bot).endswith("/deep-diagnostic"), "start button")
    check(await mps.my_status(USER) == {"state": "unlocked"}, "status unlocked")
    check(await deep_start_status(USER) == 200, "deep diagnostic still locked after approve")

    # 9) Double click / second admin → nothing granted twice, no second message.
    cb = callback("approve", p2)
    await bot_pay.cb_decide(cb)
    check(await active_entitlements(p2) == 1, "double grant")
    cb.bot.send_message.assert_not_awaited()

    # 10) Paying again while unlocked → 409.
    await expect_http(payments.manual_upload_v2(str(USER), None, upload(PNG)), 409, "already_unlocked")

    # 11) /reject after approve → access revoked, user told honestly.
    m = command(f"/reject {p2}")
    await bot_pay.cmd_reject(m)
    check(await payment_status(p2) == "rejected", "not rejected after approve")
    check(await active_entitlements(p2) == 0, "entitlement survived reject-after-approve")
    check(not await has_active_entitlement(USER, PREMIUM_KEY), "still premium")
    check(await deep_start_status(USER) == 402, "deep diagnostic open after revoke")
    check("bekor qilindi" in sent_text(m.bot), sent_text(m.bot))
    check(f"/approve {p2}" in m.answer.await_args.args[0], "undo hint missing")

    # 12) /approve again (admin correcting the correction) → exactly one active entitlement.
    m = command(f"/approve {p2}")
    await bot_pay.cmd_approve(m)
    check(await active_entitlements(p2) == 1, "re-approve grant count")
    check(await has_active_entitlement(USER, PREMIUM_KEY), "not premium after re-approve")

    # 13) Unknown payment and bad command input.
    m = command("/approve 999999")
    await bot_pay.cmd_approve(m)
    check("topilmadi" in m.answer.await_args.args[0], m.answer.await_args.args[0])
    m = command("/approve abc")
    await bot_pay.cmd_approve(m)
    check("Format" in m.answer.await_args.args[0], "bad id accepted")
    m = command(f"/approve {p2}", admin_id=USER)
    await bot_pay.cmd_approve(m)
    check(m.answer.await_args.args[0] == "Ruxsat yo'q", "non-admin command")

    # 14) Admin unreachable → user told to retry, nothing left pending.
    other = 3002
    payments._send_to_admin = AsyncMock(side_effect=RuntimeError("ADMIN_CHAT_ID not configured"))
    await expect_http(payments.manual_upload_v2(str(other), None, upload(PNG)), 503, "admin_unreachable")
    check((await mps.my_status(other))["state"] == "none", "ghost pending payment left behind")
    payments._send_to_admin = sent_to_admin
    r = await payments.manual_upload_v2(str(other), None, upload(PNG))
    check(r["status"] == "pending", "retry after admin failure")

    # 15) Someone else's discovery session id is not attached to the payment.
    async with SessionLocal() as s:
        stored = await s.get(Payment, r["payment_id"])
    check(stored.stage1_result_id == 0, "foreign/unknown session id stored")

    # 16) Audit trail: every real transition is recorded with the admin id.
    async with SessionLocal() as s:
        events = (await s.execute(
            select(PaymentEvent).where(PaymentEvent.payment_id == p2).order_by(PaymentEvent.id)
        )).scalars().all()
    check([ev.event_type for ev in events] == ["created", "approved", "rejected", "approved"],
          [ev.event_type for ev in events])
    check(all(ev.payload.get("admin_id") == ADMIN for ev in events[1:]), "admin id missing in audit")

    # 17) Legacy endpoints are gone.
    paths = {route.path for route in payments.router.routes}
    check(paths == {"/payments/manual/card-info", "/payments/manual/my-status", "/payments/manual/upload-v2"},
          f"unexpected payment routes: {sorted(paths)}")

    print("PAYMENT FLOW OK")


asyncio.run(main())
