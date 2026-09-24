"""Admin panel API — statistika + feedback."""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc

from backend.db import SessionLocal
from backend.models import User, TestResult, Feedback
from backend.auth import verify_init_data

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_IDS = set(
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
)


def _require_admin(init_data: str) -> dict:
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")
    if user["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")
    return user


@router.get("/overview")
async def overview(init_data: str = Query(...)):
    """Umumiy statistika."""
    _require_admin(init_data)

    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    async with SessionLocal() as s:
        total_users = (await s.execute(select(func.count(User.id)))).scalar() or 0
        new_today = (await s.execute(
            select(func.count(User.id)).where(User.created_at >= today)
        )).scalar() or 0
        new_week = (await s.execute(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )).scalar() or 0

        stage1 = (await s.execute(
            select(func.count(TestResult.id)).where(TestResult.stage == "stage1")
        )).scalar() or 0
        stage2 = (await s.execute(
            select(func.count(TestResult.id)).where(TestResult.stage == "stage2")
        )).scalar() or 0

        # Feedback soni
        try:
            feedback_count = (await s.execute(select(func.count(Feedback.id)))).scalar() or 0
            avg_rating = (await s.execute(select(func.avg(Feedback.rating)))).scalar() or 0
        except Exception:
            feedback_count = 0
            avg_rating = 0

    return {
        "users": {
            "total": total_users,
            "new_today": new_today,
            "new_week": new_week,
        },
        "funnel": {
            "stage1": stage1,
            "stage2": stage2,
            "stage1_to_stage2_pct": round(stage2 / stage1 * 100, 1) if stage1 else 0,
        },
        "feedback": {
            "total": feedback_count,
            "avg_rating": round(float(avg_rating), 2) if avg_rating else 0,
        },
    }


@router.get("/daily")
async def daily(days: int = Query(30, ge=1, le=180), init_data: str = Query(...)):
    """Oxirgi N kun uchun kunlik statistika."""
    _require_admin(init_data)
    since = datetime.utcnow() - timedelta(days=days)

    async with SessionLocal() as s:
        users_q = await s.execute(
            select(func.date(User.created_at).label("d"), func.count(User.id).label("c"))
            .where(User.created_at >= since)
            .group_by(func.date(User.created_at))
        )
        users_by_day = {str(row.d): row.c for row in users_q}

        s1_q = await s.execute(
            select(func.date(TestResult.created_at).label("d"), func.count(TestResult.id).label("c"))
            .where(TestResult.created_at >= since, TestResult.stage == "stage1")
            .group_by(func.date(TestResult.created_at))
        )
        s1_by_day = {str(row.d): row.c for row in s1_q}

        s2_q = await s.execute(
            select(func.date(TestResult.created_at).label("d"), func.count(TestResult.id).label("c"))
            .where(TestResult.created_at >= since, TestResult.stage == "stage2")
            .group_by(func.date(TestResult.created_at))
        )
        s2_by_day = {str(row.d): row.c for row in s2_q}

    result = []
    for i in range(days):
        d = (since + timedelta(days=i + 1)).date()
        ds = str(d)
        result.append({
            "date": ds,
            "users": users_by_day.get(ds, 0),
            "stage1": s1_by_day.get(ds, 0),
            "stage2": s2_by_day.get(ds, 0),
        })

    return {"days": result}


@router.get("/top-careers")
async def top_careers(limit: int = 15, init_data: str = Query(...)):
    """Eng ko'p tavsiya etilgan career'lar."""
    _require_admin(init_data)

    async with SessionLocal() as s:
        rows = await s.execute(
            select(TestResult.roadmap).where(TestResult.stage == "stage2").limit(5000)
        )

    counter = {}
    for (roadmap,) in rows:
        if not roadmap or "careers" not in roadmap:
            continue
        for i, c in enumerate(roadmap["careers"]):
            cid = c.get("career", {}).get("id")
            if not cid:
                continue
            if cid not in counter:
                counter[cid] = {"count": 0, "top1": 0, "sum_fit": 0.0, "uz": c["career"].get("uz")}
            counter[cid]["count"] += 1
            if i == 0:
                counter[cid]["top1"] += 1
            counter[cid]["sum_fit"] += c.get("fit", 0)

    result = []
    for cid, data in counter.items():
        result.append({
            "career_id": cid,
            "career_uz": data["uz"],
            "appearances": data["count"],
            "top1_count": data["top1"],
            "avg_fit": round(data["sum_fit"] / data["count"], 1),
        })
    result.sort(key=lambda x: -x["appearances"])
    return {"careers": result[:limit]}


# ═══════════════════════════════════════════════════════════════
# FEEDBACK — foydalanuvchi fikri
# ═══════════════════════════════════════════════════════════════

class FeedbackPayload(BaseModel):
    init_data: str
    report_id: int
    rating: int  # 1-5
    comment: str = ""


@router.post("/feedback")
async def submit_feedback(payload: FeedbackPayload):
    """Foydalanuvchi fikri."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(400, "Rating 1-5 oraligida bolishi kerak")

    async with SessionLocal() as s:
        fb = Feedback(
            user_id=user["id"],
            report_id=payload.report_id,
            rating=payload.rating,
            comment=payload.comment[:1000],
        )
        s.add(fb)
        await s.commit()

    return {"ok": True}


@router.get("/feedbacks")
async def get_feedbacks(limit: int = 50, init_data: str = Query(...)):
    """Admin uchun barcha feedback'lar."""
    _require_admin(init_data)

    async with SessionLocal() as s:
        rows = await s.execute(
            select(Feedback).order_by(desc(Feedback.created_at)).limit(limit)
        )
        items = rows.scalars().all()

    return {
        "feedbacks": [
            {
                "id": f.id,
                "user_id": f.user_id,
                "report_id": f.report_id,
                "rating": f.rating,
                "comment": f.comment,
                "created_at": f.created_at.isoformat() if f.created_at else "",
            }
            for f in items
        ]
    }
