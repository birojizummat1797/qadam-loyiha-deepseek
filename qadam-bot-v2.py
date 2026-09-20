# -*- coding: utf-8 -*-
"""QADAM Bot v2 — FTT-compliant models + bot flow."""
from pathlib import Path

ROOT = Path("qadam")
FILES = {}


def add(path, content):
    FILES[path] = content.strip() + "\n"


# ═══════════════════════════════════════════════════════════════════
# backend/models.py — FTT § 25
# ═══════════════════════════════════════════════════════════════════
add("backend/models.py", r'''
"""
QADAM Database Models — FTT § 25.

Master principle:
- Missing signal != zero (evidence_state tracked separately)
- Fit != Readiness
- NO_MATCH is a valid result

Legacy tables (User, TestResult, Payment) — V1 API uchun saqlanadi.
New FTT tables qo'shilgan.
"""
from sqlalchemy import (
    BigInteger, String, JSON, DateTime, Boolean,
    Integer, Float, func, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base


# ═══════════════════════════════════════════════════════════════════
# LEGACY (existing API uses these — do not remove)
# ═══════════════════════════════════════════════════════════════════

class User(Base):
    """User — id == telegram_id (legacy). FTT fields added on top."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram_id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)

    # ─── FTT § 7: demographic context ───
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(16), nullable=True)
    current_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TestResult(Base):
    """Legacy V1 — Stage1/Stage2 test natijalari."""
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    stage: Mapped[str] = mapped_column(String(16))  # stage1 | stage2
    answers: Mapped[dict] = mapped_column(JSON)
    profile: Mapped[dict] = mapped_column(JSON)
    roadmap: Mapped[dict] = mapped_column(JSON)
    ai_explanation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    versions: Mapped[dict] = mapped_column(JSON)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Payment(Base):
    """Legacy — Click + Stars to'lov yozuvlari."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    stage1_result_id: Mapped[int] = mapped_column(BigInteger, index=True)
    provider: Mapped[str] = mapped_column(String(32))
    amount_uzs: Mapped[int] = mapped_column(BigInteger)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ═══════════════════════════════════════════════════════════════════
# FTT § 25 — NEW TABLES
# ═══════════════════════════════════════════════════════════════════

class DiagnosticSession(Base):
    """
    FTT § 13: diagnostic state machine.
    States: created | started | in_progress | paused | completed | blocked | expired | no_match
    """
    __tablename__ = "diagnostic_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)  # telegram_id
    session_type: Mapped[str] = mapped_column(String(16))  # free | premium
    status: Mapped[str] = mapped_column(String(16), default="created")

    diagnostic_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    taxonomy_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    scoring_version: Mapped[str] = mapped_column(String(16), default="v1.0")

    current_question_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(32), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    started_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticAnswer(Base):
    """
    FTT § 12: answers — frontend only sends raw answer.
    Backend decides next question.
    """
    __tablename__ = "diagnostic_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    # raw_value: {"value": "...", "option_id": "...", "text": "..."}
    raw_value: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticSignal(Base):
    """
    FTT § 16: missing != zero.
    evidence_state: measured | unmeasured | insufficient | conflicting
    value is NULL if unmeasured.
    """
    __tablename__ = "diagnostic_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_state: Mapped[str] = mapped_column(String(16), default="unmeasured")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    coverage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "signal_key", name="uq_session_signal"),
    )


class CareerTaxonomy(Base):
    """
    FTT § 17-18: career universe — versioned, read-only for AI.
    """
    __tablename__ = "career_taxonomy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    title_uz: Mapped[str] = mapped_column(String(128))
    cluster: Mapped[str] = mapped_column(String(64), index=True)
    cluster_uz: Mapped[str] = mapped_column(String(128))

    required_signals: Mapped[dict] = mapped_column(JSON)
    scoring_weights: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    roadmap_template_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    pathway_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    learning_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticCooldown(Base):
    """
    FTT § 20: 2x NO_MATCH → 24h cooldown.
    Server-side only; client timer not trusted.
    """
    __tablename__ = "diagnostic_cooldowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    reason: Mapped[str] = mapped_column(String(32), default="no_match")
    no_match_count: Mapped[int] = mapped_column(Integer, default=0)
    blocked_until: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Event(Base):
    """FTT § 30: analytics events."""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    session_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    event_name: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
''')

# ═══════════════════════════════════════════════════════════════════
# bot/main.py — polling + webhook
# ═══════════════════════════════════════════════════════════════════
add("bot/main.py", r'''
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
''')

# ═══════════════════════════════════════════════════════════════════
# bot/handlers/start.py — FTT § 4-5
# ═══════════════════════════════════════════════════════════════════
add("bot/handlers/start.py", r'''
"""
FTT § 4-5: Welcome flow + Premium intro.
Frontend business logic yo'q — faqat UI.
"""
from html import escape
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

router = Router()


WELCOME_TEXT = (
    "Assalomu alaykum, <b>{name}</b>!\n\n"
    "Sizni <b>QADAM</b> loyihasida ko‘rib turganimizdan xursandmiz. "
    "Sizga o‘zingizga mos bo‘lishi mumkin bo‘lgan kasb va yo‘nalishlarni "
    "yaxshiroq tushunish, keyingi qadamlarni aniqlash va amaliy roadmap "
    "olishda yordam beramiz.\n\n"
    "Test davomida javoblaringiz asosida sizga mos savollar beriladi. "
    "Shuning uchun javoblarni imkon qadar o‘zingizga yaqin va halol tanlang.\n\n"
    "Boshlash uchun quyidagi variantlardan birini tanlang:"
)

PREMIUM_INTRO_TEXT = (
    "Sizni <b>QADAM Premium Personal Diagnostic</b>’da ko‘rib turganimizdan "
    "xursandmiz!\n\n"
    "Bu diagnostikada savollar shunchaki test uchun emas. Javoblaringiz "
    "asosida sizga mos bo‘lishi mumkin bo‘lgan kasbiy yo‘nalishlar, mavjud "
    "kuchli tomonlar, rivojlantirilishi kerak bo‘lgan ko‘nikmalar va keyingi "
    "qadamlar aniqlanadi.\n\n"
    "Shuning uchun javoblarni imkon qadar shoshmasdan va o‘zingizga eng "
    "yaqin holat asosida bering. Bu natijaning foydaliligiga bevosita "
    "ta’sir qiladi."
)

HELP_TEXT = (
    "<b>QADAM yordam</b>\n\n"
    "/start — boshidan boshlash\n"
    "/help — yordam\n\n"
    "Savollar bo‘lsa: @qadam_support"
)


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Bepul diagnostika", callback_data="diag:free")],
        [InlineKeyboardButton(text="💎 Premium diagnostika", callback_data="diag:premium")],
        [InlineKeyboardButton(text="ℹ️ QADAM qanday ishlaydi?", callback_data="info:how")],
        [InlineKeyboardButton(text="🔐 Maxfiylik", callback_data="info:privacy")],
    ])


def premium_intro_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Diagnostikani boshlash", callback_data="diag:premium_start")],
        [InlineKeyboardButton(text="❓ Qanday ishlaydi?", callback_data="info:how")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="nav:back")],
    ])


def _safe_name(user) -> str:
    name = user.first_name or "do‘stim"
    return escape(name)


@router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        WELCOME_TEXT.format(name=_safe_name(m.from_user)),
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(HELP_TEXT)


@router.callback_query(F.data == "diag:free")
async def cb_free(q: CallbackQuery):
    await q.answer("Tez orada")
    # TODO(Batch 2): adaptive question engine


@router.callback_query(F.data == "diag:premium")
async def cb_premium(q: CallbackQuery):
    await q.answer()
    try:
        await q.message.edit_text(
            PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb()
        )
    except Exception:
        await q.message.answer(
            PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb()
        )


@router.callback_query(F.data == "diag:premium_start")
async def cb_premium_start(q: CallbackQuery):
    await q.answer("To‘lov tizimi keyingi bosqichda ulanadi.")
    # TODO(Batch 10): payment flow


@router.callback_query(F.data == "nav:back")
async def cb_back(q: CallbackQuery):
    await q.answer()
    try:
        await q.message.edit_text(
            WELCOME_TEXT.format(name=_safe_name(q.from_user)),
            reply_markup=main_menu_kb(),
        )
    except Exception:
        pass


@router.callback_query(F.data == "info:how")
async def cb_how(q: CallbackQuery):
    await q.answer()
    await q.message.answer(
        "<b>QADAM qanday ishlaydi?</b>\n\n"
        "1. Siz savollarga javob berasiz.\n"
        "2. Tizim javoblaringizni signallarga aylantiradi.\n"
        "3. Signallar 25+ kasbiy yo‘nalish bilan taqqoslanadi.\n"
        "4. Sizga eng mos 3–5 ta yo‘nalish va amaliy roadmap beriladi.\n\n"
        "<i>Halol tahlil. Manipulyatsiyasiz.</i>"
    )


@router.callback_query(F.data == "info:privacy")
async def cb_privacy(q: CallbackQuery):
    await q.answer()
    await q.message.answer(
        "<b>Maxfiylik</b>\n\n"
        "Sizning javoblaringiz faqat tahlil uchun ishlatiladi. "
        "Uchinchi shaxslarga ruxsatingizsiz uzatilmaydi. "
        "Ma’lumotlaringiz shifrlangan holda saqlanadi."
    )
''')


def main():
    print("=" * 60)
    print("QADAM Bot v2 — fayllarni yozish")
    print("=" * 60)
    for path, content in FILES.items():
        full = ROOT / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        size = len(content.encode("utf-8"))
        print("  [OK] {} ({} bayt)".format(path, size))
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yozildi!")


if __name__ == "__main__":
    main()