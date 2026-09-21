# -*- coding: utf-8 -*-
"""QADAM v6 — PDF ranglar + backend roadmap-only (majburiy)."""
import json
from pathlib import Path
import re

# ═══════════════════════════════════════════════════════════
# 1. RANKING — FAQAT roadmap'li (majburiy, paramsiz)
# ═══════════════════════════════════════════════════════════
RANKING = Path("qadam/backend/engine/ranking.py")
RANKING.write_text('''"""
Ranking Engine v3 — FAQAT roadmap'da mavjud bo'lgan career'larni qaytaradi.
Bu MAJBURIY — foydalanuvchi premium to'lab, "tayyorlanmoqda" ko'rmasligi uchun.
"""
import json
from pathlib import Path
from .fit import calculate_fit
from .readiness import calculate_readiness

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_all_roadmap_careers():
    """Barcha roadmap KB fayllaridan career'larni birlashtirish."""
    careers = set()

    # v2 (asosiy)
    for name in ["roadmap_kb_v2.json", "roadmap_kb_v2_part_a.json",
                 "roadmap_kb_v2_part_b.json", "roadmap_kb_v1.json"]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass

    print(f"[ranking] KB careers yuklandi: {len(careers)} ta -> {sorted(careers)}")
    return careers


KB_CAREERS = _load_all_roadmap_careers()


def rank_careers(signals, taxonomy, constraints, min_coverage=0.5, top_n=3):
    """
    FAQAT roadmap'da mavjud bo'lgan career'lardan Top-N.
    Agar roadmap'li 3 tadan kam bo'lsa — mavjudlarini qaytaradi.
    """
    candidates = []
    excluded = []

    for cluster_key, cluster in taxonomy["clusters"].items():
        for career_key, career in cluster["careers"].items():
            # ⚠️ MAJBURIY FILTR — roadmap'siz career'lar HECH QACHON ko'rinmaydi
            if career_key not in KB_CAREERS:
                excluded.append({"career_id": career_key, "reason": "no_roadmap"})
                continue

            fit_result = calculate_fit(signals, career)
            if fit_result["fit"] is None:
                excluded.append({"career_id": career_key, "reason": "insufficient_data"})
                continue
            if fit_result["coverage"] < min_coverage:
                excluded.append({
                    "career_id": career_key, "reason": "low_coverage",
                    "coverage": fit_result["coverage"], "fit": fit_result["fit"],
                })
                continue

            readiness_result = calculate_readiness(
                constraints, career.get("prerequisites", {})
            )
            composite = fit_result["fit"] * (
                0.7 + 0.3 * (readiness_result["readiness"] / 100)
            )

            candidates.append({
                "career_id": career_key,
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                "career_uz": career["uz"],
                "fit": fit_result["fit"],
                "coverage": fit_result["coverage"],
                "readiness": readiness_result["readiness"],
                "barriers": readiness_result["barriers"],
                "has_hard_barrier": readiness_result["has_hard_barrier"],
                "missing_signals": fit_result["missing"],
                "learning_months": career.get("learning_months"),
                "pathway_type": career.get("pathway_type"),
                "has_roadmap": True,
                "composite_score": round(composite, 1),
            })

    candidates.sort(key=lambda x: -x["composite_score"])
    top = candidates[:top_n]

    if len(top) >= 2:
        gap = top[0]["composite_score"] - top[1]["composite_score"]
    else:
        gap = 100
    avg_coverage = sum(c["coverage"] for c in top) / len(top) if top else 0

    if avg_coverage >= 0.75 and gap >= 5:
        confidence = "high"
    elif avg_coverage >= 0.55:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "ranked": top,
        "excluded_low_coverage": excluded,
        "confidence": confidence,
        "total_candidates": len(candidates),
        "kb_careers_count": len(KB_CAREERS),
    }
''', encoding="utf-8")
print("[OK] ranking.py — FAQAT roadmap'li career'lar (majburiy)")


# ═══════════════════════════════════════════════════════════
# 2. DIAGNOSTIC — top_n=3 MAJBURIY
# ═══════════════════════════════════════════════════════════
DIAG = Path("qadam/backend/api/diagnostic.py")
diag = DIAG.read_text(encoding="utf-8")

# Barcha rank_careers chaqiruvlarida top_n=3
diag = re.sub(r'top_n\s*=\s*5', 'top_n=3', diag)
diag = re.sub(r'top_n\s*=\s*4', 'top_n=3', diag)

# Stage1 — min_coverage=0.3 (seed signallar uchun), top_n=5 → 3
diag = diag.replace(
    'min_coverage=0.3, top_n=5',
    'min_coverage=0.3, top_n=3',
)
# Stage2 — min_coverage=0.5
diag = diag.replace(
    'min_coverage=0.5, top_n=5',
    'min_coverage=0.5, top_n=3',
)

DIAG.write_text(diag, encoding="utf-8")
print("[OK] diagnostic.py — top_n=3")


# ═══════════════════════════════════════════════════════════
# 3. GLOBALS.CSS — Print ranglar QAT'IY
# ═══════════════════════════════════════════════════════════
GLOBALS = Path("qadam-miniapp/app/globals.css")
css = GLOBALS.read_text(encoding="utf-8")

# Barcha eski @media print bloklarni olib tashlash
css = re.sub(r'@media print \{.*?\n\}', '', css, flags=re.DOTALL)
css = re.sub(r'/\* ═+\s*PRINT.*?\*/\s*@media print \{.*?\n\}', '', css, flags=re.DOTALL)

PRINT_CSS = '''

/* ═══════════════════════════════════════════════════════════
   PRINT / PDF — QAT'IY ranglar + A4 full width
   Chrome'dagi "Background graphics" muammosi CSS bilan hal qilingan
   ═══════════════════════════════════════════════════════════ */
@media print {

  /* ─── ROOT DARAJASIDA MAJBURIY ─── */
  html {
    background: #ffffff !important;
    color: #0a0a0f !important;
  }

  /* ─── CSS O'ZGARUVCHILARNI QAT'IY OVERRIDE ─── */
  :root, * {
    --tg-bg: #ffffff !important;
    --tg-text: #0a0a0f !important;
    --tg-hint: #6b7280 !important;
    --tg-link: #4f46e5 !important;
    --tg-button: #6366f1 !important;
    --tg-button-text: #ffffff !important;
    --tg-secondary-bg: #f3f4f6 !important;
  }

  /* ─── RANGNI SAQLASH (BRAUZERGA MAJBURAN) ─── */
  html, body, * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }

  /* ─── ANIMATSIYALARNI O'CHIRISH ─── */
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    transform: none !important;
    opacity: 1 !important;
    box-shadow: none !important;
    text-shadow: none !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
  }

  /* ─── UMUMIY FON VA MATN ─── */
  body, main {
    background: #ffffff !important;
    color: #0a0a0f !important;
    font-size: 10pt;
    line-height: 1.45;
  }

  /* ─── A4 FULL WIDTH ─── */
  main, main.print-full, .print-full {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  @page {
    size: A4;
    margin: 8mm 10mm;
  }

  /* ─── KARTALAR — OCH FON, QORA MATN ─── */
  .card,
  [class*="rounded-2xl"],
  [class*="rounded-xl"] {
    background: #f9fafb !important;
    color: #0a0a0f !important;
    border: 1px solid #e5e7eb !important;
    padding: 8pt 10pt !important;
    margin-bottom: 6pt !important;
    break-inside: auto;
    page-break-inside: auto;
  }

  /* ─── GRADIENT KARTALAR (och fon) ─── */
  [class*="from-indigo-500/20"],
  [class*="from-indigo-500/15"] {
    background: #eef2ff !important;
    border-color: #c7d2fe !important;
  }
  [class*="from-amber-500/15"],
  [class*="from-amber-500/20"] {
    background: #fffbeb !important;
    border-color: #fde68a !important;
  }
  [class*="from-emerald-500/20"],
  [class*="from-emerald-500/15"] {
    background: #ecfdf5 !important;
    border-color: #a7f3d0 !important;
  }
  [class*="from-slate-500/10"],
  [class*="from-slate-500/15"] {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
  }

  /* ─── UMUMIY MATN — QORA ─── */
  p, span, li, h1, h2, h3, h4, h5, h6, strong, em, b, i {
    color: #0a0a0f !important;
  }

  /* ─── LEKIN RANGLI ELEMENTLAR — O'Z RANGI ─── */
  [class*="text-emerald"] { color: #059669 !important; }
  [class*="text-red-"] { color: #dc2626 !important; }
  [class*="text-amber"] { color: #d97706 !important; }
  [class*="text-indigo"] { color: #4f46e5 !important; }
  [class*="text-purple"] { color: #7c3aed !important; }
  [class*="text-blue"] { color: #2563eb !important; }
  [class*="text-cyan"] { color: #0891b2 !important; }
  [class*="text-slate"] { color: #475569 !important; }
  [class*="text-\\[var\\(--tg-hint\\)\\]"] { color: #6b7280 !important; }

  /* ─── GRADIENT MATN — BIR RANG ─── */
  .gradient-text {
    background: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    -webkit-text-fill-color: #4f46e5 !important;
    color: #4f46e5 !important;
    font-weight: 700;
  }

  /* ─── BADGE va PILL — RANGLI ─── */
  [class*="bg-indigo-500/20"],
  [class*="bg-indigo-500/30"] { background: #e0e7ff !important; color: #3730a3 !important; }
  [class*="bg-purple-500/20"],
  [class*="bg-purple-500/30"] { background: #f3e8ff !important; color: #6b21a8 !important; }
  [class*="bg-emerald-500/20"],
  [class*="bg-emerald-500/30"],
  [class*="bg-emerald-500/40"] { background: #d1fae5 !important; color: #065f46 !important; }
  [class*="bg-amber-500/20"],
  [class*="bg-amber-500/30"] { background: #fef3c7 !important; color: #92400e !important; }
  [class*="bg-blue-500/20"] { background: #dbeafe !important; color: #1e40af !important; }
  [class*="bg-red-400/20"] { background: #fee2e2 !important; color: #991b1b !important; }
  [class*="bg-slate-500/15"],
  [class*="bg-slate-500/20"] { background: #f1f5f9 !important; color: #334155 !important; }

  /* ─── PROGRESS BAR — RANGLI ─── */
  [class*="bg-gradient-to-r"][class*="from-indigo-500"] {
    background: linear-gradient(to right, #6366f1, #a855f7) !important;
    -webkit-print-color-adjust: exact !important;
  }
  [class*="bg-gradient-to-br"][class*="from-slate-500"] {
    background: linear-gradient(to bottom right, #64748b, #334155) !important;
  }
  [class*="bg-gradient-to-br"][class*="from-blue-500"] {
    background: linear-gradient(to bottom right, #3b82f6, #06b6d4) !important;
  }
  [class*="bg-gradient-to-br"][class*="from-purple-500"] {
    background: linear-gradient(to bottom right, #a855f7, #d946ef) !important;
  }
  [class*="bg-gradient-to-br"][class*="from-amber-500"] {
    background: linear-gradient(to bottom right, #f59e0b, #f97316) !important;
  }
  [class*="bg-gradient-to-br"][class*="from-emerald-500"] {
    background: linear-gradient(to bottom right, #10b981, #14b8a6) !important;
  }

  /* ─── SVG PROGRESS RING ─── */
  svg {
    -webkit-print-color-adjust: exact !important;
  }
  svg circle {
    -webkit-print-color-adjust: exact !important;
  }

  /* ─── ACCORDION — HAMMASI OCHIQ ─── */
  [data-accordion-content],
  [data-calendar-body] {
    display: block !important;
    max-height: none !important;
    height: auto !important;
    overflow: visible !important;
    opacity: 1 !important;
    margin-top: 6pt !important;
  }

  [data-chevron] { display: none !important; }

  /* ─── CHEGARALAR ─── */
  [class*="border-indigo-500"] { border-color: #c7d2fe !important; }
  [class*="border-emerald-500"] { border-color: #a7f3d0 !important; }
  [class*="border-amber-500"] { border-color: #fde68a !important; }
  [class*="border-slate-500"] { border-color: #cbd5e1 !important; }
  [class*="border-purple-500"] { border-color: #d8b4fe !important; }

  /* ─── TIMELINE ─── */
  [class*="from-slate-500"][class*="via-blue-500"] {
    background: linear-gradient(to bottom, #64748b, #3b82f6, #a855f7, #f59e0b, #10b981) !important;
  }

  /* ─── MATN O'LCHAMLARI ─── */
  h1 { font-size: 20pt; margin: 0 0 4pt; }
  h2 { font-size: 15pt; margin: 10pt 0 5pt; page-break-after: avoid; }
  h3 { font-size: 12pt; margin: 6pt 0 3pt; page-break-after: avoid; }
  h4 { font-size: 10.5pt; margin: 5pt 0 2pt; page-break-after: avoid; }
  p, li { font-size: 9.5pt; }
  .text-xs, [class*="text-\\[10px\\]"] { font-size: 8pt !important; }
  .text-sm { font-size: 9.5pt !important; }

  /* ─── RO'YXATLAR ─── */
  ul, ol { margin: 3pt 0; padding-left: 12pt; }
  li { margin: 1.5pt 0; break-inside: avoid; }

  /* ─── TUGMALAR — YASHIRISH ─── */
  button, .btn-primary {
    display: none !important;
  }

  /* ─── LINKLAR ─── */
  a {
    color: #4f46e5 !important;
    text-decoration: underline;
    text-decoration-color: #c7d2fe;
  }

  /* ─── SAHIFA BO'LINMALARI ─── */
  [class*="space-y"] > * {
    break-inside: auto;
  }

  /* ─── SAHIFA URL VA SANA — YASHIRISH (Chrome) ─── */
  @page {
    @top-left { content: ""; }
    @top-right { content: ""; }
    @bottom-left { content: ""; }
    @bottom-right { content: ""; }
  }
}
'''

css = css.rstrip() + PRINT_CSS + "\n"
GLOBALS.write_text(css, encoding="utf-8")
print("[OK] globals.css — print ranglar QAT'IY")


# ═══════════════════════════════════════════════════════════
# 4. TEKSHIRISH
# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("v6 — Tayyor!")
print("=" * 60)
print()
print("1. ranking.py — MAJBURIY faqat roadmap'li career'lar")
print("2. diagnostic.py — top_n=3")
print("3. globals.css — PDF ranglar QAT'IY")
print()
print("⚠️ MUHIM: PDF saqlashda brauzer sozlamalari:")
print("  Chrome print dialog → 'More settings' →")
print("  ✅ 'Background graphics' BELGILANISHI SHART")
print()
print("Keyingi: git push + Render MANUAL deploy")