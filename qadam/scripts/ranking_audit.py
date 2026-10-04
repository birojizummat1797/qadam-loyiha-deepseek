"""Read-only ranking audit: stored (old-formula) signals vs recomputed (current formula).

PM gate 2026-10-04, "Variant 2": before any --apply, measure the effect on the
recommendation layer. Nothing is written: the script refuses to run unless
QADAM_DB_READ_ONLY=1 (PostgreSQL then rejects every write by itself).

For every completed session it rebuilds what production shows from stored
signals, once with the stored values ("old") and once with what --apply would
store ("new"), using the same code paths:

  career_intelligence — discovery signals only           (api/v1/career_intelligence.py)
  deep_result         — merge_signals(discovery, deep)   (api/v1/deep_diagnostic.py, PDF)
  roadmap             — {**discovery, **deep}            (api/v1/roadmap.py)
  preliminary         — build_preliminary_insight        (shown at discovery completion)

Output: aggregate counts plus, per changed session, an anonymous label (D1…,
P1…) with old/new Top-5 career ids. No user ids, names or answers.

    QADAM_DB_READ_ONLY=1 python scripts/ranking_audit.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.db import SessionLocal  # noqa: E402
from backend.engine.ranking import rank_careers  # noqa: E402
from backend.models_v2 import (  # noqa: E402
    DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal,
    DiscoveryAnswer, DiscoverySession, DiscoverySignal,
)
from backend.services.context_service import discovery_constraints  # noqa: E402
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions, merge_signals  # noqa: E402
from backend.services.discovery_service import build_preliminary_insight, compute_signals_from_discovery  # noqa: E402
from backend.services.taxonomy_service import load_taxonomy_from_db  # noqa: E402

ALL = 25  # every candidate, so positions can be compared beyond Top-5
TOP = 5


def _rows(rows) -> dict:
    return {r.signal_key: {"value": r.value, "trust": r.trust, "evidence_state": r.evidence_state,
                           "coverage": r.coverage} for r in rows}


def _measured(signals: dict) -> set:
    return {k for k, v in signals.items() if (v or {}).get("value") is not None}


def compare_rankings(old: dict, new: dict) -> dict:
    """Deterministic recommendation output, old vs new (career ids and labels only)."""
    o_ids = [c["career_id"] for c in old["ranked"]]
    n_ids = [c["career_id"] for c in new["ranked"]]
    o_by, n_by = {c["career_id"]: c for c in old["ranked"]}, {c["career_id"]: c for c in new["ranked"]}
    moves = {}
    for cid in set(o_ids) | set(n_ids):
        if cid in o_by and cid in n_by:
            d = o_ids.index(cid) - n_ids.index(cid)  # + = moved up
            if d:
                moves[cid] = d
        else:
            moves[cid] = "entered" if cid in n_by else "left"
    labels = {}
    for cid in set(o_by) & set(n_by):
        for f in ("evidence_level", "context_status"):
            if o_by[cid][f] != n_by[cid][f]:
                labels.setdefault(cid, {})[f] = [o_by[cid][f], n_by[cid][f]]
        if sorted(o_by[cid]["missing_signals"]) != sorted(n_by[cid]["missing_signals"]):
            labels.setdefault(cid, {})["missing_signals"] = "changed"
    o_ex = {e["career_id"]: e["reason"] for e in old["excluded"]}
    n_ex = {e["career_id"]: e["reason"] for e in new["excluded"]}
    excluded = {cid: [o_ex.get(cid), n_ex.get(cid)] for cid in set(o_ex) | set(n_ex) if o_ex.get(cid) != n_ex.get(cid)}
    return {
        "order_changed": o_ids != n_ids,
        "top5_changed": o_ids[:TOP] != n_ids[:TOP],
        "top1_changed": o_ids[:1] != n_ids[:1],
        "old_top5": o_ids[:TOP], "new_top5": n_ids[:TOP],
        "moves": moves,
        "label_changes": labels,
        "excluded_changes": excluded,
        "confidence": [old["confidence"], new["confidence"]] if old["confidence"] != new["confidence"] else None,
        "empty": [not o_ids, not n_ids],
    }


def compare_preliminary(old: dict, new: dict) -> dict:
    return {
        "development_areas": [old["development_areas"], new["development_areas"]]
        if old["development_areas"] != new["development_areas"] else None,
        "signals_top_order": [[s["key"] for s in old["signals_top"]], [s["key"] for s in new["signals_top"]]]
        if [s["key"] for s in old["signals_top"]] != [s["key"] for s in new["signals_top"]] else None,
        "confidence": [old["confidence"], new["confidence"]] if old["confidence"] != new["confidence"] else None,
    }


def invariant_violations(old: dict, new: dict, prelim_new: dict | None = None) -> list[str]:
    """unmeasured ≠ weak: recompute must not create or remove measurements, nor list unmeasured as weak.

    (Per-career missing signals are compared in compare_rankings → label_changes.)
    """
    out = []
    if _measured(old) != _measured(new):
        out.append("measured_set_changed")
    if prelim_new is not None:
        if any(new.get(k, {}).get("value") is None for k in prelim_new["development_areas"]):
            out.append("unmeasured_in_development_areas")
    return out


def _empty_summary() -> dict:
    return {"sessions": 0, "unchanged": 0, "order_changed": 0, "top5_changed": 0, "top1_changed": 0,
            "label_changes": 0, "excluded_changes": 0, "confidence_changes": 0, "became_empty": 0,
            "became_non_empty": 0, "max_position_move": 0,
            # Per career, across sessions: a career that only ever falls would be a systematic shift.
            "career_moves": {}}


def _count(summary: dict, cmp: dict) -> None:
    summary["sessions"] += 1
    changed = cmp["order_changed"] or cmp["label_changes"] or cmp["excluded_changes"] or cmp["confidence"]
    summary["unchanged"] += int(not changed)
    for k in ("order_changed", "top5_changed", "top1_changed"):
        summary[k] += int(cmp[k])
    summary["label_changes"] += int(bool(cmp["label_changes"]))
    summary["excluded_changes"] += int(bool(cmp["excluded_changes"]))
    summary["confidence_changes"] += int(bool(cmp["confidence"]))
    summary["became_empty"] += int(cmp["empty"] == [False, True])
    summary["became_non_empty"] += int(cmp["empty"] == [True, False])
    for cid, d in cmp["moves"].items():
        m = summary["career_moves"].setdefault(cid, {"up": 0, "down": 0, "entered": 0, "left": 0})
        if isinstance(d, int):
            m["up" if d > 0 else "down"] += 1
            summary["max_position_move"] = max(summary["max_position_move"], abs(d))
        else:
            m[d] += 1


async def audit() -> dict:
    disc_q = load_discovery_questions()["questions"]
    deep_q = flatten_questions(load_deep_diagnostic())
    taxonomy = await load_taxonomy_from_db()

    report = {
        "read_only": os.getenv("QADAM_DB_READ_ONLY") == "1",
        "taxonomy_version": taxonomy.get("version"),
        "summary": {s: _empty_summary() for s in ("career_intelligence", "deep_result", "roadmap")},
        "preliminary": {"sessions": 0, "development_areas_changed": 0, "signals_top_order_changed": 0,
                        "confidence_changed": 0},
        "invariant_unmeasured_not_weak": {"checked_signal_sets": 0, "violations": []},
        "changed_sessions": [],
    }
    inv = report["invariant_unmeasured_not_weak"]

    async with SessionLocal() as s:
        disc_ids = (await s.execute(select(DiscoverySession.id).where(DiscoverySession.status == "completed")
                                    .order_by(DiscoverySession.id))).scalars().all()
        deep_ids = (await s.execute(select(DeepDiagnosticSession.id).where(DeepDiagnosticSession.status == "completed")
                                    .order_by(DeepDiagnosticSession.id))).scalars().all()

    disc_cache: dict[int, tuple[dict, dict, list]] = {}

    async def discovery_pair(sid: int):
        if sid not in disc_cache:
            async with SessionLocal() as s:
                rows = (await s.execute(select(DiscoverySignal).where(DiscoverySignal.session_id == sid))).scalars().all()
                answers = (await s.execute(select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == sid))).scalars().all()
            ans = [{"question_id": a.question_id, "answer_id": a.answer_id, "answer_value": a.answer_value} for a in answers]
            disc_cache[sid] = (_rows(rows), compute_signals_from_discovery(ans, disc_q), ans)
        return disc_cache[sid]

    for i, sid in enumerate(disc_ids, 1):
        label = f"D{i}"
        old, new, ans = await discovery_pair(sid)
        constraints = await discovery_constraints(sid)
        r_old = rank_careers(signals=old, taxonomy=taxonomy, constraints=constraints, top_n=ALL)
        r_new = rank_careers(signals=new, taxonomy=taxonomy, constraints=constraints, top_n=ALL)
        cmp = compare_rankings(r_old, r_new)
        _count(report["summary"]["career_intelligence"], cmp)

        p_old = build_preliminary_insight(old, ans, taxonomy)
        p_new = build_preliminary_insight(new, ans, taxonomy)
        pc = compare_preliminary(p_old, p_new)
        report["preliminary"]["sessions"] += 1
        report["preliminary"]["development_areas_changed"] += int(bool(pc["development_areas"]))
        report["preliminary"]["signals_top_order_changed"] += int(bool(pc["signals_top_order"]))
        report["preliminary"]["confidence_changed"] += int(bool(pc["confidence"]))

        inv["checked_signal_sets"] += 1
        inv["violations"] += [f"{label}:{v}" for v in invariant_violations(old, new, p_new)]
        inv["violations"] += [f"{label}:{c}:missing_signals_changed" for c, ch in cmp["label_changes"].items()
                              if "missing_signals" in ch]
        if cmp["order_changed"] or cmp["label_changes"] or cmp["excluded_changes"] or cmp["confidence"] or any(pc.values()):
            report["changed_sessions"].append({"session": label, "surface": "career_intelligence", **cmp,
                                               "preliminary": pc})

    for i, sid in enumerate(deep_ids, 1):
        label = f"P{i}"
        async with SessionLocal() as s:
            sess = await s.get(DeepDiagnosticSession, sid)
            rows = (await s.execute(select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == sid))).scalars().all()
            answers = (await s.execute(select(DeepDiagnosticAnswer).where(DeepDiagnosticAnswer.session_id == sid))).scalars().all()
        deep_old = _rows(rows)
        computed = compute_signals([{"question_id": a.question_id, "answer_value": a.answer_value} for a in answers], deep_q)
        deep_new = {k: v for k, v in computed.items() if v["evidence_state"] != "unmeasured"}  # what --apply stores
        if sess.discovery_session_id:
            d_old, d_new, _ = await discovery_pair(sess.discovery_session_id)
        else:
            d_old, d_new = {}, {}
        constraints = await discovery_constraints(sess.discovery_session_id)

        inv["checked_signal_sets"] += 1
        inv["violations"] += [f"{label}:deep:{v}" for v in
                              invariant_violations(deep_old, deep_new)]

        for surface, merge in (("deep_result", merge_signals), ("roadmap", lambda a, b: {**a, **b})):
            r_old = rank_careers(signals=merge(d_old, deep_old), taxonomy=taxonomy, constraints=constraints, top_n=ALL)
            r_new = rank_careers(signals=merge(d_new, deep_new), taxonomy=taxonomy, constraints=constraints, top_n=ALL)
            cmp = compare_rankings(r_old, r_new)
            _count(report["summary"][surface], cmp)
            inv["violations"] += [f"{label}:{surface}:{c}:missing_signals_changed"
                                  for c, ch in cmp["label_changes"].items() if "missing_signals" in ch]
            if cmp["order_changed"] or cmp["label_changes"] or cmp["excluded_changes"] or cmp["confidence"]:
                report["changed_sessions"].append({"session": label, "surface": surface, **cmp})

    inv["passed"] = not inv["violations"]
    return report


def main():
    if os.getenv("QADAM_DB_READ_ONLY") != "1":
        sys.exit("refused: run with QADAM_DB_READ_ONLY=1 (read-only audit)")
    print(json.dumps(asyncio.run(audit()), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
