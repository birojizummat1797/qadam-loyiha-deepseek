"""Read-only threshold audit for BL-14 (founder decision 2026-10-04).

Founder decision: 5 is a ceiling, not a quota. A career is recommended only if
its score reaches an approved minimum; 0 qualifying careers → an honest
"no clear direction yet" message. The threshold value is NOT chosen here: this
script only measures, on the current production sessions, how many
recommendations each candidate threshold would give, so the founder can decide.

    count(session, T) = min(5, number of eligible careers with score >= T)

"Eligible" = what rank_careers already ranks today (has a roadmap, coverage
>= 0.5). Two score bases are reported side by side, nothing is picked:
  fit        — how close the measured signals are to the career (0–100);
  composite  — fit × readiness modifier (0.7–1.0), what the ranking sorts by.

Surfaces (same code paths as production):
  career_intelligence — discovery signals                 (api/v1/career_intelligence.py)
  deep_result         — merge_signals(discovery, deep)    (api/v1/deep_diagnostic.py, PDF)
  roadmap             — {**discovery, **deep}             (api/v1/roadmap.py)

Reference (synthetic, no DB): the same surfaces for seeded random answer sets
("random clicking"). A threshold that random answers pass easily does not mean
"close"; this anchors the scale. It is labelled synthetic in the output.

Output is aggregate only (counts and quantiles): no ids, names or answers.
Refuses to run unless QADAM_DB_READ_ONLY=1.

    QADAM_DB_READ_ONLY=1 python scripts/threshold_audit.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MAX_RECOMMENDATIONS = 5
THRESHOLDS = list(range(20, 85, 5))  # candidate values to measure, not a choice
BASES = ("fit", "composite_score")
SURFACES = ("career_intelligence", "deep_result", "roadmap")


def count_at(scores: list[float], threshold: float, max_n: int = MAX_RECOMMENDATIONS) -> int:
    """How many recommendations a session gets at this threshold (ceiling, not quota)."""
    return min(max_n, sum(1 for s in scores if s is not None and s >= threshold))


def count_histogram(sessions: list[list[float]], threshold: float) -> dict[str, int]:
    """Sessions per recommendation count 0..5 at one threshold."""
    hist = {str(n): 0 for n in range(MAX_RECOMMENDATIONS + 1)}
    for scores in sessions:
        hist[str(count_at(scores, threshold))] += 1
    return hist


def quantiles(values: list[float]) -> dict | None:
    """min / p25 / median / p75 / max (nearest rank); None when empty."""
    v = sorted(x for x in values if x is not None)
    if not v:
        return None

    def at(q: float) -> float:
        return round(v[min(len(v) - 1, max(0, round(q * (len(v) - 1))))], 1)

    return {"n": len(v), "min": at(0), "p25": at(0.25), "median": at(0.5), "p75": at(0.75), "max": at(1)}


def summarize(sessions: list[list[dict]]) -> dict:
    """sessions: per session, the eligible candidates (rank_careers 'ranked' rows)."""
    out = {
        "sessions": len(sessions),
        "eligible_careers_per_session": {
            str(n): sum(1 for c in sessions if len(c) == n) for n in sorted({len(c) for c in sessions})
        },
        "score_quantiles": {},
        "thresholds": {},
    }
    for basis in BASES:
        per_session = [sorted((c[basis] for c in cands), reverse=True) for cands in sessions]
        out["score_quantiles"][basis] = {
            "top1": quantiles([s[0] for s in per_session if s]),
            "top5_each": quantiles([x for s in per_session for x in s[:MAX_RECOMMENDATIONS]]),
        }
        out["thresholds"][basis] = {str(t): count_histogram(per_session, t) for t in THRESHOLDS}
    return out


def random_baseline(taxonomy: dict, n: int = 200, seed: int = 2026) -> dict:
    """Same summaries for n seeded random answer sets (constraints unknown → no readiness modifier)."""
    import random

    from backend.data_loader import load_deep_diagnostic, load_discovery_questions
    from backend.engine.ranking import rank_careers
    from backend.services.deep_diagnostic_service import compute_signals, flatten_questions, merge_signals
    from backend.services.discovery_service import compute_signals_from_discovery

    rng = random.Random(seed)
    dq = load_discovery_questions()["questions"]
    deepq = flatten_questions(load_deep_diagnostic())
    out = {s: [] for s in SURFACES}
    for _ in range(n):
        answers = []
        for q in dq:
            if q["type"] == "likert":
                v = rng.randint(1, 5)
                answers.append({"question_id": q["id"], "answer_id": f"likert_{v}", "answer_value": v})
            else:
                o = rng.choice(q["options"])
                answers.append({"question_id": q["id"], "answer_id": o["id"], "answer_value": 3})
        disc = compute_signals_from_discovery(answers, dq)
        deep = {k: v for k, v in compute_signals(
            [{"question_id": q["id"], "answer_value": rng.randint(1, 5)} for q in deepq], deepq).items()
            if v["evidence_state"] != "unmeasured"}
        for name, sig in (("career_intelligence", disc), ("deep_result", merge_signals(disc, deep)),
                          ("roadmap", {**disc, **deep})):
            out[name].append(rank_careers(signals=sig, taxonomy=taxonomy, constraints={}, top_n=100)["ranked"])
    return {"synthetic": True, "answer_sets": n, "seed": seed,
            "surfaces": {name: summarize(sessions) for name, sessions in out.items()}}


async def audit() -> dict:
    from sqlalchemy import select

    from backend.db import SessionLocal
    from backend.engine.ranking import rank_careers
    from backend.models_v2 import DeepDiagnosticSession, DeepDiagnosticSignal, DiscoverySession, DiscoverySignal
    from backend.services.context_service import discovery_constraints
    from backend.services.deep_diagnostic_service import merge_signals
    from backend.services.taxonomy_service import load_taxonomy_from_db

    def rows(rs) -> dict:
        return {r.signal_key: {"value": r.value, "trust": r.trust, "evidence_state": r.evidence_state,
                               "coverage": r.coverage} for r in rs}

    taxonomy = await load_taxonomy_from_db()
    collected = {s: [] for s in SURFACES}

    def eligible(signals: dict, constraints) -> list[dict]:
        return rank_careers(signals=signals, taxonomy=taxonomy, constraints=constraints, top_n=100)["ranked"]

    async with SessionLocal() as s:
        disc_ids = (await s.execute(select(DiscoverySession.id).where(DiscoverySession.status == "completed")
                                    .order_by(DiscoverySession.id))).scalars().all()
        deep_ids = (await s.execute(select(DeepDiagnosticSession.id).where(DeepDiagnosticSession.status == "completed")
                                    .order_by(DeepDiagnosticSession.id))).scalars().all()

    async def disc_signals(sid) -> dict:
        if not sid:
            return {}
        async with SessionLocal() as s:
            return rows((await s.execute(select(DiscoverySignal).where(DiscoverySignal.session_id == sid))).scalars().all())

    for sid in disc_ids:
        collected["career_intelligence"].append(eligible(await disc_signals(sid), await discovery_constraints(sid)))

    for sid in deep_ids:
        async with SessionLocal() as s:
            sess = await s.get(DeepDiagnosticSession, sid)
            deep = rows((await s.execute(select(DeepDiagnosticSignal)
                                         .where(DeepDiagnosticSignal.session_id == sid))).scalars().all())
        disc = await disc_signals(sess.discovery_session_id)
        constraints = await discovery_constraints(sess.discovery_session_id)
        collected["deep_result"].append(eligible(merge_signals(disc, deep), constraints))
        collected["roadmap"].append(eligible({**disc, **deep}, constraints))

    return {
        "read_only": os.getenv("QADAM_DB_READ_ONLY") == "1",
        "taxonomy_version": taxonomy.get("version"),
        "max_recommendations": MAX_RECOMMENDATIONS,
        "thresholds_measured": THRESHOLDS,
        "surfaces": {name: summarize(sessions) for name, sessions in collected.items()},
        "random_baseline": random_baseline(taxonomy),
    }


def main():
    if os.getenv("QADAM_DB_READ_ONLY") != "1":
        sys.exit("refused: run with QADAM_DB_READ_ONLY=1 (read-only audit)")
    print(json.dumps(asyncio.run(audit()), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
