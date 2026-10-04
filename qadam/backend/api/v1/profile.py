"""Profile API v1."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.db import SessionLocal
from backend.models_v2 import Profile
from backend.auth import verify_init_data
from backend.services import age_gate

router = APIRouter(prefix="/api/v1/profile", tags=["profile-v1"])


class ProfilePayload(BaseModel):
    init_data: str
    location: str | None = None
    current_status: str | None = None
    education: str | None = None
    work_context: str | None = None


@router.get("")
async def get_profile(init_data: str = Query(...)):
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        p = await s.get(Profile, user["id"])
        if not p:
            return {"user_id": user["id"], "profile": None}
        return {
            "user_id": user["id"],
            "profile": {
                "age": p.age,
                "location": p.location,
                "current_status": p.current_status,
                "education": p.education,
                "work_context": p.work_context,
            },
        }


@router.post("")
async def upsert_profile(payload: ProfilePayload):
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    # Age is set only through /gate (consent + 18+ policy), never here.
    async with SessionLocal() as s:
        p = await s.get(Profile, user["id"])
        if not p:
            p = Profile(user_id=user["id"])
            s.add(p)

        if payload.location is not None:
            p.location = payload.location[:64]
        if payload.current_status is not None:
            p.current_status = payload.current_status[:32]
        if payload.education is not None:
            p.education = payload.education[:64]
        if payload.work_context is not None:
            p.work_context = payload.work_context[:128]

        await s.commit()
        await s.refresh(p)
        return {"ok": True, "user_id": user["id"]}


class GatePayload(BaseModel):
    init_data: str
    consent: bool
    age: int


@router.get("/gate")
async def gate_status(init_data: str = Query(...)):
    """required | ok (+ age_warning for 35+)."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    return await age_gate.status(user["id"])


@router.post("/gate")
async def gate_submit(payload: GatePayload):
    """Consent + self-reported age. Under 18 → nothing stored, status under_age."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    return await age_gate.submit(user, payload.consent, payload.age)
