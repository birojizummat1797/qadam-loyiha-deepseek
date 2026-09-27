"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import {
  startDiscovery, submitDiscoveryAnswer, completeDiscovery,
} from "@/lib/api";

type Question = {
  id: string;
  type: string;
  text: string;
  index: number;
  total: number;
  options: { id: string; label: string }[] | null;
};

type Answer = {
  question_id: string;
  answer_id: string;
  answer_value: number;
};

const LIKERT = [
  { value: 1, label: "Umuman yo'q" },
  { value: 2, label: "Kam" },
  { value: 3, label: "O'rtacha" },
  { value: 4, label: "Ko'p" },
  { value: 5, label: "To'liq ha" },
];

export default function DiscoveryPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<{ id: string; value: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session boshlash
  useEffect(() => {
    startDiscovery()
      .then((r) => {
        setSessionId(r.session_id);
        setQuestion(r.current_question);
        setLoading(false);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e.message);
        setLoading(false);
      });
  }, []);

  const handleSelect = (optionId: string, value: number) => {
    setSelected({ id: optionId, value });
  };

  const handleNext = async () => {
    if (!sessionId || !question || !selected) return;
    setSubmitting(true);
    try {
      const r = await submitDiscoveryAnswer(
        sessionId, question.id, selected.id, selected.value
      );
      if (r.next_question) {
        setQuestion(r.next_question);
        setSelected(null);
      } else {
        // Discovery tugadi — complete
        const result = await completeDiscovery(sessionId);
        try {
          sessionStorage.setItem("discovery_result", JSON.stringify(result));
          sessionStorage.setItem("discovery_session_id", String(sessionId));
        } catch {}
        router.push("/preliminary");
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!question) return <Loader />;

  const progress = ((question.index + 1) / question.total) * 100;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* TOP */}
        <div className="pt-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            <span className="t-caption text-subtle">Discovery</span>
            <span className="t-caption text-subtle">
              {question.index + 1} / {question.total}
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

        {/* QUESTION */}
        <AnimatePresence mode="wait">
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="flex-1 flex flex-col"
          >
            <h2 className="t-title mb-8 mt-4">{question.text}</h2>

            <div className="flex flex-col gap-2.5 mb-6">
              {question.type === "likert"
                ? LIKERT.map((o, idx) => {
                    const isSel = selected?.value === o.value && selected?.id === `likert_${o.value}`;
                    return (
                      <motion.button
                        key={o.value}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.03, duration: 0.2 }}
                        onClick={() => handleSelect(`likert_${o.value}`, o.value)}
                        className={`option-btn ${isSel ? "selected" : ""}`}
                      >
                        <span>{o.label}</span>
                        <span className="option-indicator">
                          {isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                        </span>
                      </motion.button>
                    );
                  })
                : question.options?.map((o, idx) => {
                    const isSel = selected?.id === o.id;
                    // Choice option → value optdan keladi (bu yerda 3 default)
                    const val = 3;
                    return (
                      <motion.button
                        key={o.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.03, duration: 0.2 }}
                        onClick={() => handleSelect(o.id, val)}
                        className={`option-btn ${isSel ? "selected" : ""}`}
                      >
                        <span>{o.label}</span>
                        <span className="option-indicator">
                          {isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                        </span>
                      </motion.button>
                    );
                  })}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* NEXT */}
        <div className="pb-6">
          <button
            onClick={handleNext}
            disabled={!selected || submitting}
            className="btn btn-primary"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
            ) : question.index === question.total - 1 ? (
              "Yakunlash"
            ) : (
              "Keyingisi"
            )}
          </button>
        </div>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-6">
        <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />
      </div>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-8">
        <div className="card-clean border-[var(--color-danger)]/40">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
