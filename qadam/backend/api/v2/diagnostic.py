"""Diagnostic v2 API (9×25 catalog) — DRAFT, founder review pending.

Not linked from the bot or the main Mini App flow: reachable only via the
/v2 Mini App route. The v1 discovery / deep diagnostic flow is unchanged.

Answers are submitted once per stage (stateless questions, one stored result
per finished stage). Correct task answers never leave the server.
"""
import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc

from backend.auth import verify_init_data
from backend.db import SessionLocal
from backend.engine import diagnostic_v2 as dv2
from backend.models import Event
from backend.models_v2 import DiagnosticV2Result
from backend.services import age_gate

router = APIRouter(prefix="/api/v2/diagnostic", tags=["diagnostic-v2"])

MAX_META_BYTES = 8_000


class InitPayload(BaseModel):
    init_data: str


class DeepQuestionsPayload(BaseModel):
    init_data: str
    catalogs: list[str] = Field(min_length=1, max_length=2)


class DiscoverySubmit(BaseModel):
    init_data: str
    answers: dict[str, str]
    meta: dict | None = None


class DeepSubmit(BaseModel):
    init_data: str
    catalogs: list[str] = Field(min_length=1, max_length=2)
    answers: dict[str, str]
    ease: dict[str, str] = {}
    meta: dict | None = None


async def _user(init_data: str) -> dict:
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    await age_gate.require_adult(user["id"])
    return user


def _check_meta(meta):
    if meta is not None and len(json.dumps(meta)) > MAX_META_BYTES:
        raise HTTPException(400, "meta too large")


def _valid_answers(answers: dict, questions: list, required: bool = True):
    """Every question answered (when required) with one of its own option IDs; nothing extra."""
    allowed = {q["id"]: {o["id"] for o in q["options"]} for q in questions}
    extra = set(answers) - set(allowed)
    if extra:
        raise HTTPException(400, f"Noma’lum savollar: {sorted(extra)[:3]}")
    for qid, opts in allowed.items():
        if qid not in answers:
            if required:
                raise HTTPException(400, "Barcha savollarga javob bering")
            continue
        if answers[qid] not in opts:
            raise HTTPException(400, f"Noto‘g‘ri javob: {qid}")


@router.post("/discovery/questions")
async def discovery_questions(payload: InitPayload):
    await _user(payload.init_data)
    return dv2.discovery_questions_public()


@router.post("/discovery/submit")
async def discovery_submit(payload: DiscoverySubmit):
    user = await _user(payload.init_data)
    _check_meta(payload.meta)
    _valid_answers(payload.answers, dv2.discovery_questions_public()["questions"])

    result = dv2.score_discovery(payload.answers)
    result["conditions"] = dv2.extract_conditions(payload.answers)
    async with SessionLocal() as s:
        row = DiagnosticV2Result(
            user_id=user["id"], stage="discovery", data_version=dv2.load_data()["version"],
            catalogs=[c["id"] for c in result["catalogs"]], answers=payload.answers,
            result=result, meta=payload.meta,
        )
        s.add(row)
        await s.commit()
        await s.refresh(row)
    return {"result_id": row.id, **dv2.public_result(result)}


@router.post("/deep/questions")
async def deep_questions(payload: DeepQuestionsPayload):
    await _user(payload.init_data)
    try:
        return dv2.deep_questions_public(payload.catalogs)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/deep/submit")
async def deep_submit(payload: DeepSubmit):
    user = await _user(payload.init_data)
    _check_meta(payload.meta)
    try:
        public = dv2.deep_questions_public(payload.catalogs)
    except ValueError as e:
        raise HTTPException(400, str(e))

    required = public["a_part"] + public["style"] + public["readiness"] + public["tasks"] + public["lesson"]["questions"]
    _valid_answers(payload.answers, required)
    ease_ids = {o["id"] for o in public["ease"]["options"]}
    task_ids = {t["id"] for t in public["tasks"]}
    if set(payload.ease) - task_ids or any(v not in ease_ids for v in payload.ease.values()):
        raise HTTPException(400, "Noto‘g‘ri osonlik javobi")

    result = dv2.score_deep(payload.catalogs, payload.answers, payload.ease)
    async with SessionLocal() as s:
        row = DiagnosticV2Result(
            user_id=user["id"], stage="deep", data_version=dv2.load_data()["version"],
            catalogs=payload.catalogs, answers={**payload.answers, "_ease": payload.ease},
            result=result, meta=payload.meta,
        )
        s.add(row)
        await s.commit()
        await s.refresh(row)
    return {"result_id": row.id, **dv2.public_result(result)}


@router.get("/latest")
async def latest(init_data: str = Query(...)):
    user = await _user(init_data)
    out = {}
    async with SessionLocal() as s:
        for stage in ("discovery", "deep"):
            row = (await s.execute(
                select(DiagnosticV2Result)
                .where(DiagnosticV2Result.user_id == user["id"], DiagnosticV2Result.stage == stage)
                .order_by(desc(DiagnosticV2Result.id)).limit(1)
            )).scalar_one_or_none()
            out[stage] = {"result_id": row.id, **dv2.public_result(row.result)} if row else None
    return out


def _build_roadmap(career_id: str) -> dict:
    rm = dv2.build_roadmap(career_id)
    if rm is None:
        raise HTTPException(404, "Bu kasb uchun yo‘l xaritasi hali tayyor emas")
    return rm


@router.get("/roadmap/{career_id}")
async def roadmap(career_id: str, init_data: str = Query(...)):
    await _user(init_data)
    return _build_roadmap(career_id)


# Founder request (2026-10-08): after the roadmap opens in the Mini App, the same
# roadmap is also sent to the user's bot chat as a PDF document.
PDF_EVENT = "v2_roadmap_pdf_sent"
PDF_COOLDOWN = timedelta(minutes=10)      # automatic send: once per career per 10 minutes
PDF_FORCE_COOLDOWN = timedelta(minutes=1)  # "Qayta yuborish" button: at most once a minute


class PdfPayload(BaseModel):
    init_data: str
    force: bool = False


def _utc(dt):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt


@router.post("/roadmap/{career_id}/pdf")
async def roadmap_pdf(career_id: str, payload: PdfPayload):
    """Send this career's roadmap as a PDF to the user's bot chat.

    Only for a career in the user's latest deep result (the PDF repeats that
    result's evidence). Repeated calls within the cooldown are not re-sent.
    """
    from backend.pdf_report import generate_v2_roadmap_pdf
    from backend.services.pdf_delivery import send_pdf

    user = await _user(payload.init_data)
    rm = _build_roadmap(career_id)
    async with SessionLocal() as s:
        row = (await s.execute(
            select(DiagnosticV2Result)
            .where(DiagnosticV2Result.user_id == user["id"], DiagnosticV2Result.stage == "deep")
            .order_by(desc(DiagnosticV2Result.id)).limit(1)
        )).scalar_one_or_none()
        recent = (await s.execute(
            select(Event)
            .where(Event.user_id == user["id"], Event.event_name == PDF_EVENT)
            .order_by(desc(Event.id)).limit(20)
        )).scalars().all()

    career = next((c for c in (row.result.get("careers") or []) if c["id"] == career_id), None) if row else None
    if career is None:
        raise HTTPException(409, "Bu kasb oxirgi chuqur tahlil natijangizda yo‘q")

    now = datetime.now(timezone.utc)
    window = PDF_FORCE_COOLDOWN if payload.force else PDF_COOLDOWN
    for e in recent:
        if (e.payload or {}).get("career_id") == career_id and e.created_at and now - _utc(e.created_at) < window:
            return {"ok": True, "sent_to_telegram": False, "already_sent": True}

    catalog_uz = dv2.catalogs_by_id().get(career["catalog"], {}).get("uz", "")
    pdf_bytes = generate_v2_roadmap_pdf(career["uz"], catalog_uz, rm, dv2.public_result(row.result))
    sent = await send_pdf(user, pdf_bytes, f"QADAM-yol-xaritasi-{career_id}.pdf", career["uz"])
    if sent:
        async with SessionLocal() as s:
            s.add(Event(user_id=user["id"], event_name=PDF_EVENT,
                        payload={"career_id": career_id, "result_id": row.id, "force": payload.force}))
            await s.commit()
    return {"ok": True, "sent_to_telegram": sent, "already_sent": False}
