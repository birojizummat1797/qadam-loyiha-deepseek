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