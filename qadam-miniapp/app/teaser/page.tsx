"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles, CreditCard, Send, X, Copy } from "lucide-react";
import { useStore } from "@/lib/store";
import { api, getInitData } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);

  const [openPay, setOpenPay] = useState(false);
  const [card, setCard] = useState<any>(null);
  const [sending, setSending] = useState(false);
  const [copied, setCopied] = useState(false);

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

  const openPayment = async () => {
    setSending(true);
    try {
      const r = await api.post("/payments/manual/request", {
        init_data: getInitData(),
        stage1_result_id: stage1ResultId,
      });
      setCard(r.data.card);
      setOpenPay(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSending(false);
    }
  };

  const copyCard = () => {
    if (card?.number) {
      navigator.clipboard.writeText(card.number.replace(/\s/g, ""));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* HEADER */}
        <div className="pt-8 pb-6 fade-in">
          <h1 className="t-title mb-2">Tezkor natijangiz</h1>
          <p className="t-small text-muted">
            Profilingiz bo'yicha dastlabki tahlil
          </p>
        </div>

        {/* SIGNALS */}
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

        {/* CAREERS */}
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

        {/* PREMIUM */}
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

          <div className="price-row">
            <span className="t-small text-muted">Narx</span>
            <span className="t-heading">39 000 so'm</span>
          </div>

          <div className="pt-4">
            <button
              onClick={openPayment}
              disabled={sending}
              className="btn btn-primary"
            >
              <CreditCard className="w-4 h-4" />
              <span>{sending ? "Yuklanmoqda..." : "Karta orqali to'lash"}</span>
            </button>
          </div>

          <p className="t-caption text-subtle text-center mt-4">
            7 kun ichida pulni qaytarish
          </p>
        </div>

        <p className="t-caption text-subtle text-center pb-6 fade-in fade-in-4">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>

      {/* ═══ PAYMENT MODAL ═══ */}
      {openPay && card && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            {/* Header */}
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
              <div>
                <h3 className="t-heading">Karta orqali to'lash</h3>
                <p className="t-caption text-subtle mt-1">
                  Quyidagi kartaga o'tkazing
                </p>
              </div>
              <button
                onClick={() => setOpenPay(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Card info */}
            <div className="p-5 space-y-4">
              <div>
                <p className="t-caption text-subtle mb-2">Karta raqami</p>
                <button
                  onClick={copyCard}
                  className="w-full flex items-center justify-between p-4 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)] hover:border-[var(--color-border-strong)] transition"
                >
                  <span className="t-heading tabular-nums tracking-wider">
                    {card.number}
                  </span>
                  <span className="flex items-center gap-1.5 t-caption text-primary">
                    {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? "Nusxa olindi" : "Nusxa"}</span>
                  </span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="t-caption text-subtle mb-1">Egasi</p>
                  <p className="t-small">{card.holder}</p>
                </div>
                <div>
                  <p className="t-caption text-subtle mb-1">Bank</p>
                  <p className="t-small">{card.bank}</p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[var(--color-primary-soft)] border border-primary/30">
                <p className="t-caption text-primary mb-1">To'lov summasi</p>
                <p className="t-metric text-primary leading-none">
                  {card.amount.toLocaleString("uz")}
                  <span className="text-base ml-1">so'm</span>
                </p>
              </div>

              <div className="pt-2 space-y-2">
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">1.</span>
                  <span>Yuqoridagi kartaga pul o'tkazing</span>
                </div>
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">2.</span>
                  <span>To'lov skrinshotini oling</span>
                </div>
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">3.</span>
                  <span>Skrinshotni <b className="text-text">@ulugbek_aliboyev</b> ga yuboring</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-4 pt-0 space-y-2">
              <a
                href={`https://t.me/${card.admin_username?.replace("@", "") || "ulugbek_aliboyev"}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary block text-center flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Adminga skrinshot yuborish</span>
              </a>

              <button
                onClick={() => setOpenPay(false)}
                className="btn btn-ghost"
              >
                Keyinroq
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
