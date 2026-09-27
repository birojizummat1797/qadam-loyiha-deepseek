# -*- coding: utf-8 -*-
"""Qadam.io — Redesign v3.2: Welcome fix + Stage 1 (minimal, professional)."""
from pathlib import Path

FRONTEND = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. WELCOME — max-width, proportional buttons
# ═══════════════════════════════════════════════════════════
PAGE = FRONTEND / "app/page.tsx"

PAGE.write_text(r'''"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* ═══ LOGO ═══ */}
        <div className="pt-8 pb-16 fade-in">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-base">Q</span>
          </div>
        </div>

        {/* ═══ MAIN ═══ */}
        <div className="flex-1">
          <h1 className="t-display mb-6 fade-in fade-in-1">
            Professional
            <br />
            yo&apos;lingizni taxmin
            <br />
            emas,{" "}
            <span className="text-primary">dalillar</span>
            <br />
            <span className="text-primary">bilan</span> aniqlang.
          </h1>

          <p className="t-body text-muted mb-10 fade-in fade-in-2">
            Qadam.io profilingizni tahlil qiladi, sizga mos kasblarni
            aniqlaydi va amaliy yo&apos;l xaritasi tuzadi.
          </p>

          <ul className="space-y-3 mb-12 fade-in fade-in-3">
            {[
              "8 savol — 3 daqiqa",
              "Fit va Readiness tahlili",
              "Shaxsiy 6 oylik yo'l xaritasi",
            ].map((text, i) => (
              <li
                key={i}
                className="flex items-center gap-3 t-body text-muted"
              >
                <span className="w-1 h-1 rounded-full bg-primary shrink-0" />
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* ═══ ACTIONS ═══ */}
        <div className="space-y-2 pb-6 fade-in fade-in-4">
          <Link href="/stage1" className="block">
            <button className="btn btn-primary">
              <span>Boshlash</span>
              <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
            </button>
          </Link>

          <button className="btn btn-ghost">
            Qadam.io qanday ishlaydi?
          </button>
        </div>

        <p className="text-center t-caption text-subtle pb-4 fade-in fade-in-5">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/page.tsx — Welcome fix")

# ═══════════════════════════════════════════════════════════
# 2. STAGE 1 — variant tanlash + button
# ═══════════════════════════════════════════════════════════
STAGE1 = FRONTEND / "app/stage1/page.tsx"

STAGE1.write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check } from "lucide-react";
import { fetchQuestions, submitStage1 } from "@/lib/api";
import { useStore } from "@/lib/store";
import { SkeletonQuestion } from "@/components/Skeleton";

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
    if (q.type === "multi_select") {
      return Array.isArray(currentVal) && currentVal.length > 0;
    }
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

          {/* Progress line */}
          <div className="h-px bg-[var(--color-border)] relative overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
        </div>

        {/* ═══ QUESTION + OPTIONS ═══ */}
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
              {q.options?.map((o, idx) => {
                const selected = isSelected(o.v);
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
                    onClick={() => select(o.v)}
                    className={`w-full text-left rounded-xl px-5 py-4 transition-all duration-150 flex items-center justify-between gap-3 ${
                      selected
                        ? "bg-[var(--color-primary-soft)] border border-primary"
                        : "bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-border-strong)]"
                    }`}
                    style={{
                      minHeight: "60px",
                    }}
                  >
                    <span className="t-body">{o.l}</span>

                    <span
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-all ${
                        selected
                          ? "bg-primary border-primary"
                          : "border-[var(--color-border-strong)]"
                      }`}
                    >
                      {selected && (
                        <Check
                          className="w-3 h-3 text-white"
                          strokeWidth={3}
                        />
                      )}
                    </span>
                  </motion.button>
                );
              })}
            </div>

            {q.type === "multi_select" && (
              <p className="t-caption text-subtle text-center mb-4">
                Bir nechtasini tanlash mumkin
                {q.max ? ` · maks ${q.max}` : ""}
              </p>
            )}
          </motion.div>
        </AnimatePresence>

        {/* ═══ NEXT BUTTON ═══ */}
        <div className="pb-6">
          <button
            onClick={next}
            disabled={!canNext() || submitting}
            className="btn btn-primary"
          >
            {submitting
              ? "Yuborilmoqda..."
              : current === questions.length - 1
              ? "Yakunlash"
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

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6">
        <div className="p-4 rounded-xl bg-[var(--color-danger-soft)] border border-[var(--color-danger)]/30">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/stage1/page.tsx — yangi dizayn")

# ═══════════════════════════════════════════════════════════
# 3. globals.css — .btn-primary width fix
# ═══════════════════════════════════════════════════════════
GLOBALS = FRONTEND / "app/globals.css"
css = GLOBALS.read_text(encoding="utf-8")

# btn-primary dan width:100% olib tashlash
css = css.replace(
    """.btn-primary {
  background: var(--color-primary);
  color: #FFFFFF;
  width: 100%;
}""",
    """.btn-primary {
  background: var(--color-primary);
  color: #FFFFFF;
  width: 100%;
  /* width inherited from parent container with max-width */
}""",
)

GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — btn width")