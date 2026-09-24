"""
QADAM Database Models — FTT § 25.

Master principle:
- Missing signal != zero (evidence_state tracked separately)
- Fit != Readiness
- NO_MATCH is a valid result

Legacy tables (User, TestResult, Payment) — V1 API uchun saqlanadi.
New FTT tables qo'shilgan.
"""
from sqlalchemy import (
    BigInteger, String, JSON, DateTime, Boolean,
    Integer, Float, func, UniqueConstraint, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base


# ═══════════════════════════════════════════════════════════════════
# LEGACY (existing API uses these — do not remove)
# ═══════════════════════════════════════════════════════════════════

class User(Base):
    """User — id == telegram_id (legacy). FTT fields added on top."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram_id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(8), nullable=True)

    # ─── FTT § 7: demographic context ───
    gender: Mapped[str | None] = mapped_column(String(16), nullable=True)
    age_range: Mapped[str | None] = mapped_column(String(16), nullable=True)
    current_status: Mapped[str | None] = mapped_column(String(32), nullable=True)

    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TestResult(Base):
    """Legacy V1 — Stage1/Stage2 test natijalari."""
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    stage: Mapped[str] = mapped_column(String(16))  # stage1 | stage2
    answers: Mapped[dict] = mapped_column(JSON)
    profile: Mapped[dict] = mapped_column(JSON)
    roadmap: Mapped[dict] = mapped_column(JSON)
    ai_explanation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    versions: Mapped[dict] = mapped_column(JSON)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Payment(Base):
    """Legacy — Click + Stars to'lov yozuvlari."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    stage1_result_id: Mapped[int] = mapped_column(BigInteger, index=True)
    provider: Mapped[str] = mapped_column(String(32))
    amount_uzs: Mapped[int] = mapped_column(BigInteger)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


# ═══════════════════════════════════════════════════════════════════
# FTT § 25 — NEW TABLES
# ═══════════════════════════════════════════════════════════════════

class DiagnosticSession(Base):
    """
    FTT § 13: diagnostic state machine.
    States: created | started | in_progress | paused | completed | blocked | expired | no_match
    """
    __tablename__ = "diagnostic_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)  # telegram_id
    session_type: Mapped[str] = mapped_column(String(16))  # free | premium
    status: Mapped[str] = mapped_column(String(16), default="created")

    diagnostic_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    taxonomy_version: Mapped[str] = mapped_column(String(16), default="v1.0")
    scoring_version: Mapped[str] = mapped_column(String(16), default="v1.0")

    current_question_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(32), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    started_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticAnswer(Base):
    """
    FTT § 12: answers — frontend only sends raw answer.
    Backend decides next question.
    """
    __tablename__ = "diagnostic_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    question_id: Mapped[str] = mapped_column(String(64), index=True)
    # raw_value: {"value": "...", "option_id": "...", "text": "..."}
    raw_value: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticSignal(Base):
    """
    FTT § 16: missing != zero.
    evidence_state: measured | unmeasured | insufficient | conflicting
    value is NULL if unmeasured.
    """
    __tablename__ = "diagnostic_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, index=True)
    signal_key: Mapped[str] = mapped_column(String(64), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_state: Mapped[str] = mapped_column(String(16), default="unmeasured")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    coverage: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("session_id", "signal_key", name="uq_session_signal"),
    )


class CareerTaxonomy(Base):
    """
    FTT § 17-18: career universe — versioned, read-only for AI.
    """
    __tablename__ = "career_taxonomy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    title_uz: Mapped[str] = mapped_column(String(128))
    cluster: Mapped[str] = mapped_column(String(64), index=True)
    cluster_uz: Mapped[str] = mapped_column(String(128))

    required_signals: Mapped[dict] = mapped_column(JSON)
    scoring_weights: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    constraints: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    roadmap_template_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    pathway_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    learning_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class DiagnosticCooldown(Base):
    """
    FTT § 20: 2x NO_MATCH → 24h cooldown.
    Server-side only; client timer not trusted.
    """
    __tablename__ = "diagnostic_cooldowns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    reason: Mapped[str] = mapped_column(String(32), default="no_match")
    no_match_count: Mapped[int] = mapped_column(Integer, default=0)
    blocked_until: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Event(Base):
    """FTT § 30: analytics events."""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    session_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    event_name: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


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
