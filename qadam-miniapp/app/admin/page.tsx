"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Users, TrendingUp, Star, MessageSquare, Trophy, BarChart3,
  RefreshCw, AlertCircle,
} from "lucide-react";
import {
  getAdminOverview,
  getAdminDaily,
  getAdminTopCareers,
  getAdminFeedbacks,
} from "@/lib/api";

export default function AdminPage() {
  const [overview, setOverview] = useState<any>(null);
  const [daily, setDaily] = useState<any[]>([]);
  const [topCareers, setTopCareers] = useState<any[]>([]);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ov, dl, tc, fb] = await Promise.all([
        getAdminOverview(),
        getAdminDaily(30),
        getAdminTopCareers(15),
        getAdminFeedbacks(30),
      ]);
      setOverview(ov);
      setDaily(dl.days || []);
      setTopCareers(tc.careers || []);
      setFeedbacks(fb.feedbacks || []);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading && !overview) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!overview) return null;

  const maxDaily = Math.max(
    ...daily.map((d) => Math.max(d.users, d.stage1, d.stage2, 1))
  );

  return (
    <main className="max-w-md lg:max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold">Admin Panel</h1>
          <p className="text-xs text-[var(--tg-hint)]">Qadam.io statistika</p>
        </div>
        <button
          onClick={load}
          className="w-9 h-9 rounded-full bg-[var(--tg-secondary-bg)] flex items-center justify-center"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
        <Kpi
          title="Foydalanuvchilar"
          value={overview.users.total}
          sub={`+${overview.users.new_today} bugun`}
          icon={Users}
          color="text-indigo-400"
        />
        <Kpi
          title="Stage 1"
          value={overview.funnel.stage1}
          sub={`${overview.funnel.stage1_to_stage2_pct}% → Stage 2`}
          icon={TrendingUp}
          color="text-blue-400"
        />
        <Kpi
          title="Stage 2"
          value={overview.funnel.stage2}
          sub={`Funnel`}
          icon={BarChart3}
          color="text-emerald-400"
        />
        <Kpi
          title="Feedback"
          value={overview.feedback.total}
          sub={overview.feedback.avg_rating ? `⭐ ${overview.feedback.avg_rating}` : "—"}
          icon={Star}
          color="text-amber-400"
        />
      </div>

      {/* Daily chart */}
      <div className="rounded-2xl p-4 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15 mb-5">
        <h3 className="font-semibold text-sm mb-3">Kunlik statistika (30 kun)</h3>

        {/* Simple bar chart */}
        <div className="flex items-end gap-[2px] h-32 mb-3">
          {daily.map((d, i) => (
            <div key={i} className="flex-1 flex flex-col justify-end gap-[1px]">
              <div
                className="bg-gradient-to-t from-indigo-500 to-purple-500 rounded-t-sm"
                style={{ height: `${(d.users / maxDaily) * 100}%` }}
                title={`${d.date}: ${d.users} user`}
              />
              <div
                className="bg-blue-500/60 rounded-t-sm"
                style={{ height: `${(d.stage1 / maxDaily) * 100}%` }}
                title={`${d.date}: ${d.stage1} stage1`}
              />
              <div
                className="bg-emerald-500/60 rounded-t-sm"
                style={{ height: `${(d.stage2 / maxDaily) * 100}%` }}
                title={`${d.date}: ${d.stage2} stage2`}
              />
            </div>
          ))}
        </div>

        <div className="flex gap-3 text-[10px] text-[var(--tg-hint)]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm bg-indigo-500" /> Users
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm bg-blue-500" /> Stage 1
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-sm bg-emerald-500" /> Stage 2
          </span>
        </div>
      </div>

      {/* Top careers */}
      <div className="rounded-2xl p-4 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15 mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Trophy className="w-4 h-4 text-amber-400" />
          <h3 className="font-semibold text-sm">Top career'lar</h3>
        </div>

        {topCareers.length === 0 ? (
          <p className="text-xs text-[var(--tg-hint)]">Hozircha malumot yoq</p>
        ) : (
          <div className="space-y-2">
            {topCareers.map((c, i) => (
              <div key={c.career_id} className="flex items-center gap-2 text-xs">
                <span className="w-5 text-[var(--tg-hint)]">#{i + 1}</span>
                <span className="flex-1 truncate">{c.career_uz}</span>
                <span className="text-[var(--tg-hint)]">{c.top1_count}</span>
                <span className="w-14 text-right font-medium">{c.avg_fit}%</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Feedbacks */}
      <div className="rounded-2xl p-4 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15">
        <div className="flex items-center gap-2 mb-3">
          <MessageSquare className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-sm">Oxirgi feedback'lar</h3>
        </div>

        {feedbacks.length === 0 ? (
          <p className="text-xs text-[var(--tg-hint)]">Hozircha feedback yoq</p>
        ) : (
          <div className="space-y-3">
            {feedbacks.map((f) => (
              <div key={f.id} className="p-3 rounded-xl bg-[var(--tg-bg)]">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star
                        key={s}
                        className={`w-3 h-3 ${
                          s <= f.rating
                            ? "text-amber-400 fill-amber-400"
                            : "text-[var(--tg-hint)]/30"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-[10px] text-[var(--tg-hint)]">
                    Report #{f.report_id}
                  </span>
                </div>
                {f.comment && (
                  <p className="text-xs mt-1">{f.comment}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

function Kpi({ title, value, sub, icon: Icon, color }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl p-3 bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/15"
    >
      <div className="flex items-center gap-1.5 mb-1">
        <Icon className={`w-3.5 h-3.5 ${color}`} />
        <p className="text-[10px] text-[var(--tg-hint)]">{title}</p>
      </div>
      <p className="text-xl font-bold">{value}</p>
      <p className="text-[10px] text-[var(--tg-hint)] mt-0.5">{sub}</p>
    </motion.div>
  );
}

function Loader() {
  return (
    <main className="max-w-md mx-auto px-5 py-10 text-center">
      <div className="w-10 h-10 border-4 border-[var(--tg-secondary-bg)] border-t-[var(--tg-button)] rounded-full animate-spin mx-auto" />
      <p className="mt-4 text-sm text-[var(--tg-hint)]">Yuklanmoqda...</p>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="max-w-md mx-auto px-5 py-10">
      <div className="rounded-2xl p-5 bg-red-500/10 border border-red-500/30">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-400 text-sm mb-1">Ruxsat yoq</p>
            <p className="text-xs text-[var(--tg-hint)]">{msg}</p>
          </div>
        </div>
      </div>
    </main>
  );
}
