"""
Natija tayyor bo'lganda botga xabar yuborish.
"""
import os
from aiogram import Router, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

router = Router()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://qadam.uz")


async def notify_report_ready(bot: Bot, user_id: int, report_id: int):
    """Backend /stage2 tugagach chaqiriladi."""
    url = f"{WEBAPP_URL}/report/{report_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📊 Natijani ko'rish", web_app=WebAppInfo(url=url))
    ]])
    try:
        await bot.send_message(
            user_id,
            "🎉 <b>Tahlilingiz tayyor!</b>\n\n"
            "Sizning Fit, Readiness, skill-gap va shaxsiy roadmap'ingiz tayyor.",
            reply_markup=kb,
        )
    except Exception:
        pass