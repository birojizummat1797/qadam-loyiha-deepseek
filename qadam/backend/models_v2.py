"""
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


# ═══════════════════════════════════════════════════════════
# DISCOVERY — Free bosqich (12-13 savol)
# ═══════════════════════════════════════════════════════════
class DiscoverySession(Base):
    """Free Discovery session."""
    __tablename__ = "discovery_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    status: Mapped[str] = mapped_column(String(16), default="active")
    # active | completed | abandoned
    current_q_index: Mapped[int] = mapped_column(Integer, default=0)
    answers_count: Mapped[int] = mapped_column(Integer, default=0)
    question_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    signal_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    started_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped["DateTime | None"] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DiscoveryAnswer(Base):
    """Har savol javobi."""
    __tablename__ = "discovery_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    answer_id: Mapped[str] = mapped_column(String(64))
    answer_value: Mapped[int] = mapped_column(Integer)  # 1-5 likert yoki binary
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "question_id", name="uq_session_question"),
    )


class DiscoverySignal(Base):
    """Discovery sessiyasidan olingan signallar (evidence state)."""
    __tablename__ = "discovery_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)  # [0, 10] | None
    trust: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_state: Mapped[str] = mapped_column(String(24), default="unmeasured")
    coverage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "signal_key", name="uq_session_signal_disc"),
    )


# ═══════════════════════════════════════════════════════════
# SIGNAL EVIDENCE — har signal qaysi javobdan kelganini saqlash
# ═══════════════════════════════════════════════════════════
class SignalEvidence(Base):
    """
    Har bir signal uchun "dalil" yozuvi.
    Qaysi question/answer'dan qancha contribution kelganini saqlaydi.
    """
    __tablename__ = "signal_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    session_type: Mapped[str] = mapped_column(String(16))  # discovery | deep
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    question_id: Mapped[str] = mapped_column(String(64))
    answer_id: Mapped[str] = mapped_column(String(64))
    contribution: Mapped[float] = mapped_column(Float)
    evidence_type: Mapped[str] = mapped_column(String(24))  # direct | indirect
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ═══════════════════════════════════════════════════════════
# TAXONOMY — versioned, DB-driven
# ═══════════════════════════════════════════════════════════
class TaxonomyVersion(Base):
    __tablename__ = "taxonomy_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    published_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Career(Base):
    """DB-driven career taxonomy."""
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    taxonomy_version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("taxonomy_versions.id"), index=True
    )
    slug: Mapped[str] = mapped_column(String(64), index=True)
    title_uz: Mapped[str] = mapped_column(String(128))
    cluster: Mapped[str] = mapped_column(String(64), index=True)
    cluster_uz: Mapped[str] = mapped_column(String(128))
    pathway_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    learning_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    required_signals: Mapped[dict] = mapped_column(JSON)   # {signal: weight}
    prerequisites: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    salary_usd: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    roadmap_template_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("taxonomy_version_id", "slug", name="uq_tax_slug"),
    )
