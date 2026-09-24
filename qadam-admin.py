# -*- coding: utf-8 -*-
"""Qadam.io — Admin panel + Feedback tizimi."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — admin.py endpoint
# ═══════════════════════════════════════════════════════════
ADMIN = Path("qadam/backend/api/admin.py")

ADMIN.write_text(r'''"""Admin panel API — statistika + feedback."""
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
''', encoding="utf-8")
print("[OK] backend/api/admin.py")

# ═══════════════════════════════════════════════════════════
# 2. MODELS — Feedback modeli qo'shish
# ═══════════════════════════════════════════════════════════
MODELS = Path("qadam/backend/models.py")
models = MODELS.read_text(encoding="utf-8")

if "class Feedback" not in models:
    models += '''

class Feedback(Base):
    """Foydalanuvchi fikri (har report'dan keyin)."""
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    report_id: Mapped[int] = mapped_column(Integer, index=True)
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
'''
    MODELS.write_text(models, encoding="utf-8")
    print("[OK] models.py — Feedback qoshildi")
else:
    print("[SKIP] models.py — Feedback allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 3. MAIN.py — admin router qo'shish
# ═══════════════════════════════════════════════════════════
MAIN = Path("qadam/backend/main.py")
main = MAIN.read_text(encoding="utf-8")

if "admin" not in main:
    main = main.replace(
        'from backend.api.payments import router as payments_router',
        'from backend.api.payments import router as payments_router\nfrom backend.api.admin import router as admin_router',
    )
    main = main.replace(
        "app.include_router(payments_router)",
        "app.include_router(payments_router)\napp.include_router(admin_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — admin router ulandi")
else:
    print("[SKIP] main.py — admin allaqachon ulangan")

# ═══════════════════════════════════════════════════════════
# 4. api.ts — frontend funksiyalari
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

if "submitFeedback" not in api:
    api += '''

export async function submitFeedback(
  report_id: number,
  rating: number,
  comment: string = ""
) {
  const r = await api.post("/admin/feedback", {
    init_data: getInitData(),
    report_id,
    rating,
    comment,
  });
  return r.data;
}

export async function getAdminOverview() {
  const r = await api.get("/admin/overview", {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function getAdminDaily(days: number = 30) {
  const r = await api.get("/admin/daily", {
    params: { init_data: getInitData(), days },
  });
  return r.data;
}

export async function getAdminTopCareers(limit: number = 15) {
  const r = await api.get("/admin/top-careers", {
    params: { init_data: getInitData(), limit },
  });
  return r.data;
}

export async function getAdminFeedbacks(limit: number = 50) {
  const r = await api.get("/admin/feedbacks", {
    params: { init_data: getInitData(), limit },
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] api.ts — admin funksiyalari")
else:
    print("[SKIP] api.ts — allaqachon bor")

print()
print("=" * 60)
print("Admin panel backend — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  1. git add -A")
print('  2. git commit -m "Admin panel + feedback API"')
print("  3. git push")
print("  4. Render Manual Deploy")
print()
print("Keyin frontend'da admin panel va feedback UI qo'shamiz.")