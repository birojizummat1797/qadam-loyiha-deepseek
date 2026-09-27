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
