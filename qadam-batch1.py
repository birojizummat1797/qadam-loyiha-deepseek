# -*- coding: utf-8 -*-
"""Batch 1 — Foundation: Profiles, Products, Entitlements."""
from pathlib import Path

FRONTEND = Path("qadam-miniapp")
BACKEND = Path("qadam/backend")

# ═══════════════════════════════════════════════════════════
# 1. models_v2.py — yangi jadvallar (eski buzilmaydi)
# ═══════════════════════════════════════════════════════════
(BACKEND / "models_v2.py").write_text(r'''"""
Batch 1 models — Profiles, Products, Entitlements, PaymentEvents.
Mavjud models.py buzilmaydi — yangi jadvallar qo'shiladi.
"""
from sqlalchemy import (
    BigInteger, String, JSON, DateTime, Boolean, Integer, Float,
    func, ForeignKey, Numeric, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base


# ═══════════════════════════════════════════════════════════
# PROFILE — foydalanuvchi haqida ma'lumot
# ═══════════════════════════════════════════════════════════
class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    education: Mapped[str | None] = mapped_column(String(64), nullable=True)
    work_context: Mapped[str | None] = mapped_column(String(128), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ═══════════════════════════════════════════════════════════
# PRODUCTS & PLANS — configurable
# ═══════════════════════════════════════════════════════════
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name_uz: Mapped[str] = mapped_column(String(128))
    product_type: Mapped[str] = mapped_column(String(32))  # one_time | subscription
    description_uz: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ProductPlan(Base):
    __tablename__ = "product_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), index=True)
    plan_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    price_uzs: Mapped[int] = mapped_column(BigInteger)
    price_stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    billing_period: Mapped[str] = mapped_column(String(16), default="one_time")  # one_time | monthly | yearly
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ═══════════════════════════════════════════════════════════
# ENTITLEMENTS — mustaqil (bir martalik + subscription)
# ═══════════════════════════════════════════════════════════
class Entitlement(Base):
    """
    status: pending | active | expired | cancelled | refunded | revoked
    source: stars | manual_card | click | payme | admin | grant
    """
    __tablename__ = "entitlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    entitlement_key: Mapped[str] = mapped_column(String(64), index=True)
    # premium_career_intelligence | ai_career_assistant | human_curator_support

    source: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="pending")

    activated_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    refunded_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)

    payment_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    plan_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    version: Mapped[str] = mapped_column(String(16), default="v1.0")

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_ent_user_key_status", "user_id", "entitlement_key", "status"),
    )


# ═══════════════════════════════════════════════════════════
# PAYMENT EVENTS — idempotency uchun
# ═══════════════════════════════════════════════════════════
class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(32))
    event_type: Mapped[str] = mapped_column(String(64))   # created | paid | failed | refunded
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processed_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
''', encoding="utf-8")
print("[OK] backend/models_v2.py")

# ═══════════════════════════════════════════════════════════
# 2. db.py — v2 modellarni import qilish
# ═══════════════════════════════════════════════════════════
DB = BACKEND / "db.py"
db = DB.read_text(encoding="utf-8")

if "models_v2" not in db:
    db = db.replace(
        "    from backend import models  # noqa",
        "    from backend import models  # noqa\n    from backend import models_v2  # noqa",
    )
    DB.write_text(db, encoding="utf-8")
    print("[OK] db.py — models_v2 import")

# ═══════════════════════════════════════════════════════════
# 3. products_v1.json — konfiguratsiya
# ═══════════════════════════════════════════════════════════
(BACKEND / "data/products_v1.json").write_text(r'''{
  "version": "v1.0",
  "products": [
    {
      "slug": "premium_career_intelligence",
      "name_uz": "Premium Career Intelligence",
      "product_type": "one_time",
      "description_uz": "Chuqur diagnostika, Career Intelligence va shaxsiy yo'l xaritasi",
      "plans": [
        {
          "plan_code": "pci_39000_uzs",
          "price_uzs": 39000,
          "price_stars": 150,
          "billing_period": "one_time",
          "is_active": true
        }
      ]
    },
    {
      "slug": "ai_career_assistant",
      "name_uz": "AI Career Assistant",
      "product_type": "subscription",
      "description_uz": "Doimiy AI yordamchi",
      "plans": [
        {
          "plan_code": "aica_49000_uzs_monthly",
          "price_uzs": 49000,
          "price_stars": null,
          "billing_period": "monthly",
          "is_active": false
        }
      ]
    }
  ]
}
''', encoding="utf-8")
print("[OK] backend/data/products_v1.json")

# ═══════════════════════════════════════════════════════════
# 4. entitlement_service.py
# ═══════════════════════════════════════════════════════════
(BACKEND / "services").mkdir(exist_ok=True)
(BACKEND / "services/__init__.py").write_text("", encoding="utf-8")

(BACKEND / "services/entitlement_service.py").write_text(r'''"""Entitlement Service — grant, check, revoke."""
from datetime import datetime, timezone
from sqlalchemy import select
from backend.db import SessionLocal
from backend.models_v2 import Entitlement, PaymentEvent


PREMIUM_KEY = "premium_career_intelligence"


async def get_active_entitlement(user_id: int, entitlement_key: str):
    """Aktiv entitlement qaytaradi (yoki None)."""
    async with SessionLocal() as s:
        q = (
            select(Entitlement)
            .where(
                Entitlement.user_id == user_id,
                Entitlement.entitlement_key == entitlement_key,
                Entitlement.status == "active",
            )
            .order_by(Entitlement.activated_at.desc())
            .limit(1)
        )
        r = (await s.execute(q)).scalar_one_or_none()
        return r


async def has_active_entitlement(user_id: int, entitlement_key: str) -> bool:
    e = await get_active_entitlement(user_id, entitlement_key)
    if not e:
        return False
    # Muddati tekshirish
    if e.expires_at and e.expires_at < datetime.now(timezone.utc):
        return False
    return True


async def grant_entitlement(
    user_id: int,
    entitlement_key: str,
    source: str,
    payment_reference: str | None = None,
    plan_code: str | None = None,
    expires_at=None,
    meta: dict | None = None,
):
    """Yangi aktiv entitlement yaratadi."""
    async with SessionLocal() as s:
        e = Entitlement(
            user_id=user_id,
            entitlement_key=entitlement_key,
            source=source,
            status="active",
            activated_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            payment_reference=payment_reference,
            plan_code=plan_code,
            meta=meta or {},
        )
        s.add(e)
        await s.commit()
        await s.refresh(e)
        return e


async def revoke_entitlement(entitlement_id: int):
    async with SessionLocal() as s:
        e = await s.get(Entitlement, entitlement_id)
        if e:
            e.status = "revoked"
            e.cancelled_at = datetime.now(timezone.utc)
            await s.commit()


async def record_payment_event(
    provider: str,
    event_type: str,
    idempotency_key: str,
    payment_id: int | None = None,
    payload: dict | None = None,
) -> bool:
    """
    Idempotency: agar key mavjud bo'lsa — False qaytaradi (takroriy).
    Yangi bo'lsa — yozadi, True qaytaradi.
    """
    async with SessionLocal() as s:
        existing = (await s.execute(
            select(PaymentEvent).where(PaymentEvent.idempotency_key == idempotency_key)
        )).scalar_one_or_none()
        if existing:
            return False

        ev = PaymentEvent(
            payment_id=payment_id,
            provider=provider,
            event_type=event_type,
            idempotency_key=idempotency_key,
            payload=payload or {},
        )
        s.add(ev)
        await s.commit()
        return True
''', encoding="utf-8")
print("[OK] backend/services/entitlement_service.py")

# ═══════════════════════════════════════════════════════════
# 5. api/v1 — Profile + Entitlements
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1").mkdir(exist_ok=True)
(BACKEND / "api/v1/__init__.py").write_text("", encoding="utf-8")

(BACKEND / "api/v1/profile.py").write_text(r'''"""Profile API v1."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.db import SessionLocal
from backend.models_v2 import Profile
from backend.auth import verify_init_data

router = APIRouter(prefix="/api/v1/profile", tags=["profile-v1"])


class ProfilePayload(BaseModel):
    init_data: str
    age: int | None = None
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

    # Validatsiya
    if payload.age is not None and not (10 <= payload.age <= 80):
        raise HTTPException(400, "age 10-80 orasida bo'lishi kerak")

    async with SessionLocal() as s:
        p = await s.get(Profile, user["id"])
        if not p:
            p = Profile(user_id=user["id"])
            s.add(p)

        if payload.age is not None:
            p.age = payload.age
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
''', encoding="utf-8")
print("[OK] backend/api/v1/profile.py")

(BACKEND / "api/v1/entitlements.py").write_text(r'''"""Entitlements API v1."""
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
''', encoding="utf-8")
print("[OK] backend/api/v1/entitlements.py")

# ═══════════════════════════════════════════════════════════
# 6. main.py — v1 routers ulash
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "api.v1.profile" not in main:
    main = main.replace(
        "from backend.api.admin import router as admin_router",
        "from backend.api.admin import router as admin_router\n"
        "from backend.api.v1.profile import router as v1_profile_router\n"
        "from backend.api.v1.entitlements import router as v1_entitlements_router",
    )
    main = main.replace(
        "app.include_router(admin_router)",
        "app.include_router(admin_router)\n"
        "app.include_router(v1_profile_router)\n"
        "app.include_router(v1_entitlements_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — v1 routers")

# ═══════════════════════════════════════════════════════════
# 7. Test
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch1_models.py").write_text(r'''"""Batch 1 — models + entitlement service testlari (DB'siz)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import Profile, Product, ProductPlan, Entitlement, PaymentEvent


def test_profile_columns():
    cols = {c.name for c in Profile.__table__.columns}
    assert "user_id" in cols
    assert "age" in cols
    assert "location" in cols
    assert "current_status" in cols
    assert "education" in cols
    assert "work_context" in cols


def test_product_columns():
    cols = {c.name for c in Product.__table__.columns}
    assert "slug" in cols
    assert "product_type" in cols
    assert "is_active" in cols


def test_product_plan_columns():
    cols = {c.name for c in ProductPlan.__table__.columns}
    assert "plan_code" in cols
    assert "price_uzs" in cols
    assert "price_stars" in cols
    assert "billing_period" in cols


def test_entitlement_columns():
    cols = {c.name for c in Entitlement.__table__.columns}
    for f in ("user_id", "entitlement_key", "source", "status",
              "activated_at", "expires_at", "cancelled_at", "refunded_at",
              "payment_reference", "plan_code"):
        assert f in cols, f"{f} yo'q"


def test_payment_event_idempotency_column():
    cols = {c.name for c in PaymentEvent.__table__.columns}
    assert "idempotency_key" in cols
    # Unique
    uk_cols = [
        c.name for idx in PaymentEvent.__table__.indexes
        for c in idx.columns if idx.unique
    ]
    assert "idempotency_key" in uk_cols


def test_products_json_config():
    import json
    p = Path(__file__).parent.parent / "backend/data/products_v1.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    slugs = [x["slug"] for x in data["products"]]
    assert "premium_career_intelligence" in slugs
    # Narx 39000
    pci = next(x for x in data["products"] if x["slug"] == "premium_career_intelligence")
    plan = pci["plans"][0]
    assert plan["price_uzs"] == 39000
    assert plan["price_stars"] == 150
''', encoding="utf-8")
print("[OK] tests/test_batch1_models.py")

print()
print("=" * 60)
print("Batch 1 (Foundation) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • profiles table")
print("  • products + product_plans")
print("  • entitlements (state machine)")
print("  • payment_events (idempotency)")
print("  • /api/v1/profile GET/POST")
print("  • /api/v1/entitlements/me")
print("  • /api/v1/entitlements/check")
print("  • products_v1.json config")
print("  • 6 ta model test")
print()
print("KEYINGI:")
print("  cd qadam")
print("  ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch1_models.py -v")
print("  cd ..")
print("  git add -A")
print('  git commit -m "Batch 1: Profiles + Products + Entitlements"')
print("  git push")
print("  Render Manual Deploy")