"use client";

import { ContextNote, EvidenceBadge } from "@/components/EvidenceLevel";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Sparkles, AlertCircle, Trophy } from "lucide-react";
import { fetchReport } from "@/lib/api";
import { RoadmapView } from "@/components/RoadmapView";
import { PdfDownloader } from "@/components/PdfDownloader";
import { FeedbackModal } from "@/components/FeedbackModal";
import { CloseButton } from "@/components/CloseButton";
import { SkeletonReport } from "@/components/Skeleton";

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
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6 print-full">
        {/* ═══ HEADER ═══ */}
        <div className="mb-8 fade-in">
          <h1 className="t-title mb-1">Sizning natijangiz</h1>
          <p className="t-small text-muted">
            {new Date(data.created_at).toLocaleDateString("uz", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>

        {/* ═══ AI SUMMARY ═══ */}
        {ai.summary && (
          <div className="card-clean mb-6 fade-in fade-in-1">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-primary" />
              <h3 className="t-heading">Xulosa</h3>
            </div>
            <p className="t-body text-muted">{ai.summary}</p>
            {ai.source === "fallback" && (
              <p className="t-caption text-subtle mt-3 italic">
                (AI vaqtincha ishlamadi)
              </p>
            )}
          </div>
        )}

        {/* ═══ CAREERS HEADER ═══ */}
        <div className="flex items-center gap-2 mb-4 fade-in fade-in-2">
          <Trophy className="w-4 h-4 text-warning" />
          <h2 className="t-heading">Signallaringizga yaqinroq yo&apos;nalishlar</h2>
        </div>

        {/* ═══ CAREERS ═══ */}
        {careers.map((c: any, idx: number) => (
          <div key={c.career.id} className="mb-6">
            {/* Career header */}
            <div className="card-clean mb-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="badge-soft badge-primary">
                      #{idx + 1}
                    </span>
                  </div>
                  <h3 className="t-heading mb-1">{c.career.uz}</h3>
                  <p className="t-small text-muted">{c.career.cluster_uz}</p>
                </div>

                <div className="text-right shrink-0">
                  <EvidenceBadge level={c.evidence_level} coverage={c.coverage} />
                </div>
              </div>

              <div className="divider" />

              <div className="flex flex-col gap-2">
                <span className="t-caption text-subtle">Hozirgi sharoit</span>
                <ContextNote readiness={c.readiness} barriers={c.barriers} />
              </div>

              {c.has_hard_barrier && (
                <div className="mt-4 pt-4 border-t border-[var(--color-border)] flex items-start gap-2">
                  <AlertCircle className="w-3.5 h-3.5 text-danger shrink-0 mt-0.5" />
                  <p className="t-small text-danger">
                    Hozir jiddiy to&apos;siq mavjud — yechim pastda
                  </p>
                </div>
              )}
            </div>

            {/* Roadmap */}
            <RoadmapView roadmap={c.roadmap} />
          </div>
        ))}

        {/* ═══ GLOBAL RISKS ═══ */}
        {ai.risks?.length > 0 && (
          <div className="card-clean mb-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-4 h-4 text-warning" />
              <h3 className="t-heading">Ogohlantirishlar</h3>
            </div>
            <ul className="space-y-2">
              {ai.risks.map((r: string, i: number) => (
                <li key={i} className="flex gap-2 t-small">
                  <span className="text-warning shrink-0">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* ═══ NEXT STEP ═══ */}
        {ai.next_step_emphasis && (
          <div className="card-clean mb-6">
            <h3 className="t-heading mb-2">Eng muhim qadam</h3>
            <p className="t-body text-muted">{ai.next_step_emphasis}</p>
          </div>
        )}

        {/* ═══ ACTIONS ═══ */}
        <div className="space-y-3 pt-2">
          <PdfDownloader reportId={Number(id)} />
          <FeedbackModal reportId={Number(id)} />
        </div>

        <CloseButton />

        <p className="t-caption text-subtle text-center pt-4">
          Hisobot versiyasi: {data.versions?.roadmap_kb ?? "v2.0"}
        </p>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8">
        <SkeletonReport />
      </div>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8">
        <div className="card-clean border-[var(--color-danger)]/40">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
