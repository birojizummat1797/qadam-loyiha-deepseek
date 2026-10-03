"use client";

import { ContextNote, EvidenceBadge } from "@/components/EvidenceLevel";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ChevronLeft, Target, AlertCircle, Rocket, BookOpen,
  Calendar, CheckCircle2, ExternalLink,
} from "lucide-react";
import { api, getInitData } from "@/lib/api";

export default function RoadmapPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ddSessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("dd_session_id"))
    : null;

  useEffect(() => {
    if (!slug || !ddSessionId) {
      router.push("/career-intelligence");
      return;
    }
    api.get(`/api/v1/roadmap/${slug}`, {
      params: { init_data: getInitData(), session_id: ddSessionId },
    })
      .then((r) => setData(r.data))
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false));
  }, [slug, ddSessionId, router]);

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!data) return null;

  const rm = data.roadmap || {};

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6 pb-8">
        {/* Back */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 t-small text-muted mb-6"
        >
          <ChevronLeft className="w-4 h-4" />
          Orqaga
        </button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <p className="t-caption text-primary mb-2">Shaxsiy yo&apos;l xaritasi</p>
          <h1 className="t-display mb-4">{rm.career_uz || slug}</h1>

          {/* Dalil darajasi va sharoit (foizsiz) */}
          <div className="card-clean mb-4 flex flex-col gap-3">
            <div className="flex items-center justify-between gap-3">
              <span className="t-caption text-subtle">Dalil darajasi</span>
              <EvidenceBadge level={data.evidence_level} coverage={data.coverage} />
            </div>
            {data.readiness != null && (
              <div className="flex flex-col gap-2">
                <span className="t-caption text-subtle">Hozirgi sharoit</span>
                <ContextNote readiness={data.readiness} barriers={data.barriers} />
              </div>
            )}
          </div>

          {data.has_hard_barrier && (
            <div className="flex items-start gap-2 p-3 rounded-xl bg-[var(--color-danger-soft)] border border-[var(--color-danger)]/30">
              <AlertCircle className="w-4 h-4 text-danger shrink-0 mt-0.5" />
              <p className="t-small text-danger">
                Hozir jiddiy to&apos;siq mavjud — pastdagi yechimga qarang.
              </p>
            </div>
          )}
        </motion.div>

        {/* Why */}
        {rm.why && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-2">Nega bu yo&apos;nalish ko&apos;rsatildi</p>
            <p className="t-small text-muted">{rm.why}</p>
          </motion.div>
        )}

        {/* Barrier resolutions */}
        {rm.barrier_resolutions?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card-clean mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-4 h-4 text-warning" />
              <p className="t-heading">To&apos;siqlar va yechim</p>
            </div>
            <ul className="space-y-2">
              {rm.barrier_resolutions.map((b: any, i: number) => (
                <li key={i} className="flex items-start gap-2 t-small">
                  <span className={`badge-soft ${b.level === "hard" ? "badge-danger" : "badge-warning"}`}>
                    {b.level === "hard" ? "Kuchli" : "Yengil"}
                  </span>
                  <span className="flex-1 text-muted">{b.action}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Next 3 actions */}
        {rm.next_3_actions?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="rounded-2xl p-5 mb-6 bg-gradient-to-br from-indigo-500/10 to-purple-500/5 border border-primary/30"
          >
            <div className="flex items-center gap-2 mb-3">
              <Rocket className="w-4 h-4 text-primary" />
              <p className="t-heading">Birinchi 3 qadam</p>
            </div>
            <p className="t-caption text-subtle mb-3">Bugun boshlang</p>
            <ol className="space-y-3">
              {rm.next_3_actions.map((a: string, i: number) => (
                <li key={i} className="flex items-start gap-3 t-small">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-white text-xs font-semibold shrink-0">
                    {i + 1}
                  </span>
                  <span>{a}</span>
                </li>
              ))}
            </ol>
          </motion.div>
        )}

        {/* Phases */}
        {rm.phases?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="w-4 h-4 text-primary" />
              <p className="t-heading">Yo&apos;l xaritasi</p>
            </div>

            <div className="relative">
              <div className="absolute left-[11px] top-2 bottom-2 w-px bg-[var(--color-border)]" />
              <div className="space-y-4">
                {rm.phases.map((p: any, i: number) => (
                  <div key={i} className="relative pl-8">
                    <div className="absolute left-0 top-0 w-6 h-6 rounded-full bg-[var(--color-surface-2)] border-2 border-primary flex items-center justify-center text-xs font-bold text-primary">
                      {i + 1}
                    </div>
                    <div className="card-clean">
                      <p className="t-caption text-primary mb-1">{p.period}</p>
                      <p className="t-heading mb-3">{p.goal}</p>

                      {p.skills?.length > 0 && (
                        <div className="mb-3">
                          <p className="t-caption text-subtle mb-1.5">Ko&apos;nikmalar</p>
                          <div className="flex flex-wrap gap-1">
                            {p.skills.map((s: string, j: number) => (
                              <span key={j} className="badge-soft badge-primary">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {p.actions?.length > 0 && (
                        <div className="mb-3">
                          <p className="t-caption text-subtle mb-1.5">Amallar</p>
                          <ul className="space-y-1">
                            {p.actions.map((a: string, j: number) => (
                              <li key={j} className="flex items-start gap-2 t-small text-muted">
                                <span className="text-primary shrink-0">•</span>
                                <span>{a}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {p.milestone && (
                        <div className="pt-2 mt-2 border-t border-[var(--color-border)] flex items-center gap-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0" />
                          <span className="t-caption text-muted">{p.milestone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Resources */}
        {rm.resources?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="card-clean mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-4 h-4 text-primary" />
              <p className="t-heading">Resurslar</p>
            </div>
            <div className="space-y-2">
              {rm.resources.map((r: any, i: number) => (
                <a
                  key={i}
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-2.5 rounded-lg bg-[var(--color-surface-2)] hover:bg-[var(--color-surface-2)]/80 transition"
                >
                  <span className="t-small">{r.name}</span>
                  <ExternalLink className="w-3.5 h-3.5 text-subtle" />
                </a>
              ))}
            </div>
          </motion.div>
        )}

        {/* Salary (B nuqta) */}
        {rm.b_point?.salary_usd && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-3">Daromad salohiyati (oyiga)</p>
            <div className="space-y-2">
              {["junior", "middle", "senior"].map((lvl) => {
                const s = rm.b_point.salary_usd[lvl];
                if (!s) return null;
                return (
                  <div key={lvl} className="flex items-center justify-between">
                    <span className="t-small capitalize text-muted">{lvl}</span>
                    <span className="t-heading tabular-nums">
                      ${s.min} — ${s.max}
                    </span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        <p className="t-caption text-subtle text-center pt-4">
          Halol tahlil · Manipulyatsiyasiz
        </p>
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
