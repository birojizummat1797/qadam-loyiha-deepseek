# -*- coding: utf-8 -*-
"""QADAM v7 — html2pdf.js + 3 theme (dark/light/pastel)."""
from pathlib import Path
import re

# ═══════════════════════════════════════════════════════════
# 1. GLOBALS.CSS — print override'larni yumshatish
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

# Eski print bloklarni olib tashlash
css = re.sub(r'@media print \{.*?\n\}', '', css, flags=re.DOTALL)
css = re.sub(r'/\* ═+\s*PRINT.*?\*/\s*@media print \{.*?\n\}', '', css, flags=re.DOTALL)

# Yangi yumshoq print (fallback uchun)
NEW_PRINT = '''

/* ═══════════════════════════════════════════════════════════
   PRINT — faqat layout fix (Ctrl+P fallback)
   Asosiy PDF: html2pdf.js orqali
   ═══════════════════════════════════════════════════════════ */
@media print {
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
    animation: none !important;
    transition: none !important;
    transform: none !important;
    opacity: 1 !important;
  }

  @page {
    size: A4;
    margin: 8mm 10mm;
  }

  main, main.print-full {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  [data-accordion-content],
  [data-calendar-body] {
    display: block !important;
    max-height: none !important;
    overflow: visible !important;
    margin-top: 8pt !important;
  }

  [data-chevron] { display: none !important; }

  button.no-print,
  .no-print { display: none !important; }
}
'''

css = css.rstrip() + NEW_PRINT + "\n"
GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — print override'larni yumshatdi")


# ═══════════════════════════════════════════════════════════
# 2. PdfDownloader.tsx — komponent yaratish
# ═══════════════════════════════════════════════════════════
PDF_COMP = Path("qadam-miniapp/components/PdfDownloader.tsx")

PDF_DOWNLOADER = r'''"use client";

import { useState } from "react";
import { Download, X, Moon, Sun, Flower2, Loader2 } from "lucide-react";

type Theme = "dark" | "light" | "pastel";

const THEMES: { id: Theme; label: string; icon: any; color: string; bg: string }[] = [
  { id: "dark", label: "Tungi", icon: Moon, color: "text-indigo-300", bg: "bg-slate-800" },
  { id: "light", label: "Kunduzgi", icon: Sun, color: "text-amber-500", bg: "bg-amber-50" },
  { id: "pastel", label: "Pastel", icon: Flower2, color: "text-pink-400", bg: "bg-pink-50" },
];

export function PdfDownloader({ reportId }: { reportId: number }) {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>("dark");
  const [loading, setLoading] = useState(false);

  const downloadPdf = async () => {
    setLoading(true);
    try {
      // Dynamic import — bundle kichik qolishi uchun
      const html2pdf = (await import("html2pdf.js")).default;

      const element = document.getElementById("report-root");
      if (!element) {
        alert("Xatolik: report topilmadi");
        return;
      }

      // Theme atributini qo'shish
      element.setAttribute("data-pdf-theme", theme);

      // Style qayta hisoblanishi uchun
      await new Promise((r) => setTimeout(r, 150));

      const bgColor =
        theme === "dark" ? "#0a0a0f" :
        theme === "pastel" ? "#fdf2f8" :
        "#ffffff";

      const opt = {
        margin: [8, 8, 8, 8],
        filename: `QADAM-report-${reportId}-${theme}.pdf`,
        image: { type: "jpeg", quality: 0.95 },
        html2canvas: {
          scale: 2,
          useCORS: true,
          backgroundColor: bgColor,
          logging: false,
          windowWidth: element.scrollWidth,
        },
        jsPDF: {
          unit: "mm",
          format: "a4",
          orientation: "portrait",
          compress: true,
        },
        pagebreak: {
          mode: ["css", "legacy"],
          avoid: [".card", "[class*='rounded-2xl']", "li", "p"],
        },
      };

      await html2pdf().set(opt as any).from(element).save();

      // Atributni olib tashlash
      element.removeAttribute("data-pdf-theme");
      setOpen(false);
    } catch (e: any) {
      alert("PDF xatolik: " + e.message);
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Trigger tugma */}
      <button
        onClick={() => setOpen(true)}
        className="btn-primary no-print flex items-center justify-center gap-2"
      >
        <Download className="w-4 h-4" />
        PDF sifatida yuklab olish
      </button>

      {/* Modal */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm no-print">
          <div className="w-full max-w-sm rounded-2xl bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/20 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-[var(--tg-hint)]/15 flex items-center justify-between">
              <h3 className="font-semibold">PDF dizaynini tanlang</h3>
              <button
                onClick={() => setOpen(false)}
                className="w-8 h-8 rounded-full hover:bg-[var(--tg-bg)] flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Theme picker */}
            <div className="p-4 space-y-3">
              {THEMES.map((t) => {
                const Icon = t.icon;
                const active = theme === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setTheme(t.id)}
                    className={`w-full p-3 rounded-xl border-2 transition flex items-center gap-3 ${
                      active
                        ? "border-indigo-500 bg-indigo-500/10"
                        : "border-[var(--tg-hint)]/20"
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-lg ${t.bg} flex items-center justify-center shrink-0`}>
                      <Icon className={`w-6 h-6 ${t.color}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-semibold text-sm">{t.label}</p>
                      <p className="text-xs text-[var(--tg-hint)]">
                        {t.id === "dark" && "Zamonaviy tungi dizayn"}
                        {t.id === "light" && "Ananaviy oq dizayn"}
                        {t.id === "pastel" && "Yumshoq rangli dizayn"}
                      </p>
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

            {/* Actions */}
            <div className="p-4 border-t border-[var(--tg-hint)]/15 flex gap-2">
              <button
                onClick={() => setOpen(false)}
                disabled={loading}
                className="flex-1 py-3 rounded-xl border border-[var(--tg-hint)]/20 text-sm font-medium"
              >
                Bekor qilish
              </button>
              <button
                onClick={downloadPdf}
                disabled={loading}
                className="flex-1 py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Yuklanmoqda...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Yuklash
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
'''

PDF_COMP.write_text(PDF_DOWNLOADER, encoding="utf-8")
print("[OK] components/PdfDownloader.tsx")


# ═══════════════════════════════════════════════════════════
# 3. REPORT PAGE — PdfDownloader'ni ishlatish
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

# Import qo'shish
if "PdfDownloader" not in rep:
    rep = rep.replace(
        'import { RoadmapView } from "@/components/RoadmapView";',
        'import { RoadmapView } from "@/components/RoadmapView";\nimport { PdfDownloader } from "@/components/PdfDownloader";',
    )

# main'ga id="report-root" qo'shish
if 'id="report-root"' not in rep:
    rep = rep.replace(
        '<main className="max-w-md lg:max-w-4xl mx-auto px-4 py-6 print-full">',
        '<main id="report-root" className="max-w-md lg:max-w-4xl mx-auto px-4 py-6 print-full">',
    )

# Eski "PDF sifatida saqlash" tugmasini almashtirish
old_btn = '''<button className="btn-primary mt-6" onClick={() => window.print()}>
        PDF sifatida saqlash
      </button>'''

new_btn = '''<div className="mt-6">
        <PdfDownloader reportId={Number(id)} />
      </div>'''

if old_btn in rep:
    rep = rep.replace(old_btn, new_btn)
    print("[OK] report/page.tsx — PdfDownloader ulandi")
else:
    # Agar u boshqacha bo'lsa
    rep = re.sub(
        r'<button[^>]*onClick=\{\(\) => window\.print\(\)\}[^>]*>.*?</button>',
        new_btn,
        rep,
        flags=re.DOTALL,
    )
    print("[OK] report/page.tsx — print tugmasi almashtirildi")

REPORT.write_text(rep, encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# 4. PASTEL THEME CSS
# ═══════════════════════════════════════════════════════════
css = GLOBALS.read_text(encoding="utf-8")

PASTEL_CSS = '''

/* ═══════════════════════════════════════════════════════════
   PDF THEME OVERRIDES (html2pdf.js uchun)
   ═══════════════════════════════════════════════════════════ */

/* DARK — default, o'zgartirmaydi */
[data-pdf-theme="dark"] {
  background: #0a0a0f !important;
}

/* LIGHT */
[data-pdf-theme="light"] {
  background: #ffffff !important;
  color: #0a0a0f !important;
}
[data-pdf-theme="light"] .card,
[data-pdf-theme="light"] [class*="rounded-2xl"] {
  background: #f9fafb !important;
  border-color: #e5e7eb !important;
  color: #0a0a0f !important;
}
[data-pdf-theme="light"] * {
  --tg-bg: #ffffff !important;
  --tg-text: #0a0a0f !important;
  --tg-hint: #6b7280 !important;
  --tg-secondary-bg: #f3f4f6 !important;
}
[data-pdf-theme="light"] p,
[data-pdf-theme="light"] span,
[data-pdf-theme="light"] h1,
[data-pdf-theme="light"] h2,
[data-pdf-theme="light"] h3,
[data-pdf-theme="light"] h4,
[data-pdf-theme="light"] li {
  color: #0a0a0f !important;
}
[data-pdf-theme="light"] .gradient-text {
  background: none !important;
  -webkit-text-fill-color: #4f46e5 !important;
  color: #4f46e5 !important;
}

/* PASTEL */
[data-pdf-theme="pastel"] {
  background: #fef6fb !important;
  color: #1f2937 !important;
}
[data-pdf-theme="pastel"] .card,
[data-pdf-theme="pastel"] [class*="rounded-2xl"] {
  background: #fdf2f8 !important;
  border-color: #fbcfe8 !important;
  color: #1f2937 !important;
}
[data-pdf-theme="pastel"] * {
  --tg-bg: #fef6fb !important;
  --tg-text: #1f2937 !important;
  --tg-hint: #9d174d !important;
  --tg-secondary-bg: #fce7f3 !important;
}
[data-pdf-theme="pastel"] p,
[data-pdf-theme="pastel"] span,
[data-pdf-theme="pastel"] h1,
[data-pdf-theme="pastel"] h2,
[data-pdf-theme="pastel"] h3,
[data-pdf-theme="pastel"] h4,
[data-pdf-theme="pastel"] li {
  color: #1f2937 !important;
}
[data-pdf-theme="pastel"] .gradient-text {
  background: none !important;
  -webkit-text-fill-color: #db2777 !important;
  color: #db2777 !important;
}
'''

if "[data-pdf-theme=" not in css:
    css = css.rstrip() + PASTEL_CSS + "\n"
    GLOBALS.write_text(css, encoding="utf-8")
    print("[OK] globals.css — PDF theme overrides")

print()
print("=" * 60)
print("v7 — Tayyor!")
print("=" * 60)
print()
print("KEYINGI QADAMLAR:")
print()
print("1. Terminalda:")
print("   cd qadam-miniapp")
print("   npm install html2pdf.js")
print()
print("2. Keyin:")
print("   cd ..")
print("   git add -A")
print('   git commit -m "v7: html2pdf.js with 3 themes"')
print("   git push")
print()