# -*- coding: utf-8 -*-
"""Batch 3 — Signal Evidence + Taxonomy DB-driven."""
from pathlib import Path

BACKEND = Path("qadam/backend")

# ═══════════════════════════════════════════════════════════
# 1. models_v2.py — Signal Evidence + Taxonomy jadvallari
# ═══════════════════════════════════════════════════════════
MODELS = BACKEND / "models_v2.py"
m = MODELS.read_text(encoding="utf-8")

if "SignalEvidence" not in m:
    m += '''

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
'''
    MODELS.write_text(m, encoding="utf-8")
    print("[OK] models_v2.py — SignalEvidence + Taxonomy")
else:
    print("[SKIP] models_v2.py — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 2. taxonomy_service.py — DB'dan o'qish
# ═══════════════════════════════════════════════════════════
(BACKEND / "services/taxonomy_service.py").write_text(r'''"""Taxonomy Service — DB-driven."""
import json
from pathlib import Path
from sqlalchemy import select
from backend.db import SessionLocal
from backend.models_v2 import TaxonomyVersion, Career


DATA_DIR = Path(__file__).parent.parent / "data"


async def get_active_taxonomy_version():
    async with SessionLocal() as s:
        q = (
            select(TaxonomyVersion)
            .where(TaxonomyVersion.is_active == True)
            .order_by(TaxonomyVersion.published_at.desc())
            .limit(1)
        )
        return (await s.execute(q)).scalar_one_or_none()


async def load_taxonomy_from_db() -> dict:
    """DB'dagi aktiv taxonomy'ni JSON shaklida qaytaradi (engine uchun)."""
    async with SessionLocal() as s:
        v = (await s.execute(
            select(TaxonomyVersion)
            .where(TaxonomyVersion.is_active == True)
            .order_by(TaxonomyVersion.published_at.desc())
            .limit(1)
        )).scalar_one_or_none()

        if not v:
            # Fallback: JSON fayldan
            return json.loads((DATA_DIR / "taxonomy_v1.json").read_text(encoding="utf-8"))

        rows = (await s.execute(
            select(Career).where(
                Career.taxonomy_version_id == v.id,
                Career.is_active == True,
            )
        )).scalars().all()

    clusters = {}
    for c in rows:
        if c.cluster not in clusters:
            clusters[c.cluster] = {"uz": c.cluster_uz, "careers": {}}
        clusters[c.cluster]["careers"][c.slug] = {
            "uz": c.title_uz,
            "signals": c.required_signals,
            "prerequisites": c.prerequisites or {},
            "learning_months": c.learning_months,
            "pathway_type": c.pathway_type,
            "salary_usd": c.salary_usd,
        }

    return {
        "version": v.version,
        "clusters": clusters,
    }


async def seed_taxonomy_from_json(version_str: str = "v1.0"):
    """
    taxonomy_v1.json'dan DB'ga seed qilish.
    Faqat bir marta — agar version mavjud bo'lsa, hech narsa qilmaydi.
    """
    async with SessionLocal() as s:
        existing = (await s.execute(
            select(TaxonomyVersion).where(TaxonomyVersion.version == version_str)
        )).scalar_one_or_none()
        if existing:
            return {"seeded": False, "reason": "already_exists", "version": version_str}

        v = TaxonomyVersion(version=version_str, notes="initial seed", is_active=True)
        s.add(v)
        await s.flush()

        data = json.loads((DATA_DIR / "taxonomy_v1.json").read_text(encoding="utf-8"))
        total = 0
        for cluster_key, cluster in data["clusters"].items():
            for slug, c in cluster["careers"].items():
                career = Career(
                    taxonomy_version_id=v.id,
                    slug=slug,
                    title_uz=c["uz"],
                    cluster=cluster_key,
                    cluster_uz=cluster["uz"],
                    pathway_type=c.get("pathway_type"),
                    learning_months=c.get("learning_months"),
                    required_signals=c.get("signals", {}),
                    prerequisites=c.get("prerequisites", {}),
                    salary_usd=c.get("salary_usd"),
                )
                s.add(career)
                total += 1

        await s.commit()
        return {"seeded": True, "version": version_str, "careers_count": total}
''', encoding="utf-8")
print("[OK] services/taxonomy_service.py")

# ═══════════════════════════════════════════════════════════
# 3. discovery_service.py — evidence yozish qo'shish
# ═══════════════════════════════════════════════════════════
DS = BACKEND / "services/discovery_service.py"
ds = DS.read_text(encoding="utf-8")

if "extract_evidence" not in ds:
    ds += '''

# ═══════════════════════════════════════════════════════════
# EVIDENCE EXTRACTION — har signal uchun alohida yozuv
# ═══════════════════════════════════════════════════════════
def extract_evidence(answers: list, questions: list) -> list:
    """
    Returns: [
        {"signal_key", "question_id", "answer_id", "contribution", "evidence_type"}
    ]
    """
    from engine.signals import LIKERT_TO_10

    qmap = {q["id"]: q for q in questions}
    out = []

    for a in answers:
        q = qmap.get(a["question_id"])
        if not q:
            continue

        # Likert
        if q.get("type") == "likert":
            v10 = LIKERT_TO_10.get(a["answer_value"], 5.0)
            for sig, w in q.get("signals", {}).items():
                out.append({
                    "signal_key": sig,
                    "question_id": a["question_id"],
                    "answer_id": a.get("answer_id", ""),
                    "contribution": round(v10 * w, 3),
                    "evidence_type": "direct",
                })
            continue

        # Choice
        opt = next((o for o in q.get("options", []) if o["id"] == a["answer_id"]), None)
        if not opt:
            continue
        v10 = LIKERT_TO_10.get(int(opt.get("value", 3)), 5.0)
        for sig, w in opt.get("signals", {}).items():
            out.append({
                "signal_key": sig,
                "question_id": a["question_id"],
                "answer_id": a["answer_id"],
                "contribution": round(v10 * w, 3),
                "evidence_type": "direct" if w >= 0.8 else "indirect",
            })

    return out
'''
    DS.write_text(ds, encoding="utf-8")
    print("[OK] discovery_service.py — extract_evidence")

# ═══════════════════════════════════════════════════════════
# 4. api/v1/discovery.py — complete'da evidence saqlash
# ═══════════════════════════════════════════════════════════
DISC = BACKEND / "api/v1/discovery.py"
disc = DISC.read_text(encoding="utf-8")

# Import
if "SignalEvidence" not in disc:
    disc = disc.replace(
        "from backend.models_v2 import (\n    DiscoverySession, DiscoveryAnswer, DiscoverySignal,\n)",
        "from backend.models_v2 import (\n    DiscoverySession, DiscoveryAnswer, DiscoverySignal, SignalEvidence,\n)",
    )

# complete_session ichida evidence saqlash
old_block = '''        # Signallarni saqlash
        for k, v in signals.items():
            sig = DiscoverySignal(
                session_id=session_id,
                signal_key=k,
                value=v["value"],
                trust=v["trust"],
                evidence_state=v["evidence_state"],
                coverage=v["coverage"],
            )
            s.add(sig)

        await s.commit()'''

new_block = '''        # Signallarni saqlash
        for k, v in signals.items():
            sig = DiscoverySignal(
                session_id=session_id,
                signal_key=k,
                value=v["value"],
                trust=v["trust"],
                evidence_state=v["evidence_state"],
                coverage=v["coverage"],
            )
            s.add(sig)

        # Evidence yozuvlarini saqlash
        from backend.services.discovery_service import extract_evidence
        evidences = extract_evidence(answers_list, questions)
        for ev in evidences:
            e = SignalEvidence(
                session_id=session_id,
                session_type="discovery",
                signal_key=ev["signal_key"],
                question_id=ev["question_id"],
                answer_id=ev["answer_id"],
                contribution=ev["contribution"],
                evidence_type=ev["evidence_type"],
            )
            s.add(e)

        await s.commit()'''

if old_block in disc:
    disc = disc.replace(old_block, new_block)
    print("[OK] discovery.py — evidence saqlash")

# rank_careers chaqiruvini DB taxonomy'ga o'tkazish
if "load_taxonomy_from_db" not in disc:
    disc = disc.replace(
        "from backend.services.discovery_service import (\n    get_next_question, compute_signals_from_discovery, build_preliminary_insight,\n)",
        "from backend.services.discovery_service import (\n    get_next_question, compute_signals_from_discovery, build_preliminary_insight,\n)\nfrom backend.services.taxonomy_service import load_taxonomy_from_db",
    )

DISC.write_text(disc, encoding="utf-8")
print("[OK] discovery.py — DB taxonomy import")

# ═══════════════════════════════════════════════════════════
# 5. discovery_service.py — DB taxonomy ishlatish
# ═══════════════════════════════════════════════════════════
ds = DS.read_text(encoding="utf-8")

# load_taxonomy chaqiruvini DB'ga almashtirish
ds = ds.replace(
    "    from engine.ranking import rank_careers\n    from data_loader import load_taxonomy",
    "    from engine.ranking import rank_careers\n    # taxonomy tashqaridan beriladi (async)",
)

# build_preliminary_insight signature'ni yangilash
ds = ds.replace(
    "def build_preliminary_insight(signals: dict, answers: list) -> dict:",
    "def build_preliminary_insight(signals: dict, answers: list, taxonomy: dict) -> dict:",
)
ds = ds.replace(
    "    constraints = _extract_constraints(answers)\n    taxonomy = load_taxonomy()",
    "    constraints = _extract_constraints(answers)",
)

DS.write_text(ds, encoding="utf-8")
print("[OK] discovery_service.py — taxonomy tashqaridan")

# discovery.py — complete endpoint'da taxonomy DB'dan olish
disc = DISC.read_text(encoding="utf-8")

disc = disc.replace(
    "    # Preliminary insight\n    insight = build_preliminary_insight(signals, answers_list)",
    "    # DB taxonomy\n    taxonomy = await load_taxonomy_from_db()\n\n    # Preliminary insight\n    insight = build_preliminary_insight(signals, answers_list, taxonomy)",
)

DISC.write_text(disc, encoding="utf-8")
print("[OK] discovery.py — DB taxonomy")

# ═══════════════════════════════════════════════════════════
# 6. api/v1/taxonomy.py — yangi endpoint
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1/taxonomy.py").write_text(r'''"""Taxonomy API v1 — DB-driven, public read."""
from fastapi import APIRouter, HTTPException
from backend.services.taxonomy_service import (
    load_taxonomy_from_db, get_active_taxonomy_version,
    seed_taxonomy_from_json,
)

router = APIRouter(prefix="/api/v1/taxonomy", tags=["taxonomy-v1"])


@router.get("")
async def get_taxonomy():
    """Aktiv taxonomy (JSON)."""
    data = await load_taxonomy_from_db()
    v = await get_active_taxonomy_version()
    return {
        "version": v.version if v else data.get("version"),
        "clusters": data.get("clusters", {}),
    }


@router.get("/careers")
async def list_careers():
    """Barcha career'lar (slug + title)."""
    data = await load_taxonomy_from_db()
    out = []
    for cluster_key, cluster in data.get("clusters", {}).items():
        for slug, c in cluster.get("careers", {}).items():
            out.append({
                "slug": slug,
                "title_uz": c["uz"],
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                "learning_months": c.get("learning_months"),
                "pathway_type": c.get("pathway_type"),
            })
    return {"careers": out, "total": len(out)}


@router.post("/seed")
async def seed():
    """Bir martalik: taxonomy_v1.json'dan DB'ga seed."""
    r = await seed_taxonomy_from_json("v1.0")
    return r
''', encoding="utf-8")
print("[OK] api/v1/taxonomy.py")

# ═══════════════════════════════════════════════════════════
# 7. main.py — taxonomy router
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "v1_taxonomy_router" not in main:
    main = main.replace(
        "from backend.api.v1.discovery import router as v1_discovery_router",
        "from backend.api.v1.discovery import router as v1_discovery_router\n"
        "from backend.api.v1.taxonomy import router as v1_taxonomy_router",
    )
    main = main.replace(
        "app.include_router(v1_discovery_router)",
        "app.include_router(v1_discovery_router)\n"
        "app.include_router(v1_taxonomy_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — taxonomy router")

# ═══════════════════════════════════════════════════════════
# 8. Tests
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch3_taxonomy.py").write_text(r'''"""Batch 3 — Taxonomy + Evidence testlari (DB'siz)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models_v2 import SignalEvidence, TaxonomyVersion, Career
from data_loader import load_discovery_questions
from services.discovery_service import extract_evidence


def test_signal_evidence_columns():
    cols = {c.name for c in SignalEvidence.__table__.columns}
    for f in ("session_id", "signal_key", "question_id", "answer_id",
              "contribution", "evidence_type"):
        assert f in cols


def test_taxonomy_version_columns():
    cols = {c.name for c in TaxonomyVersion.__table__.columns}
    for f in ("version", "notes", "is_active", "published_at"):
        assert f in cols


def test_career_columns():
    cols = {c.name for c in Career.__table__.columns}
    for f in ("taxonomy_version_id", "slug", "title_uz", "cluster",
              "required_signals", "prerequisites", "salary_usd"):
        assert f in cols


def test_extract_evidence_likert():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q03", "answer_id": "", "answer_value": 5},
    ]
    ev = extract_evidence(answers, questions)
    # DISC_Q03 → problem_solving (1.0), logical_thinking (0.8)
    sigs = {e["signal_key"] for e in ev}
    assert "problem_solving" in sigs
    assert "logical_thinking" in sigs
    # Contribution tekshirish
    ps = next(e for e in ev if e["signal_key"] == "problem_solving")
    assert ps["contribution"] == 10.0  # 10 * 1.0
    assert ps["evidence_type"] == "direct"


def test_extract_evidence_choice():
    questions = load_discovery_questions()["questions"]
    answers = [
        {"question_id": "DISC_Q02", "answer_id": "DISC_Q02_A01", "answer_value": 4},
    ]
    ev = extract_evidence(answers, questions)
    sigs = {e["signal_key"] for e in ev}
    assert "technical_interest" in sigs
    assert "logical_thinking" in sigs


def test_extract_evidence_empty():
    questions = load_discovery_questions()["questions"]
    assert extract_evidence([], questions) == []
''', encoding="utf-8")
print("[OK] tests/test_batch3_taxonomy.py (6 test)")

print()
print("=" * 60)
print("Batch 3 (Signal Evidence + Taxonomy DB) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • SignalEvidence table (har signal dalili)")
print("  • TaxonomyVersion + Career tables (DB-driven)")
print("  • taxonomy_service.py (load/seed)")
print("  • extract_evidence() funksiya")
print("  • /api/v1/taxonomy GET")
print("  • /api/v1/taxonomy/careers GET")
print("  • /api/v1/taxonomy/seed POST (bir martalik)")
print("  • 6 test")
print()
print("KEYINGI:")
print("  1. cd qadam")
print("  2. ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch3_taxonomy.py -v")
print("  3. cd ..")
print("  4. git add -A")
print('  5. git commit -m "Batch 3: Signal Evidence + Taxonomy DB"')
print("  6. git push")
print("  7. Render Manual Deploy")
print("  8. Brauzer: POST /api/v1/taxonomy/seed (bir marta)")