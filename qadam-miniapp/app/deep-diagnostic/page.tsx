"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { api, getInitData, isGateRequired } from "@/lib/api";
import AgeGate from "@/components/AgeGate";

const LIKERT = [
  { value: 1, label: "Umuman yo'q" },
  { value: 2, label: "Kam" },
  { value: 3, label: "O'rtacha" },
  { value: 4, label: "Ko'p" },
  { value: 5, label: "To'liq ha" },
];

export default function DeepDiagnosticPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState<any>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needGate, setNeedGate] = useState(false);
  const [attempt, setAttempt] = useState(0);

  const discoverySessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("discovery_session_id")) || null
    : null;

  useEffect(() => {
    api.post("/api/v1/deep-diagnostic", {
      init_data: getInitData(),
      discovery_session_id: discoverySessionId,
    })
      .then((r) => {
        setSessionId(r.data.session_id);
        setQuestion(r.data.current_question);
        setLoading(false);
      })
      .catch((e) => {
        if (isGateRequired(e)) setNeedGate(true);
        else setError(e?.response?.data?.detail || e.message);
        setLoading(false);
      });
  }, [discoverySessionId, attempt]);

  const handleNext = async () => {
    if (!sessionId || !question || selected === null) return;
    setSubmitting(true);
    try {
      const r = await api.post(`/api/v1/deep-diagnostic/${sessionId}/answers`, {
        init_data: getInitData(),
        question_id: question.id,
        answer_value: selected,
      });
      if (r.data.next_question) {
        setQuestion(r.data.next_question);
        setSelected(null);
      } else {
        // Complete
        const completeRes = await api.post(`/api/v1/deep-diagnostic/${sessionId}/complete`, {
          init_data: getInitData(),
        });
        sessionStorage.setItem("dd_result", JSON.stringify(completeRes.data));
        sessionStorage.setItem("dd_session_id", String(sessionId));
        router.push("/career-intelligence");
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (needGate) {
    return <AgeGate onPassed={() => { setNeedGate(false); setLoading(true); setAttempt((a) => a + 1); }} />;
  }
  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!question) return <Loader />;

  const progress = ((question.index + 1) / question.total) * 100;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        <div className="pt-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            <span className="t-caption text-subtle">
              {question.dimension_uz || "Chuqur tahlil"}
              <span className="ml-2 px-1.5 py-0.5 rounded bg-[var(--color-primary-soft)] text-primary">Beta</span>
            </span>
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

        <AnimatePresence mode="wait">
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25 }}
            className="flex-1 flex flex-col"
          >
            <h2 className="t-title mb-8 mt-4">{question.text}</h2>
            <div className="flex flex-col gap-2.5 mb-6">
              {LIKERT.map((o, idx) => {
                const isSel = selected === o.value;
                return (
                  <motion.button
                    key={o.value}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.03, duration: 0.2 }}
                    onClick={() => setSelected(o.value)}
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

        <div className="pb-6">
          <button
            onClick={handleNext}
            disabled={selected === null || submitting}
            className="btn btn-primary"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
            ) : question.index === question.total - 1 ? (
              "Natijani ko'rish"
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
