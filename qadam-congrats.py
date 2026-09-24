# -*- coding: utf-8 -*-
"""QADAM — Congrats modal + bot congrats message."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — /report/{id}/complete endpoint
# ═══════════════════════════════════════════════════════════
DIAG = Path("qadam/backend/api/diagnostic.py")
diag = DIAG.read_text(encoding="utf-8")

# Yangi endpoint qo'shish (agar yo'q bo'lsa)
if "report-complete" not in diag and "/complete" not in diag:
    COMPLETE_ENDPOINT = '''

# ═══════════════════════════════════════════════════════════════════
# REPORT COMPLETE — Foydalanuvchi PDF yuklab olgach xabar yuborish
# ═══════════════════════════════════════════════════════════════════

class ReportCompletePayload(BaseModel):
    init_data: str


@router.post("/report/{report_id}/complete")
async def report_complete(report_id: int, payload: ReportCompletePayload):
    """
    User PDF yuklab olgach chaqiriladi.
    Bot orqali tabrik xabari yuboriladi.
    """
    user = _auth(payload.init_data)

    async with SessionLocal() as s:
        r = await s.get(TestResult, report_id)
        if not r or r.user_id != user["id"]:
            raise HTTPException(404, "Report topilmadi")

        # Top-1 career nomi
        careers = (r.roadmap or {}).get("careers", [])
        top_career = careers[0]["career"]["uz"] if careers else "sizga mos yonalish"

    # Bot orqali xabar yuborish
    try:
        import os
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "dostim"

        text = (
            f"🎉 <b>Tabriklaymiz, {first_name}!</b>\\n\\n"
            f"Siz QADAM diagnostikasidan muvaffaqiyatli otdingiz va "
            f"o'zingizga mos yonalish bo'yicha shaxsiy roadmapni qolga kiritdingiz.\\n\\n"
            f"📌 <b>Sizning asosiy yonalishingiz:</b> {top_career}\\n\\n"
            f"Roadmapni 3 xil dizaynda yuklab olishingiz mumkin. "
            f"Reja boyicha bugun birinchi qadamni boshlang!\\n\\n"
            f"<b>Savollar bo'lsa</b> bemalol murojaat qiling — biz shu yerdamiz.\\n\\n"
            f"<i>Sizning muvaffaqiyatingiz — bizning maqsadimiz.</i>\\n"
            f"— QADAM jamoasi"
        )

        webapp = os.getenv("WEBAPP_URL", "")

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Hisobotni qayta ochish",
                web_app=WebAppInfo(url=f"{webapp}/report/{report_id}"),
            )],
            [InlineKeyboardButton(
                text="🚀 Yangi diagnostika",
                web_app=WebAppInfo(url=f"{webapp}/stage1"),
            )],
            [InlineKeyboardButton(
                text="💬 Yordam",
                url="https://t.me/qadam_support",
            )],
        ])

        await bot.send_message(user["id"], text, reply_markup=kb)

        # Bot sessionni yopish
        await bot.session.close()

    except Exception as e:
        log.error(f"Bot xabar yuborishda xato: {e}")

    return {"ok": True, "report_id": report_id}
'''
    diag = diag.rstrip() + COMPLETE_ENDPOINT
    DIAG.write_text(diag, encoding="utf-8")
    print("[OK] backend/api/diagnostic.py — /complete endpoint qo'shildi")
else:
    print("[SKIP] backend/api/diagnostic.py — allaqachon bor")


# ═══════════════════════════════════════════════════════════
# 2. api.ts — completeReport funksiyasi
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

if "completeReport" not in api:
    api += '''

export async function completeReport(report_id: number) {
  const r = await api.post(`/diagnostic/report/${report_id}/complete`, {
    init_data: getInitData(),
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] lib/api.ts — completeReport")
else:
    print("[SKIP] lib/api.ts — completeReport allaqachon bor")


# ═══════════════════════════════════════════════════════════
# 3. PdfDownloader.tsx — toza qayta yozish (conrats modal)
# ═══════════════════════════════════════════════════════════
PDF_COMP = Path("qadam-miniapp/components/PdfDownloader.tsx")

PDF_COMP.write_text(r'''"use client";

import { useState, useEffect, useRef } from "react";
import { Download, X, Moon, Sun, Flower2, Palette, CheckCircle2, PartyPopper, RefreshCw, Send } from "lucide-react";
import { completeReport } from "@/lib/api";

type Theme = "dark" | "light" | "pastel";

const THEMES: { id: Theme; label: string; desc: string; icon: any; color: string; bg: string }[] = [
  { id: "dark", label: "Tungi", desc: "Zamonaviy tungi dizayn", icon: Moon, color: "text-indigo-300", bg: "bg-slate-800" },
  { id: "light", label: "Kunduzgi", desc: "Ananaviy oq dizayn", icon: Sun, color: "text-amber-500", bg: "bg-amber-50" },
  { id: "pastel", label: "Pastel", desc: "Yumshoq rangli dizayn", icon: Flower2, color: "text-pink-400", bg: "bg-pink-50" },
];

export function PdfDownloader({ reportId }: { reportId: number }) {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState<Theme>("dark");
  const [applied, setApplied] = useState<Theme>("dark");
  const [showCongrats, setShowCongrats] = useState(false);
  const [sending, setSending] = useState(false);
  const [inTelegram, setInTelegram] = useState(false);
  const printDetected = useRef(false);

  useEffect(() => {
    document.body.setAttribute("data-theme", "dark");
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData && tg.initData.length > 10) setInTelegram(true);
  }, []);

  // Print dialog yopilganini aniqlash
  useEffect(() => {
    const onAfterPrint = () => {
      if (printDetected.current) return;
      printDetected.current = true;
      setTimeout(() => {
        setShowCongrats(true);
      }, 500);
    };
    window.addEventListener("afterprint", onAfterPrint);
    return () => window.removeEventListener("afterprint", onAfterPrint);
  }, []);

  const applyTheme = (t: Theme) => {
    setTheme(t);
    setApplied(t);
    document.body.setAttribute("data-theme", t);
  };

  const handleDownload = () => {
    // Barcha accordion'larni ochish
    document
      .querySelectorAll<HTMLElement>("[data-accordion-content], [data-calendar-body]")
      .forEach((el) => {
        el.style.maxHeight = "none";
        el.style.marginTop = "8pt";
      });
    document.querySelectorAll<HTMLElement>("*").forEach((el) => {
      if (el.style.opacity === "0") el.style.opacity = "1";
    });

    // Print dialog ochish
    setTimeout(() => window.print(), 100);
  };

  const handleBackToBot = async () => {
    setSending(true);
    try {
      // Backend'ga xabar yuborish — bot tabrik xabarini jo'natadi
      await completeReport(reportId);
    } catch (e) {
      console.log("Complete xatosi:", e);
    }

    // Mini App'ni yopish
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.close && inTelegram) {
      tg.close();
    } else {
      window.close();
    }
  };

  const handleRedownload = () => {
    setShowCongrats(false);
    printDetected.current = false;
    setTimeout(() => handleDownload(), 300);
  };

  return (
    <>
      {/* Trigger — 2 ta tugma */}
      <div className="flex flex-col gap-2 no-print">
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-[var(--tg-hint)]/25 text-sm font-medium hover:border-[var(--tg-hint)]/40 transition"
        >
          <Palette className="w-4 h-4" />
          Dizaynni o'zgartirish
        </button>
        <button
          onClick={handleDownload}
          className="btn-primary flex items-center justify-center gap-2"
        >
          <Download className="w-4 h-4" />
          PDF sifatida yuklab olish
        </button>
      </div>

      {/* Theme modal */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm no-print">
          <div className="w-full max-w-sm rounded-2xl bg-[var(--tg-secondary-bg)] border border-[var(--tg-hint)]/20 overflow-hidden">
            <div className="p-4 border-b border-[var(--tg-hint)]/15 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">Dizaynni tanlang</h3>
                <p className="text-[10px] text-[var(--tg-hint)] mt-0.5">
                  Tanlanganda sahifa darhol ozgaradi
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="w-8 h-8 rounded-full hover:bg-[var(--tg-bg)] flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 space-y-2">
              {THEMES.map((t) => {
                const Icon = t.icon;
                const active = applied === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => applyTheme(t.id)}
                    className={`w-full p-3 rounded-xl border-2 transition flex items-center gap-3 ${
                      active
                        ? "border-indigo-500 bg-indigo-500/10"
                        : "border-[var(--tg-hint)]/20"
                    }`}
                  >
                    <div className={`w-11 h-11 rounded-lg ${t.bg} flex items-center justify-center shrink-0`}>
                      <Icon className={`w-5 h-5 ${t.color}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="font-semibold text-sm">{t.label}</p>
                      <p className="text-[11px] text-[var(--tg-hint)]">{t.desc}</p>
                    </div>
                    {active && (
                      <div className="w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center">
                        <div className="w-2 h-2 rounded-full bg-white" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>

            <div className="p-4 border-t border-[var(--tg-hint)]/15">
              <button
                onClick={() => setOpen(false)}
                className="w-full py-3 rounded-xl bg-indigo-500 text-white font-medium text-sm"
              >
                Tayyor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════ CONGRATS MODAL ═══════════════ */}
      {showCongrats && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm no-print">
          <div className="w-full max-w-sm rounded-3xl bg-gradient-to-br from-[var(--tg-secondary-bg)] to-[var(--tg-bg)] border border-emerald-500/30 overflow-hidden">
            {/* Header with confetti-like */}
            <div className="p-6 text-center relative">
              <div className="absolute top-2 left-4 text-2xl">🎉</div>
              <div className="absolute top-4 right-6 text-xl">✨</div>
              <div className="absolute bottom-2 left-8 text-lg">🎊</div>

              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-emerald-500/30">
                <PartyPopper className="w-10 h-10 text-white" />
              </div>

              <h2 className="text-xl font-bold mb-2 gradient-text">
                Tabriklaymiz!
              </h2>
              <p className="text-sm text-[var(--tg-hint)] mb-1">
                PDF muvaffaqiyatli yuklab olindi
              </p>
            </div>

            {/* Body */}
            <div className="px-6 pb-4 space-y-3">
              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 border border-[var(--tg-hint)]/15">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs">
                    <p className="font-semibold mb-1">Nima qildingiz:</p>
                    <p className="text-[var(--tg-hint)]">
                      QADAM diagnostikasidan otdingiz va o'zingizga mos yo'nalish
                      bo'yicha shaxsiy roadmapni oldingiz.
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-[var(--tg-bg)]/60 border border-amber-500/20">
                <div className="flex items-start gap-2">
                  <span className="text-amber-400 text-sm">⚡</span>
                  <div className="text-xs">
                    <p className="font-semibold mb-1">Keyingi qadam:</p>
                    <p className="text-[var(--tg-hint)]">
                      Roadmapdagi <b>birinchi 3 qadamni</b> bugun boshlang.
                      Kichik harakat katta natija beradi.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-4 pt-2 space-y-2">
              <button
                onClick={handleBackToBot}
                disabled={sending}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-semibold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/30 disabled:opacity-60"
              >
                {sending ? (
                  <>Yuklanmoqda...</>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Botga qaytish
                  </>
                )}
              </button>

              <button
                onClick={handleRedownload}
                disabled={sending}
                className="w-full py-3 rounded-2xl border border-[var(--tg-hint)]/25 text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <RefreshCw className="w-4 h-4" />
                Boshqa dizaynda yuklash
              </button>
            </div>

            <p className="text-[10px] text-[var(--tg-hint)] text-center pb-4 px-6">
              Botga qaytganingizda sizni tabrik xabari kutadi
            </p>
          </div>
        </div>
      )}
    </>
  );
}
''', encoding="utf-8")
print("[OK] components/PdfDownloader.tsx — congrats modal")


print()
print("=" * 60)
print("Congrats + Bot notify — tayyor!")
print("=" * 60)
print()
print("YANGI OQIM:")
print("  1. PDF yuklab olish → Chrome print")
print("  2. Save as PDF → print dialog yopiladi")
print("  3. CONGRATS modal: 'Tabriklaymiz!'")
print("  4. 'Botga qaytish' → backend xabar yuboradi → Mini App yopiladi")
print("  5. Bot'da: 'Tabriklaymiz, [ism]! ...' xabari")
print()
print("Keyingi: git push")