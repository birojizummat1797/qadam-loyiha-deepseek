"""Ranking audit on a simulated legacy DB: stored values made with the OLD formula mean(v·w)."""
import asyncio
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from sqlalchemy import func, select  # noqa: E402

from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.engine.signals import LIKERT_TO_10, SIGNAL_KEYS  # noqa: E402
from backend.models_v2 import (  # noqa: E402
    DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal,
    DiscoveryAnswer, DiscoverySession, DiscoverySignal,
)
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions  # noqa: E402
from backend.services.discovery_service import compute_signals_from_discovery  # noqa: E402


def old_formula(pairs):
    """What production stored before the fix: mean(v·w) (overflows for w > 1)."""
    return round(sum(v * w for v, w in pairs) / len(pairs), 2) if pairs else None


def disc_pairs(answers, questions):
    qmap = {q["id"]: q for q in questions}
    raw = {k: [] for k in SIGNAL_KEYS}
    for a in answers:
        q = qmap[a["question_id"]]
        if q["type"] == "likert":
            for sig, w in q.get("signals", {}).items():
                raw[sig].append((LIKERT_TO_10.get(a["answer_value"], 5.0), w))
        else:
            o = next(o for o in q["options"] if o["id"] == a["answer_id"])
            for sig, w in o.get("signals", {}).items():
                raw[sig].append((LIKERT_TO_10.get(int(o.get("value", 3)), 5.0), w))
    return raw


async def seed(n_disc=8, n_deep=4, seed_=3):
    rng = random.Random(seed_)
    dq = load_discovery_questions()["questions"]
    deepq = flatten_questions(load_deep_diagnostic())
    disc_ids = []
    async with SessionLocal() as s:
        for u in range(n_disc):
            sess = DiscoverySession(user_id=100 + u, status="completed")
            s.add(sess)
            await s.flush()
            answers = []
            for q in dq:
                if q["type"] == "likert":
                    v = rng.randint(1, 5)
                    answers.append({"question_id": q["id"], "answer_id": f"likert_{v}", "answer_value": v})
                else:
                    o = rng.choice(q["options"])
                    answers.append({"question_id": q["id"], "answer_id": o["id"], "answer_value": 3})
            for a in answers:
                s.add(DiscoveryAnswer(session_id=sess.id, **a))
            new = compute_signals_from_discovery(answers, dq)
            raw = disc_pairs(answers, dq)
            for k, v in new.items():
                s.add(DiscoverySignal(session_id=sess.id, signal_key=k, value=old_formula(raw[k]) if v["value"] is not None else None,
                                      trust=v["trust"], evidence_state=v["evidence_state"], coverage=v["coverage"]))
            disc_ids.append(sess.id)
        for u in range(n_deep):
            sess = DeepDiagnosticSession(user_id=100 + u, status="completed", discovery_session_id=disc_ids[u])
            s.add(sess)
            await s.flush()
            answers = [{"question_id": q["id"], "answer_value": rng.randint(1, 5)} for q in deepq]
            for a in answers:
                s.add(DeepDiagnosticAnswer(session_id=sess.id, **a))
            new = compute_signals(answers, deepq)
            qmap = {q["id"]: q for q in deepq}
            raw = {k: [] for k in SIGNAL_KEYS}
            for a in answers:
                for sig, w in (qmap[a["question_id"]].get("signals") or {}).items():
                    if sig in raw:
                        raw[sig].append((LIKERT_TO_10.get(a["answer_value"], 5.0), w))
            for k, v in new.items():
                if v["evidence_state"] != "unmeasured":
                    s.add(DeepDiagnosticSignal(session_id=sess.id, signal_key=k, value=old_formula(raw[k]),
                                               trust=v["trust"], evidence_state=v["evidence_state"], coverage=v["coverage"]))
        await s.commit()


async def counts():
    async with SessionLocal() as s:
        return [(await s.execute(select(func.count()).select_from(m))).scalar_one()
                for m in (DiscoverySignal, DeepDiagnosticSignal, DiscoverySession, DeepDiagnosticSession)]


async def main():
    await init_db()
    await seed()
    before = await counts()
    from ranking_audit import audit
    rep = await audit()
    after = await counts()
    assert before == after, "audit wrote to the DB"
    sm = rep["summary"]
    assert sm["career_intelligence"]["sessions"] == 8 and sm["deep_result"]["sessions"] == 4 and sm["roadmap"]["sessions"] == 4, sm
    assert rep["invariant_unmeasured_not_weak"]["passed"], rep["invariant_unmeasured_not_weak"]
    for c in rep["changed_sessions"]:
        assert set(c) >= {"session", "surface", "old_top5", "new_top5", "moves", "top1_changed"}
        assert not any(isinstance(x, int) and x > 1000 for x in json.dumps(c)), "raw ids leaked"
    text = json.dumps(rep)
    assert '"user_id"' not in text and "100" not in text.replace("1000", ""), "user ids leaked"
    print("RANKING AUDIT OK", json.dumps(rep["summary"]), rep["invariant_unmeasured_not_weak"]["passed"])


asyncio.run(main())
