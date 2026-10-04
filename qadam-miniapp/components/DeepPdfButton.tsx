"use client";

import { useState } from "react";
import { FileText, CheckCircle2, Loader2 } from "lucide-react";
import { requestDeepPdf } from "@/lib/api";

/** Sends the v1 Action Document (PDF) to the user's Telegram chat. */
export function DeepPdfButton({ sessionId }: { sessionId: number }) {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");

  const send = async () => {
    setState("sending");
    try {
      const res = await requestDeepPdf(sessionId);
      setState(res.sent_to_telegram ? "sent" : "error");
    } catch {
      setState("error");
    }
  };

  if (state === "sent") {
    return (
      <div className="card-clean flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4 text-success" />
        <p className="t-small">PDF Telegram chatingizga yuborildi.</p>
      </div>
    );
  }

  return (
    <div className="card-clean">
      <button onClick={send} disabled={state === "sending"} className="btn btn-primary w-full flex items-center justify-center gap-2">
        {state === "sending" ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
        PDF hisobotni botga yuborish
      </button>
      {state === "error" && (
        <p className="t-caption text-danger mt-2">PDF yuborilmadi. Birozdan keyin qayta urinib ko&apos;ring.</p>
      )}
    </div>
  );
}
