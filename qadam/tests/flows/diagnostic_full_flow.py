"""P0-7 full-flow regression against a real SQLite database.

Bot /start → Mini App discovery (13) → preliminary result → premium → deep
diagnostic (18) → career intelligence → roadmap → PDF generator.
Invoked by tests/test_full_flow.py in a subprocess (fresh DB, isolated imports).
"""
import asyncio
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.db import init_db  # noqa: E402
from backend.api.v1 import career_intelligence as ci_api  # noqa: E402
from backend.api.v1 import deep_diagnostic as dd_api  # noqa: E402
from backend.api.v1 import discovery as disc_api  # noqa: E402
from backend.api.v1 import roadmap as rm_api  # noqa: E402
from backend.data_loader import load_deep_diagnostic, load_discovery_questions  # noqa: E402
from backend.engine.roadmap import build_full_report  # noqa: E402
from backend.pdf_report import _build_career_html, generate_pdf  # noqa: E402
from backend.services.deep_diagnostic_service import flatten_questions  # noqa: E402
from backend.services.entitlement_service import grant_entitlement  # noqa: E402
from bot.handlers import start as start_handlers  # noqa: E402

USER = 2001
INIT = str(USER)
# Real context: smartphone only, A1-A2 English, 1 hour a day.
CONTEXT_ANSWERS = {"DISC_Q11": "DISC_Q11_A02", "DISC_Q12": "DISC_Q12_A02", "DISC_Q13": "DISC_Q13_A02"}
EXPECTED_CONTEXT = {"time": "1h", "device": "smartphone_only", "english": "a2"}
HARDCODED = {"time": "2_3h", "device": "laptop", "english": "b1"}


def fake_verify(init_data):
    return {"id": int(init_data), "first_name": "Test"}


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def check_signals(signals, where):
    for key, s in signals.items():
        if s.get("value") is not None:
            check(0 <= s["value"] <= 10, f"{where}: {key}={s['value']} outside [0,10]")


def check_career(item, where):
    if item.get("fit") is not None:
        check(0 <= item["fit"] <= 100, f"{where}: fit {item['fit']} outside [0,100]")
    check(item.get("evidence_level") in {"enough", "partial", "insufficient"}, f"{where}: evidence_level {item}")
    check(item.get("context_status") in {"clear", "barriers", "unknown"}, f"{where}: context_status {item}")


async def main():
    await init_db()
    for module in (disc_api, dd_api, ci_api, rm_api):
        module.verify_init_data = fake_verify

    # 1) Bot /start: welcome text makes no fit claims and opens the Mini App.
    m = SimpleNamespace(from_user=SimpleNamespace(id=USER, first_name="Test"), answer=AsyncMock())
    await start_handlers.cmd_start(m)
    welcome = m.answer.await_args.args[0]
    check("Sizga mos" not in welcome and "%" not in welcome, f"welcome text: {welcome}")

    # 2) Discovery: 13 questions, answered the way the Mini App sends them.
    started = await disc_api.start_session(disc_api.StartSessionPayload(init_data=INIT))
    sid = started["session_id"]
    for q in load_discovery_questions()["questions"]:
        if q["type"] == "likert":
            answer_id, value = "likert_5", 5
        else:
            chosen = CONTEXT_ANSWERS.get(q["id"])
            opt = next((o for o in q["options"] if o["id"] == chosen), q["options"][0])
            answer_id, value = opt["id"], opt.get("value", 3)
        await disc_api.submit_answer(sid, disc_api.AnswerPayload(
            init_data=INIT, question_id=q["id"], answer_id=answer_id, answer_value=value,
        ))
    done = await disc_api.complete_session(sid, disc_api.StartSessionPayload(init_data=INIT))
    insight = done["insight"]
    check_signals(done.get("signals", {}), "discovery")
    for p in insight["pathways"]:
        check_career(p, "preliminary")
        check(p["readiness"] is not None, "preliminary readiness should use the real context")

    # 3) Premium + deep diagnostic (18), all answers at the maximum (old bug: values up to 15).
    await grant_entitlement(USER, "premium_career_intelligence", source="admin")
    dd = await dd_api.start(dd_api.StartPayload(init_data=INIT, discovery_session_id=sid))
    for q in flatten_questions(load_deep_diagnostic()):
        await dd_api.submit_answer(dd["session_id"], dd_api.AnswerPayload(
            init_data=INIT, question_id=q["id"], answer_value=5,
        ))
    deep = await dd_api.complete(dd["session_id"], dd_api.StartPayload(init_data=INIT))
    check(deep["constraints"] == EXPECTED_CONTEXT, f"deep used {deep['constraints']}, not the user's context")
    check(deep["constraints"] != HARDCODED, "deep diagnostic still uses hard-coded conditions")
    check_signals(deep["signals"], "deep")
    for item in deep["ranked"]:
        check_career(item, "deep ranked")

    # 4) Career intelligence (what the founder saw: 'SMM 100% / 70%').
    ci = await ci_api.get_career_intelligence(discovery_session_id=sid, init_data=INIT)
    check(ci["constraints"] == EXPECTED_CONTEXT, f"career intelligence used {ci['constraints']}")
    check_signals(ci["signals"], "career intelligence")
    check(ci["ranked"], "career intelligence returned no careers")
    for item in ci["ranked"]:
        check_career(item, "career intelligence")

    # 5) Roadmap for the first career.
    slug = ci["ranked"][0]["career_id"]
    rm = await rm_api.get_roadmap(slug, session_id=dd["session_id"], init_data=INIT)
    check(rm["evidence_level"] in {"enough", "partial", "insufficient"}, f"roadmap evidence: {rm}")
    if rm["fit"] is not None:
        check(0 <= rm["fit"] <= 100, f"roadmap fit {rm['fit']}")

    # 6) PDF generator on the same ranking: real PDF bytes, no score percentages.
    taxonomy = await ci_api.load_taxonomy_from_db()
    report = build_full_report(ci["ranked"], ci["constraints"], taxonomy, ci["signals"])
    for idx, c in enumerate(report["careers"], 1):
        html = _build_career_html({**c, "_idx": idx})
        header = html.split("</div>", 1)[0]
        check("%" not in re.sub(r'width="\d+%"', "", header), f"PDF header has a percentage: {header}")
        check("FIT" not in html and "Ready:" not in html, "PDF still shows FIT/Ready")
    pdf = generate_pdf({"id": 1, "profile": {}, "roadmap": report, "ai": None, "created_at": ""})
    check(pdf[:4] == b"%PDF", "generate_pdf did not return a PDF")

    print("FULL FLOW OK", json.dumps({
        "careers": [c["career_id"] for c in ci["ranked"]],
        "evidence": [c["evidence_level"] for c in ci["ranked"]],
        "context": ci["constraints"],
    }, ensure_ascii=False))


asyncio.run(main())
