# -*- coding: utf-8 -*-
"""Fix v6 — extract_evidence KeyError: 'id'."""
from pathlib import Path

DDS = Path("qadam/backend/services/deep_diagnostic_service.py")
d = DDS.read_text(encoding="utf-8")

# Xato: qmap.get(a["id"]) or qmap.get(a["question_id"])
# To'g'ri: faqat question_id (id mavjud emas)

old = '''        q = qmap.get(a["id"]) or qmap.get(a["question_id"])'''
new = '''        q = qmap.get(a.get("question_id") or a.get("id", ""))'''

if old in d:
    d = d.replace(old, new)
    DDS.write_text(d, encoding="utf-8")
    print("[OK] extract_evidence — 'id' xatosi tuzatildi")
else:
    print("[!!] Pattern topilmadi. Faylni qo'lda tuzatish kerak:")
    print("    qadam/backend/services/deep_diagnostic_service.py")
    print("    ~68 qator: qmap.get(a['id']) → qmap.get(a.get('question_id'))")

print()
print("=" * 60)
print("Fix v6 — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix: extract_evidence KeyError id"')
print("  git push")
print("  Render Manual Deploy (backend, clear cache)")