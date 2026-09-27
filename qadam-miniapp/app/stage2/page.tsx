"use client";

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
