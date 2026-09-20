import axios from "axios";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

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

export async function submitStage1(answers: Record<string, any>) {
  const r = await api.post("/diagnostic/stage1", {
    init_data: getInitData(),
    answers,
  });
  return r.data;
}

export async function submitStage2(
  stage1_result_id: number,
  answers: Record<string, any>
) {
  const r = await api.post("/diagnostic/stage2", {
    init_data: getInitData(),
    answers,
    stage1_result_id,
  });
  return r.data;
}

export async function fetchReport(id: number) {
  const r = await api.get(`/diagnostic/report/${id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function createPayment(
  stage1_result_id: number,
  provider: string
) {
  const r = await api.post("/payments/create", {
    init_data: getInitData(),
    stage1_result_id,
    provider,
  });
  return r.data;
}

export async function createStarsInvoice(stage1_result_id: number) {
  const r = await api.post("/payments/stars/invoice", {
    init_data: getInitData(),
    stage1_result_id,
    provider: "stars",
  });
  return r.data;
}

export async function checkPaid(stage1_result_id: number) {
  const r = await api.get(`/payments/check/${stage1_result_id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function devUnlock(stage1_result_id: number) {
  const r = await api.post("/diagnostic/dev-unlock", {
    init_data: getInitData(),
    stage1_result_id,
  });
  return r.data;
}