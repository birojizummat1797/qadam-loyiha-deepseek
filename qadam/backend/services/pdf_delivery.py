"""Send the Action Document (PDF) to the user through the bot."""
import os

from backend.logger import log


def pdf_caption(first_name: str | None, career_uz: str | None, filename: str) -> str:
    """Neutral caption: a direction close to the user's signals, not a verdict."""
    name = first_name or "do'stim"
    lines = [
        f"<b>{name}, natijangiz tayyor.</b>\n",
        "Qadam.io diagnostikasi va shaxsiy yo'l xaritasi ilova qilindi.\n",
    ]
    if career_uz:
        lines.append(f"📌 <b>Signallaringizga yaqin yo'nalish:</b> {career_uz}")
    lines += [
        f"📄 <b>Fayl:</b> {filename}\n",
        "Bu tavsiya, hukm emas — qarorni siz qilasiz.",
        "Savollar bo'lsa — @ulugbek_aliboyev",
    ]
    return "\n".join(lines)


async def send_pdf(user: dict, pdf_bytes: bytes, filename: str, career_uz: str | None) -> bool:
    """True if Telegram accepted the document. Never raises."""
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import BufferedInputFile

        bot = Bot(os.getenv("BOT_TOKEN", ""), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        try:
            await bot.send_document(
                user["id"],
                document=BufferedInputFile(pdf_bytes, filename=filename),
                caption=pdf_caption(user.get("first_name"), career_uz, filename),
            )
        finally:
            await bot.session.close()
        return True
    except Exception as e:
        log.error(f"Bot PDF yuborishda xato: {e}")
        return False
