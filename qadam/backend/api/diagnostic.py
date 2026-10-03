"""
Diagnostic API — Stage 1 (free), Stage 2 (premium), Report.
"""
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.db import SessionLocal
from backend.models import TestResult
from backend.auth import verify_init_data
from backend.data_loader import load_questions
from backend.engine.public_output import strip_unsupported
from backend.logger import log

router = APIRouter(prefix="/diagnostic", tags=["diagnostic (v0, deprecated)"])

V0_GONE = (
    "Bu eski diagnostika yo'li o'chirilgan. Yangi diagnostika: Mini App → Diagnostika. "
    "Eski hisobotlar faqat o'qish uchun ochiq."
)

APP_URL = os.getenv("APP_URL", "https://qadam.uz")

ENV = os.getenv("ENV", "development")


class Stage1Payload(BaseModel):
    init_data: str
    answers: dict


class Stage2Payload(BaseModel):
    init_data: str
    answers: dict
    stage1_result_id: int


def _auth(init_data: str) -> dict:
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    return user


@router.get("/questions")
async def get_questions():
    """Stage 1 + Stage 2 savollari."""
    return load_questions()


@router.post("/stage1")
async def stage1(payload: Stage1Payload):
    """DEPRECATED v0 (PM gate 2026-10-03). Live flow: /api/v1/discovery → /api/v1/deep-diagnostic."""
    raise HTTPException(410, V0_GONE)


@router.post("/stage2")
async def stage2(payload: Stage2Payload):
    """DEPRECATED v0 (PM gate 2026-10-03). Live flow: /api/v1/deep-diagnostic."""
    raise HTTPException(410, V0_GONE)


@router.get("/report/{report_id}")
async def get_report(report_id: int, init_data: str = Query(...)):
    user = _auth(init_data)
    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")
        return {
            "id": r.id, "stage": r.stage,
            "profile": r.profile, "roadmap": strip_unsupported(r.roadmap),
            "ai": r.ai_explanation, "versions": r.versions,
            "created_at": r.created_at,
        }


@router.get("/report/{report_id}/summary")
async def get_report_summary(report_id: int, init_data: str = Query(...)):
    """Faqat asosiy natija (Mini App uchun yengilroq)."""
    user = _auth(init_data)
    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")
        careers = (r.roadmap or {}).get("careers", [])
        return {
            "id": r.id,
            "confidence": (r.profile or {}).get("confidence"),
            "ai": r.ai_explanation,
            "top_careers": [
                {
                    "id": c["career"]["id"],
                    "uz": c["career"]["uz"],
                    "cluster_uz": c["career"]["cluster_uz"],
                    "fit": c["fit"],
                    "readiness": c["readiness"],
                    "barriers_count": len(c["barriers"]),
                }
                for c in careers[:3]
            ],
        }



# ═══════════════ DEV UNLOCK (faqat development uchun) ═══════════════

class DevUnlockPayload(BaseModel):
    init_data: str
    stage1_result_id: int


@router.post("/dev-unlock")
async def dev_unlock(payload: DevUnlockPayload):
    """REMOVED: marked a stage as paid without payment; ENV defaulted to "development"."""
    raise HTTPException(410, V0_GONE)


# ═══════════════════════════════════════════════════════════════════
# REPORT COMPLETE — Foydalanuvchi PDF yuklab olgach xabar yuborish
# ═══════════════════════════════════════════════════════════════════

class ReportCompletePayload(BaseModel):
    init_data: str


@router.post("/report/{report_id}/complete")
async def report_complete(report_id: int, payload: ReportCompletePayload):
    """
    User PDF yuklab olgach chaqiriladi.
    Bot orqali tabrik xabari yuboriladi.
    """
    user = _auth(payload.init_data)

    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")

        # Top-1 career nomi
        careers = (r.roadmap or {}).get("careers", [])
        top_career = careers[0]["career"]["uz"] if careers else "tanlangan yo'nalish"

    # Bot orqali xabar yuborish
    try:
        import os
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "dostim"

        text = (
            f"🎉 <b>Tabriklaymiz, {first_name}!</b>\n\n"
            f"Siz Qadam.io diagnostikasidan muvaffaqiyatli otdingiz va "
            f"o'zingizga mos yonalish bo'yicha shaxsiy roadmapni qolga kiritdingiz.\n\n"
            f"📌 <b>Sizning asosiy yonalishingiz:</b> {top_career}\n\n"
            f"Roadmapni 3 xil dizaynda yuklab olishingiz mumkin. "
            f"Reja boyicha bugun birinchi qadamni boshlang!\n\n"
            f"<b>Savollar bo'lsa</b> bemalol murojaat qiling — biz shu yerdamiz.\n\n"
            f"<i>Sizning muvaffaqiyatingiz — bizning maqsadimiz.</i>\n"
            f"— Qadam.io jamoasi"
        )

        webapp = os.getenv("WEBAPP_URL", "")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Hisobotni qayta ochish",
                web_app=WebAppInfo(url=f"{webapp}/report/{report_id}"),
            )],
            [InlineKeyboardButton(
                text="🚀 Yangi diagnostika",
                web_app=WebAppInfo(url=f"{webapp}/stage1"),
            )],
            [InlineKeyboardButton(
                text="💬 Yordam",
                url="https://t.me/qadam_support",
            )],
        ])

        await bot.send_message(user["id"], text, reply_markup=kb)

        # Bot sessionni yopish
        await bot.session.close()

    except Exception as e:
        log.error(f"Bot xabar yuborishda xato: {e}")

    return {"ok": True, "report_id": report_id}

# ═══════════════════════════════════════════════════════════════════
# PDF — Server-side PDF + bot orqali fayl yuborish
# ═══════════════════════════════════════════════════════════════════


class PdfRequestPayload(BaseModel):
    init_data: str
    theme: str = "light"


@router.post("/report/{report_id}/pdf")
async def report_pdf(report_id: int, payload: PdfRequestPayload):
    """PDF yaratadi va bot orqali foydalanuvchiga yuboradi."""
    user = _auth(payload.init_data)

    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")

        report_data = {
            "id": r.id,
            "profile": r.profile,
            "roadmap": r.roadmap,
            "ai": r.ai_explanation,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }

    # PDF yaratish
    try:
        from backend.pdf_report import generate_pdf
        pdf_bytes = generate_pdf(report_data, theme=payload.theme)
    except Exception as e:
        log.error(f"PDF xatoligi: {e}")
        raise HTTPException(500, f"PDF xatolik: {str(e)[:100]}")

    # Bot orqali yuborish
    from backend.services.pdf_delivery import send_pdf

    careers = (r.roadmap or {}).get("careers", [])
    top_career = careers[0]["career"]["uz"] if careers else None
    sent = await send_pdf(user, pdf_bytes, f"QADAM-report-{report_id}.pdf", top_career)

    return {"ok": True, "report_id": report_id, "sent_to_telegram": sent}
