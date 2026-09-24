# -*- coding: utf-8 -*-
"""QADAM -> Qadam.io rebranding + support almashtirish."""
from pathlib import Path
import re

# ═══════════════════════════════════════════════════════════
# O'zgarish qoidalari
# ═══════════════════════════════════════════════════════════
# MUHIM: tartib muhim! Uzundan boshlash kerak
REPLACEMENTS = [
    # Support
    ("@qadam_support", "@ulugbek_aliboyev"),

    # Brand nomlar
    ("QADAM jamoasi", "Qadam.io jamoasi"),
    ("QADAM loyihasida", "Qadam.io loyihasida"),
    ("QADAM loyihasi", "Qadam.io loyihasi"),
    ("QADAM Premium Personal Diagnostic", "Qadam.io Premium Personal Diagnostic"),
    ("QADAM Premium tahlil", "Qadam.io Premium tahlil"),
    ("QADAM diagnostikasi", "Qadam.io diagnostikasi"),
    ("QADAM diagnostikasidan", "Qadam.io diagnostikasidan"),
    ("QADAM qanday ishlaydi", "Qadam.io qanday ishlaydi"),
    ("QADAM yordam", "Qadam.io yordam"),
    ("QADAM Admin", "Qadam.io Admin"),
    ("QADAM loyihasi", "Qadam.io loyihasi"),
    ("QADAM loyihasiga", "Qadam.io loyihasiga"),
    ("QADAM — Career", "Qadam.io — Career"),
    ("QADAM — Halol", "Qadam.io — Halol"),
    ("QADAM’ning", "Qadam.io’ning"),
    ("QADAM'ning", "Qadam.io'ning"),
    # Bot title/description
    ('text="QADAM"', 'text="Qadam.io"'),
    ('"QADAM"', '"Qadam.io"'),
    # Menu button
    ("menu_button=MenuButtonWebApp(text=\"QADAM\"", "menu_button=MenuButtonWebApp(text=\"Qadam.io\""),
    # Title metadata
    ('title: "QADAM - Kasb yonaltiruvchi tahlil"', 'title: "Qadam.io - Kasb yonaltiruvchi tahlil"'),
    ('"QADAM - Kasb yonaltiruvchi tahlil"', '"Qadam.io - Kasb yonaltiruvchi tahlil"'),
    # Service name
    ('"service": "qadam-backend"', '"service": "qadam-io-backend"'),
    ('"service": "qadam-bot"', '"service": "qadam-io-bot"'),
    # README
    ("# QADAM", "# Qadam.io"),
    # Title in PDF
    ("QADAM — Halol tahlil, manipulyatsiyasiz", "Qadam.io — Halol tahlil, manipulyatsiyasiz"),
    ("QADAM — Kasb yonaltiruvchi tahlil", "Qadam.io — Kasb yonaltiruvchi tahlil"),
]


# ═══════════════════════════════════════════════════════════
# Fayllar ro'yxati
# ═══════════════════════════════════════════════════════════
FILES_TO_UPDATE = [
    # Backend
    "qadam/bot/handlers/start.py",
    "qadam/bot/handlers/payment.py",
    "qadam/bot/main.py",
    "qadam/backend/api/diagnostic.py",
    "qadam/backend/api/payments.py",
    "qadam/backend/pdf_report.py",
    "qadam/backend/ai/personalizer.py",
    "qadam/backend/logger.py",
    "qadam/backend/main.py",
    # Frontend
    "qadam-miniapp/app/layout.tsx",
    "qadam-miniapp/app/page.tsx",
    "qadam-miniapp/app/report/[id]/page.tsx",
    "qadam-miniapp/components/RoadmapView.tsx",
    "qadam-miniapp/components/PdfDownloader.tsx",
    "qadam-miniapp/components/TmaProvider.tsx",
    # Docs
    "README.md",
]


# ═══════════════════════════════════════════════════════════
# Almashtirish
# ═══════════════════════════════════════════════════════════
total_changes = 0
updated_files = []

for file_path in FILES_TO_UPDATE:
    p = Path(file_path)
    if not p.exists():
        print(f"  [SKIP] {file_path} — topilmadi")
        continue

    content = p.read_text(encoding="utf-8")
    original = content
    file_changes = 0

    for old, new in REPLACEMENTS:
        count = content.count(old)
        if count > 0:
            content = content.replace(old, new)
            file_changes += count

    if content != original:
        p.write_text(content, encoding="utf-8")
        total_changes += file_changes
        updated_files.append(file_path)
        print(f"  [OK] {file_path} — {file_changes} ta almashtirish")
    else:
        print(f"  [--] {file_path} — o'zgarish yo'q")


print()
print("=" * 60)
print(f"Jami: {total_changes} ta almashtirish, {len(updated_files)} ta faylda")
print("=" * 60)
print()
print("YANGI BRAND: Qadam.io")
print("YANGI SUPPORT: @ulugbek_aliboyev")
print()
print("Keyingi qadam:")
print("  git add -A")
print('  git commit -m "Rebrand: QADAM -> Qadam.io + support @ulugbek_aliboyev"')
print("  git push")
print()
print("⚠️ ESKIZ/UZ domen: kelajakda qadam.io domeniga ulash kerak")