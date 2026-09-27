"""Taxonomy API v1 — DB-driven, public read."""
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
