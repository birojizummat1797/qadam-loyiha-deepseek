# -*- coding: utf-8 -*-
"""QADAM Bot — WEBHOOK_BASE default qiymatni yangilash."""
from pathlib import Path
import re

BOT_MAIN = Path("qadam/bot/main.py")
code = BOT_MAIN.read_text(encoding="utf-8")

# Eski default → yangi default
code = code.replace(
    'WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "http://localhost:8080")',
    'WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "https://qadam-bot-rppk.onrender.com")'
)
code = code.replace(
    'WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "https://qadam-bot.onrender.com")',
    'WEBHOOK_BASE = os.getenv("WEBHOOK_BASE", "https://qadam-bot-rppk.onrender.com")'
)

BOT_MAIN.write_text(code, encoding="utf-8")
print("[OK] bot/main.py — WEBHOOK_BASE default yangilandi")

# Tekshirish
found = re.search(r'WEBHOOK_BASE\s*=\s*os\.getenv\([^)]+\)', code)
if found:
    print("Yangi qator:", found.group(0))