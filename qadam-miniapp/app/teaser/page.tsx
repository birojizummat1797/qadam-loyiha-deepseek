"use client";

import { EvidenceBadge } from "@/components/EvidenceLevel";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Lock, Check, Sparkles, CreditCard, X, Copy,
  Upload, Loader2, CheckCircle2, Image as ImageIcon,
} from "lucide-react";
import { useStore } from "@/lib/store";
import { getCardInfo, uploadPaymentScreenshot } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);

  const [openPay, setOpenPay] = useState(false);
  const [card, setCard] = useState<any>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [done, setDone] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const [paymentId, setPaymentId] = useState<number | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    getCardInfo()
      .then((r) => setCard(r.card))
      .catch(() => {});
  }, []);

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

  const copyCard = () => {
    if (card?.number) {
      navigator.clipboard.writeText(card.number.replace(/\s/g, ""));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;

    if (f.size > 5 * 1024 * 1024) {
      alert("Rasm hajmi 5 MB dan oshmasin");
      return;
    }

    setFile(f);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(f);
  };

  const handleSubmit = async () => {
    if (!file || !stage1ResultId) return;
    setUploading(true);
    try {
      const res = await uploadPaymentScreenshot(stage1ResultId, file);
      setPaymentId(res.payment_id);
      setDone(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
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
              <div key={s.key} className="flex items-center justify-between py-2">
                <span className="t-body capitalize">
                  {s.key.replace(/_/g, " ")}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* CAREERS */}
        <div className="mb-6 fade-in fade-in-2">
          <p className="t-caption text-subtle mb-3">Signallaringizga yaqinroq</p>
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
                <EvidenceBadge level={c.evidence_level} coverage={c.coverage} />
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
              "Signallaringizga yaqin 5 ta yo'nalish",
              "Har biri uchun dalil darajasi va to'siqlar",
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
              onClick={() => setOpenPay(true)}
              className="btn btn-primary"
            >
              <CreditCard className="w-4 h-4" />
              <span>Karta orqali to'lash</span>
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
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between sticky top-0 bg-[var(--color-surface)] z-10">
              <div>
                <h3 className="t-heading">
                  {done ? "Yuborildi" : "Karta orqali to'lash"}
                </h3>
                {!done && (
                  <p className="t-caption text-subtle mt-1">
                    Quyidagi kartaga o'tkazing
                  </p>
                )}
              </div>
              <button
                onClick={() => {
                  setOpenPay(false);
                  setFile(null);
                  setPreview(null);
                  setDone(false);
                }}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* DONE state */}
            {done ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-5">
                  <CheckCircle2 className="w-8 h-8 text-success" />
                </div>
                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin tekshiradi va <b className="text-text">5-10 daqiqa</b> ichida
                  sizga Telegram bot orqali xabar yuboriladi.
                  Xabardagi tugma orqali chuqur tahlilga o'tasiz.
                </p>

                <a
                  href={`https://t.me/${(window as any).Telegram?.WebApp?.initDataUnsafe?.user?.username ? "kelajakkailkqadam_bot" : "kelajakkailkqadam_bot"}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary block text-center"
                  onClick={() => {
                    setTimeout(() => {
                      (window as any).Telegram?.WebApp?.close?.();
                    }, 300);
                  }}
                >
                  Botga qaytish
                </a>
                <button
                  onClick={() => {
                    setOpenPay(false);
                    setFile(null);
                    setPreview(null);
                    setDone(false);
                  }}
                  className="btn btn-ghost mt-2"
                >
                  Yopish
                </button>
              </div>
            ) : (
              <>
                <div className="p-5 space-y-4">
                  {/* Card number */}
                  <div>
                    <p className="t-caption text-subtle mb-2">Karta raqami</p>
                    <button
                      onClick={copyCard}
                      className="w-full flex items-center justify-between p-4 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)]"
                    >
                      <span className="t-heading tabular-nums tracking-wider">
                        {card.number}
                      </span>
                      <span className="flex items-center gap-1.5 t-caption text-primary">
                        {copied ? (
                          <Check className="w-3.5 h-3.5" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                        <span>{copied ? "Olindi" : "Nusxa"}</span>
                      </span>
                    </button>
                  </div>

                  {/* Card meta */}
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

                  {/* Amount */}
                  <div className="p-4 rounded-xl bg-[var(--color-primary-soft)] border border-primary/30">
                    <p className="t-caption text-primary mb-1">To'lov summasi</p>
                    <p className="t-metric text-primary leading-none">
                      {card.amount.toLocaleString("uz")}
                      <span className="text-base ml-1">so'm</span>
                    </p>
                  </div>

                  <div className="divider" />

                  {/* Screenshot upload */}
                  <div>
                    <p className="t-caption text-subtle mb-3">
                      To'lov skrinshotini yuklang
                    </p>

                    {!preview ? (
                      <button
                        onClick={() => fileRef.current?.click()}
                        className="w-full flex flex-col items-center justify-center gap-3 p-6 rounded-xl border-2 border-dashed border-[var(--color-border)] hover:border-primary transition bg-[var(--color-surface-2)]"
                      >
                        <div className="w-10 h-10 rounded-full bg-[var(--color-primary-soft)] flex items-center justify-center">
                          <Upload className="w-5 h-5 text-primary" />
                        </div>
                        <div className="text-center">
                          <p className="t-small font-medium">Rasm tanlash</p>
                          <p className="t-caption text-subtle mt-0.5">
                            JPG, PNG · maks 5 MB
                          </p>
                        </div>
                      </button>
                    ) : (
                      <div className="relative">
                        <img
                          src={preview}
                          alt="Screenshot"
                          className="w-full rounded-xl border border-[var(--color-border)] max-h-64 object-contain bg-[var(--color-surface-2)]"
                        />
                        <button
                          onClick={() => {
                            setFile(null);
                            setPreview(null);
                          }}
                          className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/70 flex items-center justify-center"
                        >
                          <X className="w-4 h-4 text-white" />
                        </button>
                      </div>
                    )}

                    <input
                      ref={fileRef}
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleFile}
                      className="hidden"
                    />
                  </div>
                </div>

                {/* Submit */}
                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={!file || uploading}
                    className="btn btn-primary"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Yuborilmoqda...</span>
                      </>
                    ) : (
                      <>
                        <ImageIcon className="w-4 h-4" />
                        <span>Skrinshotni yuborish</span>
                      </>
                    )}
                  </button>
                  <p className="t-caption text-subtle text-center mt-3">
                    Admin tasdiqlagach avtomatik xabar keladi
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
