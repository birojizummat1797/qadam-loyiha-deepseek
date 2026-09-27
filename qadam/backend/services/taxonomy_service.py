"""Taxonomy Service — DB-driven."""
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
