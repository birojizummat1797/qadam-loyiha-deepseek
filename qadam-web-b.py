# -*- coding: utf-8 -*-
"""QADAM Web generator - Qism B: barcha sahifalar"""
from pathlib import Path

ROOT = Path("qadam-miniapp")
FILES = {}


def add(path, content):
    FILES[path] = content.strip() + "\n"


# ═══════════ app/page.tsx — Intro ═══════════
add("app/page.tsx", r'''
"use client";

import Link from "next/link";
import { Sparkles, Target, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <main className="max-w-md mx-auto px-5 py-10">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-3 gradient-text">QADAM</h1>
        <p className="text-[var(--tg-hint)]">
          Sizga mos kasb va sohani topish uchun tahlil
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-3 mb-3">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold">Tezkor tahlil</h3>
        </div>
        <p className="text-sm text-[var(--tg-hint)] mb-2">
          8 savol &middot; 3 daqiqa &middot; Bepul
        </p>
        <p className="text-sm">
          Kuchli 2 ta signalingizni va 2 ta mos yonalishni korasiz.
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-3 mb-3">
          <Target className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold">Chuqur tahlil (Premium)</h3>
        </div>
        <p className="text-sm text-[var(--tg-hint)] mb-2">
          18 savol &middot; Fit + Readiness + Roadmap
        </p>
        <p className="text-sm">
          Top-5 yonalish, skill-gap, 6-12 oy shaxsiy roadmap.
        </p>
      </div>

      <Link href="/stage1" className="btn-primary block text-center mt-6">
        Boshlash
      </Link>

      <div className="flex items-center justify-center gap-2 mt-6 text-xs text-[var(--tg-hint)]">
        <TrendingUp className="w-4 h-4" />
        <span>Halol tahlil. Manipulyatsiyasiz.</span>
      </div>
    </main>
  );
}
''')

# ═══════════ app/stage1/page.tsx ═══════════
add("app/stage1/page.tsx", r'''
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchQuestions, submitStage1 } from "@/lib/api";
import { useStore } from "@/lib/store";

type Q = {
  id: string;
  text: string;
  type?: string;
  options?: { v: string; l: string }[];
  max?: number;
};

export default function Stage1Page() {
  const router = useRouter();
  const setStage1 = useStore((s) => s.setStage1);
  const [questions, setQuestions] = useState<Q[]>([]);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQuestions()
      .then((data) => {
        setQuestions(data.stage_1.questions);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!questions.length) return <Err msg="Savollar topilmadi" />;

  const q = questions[current];
  const currentVal = answers[q.id];

  const select = (v: string) => {
    if (q.type === "multi_select") {
      const arr = Array.isArray(currentVal) ? [...currentVal] : [];
      const idx = arr.indexOf(v);
      if (idx >= 0) arr.splice(idx, 1);
      else if (!q.max || arr.length < q.max) arr.push(v);
      setAnswers({ ...answers, [q.id]: arr });
    } else {
      setAnswers({ ...answers, [q.id]: v });
    }
  };

  const isSelected = (v: string) => {
    if (q.type === "multi_select") {
      return Array.isArray(currentVal) && currentVal.includes(v);
    }
    return currentVal === v;
  };

  const canNext = () => {
    if (q.type === "multi_select") return Array.isArray(currentVal) && currentVal.length > 0;
    return !!currentVal;
  };

  const next = async () => {
    if (current < questions.length - 1) {
      setCurrent(current + 1);
      return;
    }
    setSubmitting(true);
    try {
      const res = await submitStage1(answers);
      setStage1(res.stage1_result_id, res);
      router.push("/teaser");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  const progress = ((current + 1) / questions.length) * 100;

  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <div className="h-1 bg-[var(--tg-secondary-bg)] rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-[var(--tg-button)] transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-xs text-[var(--tg-hint)] mb-2">
        {current + 1} / {questions.length}
      </p>
      <h2 className="text-xl font-semibold mb-5">{q.text}</h2>

      <div className="flex flex-col gap-2 mb-6">
        {q.options?.map((o) => (
          <button
            key={o.v}
            onClick={() => select(o.v)}
            className={`text-left p-4 rounded-xl border transition ${
              isSelected(o.v)
                ? "bg-[var(--tg-button)] text-[var(--tg-button-text)] border-transparent"
                : "border-[var(--tg-hint)]/30"
            }`}
          >
            {o.l}
          </button>
        ))}
      </div>

      {q.type === "multi_select" && (
        <p className="text-xs text-[var(--tg-hint)] mb-3 text-center">
          Bir nechtasini tanlashingiz mumkin {q.max ? `(max ${q.max})` : ""}
        </p>
      )}

      <button
        className="btn-primary"
        disabled={!canNext() || submitting}
        onClick={next}
      >
        {submitting
          ? "Yuborilmoqda..."
          : current === questions.length - 1
          ? "Yakunlash"
          : "Keyingisi"}
      </button>
    </main>
  );
}

function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="max-w-md mx-auto px-5 py-10">
      <div className="card">
        <p className="text-red-500">Xatolik: {msg}</p>
      </div>
    </main>
  );
}
''')

# ═══════════ app/teaser/page.tsx ═══════════
add("app/teaser/page.tsx", r'''
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles } from "lucide-react";
import { useStore } from "@/lib/store";
import { createPayment, createStarsInvoice } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);
  const [loading, setLoading] = useState(false);

  if (!teaser || !stage1ResultId) {
    return (
      <main className="max-w-md mx-auto px-5 py-10">
        <p className="mb-4">Natija topilmadi.</p>
        <button className="btn-primary" onClick={() => router.push("/stage1")}>
          Qaytadan boshlash
        </button>
      </main>
    );
  }

  const payClick = async () => {
    setLoading(true);
    try {
      const res = await createPayment(stage1ResultId, "click");
      if (res.pay_url) {
        window.open(res.pay_url, "_blank");
        // TODO: polling
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const payStars = async () => {
    setLoading(true);
    try {
      const res = await createStarsInvoice(stage1ResultId);
      const tg = (window as any).Telegram?.WebApp;
      if (!tg?.openInvoice) {
        alert("Telegram Stars bu qurilmada ishlamaydi. Karta orqali tolang.");
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

  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <h1 className="text-2xl font-bold mb-4">Tezkor natijangiz</h1>

      <div className="card">
        <h3 className="font-semibold mb-3">Kuchli signallaringiz</h3>
        {teaser.top_2_signals?.map((s: any) => (
          <div key={s.key} className="flex justify-between py-1.5">
            <span className="capitalize text-sm">
              {s.key.replace(/_/g, " ")}
            </span>
            <span className="text-[var(--tg-hint)] text-sm">
              {Math.round(s.score * 100)}%
            </span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Mos yonalishlar</h3>
        {teaser.top_2_careers?.map((c: any) => (
          <div
            key={c.career_id}
            className="py-2 border-b border-[var(--tg-hint)]/20 last:border-0"
          >
            <p className="font-medium">{c.career_uz}</p>
            <p className="text-xs text-[var(--tg-hint)]">
              {c.cluster_uz} &middot; Fit: {c.fit}%
            </p>
          </div>
        ))}
        {teaser.locked_count > 0 && (
          <p className="mt-3 text-sm text-amber-400 flex items-center gap-2">
            <Lock className="w-4 h-4" />
            Yana {teaser.locked_count} ta mos yonalish yashirilgan
          </p>
        )}
      </div>

      <div className="card border border-[var(--tg-button)]/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold">Chuqur tahlil</h3>
        </div>
        <ul className="space-y-2 mb-4 text-sm">
          {[
            "Top-5 mos yonalish",
            "Fit + Readiness har biri uchun",
            "Tosiqlar va ularni hal qilish",
            "6-12 oy shaxsiy roadmap",
            "Birinchi 3 qadam",
            "PDF hisobot",
          ].map((t, i) => (
            <li key={i} className="flex gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{t}</span>
            </li>
          ))}
        </ul>

        <div className="flex flex-col gap-2">
          <button
            disabled={loading}
            onClick={payStars}
            className="btn-primary"
          >
            Telegram Stars orqali (150 ⭐)
          </button>
          <button
            disabled={loading}
            onClick={payClick}
            className="btn-primary"
            style={{
              background: "var(--tg-secondary-bg)",
              color: "var(--tg-text)",
            }}
          >
            Karta orqali (39 000 som)
          </button>
        </div>

        <p className="text-xs text-[var(--tg-hint)] mt-3 text-center">
          7 kun ichida pulni qaytarish kafolati
        </p>
      </div>
    </main>
  );
}
''')

# ═══════════ app/stage2/page.tsx ═══════════
add("app/stage2/page.tsx", r'''
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchQuestions, submitStage2 } from "@/lib/api";
import { useStore } from "@/lib/store";

const LIKERT = [
  { v: 1, l: "Umuman yoq" },
  { v: 2, l: "Kam" },
  { v: 3, l: "Ortacha" },
  { v: 4, l: "Kop" },
  { v: 5, l: "Toliq ha" },
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

  const setAnswer = (v: number) =>
    setAnswers({ ...answers, [q.id]: v });

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

  const progress = ((current + 1) / questions.length) * 100;

  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <div className="h-1 bg-[var(--tg-secondary-bg)] rounded-full overflow-hidden mb-6">
        <div
          className="h-full bg-[var(--tg-button)] transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-xs text-[var(--tg-hint)] mb-2">
        {current + 1} / {questions.length}
      </p>
      <h2 className="text-lg font-semibold mb-6">{q.text}</h2>

      <div className="flex flex-col gap-2 mb-6">
        {LIKERT.map((o) => (
          <button
            key={o.v}
            onClick={() => setAnswer(o.v)}
            className={`text-left p-4 rounded-xl border transition ${
              currentVal === o.v
                ? "bg-[var(--tg-button)] text-[var(--tg-button-text)] border-transparent"
                : "border-[var(--tg-hint)]/30"
            }`}
          >
            {o.l}
          </button>
        ))}
      </div>

      <button
        className="btn-primary"
        disabled={!currentVal || submitting}
        onClick={next}
      >
        {submitting
          ? "AI tahlil qilmoqda..."
          : current === questions.length - 1
          ? "Natijani korish"
          : "Keyingisi"}
      </button>
    </main>
  );
}

function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
      <p className="mt-4 text-sm text-[var(--tg-hint)]">Yuklanmoqda...</p>
    </main>
  );
}
''')

# ═══════════ app/report/[id]/page.tsx ═══════════
add("app/report/[id]/page.tsx", r'''
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertTriangle, Target, ExternalLink } from "lucide-react";
import { fetchReport } from "@/lib/api";

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReport(Number(id))
      .then(setData)
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!data) return null;

  const ai = data.ai || {};
  const careers = data.roadmap?.careers || [];

  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <h1 className="text-2xl font-bold mb-4">Sizning natijangiz</h1>

      {ai.summary && (
        <div className="card">
          <h3 className="font-semibold mb-2">Xulosa</h3>
          <p className="text-sm">{ai.summary}</p>
          {ai.source === "fallback" && (
            <p className="text-xs text-[var(--tg-hint)] mt-2">
              (AI vaqtincha ishlamadi - tahlil deterministik)
            </p>
          )}
        </div>
      )}

      {ai.why_this_fits?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-2">Nega bu sizga mos</h3>
          <ul className="space-y-1 text-sm">
            {ai.why_this_fits.map((s: string, i: number) => (
              <li key={i} className="flex gap-2">
                <span className="text-indigo-400">-</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <h2 className="text-lg font-semibold mt-6 mb-3">Top-5 mos yonalish</h2>
      {careers.map((c: any, idx: number) => (
        <div key={c.career.id} className="card">
          <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs text-[var(--tg-hint)]">#{idx + 1}</span>
                <h3 className="font-semibold">{c.career.uz}</h3>
              </div>
              <p className="text-xs text-[var(--tg-hint)]">
                {c.career.cluster_uz}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm">
                Fit: <b>{c.fit}%</b>
              </p>
              <p className="text-sm text-[var(--tg-hint)]">
                Ready: <b>{c.readiness}%</b>
              </p>
            </div>
          </div>

          {c.has_hard_barrier && (
            <div className="flex items-center gap-2 text-xs text-red-400 mt-2 mb-2">
              <AlertTriangle className="w-3 h-3" />
              Jiddiy tosiq bor
            </div>
          )}

          {c.roadmap?.barrier_resolutions?.length > 0 && (
            <div className="mt-3 p-3 bg-[var(--tg-bg)] rounded-lg">
              <p className="text-xs font-semibold mb-1">Tosiqlarni hal qilish:</p>
              {c.roadmap.barrier_resolutions.map((b: any, i: number) => (
                <p key={i} className="text-xs">
                  - {b.action}
                </p>
              ))}
            </div>
          )}

          {c.roadmap?.is_placeholder ? (
            <p className="text-xs text-[var(--tg-hint)] mt-3">
              Bu yonalish uchun batafsil roadmap tez orada qoshiladi.
            </p>
          ) : (
            <>
              <div className="mt-3">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-4 h-4 text-emerald-400" />
                  <p className="text-sm font-semibold">Birinchi 3 qadam</p>
                </div>
                <ol className="text-sm space-y-1 list-decimal list-inside ml-1">
                  {c.roadmap?.first_3_actions?.map((a: string, i: number) => (
                    <li key={i}>{a}</li>
                  ))}
                </ol>
              </div>

              {c.roadmap?.phases?.length > 0 && (
                <details className="mt-3">
                  <summary className="cursor-pointer text-sm font-semibold">
                    Toliq roadmap
                  </summary>
                  <div className="mt-3 space-y-3">
                    {c.roadmap.phases.map((p: any, i: number) => (
                      <div key={i}>
                        <p className="text-sm font-semibold">
                          {p.period} - {p.goal}
                        </p>
                        <ul className="text-xs mt-1 space-y-0.5 list-disc list-inside">
                          {p.actions.map((a: string, j: number) => (
                            <li key={j}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </details>
              )}

              {c.roadmap?.resources?.length > 0 && (
                <details className="mt-2">
                  <summary className="cursor-pointer text-sm font-semibold">
                    Resurslar
                  </summary>
                  <ul className="text-sm mt-2 space-y-1">
                    {c.roadmap.resources.map((r: any, i: number) => (
                      <li key={i}>
                        <a
                          href={r.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[var(--tg-link)] underline inline-flex items-center gap-1"
                        >
                          {r.name} <ExternalLink className="w-3 h-3" />
                        </a>
                      </li>
                    ))}
                  </ul>
                </details>
              )}

              {c.roadmap?.risks?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold mb-1 text-amber-400">
                    Ehtiyot boling
                  </p>
                  <ul className="text-xs space-y-0.5 list-disc list-inside">
                    {c.roadmap.risks.map((r: string, i: number) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      ))}

      {ai.risks?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-2 text-amber-400">
            Umumiy ogohlantirishlar
          </h3>
          <ul className="text-sm space-y-1 list-disc list-inside">
            {ai.risks.map((r: string, i: number) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {ai.next_step_emphasis && (
        <div className="card border border-[var(--tg-button)]/30">
          <h3 className="font-semibold mb-2">Eng muhim qadam</h3>
          <p className="text-sm">{ai.next_step_emphasis}</p>
        </div>
      )}

      <button className="btn-primary mt-6" onClick={() => window.print()}>
        PDF sifatida saqlash
      </button>
    </main>
  );
}

function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
      <p className="mt-4 text-sm text-[var(--tg-hint)]">Tahlil yuklanmoqda...</p>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="max-w-md mx-auto px-5 py-10">
      <div className="card">
        <p className="text-red-500">Xatolik: {msg}</p>
      </div>
    </main>
  );
}
''')


def main():
    print("=" * 60)
    print("QADAM Web: Qism B - sahifalar")
    print("=" * 60)
    for path, content in FILES.items():
        full = ROOT / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] " + path)
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yaratildi!")
    print()
    print("KEYINGI: npm install")


if __name__ == "__main__":
    main()