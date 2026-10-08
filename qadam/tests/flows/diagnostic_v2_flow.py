"""Diagnostic v2 API against a real SQLite database.

Invoked by tests/test_diagnostic_v2.py in a subprocess (fresh DB, isolated imports).
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import HTTPException  # noqa: E402
from sqlalchemy import select  # noqa: E402

from backend.api.v1 import profile as profile_api  # noqa: E402
from backend.api.v2 import diagnostic as api  # noqa: E402
from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models_v2 import DiagnosticV2Result  # noqa: E402


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fake_verify(init_data):
    uid = int(init_data)
    return {"id": uid, "first_name": f"N{uid}", "last_name": "", "username": f"u{uid}", "language_code": "uz"}


async def expect(coro, status, code=None):
    try:
        await coro
    except HTTPException as e:
        check(e.status_code == status, f"expected {status}, got {e.status_code} {e.detail}")
        if code:
            check(e.detail.get("code") == code, e.detail)
        return
    raise AssertionError(f"expected HTTP {status}")


async def main():
    await init_db()
    api.verify_init_data = fake_verify
    profile_api.verify_init_data = fake_verify
    uid = "7001"

    # 18+ gate is enforced on every v2 endpoint.
    await expect(api.discovery_questions(api.InitPayload(init_data=uid)), 403, "age_gate_required")
    await profile_api.gate_submit(profile_api.GatePayload(init_data=uid, consent=True, age=24))

    qs = await api.discovery_questions(api.InitPayload(init_data=uid))
    check(len(qs["questions"]) == 13, "13 discovery questions")
    check('"catalog"' not in json.dumps(qs), "catalog tags leaked")

    # Incomplete answers rejected; foreign option rejected.
    await expect(api.discovery_submit(api.DiscoverySubmit(init_data=uid, answers={})), 400)
    first = {q["id"]: q["options"][0]["id"] for q in qs["questions"]}
    bad = {**first, qs["questions"][0]["id"]: qs["questions"][1]["options"][0]["id"]}
    await expect(api.discovery_submit(api.DiscoverySubmit(init_data=uid, answers=bad)), 400)

    # Pick "software" wherever it appears → clear.
    from backend.engine import diagnostic_v2 as dv2
    answers = {}
    for q in dv2.load_data()["discovery"]["questions"]:
        opt = next((o for o in q["options"] if o["catalog"] == "software"), q["options"][-1])
        answers[q["id"]] = opt["id"]
    for q in qs["questions"][9:]:
        answers[q["id"]] = q["options"][0]["id"]
    disc = await api.discovery_submit(api.DiscoverySubmit(init_data=uid, answers=answers, meta={"duration_ms": 61000}))
    check(disc["status"] == "clear" and disc["catalogs"][0]["id"] == "software", disc)
    check("_points" not in disc, "internal counts leaked")
    check(len(disc["conditions"]) == 4, "conditions")

    deep_q = await api.deep_questions(api.DeepQuestionsPayload(init_data=uid, catalogs=["software"]))
    check(len(deep_q["a_part"]) == 11 and len(deep_q["tasks"]) == 4, "deep payload")
    check('"correct"' not in json.dumps(deep_q), "correct answers leaked")
    await expect(api.deep_questions(api.DeepQuestionsPayload(init_data=uid, catalogs=["nope"])), 400)

    cat = next(c for c in dv2.load_data()["catalogs"] if c["id"] == "software")
    deep_answers = {}
    for q in cat["questions"]:
        deep_answers[q["id"]] = next(o["id"] for o in q["options"] if o["career"] == "backend_development") \
            if any(o["career"] == "backend_development" for o in q["options"]) else q["options"][-1]["id"]
    for q in deep_q["style"] + deep_q["readiness"]:
        deep_answers[q["id"]] = q["options"][0]["id"]
    for t in cat["tasks"] + cat["lesson"]["questions"]:
        deep_answers[t["id"]] = t["correct"]
    ease = {t["id"]: "hard_interesting" for t in cat["tasks"]}
    await expect(api.deep_submit(api.DeepSubmit(init_data=uid, catalogs=["software"], answers=deep_answers,
                                                ease={"x": "easy_boring"})), 400)
    deep = await api.deep_submit(api.DeepSubmit(init_data=uid, catalogs=["software"], answers=deep_answers, ease=ease))
    check(deep["status"] == "clear" and deep["careers"][0]["id"] == "backend_development", deep)
    check(deep["evidence"]["level"] == "first_evidence", deep["evidence"])
    check("_career_picks" not in deep, "internal counts leaked")

    latest = await api.latest(init_data=uid)
    check(latest["discovery"]["result_id"] == disc["result_id"] and latest["deep"]["result_id"] == deep["result_id"], latest)

    rm = await api.roadmap("backend_development", init_data=uid)
    check(rm["version"] == "v3.0-draft" and len(rm["path"]["stages"]) == 5, "v3 roadmap")
    rm2 = await api.roadmap("frontend_development", init_data=uid)
    check(rm2["version"] == "v2.0", "live v2 roadmap wins")
    check("junior_salary_uzs" not in json.dumps(rm2), "salary leaked")
    await expect(api.roadmap("nope", init_data=uid), 404)

    # Roadmap PDF to the bot chat (founder request 2026-10-08).
    from backend.services import pdf_delivery
    sent_docs = []

    async def fake_send(user, pdf_bytes, filename, career_uz):
        sent_docs.append((user["id"], pdf_bytes[:4], filename, career_uz))
        return True

    pdf_delivery.send_pdf = fake_send
    await expect(api.roadmap_pdf("frontend_development", api.PdfPayload(init_data=uid)), 409)
    r1 = await api.roadmap_pdf("backend_development", api.PdfPayload(init_data=uid))
    check(r1 == {"ok": True, "sent_to_telegram": True, "already_sent": False}, r1)
    check(sent_docs == [(7001, b"%PDF", "QADAM-yol-xaritasi-backend_development.pdf", "Backend dasturchi")], sent_docs)
    r2 = await api.roadmap_pdf("backend_development", api.PdfPayload(init_data=uid))
    check(r2["already_sent"] is True and len(sent_docs) == 1, "automatic resend within cooldown")
    r3 = await api.roadmap_pdf("backend_development", api.PdfPayload(init_data=uid, force=True))
    check(r3["already_sent"] is True and len(sent_docs) == 1, "forced resend within one minute")

    async def failing_send(*a):
        return False

    pdf_delivery.send_pdf = failing_send
    uid2 = "7002"
    await profile_api.gate_submit(profile_api.GatePayload(init_data=uid2, consent=True, age=30))
    await api.deep_submit(api.DeepSubmit(init_data=uid2, catalogs=["software"], answers=deep_answers, ease=ease))
    r4 = await api.roadmap_pdf("backend_development", api.PdfPayload(init_data=uid2))
    check(r4 == {"ok": True, "sent_to_telegram": False, "already_sent": False}, r4)
    pdf_delivery.send_pdf = fake_send
    r5 = await api.roadmap_pdf("backend_development", api.PdfPayload(init_data=uid2))
    check(r5["sent_to_telegram"] is True, "a failed send must not block the next try")

    async with SessionLocal() as s:
        rows = (await s.execute(select(DiagnosticV2Result).where(DiagnosticV2Result.user_id == 7001))).scalars().all()
    check([r.stage for r in rows] == ["discovery", "deep"], [r.stage for r in rows])
    check(rows[0].result["_points"]["software"] == 4, "internal counts stored for analysis")

    print("DIAGNOSTIC V2 OK")


asyncio.run(main())
