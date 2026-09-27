"""Entitlements API v1."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from backend.db import SessionLocal
from backend.models_v2 import Entitlement
from backend.auth import verify_init_data

router = APIRouter(prefix="/api/v1/entitlements", tags=["entitlements-v1"])


@router.get("/me")
async def my_entitlements(init_data: str = Query(...)):
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        q = (
            select(Entitlement)
            .where(Entitlement.user_id == user["id"])
            .order_by(Entitlement.created_at.desc())
        )
        rows = (await s.execute(q)).scalars().all()

    return {
        "entitlements": [
            {
                "id": e.id,
                "key": e.entitlement_key,
                "status": e.status,
                "source": e.source,
                "activated_at": e.activated_at.isoformat() if e.activated_at else None,
                "expires_at": e.expires_at.isoformat() if e.expires_at else None,
                "plan_code": e.plan_code,
            }
            for e in rows
        ]
    }


@router.get("/check")
async def check_entitlement(
    entitlement_key: str = Query(...),
    init_data: str = Query(...),
):
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    from backend.services.entitlement_service import has_active_entitlement
    ok = await has_active_entitlement(user["id"], entitlement_key)
    return {"user_id": user["id"], "entitlement_key": entitlement_key, "active": ok}
