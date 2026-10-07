"""Diagnostic v2 API (9×25 catalog) — DRAFT, founder review pending.

Not linked from the bot or the main Mini App flow: reachable only via the
/v2 Mini App route. The v1 discovery / deep diagnostic flow is unchanged.

Answers are submitted once per stage (stateless questions, one stored result
per finished stage). Correct task answers never leave the server.
"""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc

from backend.auth import verify_init_data
from backend.db import SessionLocal
from backend.engine import diagnostic_v2 as dv2
from backend.engine.public_output import strip_unsupported
from backend.engine.roadmap import _build_v2
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


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


@lru_cache(maxsize=1)
def _roadmap_kb() -> tuple[dict, frozenset]:
    """Merged KB (v3 draft + live v2; v2 wins on overlap) and the set of live v2 IDs."""
    v2 = json.loads((DATA_DIR / "roadmap_kb_v2.json").read_text(encoding="utf-8"))["careers"]
    v3 = json.loads((DATA_DIR / "roadmap_kb_v3_draft.json").read_text(encoding="utf-8"))["careers"]
    return {**v3, **v2}, frozenset(v2)


@router.get("/roadmap/{career_id}")
async def roadmap(career_id: str, init_data: str = Query(...)):
    await _user(init_data)
    kb, live = _roadmap_kb()
    if career_id not in kb:
        raise HTTPException(404, "Bu kasb uchun yo‘l xaritasi hali tayyor emas")
    rm = _build_v2(career_id, kb[career_id], {}, {}, None)
    rm["version"] = "v2.0" if career_id in live else "v3.0-draft"
    return strip_unsupported(rm)
