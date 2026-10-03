"""Legacy strategy check: a stored out-of-range signal is found (dry run) and fixed (--apply)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from sqlalchemy import select  # noqa: E402

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models_v2 import DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal  # noqa: E402
from recompute_signals import recompute  # noqa: E402


async def main():
    await init_db()
    async with SessionLocal() as s:
        sess = DeepDiagnosticSession(user_id=1, status="completed")
        s.add(sess)
        await s.flush()
        s.add(DeepDiagnosticAnswer(session_id=sess.id, question_id="DD_Q03", answer_value=5))
        # What the old formula stored: 10 * 1.5
        s.add(DeepDiagnosticSignal(session_id=sess.id, signal_key="technical_interest", value=15.0,
                                   trust=0.6, evidence_state="insufficient", coverage=1))
        await s.commit()
        sid = sess.id

    dry = await recompute(apply=False)
    assert dry["stored_values_above_10"] == 1 and dry["sessions_changed"] == 1, dry
    async with SessionLocal() as s:
        v = (await s.execute(select(DeepDiagnosticSignal.value).where(DeepDiagnosticSignal.session_id == sid))).scalars().all()
    assert v == [15.0], f"dry run must not write: {v}"

    applied = await recompute(apply=True)
    assert applied["sessions_changed"] == 1, applied
    async with SessionLocal() as s:
        rows = (await s.execute(select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == sid))).scalars().all()
    values = {r.signal_key: r.value for r in rows}
    assert all(0 <= x <= 10 for x in values.values()), values
    assert values.get("technical_interest") == 10.0, values

    again = await recompute(apply=False)
    assert again["sessions_changed"] == 0 and again["stored_values_above_10"] == 0, again
    print("LEGACY OK", values)


asyncio.run(main())
