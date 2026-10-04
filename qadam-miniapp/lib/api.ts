import axios from "axios";

const BACKEND =
  process.env.BACKEND_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BACKEND });

export function getInitData(): string {
  if (typeof window === "undefined") return "";
  const tg = (window as any).Telegram?.WebApp;
  return tg?.initData || "";
}

export async function fetchQuestions() {
  const r = await api.get("/diagnostic/questions");
  return r.data;
}


export async function fetchReport(id: number) {
  const r = await api.get(`/diagnostic/report/${id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}


export async function completeReport(report_id: number) {
  const r = await api.post(`/diagnostic/report/${report_id}/complete`, {
    init_data: getInitData(),
  });
  return r.data;
}


export async function requestPdf(report_id: number, theme: string = "light") {
  const r = await api.post(`/diagnostic/report/${report_id}/pdf`, {
    init_data: getInitData(),
    theme,
  });
  return r.data;
}


export async function submitFeedback(
  report_id: number,
  rating: number,
  comment: string = ""
) {
  const r = await api.post("/admin/feedback", {
    init_data: getInitData(),
    report_id,
    rating,
    comment,
  });
  return r.data;
}

export async function getAdminOverview() {
  const r = await api.get("/admin/overview", {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function getAdminDaily(days: number = 30) {
  const r = await api.get("/admin/daily", {
    params: { init_data: getInitData(), days },
  });
  return r.data;
}

export async function getAdminTopCareers(limit: number = 15) {
  const r = await api.get("/admin/top-careers", {
    params: { init_data: getInitData(), limit },
  });
  return r.data;
}

export async function getAdminFeedbacks(limit: number = 50) {
  const r = await api.get("/admin/feedbacks", {
    params: { init_data: getInitData(), limit },
  });
  return r.data;
}


export async function getCardInfo() {
  const r = await api.get("/payments/manual/card-info");
  return r.data;
}


// ═══════════════════════════════════════════════════════════
// DISCOVERY v1 — Free bosqich
// ═══════════════════════════════════════════════════════════

export async function startDiscovery() {
  const r = await api.post("/api/v1/discovery", {
    init_data: getInitData(),
  });
  return r.data;
}

export async function getDiscoverySession(session_id: number) {
  const r = await api.get(`/api/v1/discovery/${session_id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function submitDiscoveryAnswer(
  session_id: number,
  question_id: string,
  answer_id: string,
  answer_value: number
) {
  const r = await api.post(`/api/v1/discovery/${session_id}/answers`, {
    init_data: getInitData(),
    question_id,
    answer_id,
    answer_value,
  });
  return r.data;
}

export async function completeDiscovery(session_id: number) {
  const r = await api.post(`/api/v1/discovery/${session_id}/complete`, {
    init_data: getInitData(),
  });
  return r.data;
}

// ═══════════════════════════════════════════════════════════
// PROFILE v1
// ═══════════════════════════════════════════════════════════

export async function saveProfile(data: {
  age?: number;
  location?: string;
  current_status?: string;
  education?: string;
}) {
  const r = await api.post("/api/v1/profile", {
    init_data: getInitData(),
    ...data,
  });
  return r.data;
}

// ═══════════════════════════════════════════════════════════
// ENTITLEMENTS v1
// ═══════════════════════════════════════════════════════════

export async function getMyEntitlements() {
  const r = await api.get("/api/v1/entitlements/me", {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function checkEntitlement(key: string) {
  const r = await api.get("/api/v1/entitlements/check", {
    params: { init_data: getInitData(), entitlement_key: key },
  });
  return r.data;
}


/** v1 flow: Action Document (PDF) for a completed deep diagnostic, sent via the bot. */
export async function requestDeepPdf(sessionId: number) {
  const r = await api.post(`/api/v1/deep-diagnostic/${sessionId}/pdf`, {
    init_data: getInitData(),
  });
  return r.data as { ok: boolean; sent_to_telegram: boolean };
}


// ═══════════════════════════════════════════════════════════
// AGE GATE + CONSENT (18+, PM 2026-10-04)
// ═══════════════════════════════════════════════════════════

export type GateStatus = { status: "required" | "ok"; age_warning?: boolean; warning_ack?: boolean };

export async function getGateStatus(): Promise<GateStatus> {
  const r = await api.get("/api/v1/profile/gate", { params: { init_data: getInitData() } });
  return r.data;
}

export async function submitGate(consent: boolean, age: number) {
  const r = await api.post("/api/v1/profile/gate", { init_data: getInitData(), consent, age });
  return r.data as { status: "ok" | "under_age"; age_warning?: boolean };
}

/** 35+ user chose "Ha, davom etaman" (stored, so "Keyinroq" asks again next time). */
export async function ackAgeWarning() {
  const r = await api.post("/api/v1/profile/gate/ack-warning", { init_data: getInitData() });
  return r.data as GateStatus;
}

export function isGateRequired(e: any): boolean {
  const d = e?.response?.data?.detail;
  return e?.response?.status === 403 && d && typeof d === "object" && d.code === "age_gate_required";
}
