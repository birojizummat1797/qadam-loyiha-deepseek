"""
Telegram Stars to'lov oqimi.
"""
import os
from aiogram import Router, F
from aiogram.types import (
    PreCheckoutQuery, Message, InlineKeyboardMarkup,
    InlineKeyboardButton, WebAppInfo,
)
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models import Payment, TestResult

router = Router()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://qadam.uz")


@router.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery):
    try:
        payload = q.invoice_payload
        if not payload.startswith("qadam_premium_"):
            await q.answer(ok=False, error_message="Noto'g'ri to'lov.")
            return
        payment_id = int(payload.replace("qadam_premium_", ""))
        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if not p or p.user_id != q.from_user.id:
                await q.answer(ok=False, error_message="To'lov topilmadi.")
                return
            if p.status == "paid":
                await q.answer(ok=False, error_message="Allaqachon to'langan.")
                return
        await q.answer(ok=True)
    except Exception:
        await q.answer(ok=False, error_message="Xatolik yuz berdi.")


@router.message(F.successful_payment)
async def on_successful_payment(m: Message):
    payload = m.successful_payment.invoice_payload
    charge_id = m.successful_payment.telegram_payment_charge_id
    if not payload.startswith("qadam_premium_"):
        return
    payment_id = int(payload.replace("qadam_premium_", ""))

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p:
            return
        p.status = "paid"
        p.external_id = charge_id
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()

    url = f"{WEBAPP_URL}/stage2"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🎯 Chuqur tahlilni boshlash", web_app=WebAppInfo(url=url))
    ]])
    await m.answer(
        "✅ <b>To'lov muvaffaqiyatli!</b>\n\n"
        "Endi 18 ta savolga javob bering.",
        reply_markup=kb,
    )

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash
# ═══════════════════════════════════════════════════════════════════

import os as _os
import httpx as _httpx


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    payment_id = int(callback.data.split(":")[2])

    admin_ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if callback.from_user.id not in admin_ids:
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    backend = _os.getenv("BACKEND_URL", "https://qadam-backend-deepseek.onrender.com")
    bot_token = _os.getenv("BOT_TOKEN", "")

    try:
        async with _httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{backend}/payments/manual/approve",
                json={"init_data": f"dev_{callback.from_user.id}", "payment_id": payment_id},
            )
            # Fallback: agar init_data talab qilsa, to'g'ridan-to'g'ri bazaga yozamiz
            if r.status_code != 200:
                # Direct DB update
                from backend.db import SessionLocal
                from backend.models import Payment, TestResult
                async with SessionLocal() as s:
                    p = await s.get(Payment, payment_id)
                    if p:
                        p.status = "paid"
                        s1 = await s.get(TestResult, p.stage1_result_id)
                        if s1:
                            s1.paid = True
                        await s.commit()
                        # Userga xabar
                        webapp = _os.getenv("WEBAPP_URL", "")
                        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
                        kb = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(
                                text="🎯 Chuqur tahlilni boshlash",
                                web_app=WebAppInfo(url=f"{webapp}/stage2"),
                            )
                        ]])
                        try:
                            await callback.bot.send_message(
                                p.user_id,
                                "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
                                "Endi 18 ta chuqur savolga javob bering.",
                                reply_markup=kb,
                            )
                        except Exception:
                            pass
    except Exception as e:
        await callback.answer(f"Xato: {str(e)[:50]}", show_alert=True)
        return

    # Xabarni yangilash
    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>TASDIQLANDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass

    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split(":")[2])

    admin_ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if callback.from_user.id not in admin_ids:
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    from backend.db import SessionLocal
    from backend.models import Payment

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if p:
            p.status = "rejected"
            await s.commit()

    try:
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ <b>RAD ETILDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass

    await callback.answer("Rad etildi ❌")


# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash (v2)
# ═══════════════════════════════════════════════════════════════════

import os as _os


def _is_admin(user_id: int) -> bool:
    ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    return user_id in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[2])

    from backend.db import SessionLocal
    from backend.models import Payment, TestResult

    user_id = None
    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p:
            await callback.answer("Payment topilmadi", show_alert=True)
            return
        p.status = "paid"
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()
        user_id = p.user_id

    # Userga avtomatik xabar
    if user_id:
        try:
            from aiogram.types import (
                InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
            )
            webapp = _os.getenv("WEBAPP_URL", "")
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🎯 Chuqur tahlilni boshlash",
                    web_app=WebAppInfo(url=f"{webapp}/stage2"),
                )
            ]])
            await callback.bot.send_message(
                user_id,
                "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
                "Endi 18 ta chuqur savolga javob bering va shaxsiy "
                "yo'l xaritangizni oling.",
                reply_markup=kb,
            )
        except Exception as e:
            import logging
            logging.error(f"User xabar yuborishda xato: {e}")

    # Xabarni yangilash
    try:
        new_caption = (callback.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>"
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
    except Exception:
        pass

    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[2])

    from backend.db import SessionLocal
    from backend.models import Payment

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if p:
            p.status = "rejected"
            await s.commit()
            user_id = p.user_id
        else:
            user_id = None

    # Userga xabar (rad etildi)
    if user_id:
        try:
            await callback.bot.send_message(
                user_id,
                "❌ <b>To'lov tasdiqlanmadi</b>\n\n"
                "Skrinshot aniq emas yoki to'lov topilmadi. "
                "Iltimos, qaytadan urinib ko'ring.",
            )
        except Exception:
            pass

    try:
        new_caption = (callback.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>"
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
    except Exception:
        pass

    await callback.answer("Rad etildi")


# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash v3 (reliable)
# ═══════════════════════════════════════════════════════════════════

import os as _os
import logging as _log

_logger = _log.getLogger("qadam.bot.payment")


def _is_admin(user_id: int) -> bool:
    ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    return user_id in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    _logger.info(f"cb_approve: from={callback.from_user.id} data={callback.data}")

    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Tasdiqlanmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    try:
        from backend.db import SessionLocal
        from backend.models import Payment, TestResult

        user_id = None
        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if not p:
                _logger.error(f"Payment {payment_id} topilmadi")
                await callback.message.edit_caption(
                    caption=(callback.message.caption or "") + "\n\n⚠️ Payment topilmadi",
                )
                return

            p.status = "paid"
            s1 = await s.get(TestResult, p.stage1_result_id)
            if s1:
                s1.paid = True
            await s.commit()
            user_id = p.user_id

        _logger.info(f"Payment {payment_id} paid, user={user_id}")

        # Userga xabar
        if user_id:
            try:
                from aiogram.types import (
                    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
                )
                webapp = _os.getenv("WEBAPP_URL", "")
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="🎯 Chuqur tahlilni boshlash",
                        web_app=WebAppInfo(url=f"{webapp}/stage2"),
                    )
                ]])
                await callback.bot.send_message(
                    user_id,
                    "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
                    "Endi 18 ta chuqur savolga javob bering va shaxsiy "
                    "yo'l xaritangizni oling.",
                    reply_markup=kb,
                )
                _logger.info(f"User {user_id} ga xabar yuborildi")
            except Exception as e:
                _logger.error(f"User xabar xato: {e}")

        # Admin xabarni yangilash
        try:
            new_caption = (callback.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception:
            pass

    except Exception as e:
        _logger.error(f"cb_approve xato: {e}")
        try:
            await callback.message.reply(f"⚠️ Xato: {str(e)[:100]}")
        except Exception:
            pass


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    _logger.info(f"cb_reject: from={callback.from_user.id} data={callback.data}")

    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Rad etilmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    try:
        from backend.db import SessionLocal
        from backend.models import Payment

        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if p:
                p.status = "rejected"
                await s.commit()
                user_id = p.user_id
            else:
                user_id = None

        if user_id:
            try:
                await callback.bot.send_message(
                    user_id,
                    "❌ <b>To'lov tasdiqlanmadi</b>\n\n"
                    "Skrinshot aniq emas yoki to'lov topilmadi. "
                    "Iltimos, qaytadan urinib ko'ring.",
                )
            except Exception:
                pass

        try:
            new_caption = (callback.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception:
            pass

    except Exception as e:
        _logger.error(f"cb_reject xato: {e}")
