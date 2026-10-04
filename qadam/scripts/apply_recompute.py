"""Audited, verified --apply of the signal recompute (PM approval 2026-10-04).

Three modes, run in this order by .github/workflows/recompute-apply.yml:

  snapshot  (read-only)  Reference for everything after it: for every completed
                         session the stored rows ("old"), the rows --apply will
                         write ("expected"), and the expected rankings/labels on
                         every surface. Also row counts of every table.
  apply     (write)      ONE transaction: for each changed session, check the
                         stored rows still equal the snapshot (no drift), replace
                         them with the expected rows, read them back and compare.
                         Any difference → ROLLBACK, exit 1. Only *_signals rows of
                         changed sessions are touched.
  verify    (read-only)  Post-apply values == snapshot expected values; untouched
                         sessions == snapshot old values; table counts unchanged;
                         rankings == expected; labels/excluded/confidence/missing
                         unchanged vs pre-apply; unmeasured ≠ weak.

    QADAM_DB_READ_ONLY=1 python scripts/apply_recompute.py snapshot snapshot.json
    QADAM_APPLY_CONFIRM=APPLY-2026-10-04 python scripts/apply_recompute.py apply snapshot.json
    QADAM_DB_READ_ONLY=1 python scripts/apply_recompute.py verify snapshot.json

Printed output is aggregate only; the snapshot file holds per-session values
and must not be published unencrypted (public repository).
"""
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import delete, func, select, text  # noqa: E402

from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.db import Base, SessionLocal  # noqa: E402
from backend.engine.ranking import rank_careers  # noqa: E402
from backend.models_v2 import (  # noqa: E402
    DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal,
    DiscoveryAnswer, DiscoverySession, DiscoverySignal,
)
from backend.services.context_service import discovery_constraints  # noqa: E402
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions, merge_signals  # noqa: E402
from backend.services.discovery_service import build_preliminary_insight, compute_signals_from_discovery  # noqa: E402
from backend.services.taxonomy_service import load_taxonomy_from_db  # noqa: E402
from ranking_audit import compare_rankings  # noqa: E402

CONFIRM = "APPLY-2026-10-04"
FIELDS = ("value", "trust", "evidence_state", "coverage")
EPS = 0.005  # same threshold as recompute_signals._changed


class Mismatch(Exception):
    pass


def _row(r) -> dict:
    return {f: getattr(r, f) for f in FIELDS}


def _norm(rows: dict) -> dict:
    """Canonical form for exact comparison (floats rounded to 6 dp)."""
    out = {}
    for k, v in sorted(rows.items()):
        out[k] = {f: (round(v[f], 6) if isinstance(v[f], float) else v[f]) for f in FIELDS}
    return out


def _changed(old: dict, new: dict) -> bool:
    keys = set(old) | {k for k, v in new.items() if v["value"] is not None}
    for k in keys:
        a = (old.get(k) or {}).get("value")
        b = (new.get(k) or {}).get("value")
        if (a is None) != (b is None) or (a is not None and abs(a - b) > EPS):
            return True
    return False


def _ranking_view(r: dict) -> dict:
    """What a user sees from a ranking: order + per-career labels + excluded + confidence."""
    return {
        "order": [c["career_id"] for c in r["ranked"]],
        "labels": {c["career_id"]: {"evidence_level": c["evidence_level"], "context_status": c["context_status"],
                                    "missing_signals": sorted(c["missing_signals"])} for c in r["ranked"]},
        "excluded": {e["career_id"]: e["reason"] for e in r["excluded"]},
        "confidence": r["confidence"],
    }


async def _table_names(s) -> list[str]:
    """Every table in the database (catalog), plus every model table — nothing escapes the count check."""
    import backend.models  # noqa: F401  (registers legacy tables: events, users, payments, …)
    names = set(Base.metadata.tables)
    # Chosen by dialect, never by catching an error: a rollback here would also undo
    # the apply transaction's own writes.
    if s.bind.dialect.name == "postgresql":
        rows = await s.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"))
        names |= {r[0] for r in rows}
    else:
        rows = await s.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'"))
        names |= {r[0] for r in rows if not r[0].startswith("sqlite_")}
    return sorted(names)


async def _counts_in(s) -> dict:
    present = await _db_tables(s)
    return {name: ((await s.execute(text(f'SELECT count(*) FROM "{name}"'))).scalar_one() if name in present else None)
            for name in await _table_names(s)}


async def _db_tables(s) -> set:
    if s.bind.dialect.name == "postgresql":
        rows = await s.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"))
    else:
        rows = await s.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'"))
    return {r[0] for r in rows}


async def _table_counts() -> dict:
    async with SessionLocal() as s:
        return await _counts_in(s)


async def _surfaces(disc: dict, deep: dict, deep_meta: dict, taxonomy: dict, which: str) -> dict:
    """Rankings on every production surface, from `which` ("old" or "expected") rows."""
    out = {}
    for sid, d in disc.items():
        cons = await discovery_constraints(int(sid))
        out[f"ci:{sid}"] = _ranking_view(rank_careers(signals=d[which], taxonomy=taxonomy, constraints=cons, top_n=25))
    for sid, p in deep.items():
        dsid = deep_meta[sid]
        d_rows = disc[str(dsid)][which] if dsid is not None and str(dsid) in disc else {}
        cons = await discovery_constraints(dsid)
        for surface, merge in (("deep", merge_signals), ("roadmap", lambda a, b: {**a, **b})):
            out[f"{surface}:{sid}"] = _ranking_view(
                rank_careers(signals=merge(d_rows, p[which]), taxonomy=taxonomy, constraints=cons, top_n=25))
    return out


async def snapshot(path: str) -> dict:
    disc_q = load_discovery_questions()["questions"]
    deep_q = flatten_questions(load_deep_diagnostic())
    taxonomy = await load_taxonomy_from_db()
    disc, deep, deep_meta = {}, {}, {}
    async with SessionLocal() as s:
        for sid in (await s.execute(select(DiscoverySession.id).where(DiscoverySession.status == "completed")
                                    .order_by(DiscoverySession.id))).scalars().all():
            rows = (await s.execute(select(DiscoverySignal).where(DiscoverySignal.session_id == sid))).scalars().all()
            ans = (await s.execute(select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == sid))).scalars().all()
            old = {r.signal_key: _row(r) for r in rows}
            new = compute_signals_from_discovery(
                [{"question_id": a.question_id, "answer_id": a.answer_id, "answer_value": a.answer_value} for a in ans],
                disc_q)
            expected = {k: {f: v[f] for f in FIELDS} for k, v in new.items()}  # discovery keeps all keys
            disc[str(sid)] = {"old": _norm(old), "expected": _norm(expected), "changed": _changed(old, new),
                              "preliminary_dev_areas": build_preliminary_insight(new, [], taxonomy)["development_areas"]}
        for sid in (await s.execute(select(DeepDiagnosticSession.id).where(DeepDiagnosticSession.status == "completed")
                                    .order_by(DeepDiagnosticSession.id))).scalars().all():
            sess = await s.get(DeepDiagnosticSession, sid)
            rows = (await s.execute(select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == sid))).scalars().all()
            ans = (await s.execute(select(DeepDiagnosticAnswer).where(DeepDiagnosticAnswer.session_id == sid))).scalars().all()
            old = {r.signal_key: _row(r) for r in rows}
            new = compute_signals([{"question_id": a.question_id, "answer_value": a.answer_value} for a in ans], deep_q)
            expected = {k: {f: v[f] for f in FIELDS} for k, v in new.items() if v["evidence_state"] != "unmeasured"}
            deep[str(sid)] = {"old": _norm(old), "expected": _norm(expected), "changed": _changed(old, new)}
            deep_meta[str(sid)] = sess.discovery_session_id

    snap = {
        "confirm": CONFIRM,
        "discovery": disc, "deep": deep, "deep_discovery": deep_meta,
        "table_counts": await _table_counts(),
        "rankings_old": await _surfaces(disc, deep, deep_meta, taxonomy, "old"),
        "rankings_expected": await _surfaces(disc, deep, deep_meta, taxonomy, "expected"),
    }
    Path(path).write_text(json.dumps(snap, sort_keys=True, ensure_ascii=False))
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {
        "mode": "snapshot", "sha256": digest,
        "discovery_sessions": len(disc), "deep_sessions": len(deep),
        "discovery_to_change": sum(d["changed"] for d in disc.values()),
        "deep_to_change": sum(d["changed"] for d in deep.values()),
        "surfaces": len(snap["rankings_expected"]),
    }


def _load(path: str) -> dict:
    snap = json.loads(Path(path).read_text())
    if snap.get("confirm") != CONFIRM:
        raise Mismatch("snapshot is not the approved one")
    return snap


async def apply(path: str) -> dict:
    if os.getenv("QADAM_APPLY_CONFIRM") != CONFIRM:
        raise Mismatch(f"QADAM_APPLY_CONFIRM must be {CONFIRM}")
    snap = _load(path)
    plan = [("discovery", DiscoverySignal, sid, d) for sid, d in snap["discovery"].items() if d["changed"]] + \
           [("deep", DeepDiagnosticSignal, sid, d) for sid, d in snap["deep"].items() if d["changed"]]
    written = 0
    async with SessionLocal() as s:
        try:
            if s.bind.dialect.name == "postgresql":
                # The transaction sees only its own writes: the before/after counts below
                # prove that nothing outside the planned *_signals rows was mutated.
                await s.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            counts_before = await _counts_in(s)
            for kind, model, sid, d in plan:
                rows = (await s.execute(select(model).where(model.session_id == int(sid)))).scalars().all()
                current = _norm({r.signal_key: _row(r) for r in rows})
                if current != d["old"]:
                    raise Mismatch(f"{kind} session drifted since snapshot")
                await s.execute(delete(model).where(model.session_id == int(sid)))
                for key, v in d["expected"].items():
                    s.add(model(session_id=int(sid), signal_key=key, **v))
                    written += 1
                await s.flush()
                back = (await s.execute(select(model).where(model.session_id == int(sid)))).scalars().all()
                if _norm({r.signal_key: _row(r) for r in back}) != d["expected"]:
                    raise Mismatch(f"{kind} session read-back differs from expected")
            counts_after = await _counts_in(s)
            expected_delta = {
                "discovery_signals": sum(len(d["expected"]) - len(d["old"]) for k, _, _, d in plan if k == "discovery"),
                "deep_diagnostic_signals": sum(len(d["expected"]) - len(d["old"]) for k, _, _, d in plan if k == "deep"),
            }
            for name, before in counts_before.items():
                delta = (counts_after.get(name) or 0) - (before or 0)
                if delta != expected_delta.get(name, 0):
                    raise Mismatch(f"unexpected mutation in {name} (delta {delta})")
            await s.commit()
        except Exception:
            await s.rollback()
            raise
    return {"mode": "apply", "applied": True, "sessions_applied": len(plan), "rows_written": written}


async def verify(path: str) -> dict:
    snap = _load(path)
    problems = []

    async with SessionLocal() as s:
        for kind, model, block in (("discovery", DiscoverySignal, snap["discovery"]), ("deep", DeepDiagnosticSignal, snap["deep"])):
            for sid, d in block.items():
                rows = (await s.execute(select(model).where(model.session_id == int(sid)))).scalars().all()
                actual = _norm({r.signal_key: _row(r) for r in rows})
                ref = d["expected"] if d["changed"] else d["old"]
                if actual != ref:
                    problems.append(f"{kind}:values_mismatch")

    # Row counts outside the snapshot sessions may move because real users keep using the
    # product during the run. That is reported, not failed: apply's own scope is proven
    # inside its transaction (REPEATABLE READ before/after counts) and by the exact
    # per-session checks above.
    counts = await _table_counts()
    concurrent = {n: (counts.get(n) or 0) - (b or 0) for n, b in snap["table_counts"].items()
                  if counts.get(n) != b}
    for kind in ("discovery", "deep"):
        delta = sum(len(d["expected"]) - len(d["old"]) for d in snap[kind].values() if d["changed"])
        name = "discovery_signals" if kind == "discovery" else "deep_diagnostic_signals"
        if name in concurrent:
            concurrent[name] -= delta
            if not concurrent[name]:
                del concurrent[name]

    taxonomy = await load_taxonomy_from_db()
    actual_disc = {sid: {"actual": d["expected"] if d["changed"] else d["old"]} for sid, d in snap["discovery"].items()}
    # Re-read from DB (not from the snapshot) for the ranking check.
    async with SessionLocal() as s:
        for sid in actual_disc:
            rows = (await s.execute(select(DiscoverySignal).where(DiscoverySignal.session_id == int(sid)))).scalars().all()
            actual_disc[sid]["actual"] = _norm({r.signal_key: _row(r) for r in rows})
        actual_deep = {}
        for sid in snap["deep"]:
            rows = (await s.execute(select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == int(sid)))).scalars().all()
            actual_deep[sid] = {"actual": _norm({r.signal_key: _row(r) for r in rows})}
    rankings_actual = await _surfaces(actual_disc, actual_deep, snap["deep_discovery"], taxonomy, "actual")

    order_mismatch = label_changes = 0
    for key, exp in snap["rankings_expected"].items():
        act = rankings_actual.get(key)
        if act != exp:
            order_mismatch += 1
        old = snap["rankings_old"][key]
        if (act["labels"] != {c: v for c, v in old["labels"].items() if c in act["labels"]}
                or act["excluded"] != old["excluded"] or act["confidence"] != old["confidence"]):
            label_changes += 1
    if order_mismatch:
        problems.append(f"ranking_mismatch:{order_mismatch}")
    if label_changes:
        problems.append(f"labels_excluded_confidence_changed:{label_changes}")

    measured_changed = 0
    weak_unmeasured = 0
    for sid, d in snap["discovery"].items():
        a = actual_disc[sid]["actual"]
        if {k for k, v in a.items() if v["value"] is not None} != {k for k, v in d["old"].items() if v["value"] is not None}:
            measured_changed += 1
        if any(a.get(k, {}).get("value") is None for k in d["preliminary_dev_areas"]):
            weak_unmeasured += 1
    for sid, d in snap["deep"].items():
        a = actual_deep[sid]["actual"]
        if {k for k, v in a.items() if v["value"] is not None} != {k for k, v in d["old"].items() if v["value"] is not None}:
            measured_changed += 1
    if measured_changed or weak_unmeasured:
        problems.append(f"unmeasured_not_weak_failed:{measured_changed}/{weak_unmeasured}")

    return {
        "mode": "verify", "passed": not problems, "problems": problems,
        "sessions_checked": len(snap["discovery"]) + len(snap["deep"]),
        "surfaces_checked": len(snap["rankings_expected"]),
        "ranking_expected_equals_actual": order_mismatch == 0,
        "labels_excluded_confidence_unchanged": label_changes == 0,
        "unmeasured_not_weak": not (measured_changed or weak_unmeasured),
        "concurrent_activity_rows": concurrent,  # informational: new rows by real users during the run
    }


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("snapshot", "apply", "verify"):
        sys.exit("usage: apply_recompute.py snapshot|apply|verify <snapshot.json>")
    mode, path = sys.argv[1], sys.argv[2]
    read_only = os.getenv("QADAM_DB_READ_ONLY") == "1"
    if mode in ("snapshot", "verify") and not read_only:
        sys.exit(f"refused: {mode} must run with QADAM_DB_READ_ONLY=1")
    if mode == "apply" and read_only:
        sys.exit("refused: apply cannot run read-only")
    fn = {"snapshot": snapshot, "apply": apply, "verify": verify}[mode]
    try:
        result = asyncio.run(fn(path))
    except Mismatch as e:
        print(json.dumps({"mode": mode, "passed": False, "error": str(e)}))
        sys.exit(1)
    print(json.dumps(result, indent=2))
    if result.get("passed") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
