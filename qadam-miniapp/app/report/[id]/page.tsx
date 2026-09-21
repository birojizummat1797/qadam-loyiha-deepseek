"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, AlertCircle, Trophy } from "lucide-react";
import { fetchReport } from "@/lib/api";
import { RoadmapView } from "@/components/RoadmapView";

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
    <main className="max-w-md lg:max-w-4xl mx-auto px-4 py-6 print-full">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-5"
      >
        <h1 className="text-2xl font-bold mb-1">Sizning natijangiz</h1>
        <p className="text-xs text-[var(--tg-hint)]">
          {new Date(data.created_at).toLocaleDateString("uz", {
            year: "numeric", month: "long", day: "numeric",
          })}
        </p>
      </motion.div>

      {/* AI Summary */}
      {ai.summary && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl p-5 mb-4 bg-gradient-to-br from-indigo-500/15 to-purple-500/10 border border-indigo-500/30"
        >
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-full bg-indigo-500/20 flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <h3 className="font-semibold text-sm">Umumiy xulosa</h3>
          </div>
          <p className="text-sm leading-relaxed">{ai.summary}</p>
          {ai.source === "fallback" && (
            <p className="text-[10px] text-[var(--tg-hint)] mt-2 italic">
              (AI vaqtincha ishlamadi)
            </p>
          )}
        </motion.div>
      )}

      {/* Top-5 header */}
      <div className="flex items-center gap-2 my-5">
        <Trophy className="w-4 h-4 text-amber-400" />
        <h2 className="font-semibold">Top-3 mos yonalish</h2>
      </div>

      {/* Careers */}
      {careers.map((c: any, idx: number) => (
        <div key={c.career.id} className="mb-6">
          {/* Career header — gradient border */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="rounded-2xl p-4 mb-3 bg-gradient-to-br from-[var(--tg-secondary-bg)] to-[var(--tg-bg)] border border-[var(--tg-hint)]/20 relative overflow-hidden"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 font-bold">
                    #{idx + 1}
                  </span>
                  <h3 className="font-bold text-base truncate">{c.career.uz}</h3>
                </div>
                <p className="text-xs text-[var(--tg-hint)]">{c.career.cluster_uz}</p>
              </div>

              {/* Fit circle */}
              <div className="relative w-16 h-16 shrink-0">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 64 64">
                  <circle cx="32" cy="32" r="28" fill="none" stroke="currentColor" strokeWidth="4" className="text-[var(--tg-hint)]/10" />
                  <circle
                    cx="32" cy="32" r="28" fill="none"
                    stroke="url(#fitGradient)" strokeWidth="4" strokeLinecap="round"
                    strokeDasharray={`${(c.fit / 100) * 176} 176`}
                  />
                  <defs>
                    <linearGradient id="fitGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#a855f7" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-sm font-bold leading-none">{Math.round(c.fit)}%</span>
                  <span className="text-[8px] text-[var(--tg-hint)] mt-0.5">FIT</span>
                </div>
              </div>
            </div>

            {/* Readiness */}
            <div className="mt-3 pt-3 border-t border-[var(--tg-hint)]/15 flex items-center justify-between">
              <span className="text-[10px] text-[var(--tg-hint)] uppercase tracking-wider">Readiness</span>
              <span className="text-sm font-semibold text-emerald-400">{Math.round(c.readiness)}%</span>
            </div>

            {c.has_hard_barrier && (
              <div className="mt-2 pt-2 border-t border-[var(--tg-hint)]/15 flex items-center gap-1.5 text-[11px] text-red-400">
                <AlertCircle className="w-3 h-3" />
                <span>Jiddiy tosiq — yechim pastda</span>
              </div>
            )}
          </motion.div>

          {/* Roadmap */}
          <RoadmapView roadmap={c.roadmap} />
        </div>
      ))}

      {/* Global risks */}
      {ai.risks?.length > 0 && (
        <div className="rounded-2xl p-5 mb-4 bg-amber-500/10 border border-amber-500/30">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            <h3 className="font-semibold text-sm">Umumiy ogohlantirishlar</h3>
          </div>
          <ul className="space-y-1.5 text-sm">
            {ai.risks.map((r: string, i: number) => (
              <li key={i} className="flex gap-2">
                <span className="text-amber-400 shrink-0">&bull;</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Next step emphasis */}
      {ai.next_step_emphasis && (
        <div className="rounded-2xl p-5 mb-4 bg-gradient-to-br from-amber-500/15 to-orange-500/10 border border-amber-500/40">
          <h3 className="font-semibold mb-2 flex items-center gap-2 text-sm">
            <span className="text-lg">&#127919;</span>
            Eng muhim qadam
          </h3>
          <p className="text-sm leading-relaxed">{ai.next_step_emphasis}</p>
        </div>
      )}

      {/* PDF */}
      <button className="btn-primary mt-6" onClick={() => window.print()}>
        PDF sifatida saqlash
      </button>

      <p className="text-[10px] text-[var(--tg-hint)] text-center mt-4">
        Hisobot versiyasi: v{data.versions?.roadmap_kb ?? "2.0"}
      </p>
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
      <div className="rounded-2xl p-5 bg-red-500/10 border border-red-500/30">
        <p className="text-red-400 text-sm">Xatolik: {msg}</p>
      </div>
    </main>
  );
}
