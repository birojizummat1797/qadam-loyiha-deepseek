"""Audited apply on a simulated legacy DB: snapshot → apply → dry run → verify, plus refusals."""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from sqlalchemy import select, update  # noqa: E402

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models_v2 import DeepDiagnosticSignal, DiscoverySignal  # noqa: E402

src = (Path(__file__).parent / "ranking_audit_flow.py").read_text().replace("asyncio.run(main())", "")
ns = {"__name__": "seedmod", "__file__": str(Path(__file__).parent / "ranking_audit_flow.py")}
exec(compile(src, "ranking_audit_flow", "exec"), ns)

import apply_recompute as a  # noqa: E402
from recompute_signals import recompute  # noqa: E402


async def signals():
    async with SessionLocal() as s:
        d = (await s.execute(select(DiscoverySignal.session_id, DiscoverySignal.signal_key, DiscoverySignal.value)
                             .order_by(DiscoverySignal.session_id, DiscoverySignal.signal_key))).all()
        p = (await s.execute(select(DeepDiagnosticSignal.session_id, DeepDiagnosticSignal.signal_key, DeepDiagnosticSignal.value)
                             .order_by(DeepDiagnosticSignal.session_id, DeepDiagnosticSignal.signal_key))).all()
    return d, p


async def main(tmp):
    await init_db()
    await ns["seed"](n_disc=6, n_deep=3)
    snap = str(Path(tmp) / "snap.json")
    info = await a.snapshot(snap)
    assert info["discovery_to_change"] > 0 and info["deep_to_change"] > 0, info

    # Confirmation is required.
    os.environ.pop("QADAM_APPLY_CONFIRM", None)
    try:
        await a.apply(snap)
        raise AssertionError("applied without confirmation")
    except a.Mismatch:
        pass
    os.environ["QADAM_APPLY_CONFIRM"] = a.CONFIRM

    # Drift in the last deep session → nothing written at all.
    before = await signals()
    async with SessionLocal() as s:
        last = (await s.execute(select(DeepDiagnosticSignal).order_by(DeepDiagnosticSignal.id.desc()).limit(1))).scalar_one()
        last_id, orig = last.id, last.value  # the ORM update below refreshes `last`
        await s.execute(update(DeepDiagnosticSignal).where(DeepDiagnosticSignal.id == last_id)
                        .values(value=orig + 0.5))
        await s.commit()
    drifted = await signals()
    try:
        await a.apply(snap)
        raise AssertionError("drift not detected")
    except a.Mismatch:
        pass
    assert await signals() == drifted, "partial write after drift"
    async with SessionLocal() as s:  # undo the drift
        await s.execute(update(DeepDiagnosticSignal).where(DeepDiagnosticSignal.id == last_id).values(value=orig))
        await s.commit()
    assert await signals() == before

    # Happy path.
    res = await a.apply(snap)
    assert res["applied"] and res["sessions_applied"] == info["discovery_to_change"] + info["deep_to_change"], res
    dry = await recompute(apply=False)
    assert dry["applied"] is False and dry["sessions_changed"] == 0 and dry["stored_values_above_10"] == 0, dry
    ver = await a.verify(snap)
    assert ver["passed"] and ver["ranking_expected_equals_actual"] and ver["unmeasured_not_weak"], ver

    # Tampering after apply is caught.
    async with SessionLocal() as s:
        row = (await s.execute(select(DiscoverySignal).where(DiscoverySignal.value.is_not(None)).limit(1))).scalar_one()
        await s.execute(update(DiscoverySignal).where(DiscoverySignal.id == row.id).values(value=row.value + 1))
        await s.commit()
    assert not (await a.verify(snap))["passed"], "tampering not caught"
    print("APPLY FLOW OK")


asyncio.run(main(sys.argv[1]))
