"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Lock, Check, Sparkles, TrendingUp, Info } from "lucide-react";

const SIGNAL_UZ: Record<string, string> = {
  logical_thinking: "Mantiqiy fikrlash",
  problem_solving: "Muammo hal qilish",
  technical_interest: "Texnikaga qiziqish",
  creative_design: "Ijodiy dizayn",
  visual_logic: "Vizual mantiq",
  user_empathy: "Empatiya",
  system_design: "Tizimli fikrlash",
  analytical: "Tahliliy fikrlash",
  persistence: "Qat'iyat",
  math_logic: "Matematik mantiq",
  attention_to_detail: "Detallarga e'tibor",
  business_sense: "Biznes hissi",
  innovation: "Innovatsiya",
};

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
          <h1 className="t-display mb-3">
            Profilingizga mos<br />yo&apos;nalishlar
          </h1>
          <p className="t-small text-muted">
            Javoblaringiz asosida sizga mos kelishi mumkin bo&apos;lgan yo&apos;nalishlar
            aniqlandi.
          </p>
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
                    {SIGNAL_UZ[s.key] ?? s.key}
                  </span>
                  <div className="w-24 h-1.5 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(s.value / 10) * 100}%` }}
                      transition={{ delay: 0.1 + i * 0.05, duration: 0.6 }}
                      className="h-full bg-primary"
                    />
                  </div>
                  <span className="t-caption text-subtle tabular-nums w-8 text-right">
                    {Math.round(s.value)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* PATHWAYS */}
        {pathways.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="mb-6"
          >
            <p className="t-caption text-subtle mb-3">
              Sizga mos yo&apos;nalishlar
            </p>
            <div className="space-y-3">
              {pathways.slice(0, 3).map((p: any, i: number) => (
                <div key={p.career_id} className="card-clean flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="t-heading truncate">{p.career_uz}</p>
                    <p className="t-caption text-subtle">{p.cluster_uz}</p>
                  </div>
                  <div className="text-right shrink-0 pl-3">
                    <p className="t-heading text-primary tabular-nums">
                      {Math.round(p.fit)}%
                    </p>
                    <p className="t-caption text-subtle">Fit</p>
                  </div>
                </div>
              ))}
            </div>
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
                  {SIGNAL_UZ[k] ?? k}
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
              "Top-5 mos yo'nalish",
              "Fit + Readiness har biri uchun",
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
            <span className="t-small text-muted">Narx</span>
            <span className="t-heading">39 000 so&apos;m</span>
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
