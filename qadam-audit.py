# -*- coding: utf-8 -*-
"""Qadam.io — Birinchi audit: hozirgi holat hisoboti."""
from pathlib import Path
import json


REPORT = []


def add_section(title):
    REPORT.append(f"\n{'=' * 60}")
    REPORT.append(f"  {title}")
    REPORT.append('=' * 60)


def add_check(name, ok, note=""):
    mark = "[OK]" if ok else "[!!]"
    line = f"  {mark} {name}"
    if note:
        line += f" — {note}"
    REPORT.append(line)


# ═══════════════════════════════════════════════════════════
# 1. LOYIHA TUZILMASI
# ═══════════════════════════════════════════════════════════
add_section("1. LOYIHA TUZILMASI")

BACKEND = Path("qadam/backend")
BOT = Path("qadam/bot")
FRONTEND = Path("qadam-miniapp")
DATA = BACKEND / "data"

add_check("Backend papka", BACKEND.exists())
add_check("Bot papka", BOT.exists())
add_check("Frontend papka", FRONTEND.exists())
add_check("Data papka", DATA.exists())

# ═══════════════════════════════════════════════════════════
# 2. BACKEND MODULLARI
# ═══════════════════════════════════════════════════════════
add_section("2. BACKEND MODULLARI")

backend_files = [
    "main.py", "db.py", "models.py", "auth.py", "logger.py",
    "data_loader.py", "pdf_report.py",
    "api/diagnostic.py", "api/payments.py",
    "engine/signals.py", "engine/fit.py", "engine/readiness.py",
    "engine/ranking.py", "engine/roadmap.py",
    "ai/personalizer.py",
    "security/rate_limit.py",
]
for f in backend_files:
    p = BACKEND / f
    add_check(f, p.exists())

# ═══════════════════════════════════════════════════════════
# 3. DATA FAYLLAR
# ═══════════════════════════════════════════════════════════
add_section("3. DATA FAYLLAR")

data_files = [
    "taxonomy_v1.json",
    "questions_v1.json",
    "signals_v1.json",
    "roadmap_kb_v2.json",
    "roadmap_kb_v1.json",
]
for f in data_files:
    p = DATA / f
    if p.exists():
        size = p.stat().st_size
        add_check(f, True, f"{size:,} bayt")
    else:
        add_check(f, False, "TOPILMADI")

# Taxonomy soni
try:
    tax = json.loads((DATA / "taxonomy_v1.json").read_text(encoding="utf-8"))
    total_careers = sum(len(c["careers"]) for c in tax["clusters"].values())
    add_check(f"Taxonomy jami career'lar", True, f"{total_careers} ta")
except Exception as e:
    add_check("Taxonomy o'qish", False, str(e)[:60])

# Roadmap KB v2 da qaysi career'lar
try:
    kb = json.loads((DATA / "roadmap_kb_v2.json").read_text(encoding="utf-8"))
    careers_with_roadmap = list(kb["careers"].keys())
    add_check(f"Roadmap'li career'lar", True, f"{len(careers_with_roadmap)} ta")
    for c in careers_with_roadmap:
        REPORT.append(f"      • {c}")
except Exception as e:
    add_check("Roadmap KB v2 o'qish", False, str(e)[:60])

# ═══════════════════════════════════════════════════════════
# 4. FRONTEND SAHIFALAR
# ═══════════════════════════════════════════════════════════
add_section("4. FRONTEND SAHIFALAR")

frontend_pages = [
    "app/layout.tsx", "app/page.tsx", "app/globals.css",
    "app/stage1/page.tsx", "app/stage2/page.tsx",
    "app/teaser/page.tsx", "app/report/[id]/page.tsx",
    "components/RoadmapView.tsx", "components/PdfDownloader.tsx",
    "components/CloseButton.tsx", "components/TmaProvider.tsx",
    "lib/api.ts", "lib/store.ts", "lib/types.ts",
]
for f in frontend_pages:
    p = FRONTEND / f
    add_check(f, p.exists())

# ═══════════════════════════════════════════════════════════
# 5. BOT HANDLERLAR
# ═══════════════════════════════════════════════════════════
add_section("5. BOT HANDLERLAR")

bot_files = [
    "main.py", "handlers/start.py", "handlers/payment.py",
    "handlers/report.py",
]
for f in bot_files:
    p = BOT / f
    add_check(f, p.exists())


# ═══════════════════════════════════════════════════════════
# 6. RAQAMLAR — HOZIRGI HOLAT
# ═══════════════════════════════════════════════════════════
add_section("6. RAQAMLAR — hozirgi holat")

# Signals
try:
    sig = json.loads((DATA / "signals_v1.json").read_text(encoding="utf-8"))
    REPORT.append(f"  Signals: {len(sig['signals'])} ta")
except Exception:
    pass

# Questions
try:
    q = json.loads((DATA / "questions_v1.json").read_text(encoding="utf-8"))
    stage1_count = len(q["stage_1"]["questions"])
    stage2_count = sum(len(d["questions"]) for d in q["stage_2"]["dimensions"].values())
    REPORT.append(f"  Stage 1 savollar: {stage1_count} ta")
    REPORT.append(f"  Stage 2 savollar: {stage2_count} ta")
except Exception:
    pass

# Taxonomy prerequisites
try:
    tax = json.loads((DATA / "taxonomy_v1.json").read_text(encoding="utf-8"))
    with_prereq = 0
    with_signals = 0
    for cluster in tax["clusters"].values():
        for career in cluster["careers"].values():
            if career.get("prerequisites"):
                with_prereq += 1
            if career.get("signals"):
                with_signals += 1
    REPORT.append(f"  Prerequisites bor career'lar: {with_prereq}")
    REPORT.append(f"  Signals bor career'lar: {with_signals}")
except Exception:
    pass


# ═══════════════════════════════════════════════════════════
# 7. RAQAMLAR — MUAMMOLAR
# ═══════════════════════════════════════════════════════════
add_section("7. RAQAMLAR — muammolar (asoslash kerak)")

issues = [
    "[!!] Maosh raqamlari — HH.uz'dan tekshirilmagan",
    "[!!] Fit % — signal vaznlari kalibrlanmagan",
    "[!!] Readiness % — prerequisites real emas",
    "[!!] O'rganish muddati — real feedbacksiz",
    "[!!] 'Ishga tayyorlanish' mezonlari — umumiy",
    "[!!] Calendar — real o'quv rejasiz",
    "[!!] Resurslar — sifat auditisiz",
]
for i in issues:
    REPORT.append(f"  {i}")


# ═══════════════════════════════════════════════════════════
# 8. TAKLIF: KEYINGI QADAMLAR
# ═══════════════════════════════════════════════════════════
add_section("8. KEYINGI QADAMLAR")

next_steps = [
    "",
    "BOSQICH 1: AUDIT (bugun)",
    "  1.1. Backend/monitoring integratsiyasi (Sentry?)",
    "  1.2. Xatolar ro'yxati va prioritet",
    "  1.3. UX audit (mobil + desktop)",
    "",
    "BOSQICH 2: RAQAMLAR ASOSLARI (3-5 kun)",
    "  2.1. Maosh ma'lumotlari — HH.uz scraping",
    "  2.2. Fit % — signal vaznlar kalibrlash",
    "  2.3. Readiness — real prerequisites",
    "  2.4. Muddatlar — real feedback",
    "  2.5. Calendar — real o'quv reja",
    "",
    "BOSQICH 3: TEST REJIM (2-3 kun)",
    "  3.1. Admin panel (statistika)",
    "  3.2. Feedback tizimi (har report'dan keyin)",
    "  3.3. Analytics (eventlar)",
    "  3.4. Onboarding (yangi user uchun)",
    "  3.5. Rate limiting",
    "",
    "BOSQICH 4: KATTA AUDITORIYA (2-3 kun)",
    "  4.1. Landing page (qadam.io domeni)",
    "  4.2. Telegram kanali",
    "  4.3. Marketing materiallar",
    "  4.4. Referral tizim",
    "",
]
for s in next_steps:
    REPORT.append(s)


# ═══════════════════════════════════════════════════════════
# Natija
# ═══════════════════════════════════════════════════════════
report_text = "\n".join(REPORT)
print(report_text)

# Faylga saqlash
out = Path("qadam_audit.txt")
out.write_text(report_text, encoding="utf-8")
print()
print(f"Natija saqlandi: {out}")