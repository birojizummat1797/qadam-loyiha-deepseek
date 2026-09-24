# -*- coding: utf-8 -*-
"""PdfDownloader — mobile+desktop WITH TypeScript types."""
from pathlib import Path

PDF_COMP = Path("qadam-miniapp/components/PdfDownloader.tsx")

PDF_COMP.write_text(r'''"use client";

import { useState, useEffect } from "react";
import {
  Download, X, Moon, Sun, Flower2, Palette,
  CheckCircle2, PartyPopper, Send, Smartphone, Printer,
} from "lucide-react";
import { requestPdf, completeReport } from "@/lib/api";

type Theme = "dark" | "light" | "pastel";

const THEMES: {
  id: Theme;
  label: string;
  desc: string;
  icon: any;
  color: string;
  bg: string;
}[] = [
  { id: "dark", label: "Tungi", desc: "Zamonaviy tungi dizayn", icon: Moon, color: "text-indigo-300", bg: "bg-slate-800" },
  { id: "light", label: "Kunduzgi", desc: "Ananaviy oq dizayn", icon: Sun, color: "text-amber-500", bg: "bg-amber-50" },
  { id: "pastel", label: "Pastel", desc: "Yumshoq rangli dizayn", icon: Flower2, color: "text-pink-400", bg: "bg-pink-50" },
];

export function PdfDownloader({ reportId }: { reportId: number }) {
  const [open, setOpen] = useState(false);
  const [applied, setApplied] = useState<Theme>("dark");
  const [showCongrats, setShowCongrats] = useState(false);
  const [sending, setSending] = useState(false);
  const [inTelegram, setInTelegram] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [sentToTelegram, setSentToTelegram] = useState(false);

  useEffect(() => {
    document.body.setAttribute("data-theme", "dark");
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData && tg.initData.length > 10) setInTelegram(true);
    setIsMobile(/Android|iPhone|iPad|iPod/i.test(navigator.userAgent));
  }, []);

  const applyTheme = (t: Theme) => {
    setApplied(t);
    document.body.setAttribute("data-theme", t);
  };

  const handleDownload = async () => {
    if (isMobile && inTelegram) {
      setSending(true);
      try {
        const res = await requestPdf(reportId, applied);
        if (res.sent_to_telegram) {
          setSentToTelegram(true);
          setShowCongrats(true);
        } else {
          alert("PDF botga yuborilmadi.");
        }
      } catch (e: any) {
        alert("Xatolik: " + (e?.response?.data?.detail || e.message));
      } finally {
        setSending(false);
      }
    } else {
      document
        .querySelectorAll<HTMLElement>("[data-accordion-content], [data-calendar-body]")
        .forEach((el: HTMLElement) => {
          el.style.maxHeight = "none";
          el.style.marginTop = "8pt";
        });
      setTimeout(() => {
        window.print();
        setTimeout(() => setShowCongrats(true), 500);
      }, 100);
    }
  };

  const handleBackToBot = async () => {
    setSending(true);
    try {
      await completeReport(reportId);
    } catch (e) {
      console.log("Complete xatosi:", e);
    }
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.close && inTelegram) tg.close();
    else window.close();
  };

  const handleRedownload = () => {
    setShowCongrats(false);
    setSentToTelegram(false);
    setTimeout(() => handleDownload(), 300);
  };

  return (
    <>
      <div className="flex flex-col gap-2 no-print">
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-[var(--tg-hint)]/25 text-sm font-medium hover:border-[var(--tg-hint)]/40 transition"
        >
          <Palette className="w-4 h-4" />
          Dizaynni o&apos;zgartirish
        </button>
        <button
          onClick={handleDownload}
          disabled={sending}
          className="btn-primary flex items-center justify-center gap-2"
        >
          {sending ? (
            "Yuklanmoqda..."
          ) : (
            <>
              {isMobile && inTelegram ? (
                <Smartphone className="w-4 h-4" />
              ) : (
                <Printer className="w-4 h-4" />
              )}
              PDF sifatida yuklab olish
            </>
          )}
        </button>
        {isMobile && inTelegram && (
          <p className="text-[10px] text-[var(--tg-hint)] text-center">
            PDF fayl Telegram bot orqali yuboriladi
          </p>
        )}
      </div>

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

      {showCongrats && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm no-print">
          <div className="w-full max-w-sm rounded-3xl bg-gradient-to-br from-[var(--tg-secondary-bg)] to-[var(--tg-bg)] border border-emerald-500/30 overflow-hidden">
            <div className="p-6 text-center relative">
              <div className="absolute top-2 left-4 text-2xl">🎉</div>
              <div className="absolute top-4 right-6 text-xl">✨</div>

              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/30">
                <PartyPopper className="w-10 h-10 text-white" />
              </div>

              <h2 className="text-xl font-bold mb-2 gradient-text">Tabriklaymiz!</h2>
              <p className="text-sm text-[var(--tg-hint)] mb-1">
                {sentToTelegram
                  ? "PDF Telegram botingizga yuborildi"
                  : "PDF muvaffaqiyatli yuklab olindi"}
              </p>
            </div>

            <div className="px-6 pb-4 space-y-3">
              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 border border-[var(--tg-hint)]/15">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <p className="font-semibold mb-1">Nima qildingiz:</p>
                    <p className="text-[var(--tg-hint)]">
                      QADAM diagnostikasidan otdingiz va shaxsiy roadmapni oldingiz.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 border border-amber-500/20">
                <div className="flex items-start gap-2">
                  <span className="text-amber-400 text-sm">⚡</span>
                  <div className="text-xs">
                    <p className="font-semibold mb-1">Keyingi qadam:</p>
                    <p className="text-[var(--tg-hint)]">
                      Roadmapdagi birinchi 3 qadamni bugun boshlang.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 pt-2 space-y-2">
              <button
                onClick={handleBackToBot}
                disabled={sending}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/30 disabled:opacity-60"
              >
                {sending ? (
                  "Yuklanmoqda..."
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Botga qaytish
                  </>
                )}
              </button>

              <button
                onClick={handleRedownload}
                disabled={sending}
                className="w-full py-3 rounded-2xl border border-[var(--tg-hint)]/25 text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                Boshqa dizaynda yuklash
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
''', encoding="utf-8")

print("[OK] PdfDownloader.tsx — TypeScript turlari qaytarildi")
print()
print("Endi push qiling:")
print("  git add -A")
print('  git commit -m "Fix: TypeScript types in PdfDownloader"')
print("  git push")