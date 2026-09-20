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
