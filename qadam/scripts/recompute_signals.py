"""Recompute stored signals of completed sessions with the current formula.

Legacy strategy (PM gate 2026-10-03): signals saved before the weighted-mean fix
can exceed 10. Answers are stored, so signals are recomputed from them
deterministically — no guessing, nothing invented.

    python scripts/recompute_signals.py            # dry run: report only (default)
    python scripts/recompute_signals.py --apply    # write, one transaction per session

Run against production only after a DB backup. v0 TestResult rows are not
recomputed (that engine is retired); they are served read-only and filtered.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select  # noqa: E402

from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.db import SessionLocal  # noqa: E402
from backend.models_v2 import (  # noqa: E402
    DeepDiagnosticAnswer, DeepDiagnosticSession, DeepDiagnosticSignal,
    DiscoveryAnswer, DiscoverySession, DiscoverySignal,
)
from backend.services.deep_diagnostic_service import compute_signals, flatten_questions  # noqa: E402
from backend.services.discovery_service import compute_signals_from_discovery  # noqa: E402

EPS = 0.005


def _changed(old: dict, new: dict) -> list[str]:
    keys = set(old) | {k for k, v in new.items() if v["value"] is not None}
    out = []
    for k in sorted(keys):
        a = (old.get(k) or {}).get("value")
        b = (new.get(k) or {}).get("value")
        if (a is None) != (b is None) or (a is not None and abs(a - b) > EPS):
            out.append(k)
    return out


async def recompute(apply: bool) -> dict:
    disc_q = load_discovery_questions()["questions"]
    deep_q = flatten_questions(load_deep_diagnostic())
    stats = {"discovery_sessions": 0, "deep_sessions": 0, "sessions_changed": 0,
             "signals_changed": 0, "stored_values_above_10": 0, "applied": apply}

    async with SessionLocal() as s:
        disc_ids = (await s.execute(
            select(DiscoverySession.id).where(DiscoverySession.status == "completed")
        )).scalars().all()
        deep_ids = (await s.execute(
            select(DeepDiagnosticSession.id).where(DeepDiagnosticSession.status == "completed")
        )).scalars().all()

    for sid in disc_ids:
        stats["discovery_sessions"] += 1
        async with SessionLocal() as s:
            answers = (await s.execute(select(DiscoveryAnswer).where(DiscoveryAnswer.session_id == sid))).scalars().all()
            rows = (await s.execute(select(DiscoverySignal).where(DiscoverySignal.session_id == sid))).scalars().all()
            old = {r.signal_key: {"value": r.value} for r in rows}
            stats["stored_values_above_10"] += sum(1 for r in rows if r.value is not None and r.value > 10)
            new = compute_signals_from_discovery(
                [{"question_id": a.question_id, "answer_id": a.answer_id, "answer_value": a.answer_value} for a in answers],
                disc_q,
            )
            changed = _changed(old, new)
            if changed:
                stats["sessions_changed"] += 1
                stats["signals_changed"] += len(changed)
                if apply:
                    await s.execute(delete(DiscoverySignal).where(DiscoverySignal.session_id == sid))
                    for k, v in new.items():  # discovery keeps unmeasured rows too
                        s.add(DiscoverySignal(session_id=sid, signal_key=k, value=v["value"], trust=v["trust"],
                                              evidence_state=v["evidence_state"], coverage=v["coverage"]))
                    await s.commit()

    for sid in deep_ids:
        stats["deep_sessions"] += 1
        async with SessionLocal() as s:
            answers = (await s.execute(select(DeepDiagnosticAnswer).where(DeepDiagnosticAnswer.session_id == sid))).scalars().all()
            rows = (await s.execute(select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == sid))).scalars().all()
            old = {r.signal_key: {"value": r.value} for r in rows}
            stats["stored_values_above_10"] += sum(1 for r in rows if r.value is not None and r.value > 10)
            new = compute_signals([{"question_id": a.question_id, "answer_value": a.answer_value} for a in answers], deep_q)
            changed = _changed(old, new)
            if changed:
                stats["sessions_changed"] += 1
                stats["signals_changed"] += len(changed)
                if apply:
                    await s.execute(delete(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == sid))
                    for k, v in new.items():  # deep keeps measured rows only (as on completion)
                        if v["evidence_state"] != "unmeasured":
                            s.add(DeepDiagnosticSignal(session_id=sid, signal_key=k, value=v["value"], trust=v["trust"],
                                                       evidence_state=v["evidence_state"], coverage=v["coverage"]))
                    await s.commit()
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = parser.parse_args()
    if args.apply and os.getenv("QADAM_DB_READ_ONLY") == "1":
        sys.exit("refused: --apply in a read-only run")
    print(json.dumps(asyncio.run(recompute(args.apply)), indent=2))


if __name__ == "__main__":
    main()
