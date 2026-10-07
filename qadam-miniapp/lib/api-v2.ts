/** Diagnostic v2 (9×25 catalog) — draft API client. Used only by the /v2 route. */
import { api, getInitData } from "@/lib/api";

export type Option = { id: string; label: string };
export type Question = { id: string; text: string; options: Option[]; kind?: string };
export type Task = Question & { title: string };

export type DiscoveryResult = {
  result_id: number;
  status: "clear" | "two" | "unclear";
  catalogs: { id: string; uz: string; careers: string[] }[];
  answered: number;
  unmeasured: number;
  conditions: Record<string, { question: string; answer: string }>;
};

export type DeepPayload = {
  version: string;
  catalogs: { id: string; uz: string }[];
  a_part: Question[];
  style: Question[];
  readiness: Question[];
  tasks: Task[];
  lesson: { text: string; questions: Question[] };
  ease: { text: string; options: Option[] };
};

export type DeepResult = {
  result_id: number;
  status: "clear" | "two" | "unclear";
  catalogs: { id: string; uz: string }[];
  careers: { id: string; uz: string; catalog: string; has_roadmap: boolean }[];
  evidence: {
    level: "first_evidence" | "not_enough";
    statements: string[];
    tasks: { id: string; title: string; state: "done" | "not_yet" | "unmeasured"; ease_label: string | null }[];
  };
  style: { question: string; answer: string }[];
  readiness: { question: string; answer: string }[];
  unmeasured: number;
  snapshot_note: string;
};

export type CatalogInfo = { id: string; uz: string };

export async function v2DiscoveryQuestions() {
  const r = await api.post("/api/v2/diagnostic/discovery/questions", { init_data: getInitData() });
  return r.data as { version: string; questions: Question[] };
}

export async function v2DiscoverySubmit(answers: Record<string, string>, meta: object) {
  const r = await api.post("/api/v2/diagnostic/discovery/submit", { init_data: getInitData(), answers, meta });
  return r.data as DiscoveryResult;
}

export async function v2DeepQuestions(catalogs: string[]) {
  const r = await api.post("/api/v2/diagnostic/deep/questions", { init_data: getInitData(), catalogs });
  return r.data as DeepPayload;
}

export async function v2DeepSubmit(
  catalogs: string[], answers: Record<string, string>, ease: Record<string, string>, meta: object,
) {
  const r = await api.post("/api/v2/diagnostic/deep/submit", { init_data: getInitData(), catalogs, answers, ease, meta });
  return r.data as DeepResult;
}

export async function v2Roadmap(careerId: string) {
  const r = await api.get(`/api/v2/diagnostic/roadmap/${careerId}`, { params: { init_data: getInitData() } });
  return r.data;
}

/** The 9 catalogs, for the "choose yourself" option after an unclear discovery (Claude proposal). */
export const CATALOGS: CatalogInfo[] = [
  { id: "software", uz: "Dasturlash" },
  { id: "data_ai", uz: "Ma’lumotlar va sun’iy intellekt" },
  { id: "infra_security", uz: "Tizimlar, tarmoq va xavfsizlik" },
  { id: "design_creative", uz: "Raqamli dizayn" },
  { id: "digital_marketing", uz: "Raqamli marketing" },
  { id: "content_media", uz: "Kontent va media" },
  { id: "product_project", uz: "Mahsulot va loyiha boshqaruvi" },
  { id: "business_sales", uz: "Sotuv va mijozlar bilan ishlash" },
  { id: "finance_office", uz: "Moliya va raqamli ofis" },
];

/** Shuffle answer options; the last option ("Bilmayman …") always stays last. */
export function shuffleKeepLast<T>(items: T[]): T[] {
  const head = items.slice(0, -1);
  for (let i = head.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [head[i], head[j]] = [head[j], head[i]];
  }
  return [...head, items[items.length - 1]];
}
