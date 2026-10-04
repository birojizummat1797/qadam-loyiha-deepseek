"""Read-only: does the taxonomy production ranks with (DB) match taxonomy_v1.json?

load_taxonomy_from_db() reads the active TaxonomyVersion from the DB, which
seed_taxonomy_from_json() filled once; later edits to taxonomy_v1.json do not
reach it. This prints, per career, every field that differs. Taxonomy is
catalog data, not personal data. Refuses to run unless QADAM_DB_READ_ONLY=1.

    QADAM_DB_READ_ONLY=1 python scripts/taxonomy_audit.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FIELDS = ("uz", "signals", "prerequisites", "learning_months", "pathway_type")


def flatten(tax: dict) -> dict:
    return {slug: {"cluster": ck, "cluster_uz": c.get("uz"), **{f: car.get(f) for f in FIELDS}}
            for ck, c in tax["clusters"].items() for slug, car in c["careers"].items()}


def compare(db: dict, file: dict) -> dict:
    a, b = flatten(db), flatten(file)
    diffs = {}
    for slug in sorted(set(a) & set(b)):
        d = {f: {"db": a[slug][f], "file": b[slug][f]} for f in a[slug] if a[slug][f] != b[slug][f]}
        if d:
            diffs[slug] = d
    return {
        "db_version": db.get("version"), "file_version": file.get("version"),
        "db_careers": len(a), "file_careers": len(b),
        "only_in_db": sorted(set(a) - set(b)), "only_in_file": sorted(set(b) - set(a)),
        "careers_differing": len(diffs), "diffs": diffs,
        "identical": not diffs and set(a) == set(b),
    }


async def audit() -> dict:
    from backend.services.taxonomy_service import load_taxonomy_from_db
    from backend.data_loader import load_taxonomy
    return compare(await load_taxonomy_from_db(), load_taxonomy())


def main():
    if os.getenv("QADAM_DB_READ_ONLY") != "1":
        sys.exit("refused: run with QADAM_DB_READ_ONLY=1 (read-only audit)")
    print(json.dumps(asyncio.run(audit()), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
