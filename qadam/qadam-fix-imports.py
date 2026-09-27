# -*- coding: utf-8 -*-
"""Fix — import yo'llarini backend. prefiksi bilan to'g'rilash."""
from pathlib import Path
import re

BACKEND = Path("qadam/backend")

# Almashtirishlar
FIXES = [
    ("from engine.signals import", "from backend.engine.signals import"),
    ("from engine.ranking import", "from backend.engine.ranking import"),
    ("from engine.fit import", "from backend.engine.fit import"),
    ("from engine.readiness import", "from backend.engine.readiness import"),
    ("from engine.roadmap import", "from backend.engine.roadmap import"),
    ("from data_loader import", "from backend.data_loader import"),
    ("from models import", "from backend.models import"),
    ("from models_v2 import", "from backend.models_v2 import"),
    ("from db import", "from backend.db import"),
    ("from auth import", "from backend.auth import"),
    ("from logger import", "from backend.logger import"),
    ("import engine.", "import backend.engine."),
    ("from ai.", "from backend.ai."),
    ("from services.", "from backend.services."),
    ("from api.", "from backend.api."),
]

changed_files = []
total_replacements = 0

for f in BACKEND.rglob("*.py"):
    if "__pycache__" in str(f):
        continue
    try:
        content = f.read_text(encoding="utf-8")
    except Exception:
        continue
    original = content
    file_changes = 0

    for old, new in FIXES:
        # Faqat satr boshida bo'lganini almashtiramiz
        # va allaqachon `backend.` bilan boshlanmaganini tekshiramiz
        # Regex: satr boshi yoki bo'shliqdan keyin `from engine` va h.k.
        # Lekin `from backend.engine` allaqachon to'g'ri — uni qayta almashtirmaslik
        pattern = r'(?<!backend\.)(?<!\.)(?<=\n|^|\s)' + re.escape(old)
        # Soddaroq yondashuv: matnni nusxalab, "backend.backend." paydo bo'lmasin
        if old in content:
            # Ildiz: `from backend.` bilan boshlanmagan satrlarnigina almashtirish
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith(old) and not stripped.startswith("from backend."):
                    # `from engine.signals import` → `from backend.engine.signals import`
                    new_line = line.replace(old, new, 1)
                    new_lines.append(new_line)
                    file_changes += 1
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)

    if content != original:
        f.write_text(content, encoding="utf-8")
        changed_files.append(str(f.relative_to(BACKEND.parent)))
        total_replacements += file_changes
        print(f"  [OK] {f.relative_to(BACKEND.parent)} — {file_changes} ta almashtirish")

print()
print("=" * 60)
print(f"Jami: {total_replacements} ta almashtirish, {len(changed_files)} ta faylda")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix: backend. import prefix"')
print("  git push")
print("  Render Manual Deploy")