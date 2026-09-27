# -*- coding: utf-8 -*-
"""Qadam.io — UI/UX polish v1."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. INTRO SAHIFA — hero animatsiyalar
# ═══════════════════════════════════════════════════════════
INTRO = Path("qadam-miniapp/app/page.tsx")

INTRO.write_text(r'''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Target, TrendingUp, ArrowRight, Zap } from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function Home() {
  return (
    <main className="relative max-w-md mx-auto px-5 py-10 overflow-hidden min-h-screen">
      {/* Animated background blobs */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <motion.div
          animate={{
            x: [0, 30, 0],
            y: [0, -20, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-20 -left-20 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            x: [0, -30, 0],
            y: [0, 20, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-40 -right-20 w-64 h-64 bg-purple-500/15 rounded-full blur-3xl"
        />
      </div>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="text-center mb-8"
      >
        {/* Logo */}
        <motion.div variants={item} className="mb-6">
          <motion.div
            animate={{ rotate: [0, 5, -5, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30"
          >
            <Zap className="w-8 h-8 text-white" />
          </motion.div>
        </motion.div>

        <motion.h1
          variants={item}
          className="text-4xl font-bold mb-3 gradient-text"
        >
          Qadam.io
        </motion.h1>

        <motion.p
          variants={item}
          className="text-[var(--tg-hint)] text-sm leading-relaxed"
        >
          Sizga mos kasb va sohani topish uchun
          <br />
          AI diagnostic platformasi
        </motion.p>
      </motion.div>

      {/* Feature cards */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-3 mb-6"
      >
        <motion.div variants={item} className="card">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center shrink-0">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1">Tezkor tahlil</h3>
              <p className="text-[11px] text-[var(--tg-hint)] mb-2">
                8 savol &middot; 3 daqiqa &middot; Bepul
              </p>
              <p className="text-xs">
                Kuchli 2 ta signalingizni va 2 ta mos yonalishni korasiz.
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div variants={item} className="card border border-amber-500/20">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center shrink-0">
              <Target className="w-5 h-5 text-amber-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1">Chuqur tahlil</h3>
              <p className="text-[11px] text-[var(--tg-hint)] mb-2">
                18 savol &middot; Fit + Readiness + Roadmap
              </p>
              <p className="text-xs">
                Top-3 yonalish, skill-gap, 6-12 oy shaxsiy roadmap.
              </p>
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* CTA */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <Link
          href="/stage1"
          className="btn-primary block text-center flex items-center justify-center gap-2 relative overflow-hidden group"
        >
          <span className="relative z-10">Boshlash</span>
          <ArrowRight className="w-4 h-4 relative z-10 group-hover:translate-x-1 transition-transform" />
          <motion.div
            initial={{ x: "-100%" }}
            whileHover={{ x: "100%" }}
            transition={{ duration: 0.6 }}
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          />
        </Link>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="flex items-center justify-center gap-2 mt-6 text-[10px] text-[var(--tg-hint)]"
      >
        <TrendingUp className="w-3 h-3" />
        <span>Halol tahlil. Manipulyatsiyasiz.</span>
      </motion.div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/page.tsx — Intro polish")

# ═══════════════════════════════════════════════════════════
# 2. LOADING SKELETON komponenti
# ═══════════════════════════════════════════════════════════
SKELETON = Path("qadam-miniapp/components/Skeleton.tsx")

SKELETON.write_text(r'''"use client";

import { motion } from "framer-motion";

export function SkeletonCard() {
  return (
    <div className="card">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-[var(--tg-hint)]/10 animate-pulse" />
        <div className="flex-1 space-y-2">
          <div className="h-3 bg-[var(--tg-hint)]/10 rounded-full w-2/3 animate-pulse" />
          <div className="h-2 bg-[var(--tg-hint)]/10 rounded-full w-1/3 animate-pulse" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-2 bg-[var(--tg-hint)]/10 rounded-full w-full animate-pulse" />
        <div className="h-2 bg-[var(--tg-hint)]/10 rounded-full w-5/6 animate-pulse" />
      </div>
    </div>
  );
}

export function SkeletonQuestion() {
  return (
    <div className="space-y-4">
      <div className="h-1 bg-[var(--tg-hint)]/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ x: "-100%" }}
          animate={{ x: "100%" }}
          transition={{ repeat: Infinity, duration: 1.2 }}
          className="h-full w-1/2 bg-gradient-to-r from-transparent via-[var(--tg-hint)]/30 to-transparent"
        />
      </div>
      <div className="h-2 bg-[var(--tg-hint)]/10 rounded-full w-20 animate-pulse" />
      <div className="h-6 bg-[var(--tg-hint)]/10 rounded-lg w-3/4 animate-pulse" />
      <div className="space-y-2">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-14 bg-[var(--tg-hint)]/10 rounded-xl animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          />
        ))}
      </div>
    </div>
  );
}

export function SkeletonReport() {
  return (
    <div className="space-y-4">
      <SkeletonCard />
      <SkeletonCard />
      <div className="h-32 bg-[var(--tg-hint)]/10 rounded-2xl animate-pulse" />
      <SkeletonCard />
    </div>
  );
}
''', encoding="utf-8")
print("[OK] components/Skeleton.tsx")

# ═══════════════════════════════════════════════════════════
# 3. STAGE1 — animatsiyalar + skeleton
# ═══════════════════════════════════════════════════════════
STAGE1 = Path("qadam-miniapp/app/stage1/page.tsx")
s1 = STAGE1.read_text(encoding="utf-8")

# Import qo'shish
if "SkeletonQuestion" not in s1:
    s1 = s1.replace(
        'import { useStore } from "@/lib/store";',
        'import { useStore } from "@/lib/store";\nimport { SkeletonQuestion } from "@/components/Skeleton";\nimport { motion, AnimatePresence } from "framer-motion";',
    )

# Loader funksiyasini Skeleton bilan almashtirish
old_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
    </main>
  );
}'''

new_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <SkeletonQuestion />
    </main>
  );
}'''

if old_loader in s1:
    s1 = s1.replace(old_loader, new_loader)
    print("[OK] stage1/page.tsx — Skeleton loader")

STAGE1.write_text(s1, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 4. STAGE2 — skeleton
# ═══════════════════════════════════════════════════════════
STAGE2 = Path("qadam-miniapp/app/stage2/page.tsx")
s2 = STAGE2.read_text(encoding="utf-8")

if "SkeletonQuestion" not in s2:
    s2 = s2.replace(
        'import { useStore } from "@/lib/store";',
        'import { useStore } from "@/lib/store";\nimport { SkeletonQuestion } from "@/components/Skeleton";',
    )

old_s2_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
      <p className="mt-4 text-sm text-[var(--tg-hint)]">Yuklanmoqda...</p>
    </main>
  );
}'''

new_s2_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <SkeletonQuestion />
    </main>
  );
}'''

if old_s2_loader in s2:
    s2 = s2.replace(old_s2_loader, new_s2_loader)
    print("[OK] stage2/page.tsx — Skeleton loader")

STAGE2.write_text(s2, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 5. REPORT — skeleton
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

if "SkeletonReport" not in rep:
    rep = rep.replace(
        'import { FeedbackModal } from "@/components/FeedbackModal";',
        'import { FeedbackModal } from "@/components/FeedbackModal";\nimport { SkeletonReport } from "@/components/Skeleton";',
    )

old_rep_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
      <p className="mt-4 text-sm text-[var(--tg-hint)]">Tahlil yuklanmoqda...</p>
    </main>
  );
}'''

new_rep_loader = '''function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-6">
      <div className="text-center mb-4">
        <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center mx-auto mb-2 animate-pulse" />
        <p className="text-xs text-[var(--tg-hint)]">AI tahlil qilmoqda...</p>
      </div>
      <SkeletonReport />
    </main>
  );
}'''

if old_rep_loader in rep:
    rep = rep.replace(old_rep_loader, new_rep_loader)
    print("[OK] report/page.tsx — Skeleton loader")

REPORT.write_text(rep, encoding="utf-8")

print()
print("=" * 60)
print("UI/UX Polish v1 — TAYYOR!")
print("=" * 60)
print()
print("Nima ozgardi:")
print("  • Intro: animated blobs, stagger animatsiya, CTA hover")
print("  • Stage1/2: skeleton loading (spinner emas)")
print("  • Report: skeleton loading")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "UI/UX polish v1: animations + skeletons"')
print("  git push")
print("  (Vercel avtomatik deploy qiladi)")