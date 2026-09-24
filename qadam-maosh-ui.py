# -*- coding: utf-8 -*-
"""Roadmap engine + PDF — maosh ma'lumotlari."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. roadmap.py — B nuqtaga maosh qo'shish
# ═══════════════════════════════════════════════════════════
ROADMAP = Path("qadam/backend/engine/roadmap.py")
rm = ROADMAP.read_text(encoding="utf-8")

# `_build_v2` funksiyasida b_point'ni boyitish
old_b = '"b_point": b_point,'
new_b = '''"b_point": {
            **b_point,
            "salary_uzs": kb.get("salary_uzs", {}),
        },'''

if old_b in rm and "salary_uzs" not in rm:
    rm = rm.replace(old_b, new_b)
    ROADMAP.write_text(rm, encoding="utf-8")
    print("[OK] roadmap.py — maosh b_point'ga qoshildi")
else:
    print("[SKIP] roadmap.py — allaqachon yangilangan")

# ═══════════════════════════════════════════════════════════
# 2. Frontend types — Salary qo'shish
# ═══════════════════════════════════════════════════════════
TYPES = Path("qadam-miniapp/lib/types.ts")
if TYPES.exists():
    t = TYPES.read_text(encoding="utf-8")
    if "SalaryRange" not in t:
        t += '''

export type SalaryRange = {
  min: number;
  median: number;
  max: number;
};

export type SalaryData = {
  junior: SalaryRange;
  mid: SalaryRange;
  senior: SalaryRange;
  remote_usd: { junior: number; mid: number; senior: number };
};
'''
        TYPES.write_text(t, encoding="utf-8")
        print("[OK] types.ts — Salary qoshildi")
    else:
        print("[SKIP] types.ts — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 3. RoadmapView — B nuqtaga maosh jadvali
# ═══════════════════════════════════════════════════════════
RV = Path("qadam-miniapp/components/RoadmapView.tsx")
rv = RV.read_text(encoding="utf-8")

# B nuqta bo'limini topib, maosh qo'shish
if "salary_uzs" not in rv:
    old_b_point = '''<div className="grid grid-cols-2 gap-3 mb-4">
            {roadmap.b_point.junior_salary_uzs && ('''

    new_b_point = '''{roadmap.b_point.salary_uzs && roadmap.b_point.salary_uzs.junior && (
            <div className="mb-4 p-3 rounded-xl bg-[var(--tg-bg)]/60">
              <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)] mb-2">
                Maosh (ming som)
              </p>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-[10px] text-[var(--tg-hint)]">Junior</p>
                  <p className="text-sm font-bold">{roadmap.b_point.salary_uzs.junior.min}–{roadmap.b_point.salary_uzs.junior.max}</p>
                </div>
                <div>
                  <p className="text-[10px] text-[var(--tg-hint)]">Mid</p>
                  <p className="text-sm font-bold">{roadmap.b_point.salary_uzs.mid.min}–{roadmap.b_point.salary_uzs.mid.max}</p>
                </div>
                <div>
                  <p className="text-[10px] text-[var(--tg-hint)]">Senior</p>
                  <p className="text-sm font-bold">{roadmap.b_point.salary_uzs.senior.min}–{roadmap.b_point.salary_uzs.senior.max}</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3 mb-4">
            {roadmap.b_point.junior_salary_uzs && ('''

    if old_b_point in rv:
        rv = rv.replace(old_b_point, new_b_point)
        RV.write_text(rv, encoding="utf-8")
        print("[OK] RoadmapView.tsx — maosh jadvali qoshildi")
    else:
        print("[SKIP] RoadmapView.tsx — pattern topilmadi")
else:
    print("[SKIP] RoadmapView.tsx — allaqachon bor")

print()
print("=" * 60)
print("Maosh integratsiyasi — TAYYOR!")
print("=" * 60)
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Real maosh malumotlari (HH.uz)"')
print("  git push")
print("  Render Manual Deploy")