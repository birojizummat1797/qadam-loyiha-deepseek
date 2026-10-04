/**
 * User-facing levels instead of percentages (PM P0-1, 2026-10-03).
 * Mirrors qadam/backend/engine/levels.py. Fit/readiness numbers are never shown.
 */

export type EvidenceLevel = "enough" | "partial" | "insufficient";

const EVIDENCE_LABELS: Record<EvidenceLevel, string> = {
  enough: "Ma'lumot yetarli",
  partial: "Ma'lumot qisman",
  insufficient: "Ma'lumot yetarli emas",
};

const BARRIER_LABELS: Record<string, string> = {
  device: "Qurilma kerak bo'ladi",
  language: "Ingliz tilini oshirish kerak",
  time: "Ko'proq vaqt kerak bo'ladi",
};

/** Older API responses have no evidence_level; derive it with the same thresholds as the backend. */
export function evidenceLevel(level?: string | null, coverage?: number | null): EvidenceLevel {
  if (level === "enough" || level === "partial" || level === "insufficient") return level;
  if (coverage == null) return "insufficient";
  if (coverage >= 0.75) return "enough";
  if (coverage >= 0.5) return "partial";
  return "insufficient";
}

export function EvidenceBadge({ level, coverage }: { level?: string | null; coverage?: number | null }) {
  return <span className="badge-soft badge-primary">{EVIDENCE_LABELS[evidenceLevel(level, coverage)]}</span>;
}

type Barrier = { type: string };

/** Readiness in words: nothing when the context is unknown, otherwise barriers or “no barrier”. */
export function ContextNote({ readiness, barriers }: { readiness?: number | null; barriers?: Barrier[] }) {
  if (readiness == null) return null;
  if (!barriers || barriers.length === 0) {
    return <p className="t-caption text-success">Hozirgi sharoitingiz boshlash uchun to&apos;siq emas</p>;
  }
  return (
    <div className="flex flex-wrap gap-1.5">
      {barriers.map((b, i) => (
        <span key={i} className="badge-soft badge-warning">
          {BARRIER_LABELS[b.type] ?? b.type}
        </span>
      ))}
    </div>
  );
}
