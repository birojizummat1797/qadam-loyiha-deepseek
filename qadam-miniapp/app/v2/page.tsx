"use client";

/**
 * Diagnostic v2 (9×25 catalog) — DRAFT for founder review and internal testing.
 * Not linked from the main flow; open /v2 directly in the Mini App.
 *
 * Steps: 18+ gate → intro → short test (13) → short result → deep part A (11),
 * B (5), C (3) → practical tasks (4, each with an ease question) → mini lesson +
 * 2 questions → result. Answer order is shuffled; "Bilmayman" always stays last.
 */
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Loader2 } from "lucide-react";
import AgeGate from "@/components/AgeGate";
import { getGateStatus, isGateRequired } from "@/lib/api";
import {
  CATALOGS, DeepPayload, DeepResult, DiscoveryResult, Option, Question,
  shuffleKeepLast, v2DeepQuestions, v2DeepSubmit, v2DiscoveryQuestions, v2DiscoverySubmit,
} from "@/lib/api-v2";

const PRINCIPLE = "Signallarni Qadam o’qiydi. Qarorni siz qilasiz.";

type Item =
  | { type: "question"; q: Question; section: string }
  | { type: "lesson"; text: string }
  | { type: "ease"; taskId: string; text: string; options: Option[] };

type Phase =
  | "loading" | "gate" | "intro" | "discovery" | "discovery_result"
  | "deep" | "deep_result" | "error";

export default function V2Page() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState("");
  const [gateStep, setGateStep] = useState<"consent" | "over_35">("consent");

  const [discResult, setDiscResult] = useState<DiscoveryResult | null>(null);
  const [deepCatalogs, setDeepCatalogs] = useState<string[]>([]);
  const [deepResult, setDeepResult] = useState<DeepResult | null>(null);

  const [items, setItems] = useState<Item[]>([]);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [ease, setEase] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const timings = useRef<Record<string, number>>({});
  const shownAt = useRef<number>(Date.now());
  const startedAt = useRef<number>(Date.now());

  const fail = (e: any) => {
    if (isGateRequired(e)) { setPhase("gate"); return; }
    setError(e?.response?.data?.detail ? JSON.stringify(e.response.data.detail) : e?.message || "Xatolik");
    setPhase("error");
  };

  useEffect(() => {
    getGateStatus()
      .then((g) => {
        if (g.status === "ok" && g.age_warning && !g.warning_ack) { setGateStep("over_35"); setPhase("gate"); }
        else if (g.status === "ok") setPhase("intro");
        else setPhase("gate");
      })
      .catch(() => setPhase("intro"));
  }, []);

  const startDiscovery = () => {
    setPhase("loading");
    v2DiscoveryQuestions()
      .then((r) => {
        setItems(discoveryItems(r.questions)); setAnswers({}); setIndex(0);
        timings.current = {}; startedAt.current = shownAt.current = Date.now();
        setPhase("discovery");
      })
      .catch(fail);
  };

  const startDeep = (catalogs: string[]) => {
    setPhase("loading");
    v2DeepQuestions(catalogs)
      .then((r) => {
        setItems(deepItems(r)); setDeepCatalogs(catalogs); setAnswers({}); setEase({}); setIndex(0);
        timings.current = {}; startedAt.current = shownAt.current = Date.now();
        setPhase("deep");
      })
      .catch(fail);
  };

  const item = items[index];
  const selected = item
    ? item.type === "question" ? answers[item.q.id] : item.type === "ease" ? ease[item.taskId] : "lesson"
    : undefined;

  const choose = (id: string) => {
    if (!item) return;
    if (item.type === "question") setAnswers((a) => ({ ...a, [item.q.id]: id }));
    if (item.type === "ease") setEase((e) => ({ ...e, [item.taskId]: id }));
  };

  const next = async () => {
    if (!item || !selected) return;
    const key = item.type === "question" ? item.q.id : item.type === "ease" ? `ease_${item.taskId}` : "lesson";
    timings.current[key] = Date.now() - shownAt.current;
    shownAt.current = Date.now();
    if (index < items.length - 1) { setIndex(index + 1); return; }

    setSubmitting(true);
    const meta = { duration_ms: Date.now() - startedAt.current, timings_ms: timings.current, client: "miniapp-v2" };
    try {
      if (phase === "discovery") {
        const r = await v2DiscoverySubmit(answers, meta);
        setDiscResult(r); setPhase("discovery_result");
      } else {
        const r = await v2DeepSubmit(deepCatalogs, answers, ease, meta);
        setDeepResult(r); setPhase("deep_result");
      }
    } catch (e) {
      fail(e);
    } finally {
      setSubmitting(false);
    }
  };

  if (phase === "gate") return <AgeGate initialStep={gateStep} onPassed={() => setPhase("intro")} />;
  if (phase === "loading") return <Shell><Spinner /></Shell>;
  if (phase === "error") return <Shell><div className="card-clean"><p className="t-small text-danger">{error}</p></div></Shell>;

  if (phase === "intro") {
    return (
      <Shell>
        <p className="t-caption text-subtle mb-2">Qadam · sinov versiyasi (v2)</p>
        <h1 className="t-title mb-4">O‘zingizga yaqin yo‘nalishni toping</h1>
        <div className="card-clean mb-4">
          <p className="t-body mb-2">Ikki qism:</p>
          <p className="t-small text-muted">1) Qisqa test — 13 savol, 9 ta raqamli yo‘nalishdan sizga yaqinini ko‘rsatadi.</p>
          <p className="t-small text-muted">2) Chuqur tahlil — yo‘nalish ichida kasb, ish uslubi, sharoit, 4 ta amaliy topshiriq va qisqa dars.</p>
        </div>
        <p className="t-small text-muted mb-6">
          To‘g‘ri yoki noto‘g‘ri javob yo‘q (amaliy topshiriqlardan tashqari). Bilmasangiz — “Bilmayman” deng: bu ham halol javob.
        </p>
        <button className="btn btn-primary" onClick={startDiscovery}>Boshlash</button>
      </Shell>
    );
  }

  if (phase === "discovery_result" && discResult) {
    return (
      <Shell>
        <p className="t-caption text-subtle mb-2">Qisqa test natijasi</p>
        {discResult.status === "unclear" ? (
          <>
            <div className="card-clean mb-4">
              <p className="t-heading mb-2">Hozircha javoblaringiz bo‘yicha aniq yo‘nalish ko‘rinmayapti.</p>
              <p className="t-small text-muted">
                Bu yomon natija emas — shunchaki hali yetarli signal yo‘q. Xohlasangiz, o‘zingiz qiziqqan yo‘nalishni tanlab, chuqur tahlilni sinab ko‘ring.
              </p>
            </div>
            <div className="flex flex-col gap-2 mb-6">
              {CATALOGS.map((c) => (
                <button key={c.id} className="option-btn" onClick={() => startDeep([c.id])}><span>{c.uz}</span></button>
              ))}
            </div>
          </>
        ) : (
          <>
            <h2 className="t-title mb-4">
              {discResult.status === "clear" ? "Sizga eng yaqin yo‘nalish:" : "Sizga yaqin ikki yo‘nalish:"}
            </h2>
            {discResult.catalogs.map((c) => (
              <div key={c.id} className="card-clean mb-3">
                <p className="t-heading mb-1">{c.uz}</p>
                <p className="t-small text-muted">{c.careers.join(" · ")}</p>
              </div>
            ))}
            <p className="t-small text-muted mb-6">
              {discResult.status === "two"
                ? "Chuqur tahlil ikkala yo‘nalishdan savol beradi va farqni aniqlashtiradi."
                : "Chuqur tahlil shu yo‘nalish ichida sizga yaqin kasbni aniqlashtiradi."}
            </p>
            <button className="btn btn-primary" onClick={() => startDeep(discResult.catalogs.map((c) => c.id))}>
              Chuqur tahlilni boshlash
            </button>
          </>
        )}
        <p className="t-caption text-subtle mt-6">{PRINCIPLE}</p>
      </Shell>
    );
  }

  if (phase === "deep_result" && deepResult) {
    return (
      <Shell>
        <p className="t-caption text-subtle mb-2">Chuqur tahlil natijasi · {deepResult.catalogs.map((c) => c.uz).join(" + ")}</p>
        {deepResult.status === "unclear" ? (
          <div className="card-clean mb-4">
            <p className="t-heading mb-2">Hozircha bu yo‘nalish ichida aniq kasb ko‘rinmayapti.</p>
            <p className="t-small text-muted">Javoblaringiz bir nechta kasb orasida bo‘lindi. Bu normal — keyinroq amaliy ish bilan aniqlashadi.</p>
          </div>
        ) : (
          <>
            <h2 className="t-title mb-4">{deepResult.status === "clear" ? "Hozirgi javoblaringizga eng yaqin kasb:" : "Hozirgi javoblaringizga yaqin ikki kasb:"}</h2>
            {deepResult.careers.map((c) => (
              <div key={c.id} className="card-clean mb-3">
                <p className="t-heading mb-2">{c.uz}</p>
                {c.has_roadmap
                  ? <button className="btn btn-secondary" onClick={() => router.push(`/v2/roadmap/${c.id}`)}>Yo‘l xaritasini ko‘rish</button>
                  : <p className="t-small text-muted">Yo‘l xaritasi hali tayyor emas.</p>}
              </div>
            ))}
          </>
        )}

        <Section title="Amaliy dalillar">
          {deepResult.evidence.statements.map((s, i) => <p key={i} className="t-small mb-1">• {s}</p>)}
          <div className="mt-2">
            {deepResult.evidence.tasks.map((t) => (
              <p key={t.id} className="t-caption text-subtle">
                {t.title}: {t.state === "done" ? "bajarildi" : t.state === "not_yet" ? "hali emas" : "javob berilmadi"}
                {t.ease_label ? ` · ${t.ease_label}` : ""}
              </p>
            ))}
          </div>
        </Section>

        {deepResult.style.length > 0 && (
          <Section title="Ish uslubingiz (o‘zingiz aytganingiz)">
            {deepResult.style.map((s, i) => <p key={i} className="t-small mb-1">• {s.answer}</p>)}
          </Section>
        )}
        {deepResult.readiness.length > 0 && (
          <Section title="Sharoitingiz">
            {deepResult.readiness.map((s, i) => <p key={i} className="t-small mb-1">• {s.question} — {s.answer}</p>)}
          </Section>
        )}

        <div className="card-clean mb-4"><p className="t-small text-muted">{deepResult.snapshot_note}</p></div>
        <p className="t-caption text-subtle mb-6">{PRINCIPLE}</p>
        <button className="btn btn-secondary" onClick={() => { setDeepResult(null); setDiscResult(null); setPhase("intro"); }}>
          Boshidan
        </button>
      </Shell>
    );
  }

  if (!item) return <Shell><Spinner /></Shell>;

  const progress = ((index + 1) / items.length) * 100;
  return (
    <Shell>
      <div className="pb-4">
        <div className="flex items-center justify-between mb-3">
          <span className="t-caption text-subtle">
            {item.type === "question" ? item.section : item.type === "ease" ? "Topshiriqdan keyin" : "Qisqa dars"}
          </span>
          <span className="t-caption text-subtle">{index + 1} / {items.length}</span>
        </div>
        <div className="h-px bg-[var(--color-border)] relative overflow-hidden">
          <div className="absolute top-0 left-0 h-full bg-primary" style={{ width: `${progress}%` }} />
        </div>
      </div>

      {item.type === "lesson" ? (
        <div className="card-clean mb-6 mt-4">
          <p className="t-caption text-subtle mb-2">30 soniyalik dars — keyin 2 ta savol</p>
          <RichText text={item.text} className="t-body" />
        </div>
      ) : (
        <>
          <RichText text={item.type === "question" ? item.q.text : item.text} className="t-title mb-6 mt-4" />
          <div className="flex flex-col gap-2.5 mb-6">
            {(item.type === "question" ? item.q.options : item.options).map((o) => {
              const isSel = selected === o.id;
              return (
                <button key={o.id} onClick={() => choose(o.id)} className={`option-btn ${isSel ? "selected" : ""}`}>
                  <span className="text-left">{o.label}</span>
                  <span className="option-indicator">{isSel && <Check className="w-3 h-3 text-white" strokeWidth={3} />}</span>
                </button>
              );
            })}
          </div>
        </>
      )}

      <button onClick={next} disabled={!selected || submitting} className="btn btn-primary">
        {submitting ? <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
          : index === items.length - 1 ? "Yakunlash" : item.type === "lesson" ? "Tushundim" : "Keyingisi"}
      </button>
    </Shell>
  );
}

/** One screen per item; options shuffled once when the stage starts. */
function discoveryItems(qs: Question[]): Item[] {
  return qs.map((q) => ({ type: "question", q: { ...q, options: shuffleKeepLast(q.options) }, section: "Qisqa test" }));
}

function deepItems(d: DeepPayload): Item[] {
  const out: Item[] = [];
  d.a_part.forEach((q) => out.push({ type: "question", q: { ...q, options: shuffleKeepLast(q.options) }, section: "Yo‘nalish ichida" }));
  d.style.forEach((q) => out.push({ type: "question", q, section: "Ish uslubi" }));
  d.readiness.forEach((q) => out.push({ type: "question", q, section: "Sharoit" }));
  d.tasks.forEach((t) => {
    out.push({ type: "question", q: { ...t, options: shuffleKeepLast(t.options) }, section: `Amaliy topshiriq: ${t.title}` });
    out.push({ type: "ease", taskId: t.id, text: d.ease.text, options: d.ease.options });
  });
  out.push({ type: "lesson", text: d.lesson.text });
  d.lesson.questions.forEach((q) => out.push({ type: "question", q: { ...q, options: shuffleKeepLast(q.options) }, section: "O‘rgan va bajar" }));
  return out;
}

/** Renders line breaks and **bold** from the spec texts. */
function RichText({ text, className }: { text: string; className?: string }) {
  return (
    <div className={className}>
      {text.split("\n").map((line, i) => (
        <p key={i} className={i ? "mt-1" : ""}>
          {line.split("**").map((part, j) => (j % 2 ? <strong key={j}>{part}</strong> : <span key={j}>{part}</span>))}
        </p>
      ))}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card-clean mb-4">
      <p className="t-heading mb-2">{title}</p>
      {children}
    </div>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom pt-6 pb-8">{children}</div>
    </main>
  );
}

function Spinner() {
  return <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />;
}
