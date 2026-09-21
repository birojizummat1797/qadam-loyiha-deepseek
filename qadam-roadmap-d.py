# -*- coding: utf-8 -*-
"""QADAM Roadmap v2.0 — Part D: report/page.tsx yangilash."""
from pathlib import Path

FRONTEND = Path("qadam-miniapp/app/report/[id]/page.tsx")

report_page = r'''"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Sparkles, AlertCircle } from "lucide-react";
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
    <main className="max-w-md mx-auto px-5 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Sizning natijangiz</h1>
        <p className="text-xs text-[var(--tg-hint)]">
          Sana: {new Date(data.created_at).toLocaleDateString("uz")}
        </p>
      </div>

      {/* AI Summary */}
      {ai.summary && (
        <div className="card border border-indigo-500/30">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h3 className="font-semibold">Umumiy xulosa</h3>
          </div>
          <p className="text-sm leading-relaxed">{ai.summary}</p>
          {ai.source === "fallback" && (
            <p className="text-[10px] text-[var(--tg-hint)] mt-2 italic">
              (AI vaqtincha ishlamadi — tahlil deterministik tizimdan)
            </p>
          )}
        </div>
      )}

      {/* Why fits */}
      {ai.why_this_fits?.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-3">Nega bu sizga mos</h3>
          <ul className="space-y-2">
            {ai.why_this_fits.map((s: string, i: number) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-emerald-400 shrink-0">&rarr;</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Careers — yangi roadmap view bilan */}
      <h2 className="text-lg font-semibold mt-6 mb-3">
        Top-{careers.length} mos yonalish
      </h2>

      {careers.map((c: any, idx: number) => (
        <div key={c.career.id} className="mb-6">
          {/* Career header card */}
          <div className="card mb-2">
            <div className="flex justify-between items-start mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-medium">
                    #{idx + 1}
                  </span>
                  <h3 className="font-semibold text-base">{c.career.uz}</h3>
                </div>
                <p className="text-xs text-[var(--tg-hint)]">{c.career.cluster_uz}</p>
              </div>
              <div className="text-right shrink-0">
                <div className="mb-1">
                  <span className="text-[10px] text-[var(--tg-hint)]">Fit</span>
                  <p className="text-lg font-bold text-emerald-400 leading-none">
                    {c.fit}%
                  </p>
                </div>
                <div>
                  <span className="text-[10px] text-[var(--tg-hint)]">Ready</span>
                  <p className="text-sm font-semibold">{c.readiness}%</p>
                </div>
              </div>
            </div>

            {c.has_hard_barrier && (
              <div className="flex items-center gap-2 text-xs text-red-400 mt-2 pt-2 border-t border-[var(--tg-hint)]/20">
                <AlertCircle className="w-3 h-3" />
                <span>Hozir jiddiy tosiq bor — quyida yechim bor</span>
              </div>
            )}
          </div>

          {/* Roadmap — yangi komponent */}
          <RoadmapView roadmap={c.roadmap} />
        </div>
      ))}

      {/* Global risks */}
      {ai.risks?.length > 0 && (
        <div className="card border border-amber-500/30">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            Umumiy ogohlantirishlar
          </h3>
          <ul className="space-y-2 text-sm">
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
        <div className="card border border-amber-500/40 bg-amber-500/5">
          <h3 className="font-semibold mb-2 flex items-center gap-2">
            <span className="text-amber-400 text-lg">&#127919;</span>
            Eng muhim qadam
          </h3>
          <p className="text-sm leading-relaxed">{ai.next_step_emphasis}</p>
        </div>
      )}

      {/* PDF tugma */}
      <button
        className="btn-primary mt-6"
        onClick={() => window.print()}
      >
        PDF sifatida saqlash
      </button>

      <p className="text-[10px] text-[var(--tg-hint)] text-center mt-4">
        Hisobot versiyasi: {data.versions?.roadmap_kb ?? "v2.0"}
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
      <div className="card border border-red-500/30">
        <p className="text-red-400">Xatolik: {msg}</p>
      </div>
    </main>
  );
}
'''

FRONTEND.write_text(report_page, encoding="utf-8")
print("=" * 60)
print("[OK] qadam-miniapp/app/report/[id]/page.tsx yangilandi")
print("=" * 60)
print()
print("Keyingi qadam: git push")