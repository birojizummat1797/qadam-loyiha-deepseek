"""
To'lov API — Click (karta) + Telegram Stars.
Master § 49: Payment confirmation must be verified server-side.
"""
import os
import hashlib
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models import Payment, TestResult
from backend.auth import verify_init_data

router = APIRouter(prefix="/payments", tags=["payments"])

PRICE_UZS = 39000
PRICE_STARS = 150

CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")

_bot_instance = None


def _get_bot():
    """aiogram Bot lazy loader — faqat Stars uchun kerak."""
    global _bot_instance
    if _bot_instance is None:
        from aiogram import Bot
        _bot_instance = Bot(os.getenv("BOT_TOKEN", ""))
    return _bot_instance


class CreatePaymentPayload(BaseModel):
    init_data: str
    stage1_result_id: int
    provider: str


class StarsConfirmPayload(BaseModel):
    init_data: str
    payment_id: int
    telegram_payment_charge_id: str


@router.post("/create")
async def create_payment(payload: CreatePaymentPayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    if payload.provider not in ("click", "stars"):
        raise HTTPException(400, "Unsupported provider")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        p = Payment(
            user_id=user["id"],
            stage1_result_id=payload.stage1_result_id,
            provider=payload.provider,
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    if payload.provider == "click":
        pay_url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={CLICK_SERVICE_ID}"
            f"&merchant_id={CLICK_MERCHANT_ID}"
            f"&amount={PRICE_UZS}"
            f"&transaction_param={payment_id}"
        )
        return {"payment_id": payment_id, "pay_url": pay_url, "provider": "click"}

    return {
        "payment_id": payment_id,
        "provider": "stars",
        "stars_amount": PRICE_STARS,
        "title": "QADAM Premium tahlil",
        "description": "18 savol + Fit + Readiness + Roadmap + PDF",
    }


@router.post("/stars/invoice")
async def stars_invoice(payload: CreatePaymentPayload):
    """Frontend Stars uchun invoice_link so'raydi."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        p = Payment(
            user_id=user["id"],
            stage1_result_id=payload.stage1_result_id,
            provider="stars",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    from aiogram.types import LabeledPrice
    bot = _get_bot()
    try:
        invoice_link = await bot.create_invoice_link(
            title="QADAM Premium tahlil",
            description="18 savol + Fit + Readiness + Roadmap + PDF",
            payload=f"qadam_premium_{payment_id}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Premium tahlil", amount=PRICE_STARS)],
        )
    except Exception as e:
        raise HTTPException(500, f"Invoice yaratilmadi: {str(e)[:100]}")

    return {"payment_id": payment_id, "invoice_link": invoice_link}


@router.post("/stars/confirm")
async def stars_confirm(payload: StarsConfirmPayload):
    """Frontend Stars to'lovdan keyin bu endpointni chaqiradi."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        p = await s.get(Payment, payload.payment_id)
        if not p or p.user_id != user["id"]:
            raise HTTPException(404, "Payment topilmadi")
        p.status = "paid"
        p.external_id = payload.telegram_payment_charge_id
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()

    return {"ok": True, "payment_id": payload.payment_id}


@router.post("/click/prepare")
async def click_prepare(request: Request):
    body = await request.json()
    return await _click_handle(body, complete=False)


@router.post("/click/complete")
async def click_complete(request: Request):
    body = await request.json()
    return await _click_handle(body, complete=True)


async def _click_handle(body: dict, complete: bool):
    click_trans_id = body.get("click_trans_id")
    service_id = body.get("service_id")
    merchant_trans_id = body.get("merchant_trans_id")
    amount = body.get("amount")
    action = body.get("action")
    sign_string = body.get("sign_string")

    if not CLICK_SECRET_KEY:
        return {"error": -1, "error_note": "Server not configured"}

    expected = hashlib.md5(
        f"{click_trans_id}{service_id}{CLICK_SECRET_KEY}"
        f"{merchant_trans_id}{amount}{action}".encode()
    ).hexdigest()
    if sign_string != expected:
        return {"error": -1, "error_note": "SIGN CHECK FAILED"}

    try:
        pid = int(merchant_trans_id)
    except (TypeError, ValueError):
        return {"error": -5, "error_note": "Invalid merchant_trans_id"}

    async with SessionLocal() as s:
        p = await s.get(Payment, pid)
        if not p:
            return {"error": -5, "error_note": "Payment not found"}
        if complete:
            p.status = "paid"
            p.external_id = str(click_trans_id)
            s1 = await s.get(TestResult, p.stage1_result_id)
            if s1:
                s1.paid = True
            await s.commit()

    return {
        "error": 0, "error_note": "Success",
        "click_trans_id": click_trans_id,
        "merchant_trans_id": merchant_trans_id,
        "merchant_prepare_id": merchant_trans_id,
    }


@router.get("/check/{stage1_result_id}")
async def check_paid(stage1_result_id: int, init_data: str = Query(...)):
    """Frontend polling uchun (Click uchun)."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    async with SessionLocal() as s:
        s1 = await s.get(TestResult, stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Topilmadi")
        return {"paid": s1.paid}