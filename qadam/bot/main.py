"""
QADAM Bot — Aiogram 3.

Rejim:
- WEBHOOK_BASE .env da bo'sh bo'lsa → POLLING (lokal test)
- WEBHOOK_BASE to'ldirilsa → WEBHOOK (production)
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.handlers import start as start_handlers

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


async def _set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Boshlash"),
        BotCommand(command="help", description="Yordam"),
    ])


async def run_polling():
    log.info("Bot rejimi: POLLING (lokal test)")
    await bot.delete_webhook(drop_pending_updates=True)
    await _set_commands()
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


def run_webhook():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    webhook_path = "/webhook"
    webhook_url = f"{WEBHOOK_BASE}{webhook_path}"
    log.info(f"Bot rejimi: WEBHOOK -> {webhook_url}")

    async def on_startup(bot: Bot):
        await bot.set_webhook(
            webhook_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
        )
        await _set_commands()

    async def on_shutdown(bot: Bot):
        await bot.delete_webhook()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET
    ).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    async def health(request):
        return web.json_response({"ok": True, "service": "qadam-bot"})

    app.router.add_get("/health", health)
    web.run_app(app, host="0.0.0.0", port=PORT)


def main():
    if not BOT_TOKEN or BOT_TOKEN.startswith("123456"):
        print("=" * 60)
        print("XATO: BOT_TOKEN .env da sozlanmagan!")
        print("=" * 60)
        print()
        print("1) Telegram'da @BotFather ni oching")
        print("2) /newbot buyrug'ini yuboring")
        print("3) Bot nomini kiriting (masalan: QADAM Test)")
        print("4) Username tanlang (masalan: qadam_test_bot)")
        print("5) Token olasiz: 1234567890:AAH...")
        print("6) qadam/.env faylini ochib, BOT_TOKEN ni yangilang")
        print()
        return

    if WEBHOOK_BASE:
        run_webhook()
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
