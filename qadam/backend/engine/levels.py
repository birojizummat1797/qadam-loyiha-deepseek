"""User-facing levels instead of percentages (PM P0-1, 2026-10-03).

Fit, readiness and confidence stay internal numbers. Users see:
- evidence level: how much of the career's signal weight was measured
  (thresholds reuse existing engine rules: MIN_COVERAGE = 0.5 in ranking,
  0.75 = ranking's "high" confidence);
- barriers in words (device / language / time), never a readiness percentage.
No fit threshold is used: fit is not shown as a verdict.
"""

EVIDENCE_ENOUGH = 0.75
EVIDENCE_PARTIAL = 0.5

EVIDENCE_LABELS_UZ = {
    "enough": "Ma'lumot yetarli",
    "partial": "Ma'lumot qisman",
    "insufficient": "Ma'lumot yetarli emas",
}

BARRIER_LABELS_UZ = {
    "device": "Qurilma kerak bo'ladi",
    "language": "Ingliz tilini oshirish kerak",
    "time": "Ko'proq vaqt kerak bo'ladi",
}


def evidence_level(coverage) -> str:
    if coverage is None:
        return "insufficient"
    if coverage >= EVIDENCE_ENOUGH:
        return "enough"
    if coverage >= EVIDENCE_PARTIAL:
        return "partial"
    return "insufficient"


def context_status(readiness_result) -> str:
    """unknown | clear | barriers — readiness as words, not a number."""
    if not readiness_result or readiness_result.get("readiness") is None:
        return "unknown"
    return "barriers" if readiness_result.get("barriers") else "clear"
