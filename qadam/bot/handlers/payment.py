"""Manual to'lov — admin decides with buttons or /approve, /reject; users get one clear message.

All state changes go through `backend.services.manual_payment_service`
(locked row, no double grant, reject-after-approve revokes access).
"""
import logging
import os
from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo,
)
from sqlalchemy import desc, select

router = Router()
log = logging.getLogger("qadam.bot.payment")


def _is_admin(uid: int) -> bool:
    ids = set(int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    return uid in ids


def _webapp_button(text: str, path: str) -> InlineKeyboardMarkup:
    webapp = os.getenv("WEBAPP_URL", "")
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=text, web_app=WebAppInfo(url=f"{webapp}{path}")),
    ]])


# What the user is told after a real state change. No-ops send nothing.
USER_MESSAGES = {
    "approved": (
        "✅ <b>To'lovingiz tasdiqlandi!</b>\n\nChuqur tahlil siz uchun ochildi.",
        ("🎯 Chuqur tahlilni boshlash", "/deep-diagnostic"),
    ),
    "rejected": (
        "❌ <b>To'lov tasdiqlanmadi</b>\n\n"
        "Kartaga to'lov topilmadi yoki skrinshot aniq emas.\n"
        "Agar pul o'tkazgan bo'lsangiz, to'lov chekining aniq skrinshotini qayta yuboring.",
        ("📤 Skrinshotni qayta yuborish", "/premium"),
    ),
    "approval_revoked": (
        "⚠️ <b>Avvalgi tasdiq bekor qilindi</b>\n\n"
        "Tekshiruvda to'lov kartaga tushmagani aniqlandi, shuning uchun chuqur tahlil yopildi.\n"
        "Xato bo'lgan deb o'ylasangiz, to'lov chekining skrinshotini qayta yuboring.",
        ("📤 Skrinshotni qayta yuborish", "/premium"),
    ),
}

# What the admin sees.
ADMIN_RESULT = {
    "approved": "✅ TASDIQLANDI",
    "rejected": "❌ RAD ETILDI",
    "approval_revoked": "⚠️ TASDIQ BEKOR QILINDI — kirish yopildi",
    "already_approved": "Bu to'lov allaqachon tasdiqlangan",
    "already_rejected": "Bu to'lov allaqachon rad etilgan",
    "not_found": "To'lov topilmadi",
}


async def notify_user(bot, decision) -> None:
    msg = USER_MESSAGES.get(decision.outcome)
    if not msg or decision.user_id is None:
        return
    text, (button, path) = msg
    try:
        await bot.send_message(decision.user_id, text, reply_markup=_webapp_button(button, path))
    except Exception as e:
        log.error(f"payment {decision.payment_id}: user notify failed: {e}")


async def decide(action: str, payment_id: int, admin_id: int):
    from backend.services import manual_payment_service as mps

    fn = mps.approve if action == "approve" else mps.reject
    return await fn(payment_id, admin_id)


def _undo_hint(decision) -> str:
    if decision.outcome == "approved":
        return f"\nO'zgartirish: /reject {decision.payment_id}"
    if decision.outcome in ("rejected", "approval_revoked"):
        return f"\nO'zgartirish: /approve {decision.payment_id}"
    return ""


# ═══════════════ CALLBACK ═══════════════

@router.callback_query(F.data.regexp(r"^pay:(approve|reject):\d+$"))
async def cb_decide(callback: CallbackQuery):
    log.info(f"pay callback: from={callback.from_user.id} data={callback.data}")
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    _, action, raw_id = callback.data.split(":")
    decision = await decide(action, int(raw_id), callback.from_user.id)

    if not decision.changed:
        await callback.answer(ADMIN_RESULT[decision.outcome], show_alert=True)
        return
    await callback.answer(ADMIN_RESULT[decision.outcome])
    await notify_user(callback.bot, decision)

    admin = escape(callback.from_user.first_name or str(callback.from_user.id))
    try:
        await callback.message.edit_caption(
            caption=escape(callback.message.caption or "")
            + f"\n\n<b>{ADMIN_RESULT[decision.outcome]}</b> — {admin}{_undo_hint(decision)}",
            reply_markup=None,
        )
    except Exception as e:
        log.warning(f"payment {decision.payment_id}: caption edit failed: {e}")


# ═══════════════ TEXT COMMANDS ═══════════════

@router.message(Command("pending"))
async def cmd_pending(m: Message):
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    from backend.db import SessionLocal
    from backend.models import Payment

    async with SessionLocal() as s:
        rows = (await s.execute(
            select(Payment)
            .where(Payment.status == "pending")
            .order_by(desc(Payment.created_at))
            .limit(10)
        )).scalars().all()

    if not rows:
        await m.answer("Kutilayotgan to'lovlar yo'q")
        return

    text = "<b>Kutilayotgan to'lovlar:</b>\n\n"
    for r in rows:
        text += (
            f"🎫 #{r.id} — user <code>{r.user_id}</code>\n"
            f"💰 {r.amount_uzs:,} so'm\n"
            f"✅ /approve {r.id}\n"
            f"❌ /reject {r.id}\n\n"
        )
    await m.answer(text)


async def _cmd_decide(m: Message, action: str):
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return
    parts = (m.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await m.answer(f"Format: /{action} <payment_id>\nMisol: /{action} 5")
        return

    decision = await decide(action, int(parts[1]), m.from_user.id)
    await m.answer(f"#{decision.payment_id}: {ADMIN_RESULT[decision.outcome]}{_undo_hint(decision)}")
    if decision.changed:
        await notify_user(m.bot, decision)


@router.message(Command("approve"))
async def cmd_approve(m: Message):
    await _cmd_decide(m, "approve")


@router.message(Command("reject"))
async def cmd_reject(m: Message):
    await _cmd_decide(m, "reject")
