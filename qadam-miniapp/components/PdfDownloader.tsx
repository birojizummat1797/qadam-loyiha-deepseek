"use client";

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
