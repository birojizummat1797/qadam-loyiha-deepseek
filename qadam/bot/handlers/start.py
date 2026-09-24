"""
FTT § 4-5: Welcome flow + Premium intro.
Tugmalar Mini App'ni ochadi.
"""
import os
from html import escape
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)

router = Router()

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://qadam-loyiha-deepseek-eight.vercel.app")

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
    "Sizni <b>Qadam.io Premium Personal Diagnostic</b>’da ko‘rib turganimizdan "
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
    "<b>Qadam.io yordam</b>\n\n"
    "/start — boshidan boshlash\n"
    "/help — yordam\n\n"
    "Savollar bo‘lsa: @ulugbek_aliboyev"
)


def main_menu_kb() -> InlineKeyboardMarkup:
    """Asosiy menyu — Mini App tugmalari."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎯 Bepul diagnostika",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/stage1"),
        )],
        [InlineKeyboardButton(
            text="💎 Premium diagnostika",
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
    """Premium intro — Mini App ochish."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Diagnostikani boshlash",
            web_app=WebAppInfo(url=WEBAPP_URL),
        )],
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
        "1. Siz savollarga javob berasiz.\n"
        "2. Tizim javoblaringizni signallarga aylantiradi.\n"
        "3. Signallar 25+ kasbiy yo‘nalish bilan taqqoslanadi.\n"
        "4. Sizga eng mos 3 ta yo‘nalish va amaliy roadmap beriladi.\n\n"
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
