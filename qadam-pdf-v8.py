# -*- coding: utf-8 -*-
"""QADAM v8 — Theme switcher + native window.print() PDF."""
from pathlib import Path
import re

# ═══════════════════════════════════════════════════════════
# 1. GLOBALS.CSS — To'liq print + theme
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

# Eski print va theme bloklarni olib tashlash
css = re.sub(r'@media print \{.*?\n\}', '', css, flags=re.DOTALL)
css = re.sub(r'/\* ═+\s*PRINT.*?\*/', '', css, flags=re.DOTALL)
css = re.sub(r'/\* ═+\s*PDF THEME.*$', '', css, flags=re.DOTALL)
css = re.sub(r'\[data-pdf-theme=.*?\}', '', css, flags=re.DOTALL)

NEW_CSS = '''

/* ═══════════════════════════════════════════════════════════
   THEME PRESETS — body[data-theme]
   ═══════════════════════════════════════════════════════════ */

/* DARK (default) */
body[data-theme="dark"] {
  background: #0a0a0f;
  color: #f5f5f7;
  --tg-bg: #0a0a0f;
  --tg-text: #f5f5f7;
  --tg-hint: #9a9aa8;
  --tg-secondary-bg: #13131a;
  --tg-link: #6366f1;
  --tg-button: #6366f1;
}

/* LIGHT */
body[data-theme="light"] {
  background: #ffffff;
  color: #0a0a0f;
  --tg-bg: #ffffff;
  --tg-text: #0a0a0f;
  --tg-hint: #6b7280;
  --tg-secondary-bg: #f9fafb;
  --tg-link: #4f46e5;
  --tg-button: #6366f1;
}

/* PASTEL */
body[data-theme="pastel"] {
  background: #fef6fb;
  color: #1f2937;
  --tg-bg: #fef6fb;
  --tg-text: #1f2937;
  --tg-hint: #9d174d;
  --tg-secondary-bg: #fce7f3;
  --tg-link: #db2777;
  --tg-button: #db2777;
}

/* Light theme — gradient matnlar */
body[data-theme="light"] .gradient-text {
  background: none;
  -webkit-text-fill-color: #4f46e5;
  color: #4f46e5;
}
body[data-theme="pastel"] .gradient-text {
  background: none;
  -webkit-text-fill-color: #db2777;
  color: #db2777;
}

/* ═══════════════════════════════════════════════════════════
   PRINT — A4 to'liq egallash + ranglar + accordion ochiq
   ═══════════════════════════════════════════════════════════ */
@media print {
  /* ─── 1. SAHIFA A4 ─── */
  @page {
    size: A4;
    margin: 10mm 12mm;
  }

  /* ─── 2. RANGLARNI SAQLASH ─── */
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }

  /* ─── 3. ANIMATSIYA O'CHIRISH ─── */
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    transform: none !important;
    opacity: 1 !important;
  }

  /* ─── 4. FON VA RANG (themega qarab) ─── */
  html, body {
    background: var(--tg-bg, #ffffff) !important;
    color: var(--tg-text, #0a0a0f) !important;
    font-size: 10pt;
    line-height: 1.4;
  }

  /* ─── 5. FULL WIDTH ─── */
  main, main.print-full, .print-full {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* ─── 6. KARTALAR ─── */
  .card, [class*="rounded-2xl"], [class*="rounded-xl"] {
    background: var(--tg-secondary-bg, #f9fafb) !important;
    border: 1px solid rgba(128, 128, 128, 0.2) !important;
    padding: 8pt 10pt !important;
    margin-bottom: 5pt !important;
    break-inside: auto;
    page-break-inside: auto;
  }

  /* ─── 7. ACCORDION — HAMMASI OCHIQ ─── */
  [data-accordion-content],
  [data-calendar-body] {
    display: block !important;
    max-height: none !important;
    height: auto !important;
    overflow: visible !important;
    opacity: 1 !important;
    margin-top: 6pt !important;
  }

  [data-chevron] { display: none !important; }

  /* ─── 8. MATN O'LCHAMLARI ─── */
  h1 { font-size: 18pt; margin: 0 0 3pt; }
  h2 { font-size: 14pt; margin: 8pt 0 4pt; page-break-after: avoid; }
  h3 { font-size: 12pt; margin: 6pt 0 3pt; page-break-after: avoid; }
  h4 { font-size: 10.5pt; margin: 4pt 0 2pt; page-break-after: avoid; }
  p, li { font-size: 9.5pt; }
  .text-sm { font-size: 9.5pt !important; }
  .text-xs { font-size: 8pt !important; }

  /* ─── 9. RO'YXATLAR ─── */
  ul, ol { margin: 3pt 0; padding-left: 12pt; }
  li { margin: 1.5pt 0; break-inside: avoid; }

  /* ─── 10. TUGMALAR — YASHIRISH ─── */
  button, .btn-primary, .no-print {
    display: none !important;
  }

  /* ─── 11. LINKLAR ─── */
  a { color: var(--tg-link, #4f46e5) !important; }

  /* ─── 12. SVG ─── */
  svg { -webkit-print-color-adjust: exact !important; }

  /* ─── 13. GRADIENT MATN ─── */
  .gradient-text {
    background: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    -webkit-text-fill-color: var(--tg-link, #4f46e5) !important;
    color: var(--tg-link, #4f46e5) !important;
  }
}
'''

css = css.rstrip() + NEW_CSS + "\n"
GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — theme + print (A4 full)")


# ═══════════════════════════════════════════════════════════
# 2. PdfDownloader → ThemeSwitcher
# ═══════════════════════════════════════════════════════════
COMP = Path("qadam-miniapp/components/PdfDownloader.tsx")

SWITCHER = r'''"use client";

import { useState, useEffect } from "react";
import { Download, X, Moon, Sun, Flower2, Palette } from "lucide-react";

type Theme = "dark" | "light" | "pastel";

const THEMES: { id: Theme; label: string; desc: string; icon: any; color: string; bg: string }[] = [
  { id: "dark", label: "Tungi", desc: "Zamonaviy tungi dizayn", icon: Moon, color: "text-indigo-300", bg: "bg-slate-800" },
  { id: "light", label: "Kunduzgi", desc: "Ananaviy oq dizayn", icon: Sun, color: "text-amber-500", bg: "bg-amber-50" },
  { id: "pastel", label: "Pastel", desc: "Yumshoq rangli dizayn", icon: Flower2, color: "text-pink-400", bg: "bg-pink-50" },
];

export function PdfDownloader({ reportId }: { reportId: number }) {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>("dark");
  const [applied, setApplied] = useState<Theme>("dark");

  // Sahifa ochilganda default theme
  useEffect(() => {
    document.body.setAttribute("data-theme", "dark");
  }, []);

  // Theme tanlash — modal yopilmaydi, faqat "Qo'llash" bosilganda
  const applyTheme = (t: Theme) => {
    setTheme(t);
    setApplied(t);
    document.body.setAttribute("data-theme", t);
  };

  // Print (PDF) tugmasi
  const handleDownload = () => {
    // Barcha accordion'larni ochish
    const accordions = document.querySelectorAll<HTMLElement>("[data-accordion-content], [data-calendar-body]");
    accordions.forEach((el) => {
      el.style.maxHeight = "none";
      el.style.marginTop = "8pt";
    });

    // Framer motion opacity'larni 1 ga
    document.querySelectorAll<HTMLElement>("*").forEach((el) => {
      if (el.style.opacity === "0") el.style.opacity = "1";
    });

    // Print
    setTimeout(() => {
      window.print();
    }, 150);
  };

  return (
    <>
      {/* Trigger — 2 ta tugma */}
      <div className="flex flex-col gap-2 no-print">
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-[var(--tg-hint)]/25 text-sm font-medium hover:border-[var(--tg-hint)]/40 transition"
        >
          <Palette className="w-4 h-4" />
          Dizaynni o'zgartirish
        </button>
        <button
          onClick={handleDownload}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          PDF sifatida yuklab olish
        </button>
      </div>

      {/* Modal — faqat theme tanlash */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm no-print">
          <div className="w-full max-w-sm rounded-2xl bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/20 overflow-hidden">
            <div className="p-4 border-b border-[var(--tg-hint)]/15 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Dizaynni tanlang</h3>
                <p className="text-[10px] text-[var(--tg-hint)] mt-0.5">
                  Tanlanganda sahifa darhol ozgaradi
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="w-8 h-8 rounded-full hover:bg-[var(--tg-bg)] flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 space-y-2">
              {THEMES.map((t) => {
                const Icon = t.icon;
                const active = applied === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => applyTheme(t.id)}
                    className={`w-full p-3 rounded-xl border-2 transition flex items-center gap-3 ${
                      active ? "border-indigo-500 bg-indigo-500/10" : "border-[var(--tg-hint)]/20"
                    }`}
                  >
                    <div className={`w-11 h-11 rounded-lg ${t.bg} flex items-center justify-center shrink-0`}>
                      <Icon className={`w-5 h-5 ${t.color}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-semibold text-sm">{t.label}</p>
                      <p className="text-[11px] text-[var(--tg-hint)]">{t.desc}</p>
                    </div>
                    {active && (
                      <div className="w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-white" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="p-4 border-t border-[var(--tg-hint)]/15">
              <button
                onClick={() => setOpen(false)}
                className="w-full py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm"
              >
                Tayyor
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
'''

COMP.write_text(SWITCHER, encoding="utf-8")
print("[OK] components/PdfDownloader.tsx — theme switcher")


# ═══════════════════════════════════════════════════════════
# 3. REPORT PAGE — tugma joylashuvini o'zgartirish
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

# Eski almashtirishni topish
old_block = re.search(
    r'<div className="mt-6">\s*<PdfDownloader reportId=\{Number\(id\)\} />\s*</div>',
    rep,
)
if old_block:
    print("[OK] report/page.tsx — tugma allaqachon PdfDownloader")

REPORT.write_text(rep, encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 4. RoadmapView — beforeprint'ni olib tashlash (endi PdfDownloader boshqaradi)
# ═══════════════════════════════════════════════════════════
RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

# Eski beforeprint useEffect'ni olib tashlash
rv = re.sub(
    r'// PDF/print.*?\}, \[\]\);',
    '',
    rv,
    flags=re.DOTALL,
)

RV.write_text(rv, encoding="utf-8")
print("[OK] RoadmapView — beforeprint olib tashlandi")

print()
print("=" * 60)
print("v8 — Tayyor!")
print("=" * 60)
print()
print("YANGI OQIM:")
print("  1. 'Dizaynni o'zgartirish' → modal")
print("  2. Theme tanlash → SAHIFA DARHOL O'ZGARADI")
print("  3. 'Tayyor' → modal yopiladi")
print("  4. 'PDF sifatida yuklab olish' → brauzer print")
print("  5. Chrome print → 'Save as PDF'")
print()
print("Keyingi: git push")