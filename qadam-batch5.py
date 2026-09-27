# -*- coding: utf-8 -*-
"""Batch 5 — Frontend: Discovery + Preliminary Insight (yangi API)."""
from pathlib import Path

FE = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. lib/api.ts — yangi funksiyalar
# ═══════════════════════════════════════════════════════════
API = FE / "lib/api.ts"
api = API.read_text(encoding="utf-8")

if "startDiscovery" not in api:
    api += '''

// ═══════════════════════════════════════════════════════════
// DISCOVERY v1 — Free bosqich
// ═══════════════════════════════════════════════════════════

export async function startDiscovery() {
  const r = await api.post("/api/v1/discovery", {
    init_data: getInitData(),
  });
  return r.data;
}

export async function getDiscoverySession(session_id: number) {
  const r = await api.get(`/api/v1/discovery/${session_id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function submitDiscoveryAnswer(
  session_id: number,
  question_id: string,
  answer_id: string,
  answer_value: number
) {
  const r = await api.post(`/api/v1/discovery/${session_id}/answers`, {
    init_data: getInitData(),
    question_id,
    answer_id,
    answer_value,
  });
  return r.data;
}

export async function completeDiscovery(session_id: number) {
  const r = await api.post(`/api/v1/discovery/${session_id}/complete`, {
    init_data: getInitData(),
  });
  return r.data;
}

// ═══════════════════════════════════════════════════════════
// PROFILE v1
// ═══════════════════════════════════════════════════════════

export async function saveProfile(data: {
  age?: number;
  location?: string;
  current_status?: string;
  education?: string;
}) {
  const r = await api.post("/api/v1/profile", {
    init_data: getInitData(),
    ...data,
  });
  return r.data;
}

// ═══════════════════════════════════════════════════════════
// ENTITLEMENTS v1
// ═══════════════════════════════════════════════════════════

export async function getMyEntitlements() {
  const r = await api.get("/api/v1/entitlements/me", {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function checkEntitlement(key: string) {
  const r = await api.get("/api/v1/entitlements/check", {
    params: { init_data: getInitData(), entitlement_key: key },
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] lib/api.ts — v1 funksiyalar")
else:
    print("[SKIP] lib/api.ts — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 2. app/discovery/page.tsx — 13 savol (yangi API)
# ═══════════════════════════════════════════════════════════
(FE / "app/discovery").mkdir(exist_ok=True)

(FE / "app/discovery/page.tsx").write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import {
  startDiscovery, submitDiscoveryAnswer, completeDiscovery,
} from "@/lib/api";

type Question = {
  id: string;
  type: string;
  text: string;
  index: number;
  total: number;
  options: { id: string; label: string }[] | null;
};

type Answer = {
  question_id: string;
  answer_id: string;
  answer_value: number;
};

const LIKERT = [
  { value: 1, label: "Umuman yo'q" },
  { value: 2, label: "Kam" },
  { value: 3, label: "O'rtacha" },
  { value: 4, label: "Ko'p" },
  { value: 5, label: "To'liq ha" },
];

export default function DiscoveryPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<{ id: string; value: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session boshlash
  useEffect(() => {
    startDiscovery()
      .then((r) => {
        setSessionId(r.session_id);
        setQuestion(r.current_question);
        setLoading(false);
      })
      .catch((e) => {
        setError(e?.response?.data?.detail || e.message);
        setLoading(false);
      });
  }, []);

  const handleSelect = (optionId: string, value: number) => {
    setSelected({ id: optionId, value });
  };

  const handleNext = async () => {
    if (!sessionId || !question || !selected) return;
    setSubmitting(true);
    try {
      const r = await submitDiscoveryAnswer(
        sessionId, question.id, selected.id, selected.value
      );
      if (r.next_question) {
        setQuestion(r.next_question);
        setSelected(null);
      } else {
        // Discovery tugadi — complete
        await completeDiscovery(sessionId);
        router.push("/preliminary");
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!question) return <Loader />;

  const progress = ((question.index + 1) / question.total) * 100;

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* TOP */}
        <div className="pt-6 pb-4">
          <div className="flex items-center justify-between mb-4">
            <span className="t-caption text-subtle">Discovery</span>
            <span className="t-caption text-subtle">
              {question.index + 1} / {question.total}
            </span>
          </div>
          <div className="h-px bg-[var(--color-border)] relative overflow-hidden">
            <motion.div
              className="absolute top-0 left-0 h-full bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            />
          </div>
        </div>

        {/* QUESTION */}
        <AnimatePresence mode="wait">
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            className="flex-1 flex flex-col"
          >
            <h2 className="t-title mb-8 mt-4">{question.text}</h2>

            <div className="flex flex-col gap-2.5 mb-6">
              {question.type === "likert"
                ? LIKERT.map((o, idx) => {
                    const isSel = selected?.value === o.value && selected?.id === `likert_${o.value}`;
                    return (
                      <motion.button
                        key={o.value}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.03, duration: 0.2 }}
                        onClick={() => handleSelect(`likert_${o.value}`, o.value)}
                        className={`option-btn ${isSel ? "selected" : ""}`}
                      >
                        <span>{o.label}</span>
                        <span className="option-indicator">
                          {isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                        </span>
                      </motion.button>
                    );
                  })
                : question.options?.map((o, idx) => {
                    const isSel = selected?.id === o.id;
                    // Choice option → value optdan keladi (bu yerda 3 default)
                    const val = 3;
                    return (
                      <motion.button
                        key={o.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.03, duration: 0.2 }}
                        onClick={() => handleSelect(o.id, val)}
                        className={`option-btn ${isSel ? "selected" : ""}`}
                      >
                        <span>{o.label}</span>
                        <span className="option-indicator">
                          {isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                        </span>
                      </motion.button>
                    );
                  })}
            </div>
          </motion.div>
        </AnimatePresence>

        {/* NEXT */}
        <div className="pb-6">
          <button
            onClick={handleNext}
            disabled={!selected || submitting}
            className="btn btn-primary"
          >
            {submitting ? (
              <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
            ) : question.index === question.total - 1 ? (
              "Yakunlash"
            ) : (
              "Keyingisi"
            )}
          </button>
        </div>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-6">
        <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />
      </div>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-8">
        <div className="card-clean border-[var(--color-danger)]/40">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/discovery/page.tsx")

# ═══════════════════════════════════════════════════════════
# 3. app/preliminary/page.tsx — Free natija
# ═══════════════════════════════════════════════════════════
(FE / "app/preliminary").mkdir(exist_ok=True)

(FE / "app/preliminary/page.tsx").write_text(r'''"use client";

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
''', encoding="utf-8")
print("[OK] app/preliminary/page.tsx")

# ═══════════════════════════════════════════════════════════
# 4. Discovery complete → sessionStorage'ga saqlash
# ═══════════════════════════════════════════════════════════
DISC = FE / "app/discovery/page.tsx"
d = DISC.read_text(encoding="utf-8")

d = d.replace(
    '''      } else {
        // Discovery tugadi — complete
        await completeDiscovery(sessionId);
        router.push("/preliminary");
      }''',
    '''      } else {
        // Discovery tugadi — complete
        const result = await completeDiscovery(sessionId);
        try {
          sessionStorage.setItem("discovery_result", JSON.stringify(result));
          sessionStorage.setItem("discovery_session_id", String(sessionId));
        } catch {}
        router.push("/preliminary");
      }''',
)
DISC.write_text(d, encoding="utf-8")
print("[OK] discovery — sessionStorage saqlash")

# ═══════════════════════════════════════════════════════════
# 5. Welcome — "Boshlash" → /discovery
# ═══════════════════════════════════════════════════════════
PAGE = FE / "app/page.tsx"
p = PAGE.read_text(encoding="utf-8")

p = p.replace('href="/stage1"', 'href="/discovery"')
PAGE.write_text(p, encoding="utf-8")
print("[OK] app/page.tsx — Boshlash → /discovery")

print()
print("=" * 60)
print("Batch 5 (Frontend: Discovery + Preliminary) — TAYYOR!")
print("=" * 60)
print()
print("Yangi sahifalar:")
print("  • /discovery — 13 savol (yangi API /api/v1/discovery)")
print("  • /preliminary — Free natija (signals + pathways)")
print("  • /  — Boshlash → /discovery")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Batch 5: Discovery + Preliminary (new API)"')
print("  git push")
print("  Vercel avtomatik deploy (2 daqiqa)")
print("  Render kerak emas (backend o'zgarmadi)")