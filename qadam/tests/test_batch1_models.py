"""Batch 1 — models + entitlement service testlari (DB'siz)."""
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
