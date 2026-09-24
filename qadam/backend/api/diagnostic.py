"""
Diagnostic API — Stage 1 (free), Stage 2 (premium), Report.
"""
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models import User, TestResult
from backend.auth import verify_init_data
from backend.data_loader import (
    load_questions, load_taxonomy, get_versions,
)
from backend.engine.signals import signals_from_answers
from backend.engine.ranking import rank_careers
from backend.engine.roadmap import build_full_report
from backend.ai.personalizer import personalize
from backend.security.rate_limit import check as rl_check
from backend.logger import log

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])

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


def _extract_constraints(answers: dict) -> dict:
    return {
        "time": answers.get("s1_q6"),
        "device": answers.get("s1_q7"),
        "english": answers.get("s1_q8"),
    }


def _stage1_seed_signals(answers: dict) -> dict:
    """Stage 1 → taxminiy signallar (teaser uchun yetarli)."""
    seed = {}
    q4 = answers.get("s1_q4")
    seed_map = {
        "tech": {"logical_thinking": 0.7, "technical_interest": 0.8},
        "creative": {"creative_design": 0.8, "visual_logic": 0.7},
        "people": {"user_empathy": 0.8, "business_sense": 0.6},
        "analysis": {"analytical": 0.8, "math_logic": 0.7, "attention_to_detail": 0.7},
        "business": {"business_sense": 0.8, "persistence": 0.6},
        "systems": {"system_design": 0.8, "attention_to_detail": 0.7},
    }
    if q4 and q4 in seed_map:
        for k, v in seed_map[q4].items():
            seed[k] = {"score": v, "measured": True, "coverage": 1, "confidence": 0.4}

    q5 = answers.get("s1_q5") or []
    if isinstance(q5, str):
        q5 = [q5]
    sector_boost = {
        "software": ["logical_thinking", "problem_solving"],
        "data_ai": ["analytical", "math_logic"],
        "design": ["creative_design", "visual_logic"],
        "marketing": ["business_sense", "user_empathy"],
        "media": ["creative_design"],
        "product": ["system_design", "business_sense"],
        "business": ["business_sense", "persistence"],
        "security": ["attention_to_detail", "persistence"],
    }
    for sector in q5:
        for sig in sector_boost.get(sector, []):
            if sig in seed:
                seed[sig]["score"] = min(1.0, seed[sig]["score"] + 0.15)
            else:
                seed[sig] = {"score": 0.55, "measured": True, "coverage": 1, "confidence": 0.35}
    return seed


def _top_signals_list(signals: dict, n: int) -> list:
    items = [
        {"key": k, "score": v["score"], "confidence": v.get("confidence", 0)}
        for k, v in signals.items()
        if v.get("measured") and v.get("score") is not None
    ]
    items.sort(key=lambda x: (-x["score"], -x["confidence"]))
    return items[:n]


@router.get("/questions")
async def get_questions():
    """Stage 1 + Stage 2 savollari."""
    return load_questions()


@router.post("/stage1")
async def stage1(payload: Stage1Payload):
    user = _auth(payload.init_data)

    if not rl_check(user["id"], "stage1", max_per_window=10, window_sec=3600):
        raise HTTPException(429, "Juda ko'p urinish. 1 soatdan keyin.")

    questions = load_questions()
    expected = len(questions["stage_1"]["questions"])
    if len(payload.answers) < expected:
        raise HTTPException(400, "Barcha savollarga javob bering")

    seed_signals = _stage1_seed_signals(payload.answers)
    taxonomy = load_taxonomy()
    constraints = _extract_constraints(payload.answers)

    ranking = rank_careers(
        signals=seed_signals, taxonomy=taxonomy,
        constraints=constraints, min_coverage=0.3, top_n=3,
    )
    top_2 = ranking["ranked"][:2]
    locked_count = max(0, len(ranking["ranked"]) - 2)

    async with SessionLocal() as s:
        u = await s.get(User, user["id"])
        if not u:
            u = User(id=user["id"], username=user.get("username"),
                     first_name=user.get("first_name"))
            s.add(u)
            await s.flush()

        teaser = TestResult(
            user_id=user["id"], stage="stage1",
            answers=payload.answers,
            profile={"seed_signals": seed_signals, "constraints": constraints},
            roadmap={"teaser": True},
            versions=get_versions(), paid=False,
        )
        s.add(teaser)
        await s.commit()
        await s.refresh(teaser)
        teaser_id = teaser.id

    log.info("stage1_completed", extra={"user_id": user["id"], "action": "stage1"})

    return {
        "stage1_result_id": teaser_id,
        "top_2_signals": _top_signals_list(seed_signals, 2),
        "top_2_careers": top_2,
        "locked_count": locked_count,
        "confidence": ranking["confidence"],
        "next": "premium_required",
    }


@router.post("/stage2")
async def stage2(payload: Stage2Payload):
    user = _auth(payload.init_data)

    if not rl_check(user["id"], "stage2", max_per_window=3, window_sec=3600):
        raise HTTPException(429, "Juda ko'p urinish.")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 natijasi topilmadi")
        if not s1.paid:
            raise HTTPException(402, "To'lov tasdiqlanmagan")
        merged = {**s1.answers, **payload.answers}

    if len(payload.answers) < 18:
        raise HTTPException(400, "Barcha 18 savolga javob bering")

    questions = load_questions()
    signals = signals_from_answers(merged, questions)
    taxonomy = load_taxonomy()
    constraints = _extract_constraints(merged)

    ranking = rank_careers(
        signals=signals, taxonomy=taxonomy,
        constraints=constraints, min_coverage=0.5, top_n=3,
    )
    if not ranking["ranked"]:
        raise HTTPException(422, "Yetarli ma'lumot yo'q")

    report = build_full_report(ranking["ranked"], constraints, taxonomy, signals)
    ai_explanation = await personalize(signals, ranking["ranked"], ranking["confidence"])

    async with SessionLocal() as s:
        result = TestResult(
            user_id=user["id"], stage="stage2",
            answers=merged,
            profile={"signals": signals, "constraints": constraints,
                     "confidence": ranking["confidence"]},
            roadmap=report,
            ai_explanation=ai_explanation,
            versions=get_versions(), paid=True,
        )
        s.add(result)
        await s.commit()
        await s.refresh(result)
        result_id = result.id

    log.info("stage2_completed", extra={
        "user_id": user["id"], "action": "stage2",
        "extra": {"report_id": result_id, "ai_source": ai_explanation.get("source")},
    })

    return {
        "report_id": result_id,
        "confidence": ranking["confidence"],
        "ai": ai_explanation,
        "careers": report["careers"],
    }


@router.get("/report/{report_id}")
async def get_report(report_id: int, init_data: str = Query(...)):
    user = _auth(init_data)
    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")
        return {
            "id": r.id, "stage": r.stage,
            "profile": r.profile, "roadmap": r.roadmap,
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
    """
    DEV MODE ONLY: to'lovsiz stage1'ni paid deb belgilaydi.
    Production'da ishlamaydi.
    """
    if ENV != "development":
        raise HTTPException(403, "Faqat development uchun")

    user = _auth(payload.init_data)

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        s1.paid = True
        await s.commit()

    return {"ok": True, "stage1_result_id": payload.stage1_result_id, "paid": True}

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
        top_career = careers[0]["career"]["uz"] if careers else "sizga mos yonalish"

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
            f"Siz QADAM diagnostikasidan muvaffaqiyatli otdingiz va "
            f"o'zingizga mos yonalish bo'yicha shaxsiy roadmapni qolga kiritdingiz.\n\n"
            f"📌 <b>Sizning asosiy yonalishingiz:</b> {top_career}\n\n"
            f"Roadmapni 3 xil dizaynda yuklab olishingiz mumkin. "
            f"Reja boyicha bugun birinchi qadamni boshlang!\n\n"
            f"<b>Savollar bo'lsa</b> bemalol murojaat qiling — biz shu yerdamiz.\n\n"
            f"<i>Sizning muvaffaqiyatingiz — bizning maqsadimiz.</i>\n"
            f"— QADAM jamoasi"
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
    sent = False
    try:
        import os
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import BufferedInputFile

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "dostim"
        top_career = "sizga mos yonalish"
        careers = (r.roadmap or {}).get("careers", [])
        if careers:
            top_career = careers[0]["career"]["uz"]

        caption = (
            f"🎉 <b>Tabriklaymiz, {first_name}!</b>\n\n"
            f"QADAM diagnostikasi natijangiz va shaxsiy roadmap tayyor.\n\n"
            f"📌 <b>Asosiy yonalish:</b> {top_career}\n"
            f"📄 <b>Fayl:</b> QADAM-report-{report_id}.pdf\n\n"
            f"Reja boyicha bugun birinchi qadamni boshlang!\n"
            f"Savollar bolsa — @qadam_support\n\n"
            f"<i>Sizning muvaffaqiyatingiz — bizning maqsadimiz.</i>\n"
            f"— QADAM jamoasi"
        )

        file = BufferedInputFile(pdf_bytes, filename=f"QADAM-report-{report_id}.pdf")
        await bot.send_document(user["id"], document=file, caption=caption)
        await bot.session.close()
        sent = True
    except Exception as e:
        log.error(f"Bot PDF yuborishda xato: {e}")

    return {"ok": True, "report_id": report_id, "sent_to_telegram": sent}
