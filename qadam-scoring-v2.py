# -*- coding: utf-8 -*-
"""Scoring v2 — PM spec bo'yicha (deterministik matematika)."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. ENGINE — signals.py (V_s ∈ [0, 10], T_s)
# ═══════════════════════════════════════════════════════════
SIGNALS = Path("qadam/backend/engine/signals.py")

SIGNALS.write_text(r'''"""
Signal Engine — PM spec (PHASE G).

Qoidalar:
- Likert 1-5 → value [0, 10] shkalada
- Trust Factor: measured=1.0, insufficient=0.6, conflicting=0.4
- Unmeasured signallar hisobga OLINMAYDI (0 emas!)
- Har bir signal uchun: value, trust, coverage (n ta answer), confidence
"""

LIKERT_TO_10 = {
    1: 0.0,
    2: 2.5,
    3: 5.0,
    4: 7.5,
    5: 10.0,
}

SIGNAL_KEYS = [
    "logical_thinking", "problem_solving", "technical_interest",
    "creative_design", "visual_logic", "user_empathy",
    "system_design", "analytical", "persistence", "math_logic",
    "attention_to_detail", "business_sense", "innovation",
]

# Trust Factor chegaralari
TRUST_MEASURED = 1.0
TRUST_INSUFFICIENT = 0.6
TRUST_CONFLICTING = 0.4
CONFLICT_STD_THRESHOLD = 3.0   # [0,10] shkalada std threshold
MIN_MEASURED_ANSWERS = 3        # measured bo'lish uchun kamida


def _collect_all_questions(questions):
    out = []
    for q in questions.get("stage_1", {}).get("questions", []):
        out.append(q)
    for dim in questions.get("stage_2", {}).get("dimensions", {}).values():
        out.extend(dim.get("questions", []))
    return out


def _classify_trust(contributions):
    """
    Har bir answer'dan kelgan normalized qiymatlar ro'yxati.
    - coverage: nechta javob keldi
    - std: qanchalik ziddiyatli
    """
    n = len(contributions)
    if n == 0:
        return None, "unmeasured", 0
    if n < MIN_MEASURED_ANSWERS:
        return TRUST_INSUFFICIENT, "insufficient", n

    # Std Dev hisoblash
    mean = sum(contributions) / n
    variance = sum((x - mean) ** 2 for x in contributions) / n
    std = variance ** 0.5

    if std > CONFLICT_STD_THRESHOLD:
        return TRUST_CONFLICTING, "conflicting", n
    return TRUST_MEASURED, "measured", n


def signals_from_answers(answers, questions):
    """
    Returns: {
        signal_key: {
            "value": float [0,10] | None,   # None = unmeasured
            "trust": float,                  # 0.0 - 1.0
            "evidence_state": str,           # measured|insufficient|conflicting|unmeasured
            "coverage": int,                 # measured answers soni
            "contributions": list[float],    # har answer'dan [0,10]
        }
    }
    """
    # Signal uchun xom qiymatlar
    raw = {k: [] for k in SIGNAL_KEYS}

    for q in _collect_all_questions(questions):
        qid = q["id"]
        if qid not in answers:
            continue
        a = answers[qid]
        if a is None:
            continue

        maps = q.get("maps_to", {}) or {}
        signal = maps.get("signal")
        if not signal or signal not in raw:
            continue

        w = float(maps.get("weight", 1.0))

        # Likert: 1-5 → [0, 10]
        if isinstance(a, (int, float)) and 1 <= int(a) <= 5:
            v = LIKERT_TO_10[int(a)]
        else:
            # Choice savol — neytral 5.0
            v = 5.0

        # Weighted contribution (weight bilan ko'paytirilgan)
        raw[signal].append(v * w)

    out = {}
    for k in SIGNAL_KEYS:
        contribs = raw[k]
        trust, state, count = _classify_trust(contribs)

        if state == "unmeasured" or not contribs:
            out[k] = {
                "value": None,
                "trust": 0.0,
                "evidence_state": "unmeasured",
                "coverage": 0,
                "contributions": [],
            }
            continue

        # Weighted average → [0, 10] shkalada
        avg = sum(contribs) / len(contribs)

        out[k] = {
            "value": round(avg, 2),
            "trust": trust,
            "evidence_state": state,
            "coverage": count,
            "contributions": [round(c, 2) for c in contribs],
        }

    return out
''', encoding="utf-8")
print("[OK] engine/signals.py — PM spec (V_s, T_s)")

# ═══════════════════════════════════════════════════════════
# 2. ENGINE — fit.py (formula)
# ═══════════════════════════════════════════════════════════
FIT = Path("qadam/backend/engine/fit.py")

FIT.write_text(r'''"""
Fit & Coverage & Confidence — PM spec (PHASE G).

Fit(c) = (Σ W_c,s · V_s · T_s) / (Σ W_c,s · 10) × 100
Coverage(c) = Σ W_c,s (measured) / Σ W_c,s (all)
Confidence(c) = Coverage × avg(T_s)
"""


def calculate_fit(signals, career):
    weights = career["signals"]  # {signal_key: weight 1-5}

    total_weight = sum(weights.values())

    # ─── Fit numerator / denominator ───
    num = 0.0
    measured_weight = 0.0
    trust_sum = 0.0
    measured_count = 0
    missing = []

    for sig, w in weights.items():
        s = signals.get(sig, {})
        if s.get("evidence_state") == "unmeasured" or s.get("value") is None:
            missing.append(sig)
            continue

        v = s["value"]           # [0, 10]
        t = s["trust"]           # 0.0 - 1.0

        num += w * v * t
        measured_weight += w
        trust_sum += t
        measured_count += 1

    # ─── Coverage ───
    coverage = (measured_weight / total_weight) if total_weight else 0.0

    # ─── Fit ───
    if measured_weight == 0 or measured_count == 0:
        fit = None
    else:
        fit = (num / (measured_weight * 10.0)) * 100.0

    # ─── Confidence ───
    if measured_count == 0:
        confidence = 0.0
    else:
        avg_trust = trust_sum / measured_count
        confidence = coverage * avg_trust

    # ─── Status ───
    if fit is None:
        status = "no_evidence"
    elif coverage < 0.5:
        status = "insufficient_coverage"
    else:
        status = "ok"

    return {
        "fit": round(fit, 2) if fit is not None else None,
        "coverage": round(coverage, 3),
        "confidence": round(confidence, 3),
        "measured_signals": measured_count,
        "missing_signals": missing,
        "status": status,
    }
''', encoding="utf-8")
print("[OK] engine/fit.py — PM formula")

# ═══════════════════════════════════════════════════════════
# 3. ENGINE — readiness.py
# ═══════════════════════════════════════════════════════════
READINESS = Path("qadam/backend/engine/readiness.py")

READINESS.write_text(r'''"""
Readiness — PM spec (PHASE G).

Readiness(c) = Base × P_computer × P_english × P_time

P_computer = 0.5     (agar device 'required' va user'da yo'q)
P_english  = 0.85^k  (k = yetishmayotgan darajalar soni)
P_time     = min(1, user_vaqti / career_minimal_vaqti)
"""

BASE_READINESS = 100.0

ENGLISH_ORDER = {"none": 0, "a2": 1, "b1": 2, "b2": 3, "c1": 4}

# Foydalanuvchi vaqti (kunlik soat) → numeric
TIME_TO_HOURS = {
    "lt_1h": 0.5,
    "1h": 1.0,
    "2_3h": 2.5,
    "4h_plus": 4.5,
    "full_time": 8.0,
}

# Career minimal vaqti (kunlik soat) — default
DEFAULT_MIN_HOURS = 2.0


def _p_computer(constraints, prerequisites):
    req = prerequisites.get("device")
    user = constraints.get("device")
    if req != "required":
        return 1.0
    if user in ("laptop", "both"):
        return 1.0
    if user == "smartphone_only":
        return 0.5
    return 0.5  # "none" ham


def _p_english(constraints, prerequisites):
    req = prerequisites.get("english", "none")
    user = constraints.get("english", "none")
    gap = ENGLISH_ORDER.get(req, 0) - ENGLISH_ORDER.get(user, 0)
    if gap <= 0:
        return 1.0
    return 0.85 ** gap


def _p_time(constraints, prerequisites):
    user_t = constraints.get("time", "2_3h")
    user_hours = TIME_TO_HOURS.get(user_t, 2.5)
    min_hours = prerequisites.get("min_hours", DEFAULT_MIN_HOURS)
    if min_hours <= 0:
        return 1.0
    return min(1.0, user_hours / min_hours)


def calculate_readiness(constraints, prerequisites):
    p_c = _p_computer(constraints, prerequisites)
    p_e = _p_english(constraints, prerequisites)
    p_t = _p_time(constraints, prerequisites)

    readiness = BASE_READINESS * p_c * p_e * p_t

    # Barrier ro'yxati (frontend uchun)
    barriers = []
    if p_c < 1.0:
        barriers.append({
            "type": "device",
            "level": "hard" if constraints.get("device") == "none" else "soft",
            "path": "Noutbuk topish yollari — grantlar, kutubxona, ijaraga olish",
        })
    if p_e < 1.0:
        req = prerequisites.get("english", "")
        barriers.append({
            "type": "language",
            "level": "soft",
            "path": f"Ingliz tilini {req.upper()} darajaga ko'tarish (3-6 oy)",
        })
    if p_t < 1.0:
        barriers.append({
            "type": "time",
            "level": "soft",
            "path": "Haftalik jadval tuzish, vaqt ajratish",
        })

    return {
        "readiness": round(readiness, 2),
        "p_computer": round(p_c, 3),
        "p_english": round(p_e, 3),
        "p_time": round(p_t, 3),
        "barriers": barriers,
        "has_hard_barrier": any(b["level"] == "hard" for b in barriers),
    }
''', encoding="utf-8")
print("[OK] engine/readiness.py — PM formula")

# ═══════════════════════════════════════════════════════════
# 4. ENGINE — ranking.py
# ═══════════════════════════════════════════════════════════
RANKING = Path("qadam/backend/engine/ranking.py")

RANKING.write_text(r'''"""
Ranking — PM spec (PHASE G).

Qoidalar:
- Coverage < 0.5 → tavsiya qilinmaydi
- Top 3-5, lekin dalil yetmasa — kamroq
- Confidence = Coverage × avg(T_s)
"""

import json
from pathlib import Path
from .fit import calculate_fit
from .readiness import calculate_readiness

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_roadmap_careers():
    careers = set()
    for name in [
        "roadmap_kb_v3.json", "roadmap_kb_v2.json",
        "roadmap_kb_v2_part_a.json", "roadmap_kb_v2_part_b.json",
    ]:
        p = DATA_DIR / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            careers.update(data.get("careers", {}).keys())
        except Exception:
            pass
    return careers


KB_CAREERS = _load_roadmap_careers()

MIN_COVERAGE = 0.5
TOP_N = 5


def rank_careers(signals, taxonomy, constraints, top_n=TOP_N):
    candidates = []
    excluded = []

    for cluster_key, cluster in taxonomy["clusters"].items():
        for career_key, career in cluster["careers"].items():
            if career_key not in KB_CAREERS:
                excluded.append({"career_id": career_key, "reason": "no_roadmap"})
                continue

            fit_result = calculate_fit(signals, career)

            if fit_result["status"] == "no_evidence":
                excluded.append({"career_id": career_key, "reason": "no_evidence"})
                continue
            if fit_result["status"] == "insufficient_coverage":
                excluded.append({
                    "career_id": career_key,
                    "reason": "coverage_below_0.5",
                    "coverage": fit_result["coverage"],
                })
                continue

            readiness_result = calculate_readiness(
                constraints, career.get("prerequisites", {})
            )

            # Composite score (Fit ustuvor, Readiness modifikator)
            composite = fit_result["fit"] * (
                0.7 + 0.3 * (readiness_result["readiness"] / 100.0)
            )

            candidates.append({
                "career_id": career_key,
                "cluster": cluster_key,
                "cluster_uz": cluster["uz"],
                "career_uz": career["uz"],
                "fit": fit_result["fit"],
                "coverage": fit_result["coverage"],
                "confidence": fit_result["confidence"],
                "measured_signals": fit_result["measured_signals"],
                "missing_signals": fit_result["missing_signals"],
                "readiness": readiness_result["readiness"],
                "p_computer": readiness_result["p_computer"],
                "p_english": readiness_result["p_english"],
                "p_time": readiness_result["p_time"],
                "barriers": readiness_result["barriers"],
                "has_hard_barrier": readiness_result["has_hard_barrier"],
                "learning_months": career.get("learning_months"),
                "pathway_type": career.get("pathway_type"),
                "composite_score": round(composite, 2),
            })

    candidates.sort(key=lambda x: -x["composite_score"])
    top = candidates[:top_n]

    # Global confidence
    if not top:
        confidence = "none"
    else:
        avg_cov = sum(c["coverage"] for c in top) / len(top)
        if avg_cov >= 0.75:
            confidence = "high"
        elif avg_cov >= 0.55:
            confidence = "medium"
        else:
            confidence = "low"

    return {
        "ranked": top,
        "excluded": excluded,
        "confidence": confidence,
        "total_candidates": len(candidates),
        "kb_careers_count": len(KB_CAREERS),
    }
''', encoding="utf-8")
print("[OK] engine/ranking.py — PM formula")

# ═══════════════════════════════════════════════════════════
# 5. TEST — formulalarni tekshirish
# ═══════════════════════════════════════════════════════════
TEST = Path("qadam/tests/test_scoring_v2.py")

TEST.write_text(r'''"""Scoring v2 — PM spec tekshiruvlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.signals import signals_from_answers
from engine.fit import calculate_fit
from engine.readiness import calculate_readiness
from data_loader import load_questions


def test_likert_converts_to_10_scale():
    """Likert 5 → 10.0, 1 → 0.0, 3 → 5.0"""
    from engine.signals import LIKERT_TO_10
    assert LIKERT_TO_10[1] == 0.0
    assert LIKERT_TO_10[3] == 5.0
    assert LIKERT_TO_10[5] == 10.0


def test_unmeasured_not_zero():
    """O'lchanmagan signal → value=None, state='unmeasured'."""
    questions = load_questions()
    signals = signals_from_answers({}, questions)
    for k, v in signals.items():
        assert v["value"] is None
        assert v["evidence_state"] == "unmeasured"
        assert v["trust"] == 0.0


def test_insufficient_with_few_answers():
    """1-2 javob → insufficient, trust=0.6."""
    questions = load_questions()
    # faqat 1 ta javob
    signals = signals_from_answers({"s2_q3": 4}, questions)
    s = signals["technical_interest"]
    assert s["evidence_state"] == "insufficient"
    assert s["trust"] == 0.6
    assert s["value"] is not None  # value bor, lekin trust past


def test_measured_with_3plus_answers():
    """3+ javob → measured, trust=1.0."""
    questions = load_questions()
    # 3 ta javob bir signalga
    answers = {"s2_q1": 4, "s2_q11": 4, "s2_q12": 4, "s2_q18": 4}
    signals = signals_from_answers(answers, questions)
    s = signals["persistence"]
    assert s["evidence_state"] == "measured"
    assert s["trust"] == 1.0
    assert s["coverage"] == 4


def test_fit_formula_100_percent():
    """Signal=10, trust=1.0, weight teng → Fit=100."""
    signals = {
        "logical_thinking": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "persistence": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
    }
    career = {"signals": {"logical_thinking": 5, "problem_solving": 5, "persistence": 5}}
    r = calculate_fit(signals, career)
    assert r["fit"] == 100.0
    assert r["coverage"] == 1.0
    assert r["confidence"] == 1.0


def test_fit_formula_50_percent():
    """Signal=5, trust=1.0 → Fit=50."""
    signals = {
        "logical_thinking": {"value": 5.0, "trust": 1.0, "evidence_state": "measured"},
    }
    career = {"signals": {"logical_thinking": 5}}
    r = calculate_fit(signals, career)
    assert r["fit"] == 50.0


def test_fit_coverage_below_half():
    """Coverage < 0.5 → status='insufficient_coverage'."""
    signals = {
        "logical_thinking": {"value": 8.0, "trust": 1.0, "evidence_state": "measured"},
    }
    # 5 ta signal kerak, faqat 1 ta o'lchangan → coverage=0.2
    career = {"signals": {
        "logical_thinking": 5, "problem_solving": 5, "persistence": 5,
        "attention_to_detail": 5, "analytical": 5,
    }}
    r = calculate_fit(signals, career)
    assert r["coverage"] < 0.5
    assert r["status"] == "insufficient_coverage"


def test_fit_unmeasured_excluded():
    """Unmeasured signal hisobga olinmaydi (0 emas)."""
    signals = {
        "logical_thinking": {"value": 10.0, "trust": 1.0, "evidence_state": "measured"},
        "problem_solving": {"value": None, "trust": 0.0, "evidence_state": "unmeasured"},
    }
    career = {"signals": {"logical_thinking": 5, "problem_solving": 5}}
    r = calculate_fit(signals, career)
    # faqat logical_thinking hisobga olinadi → Fit=100, coverage=0.5
    assert r["fit"] == 100.0
    assert r["coverage"] == 0.5
    assert r["measured_signals"] == 1
    assert "problem_solving" in r["missing_signals"]


def test_readiness_base_100():
    """Barcha shartlar bajarilsa → Readiness=100."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "b2", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["readiness"] == 100.0
    assert r["p_computer"] == 1.0
    assert r["p_english"] == 1.0
    assert r["p_time"] == 1.0


def test_readiness_no_computer():
    """Device yo'q → P_computer=0.5."""
    r = calculate_readiness(
        constraints={"device": "none", "english": "b1", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_computer"] == 0.5
    assert r["readiness"] == 50.0


def test_readiness_english_gap():
    """English A2 vs B1 kerak → 1 gap → 0.85."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "a2", "time": "2_3h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_english"] == 0.85
    assert abs(r["readiness"] - 85.0) < 0.01


def test_readiness_time_ratio():
    """User 1h, kerak 2h → 0.5."""
    r = calculate_readiness(
        constraints={"device": "laptop", "english": "b1", "time": "1h"},
        prerequisites={"device": "required", "english": "b1", "min_hours": 2.0},
    )
    assert r["p_time"] == 0.5
    assert r["readiness"] == 50.0
''', encoding="utf-8")
print("[OK] tests/test_scoring_v2.py — 12 test")

print()
print("=" * 60)
print("Scoring v2 — TAYYOR!")
print("=" * 60)
print()
print("Formula (PM spec):")
print("  • V_s ∈ [0, 10] shkalada")
print("  • T_s = measured(1.0) | insufficient(0.6) | conflicting(0.4)")
print("  • Fit = Σ(W·V·T) / Σ(W·10) × 100")
print("  • Coverage = W_measured / W_total")
print("  • Confidence = Coverage × avg(T_s)")
print("  • Readiness = Base × P_computer × P_english × P_time")
print()
print("TESTLAR:")
print("  1. Likert → [0,10] konversiya")
print("  2. Unmeasured ≠ 0")
print("  3. Insufficient (1-2 javob)")
print("  4. Measured (3+ javob)")
print("  5. Fit = 100%")
print("  6. Fit = 50%")
print("  7. Coverage < 0.5 → excluded")
print("  8. Unmeasured hisobga olinmaydi")
print("  9. Readiness base = 100")
print(" 10. No computer → 0.5")
print(" 11. English gap → 0.85^k")
print(" 12. Time ratio")
print()
print("KEYINGI:")
print("  cd qadam")
print("  ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests/test_scoring_v2.py -v")
print("  cd ..")
print("  git add -A")
print('  git commit -m "Scoring v2: PM spec formulas (Fit/Coverage/Readiness)"')
print("  git push")