"use client";

/** Diagnostic v2 — roadmap for one career (live v2 KB or the v3 draft KB). Draft route. */
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { RoadmapView } from "@/components/RoadmapView";
import { v2Roadmap } from "@/lib/api-v2";

export default function V2RoadmapPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    v2Roadmap(id)
      .then(setData)
      .catch((e) => setError(e?.response?.data?.detail || e.message));
  }, [id]);

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6 pb-8">
        <button onClick={() => router.back()} className="flex items-center gap-1 t-small text-muted mb-6">
          <ChevronLeft className="w-4 h-4" />
          Orqaga
        </button>
        {error && <div className="card-clean"><p className="t-small text-danger">{error}</p></div>}
        {!error && !data && (
          <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />
        )}
        {data && (
          <>
            {data.version === "v3.0-draft" && (
              <p className="t-caption text-subtle mb-3">Yo‘l xaritasi — qoralama (ko‘rib chiqilmoqda)</p>
            )}
            <h1 className="t-title mb-6">{data.career_uz}</h1>
            <RoadmapView roadmap={data} />
          </>
        )}
      </div>
    </main>
  );
}
