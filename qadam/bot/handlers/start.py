"""FTT § 4-5: Welcome flow + Mini App buttons (v3)."""
import os
from html import escape
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)

from bot.deeplink import (
    StartAttribution, discovery_url, log_bot_start, resolve_attribution,
)

router = Router()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://qadam-loyiha-deepseek-eight.vercel.app")

WELCOME_TEXT = (
    "Assalomu alaykum, <b>{name}</b>!\n\n"
    "Men — <b>Qadam.io</b>, kasb va soha tanlashda yordamchi.\n\n"
    "Sizga mos yo'nalishni dalillar asosida aniqlash va shaxsiy "
    "yo'l xaritasi tuzishda yordam beraman.\n\n"
    "<b>3 daqiqa</b> — 13 savol — <b>bepul</b>."
)

PREMIUM_INTRO_TEXT = (
    "<b>Chuqur tahlil</b>\n\n"
    "Chuqur tahlil sizga:\n"
    "• 18 qo'shimcha savol\n"
    "• Top-5 mos yo'nalish\n"
    "• Fit va Readiness (har biri uchun)\n"
    "• Skill-gap tahlili\n"
    "• 6-12 oylik shaxsiy yo'l xaritasi\n"
    "• PDF hisobot\n\n"
    "Narx: <b>39 000 so'm</b> yoki <b>150 Stars</b>"
)

HELP_TEXT = (
    "<b>Qadam.io yordam</b>\n\n"
    "/start — boshidan boshlash\n"
    "/help — yordam\n\n"
    "Savollar: @ulugbek_aliboyev"
)


def main_menu_kb(attribution: StartAttribution | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎯 Bepul diagnostika",
            web_app=WebAppInfo(url=discovery_url(WEBAPP_URL, attribution)),
        )],
        [InlineKeyboardButton(
            text="💎 Chuqur tahlil (premium)",
            callback_data="diag:premium",
        )],
        [InlineKeyboardButton(
            text="ℹ️ Qadam.io qanday ishlaydi?",
            callback_data="info:how",
        )],
        [InlineKeyboardButton(
            text="🔐 Maxfiylik",
            callback_data="info:privacy",
        )],
    ])


def premium_intro_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Bepul diagnostikadan boshlash",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/discovery"),
        )],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="nav:back")],
    ])


def _safe_name(user) -> str:
    return escape(user.first_name or "do'stim")


@router.message(CommandStart())
async def cmd_start(m: Message, command: CommandObject | None = None):
    # Website deep link (t.me/<bot>?start=w1-...). Invalid or missing → old flow.
    attribution = await resolve_attribution(command.args if command else None)
    if attribution:
        await log_bot_start(m.from_user.id, attribution)
    await m.answer(
        WELCOME_TEXT.format(name=_safe_name(m.from_user)),
        reply_markup=main_menu_kb(attribution),
    )


@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(HELP_TEXT)


@router.callback_query(F.data == "diag:premium")
async def cb_premium(q: CallbackQuery):
    await q.answer()
    try:
        await q.message.edit_text(PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb())
    except Exception:
        await q.message.answer(PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb())


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
        "<b>Qadam.io qanday ishlaydi?</b>\n\n"
        "1. Siz 13 ta savolga javob berasiz (3 daqiqa).\n"
        "2. Tizim javoblarni signallarga aylantiradi.\n"
        "3. Signallar 25+ kasbiy yo'nalish bilan taqqoslanadi.\n"
        "4. Sizga mos 3 ta yo'nalish va amaliy yo'l xaritasi beriladi.\n\n"
        "<i>Halol tahlil. Manipulyatsiyasiz.</i>"
    )


@router.callback_query(F.data == "info:privacy")
async def cb_privacy(q: CallbackQuery):
    await q.answer()
    await q.message.answer(
        "<b>Maxfiylik</b>\n\n"
        "Javoblaringiz faqat tahlil uchun ishlatiladi. "
        "Uchinchi shaxslarga ruxsatsiz uzatilmaydi."
    )


@router.message(Command("admin"))
async def cmd_admin(m: Message):
    admin_ids = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if m.from_user.id not in admin_ids:
        await m.answer("Ruxsat yo'q")
        return

    url = f"{WEBAPP_URL}/admin"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Admin Panel", web_app=WebAppInfo(url=url))
    ]])
    await m.answer("Admin panel:", reply_markup=kb)
