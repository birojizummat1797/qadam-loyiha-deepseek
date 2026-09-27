# -*- coding: utf-8 -*-
"""Qadam.io — WOW animatsiyalar v2."""
from pathlib import Path

INTRO = Path("qadam-miniapp/app/page.tsx")

INTRO.write_text(r'''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Target, TrendingUp, ArrowRight, Zap, Star } from "lucide-react";

export default function Home() {
  return (
    <main className="relative max-w-md mx-auto px-5 py-10 overflow-hidden min-h-screen">
      {/* ═══ ANIMATED BACKGROUND ═══ */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        {/* Blob 1 — katta indigo */}
        <motion.div
          animate={{
            x: [0, 50, 0],
            y: [0, -40, 0],
            scale: [1, 1.4, 1],
            opacity: [0.3, 0.6, 0.3],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-20 -left-20 w-72 h-72 bg-indigo-500/40 rounded-full blur-3xl"
        />
        {/* Blob 2 — purple */}
        <motion.div
          animate={{
            x: [0, -60, 0],
            y: [0, 40, 0],
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.5, 0.2],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="absolute top-40 -right-20 w-72 h-72 bg-purple-500/30 rounded-full blur-3xl"
        />
        {/* Blob 3 — amber pastroqda */}
        <motion.div
          animate={{
            x: [0, -30, 0],
            y: [0, -30, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut", delay: 4 }}
          className="absolute bottom-0 left-1/4 w-64 h-64 bg-amber-500/20 rounded-full blur-3xl"
        />
      </div>

      {/* ═══ LOGO — katta harakat ═══ */}
      <motion.div
        initial={{ scale: 0, rotate: -180, opacity: 0 }}
        animate={{ scale: 1, rotate: 0, opacity: 1 }}
        transition={{ duration: 0.9, type: "spring", bounce: 0.5 }}
        className="text-center mb-6"
      >
        <motion.div
          animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.1, 1] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 shadow-2xl shadow-indigo-500/50"
        >
          <Zap className="w-10 h-10 text-white" />
        </motion.div>
      </motion.div>

      {/* ═══ BRAND — sakrab chiqadi ═══ */}
      <motion.h1
        initial={{ opacity: 0, y: 40, scale: 0.5 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ delay: 0.4, duration: 0.7, type: "spring", bounce: 0.4 }}
        className="text-5xl font-bold mb-3 text-center gradient-text"
      >
        Qadam.io
      </motion.h1>

      {/* ═══ SUBTITLE ═══ */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7, duration: 0.5 }}
        className="text-[var(--tg-hint)] text-sm leading-relaxed text-center mb-8"
      >
        Sizga mos kasb va sohani topish uchun
        <br />
        AI diagnostic platformasi
      </motion.p>

      {/* ═══ FEATURE CARDS — chapdan/o'ngdan kiradi ═══ */}
      <div className="space-y-3 mb-6">
        {/* Card 1 — chapdan */}
        <motion.div
          initial={{ opacity: 0, x: -100, rotate: -5 }}
          animate={{ opacity: 1, x: 0, rotate: 0 }}
          transition={{ delay: 0.9, duration: 0.6, type: "spring", bounce: 0.3 }}
          whileHover={{ scale: 1.03, y: -4 }}
          className="card cursor-pointer"
        >
          <div className="flex items-start gap-3">
            <motion.div
              animate={{ rotate: [0, 15, -15, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center shrink-0"
            >
              <Sparkles className="w-6 h-6 text-indigo-400" />
            </motion.div>
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

        {/* Card 2 — o'ngdan */}
        <motion.div
          initial={{ opacity: 0, x: 100, rotate: 5 }}
          animate={{ opacity: 1, x: 0, rotate: 0 }}
          transition={{ delay: 1.1, duration: 0.6, type: "spring", bounce: 0.3 }}
          whileHover={{ scale: 1.03, y: -4 }}
          className="card border border-amber-500/30 cursor-pointer relative overflow-hidden"
        >
          {/* Glow animation */}
          <motion.div
            animate={{ opacity: [0, 0.4, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
            className="absolute inset-0 bg-gradient-to-r from-amber-500/0 via-amber-500/20 to-amber-500/0 pointer-events-none"
          />
          <div className="flex items-start gap-3 relative">
            <motion.div
              animate={{ scale: [1, 1.15, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center shrink-0"
            >
              <Target className="w-6 h-6 text-amber-400" />
            </motion.div>
            <div className="flex-1">
              <h3 className="font-semibold mb-1 flex items-center gap-2">
                Chuqur tahlil
                <motion.span
                  animate={{ scale: [1, 1.2, 1], rotate: [0, 10, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="text-[9px] px-2 py-0.5 rounded-full bg-amber-500/30 text-amber-300 font-medium"
                >
                  ⭐ Premium
                </motion.span>
              </h3>
              <p className="text-[11px] text-[var(--tg-hint)] mb-2">
                18 savol &middot; Fit + Readiness + Roadmap
              </p>
              <p className="text-xs">
                Top-3 yonalish, skill-gap, 6-12 oy shaxsiy roadmap.
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ═══ CTA — katta harakat ═══ */}
      <motion.div
        initial={{ opacity: 0, scale: 0.7, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ delay: 1.4, duration: 0.6, type: "spring", bounce: 0.5 }}
      >
        <Link
          href="/stage1"
          className="btn-primary block text-center flex items-center justify-center gap-2 relative overflow-hidden group"
        >
          <motion.span
            animate={{ x: [0, 5, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="relative z-10"
          >
            Boshlash
          </motion.span>
          <motion.div
            animate={{ x: [0, 8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="relative z-10"
          >
            <ArrowRight className="w-5 h-5" />
          </motion.div>

          {/* Shine effect */}
          <motion.div
            animate={{ x: ["-100%", "200%"] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 w-1/2 bg-gradient-to-r from-transparent via-white/40 to-transparent pointer-events-none"
          />
        </Link>
      </motion.div>

      {/* ═══ TRUST BADGE ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.8, duration: 0.5 }}
        className="flex items-center justify-center gap-2 mt-6 text-[10px] text-[var(--tg-hint)]"
      >
        <motion.div
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
        </motion.div>
        <span>Halol tahlil. Manipulyatsiyasiz.</span>
        <TrendingUp className="w-3 h-3" />
      </motion.div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/page.tsx — WOW animatsiyalar")

# ═══════════════════════════════════════════════════════════
# CSS — globals.css ga glow effekt qo'shish
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

if "pulse-glow" not in css:
    css += '''

/* ═══════════════════════════════════════════════════════════
   WOW EFFECTS — glow, pulse, shine
   ═══════════════════════════════════════════════════════════ */

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.6);
  }
}

.pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.float {
  animation: float 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.gradient-animate {
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}
'''
    GLOBALS.write_text(css, encoding="utf-8")
    print("[OK] globals.css — WOW effects")

print()
print("=" * 60)
print("WOW v2 — TAYYOR!")
print("=" * 60)
print()
print("Nima ozgardi:")
print("  • Logo: spring bounce (sakrab chiqadi)")
print("  • Brand: 0.5 → 1 scale, spring bounce")
print("  • Kartalar: chapdan/o'ngdan 100px siljiydi")
print("  • Iconlar: doimiy harakat (rotate, scale)")
print("  • Premium badge: pulse")
print("  • CTA: shine effect + arrow harakat")
print("  • Blob'lar: kattaroq, ko'proq harakat")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "WOW v2: dramatic animations"')
print("  git push")