"""End-to-end flow for deep-link spec v2 against a real SQLite database.

Invoked by tests/test_entry_context.py in a subprocess.
"""
import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models_v2 import DiscoverySession  # noqa: E402
from backend.api.v1 import discovery as api  # noqa: E402
from bot import deeplink  # noqa: E402
from bot.handlers import start as start_handlers  # noqa: E402

WEB_USER, PLAIN_USER = 1001, 1002


def fake_verify(init_data):
    return {"id": int(init_data)}


async def bot_start(user_id, args):
    m = SimpleNamespace(from_user=SimpleNamespace(id=user_id, first_name="Test"), answer=AsyncMock())
    await start_handlers.cmd_start(m, SimpleNamespace(args=args))
    return m.answer.await_args.kwargs["reply_markup"].inline_keyboard[0][0].web_app.url


async def main():
    await init_db()
    from backend.services import age_gate
    await age_gate.submit({"id": WEB_USER, "first_name": "Test"}, True, 25)  # 18+ gate (PM 2026-10-04)
    await age_gate.submit({"id": PLAIN_USER, "first_name": "Test"}, True, 25)  # 18+ gate (PM 2026-10-04)
    api.verify_init_data = fake_verify
    deeplink.known_career_slugs = AsyncMock(return_value={"data_analytics"})
    start_handlers.WEBAPP_URL = "https://mini.example"

    # 1) Website user: /start w2-hr-al → bot_start event with state "switch".
    url = await bot_start(WEB_USER, "w2-hr-al")
    assert url == "https://mini.example/discovery?src=hr&state=switch", url

    # 2) Discovery session picks the context up server-side.
    started = await api.start_session(api.StartSessionPayload(init_data=str(WEB_USER)))
    assert started["entry_state"] == "switch", started
    async with SessionLocal() as s:
        sess = await s.get(DiscoverySession, started["session_id"])
        ctx = (sess.meta or {}).get("entry_context")
    assert ctx == {"channel": "web", "v": 2, "src": "hr", "placement": "hero", "state": "switch"}, ctx

    # 3) Completing the session keeps the context (meta is merged, not overwritten).
    questions = api.load_discovery_questions()["questions"]
    for q in questions:
        # Same answer shapes the Mini App sends (likert → "likert_<value>").
        if q["type"] == "likert":
            answer_id, value = "likert_4", 4
        else:
            answer_id, value = q["options"][0]["id"], q["options"][0].get("value", 3)
        await api.submit_answer(started["session_id"], api.AnswerPayload(
            init_data=str(WEB_USER), question_id=q["id"], answer_id=answer_id, answer_value=value,
        ))
    await api.complete_session(started["session_id"], api.StartSessionPayload(init_data=str(WEB_USER)))
    async with SessionLocal() as s:
        meta = (await s.get(DiscoverySession, started["session_id"])).meta
    assert meta["entry_context"]["state"] == "switch", meta
    assert "constraints" in meta, meta

    # 4) Plain /start user: no event, no context, behaviour unchanged.
    url = await bot_start(PLAIN_USER, None)
    assert url == "https://mini.example/discovery", url
    plain = await api.start_session(api.StartSessionPayload(init_data=str(PLAIN_USER)))
    assert plain["entry_state"] is None
    async with SessionLocal() as s:
        assert (await s.get(DiscoverySession, plain["session_id"])).meta is None

    # 5) Unknown state: source kept, state dropped.
    url = await bot_start(PLAIN_USER, "w2-hr-zz")
    assert url == "https://mini.example/discovery?src=hr", url

    print("FLOW OK", json.dumps(ctx, ensure_ascii=False))


asyncio.run(main())
