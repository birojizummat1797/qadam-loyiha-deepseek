"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col px-6 safe-top safe-bottom">
      {/* ═══ LOGO MARK ═══ */}
      <div className="pt-8 pb-12 fade-in">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <span className="text-white font-bold text-lg tracking-tight">Q</span>
        </div>
      </div>

      {/* ═══ MAIN CONTENT ═══ */}
      <div className="flex-1 flex flex-col">
        {/* Headline */}
        <h1 className="t-display mb-5 fade-in fade-in-1">
          Professional yo'lingizni
          <br />
          taxmin bilan emas,
          <br />
          <span className="text-primary">dalillar bilan</span> aniqlang.
        </h1>

        {/* Subtext */}
        <p className="t-body text-muted mb-10 max-w-[340px] fade-in fade-in-2">
          Qadam.io profilingizni tahlil qiladi, sizga mos kasblarni aniqlaydi
          va amaliy yo'l xaritasi tuzadi.
        </p>

        {/* Feature points — no cards, just list */}
        <ul className="space-y-4 mb-10 fade-in fade-in-3">
          {[
            "8 savol — 3 daqiqa",
            "Fit va Readiness tahlili",
            "Shaxsiy 6 oylik yo'l xaritasi",
          ].map((text, i) => (
            <li
              key={i}
              className="flex items-center gap-3 text-[14px] text-muted"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
              <span>{text}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* ═══ ACTIONS ═══ */}
      <div className="space-y-3 pb-4 fade-in fade-in-4">
        <Link href="/stage1" className="block">
          <button className="btn btn-primary">
            Boshlash
            <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
          </button>
        </Link>

        <button className="btn btn-ghost">
          Qadam.io qanday ishlaydi?
        </button>
      </div>

      {/* ═══ TRUST LINE ═══ */}
      <p className="text-center t-caption text-subtle pb-4 fade-in fade-in-5">
        Halol tahlil · Manipulyatsiyasiz
      </p>
    </main>
  );
}
