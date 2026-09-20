"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles } from "lucide-react";
import { useStore } from "@/lib/store";
// import { createPayment, createStarsInvoice } from "@/lib/api";
import { createPayment, createStarsInvoice, devUnlock } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);
  const [loading, setLoading] = useState(false);

  if (!teaser || !stage1ResultId) {
    return (
      <main className="max-w-md mx-auto px-5 py-10">
        <p className="mb-4">Natija topilmadi.</p>
        <button className="btn-primary" onClick={() => router.push("/stage1")}>
          Qaytadan boshlash
        </button>
      </main>
    );
  }

  const payClick = async () => {
    setLoading(true);
    try {
      const res = await createPayment(stage1ResultId, "click");
      if (res.pay_url) {
        window.open(res.pay_url, "_blank");
        // TODO: polling
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const payStars = async () => {
    setLoading(true);
    try {
      const res = await createStarsInvoice(stage1ResultId);
      const tg = (window as any).Telegram?.WebApp;
      if (!tg?.openInvoice) {
        alert("Telegram Stars bu qurilmada ishlamaydi. Karta orqali tolang.");
        return;
      }
      tg.openInvoice(res.invoice_link, (status: string) => {
        if (status === "paid") router.push("/stage2");
      });
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <h1 className="text-2xl font-bold mb-4">Tezkor natijangiz</h1>

      <div className="card">
        <h3 className="font-semibold mb-3">Kuchli signallaringiz</h3>
        {teaser.top_2_signals?.map((s: any) => (
          <div key={s.key} className="flex justify-between py-1.5">
            <span className="capitalize text-sm">
              {s.key.replace(/_/g, " ")}
            </span>
            <span className="text-[var(--tg-hint)] text-sm">
              {Math.round(s.score * 100)}%
            </span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold mb-3">Mos yonalishlar</h3>
        {teaser.top_2_careers?.map((c: any) => (
          <div
            key={c.career_id}
            className="py-2 border-b border-[var(--tg-hint)]/20 last:border-0"
          >
            <p className="font-medium">{c.career_uz}</p>
            <p className="text-xs text-[var(--tg-hint)]">
              {c.cluster_uz} &middot; Fit: {c.fit}%
            </p>
          </div>
        ))}
        {teaser.locked_count > 0 && (
          <p className="mt-3 text-sm text-amber-400 flex items-center gap-2">
            <Lock className="w-4 h-4" />
            Yana {teaser.locked_count} ta mos yonalish yashirilgan
          </p>
        )}
      </div>

      <div className="card border border-[var(--tg-button)]/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold">Chuqur tahlil</h3>
        </div>
        <ul className="space-y-2 mb-4 text-sm">
          {[
            "Top-5 mos yonalish",
            "Fit + Readiness har biri uchun",
            "Tosiqlar va ularni hal qilish",
            "6-12 oy shaxsiy roadmap",
            "Birinchi 3 qadam",
            "PDF hisobot",
          ].map((t, i) => (
            <li key={i} className="flex gap-2">
              <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>{t}</span>
            </li>
          ))}
        </ul>

        <div className="flex flex-col gap-2">
          <button
            disabled={loading}
            onClick={payStars}
            className="btn-primary"
          >
            Telegram Stars orqali (150 ⭐)
          </button>
          <button
            disabled={loading}
            onClick={payClick}
            className="btn-primary"
            style={{
              background: "var(--tg-secondary-bg)",
              color: "var(--tg-text)",
            }}
          >
            Karta orqali (39 000 som)
          </button>
        </div>

	<button
  disabled={loading}
  onClick={async () => {
    setLoading(true);
    try {
      await devUnlock(stage1ResultId);
      router.push("/stage2");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  }}
  className="btn-primary mt-2"
  style={{ background: "#10b981", color: "white" }}
>
  🛠 DEV: Test uchun ochish (to‘lovsiz)
</button>

        <p className="text-xs text-[var(--tg-hint)] mt-3 text-center">
          7 kun ichida pulni qaytarish kafolati
        </p>
      </div>
    </main>
  );
}
