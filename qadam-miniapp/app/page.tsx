"use client";

import Link from "next/link";
import { Sparkles, Target, TrendingUp } from "lucide-react";

export default function Home() {
  return (
    <main className="max-w-md mx-auto px-5 py-10">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-3 gradient-text">QADAM</h1>
        <p className="text-[var(--tg-hint)]">
          Sizga mos kasb va sohani topish uchun tahlil
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-3 mb-3">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold">Tezkor tahlil</h3>
        </div>
        <p className="text-sm text-[var(--tg-hint)] mb-2">
          8 savol &middot; 3 daqiqa &middot; Bepul
        </p>
        <p className="text-sm">
          Kuchli 2 ta signalingizni va 2 ta mos yonalishni korasiz.
        </p>
      </div>

      <div className="card">
        <div className="flex items-center gap-3 mb-3">
          <Target className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold">Chuqur tahlil (Premium)</h3>
        </div>
        <p className="text-sm text-[var(--tg-hint)] mb-2">
          18 savol &middot; Fit + Readiness + Roadmap
        </p>
        <p className="text-sm">
          Top-5 yonalish, skill-gap, 6-12 oy shaxsiy roadmap.
        </p>
      </div>

      <Link href="/stage1" className="btn-primary block text-center mt-6">
        Boshlash
      </Link>

      <div className="flex items-center justify-center gap-2 mt-6 text-xs text-[var(--tg-hint)]">
        <TrendingUp className="w-4 h-4" />
        <span>Halol tahlil. Manipulyatsiyasiz.</span>
      </div>
    </main>
  );
}
