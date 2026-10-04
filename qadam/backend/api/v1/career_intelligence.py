"""Career Intelligence API v1 — Premium (39,000 UZS)."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select, desc
from backend.db import SessionLocal
from backend.models_v2 import (
    DiscoverySession, DiscoverySignal, Entitlement,
)
from backend.auth import verify_init_data
from backend.services.entitlement_service import has_active_entitlement
from backend.services.taxonomy_service import load_taxonomy_from_db
from backend.engine.ranking import rank_careers
from backend.services.context_service import discovery_constraints
from backend.engine.public_output import strip_unsupported

router = APIRouter(prefix="/api/v1/career-intelligence", tags=["career-intelligence-v1"])


PREMIUM_KEY = "premium_career_intelligence"


async def _require_premium(user_id: int):
    from backend.services.age_gate import require_adult
    await require_adult(user_id)
    from backend.services.entitlement_service import DEEP_DIAGNOSTIC_FREE_BETA
    if DEEP_DIAGNOSTIC_FREE_BETA:
        return
    ok = await has_active_entitlement(user_id, PREMIUM_KEY)
    if not ok:
        raise HTTPException(
            402,
            "Premium Career Intelligence kerak. Iltimos, 39,000 UZS to'lovni amalga oshiring.",
        )


def _signals_from_db(rows) -> dict:
    """DiscoverySignal rows → signals dict."""
    out = {}
    for r in rows:
        out[r.signal_key] = {
            "value": r.value,
            "trust": r.trust,
            "evidence_state": r.evidence_state,
            "coverage": r.coverage,
        }
    return out


@router.get("")
async def get_career_intelligence(
    discovery_session_id: int = Query(...),
    init_data: str = Query(...),
):
    """
    Premium Career Intelligence natijasi.
    Fit + Readiness + Ranking + Explainability.
    """
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    await _require_premium(user["id"])

    # Discovery session'ni tekshirish
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, discovery_session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")
        if sess.status != "completed":
            raise HTTPException(400, "Session yakunlanmagan")

        signal_rows = (await s.execute(
            select(DiscoverySignal).where(
                DiscoverySignal.session_id == discovery_session_id
            )
        )).scalars().all()

    signals = _signals_from_db(signal_rows)

    # DB taxonomy
    taxonomy = await load_taxonomy_from_db()

    # Foydalanuvchining haqiqiy sharoiti (default yo'q; noma'lum bo'lsa readiness = None)
    constraints = await discovery_constraints(discovery_session_id)

    # Ranking
    ranking = rank_careers(
        signals=signals,
        taxonomy=taxonomy,
        constraints=constraints,
        top_n=5,
    )

    return {
        "discovery_session_id": discovery_session_id,
        "taxonomy_version": taxonomy.get("version", "v1.0"),
        "signals": signals,
        "constraints": constraints,
        "ranked": ranking["ranked"],
        "excluded": ranking["excluded"][:10],
        "confidence": ranking["confidence"],
    }


@router.get("/{career_slug}")
async def get_career_detail(
    career_slug: str,
    discovery_session_id: int = Query(...),
    init_data: str = Query(...),
):
    """Bitta career uchun batafsil ma'lumot."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    await _require_premium(user["id"])

    taxonomy = await load_taxonomy_from_db()

    # Career topish
    found = None
    for cluster_key, cluster in taxonomy["clusters"].items():
        if career_slug in cluster["careers"]:
            found = {
                "slug": career_slug,
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                **cluster["careers"][career_slug],
            }
            break

    if not found:
        raise HTTPException(404, "Career topilmadi")

    return strip_unsupported(found)
