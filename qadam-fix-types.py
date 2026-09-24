# -*- coding: utf-8 -*-
"""RoadmapView type fix — salary_usd va income_factors."""
from pathlib import Path

RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# Eski type bloklarini almashtirish
# ═══════════════════════════════════════════════════════════

# b_point type
old_b_point = '''  b_point: {
    junior_salary_uzs?: string;
    remote_salary_usd?: string;
    outcomes?: string[];
    next_step?: string;
  };'''

new_b_point = '''  b_point: {
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

if old_b_point in rv:
    rv = rv.replace(old_b_point, new_b_point)
    print("[OK] b_point type yangilandi")
else:
    print("[SKIP] b_point pattern topilmadi (allaqachon yangilangan)")

RV.write_text(rv, encoding="utf-8")
print()
print("=" * 60)
print("Type fix — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix: Roadmap type salary_usd"')
print("  git push")