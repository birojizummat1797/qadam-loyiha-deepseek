# -*- coding: utf-8 -*-
"""Fix — bot/main.py + payment.py TOZA qayta yozish."""
from pathlib import Path

BOT = Path("qadam/bot")

# ═══════════════════════════════════════════════════════════
# 1. bot/main.py — TOZA
# ═══════════════════════════════════════════════════════════
(BOT / "main.py").write_text(r'''"""Qadam.io Bot — Webhook (Render)."""
import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.handlers import start as start_handlers
from bot.handlers import payment as payment_handlers

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("qadam.bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "").strip()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "qadam-secret")
PORT = int(os.getenv("PORT", 8080))

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(start_handlers.router)
dp.include_router(payment_handlers.router)


async def _set_commands():
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Boshlash"),
            BotCommand(command="help", description="Yordam"),
            BotCommand(command="pending", description="Kutilayotgan to'lovlar"),
            BotCommand(command="approve", description="To'lovni tasdiqlash"),
            BotCommand(command="reject", description="To'lovni rad etish"),
        ])
    except Exception as e:
        log.error(f"set_my_commands xato: {e}")


async def run_polling():
    log.info("Bot rejimi: POLLING")
    await bot.delete_webhook(drop_pending_updates=True)
    await _set_commands()
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


def run_webhook():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    webhook_path = "/webhook"
    webhook_url = f"{WEBHOOK_BASE}{webhook_path}"
    log.info(f"Webhook URL: {webhook_url}")

    async def on_startup(bot: Bot):
        try:
            result = await bot.set_webhook(
                webhook_url,
                secret_token=WEBHOOK_SECRET,
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"],
            )
            log.info(f"set_webhook: {result}")
            info = await bot.get_webhook_info()
            log.info(f"webhook_info: url={info.url}, pending={info.pending_update_count}")
            if info.last_error_message:
                log.error(f"webhook LAST ERROR: {info.last_error_message}")
            await _set_commands()
        except Exception as e:
            log.error(f"set_webhook xato: {e}")

    async def on_shutdown(bot: Bot):
        try:
            await bot.delete_webhook()
        except Exception:
            pass

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET
    ).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    async def health(request):
        return web.json_response({"ok": True, "service": "qadam-bot"})

    async def root(request):
        return web.json_response({"service": "qadam-bot", "webhook": webhook_url})

    app.router.add_get("/health", health)
    app.router.add_get("/", root)

    web.run_app(app, host="0.0.0.0", port=PORT)


def main():
    log.info(f"BOT_TOKEN: {'set' if BOT_TOKEN and not BOT_TOKEN.startswith('123456') else 'MISSING'}")
    log.info(f"WEBHOOK_BASE: {WEBHOOK_BASE or '(empty)'}")

    if not BOT_TOKEN or BOT_TOKEN.startswith("123456"):
        log.error("BOT_TOKEN sozlanmagan!")
        return

    log.info("Routers ulandi: start + payment")

    if WEBHOOK_BASE:
        run_webhook()
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
''', encoding="utf-8")
print("[OK] bot/main.py")

# ═══════════════════════════════════════════════════════════
# 2. bot/handlers/payment.py — TOZA
# ═══════════════════════════════════════════════════════════
(BOT / "handlers/payment.py").write_text(r'''"""Manual to'lov — callback + text commands."""
import os
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery, Message,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
)
from sqlalchemy import select, desc

router = Router()
log = logging.getLogger("qadam.bot.payment")

PREMIUM_KEY = "premium_career_intelligence"


def _is_admin(uid: int) -> bool:
    ids = set(int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    return uid in ids


async def _approve_impl(payment_id: int) -> dict:
    from backend.db import SessionLocal
    from backend.models import Payment
    from backend.services.entitlement_service import grant_entitlement

    async with SessionLocal() as s:
        pay = await s.get(Payment, payment_id)
        if not pay:
            return {"ok": False, "error": f"Payment #{payment_id} topilmadi"}
        pay.status = "paid"
        await s.commit()
        user_id = pay.user_id

    await grant_entitlement(
        user_id=user_id,
        entitlement_key=PREMIUM_KEY,
        source="manual_card",
        payment_reference=str(payment_id),
    )
    return {"ok": True, "user_id": user_id}


async def _reject_impl(payment_id: int) -> dict:
    from backend.db import SessionLocal
    from backend.models import Payment

    async with SessionLocal() as s:
        pay = await s.get(Payment, payment_id)
        if not pay:
            return {"ok": False, "error": f"Payment #{payment_id} topilmadi"}
        pay.status = "rejected"
        await s.commit()
        user_id = pay.user_id

    return {"ok": True, "user_id": user_id}


async def _notify_user_approve(bot, user_id: int):
    try:
        webapp = os.getenv("WEBAPP_URL", "")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Chuqur tahlilni boshlash",
                web_app=WebAppInfo(url=f"{webapp}/deep-diagnostic"),
            )
        ]])
        await bot.send_message(
            user_id,
            "✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
            "Chuqur tahlilni boshlashingiz mumkin.",
            reply_markup=kb,
        )
    except Exception as e:
        log.error(f"notify approve: {e}")


async def _notify_user_reject(bot, user_id: int):
    try:
        await bot.send_message(
            user_id,
            "❌ <b>To'lov tasdiqlanmadi</b>\n\n"
            "Skrinshot aniq emas yoki to'lov topilmadi. Qaytadan urinib ko'ring.",
        )
    except Exception as e:
        log.error(f"notify reject: {e}")


# ═══════════════ CALLBACK ═══════════════

@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    log.info(f"cb_approve: from={callback.from_user.id} data={callback.data}")

    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Tasdiqlanmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    result = await _approve_impl(payment_id)
    if not result["ok"]:
        try:
            await callback.message.edit_caption(
                caption=(callback.message.caption or "") + f"\n\n⚠️ {result['error']}"
            )
        except Exception:
            pass
        return

    await _notify_user_approve(callback.bot, result["user_id"])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    log.info(f"cb_reject: from={callback.from_user.id} data={callback.data}")

    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Rad etilmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    result = await _reject_impl(payment_id)
    if not result["ok"]:
        return

    await _notify_user_reject(callback.bot, result["user_id"])

    try:
        await callback.message.edit_caption(
            caption=(callback.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass


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


@router.message(Command("approve"))
async def cmd_approve(m: Message):
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    parts = (m.text or "").split()
    if len(parts) < 2:
        await m.answer("Format: /approve <payment_id>\nMisol: /approve 5")
        return

    try:
        pid = int(parts[1])
    except ValueError:
        await m.answer("payment_id raqam bo'lishi kerak")
        return

    result = await _approve_impl(pid)
    if not result["ok"]:
        await m.answer(f"❌ {result['error']}")
        return

    await m.answer(f"✅ Payment #{pid} tasdiqlandi (user: {result['user_id']})")
    await _notify_user_approve(m.bot, result["user_id"])


@router.message(Command("reject"))
async def cmd_reject(m: Message):
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    parts = (m.text or "").split()
    if len(parts) < 2:
        await m.answer("Format: /reject <payment_id>")
        return

    try:
        pid = int(parts[1])
    except ValueError:
        await m.answer("payment_id raqam bo'lishi kerak")
        return

    result = await _reject_impl(pid)
    if not result["ok"]:
        await m.answer(f"❌ {result['error']}")
        return

    await m.answer(f"❌ Payment #{pid} rad etildi")
    await _notify_user_reject(m.bot, result["user_id"])
''', encoding="utf-8")
print("[OK] bot/handlers/payment.py")

print()
print("=" * 60)
print("Fix — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI — LOKAL TEST (muhim!):")
print("  1. cd qadam")
print("  2. ..\\qadam\\venv\\Scripts\\python.exe -c \"import bot.main; print('IMPORT OK')\"")
print("  3. Agar 'IMPORT OK' chiqsa — bot kodi ishlaydi")
print("  4. cd ..")
print("  5. git add -A")
print('  6. git commit -m "Fix: bot main + payment clean rewrite"')
print("  7. git push")
print("  8. Render Manual Deploy (bot, clear cache)")