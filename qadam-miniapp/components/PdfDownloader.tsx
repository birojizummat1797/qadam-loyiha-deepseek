"use client";

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
