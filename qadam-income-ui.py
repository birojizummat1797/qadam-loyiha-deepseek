# -*- coding: utf-8 -*-
"""Frontend — Daromad salohiyati bloki."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. IncomeSection.tsx — yangi komponent
# ═══════════════════════════════════════════════════════════
COMP = Path("qadam-miniapp/components/IncomeSection.tsx")

COMP.write_text(r'''"use client";

import {
  DollarSign, Briefcase, Globe, Folder, Languages, Target,
  Award, Users, Code, TrendingUp, Info,
} from "lucide-react";

const ICON_MAP: Record<string, any> = {
  briefcase: Briefcase,
  globe: Globe,
  folder: Folder,
  language: Languages,
  target: Target,
  award: Award,
  users: Users,
  code: Code,
};

type Salary = {
  junior: { min: number; max: number };
  middle: { min: number; max: number };
  senior: { min: number; max: number };
};

type Factor = {
  name: string;
  icon: string;
  boost: string;
  desc: string;
};

export function IncomeSection({
  salary,
  factors,
}: {
  salary?: Salary;
  factors?: Factor[];
}) {
  if (!salary) return null;

  return (
    <div className="space-y-4">
      {/* ═══ Maosh oraliqlari ═══ */}
      <div className="rounded-2xl p-5 bg-gradient-to-br from-emerald-500/15 via-teal-500/10 to-cyan-500/15 border border-emerald-500/30 relative overflow-hidden">
        <div className="absolute -top-8 -right-8 w-32 h-32 bg-emerald-500/20 blur-3xl rounded-full" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-emerald-500/30 flex items-center justify-center">
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-emerald-400/80">
                Daromad salohiyati (oyiga)
              </p>
              <h3 className="font-semibold">Maosh oraliglari</h3>
            </div>
          </div>

          {/* 3 daraja */}
          <div className="space-y-3">
            {/* Junior */}
            <div className="p-3 rounded-xl bg-[var(--tg-bg)]/70">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-blue-400">Junior</span>
                <span className="text-[10px] text-[var(--tg-hint)]">0-1 yil</span>
              </div>
              <p className="text-xl font-bold">
                ${salary.junior.min}
                <span className="text-[var(--tg-hint)] font-normal mx-1">—</span>
                ${salary.junior.max}
              </p>
            </div>

            {/* Middle */}
            <div className="p-3 rounded-xl bg-[var(--tg-bg)]/70">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-amber-400">Middle</span>
                <span className="text-[10px] text-[var(--tg-hint)]">1-3 yil</span>
              </div>
              <p className="text-xl font-bold">
                ${salary.middle.min}
                <span className="text-[var(--tg-hint)] font-normal mx-1">—</span>
                ${salary.middle.max}
              </p>
            </div>

            {/* Senior */}
            <div className="p-3 rounded-xl bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-emerald-400">Senior</span>
                <span className="text-[10px] text-[var(--tg-hint)]">3+ yil</span>
              </div>
              <p className="text-xl font-bold">
                ${salary.senior.min}
                <span className="text-[var(--tg-hint)] font-normal mx-1">—</span>
                ${salary.senior.max}
                <span className="text-sm font-normal text-[var(--tg-hint)] ml-1">+</span>
              </p>
            </div>
          </div>

          <p className="text-[10px] text-[var(--tg-hint)] mt-3 leading-relaxed">
            Bu oraliglar O&apos;zbekiston bozori uchun real (2025-2026).
            Tajriba, portfolio, remote va boshqa omillarga qarab o&apos;zgaradi.
          </p>
        </div>
      </div>

      {/* ═══ Daromadga ta'sir qiluvchi omillar ═══ */}
      {factors && factors.length > 0 && (
        <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-indigo-400" />
            <h3 className="font-semibold text-sm">
              Daromadni oshirish imkoniyatlari
            </h3>
          </div>
          <p className="text-[11px] text-[var(--tg-hint)] mb-4 leading-relaxed">
            Maosh faqat daraja (junior/middle/senior) ga bog&apos;liq emas.
            Quyidagi omillar daromadni <b>1.5x dan 3x gacha</b> oshirishi mumkin.
          </p>

          <div className="space-y-2">
            {factors.map((f, i) => {
              const Icon = ICON_MAP[f.icon] ?? TrendingUp;
              return (
                <div
                  key={i}
                  className="p-3 rounded-xl bg-[var(--tg-bg)]/60 flex items-start gap-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center shrink-0">
                    <Icon className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-0.5">
                      <p className="text-xs font-semibold truncate">{f.name}</p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-medium whitespace-nowrap">
                        {f.boost}
                      </span>
                    </div>
                    <p className="text-[11px] text-[var(--tg-hint)] leading-relaxed">
                      {f.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
            <p className="text-[11px] text-[var(--tg-hint)] leading-relaxed">
              <b className="text-indigo-400">Misol:</b> Junior frontend dasturchi
              oddiy ishda $400 oladi. Ammo kuchli portfolio + B2 ingliz tili +
              remote ish bilan <b className="text-emerald-400">$1,200+</b> topishi
              mumkin.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
''', encoding="utf-8")
print("[OK] components/IncomeSection.tsx")

# ═══════════════════════════════════════════════════════════
# 2. RoadmapView — IncomeSection'ni qo'shish
# ═══════════════════════════════════════════════════════════
RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

if "IncomeSection" not in rv:
    rv = rv.replace(
        'import { requestPdf, completeReport } from "@/lib/api";',
        'import { requestPdf, completeReport } from "@/lib/api";',
    )
    # Import qo'shish
    if 'from "./IncomeSection"' not in rv:
        rv = rv.replace(
            'import {\n  MapPin, Target, Calendar, ChevronDown, ChevronRight, Info,',
            'import { IncomeSection } from "./IncomeSection";\nimport {\n  MapPin, Target, Calendar, ChevronDown, ChevronRight, Info,',
        )

    # B NUQTA'dan keyin IncomeSection
    old_block = '''      {/* ═══ FIRST 3 ACTIONS ═══ */}'''
    new_block = '''      {/* ═══ INCOME ═══ */}
      <IncomeSection
        salary={roadmap.b_point?.salary_usd}
        factors={(roadmap as any).income_factors}
      />

      {/* ═══ FIRST 3 ACTIONS ═══ */}'''

    if old_block in rv:
        rv = rv.replace(old_block, new_block)
        RV.write_text(rv, encoding="utf-8")
        print("[OK] RoadmapView.tsx — IncomeSection qoshildi")
    else:
        print("[!!] RoadmapView.tsx — pattern topilmadi")
else:
    print("[SKIP] RoadmapView.tsx — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 3. roadmap.py — income_factors qo'shish
# ═══════════════════════════════════════════════════════════
ROADMAP = Path("qadam/backend/engine/roadmap.py")
rm = ROADMAP.read_text(encoding="utf-8")

if "income_factors" not in rm:
    # `_build_v2` funksiyasiga income_factors qo'shish
    rm = rm.replace(
        '"b_point": {\n            **b_point,\n            "salary_uzs": kb.get("salary_uzs", {}),\n        },',
        '"b_point": {\n            **b_point,\n            "salary_uzs": kb.get("salary_uzs", {}),\n            "salary_usd": kb.get("salary_usd", {}),\n        },\n        "income_factors": KB_V2.get("income_factors", {}).get("factors", []),',
    )

    # Agar salary_uzs yo'q bo'lsa (yangi struktur)
    rm = rm.replace(
        '"b_point": b_point,',
        '"b_point": {\n            **b_point,\n            "salary_usd": kb.get("salary_usd", {}),\n        },\n        "income_factors": KB_V2.get("income_factors", {}).get("factors", []),',
    )

    ROADMAP.write_text(rm, encoding="utf-8")
    print("[OK] roadmap.py — income_factors qoshildi")
else:
    print("[SKIP] roadmap.py — allaqachon bor")

print()
print("=" * 60)
print("Daromad salohiyati bloki — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Daromad salohiyati + omillar (USD)"')
print("  git push")
print("  Render Manual Deploy")