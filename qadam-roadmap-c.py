# -*- coding: utf-8 -*-
"""QADAM Roadmap v2.0 — Part C: merge + engine + frontend."""
import json
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. MERGE — Part A + B → roadmap_kb_v2.json
# ═══════════════════════════════════════════════════════════

DATA_DIR = Path("qadam/backend/data")
part_a = json.loads((DATA_DIR / "roadmap_kb_v2_part_a.json").read_text(encoding="utf-8"))
part_b = json.loads((DATA_DIR / "roadmap_kb_v2_part_b.json").read_text(encoding="utf-8"))

merged_careers = {**part_a["careers"], **part_b["careers"]}
merged = {
    "version": "v2.0",
    "created_at": "2026-09-21",
    "note": "QADAM Roadmap KB v2.0 — ACQ-style, 5 ta to'liq career",
    "careers": merged_careers,
}
(DATA_DIR / "roadmap_kb_v2.json").write_text(
    json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("[OK] roadmap_kb_v2.json — " + str(len(merged_careers)) + " ta career")


# ═══════════════════════════════════════════════════════════
# 2. ENGINE — roadmap.py yangilash (v2 format)
# ═══════════════════════════════════════════════════════════

ENGINE_PATH = Path("qadam/backend/engine/roadmap.py")
engine_code = '''"""
Roadmap Engine v2.0 — ACQ uslubida.
A nuqta → Yo'l (5 stage) → B nuqta + Calendar + First 3 Actions.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

# v2 KB yuklash
KB_V2 = json.loads((DATA_DIR / "roadmap_kb_v2.json").read_text(encoding="utf-8"))
# v1 (fallback) — hali ham mavjud
try:
    KB_V1 = json.loads((DATA_DIR / "roadmap_kb_v1.json").read_text(encoding="utf-8"))
except Exception:
    KB_V1 = {"careers": {}}


def build_roadmap(career_id, readiness_result, user_constraints, signals=None):
    """
    Roadmap — v2 formatda (agar mavjud bo'lsa), aks holda v1 (fallback).
    """
    # v2 dan izlash
    kb2 = KB_V2["careers"].get(career_id)
    if kb2:
        return _build_v2(career_id, kb2, readiness_result, user_constraints, signals)

    # v1 fallback
    kb1 = KB_V1["careers"].get(career_id)
    if kb1:
        return _build_v1_fallback(career_id, kb1, readiness_result)

    # Hech narsa yo'q — placeholder
    return _placeholder(career_id, readiness_result)


def _build_v2(career_id, kb, readiness_result, user_constraints, signals):
    """Yangi ACQ-style format."""
    barriers = readiness_result.get("barriers", [])

    # ── A NUQTA — foydalanuvchining hozirgi holati ──
    a_point = {
        "uz": "Sizning hozirgi holatingiz",
        "constraints": [
            {"type": b["type"], "level": b["level"], "solution": b.get("path", "")}
            for b in barriers
        ],
        "existing_constraints": user_constraints,
        "signal_summary": _signal_summary(signals) if signals else {},
    }

    # ── B NUQTA ──
    b_point = kb.get("b_point", {})

    # ── YO'L — 5 stage ──
    stages = []
    for s in kb.get("stages", []):
        stages.append({
            "n": s["n"],
            "name": s["name"],
            "name_uz": s["name_uz"],
            "weeks": s["weeks"],
            "role": s["role"],
            "daily_hours": s["daily_hours"],
            "graduate_by": s["graduate_by"],
            "constraints": [{"problem": c[0], "solution": c[1]} for c in s.get("constraints", [])],
            "daily_focus": s.get("daily_focus", []),
            "signs_right": s.get("signs_right", []),
            "signs_wrong": s.get("signs_wrong", []),
            "graduate_criteria": s.get("graduate_criteria", []),
            "challenges": s.get("challenges", []),
            "skills_gained": s.get("skills_gained", []),
        })

    return {
        "career_id": career_id,
        "career_uz": kb["uz"],
        "cluster": kb.get("cluster", ""),
        "cluster_uz": kb.get("cluster_uz", ""),
        "why_this_path": kb["why"],
        "version": "v2.0",

        # ── 3 asosiy blok ──
        "a_point": a_point,
        "path": {
            "uz": "A dan B gacha yo'l",
            "total_weeks": sum(s["weeks"] for s in stages),
            "stages": stages,
        },
        "b_point": b_point,

        # ── Bonus bloklar ──
        "calendar_30d": kb.get("calendar_30d", []),
        "first_3_actions": kb.get("first_3_actions", []),
        "mentor_path": kb.get("mentor_path", []),
        "resources": kb.get("resources", []),
        "milestones": kb.get("milestones", []),

        "is_placeholder": False,
    }


def _signal_summary(signals):
    """Top signallar qisqa tarzda."""
    if not signals:
        return {}
    measured = [
        {"key": k, "score": round(v["score"], 3)}
        for k, v in signals.items()
        if v.get("score") is not None
    ]
    measured.sort(key=lambda x: -x["score"])
    return {
        "top_5": measured[:5],
        "total_measured": len(measured),
    }


def _build_v1_fallback(career_id, kb, readiness_result):
    """Eski v1 formatni yangi ko'rinishga moslashtirish."""
    barriers = readiness_result.get("barriers", [])
    barrier_actions = []
    for b in barriers:
        if b.get("path"):
            barrier_actions.append({
                "barrier_type": b["type"],
                "level": b["level"],
                "action": b["path"],
                "priority": "high" if b["level"] == "hard" else "medium",
            })

    # v1 stage'larni v2 ga moslashtirish
    stages = []
    for i, phase in enumerate(kb["roadmap"]["phases"]):
        stages.append({
            "n": i + 1,
            "name": phase["period"].upper(),
            "name_uz": phase["goal"],
            "weeks": 4,
            "role": "O'rganuvchi",
            "daily_hours": "2 soat",
            "graduate_by": phase["goal"],
            "constraints": [],
            "daily_focus": phase["actions"],
            "signs_right": [],
            "signs_wrong": [],
            "graduate_criteria": phase["actions"],
            "challenges": [],
            "skills_gained": [],
        })

    return {
        "career_id": career_id,
        "career_uz": kb["uz"],
        "why_this_path": kb["why"],
        "version": "v1.0",
        "a_point": {"constraints": barrier_actions},
        "path": {"total_weeks": len(stages) * 4, "stages": stages},
        "b_point": {"outcomes": kb.get("projects", [])},
        "calendar_30d": [],
        "first_3_actions": kb["roadmap"]["first_steps"],
        "mentor_path": [],
        "resources": kb.get("resources", []),
        "milestones": [{"week": (i+1)*4, "milestone": m} for i, m in enumerate(kb["roadmap"]["milestones"])],
        "is_placeholder": False,
        "fallback_from": "v1",
    }


def _placeholder(career_id, readiness_result):
    barriers = readiness_result.get("barriers", [])
    return {
        "career_id": career_id,
        "career_uz": career_id,
        "why_this_path": "Bu yo'nalish signallaringizga mos, roadmap tayyorlanmoqda.",
        "version": "placeholder",
        "a_point": {"constraints": [
            {"type": b["type"], "level": b["level"], "solution": b.get("path", "")}
            for b in barriers
        ]},
        "path": {"total_weeks": 0, "stages": []},
        "b_point": {},
        "calendar_30d": [],
        "first_3_actions": ["Roadmap tayyorlanmoqda..."],
        "mentor_path": [],
        "resources": [],
        "milestones": [],
        "is_placeholder": True,
    }


def build_full_report(ranked, constraints, taxonomy, signals=None):
    reports = []
    for item in ranked:
        rr = {"readiness": item["readiness"], "barriers": item["barriers"]}
        rm = build_roadmap(item["career_id"], rr, constraints, signals)
        reports.append({
            "career": {
                "id": item["career_id"],
                "uz": item["career_uz"],
                "cluster": item["cluster"],
                "cluster_uz": item["cluster_uz"],
                "pathway_type": item["pathway_type"],
                "learning_months": item["learning_months"],
            },
            "fit": item["fit"],
            "readiness": item["readiness"],
            "coverage": item["coverage"],
            "barriers": item["barriers"],
            "has_hard_barrier": item["has_hard_barrier"],
            "roadmap": rm,
        })
    return {"careers": reports}
'''
ENGINE_PATH.write_text(engine_code, encoding="utf-8")
print("[OK] engine/roadmap.py — v2 formatga yangilandi")


# ═══════════════════════════════════════════════════════════
# 3. FRONTEND — Report sahifasida yangi roadmap komponenti
# ═══════════════════════════════════════════════════════════

FRONTEND_DIR = Path("qadam-miniapp/components")

# 3.1. RoadmapView.tsx — asosiy komponent
roadmap_view = r'''"use client";

import { useState } from "react";
import {
  MapPin, Target, Calendar, ChevronDown, ChevronRight,
  AlertCircle, Check, X, TrendingUp, Clock, BookOpen,
} from "lucide-react";

type Constraint = { problem?: string; type?: string; level?: string; solution: string };
type Stage = {
  n: number;
  name: string;
  name_uz: string;
  weeks: number;
  role: string;
  daily_hours: string;
  graduate_by: string;
  constraints: Constraint[];
  daily_focus: string[];
  signs_right: string[];
  signs_wrong: string[];
  graduate_criteria: string[];
  challenges: string[];
  skills_gained: string[];
};

type Roadmap = {
  career_id: string;
  career_uz: string;
  cluster_uz: string;
  why_this_path: string;
  version?: string;
  a_point: {
    constraints: Constraint[];
    existing_constraints?: Record<string, any>;
    signal_summary?: { top_5: { key: string; score: number }[]; total_measured: number };
  };
  path: { total_weeks: number; stages: Stage[] };
  b_point: {
    junior_salary_uzs?: string;
    remote_salary_usd?: string;
    outcomes?: string[];
    next_step?: string;
  };
  calendar_30d: { w: number; theme: string; days: string[] }[];
  first_3_actions: string[];
  mentor_path: string[];
  resources: { name: string; url: string }[];
  milestones: { week: number; milestone: string }[];
  is_placeholder?: boolean;
};

const SIGNAL_UZ: Record<string, string> = {
  logical_thinking: "Mantiq", problem_solving: "Muammo hal",
  technical_interest: "Texnika", creative_design: "Ijodiy dizayn",
  visual_logic: "Vizual mantiq", user_empathy: "Empatiya",
  system_design: "Tizim", analytical: "Tahlil",
  persistence: "Qatiyat", math_logic: "Matematika",
  attention_to_detail: "Detal", business_sense: "Biznes",
  innovation: "Innovatsiya",
};

export function RoadmapView({ roadmap }: { roadmap: Roadmap }) {
  const [openStage, setOpenStage] = useState<number | null>(0);
  const [showCalendar, setShowCalendar] = useState(false);

  if (!roadmap || roadmap.is_placeholder) {
    return (
      <div className="card">
        <p className="text-sm text-[var(--tg-hint)]">
          Bu yonalish uchun batafsil roadmap tez orada qoshiladi.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* NEGA BU MOS */}
      <div className="card">
        <h3 className="font-semibold mb-2 flex items-center gap-2">
          <Target className="w-4 h-4 text-emerald-400" />
          Nega bu sizga mos
        </h3>
        <p className="text-sm leading-relaxed">{roadmap.why_this_path}</p>
      </div>

      {/* A NUQTA */}
      <div className="card">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-indigo-400" />
          A NUQTA — Hozirgi holatingiz
        </h3>

        {roadmap.a_point?.signal_summary?.top_5 && (
          <div className="mb-3">
            <p className="text-xs text-[var(--tg-hint)] mb-2">Kuchli signallaringiz:</p>
            <div className="space-y-1">
              {roadmap.a_point.signal_summary.top_5.map((s) => (
                <div key={s.key} className="flex items-center gap-2 text-xs">
                  <div className="w-24 capitalize">{SIGNAL_UZ[s.key] ?? s.key}</div>
                  <div className="flex-1 h-1.5 bg-[var(--tg-hint)]/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-400"
                      style={{ width: `${s.score * 100}%` }}
                    />
                  </div>
                  <span className="w-9 text-right text-[var(--tg-hint)]">
                    {Math.round(s.score * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {roadmap.a_point?.constraints?.length > 0 && (
          <div>
            <p className="text-xs text-[var(--tg-hint)] mb-2">
              Hal qilish kerak bolgan tosiqlar:
            </p>
            <div className="space-y-2">
              {roadmap.a_point.constraints.map((c, i) => (
                <div key={i} className="p-2 bg-[var(--tg-bg)] rounded-lg">
                  <div className="flex items-center gap-2 text-xs font-medium mb-1">
                    <AlertCircle
                      className={`w-3 h-3 ${
                        c.level === "hard" ? "text-red-400" : "text-amber-400"
                      }`}
                    />
                    <span className="capitalize">{c.problem ?? c.type}</span>
                    <span
                      className={`ml-auto text-[10px] px-1.5 py-0.5 rounded ${
                        c.level === "hard"
                          ? "bg-red-400/20 text-red-400"
                          : "bg-amber-400/20 text-amber-400"
                      }`}
                    >
                      {c.level}
                    </span>
                  </div>
                  {c.solution && (
                    <p className="text-xs text-[var(--tg-hint)] pl-5">
                      Yechim: {c.solution}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* YO'L — 5 stage */}
      <div className="card">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-amber-400" />
          A dan B gacha yol — {roadmap.path.total_weeks} hafta
        </h3>

        <div className="space-y-2">
          {roadmap.path.stages.map((s, i) => {
            const isOpen = openStage === i;
            return (
              <div
                key={i}
                className="border border-[var(--tg-hint)]/20 rounded-xl overflow-hidden"
              >
                <button
                  onClick={() => setOpenStage(isOpen ? null : i)}
                  className="w-full p-3 flex items-center gap-3 text-left hover:bg-[var(--tg-bg)]/50 transition"
                >
                  {isOpen ? (
                    <ChevronDown className="w-4 h-4 text-[var(--tg-hint)]" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-[var(--tg-hint)]" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400">
                        STAGE {s.n}
                      </span>
                      <span className="font-semibold text-sm">{s.name_uz}</span>
                    </div>
                    <p className="text-xs text-[var(--tg-hint)]">
                      {s.weeks} hafta &middot; {s.daily_hours}
                    </p>
                  </div>
                </button>

                {isOpen && (
                  <div className="p-3 border-t border-[var(--tg-hint)]/20 space-y-4">
                    {/* Rol + maqsad */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="p-2 bg-[var(--tg-bg)] rounded-lg">
                        <p className="text-[var(--tg-hint)] mb-0.5">Rolingiz</p>
                        <p className="font-medium">{s.role}</p>
                      </div>
                      <div className="p-2 bg-[var(--tg-bg)] rounded-lg">
                        <p className="text-[var(--tg-hint)] mb-0.5">Graduate by</p>
                        <p className="font-medium">{s.graduate_by}</p>
                      </div>
                    </div>

                    {/* Daily focus */}
                    {s.daily_focus.length > 0 && (
                      <Section title="Har kun nima qilish" icon={Clock} color="text-blue-400">
                        <ul className="space-y-1">
                          {s.daily_focus.map((d, j) => (
                            <li key={j} className="flex gap-2 text-xs">
                              <span className="text-blue-400">&bull;</span>
                              <span>{d}</span>
                            </li>
                          ))}
                        </ul>
                      </Section>
                    )}

                    {/* Constraints */}
                    {s.constraints.length > 0 && (
                      <Section title="To'siqlar va yechim" icon={AlertCircle} color="text-amber-400">
                        <div className="space-y-2">
                          {s.constraints.map((c, j) => (
                            <div key={j} className="p-2 bg-[var(--tg-bg)] rounded-lg text-xs">
                              <p className="font-medium mb-1">&#10007; {c.problem}</p>
                              <p className="text-[var(--tg-hint)]">&#10003; {c.solution}</p>
                            </div>
                          ))}
                        </div>
                      </Section>
                    )}

                    {/* Signs right / wrong */}
                    {s.signs_right.length > 0 && (
                      <div className="grid grid-cols-1 gap-3">
                        <Section title="To'g'ri ketayapsizmi?" icon={Check} color="text-emerald-400">
                          <ul className="space-y-1">
                            {s.signs_right.map((x, j) => (
                              <li key={j} className="flex gap-2 text-xs">
                                <Check className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                                <span>{x}</span>
                              </li>
                            ))}
                          </ul>
                        </Section>
                        <Section title="Yaxshilash kerak" icon={X} color="text-red-400">
                          <ul className="space-y-1">
                            {s.signs_wrong.map((x, j) => (
                              <li key={j} className="flex gap-2 text-xs">
                                <X className="w-3 h-3 text-red-400 shrink-0 mt-0.5" />
                                <span>{x}</span>
                              </li>
                            ))}
                          </ul>
                        </Section>
                      </div>
                    )}

                    {/* Graduate criteria */}
                    {s.graduate_criteria.length > 0 && (
                      <Section title="Keyingi stage'ga o'tish sharti" icon={Target} color="text-indigo-400">
                        <ul className="space-y-1">
                          {s.graduate_criteria.map((x, j) => (
                            <li key={j} className="flex gap-2 text-xs">
                              <span className="text-indigo-400">&rarr;</span>
                              <span>{x}</span>
                            </li>
                          ))}
                        </ul>
                      </Section>
                    )}

                    {/* Challenges */}
                    {s.challenges.length > 0 && (
                      <Section title="Qiyinchiliklar" icon={AlertCircle} color="text-red-400">
                        <ul className="space-y-1">
                          {s.challenges.map((x, j) => (
                            <li key={j} className="text-xs text-[var(--tg-hint)]">
                              &bull; {x}
                            </li>
                          ))}
                        </ul>
                      </Section>
                    )}

                    {/* Skills gained */}
                    {s.skills_gained.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {s.skills_gained.map((sk, j) => (
                          <span
                            key={j}
                            className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400"
                          >
                            {sk}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* B NUQTA */}
      <div className="card bg-gradient-to-br from-emerald-500/10 to-indigo-500/10 border border-emerald-500/30">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Target className="w-4 h-4 text-emerald-400" />
          B NUQTA — Erishishingiz mumkin
        </h3>

        <div className="grid grid-cols-2 gap-2 mb-3">
          {roadmap.b_point.junior_salary_uzs && (
            <div className="p-3 bg-[var(--tg-bg)] rounded-lg text-center">
              <p className="text-[10px] text-[var(--tg-hint)] mb-1">
                Junior (UZ)
              </p>
              <p className="font-semibold text-sm">{roadmap.b_point.junior_salary_uzs}</p>
            </div>
          )}
          {roadmap.b_point.remote_salary_usd && (
            <div className="p-3 bg-[var(--tg-bg)] rounded-lg text-center">
              <p className="text-[10px] text-[var(--tg-hint)] mb-1">
                Remote (USD)
              </p>
              <p className="font-semibold text-sm">{roadmap.b_point.remote_salary_usd}</p>
            </div>
          )}
        </div>

        {roadmap.b_point.outcomes && (
          <ul className="space-y-1 text-xs">
            {roadmap.b_point.outcomes.map((o, i) => (
              <li key={i} className="flex gap-2">
                <Check className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                <span>{o}</span>
              </li>
            ))}
          </ul>
        )}

        {roadmap.b_point.next_step && (
          <p className="mt-3 text-xs text-[var(--tg-hint)] italic">
            Keyingi qadam: {roadmap.b_point.next_step}
          </p>
        )}
      </div>

      {/* FIRST 3 ACTIONS */}
      {roadmap.first_3_actions.length > 0 && (
        <div className="card border border-amber-500/30">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <span className="text-amber-400">&#128640;</span>
            Birinchi 3 qadam — bugun boshlang
          </h3>
          <ol className="space-y-2">
            {roadmap.first_3_actions.map((a, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 text-xs flex items-center justify-center shrink-0 font-semibold">
                  {i + 1}
                </span>
                <span>{a}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* CALENDAR */}
      {roadmap.calendar_30d.length > 0 && (
        <div className="card">
          <button
            onClick={() => setShowCalendar(!showCalendar)}
            className="w-full flex items-center gap-2 justify-between text-left"
          >
            <h3 className="font-semibold flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-400" />
              30 kunlik kalendar
            </h3>
            {showCalendar ? (
              <ChevronDown className="w-4 h-4 text-[var(--tg-hint)]" />
            ) : (
              <ChevronRight className="w-4 h-4 text-[var(--tg-hint)]" />
            )}
          </button>

          {showCalendar && (
            <div className="mt-3 space-y-3">
              {roadmap.calendar_30d.map((w, i) => (
                <div key={i} className="border-l-2 border-indigo-400/40 pl-3">
                  <p className="text-xs font-semibold mb-2">
                    {w.w}-hafta: <span className="text-[var(--tg-hint)] font-normal">{w.theme}</span>
                  </p>
                  <div className="space-y-1">
                    {w.days.map((d, j) => (
                      <p key={j} className="text-xs text-[var(--tg-hint)]">{d}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MILESTONES */}
      {roadmap.milestones.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-emerald-400" />
            Muhim nuqtalar
          </h3>
          <div className="space-y-2">
            {roadmap.milestones.map((m, i) => (
              <div key={i} className="flex items-center gap-3 text-xs">
                <span className="w-14 text-[var(--tg-hint)] text-right">
                  {m.week}-hafta
                </span>
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>{m.milestone}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MENTOR PATH */}
      {roadmap.mentor_path.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-purple-400" />
            Ustoz-shogird va jamoa
          </h3>
          <ul className="space-y-1 text-xs">
            {roadmap.mentor_path.map((m, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-purple-400">&bull;</span>
                <span>{m}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* RESOURCES */}
      {roadmap.resources.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-400" />
            Resurslar
          </h3>
          <ul className="space-y-2">
            {roadmap.resources.map((r, i) => (
              <li key={i}>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-[var(--tg-link)] underline"
                >
                  {r.name}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Section({
  title, icon: Icon, color, children,
}: {
  title: string;
  icon: any;
  color: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        <Icon className={`w-3 h-3 ${color}`} />
        <p className="text-xs font-semibold">{title}</p>
      </div>
      {children}
    </div>
  );
}
'''
(FRONTEND_DIR / "RoadmapView.tsx").write_text(roadmap_view, encoding="utf-8")
print("[OK] components/RoadmapView.tsx")

print()
print("=" * 60)
print("Part C — TAYYOR!")
print("=" * 60)
print()
print("Keyingi qadam: report/page.tsx ni yangilash")