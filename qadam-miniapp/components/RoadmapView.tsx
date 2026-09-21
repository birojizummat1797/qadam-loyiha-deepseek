"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MapPin, Target, Calendar, ChevronDown, ChevronRight, Info,
  AlertCircle, Check, X, TrendingUp, Clock, BookOpen,
  Zap, DollarSign, GraduationCap, Users, Rocket, Star,
} from "lucide-react";

type Constraint = { problem?: string; type?: string; level?: string; solution: string };
type Stage = {
  n: number; name: string; name_uz: string; weeks: number;
  role: string; daily_hours: string; graduate_by: string;
  constraints: Constraint[]; daily_focus: string[]; signs_right: string[];
  signs_wrong: string[]; graduate_criteria: string[];
  challenges: string[]; skills_gained: string[];
};

type Roadmap = {
  career_id: string; career_uz: string; cluster_uz: string; why_this_path: string;
  version?: string;
  a_point: {
    constraints: Constraint[];
    signal_summary?: { top_5: { key: string; score: number }[]; total_measured: number };
  };
  path: { total_weeks: number; stages: Stage[] };
  b_point: {
    junior_salary_uzs?: string; remote_salary_usd?: string;
    outcomes?: string[]; next_step?: string;
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
  system_design: "Tizim", analytical: "Tahlil", persistence: "Qatiyat",
  math_logic: "Matematika", attention_to_detail: "Detal",
  business_sense: "Biznes", innovation: "Innovatsiya",
};

const STAGE_COLORS = [
  { from: "from-slate-500", to: "to-slate-700", bg: "bg-slate-500/15", text: "text-slate-300", accent: "border-slate-500/40" },
  { from: "from-blue-500", to: "to-cyan-500", bg: "bg-blue-500/15", text: "text-blue-300", accent: "border-blue-500/40" },
  { from: "from-purple-500", to: "to-fuchsia-500", bg: "bg-purple-500/15", text: "text-purple-300", accent: "border-purple-500/40" },
  { from: "from-amber-500", to: "to-orange-500", bg: "bg-amber-500/15", text: "text-amber-300", accent: "border-amber-500/40" },
  { from: "from-emerald-500", to: "to-teal-500", bg: "bg-emerald-500/15", text: "text-emerald-300", accent: "border-emerald-500/40" },
];

export function RoadmapView({ roadmap }: { roadmap: Roadmap }) {
  const [openStage, setOpenStage] = useState<number | null>(0);
  const [showCalendar, setShowCalendar] = useState(false);

  

  if (!roadmap || !roadmap.path || !Array.isArray(roadmap.path.stages)) {
    return (
      <div className="rounded-2xl p-5 bg-gradient-to-br from-slate-500/10 to-slate-700/5 border border-slate-500/20">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-500/20 flex items-center justify-center shrink-0">
            <Info className="w-5 h-5 text-slate-400" />
          </div>
          <div>
            <h4 className="font-semibold text-sm mb-1">
              Bu yonalish uchun batafsil tahlil
            </h4>
            <p className="text-xs text-[var(--tg-hint)] leading-relaxed">
              Sizga eng mos yonalishlar uchun toliq roadmap tayyorlangan.
              Bu yonalish boyicha malumot tez orada qoshiladi.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* ═══ WHY THIS FITS ═══ */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl p-5 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-pink-500/15 border border-indigo-500/30"
      >
        <div className="flex items-center gap-2 mb-2">
          <Star className="w-4 h-4 text-amber-400" />
          <h3 className="font-semibold text-sm">Nega bu sizga mos</h3>
        </div>
        <p className="text-sm leading-relaxed">{roadmap.why_this_path}</p>
      </motion.div>

      {/* ═══ A NUQTA ═══ */}
      <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
            <MapPin className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Sizning boshlanish</p>
            <h3 className="font-semibold">A NUQTA</h3>
          </div>
        </div>

        {roadmap.a_point?.signal_summary?.top_5 && (
          <div className="mb-4">
            <p className="text-xs text-[var(--tg-hint)] mb-2">Kuchli signallaringiz</p>
            <div className="space-y-2">
              {roadmap.a_point.signal_summary.top_5.map((s, i) => (
                <div key={s.key} className="flex items-center gap-2">
                  <span className="text-xs w-24 capitalize">{SIGNAL_UZ[s.key] ?? s.key}</span>
                  <div className="flex-1 h-2 bg-[var(--tg-hint)]/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                      style={{ width: `${s.score * 100}%` }}
                    />
                  </div>
                  <span className="text-xs w-10 text-right font-medium">
                    {Math.round(s.score * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {roadmap.a_point?.constraints?.length > 0 && (
          <div>
            <p className="text-xs text-[var(--tg-hint)] mb-2">Hal qilish kerak</p>
            <div className="space-y-2">
              {roadmap.a_point.constraints.map((c, i) => (
                <div key={i} className="p-3 bg-[var(--tg-bg)] rounded-xl">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className={`w-3.5 h-3.5 ${c.level === "hard" ? "text-red-400" : "text-amber-400"}`} />
                    <span className="text-xs font-medium capitalize flex-1">{c.problem ?? c.type}</span>
                    <span className={`text-[9px] px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      c.level === "hard" ? "bg-red-400/20 text-red-400" : "bg-amber-400/20 text-amber-400"
                    }`}>
                      {c.level}
                    </span>
                  </div>
                  {c.solution && (
                    <p className="text-xs text-[var(--tg-hint)] pl-6 flex gap-1.5">
                      <Check className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                      <span>{c.solution}</span>
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ═══ YO'L — TIMELINE ═══ */}
      <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Bosib o'tadigan</p>
              <h3 className="font-semibold">YO'L</h3>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold gradient-text">{roadmap.path.total_weeks}</p>
            <p className="text-[10px] text-[var(--tg-hint)]">hafta</p>
          </div>
        </div>

        <div className="relative">
          <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-gradient-to-b from-slate-500 via-blue-500 via-purple-500 via-amber-500 to-emerald-500 opacity-40" />

          <div className="space-y-3">
            {roadmap.path.stages.map((s, i) => {
              const isOpen = openStage === i || openStage === -1;
              const color = STAGE_COLORS[i % STAGE_COLORS.length];
              return (
                <div key={i} className="relative">
                  <div className={`absolute left-0 top-3 w-8 h-8 rounded-full bg-gradient-to-br ${color.from} ${color.to} flex items-center justify-center text-white text-xs font-bold shadow-lg z-10`}>
                    {s.n}
                  </div>

                  <div className="ml-12">
                    <button
                      onClick={() => setOpenStage(isOpen ? null : i)}
                      className={`w-full text-left rounded-xl p-3 border ${color.accent} ${color.bg} transition-all`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <div className={`w-6 h-6 rounded-lg bg-gradient-to-br ${color.from} ${color.to} flex items-center justify-center shrink-0`}>
                          {isOpen ? (
                            <ChevronDown data-chevron className="w-3.5 h-3.5 text-white" />
                          ) : (
                            <ChevronRight data-chevron className="w-3.5 h-3.5 text-white" />
                          )}
                        </div>
                        <span className={`text-[9px] px-2 py-0.5 rounded-full bg-white/10 ${color.text} uppercase tracking-wider font-medium`}>
                          Stage {s.n}
                        </span>
                      </div>
                      <p className="font-semibold text-sm mb-1">{s.name_uz}</p>
                      <div className="flex items-center gap-3 text-[10px] text-[var(--tg-hint)]">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />{s.weeks} hafta
                        </span>
                        <span className="flex items-center gap-1">
                          <Zap className="w-3 h-3" />{s.daily_hours}
                        </span>
                      </div>
                    </button>

                    <div
                      data-accordion-content
                      className={`overflow-hidden transition-all duration-300 ${
                        isOpen ? "max-h-[10000px] mt-2" : "max-h-0"
                      }`}
                    >
                      <div className="p-3 bg-[var(--tg-bg)] rounded-xl space-y-3 text-xs">
                        <div className="grid grid-cols-2 gap-2">
                          <div className="p-2 rounded-lg bg-[var(--tg-secondary-bg)]">
                            <p className="text-[10px] text-[var(--tg-hint)] mb-0.5">Rolingiz</p>
                            <p className="font-medium">{s.role}</p>
                          </div>
                          <div className="p-2 rounded-lg bg-[var(--tg-secondary-bg)]">
                            <p className="text-[10px] text-[var(--tg-hint)] mb-0.5">Maqsad</p>
                            <p className="font-medium">{s.graduate_by}</p>
                          </div>
                        </div>

                        {s.daily_focus.length > 0 && (
                          <SubSection title="Har kun nima qilish" icon={Clock} color="text-blue-400">
                            <ul className="space-y-1">
                              {s.daily_focus.map((d, j) => (
                                <li key={j} className="flex gap-1.5 text-xs">
                                  <span className="text-blue-400 shrink-0">&bull;</span>
                                  <span>{d}</span>
                                </li>
                              ))}
                            </ul>
                          </SubSection>
                        )}

                        {s.constraints.length > 0 && (
                          <SubSection title="To'siq va yechim" icon={AlertCircle} color="text-amber-400">
                            <div className="space-y-1.5">
                              {s.constraints.map((c, j) => (
                                <div key={j} className="p-2 rounded-lg bg-[var(--tg-secondary-bg)]">
                                  <p className="flex gap-1.5 mb-1">
                                    <X className="w-3 h-3 text-red-400 shrink-0 mt-0.5" />
                                    <span>{c.problem}</span>
                                  </p>
                                  <p className="flex gap-1.5 text-[var(--tg-hint)] pl-4">
                                    <Check className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>{c.solution}</span>
                                  </p>
                                </div>
                              ))}
                            </div>
                          </SubSection>
                        )}

                        {s.signs_right.length > 0 && (
                          <SubSection title="To'g'ri ketayapsizmi" icon={Check} color="text-emerald-400">
                            <ul className="space-y-1">
                              {s.signs_right.map((x, j) => (
                                <li key={j} className="flex gap-1.5">
                                  <Check className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                                  <span>{x}</span>
                                </li>
                              ))}
                            </ul>
                          </SubSection>
                        )}

                        {s.signs_wrong.length > 0 && (
                          <SubSection title="Yaxshilash kerak" icon={X} color="text-red-400">
                            <ul className="space-y-1">
                              {s.signs_wrong.map((x, j) => (
                                <li key={j} className="flex gap-1.5">
                                  <X className="w-3 h-3 text-red-400 shrink-0 mt-0.5" />
                                  <span>{x}</span>
                                </li>
                              ))}
                            </ul>
                          </SubSection>
                        )}

                        {s.graduate_criteria.length > 0 && (
                          <SubSection title="Keyingi stage'ga shart" icon={GraduationCap} color="text-indigo-400">
                            <ul className="space-y-1">
                              {s.graduate_criteria.map((x, j) => (
                                <li key={j} className="flex gap-1.5">
                                  <span className="text-indigo-400 shrink-0">&rarr;</span>
                                  <span>{x}</span>
                                </li>
                              ))}
                            </ul>
                          </SubSection>
                        )}

                        {s.skills_gained.length > 0 && (
                          <div className="flex flex-wrap gap-1 pt-1">
                            {s.skills_gained.map((sk, j) => (
                              <span key={j} className={`text-[10px] px-2 py-0.5 rounded-full ${color.bg} ${color.text}`}>
                                {sk}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ═══ B NUQTA ═══ */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        className="rounded-2xl p-5 bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-cyan-500/20 border border-emerald-500/40 relative overflow-hidden"
      >
        <div className="absolute -top-8 -right-8 w-32 h-32 bg-emerald-500/20 blur-3xl rounded-full" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-emerald-500/30 flex items-center justify-center">
              <Target className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-emerald-400/80">Erishishingiz mumkin</p>
              <h3 className="font-semibold">B NUQTA</h3>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            {roadmap.b_point.junior_salary_uzs && (
              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 backdrop-blur-sm">
                <div className="flex items-center gap-1.5 mb-1">
                  <DollarSign className="w-3 h-3 text-emerald-400" />
                  <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Junior UZ</p>
                </div>
                <p className="text-xl font-bold">{roadmap.b_point.junior_salary_uzs}</p>
              </div>
            )}
            {roadmap.b_point.remote_salary_usd && (
              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 backdrop-blur-sm">
                <div className="flex items-center gap-1.5 mb-1">
                  <Rocket className="w-3 h-3 text-cyan-400" />
                  <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Remote</p>
                </div>
                <p className="text-xl font-bold">{roadmap.b_point.remote_salary_usd}</p>
              </div>
            )}
          </div>

          {roadmap.b_point.outcomes && (
            <ul className="space-y-1.5">
              {roadmap.b_point.outcomes.map((o, i) => (
                <li key={i} className="flex gap-2 text-xs">
                  <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{o}</span>
                </li>
              ))}
            </ul>
          )}

          {roadmap.b_point.next_step && (
            <div className="mt-3 pt-3 border-t border-emerald-500/20">
              <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)] mb-1">Keyingi qadam</p>
              <p className="text-xs font-medium">{roadmap.b_point.next_step}</p>
            </div>
          )}
        </div>
      </motion.div>

      {/* ═══ FIRST 3 ACTIONS ═══ */}
      {roadmap.first_3_actions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="rounded-2xl p-5 bg-gradient-to-br from-amber-500/15 to-orange-500/10 border border-amber-500/40"
        >
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-amber-500/30 flex items-center justify-center">
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-amber-400/80">Bugun boshlang</p>
              <h3 className="font-semibold">Birinchi 3 qadam</h3>
            </div>
          </div>

          <div className="space-y-2">
            {roadmap.first_3_actions.map((a, i) => (
              <div key={i} className="flex gap-3 p-3 rounded-xl bg-[var(--tg-bg)]/60">
                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                  {i + 1}
                </div>
                <p className="text-sm self-center">{a}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ═══ CALENDAR ═══ */}
      {roadmap.calendar_30d.length > 0 && (
        <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
          <button
            onClick={() => setShowCalendar(!showCalendar)}
            className="w-full flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                <Calendar className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-left">
                <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Reja</p>
                <h3 className="font-semibold">30 kunlik kalendar</h3>
              </div>
            </div>
            {showCalendar ? (
              <ChevronDown data-chevron className="w-4 h-4 text-[var(--tg-hint)]" />
            ) : (
              <ChevronRight data-chevron className="w-4 h-4 text-[var(--tg-hint)]" />
            )}
          </button>

          <div
            data-calendar-body
            className={`overflow-hidden transition-all duration-300 ${
              showCalendar ? "max-h-[10000px] mt-4" : "max-h-0"
            }`}
          >
            <div className="space-y-3">
              {roadmap.calendar_30d.map((w, i) => (
                <div key={i} className="p-3 rounded-xl bg-[var(--tg-bg)]">
                  <p className="text-xs font-semibold mb-2 flex items-center gap-2">
                    <span className="w-6 h-6 rounded-md bg-blue-500/20 text-blue-400 text-[10px] flex items-center justify-center">
                      {w.w}
                    </span>
                    <span>{w.theme}</span>
                  </p>
                  <div className="space-y-1 pl-8">
                    {w.days.map((d, j) => (
                      <p key={j} className="text-[11px] text-[var(--tg-hint)]">{d}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ═══ MILESTONES ═══ */}
      {roadmap.milestones.length > 0 && (
        <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
              <Target className="w-4 h-4 text-purple-400" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-[var(--tg-hint)]">Belgilar</p>
              <h3 className="font-semibold">Muhim nuqtalar</h3>
            </div>
          </div>
          <div className="space-y-2">
            {roadmap.milestones.map((m, i) => (
              <div key={i} className="flex items-center gap-3 text-xs">
                <span className="w-16 text-[var(--tg-hint)] text-right tabular-nums">{m.week}h</span>
                <div className="w-2 h-2 rounded-full bg-gradient-to-br from-purple-400 to-fuchsia-400 shrink-0" />
                <span>{m.milestone}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══ MENTOR ═══ */}
      {roadmap.mentor_path.length > 0 && (
        <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
          <div className="flex items-center gap-2 mb-3">
            <Users className="w-4 h-4 text-purple-400" />
            <h3 className="font-semibold text-sm">Ustoz-shogird va jamoa</h3>
          </div>
          <ul className="space-y-1.5">
            {roadmap.mentor_path.map((m, i) => (
              <li key={i} className="flex gap-2 text-xs">
                <span className="text-purple-400 shrink-0">&bull;</span>
                <span>{m}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ═══ RESOURCES ═══ */}
      {roadmap.resources.length > 0 && (
        <div className="rounded-2xl p-5 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
          <div className="flex items-center gap-2 mb-3">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <h3 className="font-semibold text-sm">Resurslar</h3>
          </div>
          <div className="space-y-2">
            {roadmap.resources.map((r, i) => (
              <a
                key={i}
                href={r.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 p-2.5 rounded-lg bg-[var(--tg-bg)] hover:bg-[var(--tg-bg)]/80 transition text-xs"
              >
                <div className="w-6 h-6 rounded-md bg-blue-500/20 flex items-center justify-center shrink-0">
                  <BookOpen className="w-3 h-3 text-blue-400" />
                </div>
                <span className="flex-1 truncate">{r.name}</span>
                <ChevronRight className="w-3 h-3 text-[var(--tg-hint)] shrink-0" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SubSection({ title, icon: Icon, color, children }: { title: string; icon: any; color: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1.5">
        <Icon className={`w-3 h-3 ${color}`} />
        <p className="text-[10px] uppercase tracking-wider font-medium">{title}</p>
      </div>
      {children}
    </div>
  );
}
