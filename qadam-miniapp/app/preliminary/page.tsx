"use client";

import { signalLabel } from "@/lib/signals";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Lock, Check, Sparkles, TrendingUp, Info } from "lucide-react";
import { EvidenceBadge } from "@/components/EvidenceLevel";
import { NoClearDirection } from "@/components/NoClearDirection";


export default function PreliminaryPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("discovery_result");
    if (!raw) {
      router.push("/discovery");
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setData(parsed);
    } catch (e) {
      setError("Natija topilmadi");
    }
  }, [router]);

  if (error) {
    return (
      <main className="min-h-screen flex justify-center">
        <div className="w-full max-w-md px-6 pt-8">
          <div className="card-clean"><p className="t-small text-danger">{error}</p></div>
        </div>
      </main>
    );
  }
  if (!data) return null;

  const insight = data.insight || {};
  const signals = insight.signals_top || [];
  const pathways = insight.pathways || [];
  const devAreas = insight.development_areas || [];
  const noClearDirection = insight.no_clear_direction === true;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6">
        {/* HEADER */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <p className="t-caption text-primary mb-2">Dastlabki natija</p>
          {noClearDirection ? (
            <h1 className="t-display mb-3">Sizning natijangiz</h1>
          ) : (
            <>
              <h1 className="t-display mb-3">
                Signallaringizga yaqin<br />yo&apos;nalishlar
              </h1>
              <p className="t-small text-muted">
                Javoblaringiz asosida signallaringizga yaqinroq yo&apos;nalishlar.
                Bu tavsiya, hukm emas — qarorni siz qilasiz.
              </p>
            </>
          )}
        </motion.div>

        {/* SIGNALS */}
        {signals.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="mb-6"
          >
            <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
            <div className="space-y-2.5">
              {signals.slice(0, 5).map((s: any, i: number) => (
                <div key={s.key} className="flex items-center gap-3">
                  <span className="t-small flex-1 truncate">
                    {signalLabel(s.key)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {noClearDirection && <NoClearDirection />}

        {/* PATHWAYS */}
        {pathways.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-6"
          >
            <p className="t-caption text-subtle mb-3">
              Signallaringizga yaqinroq
            </p>
            <div className="space-y-3">
              {pathways.slice(0, 3).map((p: any, i: number) => (
                <div key={p.career_id} className="card-clean flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="t-heading truncate">{p.career_uz}</p>
                    <p className="t-caption text-subtle">{p.cluster_uz}</p>
                  </div>
                  <div className="text-right shrink-0 pl-3">
                    <EvidenceBadge level={p.evidence_level} coverage={p.coverage} />
                  </div>
                </div>
              ))}
            </div>
            <p className="t-caption text-subtle mt-3">
              Hozircha natijada faqat yo&apos;l xaritasi tayyor bo&apos;lgan yo&apos;nalishlar ko&apos;rib chiqiladi.
              Qadam katalogidagi boshqa yo&apos;nalishlar bu ro&apos;yxatga keyinroq qo&apos;shiladi.
            </p>
          </motion.div>
        )}

        {/* DEV AREAS */}
        {devAreas.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="card-clean mb-6"
          >
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-warning" />
              <p className="t-heading">Rivojlantirish mumkin</p>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {devAreas.map((k: string) => (
                <span key={k} className="badge-soft badge-warning">
                  {signalLabel(k)}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* DISCLAIMER */}
        {insight.disclaimer && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-start gap-2 mb-6"
          >
            <Info className="w-3.5 h-3.5 text-subtle shrink-0 mt-0.5" />
            <p className="t-caption text-subtle">{insight.disclaimer}</p>
          </motion.div>
        )}

        {/* PREMIUM CTA */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="card-clean mb-4"
        >
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-primary" />
            <p className="t-heading">Chuqur tahlil</p>
          </div>
          <ul className="space-y-2 mb-4">
            {[
              "18 savol chuqur diagnostika",
              "Signallaringizga yaqin yo'nalishlar (yo'l xaritasi tayyorlari)",
              "Har biri uchun dalil darajasi va to'siqlar",
              "Skill-gap va to'siqlar",
              "6-12 oy shaxsiy yo'l xaritasi",
              "PDF hisobot",
            ].map((t, i) => (
              <li key={i} className="flex items-start gap-2 t-small">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
          <div className="flex items-center justify-between mb-3 pt-3 border-t border-[var(--color-border)]">
            <span className="t-small text-muted">Hozir</span>
            <span className="t-heading">Beta · bepul</span>
          </div>
          <button
            onClick={() => router.push("/premium")}
            className="btn btn-primary"
          >
            Chuqur tahlilni boshlash
          </button>
        </motion.div>

        <p className="t-caption text-subtle text-center pb-4">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>
    </main>
  );
}
