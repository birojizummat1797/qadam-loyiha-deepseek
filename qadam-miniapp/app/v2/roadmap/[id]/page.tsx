"use client";

/**
 * Diagnostic v2 — roadmap for one career (live v2 KB or the v3 draft KB). Draft route.
 * After the roadmap opens, the same roadmap is sent to the bot chat as a PDF
 * (founder request 2026-10-08). The server skips repeats within its cooldown.
 */
import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { CheckCircle2, ChevronLeft, FileText, Loader2 } from "lucide-react";
import { RoadmapView } from "@/components/RoadmapView";
import { v2Roadmap, v2SendRoadmapPdf } from "@/lib/api-v2";

type PdfState = "idle" | "sending" | "sent" | "already" | "failed" | "unavailable";

export default function V2RoadmapPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [pdf, setPdf] = useState<PdfState>("idle");
  const autoSent = useRef(false);

  const sendPdf = (force: boolean) => {
    if (!id) return;
    setPdf("sending");
    v2SendRoadmapPdf(id, force)
      .then((r) => setPdf(r.sent_to_telegram ? "sent" : r.already_sent ? "already" : "failed"))
      .catch((e) => setPdf(e?.response?.status === 409 ? "unavailable" : "failed"));
  };

  useEffect(() => {
    if (!id) return;
    v2Roadmap(id)
      .then((r) => {
        setData(r);
        if (!autoSent.current) {
          autoSent.current = true;
          sendPdf(false);
        }
      })
      .catch((e) => setError(e?.response?.data?.detail || e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
            <PdfCard state={pdf} onResend={() => sendPdf(true)} />
          </>
        )}
      </div>
    </main>
  );
}

function PdfCard({ state, onResend }: { state: PdfState; onResend: () => void }) {
  if (state === "idle" || state === "unavailable") return null;
  const text: Record<Exclude<PdfState, "idle" | "unavailable">, string> = {
    sending: "Yo‘l xaritangiz PDF ko‘rinishida botga yuborilmoqda...",
    sent: "PDF botga yuborildi — Qadam chatini oching.",
    already: "Bu yo‘l xaritasining PDF’i yaqinda botga yuborilgan — Qadam chatini tekshiring.",
    failed: "PDF yuborilmadi. Botni to‘xtatmaganingizni tekshirib, qayta urinib ko‘ring.",
  };
  return (
    <div className="card-clean mt-6" data-testid="v2-pdf-card">
      <div className="flex items-start gap-3">
        {state === "sending" ? <Loader2 className="w-5 h-5 animate-spin shrink-0 mt-0.5" />
          : state === "sent" || state === "already" ? <CheckCircle2 className="w-5 h-5 text-primary shrink-0 mt-0.5" />
          : <FileText className="w-5 h-5 text-subtle shrink-0 mt-0.5" />}
        <p className="t-small">{text[state]}</p>
      </div>
      {state !== "sending" && (
        <button className="btn btn-secondary mt-4" onClick={onResend}>
          {state === "failed" ? "Qayta urinish" : "Qayta yuborish"}
        </button>
      )}
    </div>
  );
}
