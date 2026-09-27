"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, AlertCircle } from "lucide-react";

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

export default function CareerIntelligencePage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("dd_result");
    if (!raw) {
      router.push("/deep-diagnostic");
      return;
    }
    try {
      setData(JSON.parse(raw));
    } catch {
      router.push("/deep-diagnostic");
    }
  }, [router]);

  if (!data) return null;

  const ranked = data.ranked || [];
  const signals = data.signals || {};

  // Top measured signals
  const measuredSignals = Object.entries(signals)
    .filter(([_, v]: any) => v.value !== null)
    .sort(([_, a]: any, [__, b]: any) => -(a.value * a.trust) + (b.value * b.trust))
    .slice(0, 6);

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <p className="t-caption text-primary mb-2">Chuqur tahlil</p>
          <h1 className="t-display mb-3">Sizning natijangiz</h1>
          <p className="t-small text-muted">
            {ranked.length} ta yo&apos;nalish tahlil qilindi. Ishonch:{" "}
            <span className="text-primary font-medium">{data.confidence}</span>
          </p>
        </motion.div>

        {/* Top signallar */}
        {measuredSignals.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
            <div className="space-y-2.5">
              {measuredSignals.map(([key, v]: any, i: number) => (
                <div key={key} className="flex items-center gap-3">
                  <span className="t-small flex-1 truncate">
                    {SIGNAL_UZ[key] ?? key}
                  </span>
                  <div className="w-24 h-1.5 bg-[var(--color-surface-2)] rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(v.value / 10) * 100}%` }}
                      transition={{ delay: 0.1 + i * 0.05, duration: 0.6 }}
                      className="h-full bg-primary"
                    />
                  </div>
                  <span className="t-caption text-subtle tabular-nums w-8 text-right">
                    {Math.round(v.value)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Ranked careers */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mb-6"
        >
          <p className="t-caption text-subtle mb-3">
            Sizga eng mos yo&apos;nalishlar
          </p>
          <div className="space-y-4">
            {ranked.map((c: any, i: number) => (
              <div
                key={c.career_id}
                className="card-clean cursor-pointer hover:border-primary/40 transition"
                onClick={() => router.push(`/roadmap/${c.career_id}`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 min-w-0">
                    <p className="t-caption text-primary mb-1">#{i + 1}</p>
                    <p className="t-heading">{c.career_uz}</p>
                    <p className="t-caption text-subtle">{c.cluster_uz}</p>
                  </div>
                  <div className="text-right shrink-0 pl-3">
                    <p className="t-metric text-primary leading-none">
                      {Math.round(c.fit)}
                      <span className="text-base">%</span>
                    </p>
                    <p className="t-caption text-subtle mt-1">Fit</p>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
                  <span className="t-caption text-subtle">Readiness</span>
                  <span className="t-small text-success font-medium tabular-nums">
                    {Math.round(c.readiness)}%
                  </span>
                </div>

                {c.has_hard_barrier && (
                  <div className="flex items-start gap-2 mt-3 pt-3 border-t border-[var(--color-border)]">
                    <AlertCircle className="w-3.5 h-3.5 text-danger shrink-0 mt-0.5" />
                    <p className="t-caption text-danger">
                      Jiddiy to&apos;siq — yechim pastda
                    </p>
                  </div>
                )}

                {c.barriers?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-[var(--color-border)]">
                    <p className="t-caption text-subtle mb-2">To&apos;siqlar va yechim:</p>
                    {c.barriers.map((b: any, j: number) => (
                      <p key={j} className="t-caption text-muted mb-1">
                        • {b.path}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>

        {ranked.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="card-clean"
          >
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-subtle shrink-0 mt-0.5" />
              <div>
                <p className="t-heading mb-2">Yetarli dalil yo&apos;q</p>
                <p className="t-small text-muted">
                  Hozircha sizning javoblaringiz asosida yetarli mos yo&apos;nalish
                  topilmadi. Iltimos, savollarga samimiyroq javob bering.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </main>
  );
}
