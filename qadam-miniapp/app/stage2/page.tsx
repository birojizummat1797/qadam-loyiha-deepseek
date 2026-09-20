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
