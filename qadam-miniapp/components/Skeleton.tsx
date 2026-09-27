"use client";

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
