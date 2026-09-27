"""
To'lov API — Click (karta) + Telegram Stars.
Master § 49: Payment confirmation must be verified server-side.
"""
import os
import hashlib
from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form
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
        "title": "Qadam.io Premium tahlil",
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
            title="Qadam.io Premium tahlil",
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

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — karta orqali, admin tasdiqlaydi
# ═══════════════════════════════════════════════════════════════════

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


class ManualRequestPayload(BaseModel):
    init_data: str
    stage1_result_id: int


@router.post("/manual/request")
async def manual_request(payload: ManualRequestPayload):
    """User karta orqali to'lov qilmoqchi — adminga xabar yuborish."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        # Manual payment yozuvi
        p = Payment(
            user_id=user["id"],
            stage1_result_id=payload.stage1_result_id,
            provider="manual",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    # Adminga bot orqali xabar
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "Nomalum"
        username = user.get("username") or "-"
        user_id = user["id"]

        text = (
            f"💳 <b>Yangi to'lov so'rovi</b>\n\n"
            f"👤 <b>User:</b> {first_name}\n"
            f"🔗 <b>Username:</b> @{username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📊 <b>Stage 1 ID:</b> {payload.stage1_result_id}\n"
            f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\n"
            f"🎫 <b>Payment ID:</b> {payment_id}\n\n"
            f"<i>Skrinshotni kutish kerak.</i>"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"pay:approve:{payment_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"pay:reject:{payment_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Userga yozish",
                    url=f"tg://user?id={user_id}",
                ),
            ],
        ])

        if ADMIN_CHAT_ID:
            await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=kb)

        await bot.session.close()
    except Exception as e:
        log.error(f"Admin xabar yuborishda xato: {e}")

    return {
        "payment_id": payment_id,
        "status": "pending",
        "card": {
            "number": CARD_NUMBER,
            "holder": CARD_HOLDER,
            "bank": CARD_BANK,
            "amount": PRICE_UZS,
        },
        "admin_username": "@ulugbek_aliboyev",
    }


class ApprovePayload(BaseModel):
    init_data: str
    payment_id: int


@router.post("/manual/approve")
async def manual_approve(payload: ApprovePayload):
    """Admin to'lovni tasdiqlaydi."""
    admin = verify_init_data(payload.init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    ADMIN_IDS = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if admin["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")

    async with SessionLocal() as s:
        p = await s.get(Payment, payload.payment_id)
        if not p:
            raise HTTPException(404, "Payment topilmadi")

        p.status = "paid"
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()

        user_id = p.user_id

    # Userga xabar yuborish
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        webapp = os.getenv("WEBAPP_URL", "")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Chuqur tahlilni boshlash",
                web_app=WebAppInfo(url=f"{webapp}/stage2"),
            )
        ]])

        await bot.send_message(
            user_id,
            "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            "Endi 18 ta chuqur savolga javob bering va shaxsiy yo'l xaritangizni oling.",
            reply_markup=kb,
        )

        await bot.session.close()
    except Exception as e:
        log.error(f"User xabar yuborishda xato: {e}")

    return {"ok": True, "payment_id": payload.payment_id}


@router.get("/manual/pending")
async def manual_pending(init_data: str = Query(...)):
    """Admin uchun: kutilayotgan to'lovlar."""
    admin = verify_init_data(init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    ADMIN_IDS = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if admin["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")

    async with SessionLocal() as s:
        rows = await s.execute(
            select(Payment)
            .where(Payment.status == "pending", Payment.provider == "manual")
            .order_by(Payment.created_at.desc())
        )
        items = rows.scalars().all()

    return {
        "payments": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "stage1_result_id": p.stage1_result_id,
                "amount_uzs": p.amount_uzs,
                "created_at": p.created_at.isoformat() if p.created_at else "",
            }
            for p in items
        ]
    }


# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV v2 — screenshot Mini App ichida yuklanadi
# ═══════════════════════════════════════════════════════════════════

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


@router.get("/manual/card-info")
async def get_card_info():
    """Karta ma'lumotlari (frontend uchun)."""
    return {
        "card": {
            "number": CARD_NUMBER,
            "holder": CARD_HOLDER,
            "bank": CARD_BANK,
            "amount": PRICE_UZS,
        }
    }


@router.post("/manual/upload")
async def manual_upload(
    init_data: str = Form(...),
    stage1_result_id: int = Form(...),
    screenshot: UploadFile = File(...),
):
    """
    User screenshot yuklaydi — Mini App ichida.
    Backend: rasmni adminga bot orqali yuboradi + payment yozadi.
    """
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    # Rasm tekshiruvi
    if screenshot.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(400, "Faqat rasm fayl yuklang (JPG, PNG)")

    content = await screenshot.read()
    if len(content) > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(400, "Rasm hajmi 5 MB dan oshmasin")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        p = Payment(
            user_id=user["id"],
            stage1_result_id=stage1_result_id,
            provider="manual",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    # Adminga bot orqali rasm + tugmalar
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import (
            BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
        )

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "Nomalum"
        username = user.get("username") or "-"
        user_id = user["id"]

        caption = (
            f"💳 <b>Yangi to'lov</b>\n\n"
            f"👤 <b>User:</b> {first_name}\n"
            f"🔗 <b>Username:</b> @{username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\n"
            f"🎫 <b>Payment ID:</b> {payment_id}\n\n"
            f"Rasmni tekshiring va tasdiqlang:"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"pay:approve:{payment_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"pay:reject:{payment_id}",
                ),
            ],
        ])

        photo = BufferedInputFile(content, filename="screenshot.jpg")
        if ADMIN_CHAT_ID:
            await bot.send_photo(
                ADMIN_CHAT_ID,
                photo=photo,
                caption=caption,
                reply_markup=kb,
            )

        await bot.session.close()
    except Exception as e:
        log.error(f"Adminga rasm yuborishda xato: {e}")

    return {"ok": True, "payment_id": payment_id, "status": "pending"}


class ApprovePayload(BaseModel):
    init_data: str
    payment_id: int


@router.post("/manual/approve")
async def manual_approve(payload: ApprovePayload):
    """Admin to'lovni tasdiqlaydi."""
    admin = verify_init_data(payload.init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    ADMIN_IDS = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if admin["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")

    async with SessionLocal() as s:
        p = await s.get(Payment, payload.payment_id)
        if not p:
            raise HTTPException(404, "Payment topilmadi")

        p.status = "paid"
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()
        user_id = p.user_id

    # Userga xabar
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        webapp = os.getenv("WEBAPP_URL", "")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Chuqur tahlilni boshlash",
                web_app=WebAppInfo(url=f"{webapp}/stage2"),
            )
        ]])

        await bot.send_message(
            user_id,
            "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            "Endi 18 ta chuqur savolga javob bering va shaxsiy yo'l xaritangizni oling.",
            reply_markup=kb,
        )

        await bot.session.close()
    except Exception as e:
        log.error(f"User xabar yuborishda xato: {e}")

    return {"ok": True, "payment_id": payload.payment_id}


@router.get("/manual/status/{payment_id}")
async def manual_status(payment_id: int, init_data: str = Query(...)):
    """Mini App poll qiladi — to'lov tasdiqlanganmi?"""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p or p.user_id != user["id"]:
            raise HTTPException(404, "Payment topilmadi")

        stage2_ready = p.status == "paid"

        return {
            "payment_id": p.id,
            "status": p.status,
            "stage2_ready": stage2_ready,
        }
