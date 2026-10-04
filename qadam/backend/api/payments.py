"""
To'lov API — manual card payment (screenshot → admin decides in the bot).
Master § 49: payment confirmation is decided server-side, never by the client.

State changes live in `backend.services.manual_payment_service`.
Legacy v0 endpoints (Click, Stars, stage1-based manual flow) were removed
2026-10-04: nothing in the Mini App called them, and `/stars/confirm`
marked a payment paid on the client's word.
"""
import logging
import os

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from backend.auth import verify_init_data
from backend.db import SessionLocal
from backend.services import manual_payment_service as mps

router = APIRouter(prefix="/payments", tags=["payments"])
log = logging.getLogger("qadam.payments")

PRICE_UZS = 39000
MAX_SCREENSHOT_BYTES = 5 * 1024 * 1024

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")


def _admin_chat_id() -> int:
    try:
        return int(os.getenv("ADMIN_CHAT_ID", "0"))
    except ValueError:
        return 0


def image_kind(data: bytes) -> str | None:
    """Real image type from the file's first bytes (the client's content-type is not trusted)."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


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


@router.get("/manual/my-status")
async def my_status(init_data: str = Query(...)):
    """unlocked | pending | rejected | none — the Mini App premium page shows the matching screen."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    return await mps.my_status(user["id"])


async def _owned_discovery_session(user_id: int, session_id: int | None) -> int | None:
    if not session_id:
        return None
    from backend.models_v2 import DiscoverySession

    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
    return session_id if sess and sess.user_id == user_id else None


async def _send_to_admin(content: bytes, caption: str, payment_id: int) -> None:
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup

    chat_id = _admin_chat_id()
    if not chat_id or not os.getenv("BOT_TOKEN"):
        raise RuntimeError("ADMIN_CHAT_ID or BOT_TOKEN not configured")

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay:approve:{payment_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay:reject:{payment_id}"),
    ]])
    bot = Bot(os.getenv("BOT_TOKEN", ""), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.send_photo(
            chat_id,
            photo=BufferedInputFile(content, filename="screenshot.jpg"),
            caption=caption,
            reply_markup=kb,
        )
    finally:
        await bot.session.close()


@router.post("/manual/upload-v2")
async def manual_upload_v2(
    init_data: str = Form(...),
    discovery_session_id: int | None = Form(None),
    screenshot: UploadFile = File(...),
):
    """User uploads a payment screenshot; the admin gets it with approve/reject buttons."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    content = await screenshot.read(MAX_SCREENSHOT_BYTES + 1)
    if len(content) > MAX_SCREENSHOT_BYTES:
        raise HTTPException(400, "Rasm hajmi 5 MB dan oshmasin")
    if image_kind(content) is None:
        raise HTTPException(400, "Faqat rasm yuklang (JPG, PNG yoki WEBP)")

    from backend.services.age_gate import require_adult

    await require_adult(user["id"])
    session_id = await _owned_discovery_session(user["id"], discovery_session_id)
    try:
        payment_id = await mps.create_pending(user["id"], session_id, PRICE_UZS)
    except mps.AlreadyUnlocked:
        raise HTTPException(409, {"code": "already_unlocked", "message": "Chuqur tahlil sizda allaqachon ochiq"})
    except mps.PendingExists as e:
        raise HTTPException(409, {
            "code": "pending_exists",
            "message": "Oldingi skrinshotingiz tekshirilmoqda. Admin javobini kuting.",
            "payment_id": e.payment_id,
        })

    from html import escape

    caption = (
        f"💳 <b>Yangi to'lov</b>\n\n"
        f"👤 <b>User:</b> {escape(user.get('first_name') or 'Nomalum')}\n"
        f"🔗 <b>Username:</b> @{escape(user.get('username') or '-')}\n"
        f"🆔 <b>ID:</b> <code>{user['id']}</code>\n"
        f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\n"
        f"🎫 <b>Payment ID:</b> {payment_id}\n\n"
        f"Kartaga {PRICE_UZS:,} so'm tushganini tekshirib, qaror qiling:"
    )
    try:
        await _send_to_admin(content, caption, payment_id)
    except Exception as e:
        log.error(f"payment {payment_id}: screenshot not delivered to admin: {e}")
        await mps.cancel_undelivered(payment_id, str(e))
        raise HTTPException(503, {
            "code": "admin_unreachable",
            "message": "Skrinshotni hozir qabul qila olmadik. Bir necha daqiqadan keyin qayta urinib ko'ring.",
        })

    return {"ok": True, "payment_id": payment_id, "status": "pending"}
