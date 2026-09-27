"use client";

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
  { id: "dark", label: "Tungi", desc: "Zamonaviy tungi dizayn", icon: Moon, color: "text-slate-300", bg: "bg-slate-800" },
  { id: "light", label: "Kunduzgi", desc: "An'anaviy oq dizayn", icon: Sun, color: "text-amber-400", bg: "bg-amber-50" },
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
      {/* Trigger buttons */}
      <div className="space-y-2 no-print">
        <button
          onClick={() => setOpen(true)}
          className="btn btn-secondary"
        >
          <Palette className="w-4 h-4" />
          <span>Dizaynni o'zgartirish</span>
        </button>

        <button
          onClick={handleDownload}
          disabled={sending}
          className="btn btn-primary"
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
              <span>PDF sifatida yuklab olish</span>
            </>
          )}
        </button>

        {isMobile && inTelegram && (
          <p className="t-caption text-subtle text-center pt-1">
            PDF fayl Telegram bot orqali yuboriladi
          </p>
        )}
      </div>

      {/* Theme modal */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 no-print">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
              <div>
                <h3 className="t-heading">Dizaynni tanlang</h3>
                <p className="t-caption text-subtle mt-1">
                  Tanlanganda sahifa o'zgaradi
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted hover:text-text"
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
                    className={`option-btn ${active ? "selected" : ""}`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-lg ${t.bg} flex items-center justify-center shrink-0`}
                      >
                        <Icon className={`w-5 h-5 ${t.color}`} />
                      </div>
                      <div className="text-left">
                        <p className="t-heading">{t.label}</p>
                        <p className="t-small text-muted">{t.desc}</p>
                      </div>
                    </div>
                    <span className="option-indicator">
                      {active && (
                        <CheckCircle2 className="w-3 h-3 text-white" strokeWidth={3} />
                      )}
                    </span>
                  </button>
                );
              })}
            </div>

            <div className="p-4 pt-2">
              <button
                onClick={() => setOpen(false)}
                className="btn btn-primary"
              >
                Tayyor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Congrats modal */}
      {showCongrats && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 no-print">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            <div className="p-8 text-center">
              <div className="w-16 h-16 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-5">
                <PartyPopper className="w-7 h-7 text-success" />
              </div>

              <h2 className="t-title mb-2">Tabriklaymiz!</h2>
              <p className="t-small text-muted">
                {sentToTelegram
                  ? "PDF Telegram botingizga yuborildi"
                  : "PDF muvaffaqiyatli yuklab olindi"}
              </p>
            </div>

            <div className="px-5 pb-5 space-y-3">
              <div className="card-clean">
                <div className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
                  <div>
                    <p className="t-heading mb-1">Nima qildingiz</p>
                    <p className="t-small text-muted">
                      Diagnostikadan o'tdingiz va shaxsiy yo'l xaritangizni oldingiz.
                    </p>
                  </div>
                </div>
              </div>

              <div className="card-clean">
                <div className="flex items-start gap-2.5">
                  <span className="text-warning text-base leading-none mt-0.5">⚡</span>
                  <div>
                    <p className="t-heading mb-1">Keyingi qadam</p>
                    <p className="t-small text-muted">
                      Yo'l xaritangizdagi birinchi 3 qadamni bugun boshlang.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 pt-0 space-y-2">
              <button
                onClick={handleBackToBot}
                disabled={sending}
                className="btn btn-primary"
              >
                {sending ? (
                  "Yuklanmoqda..."
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Botga qaytish</span>
                  </>
                )}
              </button>

              <button
                onClick={handleRedownload}
                disabled={sending}
                className="btn btn-ghost"
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
