"""Threshold audit (BL-14) on a seeded DB: read-only, aggregate output, consistent counts."""
import asyncio
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from sqlalchemy import func, select  # noqa: E402

from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models_v2 import (  # noqa: E402
    DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal,
    DiscoveryAnswer, DiscoverySession, DiscoverySignal,
)
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions  # noqa: E402
from backend.services.discovery_service import compute_signals_from_discovery  # noqa: E402


async def seed(n_disc=6, n_deep=3, seed_=5):
    rng = random.Random(seed_)
    dq = load_discovery_questions()["questions"]
    deepq = flatten_questions(load_deep_diagnostic())
    disc_ids = []
    async with SessionLocal() as s:
        for u in range(n_disc):
            sess = DiscoverySession(user_id=500 + u, status="completed")
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
            for k, v in compute_signals_from_discovery(answers, dq).items():
                s.add(DiscoverySignal(session_id=sess.id, signal_key=k, **v))
            disc_ids.append(sess.id)
        for u in range(n_deep):
            sess = DeepDiagnosticSession(user_id=500 + u, status="completed", discovery_session_id=disc_ids[u])
            s.add(sess)
            await s.flush()
            answers = [{"question_id": q["id"], "answer_value": rng.randint(1, 5)} for q in deepq]
            for a in answers:
                s.add(DeepDiagnosticAnswer(session_id=sess.id, **a))
            for k, v in compute_signals(answers, deepq).items():
                if v["evidence_state"] != "unmeasured":
                    s.add(DeepDiagnosticSignal(session_id=sess.id, signal_key=k, **v))
        await s.commit()


async def counts():
    async with SessionLocal() as s:
        return [(await s.execute(select(func.count()).select_from(m))).scalar_one()
                for m in (DiscoverySignal, DeepDiagnosticSignal, DiscoverySession, DeepDiagnosticSession)]


async def main():
    await init_db()
    await seed()
    before = await counts()
    from threshold_audit import MAX_RECOMMENDATIONS, THRESHOLDS, audit
    rep = await audit()
    assert before == await counts(), "audit wrote to the DB"
    sf = rep["surfaces"]
    assert sf["career_intelligence"]["sessions"] == 6 and sf["deep_result"]["sessions"] == 3, sf
    for name, s in sf.items():
        for basis, by_t in s["thresholds"].items():
            prev_mean = None
            for t in THRESHOLDS:
                hist = by_t[str(t)]
                assert sum(hist.values()) == s["sessions"], (name, basis, t)
                assert set(hist) == {str(n) for n in range(MAX_RECOMMENDATIONS + 1)}
                mean = sum(int(k) * v for k, v in hist.items())
                assert prev_mean is None or mean <= prev_mean, "higher threshold must not add recommendations"
                prev_mean = mean
    text = json.dumps(rep)
    assert '"user_id"' not in text and "500" not in text, "ids leaked"
    print("THRESHOLD AUDIT OK", json.dumps({k: v["sessions"] for k, v in sf.items()}))


asyncio.run(main())
