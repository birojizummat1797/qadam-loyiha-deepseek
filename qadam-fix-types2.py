# -*- coding: utf-8 -*-
"""RoadmapView type fix — salary_usd + income_factors."""
from pathlib import Path

RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# Eski b_point pattern (bir qatorlik)
# ═══════════════════════════════════════════════════════════
old = '''  b_point: {
    junior_salary_uzs?: string; remote_salary_usd?: string;
    outcomes?: string[]; next_step?: string;
  };'''

new = '''  b_point: {
    junior_salary_uzs?: string;
    remote_salary_usd?: string;
    salary_uzs?: Record<string, any>;
    salary_usd?: {
      junior: { min: number; max: number };
      middle: { min: number; max: number };
      senior: { min: number; max: number };
    };
    outcomes?: string[];
    next_step?: string;
  };
  income_factors?: {
    name: string;
    icon: string;
    boost: string;
    desc: string;
  }[];'''

if old in rv:
    rv = rv.replace(old, new)
    RV.write_text(rv, encoding="utf-8")
    print("[OK] b_point type yangilandi (single-line pattern)")
else:
    print("[!!] Pattern hali ham topilmadi")
    print("Faylning 25-35 qatorlarini tekshiring")

# ═══════════════════════════════════════════════════════════
# Frontend types.ts ham yangilash
# ═══════════════════════════════════════════════════════════
TYPES = Path("qadam-miniapp/lib/types.ts")
if TYPES.exists():
    t = TYPES.read_text(encoding="utf-8")
    if "SalaryRange" not in t:
        t += '''

export type SalaryRange = { min: number; max: number };

export type SalaryUSD = {
  junior: SalaryRange;
  middle: SalaryRange;
  senior: SalaryRange;
};

export type IncomeFactor = {
  name: string;
  icon: string;
  boost: string;
  desc: string;
};
'''
        TYPES.write_text(t, encoding="utf-8")
        print("[OK] types.ts — Salary tiplari qoshildi")

print()
print("=" * 60)
print("Type fix 2 — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix: b_point type salary_usd"')
print("  git push")