# -*- coding: utf-8 -*-
"""Batch 4 — Career Intelligence: Fit + Readiness + Ranking DB bilan."""
from pathlib import Path

BACKEND = Path("qadam/backend")

# ═══════════════════════════════════════════════════════════
# 1. engine/ranking.py — DB taxonomy (dict) qabul qilish
# ═══════════════════════════════════════════════════════════
RANKING = BACKEND / "engine/ranking.py"
r = RANKING.read_text(encoding="utf-8")

# KB_CAREERS endi dinamik (chunki DB taxonomy beriladi)
r = r.replace(
    '''def _load_roadmap_careers():
    careers = set()
    for name in [
        "roadmap_kb_v3.json", "roadmap_kb_v2.json",
        "roadmap_kb_v2_part_a.json", "roadmap_kb_v2_part_b.json",
    ]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass
    return careers


KB_CAREERS = _load_roadmap_careers()''',
    '''def _load_roadmap_careers():
    careers = set()
    for name in [
        "roadmap_kb_v3.json", "roadmap_kb_v2.json",
        "roadmap_kb_v2_part_a.json", "roadmap_kb_v2_part_b.json",
        "roadmap_kb_v1.json",
    ]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass
    return careers


KB_CAREERS = _load_roadmap_careers()''',
)

RANKING.write_text(r, encoding="utf-8")
print("[OK] engine/ranking.py — KB_CAREERS yangilandi")

# ═══════════════════════════════════════════════════════════
# 2. api/v1/career_intelligence.py
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1/career_intelligence.py").write_text(r'''"""Career Intelligence API v1 — Premium (39,000 UZS)."""
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

router = APIRouter(prefix="/api/v1/career-intelligence", tags=["career-intelligence-v1"])


PREMIUM_KEY = "premium_career_intelligence"


async def _require_premium(user_id: int):
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

    # Constraints sessiya meta'sidan
    constraints = (sess.meta or {}).get("constraints") or {
        "time": "2_3h", "device": "laptop", "english": "b1",
    }

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

    return found


@router.get("/compare")
async def compare_careers(
    slugs: str = Query(..., description="vergul bilan ajratilgan slug'lar"),
    discovery_session_id: int = Query(...),
    init_data: str = Query(...),
):
    """2-3 ta career taqqoslash."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    await _require_premium(user["id"])

    slug_list = [x.strip() for x in slugs.split(",") if x.strip()][:3]
    if len(slug_list) < 2:
        raise HTTPException(400, "Kamida 2 ta career kerak")

    taxonomy = await load_taxonomy_from_db()
    from backend.engine.fit import calculate_fit
    from backend.engine.readiness import calculate_readiness

    async with SessionLocal() as s:
        signal_rows = (await s.execute(
            select(DiscoverySignal).where(
                DiscoverySignal.session_id == discovery_session_id
            )
        )).scalars().all()
    signals = _signals_from_db(signal_rows)

    out = []
    for slug in slug_list:
        for cluster_key, cluster in taxonomy["clusters"].items():
            if slug in cluster["careers"]:
                c = cluster["careers"][slug]
                fit = calculate_fit(signals, c)
                readiness = calculate_readiness(
                    {"device": "laptop", "english": "b1", "time": "2_3h"},
                    c.get("prerequisites", {}),
                )
                out.append({
                    "slug": slug,
                    "title_uz": c["uz"],
                    "cluster_uz": cluster["uz"],
                    "fit": fit["fit"],
                    "coverage": fit["coverage"],
                    "confidence": fit["confidence"],
                    "readiness": readiness["readiness"],
                    "barriers_count": len(readiness["barriers"]),
                })
                break

    return {"careers": out}
''', encoding="utf-8")
print("[OK] api/v1/career_intelligence.py")

# ═══════════════════════════════════════════════════════════
# 3. Discovery complete — constraints sessiya.meta'ga saqlash
# ═══════════════════════════════════════════════════════════
DISC = BACKEND / "api/v1/discovery.py"
disc = DISC.read_text(encoding="utf-8")

# constraints saqlash
disc = disc.replace(
    '''    # Saqlash
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        sess.status = "completed"
        sess.completed_at = datetime.now(timezone.utc)
        sess.meta = {"confidence": insight.get("confidence")}''',
    '''    # Constraints
    from backend.services.discovery_service import _extract_constraints
    constraints = _extract_constraints(answers_list)

    # Saqlash
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, session_id)
        sess.status = "completed"
        sess.completed_at = datetime.now(timezone.utc)
        sess.meta = {
            "confidence": insight.get("confidence"),
            "constraints": constraints,
        }''',
)

DISC.write_text(disc, encoding="utf-8")
print("[OK] discovery.py — constraints saqlash")

# ═══════════════════════════════════════════════════════════
# 4. main.py — career_intelligence router
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "v1_career_intel_router" not in main:
    main = main.replace(
        "from backend.api.v1.taxonomy import router as v1_taxonomy_router",
        "from backend.api.v1.taxonomy import router as v1_taxonomy_router\n"
        "from backend.api.v1.career_intelligence import router as v1_career_intel_router",
    )
    main = main.replace(
        "app.include_router(v1_taxonomy_router)",
        "app.include_router(v1_taxonomy_router)\n"
        "app.include_router(v1_career_intel_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — career_intelligence router")

# ═══════════════════════════════════════════════════════════
# 5. Tests
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch4_career_intel.py").write_text(r'''"""Batch 4 — Career Intelligence testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.ranking import rank_careers
from engine.fit import calculate_fit
from engine.readiness import calculate_readiness
from data_loader import load_taxonomy


def _fake_signals_top():
    """5 ta measured signal."""
    return {
        "logical_thinking": {"value": 8.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": 7.5, "trust": 1.0, "evidence_state": "measured"},
        "persistence": {"value": 8.5, "trust": 1.0, "evidence_state": "measured"},
        "technical_interest": {"value": 9.0, "trust": 1.0, "evidence_state": "measured"},
        "analytical": {"value": 7.0, "trust": 1.0, "evidence_state": "measured"},
    }


def test_ranking_returns_top5():
    taxonomy = load_taxonomy()
    r = rank_careers(
        signals=_fake_signals_top(),
        taxonomy=taxonomy,
        constraints={"device": "laptop", "english": "b1", "time": "2_3h"},
        top_n=5,
    )
    assert len(r["ranked"]) <= 5
    # Confidence
    assert r["confidence"] in ("high", "medium", "low")


def test_ranking_excludes_low_coverage():
    """Faqat 1 signal measured → coverage < 0.5 → excluded."""
    signals = {
        "logical_thinking": {"value": 9.0, "trust": 1.0, "evidence_state": "measured"},
    }
    taxonomy = load_taxonomy()
    r = rank_careers(signals, taxonomy, {"device": "laptop", "english": "b1", "time": "2_3h"})
    # backend_dev kabi 5+ signal talab qiladigan career'lar chiqmasligi kerak
    for c in r["ranked"]:
        assert c["coverage"] >= 0.5


def test_fit_and_readiness_separate():
    """Fit yuqori, Readiness past — bo'lishi mumkin."""
    signals = _fake_signals_top()
    taxonomy = load_taxonomy()
    # Backend dev
    career = taxonomy["clusters"]["software"]["careers"]["backend_development"]
    fit = calculate_fit(signals, career)
    readiness = calculate_readiness(
        {"device": "smartphone_only", "english": "none", "time": "lt_1h"},
        career.get("prerequisites", {}),
    )
    assert fit["fit"] is not None
    assert readiness["readiness"] < 100
    # Ikkalasi alohida
    assert "readiness" not in fit
    assert "fit" not in readiness


def test_readiness_p_computer_penalty():
    """Device yo'q → 0.5 penalty."""
    signals = _fake_signals_top()
    taxonomy = load_taxonomy()
    career = taxonomy["clusters"]["software"]["careers"]["frontend_development"]

    r_no_device = calculate_readiness(
        {"device": "none", "english": "b1", "time": "2_3h"},
        career["prerequisites"],
    )
    r_laptop = calculate_readiness(
        {"device": "laptop", "english": "b1", "time": "2_3h"},
        career["prerequisites"],
    )
    assert r_no_device["p_computer"] == 0.5
    assert r_laptop["p_computer"] == 1.0
    assert r_no_device["readiness"] < r_laptop["readiness"]


def test_ranking_composite_score():
    """Composite = Fit × (0.7 + 0.3 × Readiness/100)."""
    taxonomy = load_taxonomy()
    r = rank_careers(_fake_signals_top(), taxonomy,
                     {"device": "laptop", "english": "b1", "time": "2_3h"})
    if len(r["ranked"]) >= 2:
        assert r["ranked"][0]["composite_score"] >= r["ranked"][1]["composite_score"]


def test_ranking_confidence_labels():
    taxonomy = load_taxonomy()
    r = rank_careers(_fake_signals_top(), taxonomy,
                     {"device": "laptop", "english": "b1", "time": "2_3h"})
    assert r["confidence"] in ("high", "medium", "low", "none")
''', encoding="utf-8")
print("[OK] tests/test_batch4_career_intel.py (6 test)")

print()
print("=" * 60)
print("Batch 4 (Career Intelligence) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • /api/v1/career-intelligence (premium, Fit+Readiness+Ranking)")
print("  • /api/v1/career-intelligence/{slug}")
print("  • /api/v1/career-intelligence/compare?slugs=a,b")
print("  • Constraints sessiya.meta'da saqlanadi")
print("  • 6 test")
print()
print("KEYINGI:")
print("  1. cd qadam")
print("  2. ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch4_career_intel.py -v")
print("  3. cd ..")
print("  4. git add -A")
print('  5. git commit -m "Batch 4: Career Intelligence (Fit+Readiness+Ranking)"')
print("  6. git push")
print("  7. Render Manual Deploy")