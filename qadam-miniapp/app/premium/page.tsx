"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Check, CreditCard, Copy, X, Upload, Loader2,
  CheckCircle2, Image as ImageIcon, Sparkles,
} from "lucide-react";
import { api, getInitData } from "@/lib/api";

type PayState = "loading" | "none" | "pending" | "rejected" | "unlocked";

async function fetchPayState(): Promise<PayState> {
  const r = await api.get("/payments/manual/my-status", {
    params: { init_data: getInitData() },
  });
  return r.data.state as PayState;
}

function errorDetail(e: any): { code?: string; message: string } {
  const d = e?.response?.data?.detail;
  if (d && typeof d === "object") return { code: d.code, message: d.message };
  return { message: typeof d === "string" ? d : "Tarmoq xatosi. Qayta urinib ko'ring." };
}

export default function PremiumPage() {
  const router = useRouter();
  const [card, setCard] = useState<any>(null);
  const [openPay, setOpenPay] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // unlocked | pending | rejected | none — from the backend, never guessed on the client.
  const [status, setStatus] = useState<PayState>("loading");
  const [checking, setChecking] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const discoverySessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("discovery_session_id"))
    : null;

  const refreshStatus = async () => {
    setChecking(true);
    try {
      const next = await fetchPayState();
      setStatus(next);
      return next;
    } catch {
      setStatus((s) => (s === "loading" ? "none" : s));
      return null;
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    refreshStatus();
    api.get("/payments/manual/card-info")
      .then((r) => setCard(r.data.card))
      .catch(() => setError("Karta malumotlarini yuklab bolmadi"));
  }, []);

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
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("init_data", getInitData());
      if (discoverySessionId) {
        formData.append("discovery_session_id", String(discoverySessionId));
      }
      formData.append("screenshot", file);

      const r = await api.post("/payments/manual/upload-v2", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (r.data.ok) {
        setDone(true);
        setStatus("pending");
      }
    } catch (e: any) {
      const { code, message } = errorDetail(e);
      if (code === "already_unlocked" || code === "pending_exists") {
        setOpenPay(false);
        setStatus(code === "already_unlocked" ? "unlocked" : "pending");
      } else {
        alert(message);
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6">
        {/* Header */}
        <div className="mb-8 fade-in">
          <p className="t-caption text-primary mb-2">Chuqur tahlil</p>
          <h1 className="t-display mb-3">
            Shaxsiy kasb<br />yo&apos;l xaritasi
          </h1>
          <p className="t-small text-muted">
            Dalil darajasi, to'siqlar, skill-gap, 6-12 oylik reja va PDF hisobot.
          </p>
        </div>

        {/* Payment state */}
        {status === "unlocked" && (
          <div className="card-clean mb-6 fade-in">
            <p className="t-heading mb-1">Chuqur tahlil siz uchun ochiq</p>
            <p className="t-small text-muted mb-4">To&apos;lovingiz tasdiqlangan.</p>
            <button onClick={() => router.push("/deep-diagnostic")} className="btn btn-primary">
              <Sparkles className="w-4 h-4" />
              <span>Chuqur tahlilni boshlash</span>
            </button>
          </div>
        )}
        {status === "pending" && (
          <div className="card-clean mb-6 fade-in">
            <p className="t-heading mb-1">Skrinshotingiz tekshirilmoqda</p>
            <p className="t-small text-muted mb-4">
              Admin to&apos;lovni qo&apos;lda tekshiradi. Qaror bo&apos;lgach, Telegram orqali xabar keladi.
            </p>
            <button onClick={refreshStatus} disabled={checking} className="btn btn-ghost">
              {checking ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              <span>Holatni yangilash</span>
            </button>
          </div>
        )}
        {status === "rejected" && (
          <div className="card-clean mb-6 fade-in border-[var(--color-danger)]/40">
            <p className="t-heading mb-1">Oldingi to&apos;lov tasdiqlanmadi</p>
            <p className="t-small text-muted">
              Kartaga to&apos;lov topilmadi yoki skrinshot aniq emas. Agar pul o&apos;tkazgan
              bo&apos;lsangiz, to&apos;lov chekining aniq skrinshotini qayta yuboring.
            </p>
          </div>
        )}

        {/* Features */}
        <div className="card-clean mb-6 fade-in fade-in-1">
          <ul className="space-y-2.5">
            {[
              "18 savol chuqur diagnostika",
              "Signallaringizga yaqin yo'nalishlar (yo'l xaritasi tayyorlari)",
              "Dalil darajasi va to'siqlar tahlili",
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
        </div>

        {/* Price */}
        <div className="card-clean mb-6 fade-in fade-in-2">
          <div className="flex items-baseline justify-between mb-1">
            <span className="t-small text-muted">Narx</span>
            <div className="text-right">
              <span className="t-title">39 000</span>
              <span className="t-small text-muted ml-1">so&apos;m</span>
            </div>
          </div>
        </div>

        {/* CTA — only when a payment can actually be started */}
        {(status === "none" || status === "rejected") && (
          <div className="fade-in fade-in-3">
            <button onClick={() => { setDone(false); setOpenPay(true); }} className="btn btn-primary">
              <CreditCard className="w-4 h-4" />
              <span>{status === "rejected" ? "Skrinshotni qayta yuborish" : "Karta orqali to'lash"}</span>
            </button>
            <p className="t-caption text-subtle text-center mt-4">
              Admin to&apos;lovni qo&apos;lda tekshiradi. Natija Telegram orqali keladi.
            </p>
          </div>
        )}
        {status === "loading" && (
          <div className="flex justify-center py-4">
            <Loader2 className="w-5 h-5 animate-spin text-muted" />
          </div>
        )}

        {error && (
          <div className="card-clean border-[var(--color-danger)]/40 mt-4">
            <p className="t-small text-danger">{error}</p>
          </div>
        )}
      </div>

      {/* ═══ PAYMENT MODAL ═══ */}
      {openPay && card && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between sticky top-0 bg-[var(--color-surface)] z-10">
              <div>
                <h3 className="t-heading">
                  {done ? "Yuborildi" : "Karta orqali to'lash"}
                </h3>
                {!done && (
                  <p className="t-caption text-subtle mt-1">
                    Quyidagi kartaga o&apos;tkazing
                  </p>
                )}
              </div>
              <button
                onClick={() => { setOpenPay(false); setDone(false); }}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {done ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-5">
                  <CheckCircle2 className="w-8 h-8 text-success" />
                </div>
                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin to&apos;lovni qo&apos;lda tekshiradi. Qaror bo&apos;lgach, Telegram orqali xabar keladi.
                </p>
                <button
                  onClick={async () => {
                    const next = await refreshStatus();
                    if (next === "unlocked") {
                      router.push("/deep-diagnostic");
                    } else {
                      setNotice(
                        next === "rejected"
                          ? "To'lov tasdiqlanmadi. Botdagi xabarni ko'ring."
                          : "Hali tekshirilmoqda. Admin qaror qilgach, Telegram orqali xabar keladi."
                      );
                    }
                  }}
                  disabled={checking}
                  className="btn btn-primary"
                >
                  Holatni tekshirish
                </button>
                {notice && <p className="t-caption text-muted mt-3">{notice}</p>}
                <button
                  onClick={() => {
                    const tg = (window as any).Telegram?.WebApp;
                    if (tg?.close) tg.close();
                  }}
                  className="btn btn-ghost mt-2"
                >
                  Botga qaytish
                </button>
              </div>
            ) : (
              <>
                <div className="p-5 space-y-4">
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
                        {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copied ? "Olindi" : "Nusxa"}</span>
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
                    <p className="t-caption text-primary mb-1">To&apos;lov summasi</p>
                    <p className="t-metric text-primary leading-none">
                      {card.amount.toLocaleString("uz")}
                      <span className="text-base ml-1">so&apos;m</span>
                    </p>
                  </div>

                  <div className="divider" />

                  <div>
                    <p className="t-caption text-subtle mb-3">To&apos;lov skrinshotini yuklang</p>
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
                          <p className="t-caption text-subtle mt-0.5">JPG, PNG · maks 5 MB</p>
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
                          onClick={() => { setFile(null); setPreview(null); }}
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

                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={!file || uploading}
                    className="btn btn-primary"
                  >
                    {uploading ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
                    ) : (
                      <><ImageIcon className="w-4 h-4" /><span>Skrinshotni yuborish</span></>
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
