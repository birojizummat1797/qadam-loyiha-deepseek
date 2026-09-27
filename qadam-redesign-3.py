# -*- coding: utf-8 -*-
"""Qadam.io — Redesign v3.3: BARCHA sahifalarni yangi dizaynga o'tkazish."""
from pathlib import Path

FRONTEND = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. globals.css — to'liq utility qo'shish
# ═══════════════════════════════════════════════════════════
GLOBALS = FRONTEND / "app/globals.css"
css = GLOBALS.read_text(encoding="utf-8")

# Eski WOW effects va print override'larni olib tashlash
import re
css = re.sub(r'/\* ═+\s*WOW EFFECTS.*$', '', css, flags=re.DOTALL)

# Yangi utility'lar
css += '''

/* ═══════════════════════════════════════════════════════════
   OPTION BUTTONS — variant tanlash (professional)
   ═══════════════════════════════════════════════════════════ */
.option-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  min-height: 60px;
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 15px;
  line-height: 1.4;
  font-weight: 400;
  text-align: left;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease);
  -webkit-tap-highlight-color: transparent;
}

.option-btn:hover {
  border-color: var(--color-border-strong);
}

.option-btn.selected {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
}

.option-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--color-border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--duration-fast) var(--ease);
}

.option-btn.selected .option-indicator {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

/* ═══════════════════════════════════════════════════════════
   CARD — minimal
   ═══════════════════════════════════════════════════════════ */
.card-clean {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

/* ═══════════════════════════════════════════════════════════
   PRICE CARD
   ═══════════════════════════════════════════════════════════ */
.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
}

.price-row + .price-row {
  border-top: 1px solid var(--color-border);
}

/* ═══════════════════════════════════════════════════════════
   BADGE — minimal
   ═══════════════════════════════════════════════════════════ */
.badge-soft {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.badge-warning { background: var(--color-warning-soft); color: var(--color-warning); }
.badge-success { background: var(--color-success-soft); color: var(--color-success); }
.badge-primary { background: var(--color-primary-soft); color: var(--color-primary); }
.badge-danger { background: var(--color-danger-soft); color: var(--color-danger); }

/* ═══════════════════════════════════════════════════════════
   DIVIDER
   ═══════════════════════════════════════════════════════════ */
.divider {
  height: 1px;
  background: var(--color-border);
  margin: 16px 0;
}
'''

GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — utility qo'shildi")

# ═══════════════════════════════════════════════════════════
# 2. STAGE 2 — yangi dizayn
# ═══════════════════════════════════════════════════════════
STAGE2 = FRONTEND / "app/stage2/page.tsx"

STAGE2.write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check } from "lucide-react";
import { fetchQuestions, submitStage2 } from "@/lib/api";
import { useStore } from "@/lib/store";
import { SkeletonQuestion } from "@/components/Skeleton";

const LIKERT = [
  { v: 1, l: "Umuman yo'q" },
  { v: 2, l: "Kam" },
  { v: 3, l: "O'rtacha" },
  { v: 4, l: "Ko'p" },
  { v: 5, l: "To'liq ha" },
];

export default function Stage2Page() {
  const router = useRouter();
  const stage1ResultId = useStore((s) => s.stage1ResultId);
  const [questions, setQuestions] = useState<any[]>([]);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!stage1ResultId) {
      router.push("/stage1");
      return;
    }
    fetchQuestions()
      .then((data) => {
        const all: any[] = [];
        Object.values(data.stage_2.dimensions).forEach((dim: any) => {
          dim.questions.forEach((q: any) => all.push(q));
        });
        setQuestions(all);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [stage1ResultId, router]);

  if (loading) return <Loader />;
  if (!questions.length) return <Loader />;

  const q = questions[current];
  const currentVal = answers[q.id];

  const setAnswer = (v: number) => setAnswers({ ...answers, [q.id]: v });

  const next = async () => {
    if (current < questions.length - 1) {
      setCurrent(current + 1);
      return;
    }
    setSubmitting(true);
    try {
      const res = await submitStage2(stage1ResultId!, answers);
      router.push(`/report/${res.report_id}`);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  const back = () => {
    if (current > 0) setCurrent(current - 1);
  };

  const progress = ((current + 1) / questions.length) * 100;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* ═══ TOP BAR ═══ */}
        <div className="pt-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={back}
              disabled={current === 0}
              className="text-muted t-small disabled:opacity-0 transition-opacity"
            >
              Orqaga
            </button>
            <span className="t-caption text-subtle">
              {current + 1} / {questions.length}
            </span>
          </div>

          <div className="h-px bg-[var(--color-border)] relative overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
        </div>

        {/* ═══ QUESTION ═══ */}
        <AnimatePresence mode="wait">
          <motion.div
            key={current}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="flex-1 flex flex-col"
          >
            <h2 className="t-title mb-8 mt-4">{q.text}</h2>

            <div className="flex flex-col gap-2.5 mb-6">
              {LIKERT.map((o, idx) => {
                const selected = currentVal === o.v;
                return (
                  <motion.button
                    key={o.v}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      delay: idx * 0.03,
                      duration: 0.2,
                      ease: [0.4, 0, 0.2, 1],
                    }}
                    onClick={() => setAnswer(o.v)}
                    className={`option-btn ${selected ? "selected" : ""}`}
                  >
                    <span>{o.l}</span>
                    <span className="option-indicator">
                      {selected && (
                        <Check className="w-3 h-3 text-white" strokeWidth={3} />
                      )}
                    </span>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* ═══ NEXT BUTTON ═══ */}
        <div className="pb-6">
          <button
            onClick={next}
            disabled={!currentVal || submitting}
            className="btn btn-primary"
          >
            {submitting
              ? "Tahlil qilmoqda..."
              : current === questions.length - 1
              ? "Natijani ko'rish"
              : "Keyingisi"}
          </button>
        </div>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6">
        <SkeletonQuestion />
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/stage2/page.tsx")

# ═══════════════════════════════════════════════════════════
# 3. TEASER — yangi dizayn
# ═══════════════════════════════════════════════════════════
TEASER = FRONTEND / "app/teaser/page.tsx"

TEASER.write_text(r'''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles } from "lucide-react";
import { useStore } from "@/lib/store";
import { createPayment, createStarsInvoice, devUnlock } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);
  const [loading, setLoading] = useState(false);

  if (!teaser || !stage1ResultId) {
    return (
      <main className="min-h-screen flex justify-center">
        <div className="w-full max-w-md px-6 pt-10">
          <p className="t-body text-muted mb-6">Natija topilmadi.</p>
          <button
            className="btn btn-primary"
            onClick={() => router.push("/stage1")}
          >
            Qaytadan boshlash
          </button>
        </div>
      </main>
    );
  }

  const payStars = async () => {
    setLoading(true);
    try {
      const res = await createStarsInvoice(stage1ResultId);
      const tg = (window as any).Telegram?.WebApp;
      if (!tg?.openInvoice) {
        alert("Telegram Stars bu qurilmada ishlamaydi.");
        return;
      }
      tg.openInvoice(res.invoice_link, (status: string) => {
        if (status === "paid") router.push("/stage2");
      });
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const payClick = async () => {
    setLoading(true);
    try {
      const res = await createPayment(stage1ResultId, "click");
      if (res.pay_url) window.open(res.pay_url, "_blank");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDev = async () => {
    setLoading(true);
    try {
      await devUnlock(stage1ResultId);
      router.push("/stage2");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* ═══ HEADER ═══ */}
        <div className="pt-8 pb-6 fade-in">
          <h1 className="t-title mb-2">Tezkor natijangiz</h1>
          <p className="t-small text-muted">
            Profilingiz bo'yicha dastlabki tahlil
          </p>
        </div>

        {/* ═══ SIGNALS ═══ */}
        <div className="mb-6 fade-in fade-in-1">
          <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
          <div className="space-y-2">
            {teaser.top_2_signals?.map((s: any) => (
              <div
                key={s.key}
                className="flex items-center justify-between py-2"
              >
                <span className="t-body capitalize">
                  {s.key.replace(/_/g, " ")}
                </span>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(s.score * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* ═══ CAREERS ═══ */}
        <div className="mb-6 fade-in fade-in-2">
          <p className="t-caption text-subtle mb-3">Mos yo'nalishlar</p>
          <div className="space-y-3">
            {teaser.top_2_careers?.map((c: any) => (
              <div
                key={c.career_id}
                className="card-clean flex items-center justify-between"
              >
                <div>
                  <p className="t-heading">{c.career_uz}</p>
                  <p className="t-small text-muted">{c.cluster_uz}</p>
                </div>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(c.fit)}%
                </span>
              </div>
            ))}
          </div>

          {teaser.locked_count > 0 && (
            <div className="mt-3 flex items-center gap-2 t-small text-muted">
              <Lock className="w-3.5 h-3.5" />
              <span>Yana {teaser.locked_count} ta yo'nalish yashirilgan</span>
            </div>
          )}
        </div>

        {/* ═══ PREMIUM ═══ */}
        <div className="card-clean mb-6 fade-in fade-in-3">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-primary" />
            <h3 className="t-heading">Chuqur tahlil</h3>
          </div>

          <ul className="space-y-2.5 mb-5">
            {[
              "Top-5 mos yo'nalish",
              "Fit + Readiness har biri uchun",
              "To'siqlar va yechimlar",
              "6-12 oy shaxsiy yo'l xaritasi",
              "Birinchi 3 qadam",
              "PDF hisobot",
            ].map((t, i) => (
              <li key={i} className="flex items-start gap-2.5 t-small">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>{t}</span>
              </li>
            ))}
          </ul>

          <div className="divider" />

          {/* Price */}
          <div className="price-row">
            <span className="t-small text-muted">Narx</span>
            <span className="t-heading">39 000 so'm</span>
          </div>

          {/* Actions */}
          <div className="space-y-2.5 pt-4">
            <button
              onClick={payStars}
              disabled={loading}
              className="btn btn-primary"
            >
              Telegram Stars orqali · 150 ⭐
            </button>

            <button
              onClick={payClick}
              disabled={loading}
              className="btn btn-secondary"
            >
              Karta orqali to'lash
            </button>
          </div>

          <p className="t-caption text-subtle text-center mt-4">
            7 kun ichida pulni qaytarish
          </p>
        </div>

        {/* ═══ DEV MODE ═══ */}
        <div className="pb-6 fade-in fade-in-4">
          <button onClick={handleDev} disabled={loading} className="btn btn-ghost">
            🛠 Test uchun ochish (to'lovsiz)
          </button>
        </div>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/teaser/page.tsx")

# ═══════════════════════════════════════════════════════════
# 4. REPORT — button qismlari
# ═══════════════════════════════════════════════════════════
REPORT = FRONTEND / "app/report/[id]/page.tsx"
rep = REPORT.read_text(encoding="utf-8")

# main wrapper'ni yangilash
rep = rep.replace(
    '<main className="max-w-md lg:max-w-4xl mx-auto px-4 py-6 print-full">',
    '<main className="min-h-screen flex justify-center">\n      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6 print-full">',
)

# Yopuvchi tag
rep = rep.replace(
    '    </main>\n  );\n}\n\nfunction Loader',
    '      </div>\n    </main>\n  );\n}\n\nfunction Loader',
)

REPORT.write_text(rep, encoding="utf-8")
print("[OK] report/page.tsx — wrapper")

# ═══════════════════════════════════════════════════════════
# 5. PdfDownloader — yangi dizayn
# ═══════════════════════════════════════════════════════════
PDF_COMP = FRONTEND / "components/PdfDownloader.tsx"

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
''', encoding="utf-8")
print("[OK] components/PdfDownloader.tsx")

# ═══════════════════════════════════════════════════════════
# 6. FeedbackModal — yangi dizayn
# ═══════════════════════════════════════════════════════════
FEEDBACK = FRONTEND / "components/FeedbackModal.tsx"

FEEDBACK.write_text(r'''"use client";

import { useState } from "react";
import { Star, MessageSquare, Send, CheckCircle2, X } from "lucide-react";
import { submitFeedback } from "@/lib/api";

export function FeedbackModal({
  reportId,
  onClose,
}: {
  reportId: number;
  onClose?: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const handleSubmit = async () => {
    if (rating < 1) return;
    setSubmitting(true);
    try {
      await submitFeedback(reportId, rating, comment);
      setDone(true);
      setTimeout(() => {
        setOpen(false);
        onClose?.();
      }, 1500);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  const LABELS: { [key: number]: string } = {
    1: "Yomon",
    2: "Qoniqarli emas",
    3: "O'rtacha",
    4: "Yaxshi",
    5: "Zo'r",
  };

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="btn btn-secondary no-print"
        >
          <MessageSquare className="w-4 h-4" />
          <span>Fikringizni bildiring</span>
        </button>
      )}

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 no-print">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            {done ? (
              <div className="p-10 text-center">
                <div className="w-14 h-14 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 className="w-7 h-7 text-success" />
                </div>
                <h3 className="t-heading mb-2">Rahmat!</h3>
                <p className="t-small text-muted">
                  Fikringiz mahsulotni yaxshilashga yordam beradi.
                </p>
              </div>
            ) : (
              <>
                <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
                  <h3 className="t-heading">Fikringizni bildiring</h3>
                  <button
                    onClick={() => setOpen(false)}
                    className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div className="p-5 space-y-5">
                  <div>
                    <p className="t-small text-center mb-4">
                      Natijadan qanchalik mamnunmisiz?
                    </p>
                    <div className="flex justify-center gap-2">
                      {[1, 2, 3, 4, 5].map((s) => (
                        <button
                          key={s}
                          onClick={() => setRating(s)}
                          className="p-1"
                        >
                          <Star
                            className={`w-8 h-8 transition-colors ${
                              s <= rating
                                ? "text-warning fill-warning"
                                : "text-subtle"
                            }`}
                          />
                        </button>
                      ))}
                    </div>
                    {rating > 0 && (
                      <p className="t-small text-warning text-center mt-2 font-medium">
                        {LABELS[rating]}
                      </p>
                    )}
                  </div>

                  <div>
                    <p className="t-caption text-subtle mb-2">
                      Izoh (ixtiyoriy)
                    </p>
                    <textarea
                      value={comment}
                      onChange={(e) => setComment(e.target.value.slice(0, 500))}
                      placeholder="Nima yaxshi, nima yaxshilanishi kerak?"
                      className="w-full p-3 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)] t-small resize-none focus:outline-none focus:border-primary"
                      rows={3}
                    />
                    <p className="t-caption text-subtle text-right mt-1">
                      {comment.length}/500
                    </p>
                  </div>
                </div>

                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={rating < 1 || submitting}
                    className="btn btn-primary"
                  >
                    {submitting ? (
                      "Yuborilmoqda..."
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Yuborish</span>
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
''', encoding="utf-8")
print("[OK] components/FeedbackModal.tsx")

# ═══════════════════════════════════════════════════════════
# 7. CloseButton — yangi dizayn
# ═══════════════════════════════════════════════════════════
CLOSE = FRONTEND / "components/CloseButton.tsx"

CLOSE.write_text(r'''"use client";

import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";

export function CloseButton() {
  const [inTelegram, setInTelegram] = useState(false);

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData && tg.initData.length > 10) setInTelegram(true);
  }, []);

  const handleClose = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.close) tg.close();
    else if (window.history.length > 1) window.history.back();
    else window.close();
  };

  if (!inTelegram) return null;

  return (
    <div className="mt-6 mb-2 no-print">
      <button onClick={handleClose} className="btn btn-secondary">
        <ArrowLeft className="w-4 h-4" />
        <span>Botga qaytish</span>
      </button>
      <p className="t-caption text-subtle text-center mt-3">
        Hisobotingiz saqlandi
      </p>
    </div>
  );
}
''', encoding="utf-8")
print("[OK] components/CloseButton.tsx")

print()
print("=" * 60)
print("Redesign v3.3 — HAMMA sahifalar yangilandi!")
print("=" * 60)
print()
print("Yangilangan sahifalar:")
print("  • app/page.tsx — Welcome")
print("  • app/stage1/page.tsx — 8 savol")
print("  • app/stage2/page.tsx — 18 savol")
print("  • app/teaser/page.tsx — Teaser")
print("  • app/report/[id]/page.tsx — Report wrapper")
print("  • components/PdfDownloader.tsx")
print("  • components/FeedbackModal.tsx")
print("  • components/CloseButton.tsx")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Redesign v3.3: ALL pages unified design"')
print("  git push")
print("  Vercel redeploy (cache'siz)")