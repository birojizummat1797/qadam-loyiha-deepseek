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
