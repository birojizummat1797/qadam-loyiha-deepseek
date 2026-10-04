"""Deep diagnostic as a free beta (PM decision 2026-10-04): 18+ gate only, no payment taken."""
import asyncio
import io
import sys
from pathlib import Path
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import HTTPException, UploadFile  # noqa: E402

from backend.api import payments  # noqa: E402
from backend.api.v1 import career_intelligence as ci_api  # noqa: E402
from backend.api.v1 import deep_diagnostic as dd_api  # noqa: E402
from backend.db import init_db  # noqa: E402
from backend.services import age_gate, entitlement_service  # noqa: E402
from backend.services import manual_payment_service as mps  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fake_verify(init_data):
    return {"id": int(init_data), "first_name": "T"}


async def main():
    await init_db()
    check(entitlement_service.DEEP_DIAGNOSTIC_FREE_BETA is True, "free beta switch is off in code")
    for m in (payments, dd_api, ci_api):
        m.verify_init_data = fake_verify
    payments._send_to_admin = AsyncMock()

    # Without the 18+ gate: still refused, beta or not.
    try:
        await dd_api.start(dd_api.StartPayload(init_data="6001"))
        raise AssertionError("deep diagnostic started without the gate")
    except HTTPException as e:
        check(e.status_code == 403, e.detail)

    # Adult, no payment, no entitlement → deep diagnostic starts.
    await age_gate.submit({"id": 6001, "first_name": "T"}, True, 22)
    r = await dd_api.start(dd_api.StartPayload(init_data="6001"))
    check(r.get("session_id"), "deep diagnostic did not start in free beta")

    # No money is taken during the beta.
    try:
        await payments.manual_upload_v2("6001", None, UploadFile(file=io.BytesIO(PNG), filename="s.png"))
        raise AssertionError("payment accepted during free beta")
    except HTTPException as e:
        check(e.status_code == 409 and e.detail["code"] == "free_beta", e.detail)
    payments._send_to_admin.assert_not_awaited()
    check(await mps.my_status(6001) == {"state": "free_beta"}, "premium page state")
    print("FREE BETA OK")


asyncio.run(main())
