"""
AI personalization — OpenRouter orqali.
Master § 26: AI assists; controlled system logic decides.
Master § 27: AI output must be schema-validated. Invalid → deterministic fallback.
"""
import os
import json
import httpx
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-flash-1.5")
APP_URL = os.getenv("APP_URL", "https://qadam.uz")


class AIExplanation(BaseModel):
    """AI faqat IZOH va SHAXSIYLASHTIRISH qiladi. Ballar bu yerga kirmaydi."""
    summary: str = Field(min_length=40, max_length=600)
    why_this_fits: list[str] = Field(min_length=2, max_length=5)
    risks: list[str] = Field(default_factory=list, max_length=3)
    next_step_emphasis: str = Field(min_length=20, max_length=300)


SYSTEM_PROMPT = """Sen Qadam.io loyihasining kasb yo'naltiruvchi maslahatchisisan.
Senga deterministic tizim tomonidan hisoblangan natijalar beriladi.
Sening vazifang — FAQAT izoh yozish va shaxsiylashtirish.

QAT'IY QOIDALAR:
1. Ballarni o'zgartirmaysan, yangi ball qo'shmaysan.
2. Yangi kasb o'ylab topmaysan — faqat berilgan ro'yxatdan.
3. "Siz albatta..." deb va'da bermaysan.
4. Maosh raqamlarini o'zingdan to'qimaysan.
5. Faqat quyidagi JSON formatda javob qaytarasan:

{
  "summary": "2-3 gap, umumiy xulosa",
  "why_this_fits": ["sabab 1", "sabab 2"],
  "risks": ["ogohlantirish"],
  "next_step_emphasis": "eng muhim birinchi qadam (1-2 gap)"
}
"""


def _build_user_prompt(profile: dict, ranked: list, confidence: str) -> str:
    signals_summary = {
        k: round(v["score"], 3)
        for k, v in profile.items()
        if v.get("score") is not None
    }
    careers_summary = [
        {
            "career": c["career_uz"],
            "cluster": c["cluster_uz"],
            "fit": c["fit"],
            "readiness": c["readiness"],
            "barriers_count": len(c["barriers"]),
        }
        for c in ranked[:5]
    ]
    return f"""Foydalanuvchi signallari (0-1 shkalada):
{json.dumps(signals_summary, ensure_ascii=False)}

Top-5 mos yo'nalishlar (deterministik):
{json.dumps(careers_summary, ensure_ascii=False)}

Confidence: {confidence}

Vazifa: foydalanuvchi uchun qisqa, halol va aniq IZOH yoz.
O'zbek tilida yoz. Raqamlarni o'zgartirmasdan.
"""


async def personalize(profile: dict, ranked: list, confidence: str) -> dict:
    """
    AI izoh yaratadi. Xatolik bo'lsa — deterministic fallback.
    """
    if not OPENROUTER_KEY:
        return {"source": "fallback", "reason": "no_api_key", **_fallback(ranked)}

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(profile, ranked, confidence)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5,
        "max_tokens": 800,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "HTTP-Referer": APP_URL,
        "X-Title": "Qadam.io",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(OPENROUTER_URL, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        content = data["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("```")[1].replace("json", "", 1).strip()

        parsed = json.loads(content)
        validated = AIExplanation.model_validate(parsed)
        return {"source": "ai", "model": MODEL, **validated.model_dump()}

    except (httpx.HTTPError, json.JSONDecodeError, ValidationError, KeyError) as e:
        return {"source": "fallback", "reason": str(e)[:100], **_fallback(ranked)}


def _fallback(ranked: list) -> dict:
    """AI ishlamasa — buni ishlatamiz. Master § 27."""
    if not ranked:
        return {
            "summary": "Profil bo'yicha hozircha yetarli ma'lumot yo'q.",
            "why_this_fits": ["Ma'lumot yetarli emas"],
            "risks": [],
            "next_step_emphasis": "Barcha savollarga samimiy javob bering.",
        }

    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None

    summary = (
        f"Sizning profilingiz {top['career_uz']} yo'nalishiga eng mos keladi "
        f"(Fit: {top['fit']}%, Readiness: {top['readiness']}%)."
    )
    if second:
        summary += f" Shuningdek {second['career_uz']} ham variant sifatida ko'rilishi mumkin."

    why = [f"{top['career_uz']} signallaringizga mos keladi."]
    if top.get("coverage", 0) >= 0.7:
        why.append("Yetarli ma'lumot yig'ildi.")
    if top.get("readiness", 0) >= 70:
        why.append("Hozirgi sharoitda boshlash uchun tayyorlik yuqori.")
    if not why:
        why.append("Profilingiz bu yo'nalishga qisman mos keladi.")

    risks = []
    if top.get("has_hard_barrier"):
        risks.append("Hozir jiddiy to'siq bor.")
    if top.get("coverage", 1) < 0.7:
        risks.append("Ba'zi signallar to'liq o'lchanmagan.")
    if not risks:
        risks.append("Uzoq muddatli harakat talab qilinadi.")

    return {
        "summary": summary[:600],
        "why_this_fits": why[:5],
        "risks": risks[:3],
        "next_step_emphasis": (
            "Eng muhim birinchi qadam — kichik, aniq va bugun bajarilishi mumkin bo'lgan harakat."
        ),
    }