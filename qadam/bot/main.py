"""Qadam.io Bot — Webhook (Render)."""
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
from bot import webhook_secret

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("qadam.bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "").strip()
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


async def on_shutdown(bot: Bot):
    """Do NOT delete the webhook here.

    On a redeploy Render starts the new instance (which sets the webhook) and only
    then stops the old one. Deleting the webhook on shutdown removed the new
    instance's webhook, so Telegram stopped delivering updates (incident 2026-10-04).
    The webhook is (re)set on every startup; shutdown only closes the HTTP session.
    """
    try:
        await bot.session.close()
    except Exception:
        pass


def run_webhook(secret_token: str):
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    webhook_path = "/webhook"
    webhook_url = f"{WEBHOOK_BASE}{webhook_path}"
    log.info(f"Webhook URL: {webhook_url}")

    async def on_startup(bot: Bot):
        try:
            result = await bot.set_webhook(
                webhook_url,
                secret_token=secret_token,
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

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=secret_token
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
        try:
            secret_token = webhook_secret.telegram_token(os.getenv("WEBHOOK_SECRET"))
        except webhook_secret.WeakWebhookSecret as e:
            # Fail closed: without a strong secret anyone could forge updates
            # (including admin payment approvals).
            log.error(f"Bot not started: {e}. Set a random WEBHOOK_SECRET (40+ letters/digits).")
            raise SystemExit(1)
        log.info("WEBHOOK_SECRET: ok")
        run_webhook(secret_token)
    else:
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()
