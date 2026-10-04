"""18+ age gate and consent against a real SQLite database (PM decision 2026-10-04, P0).

Invoked by tests/test_age_gate.py in a subprocess (fresh DB, isolated imports).
"""
import asyncio
import io
import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import HTTPException, UploadFile  # noqa: E402
from sqlalchemy import select  # noqa: E402

from backend.api import payments  # noqa: E402
from backend.api.v1 import deep_diagnostic as dd_api  # noqa: E402
from backend.api.v1 import discovery as disc_api  # noqa: E402
from backend.api.v1 import profile as profile_api  # noqa: E402
from backend.data_loader import load_discovery_questions  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Event, User  # noqa: E402
from backend.models_v2 import Profile  # noqa: E402
from backend.services import age_gate  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fake_verify(init_data):
    uid = int(init_data)
    return {"id": uid, "first_name": f"Name{uid}", "last_name": "L", "username": f"u{uid}", "language_code": "uz"}


async def expect(coro, status, code=None):
    try:
        await coro
    except HTTPException as e:
        check(e.status_code == status, f"expected {status}, got {e.status_code} {e.detail}")
        if code:
            check(e.detail.get("code") == code, e.detail)
        return
    raise AssertionError(f"expected HTTP {status}")


async def gate(uid, age, consent=True):
    return await profile_api.gate_submit(profile_api.GatePayload(init_data=str(uid), consent=consent, age=age))


async def status(uid):
    return await profile_api.gate_status(init_data=str(uid))


async def blocked_everywhere(uid):
    await expect(disc_api.start_session(disc_api.StartSessionPayload(init_data=str(uid))), 403, "age_gate_required")
    await expect(dd_api.start(dd_api.StartPayload(init_data=str(uid))), 403, "age_gate_required")
    await expect(payments.manual_upload_v2(str(uid), None, UploadFile(file=io.BytesIO(PNG), filename="s.png")),
                 403, "age_gate_required")


async def run_discovery(uid):
    started = await disc_api.start_session(disc_api.StartSessionPayload(init_data=str(uid)))
    sid = started["session_id"]
    for q in load_discovery_questions()["questions"]:
        if q["type"] == "likert":
            aid, val = "likert_4", 4
        else:
            aid, val = q["options"][0]["id"], 3
        await disc_api.submit_answer(sid, disc_api.AnswerPayload(
            init_data=str(uid), question_id=q["id"], answer_id=aid, answer_value=val))
    return await disc_api.complete_session(sid, disc_api.StartSessionPayload(init_data=str(uid)))


def strip_ids(obj):
    if isinstance(obj, dict):
        return {k: strip_ids(v) for k, v in obj.items() if k not in ("session_id", "id", "created_at", "completed_at")}
    if isinstance(obj, list):
        return [strip_ids(v) for v in obj]
    return obj


async def main():
    await init_db()
    for m in (disc_api, dd_api, payments, profile_api):
        m.verify_init_data = fake_verify
    payments._send_to_admin = AsyncMock()

    # 1) No gate yet → every entry point refuses.
    check(await status(5001) == {"status": "required"}, "status before gate")
    await blocked_everywhere(5001)

    # 2) Consent is mandatory; implausible age is a typo, not a decision.
    await expect(gate(5001, 25, consent=False), 400, "consent_required")
    await expect(gate(5001, 3), 400, "age_invalid")

    # 3) Under 18 → nothing stored; earlier /start event removed; only an anonymous counter.
    async with SessionLocal() as s:
        s.add(Event(user_id=5002, event_name="bot_start", payload={}))
        await s.commit()
    check(await gate(5002, 17) == {"status": "under_age"}, "17 accepted")
    async with SessionLocal() as s:
        check(await s.get(Profile, 5002) is None, "minor profile stored")
        check(await s.get(User, 5002) is None, "minor name stored")
        mine = (await s.execute(select(Event).where(Event.user_id == 5002))).scalars().all()
        check(mine == [], "minor events kept")
        anon = (await s.execute(select(Event).where(Event.event_name == "age_gate_blocked"))).scalars().all()
        check(len(anon) == 1 and anon[0].user_id is None and anon[0].payload == {"band": "under_18"}, "counter")
    check(await status(5002) == {"status": "required"}, "minor passed")
    await blocked_everywhere(5002)

    # 4) Exactly 18 → accepted; name and consent stored.
    check(await gate(5003, 18) == {"status": "ok", "age_warning": False}, "18 refused")
    async with SessionLocal() as s:
        u, p = await s.get(User, 5003), await s.get(Profile, 5003)
    check(u.first_name == "Name5003" and u.username == "u5003", "telegram name not stored")
    check(p.age == 18 and p.meta["consent_version"] == age_gate.CONSENT_VERSION and p.meta["consented_at"], "consent")
    check(await status(5003) == {"status": "ok", "age_warning": False}, "status 18")

    # 5) 35 → no warning; 36 → warning but allowed (never blocked).
    check((await gate(5004, 35))["age_warning"] is False, "35 warned")
    check(await gate(5005, 36) == {"status": "ok", "age_warning": True}, "36 not warned")
    check(await status(5005) == {"status": "ok", "age_warning": True}, "status 36")

    # 6) The generic profile endpoint cannot set age (no bypass of consent/gate).
    try:
        await profile_api.upsert_profile(profile_api.ProfilePayload(init_data="5006", age=30))
    except Exception:
        pass
    check(await status(5006) == {"status": "required"}, "profile endpoint bypassed the gate")

    # 7) Outdated consent version → asked again.
    async with SessionLocal() as s:
        p = await s.get(Profile, 5003)
        p.meta = {**p.meta, "consent_version": "old"}
        await s.commit()
    check(await status(5003) == {"status": "required"}, "old consent accepted")
    await gate(5003, 18)

    # 8) Age never changes the result: same answers at 20 and 60 → identical preliminary result.
    await gate(5007, 20)
    await gate(5008, 60)
    a, b = strip_ids(await run_discovery(5007)), strip_ids(await run_discovery(5008))
    check(a == b, "age changed the diagnostic result")

    print("AGE GATE OK")


asyncio.run(main())
