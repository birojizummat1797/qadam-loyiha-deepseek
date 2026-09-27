"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles } from "lucide-react";
import { useStore } from "@/lib/store";
import { createPayment, createStarsInvoice, devUnlock } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);
  const [loading, setLoading] = useState(false);

  if (!teaser || !stage1ResultId) {
    return (
      <main className="min-h-screen flex justify-center">
        <div className="w-full max-w-md px-6 pt-10">
          <p className="t-body text-muted mb-6">Natija topilmadi.</p>
          <button
            className="btn btn-primary"
            onClick={() => router.push("/stage1")}
          >
            Qaytadan boshlash
          </button>
        </div>
      </main>
    );
  }

  const payStars = async () => {
    setLoading(true);
    try {
      const res = await createStarsInvoice(stage1ResultId);
      const tg = (window as any).Telegram?.WebApp;
      if (!tg?.openInvoice) {
        alert("Telegram Stars bu qurilmada ishlamaydi.");
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

  const payClick = async () => {
    setLoading(true);
    try {
      const res = await createPayment(stage1ResultId, "click");
      if (res.pay_url) window.open(res.pay_url, "_blank");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const handleDev = async () => {
    setLoading(true);
    try {
      await devUnlock(stage1ResultId);
      router.push("/stage2");
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* ═══ HEADER ═══ */}
        <div className="pt-8 pb-6 fade-in">
          <h1 className="t-title mb-2">Tezkor natijangiz</h1>
          <p className="t-small text-muted">
            Profilingiz bo'yicha dastlabki tahlil
          </p>
        </div>

        {/* ═══ SIGNALS ═══ */}
        <div className="mb-6 fade-in fade-in-1">
          <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
          <div className="space-y-2">
            {teaser.top_2_signals?.map((s: any) => (
              <div
                key={s.key}
                className="flex items-center justify-between py-2"
              >
                <span className="t-body capitalize">
                  {s.key.replace(/_/g, " ")}
                </span>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(s.score * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* ═══ CAREERS ═══ */}
        <div className="mb-6 fade-in fade-in-2">
          <p className="t-caption text-subtle mb-3">Mos yo'nalishlar</p>
          <div className="space-y-3">
            {teaser.top_2_careers?.map((c: any) => (
              <div
                key={c.career_id}
                className="card-clean flex items-center justify-between"
              >
                <div>
                  <p className="t-heading">{c.career_uz}</p>
                  <p className="t-small text-muted">{c.cluster_uz}</p>
                </div>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(c.fit)}%
                </span>
              </div>
            ))}
          </div>

          {teaser.locked_count > 0 && (
            <div className="mt-3 flex items-center gap-2 t-small text-muted">
              <Lock className="w-3.5 h-3.5" />
              <span>Yana {teaser.locked_count} ta yo'nalish yashirilgan</span>
            </div>
          )}
        </div>

        {/* ═══ PREMIUM ═══ */}
        <div className="card-clean mb-6 fade-in fade-in-3">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-primary" />
            <h3 className="t-heading">Chuqur tahlil</h3>
          </div>

          <ul className="space-y-2.5 mb-5">
            {[
              "Top-5 mos yo'nalish",
              "Fit + Readiness har biri uchun",
              "To'siqlar va yechimlar",
              "6-12 oy shaxsiy yo'l xaritasi",
              "Birinchi 3 qadam",
              "PDF hisobot",
            ].map((t, i) => (
              <li key={i} className="flex items-start gap-2.5 t-small">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>{t}</span>
              </li>
            ))}
          </ul>

          <div className="divider" />

          {/* Price */}
          <div className="price-row">
            <span className="t-small text-muted">Narx</span>
            <span className="t-heading">39 000 so'm</span>
          </div>

          {/* Actions */}
          <div className="space-y-2.5 pt-4">
            <button
              onClick={payStars}
              disabled={loading}
              className="btn btn-primary"
            >
              Telegram Stars orqali · 150 ⭐
            </button>

            <button
              onClick={payClick}
              disabled={loading}
              className="btn btn-secondary"
            >
              Karta orqali to'lash
            </button>
          </div>

          <p className="t-caption text-subtle text-center mt-4">
            7 kun ichida pulni qaytarish
          </p>
        </div>

        {/* ═══ DEV MODE ═══ */}
        <div className="pb-6 fade-in fade-in-4">
          <button onClick={handleDev} disabled={loading} className="btn btn-ghost">
            🛠 Test uchun ochish (to'lovsiz)
          </button>
        </div>
      </div>
    </main>
  );
}
