"use client";

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
