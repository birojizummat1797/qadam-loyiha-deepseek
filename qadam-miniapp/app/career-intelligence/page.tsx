"use client";

import { Sparkles } from "lucide-react";

export default function CareerIntelligencePage() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-10 text-center">
        <div className="w-16 h-16 rounded-full bg-[var(--color-primary-soft)] flex items-center justify-center mx-auto mb-6">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
        <h1 className="t-title mb-3">Chuqur tahlil</h1>
        <p className="t-small text-muted mb-6">
          Bu qism keyingi bosqichda qo&apos;shiladi. Hozircha sizning to&apos;lovingiz
          tasdiqlangan — natija tez orada tayyor bo&apos;ladi.
        </p>
      </div>
    </main>
  );
}
