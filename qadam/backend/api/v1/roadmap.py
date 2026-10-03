"""Roadmap API v1 — premium."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models_v2 import (
    DeepDiagnosticSession, DeepDiagnosticSignal, DiscoverySignal,
)
from backend.auth import verify_init_data
from backend.services.entitlement_service import has_active_entitlement
from backend.services.taxonomy_service import load_taxonomy_from_db
from backend.engine.ranking import rank_careers
from backend.engine.roadmap_engine import build_roadmap
from backend.engine.public_output import strip_unsupported
from backend.services.context_service import discovery_constraints

router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap-v1"])

PREMIUM_KEY = "premium_career_intelligence"


def _signals_from_rows(rows) -> dict:
    return {
        r.signal_key: {
            "value": r.value, "trust": r.trust,
            "evidence_state": r.evidence_state, "coverage": r.coverage,
        }
        for r in rows
    }


@router.get("/{career_slug}")
async def get_roadmap(
    career_slug: str,
    session_id: int = Query(..., description="Deep diagnostic session id"),
    init_data: str = Query(...),
):
    """Bitta career uchun shaxsiy roadmap."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if not await has_active_entitlement(user["id"], PREMIUM_KEY):
        raise HTTPException(402, "Premium kerak")

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

        signal_rows = (await s.execute(
            select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == session_id)
        )).scalars().all()

        disc_rows = []
        if sess.discovery_session_id:
            disc_rows = (await s.execute(
                select(DiscoverySignal).where(DiscoverySignal.session_id == sess.discovery_session_id)
            )).scalars().all()

    signals = {**_signals_from_rows(disc_rows), **_signals_from_rows(signal_rows)}
    # Haqiqiy sharoit discovery javoblaridan (deep meta'da faqat moliya/shoshilinchlik bor)
    base = await discovery_constraints(sess.discovery_session_id)

    taxonomy = await load_taxonomy_from_db()

    # Career topish
    career_data = None
    cluster_key = None
    for ck, cluster in taxonomy["clusters"].items():
        if career_slug in cluster["careers"]:
            career_data = cluster["careers"][career_slug]
            cluster_key = ck
            break

    if not career_data:
        raise HTTPException(404, "Career topilmadi")

    # Ranking'dan bu career uchun Fit/Readiness
    ranking = rank_careers(signals, taxonomy, base, top_n=25)
    ranked_item = next(
        (r for r in ranking["ranked"] if r["career_id"] == career_slug),
        None,
    )
    if not ranked_item:
        # Top-25'da yo'q — qo'lda hisoblash
        from backend.engine.fit import calculate_fit
        from backend.engine.readiness import calculate_readiness
        from backend.engine.levels import context_status, evidence_level
        fit = calculate_fit(signals, career_data)
        readiness = calculate_readiness(base, career_data.get("prerequisites", {}))
        ranked_item = {
            "career_id": career_slug,
            "fit": fit["fit"],
            "coverage": fit["coverage"],
            "confidence": fit["confidence"],
            "readiness": readiness["readiness"],
            "barriers": readiness["barriers"],
            "has_hard_barrier": readiness["has_hard_barrier"],
            "evidence_level": evidence_level(fit["coverage"]),
            "context_status": context_status(readiness),
        }

    # Roadmap
    career_full = {**career_data, "cluster": cluster_key or ""}
    roadmap = build_roadmap(career_slug, career_full, ranked_item)

    return {
        "career_slug": career_slug,
        "fit": ranked_item.get("fit"),
        "coverage": ranked_item.get("coverage"),
        "confidence": ranked_item.get("confidence"),
        "readiness": ranked_item.get("readiness"),
        "has_hard_barrier": ranked_item.get("has_hard_barrier"),
        "evidence_level": ranked_item.get("evidence_level"),
        "context_status": ranked_item.get("context_status"),
        "roadmap": strip_unsupported(roadmap),
    }
