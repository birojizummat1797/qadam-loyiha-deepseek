# -*- coding: utf-8 -*-
"""QADAM v5 — Print CSS to'liq tuzatish (ranglar + kenglik + kontrast)."""
from pathlib import Path
import re

# ═══════════════════════════════════════════════════════════
# 1. GLOBALS.CSS — Print uchun 3 ta kritik fix
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

# Eski print blokni olib tashlash
css = re.sub(
    r'/\* ═+\s*PRINT.*?\*/.*?@media print \{.*?\n\}',
    '',
    css,
    flags=re.DOTALL,
)
css = re.sub(r'@media print \{.*?\n\}\s*$', '', css, flags=re.DOTALL)

PRINT_CSS = '''

/* ═══════════════════════════════════════════════════════════
   PRINT / PDF — Ranglarni saqlash + A4 full width
   ═══════════════════════════════════════════════════════════ */
@media print {
  /* ─── 1. RANGLARNI SAQLASH ─── */
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }

  /* ─── 2. CSS VARIABLES — Light mode'ga o'tkazish ─── */
  :root {
    --tg-bg: #ffffff !important;
    --tg-text: #0a0a0f !important;
    --tg-hint: #6b7280 !important;
    --tg-link: #4f46e5 !important;
    --tg-button: #6366f1 !important;
    --tg-button-text: #ffffff !important;
    --tg-secondary-bg: #f9fafb !important;
  }

  /* ─── 3. A4 FULL WIDTH ─── */
  html, body {
    background: #ffffff !important;
    color: #0a0a0f !important;
    font-size: 10.5pt;
    line-height: 1.5;
  }

  @page {
    size: A4;
    margin: 10mm 12mm;
  }

  /* Container — full width */
  main {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* ─── 4. ANIMATSIYALAR — statik ─── */
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    transform: none !important;
    opacity: 1 !important;
    box-shadow: none !important;
    text-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
  }

  /* ─── 5. KARTALAR — ranglarni saqlash ─── */
  .card,
  [class*="rounded-2xl"],
  [class*="rounded-xl"] {
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    padding: 10pt 12pt !important;
    margin-bottom: 6pt !important;
    /* Uzluksiz oqim — bo'linmalarni buzmaslik */
    break-inside: auto;
    page-break-inside: auto;
  }

  /* Gradient kartalar — och rang bilan */
  [class*="from-indigo"] { background: #eef2ff !important; }
  [class*="from-amber"] { background: #fffbeb !important; }
  [class*="from-emerald"] { background: #ecfdf5 !important; }
  [class*="from-slate"] { background: #f8fafc !important; }

  /* ─── 6. GRADIENT MATN ─── */
  .gradient-text {
    background: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    -webkit-text-fill-color: #6366f1 !important;
    color: #6366f1 !important;
    font-weight: 700;
  }

  /* ─── 7. ACCORDION — HAMMASI OCHIQ ─── */
  [data-accordion-content],
  [data-calendar-body] {
    display: block !important;
    max-height: none !important;
    height: auto !important;
    overflow: visible !important;
    opacity: 1 !important;
    margin-top: 8pt !important;
  }

  /* Chevron — yashirish */
  [data-chevron] { display: none !important; }

  /* ─── 8. PROGRESS BAR ─── */
  [style*="width"] {
    /* Bar ranglari saqlanadi */
    -webkit-print-color-adjust: exact !important;
  }

  /* ─── 9. SVG PROGRESS RING ─── */
  svg {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  /* ─── 10. TUGMALAR — YASHIRISH ─── */
  button.btn-primary,
  button[onclick*="print"] {
    display: none !important;
  }

  /* ─── 11. SARLAVHALAR — birga ─── */
  h1 { font-size: 22pt; margin: 0 0 4pt; }
  h2 { font-size: 16pt; margin: 12pt 0 6pt; page-break-after: avoid; }
  h3 { font-size: 13pt; margin: 8pt 0 4pt; page-break-after: avoid; }
  h4 { font-size: 11pt; margin: 6pt 0 3pt; page-break-after: avoid; }

  /* ─── 12. RO'YXATLAR ─── */
  ul, ol { margin: 4pt 0; padding-left: 14pt; }
  li { margin: 2pt 0; }

  /* ─── 13. LINKLAR ─── */
  a {
    color: #4f46e5 !important;
    text-decoration: underline;
    text-decoration-color: #a5b4fc;
  }

  /* ─── 14. SVG IKONKALAR ─── */
  svg { color: inherit; }

  /* ─── 15. TIMELINE ─── */
  [class*="absolute"][class*="left-"] {
    /* Timeline node — ko'rinsin */
    -webkit-print-color-adjust: exact !important;
  }

  /* ─── 16. RANGLI BADGE va PILL ─── */
  [class*="bg-indigo"] { background: #e0e7ff !important; color: #3730a3 !important; }
  [class*="bg-purple"] { background: #f3e8ff !important; color: #6b21a8 !important; }
  [class*="bg-emerald"] { background: #d1fae5 !important; color: #065f46 !important; }
  [class*="bg-amber"] { background: #fef3c7 !important; color: #92400e !important; }
  [class*="bg-blue"] { background: #dbeafe !important; color: #1e40af !important; }
  [class*="bg-red"] { background: #fee2e2 !important; color: #991b1b !important; }
  [class*="bg-slate"] { background: #f1f5f9 !important; color: #334155 !important; }

  /* ─── 17. MATN RANGLARI ─── */
  [class*="text-emerald"] { color: #059669 !important; }
  [class*="text-red"] { color: #dc2626 !important; }
  [class*="text-amber"] { color: #d97706 !important; }
  [class*="text-indigo"] { color: #4f46e5 !important; }
  [class*="text-purple"] { color: #9333ea !important; }
  [class*="text-blue"] { color: #2563eb !important; }
  [class*="text-cyan"] { color: #0891b2 !important; }

  /* ─── 18. SAHIFA BO'LINMALARI ─── */
  section, .card {
    break-inside: auto;
  }

  /* Har bir career — yangi sahifada boshlanishi (kerak bo'lsa) */
  .career-section {
    break-before: auto;
  }

  /* Ro'yxat elementlari uzilmasin */
  li { break-inside: avoid; }

  /* ─── 19. RANGLI BORDER'LAR ─── */
  [class*="border-indigo"] { border-color: #c7d2fe !important; }
  [class*="border-emerald"] { border-color: #a7f3d0 !important; }
  [class*="border-amber"] { border-color: #fde68a !important; }
  [class*="border-slate"] { border-color: #cbd5e1 !important; }
  [class*="border-purple"] { border-color: #d8b4fe !important; }
  [class*="border-blue"] { border-color: #bfdbfe !important; }

  /* ─── 20. FON RANGLARI — och versiyalar ─── */
  .bg-\\[var\\(--tg-secondary-bg\\)\\] { background: #f9fafb !important; }
  .bg-\\[var\\(--tg-bg\\)\\] { background: #ffffff !important; }

  /* Dark overlay'lar — olib tashlash */
  [class*="backdrop"] { backdrop-filter: none !important; }
}
'''

css = css.rstrip() + PRINT_CSS + "\n"
GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — 20 ta print fix")


# ═══════════════════════════════════════════════════════════
# 2. REPORT SAHIFA — Print wrapper qo'shish
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

# main'ga className qo'shish
old_main = '<main className="max-w-md mx-auto px-4 py-6">'
new_main = '<main className="max-w-md lg:max-w-4xl mx-auto px-4 py-6 print-full">'
if old_main in rep:
    rep = rep.replace(old_main, new_main)
    print("[OK] report/page.tsx — kengaytirilgan container")
else:
    print("[SKIP] report/page.tsx — main topilmadi")

REPORT.write_text(rep, encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 3. CSS — print-full klassi
# ═══════════════════════════════════════════════════════════
css = GLOBALS.read_text(encoding="utf-8")

PRINT_FULL = '''

/* Print uchun to'liq kenglik */
@media print {
  .print-full {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }
}
'''

if ".print-full" not in css:
    css = css.rstrip() + PRINT_FULL + "\n"
    GLOBALS.write_text(css, encoding="utf-8")
    print("[OK] globals.css — .print-full klassi")

print()
print("=" * 60)
print("v5 — Print CSS tuzatildi!")
print("=" * 60)
print()
print("Nima o'zgardi:")
print("  1. Ranglar saqlanadi (print-color-adjust: exact)")
print("  2. CSS variables print'da light mode'ga o'tadi")
print("  3. A4 full width (max-w-md → 100%)")
print("  4. Kontrast muammolari tuzatildi")
print("  5. Accordion — hammasi PDF'da ochiq")
print()
print("Keyingi: git push")