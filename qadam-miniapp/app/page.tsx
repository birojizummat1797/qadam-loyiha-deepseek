"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* ═══ LOGO ═══ */}
        <div className="pt-8 pb-16 fade-in">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-white font-bold text-base">Q</span>
          </div>
        </div>

        {/* ═══ MAIN ═══ */}
        <div className="flex-1">
          <h1 className="t-display mb-6 fade-in fade-in-1">
            Professional
            <br />
            yo&apos;lingizni taxmin
            <br />
            emas,{" "}
            <span className="text-primary">dalillar</span>
            <br />
            <span className="text-primary">bilan</span> aniqlang.
          </h1>

          <p className="t-body text-muted mb-10 fade-in fade-in-2">
            Qadam.io profilingizni tahlil qiladi, signallaringizga yaqin kasblarni
            ko&apos;rsatadi va amaliy yo&apos;l xaritasi tuzadi.
          </p>

          <ul className="space-y-3 mb-12 fade-in fade-in-3">
            {[
              "8 savol — 3 daqiqa",
              "Dalil darajasi va to'siqlar tahlili",
              "Shaxsiy 6 oylik yo'l xaritasi",
            ].map((text, i) => (
              <li
                key={i}
                className="flex items-center gap-3 t-body text-muted"
              >
                <span className="w-1 h-1 rounded-full bg-primary shrink-0" />
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* ═══ ACTIONS ═══ */}
        <div className="space-y-2 pb-6 fade-in fade-in-4">
          <Link href="/discovery" className="block">
            <button className="btn btn-primary">
              <span>Boshlash</span>
              <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
            </button>
          </Link>

          <button className="btn btn-ghost">
            Qadam.io qanday ishlaydi?
          </button>
        </div>

        <p className="text-center t-caption text-subtle pb-4 fade-in fade-in-5">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>
    </main>
  );
}
