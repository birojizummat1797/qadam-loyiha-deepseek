"use client";

/**
 * Consent + age gate (PM decision 2026-10-04, P0).
 * 18+ only for now; 35+ sees an honest warning and may continue.
 * Age is a gate, never a signal: it does not change any result.
 */
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { ackAgeWarning, submitGate } from "@/lib/api";

export type Step = "consent" | "age" | "under_age" | "over_35";

function firstName(): string {
  if (typeof window === "undefined") return "";
  return (window as any).Telegram?.WebApp?.initDataUnsafe?.user?.first_name || "";
}

function closeApp() {
  const tg = (window as any).Telegram?.WebApp;
  if (tg?.close) tg.close();
}

export default function AgeGate({
  onPassed,
  initialStep = "consent",
}: {
  onPassed: () => void;
  initialStep?: Step;
}) {
  const [step, setStep] = useState<Step>(initialStep);
  const [age, setAge] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const name = firstName();

  const send = async () => {
    const n = Number(age);
    if (!Number.isInteger(n) || n < 5 || n > 120) {
      setError("Yoshingizni raqam bilan kiriting.");
      return;
    }
    setSending(true);
    setError(null);
    try {
      const r = await submitGate(true, n);
      if (r.status === "under_age") setStep("under_age");
      else if (r.age_warning) setStep("over_35");
      else onPassed();
    } catch (e: any) {
      const d = e?.response?.data?.detail;
      setError((d && typeof d === "object" && d.message) || "Tarmoq xatosi. Qayta urinib ko'ring.");
    } finally {
      setSending(false);
    }
  };

  const continueOver35 = async () => {
    setSending(true);
    try {
      await ackAgeWarning();
    } catch {
      // The warning is information, not a block: continue even if saving the choice failed.
    } finally {
      setSending(false);
    }
    onPassed();
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-10 pb-6">
        {step === "consent" && (
          <div className="fade-in">
            <p className="t-caption text-primary mb-2">Boshlashdan oldin</p>
            <h1 className="t-heading mb-4">Assalomu alaykum{name ? `, ${name}` : ""}!</h1>
            <div className="card-clean mb-4">
              <p className="t-small mb-2">Natijangizni tayyorlash uchun Qadam quyidagilarni saqlaydi:</p>
              <ul className="t-small text-muted space-y-1 mb-3 list-disc pl-5">
                <li>Telegram&apos;dagi ismingiz va foydalanuvchi nomingiz</li>
                <li>yoshingiz</li>
                <li>savollarga bergan javoblaringiz va ularning tahlili</li>
              </ul>
              <p className="t-small text-muted mb-3">
                Nima uchun: natija va yo&apos;l xaritasini ko&apos;rsatish, yosh chegarasiga rioya qilish va
                xizmatni yaxshilash.
              </p>
              <p className="t-small mb-1">Va&apos;damiz:</p>
              <ul className="t-small text-muted space-y-1 list-disc pl-5">
                <li>ma&apos;lumotlaringiz faqat natijangizni tayyorlash uchun ishlatiladi va boshqa maqsadlarda hech kimga berilmaydi;</li>
                <li>ismingiz va yoshingiz natijangizga ta&apos;sir qilmaydi — natija faqat javoblaringizga asoslanadi.</li>
              </ul>
            </div>
            <p className="t-caption text-subtle mb-4">Qadam hozircha 18 yosh va undan kattalar uchun.</p>
            <button onClick={() => setStep("age")} className="btn btn-primary">Roziman, davom etaman</button>
            <button onClick={closeApp} className="btn btn-ghost mt-2">Yo&apos;q, rahmat</button>
          </div>
        )}

        {step === "age" && (
          <div className="fade-in">
            <h1 className="t-heading mb-4">Yoshingiz nechada?</h1>
            <input
              type="number"
              inputMode="numeric"
              min={5}
              max={120}
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="w-full p-4 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)] t-title mb-3"
              placeholder="Masalan, 21"
              aria-label="Yoshingiz"
            />
            {error && <p className="t-caption text-danger mb-3">{error}</p>}
            <button onClick={send} disabled={sending || !age} className="btn btn-primary">
              {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              <span>Davom etish</span>
            </button>
          </div>
        )}

        {step === "under_age" && (
          <div className="fade-in">
            <h1 className="t-heading mb-3">Rahmat{name ? `, ${name}` : ""}!</h1>
            <p className="t-small text-muted mb-3">
              Qadam hozircha 18 yosh va undan kattalar uchun mo&apos;ljallangan. Bu sizning
              qobiliyatingiz haqida emas — xizmatimiz hali sizning yoshingizga moslashtirilmagan.
            </p>
            <p className="t-small text-muted mb-6">
              Hech qanday ma&apos;lumotingiz saqlanmadi. 18 yoshga to&apos;lganingizda sizni kutib qolamiz. 🌱
            </p>
            <button onClick={closeApp} className="btn btn-ghost">Yopish</button>
          </div>
        )}

        {step === "over_35" && (
          <div className="fade-in">
            <h1 className="t-heading mb-3">Rahmat{name ? `, ${name}` : ""}!</h1>
            <p className="t-small text-muted mb-6">
              Ochig&apos;ini aytamiz: Qadam savollari va o&apos;qish yo&apos;llari hozircha asosan 18–35
              yoshdagilar tajribasiga moslashtirilgan. Shuning uchun natijalar siz uchun kamroq aniq bo&apos;lishi
              mumkin. Yoshingiz natijaga ta&apos;sir qilmaydi. Davom etishni xohlaysizmi?
            </p>
            <button onClick={continueOver35} disabled={sending} className="btn btn-primary">Ha, davom etaman</button>
            <button onClick={closeApp} className="btn btn-ghost mt-2">Keyinroq</button>
          </div>
        )}
      </div>
    </main>
  );
}
