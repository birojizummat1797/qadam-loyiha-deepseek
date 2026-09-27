# -*- coding: utf-8 -*-
"""Manual to'lov tizimi (karta orqali)."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — manual payment endpoint
# ═══════════════════════════════════════════════════════════
PAYMENTS = Path("qadam/backend/api/payments.py")
pay = PAYMENTS.read_text(encoding="utf-8")

if "manual/request" not in pay:
    MANUAL_ENDPOINT = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — karta orqali, admin tasdiqlaydi
# ═══════════════════════════════════════════════════════════════════

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


class ManualRequestPayload(BaseModel):
    init_data: str
    stage1_result_id: int


@router.post("/manual/request")
async def manual_request(payload: ManualRequestPayload):
    """User karta orqali to'lov qilmoqchi — adminga xabar yuborish."""
    user = verify_init_data(payload.init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, payload.stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        # Manual payment yozuvi
        p = Payment(
            user_id=user["id"],
            stage1_result_id=payload.stage1_result_id,
            provider="manual",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    # Adminga bot orqali xabar
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "Nomalum"
        username = user.get("username") or "-"
        user_id = user["id"]

        text = (
            f"💳 <b>Yangi to'lov so'rovi</b>\\n\\n"
            f"👤 <b>User:</b> {first_name}\\n"
            f"🔗 <b>Username:</b> @{username}\\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\\n"
            f"📊 <b>Stage 1 ID:</b> {payload.stage1_result_id}\\n"
            f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\\n"
            f"🎫 <b>Payment ID:</b> {payment_id}\\n\\n"
            f"<i>Skrinshotni kutish kerak.</i>"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"pay:approve:{payment_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"pay:reject:{payment_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Userga yozish",
                    url=f"tg://user?id={user_id}",
                ),
            ],
        ])

        if ADMIN_CHAT_ID:
            await bot.send_message(ADMIN_CHAT_ID, text, reply_markup=kb)

        await bot.session.close()
    except Exception as e:
        log.error(f"Admin xabar yuborishda xato: {e}")

    return {
        "payment_id": payment_id,
        "status": "pending",
        "card": {
            "number": CARD_NUMBER,
            "holder": CARD_HOLDER,
            "bank": CARD_BANK,
            "amount": PRICE_UZS,
        },
        "admin_username": "@ulugbek_aliboyev",
    }


class ApprovePayload(BaseModel):
    init_data: str
    payment_id: int


@router.post("/manual/approve")
async def manual_approve(payload: ApprovePayload):
    """Admin to'lovni tasdiqlaydi."""
    admin = verify_init_data(payload.init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    ADMIN_IDS = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if admin["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")

    async with SessionLocal() as s:
        p = await s.get(Payment, payload.payment_id)
        if not p:
            raise HTTPException(404, "Payment topilmadi")

        p.status = "paid"
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()

        user_id = p.user_id

    # Userga xabar yuborish
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        webapp = os.getenv("WEBAPP_URL", "")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Chuqur tahlilni boshlash",
                web_app=WebAppInfo(url=f"{webapp}/stage2"),
            )
        ]])

        await bot.send_message(
            user_id,
            "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
            "Endi 18 ta chuqur savolga javob bering va shaxsiy yo'l xaritangizni oling.",
            reply_markup=kb,
        )

        await bot.session.close()
    except Exception as e:
        log.error(f"User xabar yuborishda xato: {e}")

    return {"ok": True, "payment_id": payload.payment_id}


@router.get("/manual/pending")
async def manual_pending(init_data: str = Query(...)):
    """Admin uchun: kutilayotgan to'lovlar."""
    admin = verify_init_data(init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    ADMIN_IDS = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if admin["id"] not in ADMIN_IDS:
        raise HTTPException(403, "Ruxsat yoq")

    async with SessionLocal() as s:
        rows = await s.execute(
            select(Payment)
            .where(Payment.status == "pending", Payment.provider == "manual")
            .order_by(Payment.created_at.desc())
        )
        items = rows.scalars().all()

    return {
        "payments": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "stage1_result_id": p.stage1_result_id,
                "amount_uzs": p.amount_uzs,
                "created_at": p.created_at.isoformat() if p.created_at else "",
            }
            for p in items
        ]
    }
'''
    PAYMENTS.write_text(pay + MANUAL_ENDPOINT, encoding="utf-8")
    print("[OK] backend/api/payments.py — manual endpoint qoshildi")
else:
    print("[SKIP] payments.py — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 2. BOT — callback handler (approve/reject)
# ═══════════════════════════════════════════════════════════
BOT_PAY = Path("qadam/bot/handlers/payment.py")
bot_pay = BOT_PAY.read_text(encoding="utf-8")

if "pay:approve" not in bot_pay:
    bot_pay += '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash
# ═══════════════════════════════════════════════════════════════════

import os as _os
import httpx as _httpx


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    payment_id = int(callback.data.split(":")[2])

    admin_ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if callback.from_user.id not in admin_ids:
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    backend = _os.getenv("BACKEND_URL", "https://qadam-backend-deepseek.onrender.com")
    bot_token = _os.getenv("BOT_TOKEN", "")

    try:
        async with _httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{backend}/payments/manual/approve",
                json={"init_data": f"dev_{callback.from_user.id}", "payment_id": payment_id},
            )
            # Fallback: agar init_data talab qilsa, to'g'ridan-to'g'ri bazaga yozamiz
            if r.status_code != 200:
                # Direct DB update
                from backend.db import SessionLocal
                from backend.models import Payment, TestResult
                async with SessionLocal() as s:
                    p = await s.get(Payment, payment_id)
                    if p:
                        p.status = "paid"
                        s1 = await s.get(TestResult, p.stage1_result_id)
                        if s1:
                            s1.paid = True
                        await s.commit()
                        # Userga xabar
                        webapp = _os.getenv("WEBAPP_URL", "")
                        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
                        kb = InlineKeyboardMarkup(inline_keyboard=[[
                            InlineKeyboardButton(
                                text="🎯 Chuqur tahlilni boshlash",
                                web_app=WebAppInfo(url=f"{webapp}/stage2"),
                            )
                        ]])
                        try:
                            await callback.bot.send_message(
                                p.user_id,
                                "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
                                "Endi 18 ta chuqur savolga javob bering.",
                                reply_markup=kb,
                            )
                        except Exception:
                            pass
    except Exception as e:
        await callback.answer(f"Xato: {str(e)[:50]}", show_alert=True)
        return

    # Xabarni yangilash
    try:
        await callback.message.edit_text(
            callback.message.text + "\\n\\n✅ <b>TASDIQLANDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass

    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    payment_id = int(callback.data.split(":")[2])

    admin_ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if callback.from_user.id not in admin_ids:
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    from backend.db import SessionLocal
    from backend.models import Payment

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if p:
            p.status = "rejected"
            await s.commit()

    try:
        await callback.message.edit_text(
            callback.message.text + "\\n\\n❌ <b>RAD ETILDI</b>",
            reply_markup=None,
        )
    except Exception:
        pass

    await callback.answer("Rad etildi ❌")
'''
    BOT_PAY.write_text(bot_pay, encoding="utf-8")
    print("[OK] bot/handlers/payment.py — approve/reject callback")
else:
    print("[SKIP] bot/handlers/payment.py — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 3. TEASER SAHIFA — Click olib tashlash, manual to'lov
# ═══════════════════════════════════════════════════════════
TEASER = Path("qadam-miniapp/app/teaser/page.tsx")

TEASER.write_text(r'''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Check, Sparkles, CreditCard, Send, X, Copy } from "lucide-react";
import { useStore } from "@/lib/store";
import { api, getInitData } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);

  const [openPay, setOpenPay] = useState(false);
  const [card, setCard] = useState<any>(null);
  const [sending, setSending] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!teaser || !stage1ResultId) {
    return (
      <main className="min-h-screen flex justify-center">
        <div className="w-full max-w-md px-6 pt-10">
          <p className="t-body text-muted mb-6">Natija topilmadi.</p>
          <button
            className="btn btn-primary"
            onClick={() => router.push("/stage1")}
          >
            Qaytadan boshlash
          </button>
        </div>
      </main>
    );
  }

  const openPayment = async () => {
    setSending(true);
    try {
      const r = await api.post("/payments/manual/request", {
        init_data: getInitData(),
        stage1_result_id: stage1ResultId,
      });
      setCard(r.data.card);
      setOpenPay(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setSending(false);
    }
  };

  const copyCard = () => {
    if (card?.number) {
      navigator.clipboard.writeText(card.number.replace(/\s/g, ""));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md flex flex-col px-6 safe-top safe-bottom">
        {/* HEADER */}
        <div className="pt-8 pb-6 fade-in">
          <h1 className="t-title mb-2">Tezkor natijangiz</h1>
          <p className="t-small text-muted">
            Profilingiz bo'yicha dastlabki tahlil
          </p>
        </div>

        {/* SIGNALS */}
        <div className="mb-6 fade-in fade-in-1">
          <p className="t-caption text-subtle mb-3">Kuchli signallaringiz</p>
          <div className="space-y-2">
            {teaser.top_2_signals?.map((s: any) => (
              <div
                key={s.key}
                className="flex items-center justify-between py-2"
              >
                <span className="t-body capitalize">
                  {s.key.replace(/_/g, " ")}
                </span>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(s.score * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* CAREERS */}
        <div className="mb-6 fade-in fade-in-2">
          <p className="t-caption text-subtle mb-3">Mos yo'nalishlar</p>
          <div className="space-y-3">
            {teaser.top_2_careers?.map((c: any) => (
              <div
                key={c.career_id}
                className="card-clean flex items-center justify-between"
              >
                <div>
                  <p className="t-heading">{c.career_uz}</p>
                  <p className="t-small text-muted">{c.cluster_uz}</p>
                </div>
                <span className="t-heading text-primary tabular-nums">
                  {Math.round(c.fit)}%
                </span>
              </div>
            ))}
          </div>

          {teaser.locked_count > 0 && (
            <div className="mt-3 flex items-center gap-2 t-small text-muted">
              <Lock className="w-3.5 h-3.5" />
              <span>Yana {teaser.locked_count} ta yo'nalish yashirilgan</span>
            </div>
          )}
        </div>

        {/* PREMIUM */}
        <div className="card-clean mb-6 fade-in fade-in-3">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-4 h-4 text-primary" />
            <h3 className="t-heading">Chuqur tahlil</h3>
          </div>

          <ul className="space-y-2.5 mb-5">
            {[
              "Top-5 mos yo'nalish",
              "Fit + Readiness har biri uchun",
              "To'siqlar va yechimlar",
              "6-12 oy shaxsiy yo'l xaritasi",
              "Birinchi 3 qadam",
              "PDF hisobot",
            ].map((t, i) => (
              <li key={i} className="flex items-start gap-2.5 t-small">
                <Check className="w-4 h-4 text-success shrink-0 mt-0.5" />
                <span>{t}</span>
              </li>
            ))}
          </ul>

          <div className="divider" />

          <div className="price-row">
            <span className="t-small text-muted">Narx</span>
            <span className="t-heading">39 000 so'm</span>
          </div>

          <div className="pt-4">
            <button
              onClick={openPayment}
              disabled={sending}
              className="btn btn-primary"
            >
              <CreditCard className="w-4 h-4" />
              <span>{sending ? "Yuklanmoqda..." : "Karta orqali to'lash"}</span>
            </button>
          </div>

          <p className="t-caption text-subtle text-center mt-4">
            7 kun ichida pulni qaytarish
          </p>
        </div>

        <p className="t-caption text-subtle text-center pb-6 fade-in fade-in-4">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>

      {/* ═══ PAYMENT MODAL ═══ */}
      {openPay && card && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden">
            {/* Header */}
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between">
              <div>
                <h3 className="t-heading">Karta orqali to'lash</h3>
                <p className="t-caption text-subtle mt-1">
                  Quyidagi kartaga o'tkazing
                </p>
              </div>
              <button
                onClick={() => setOpenPay(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Card info */}
            <div className="p-5 space-y-4">
              <div>
                <p className="t-caption text-subtle mb-2">Karta raqami</p>
                <button
                  onClick={copyCard}
                  className="w-full flex items-center justify-between p-4 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)] hover:border-[var(--color-border-strong)] transition"
                >
                  <span className="t-heading tabular-nums tracking-wider">
                    {card.number}
                  </span>
                  <span className="flex items-center gap-1.5 t-caption text-primary">
                    {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? "Nusxa olindi" : "Nusxa"}</span>
                  </span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="t-caption text-subtle mb-1">Egasi</p>
                  <p className="t-small">{card.holder}</p>
                </div>
                <div>
                  <p className="t-caption text-subtle mb-1">Bank</p>
                  <p className="t-small">{card.bank}</p>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-[var(--color-primary-soft)] border border-primary/30">
                <p className="t-caption text-primary mb-1">To'lov summasi</p>
                <p className="t-metric text-primary leading-none">
                  {card.amount.toLocaleString("uz")}
                  <span className="text-base ml-1">so'm</span>
                </p>
              </div>

              <div className="pt-2 space-y-2">
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">1.</span>
                  <span>Yuqoridagi kartaga pul o'tkazing</span>
                </div>
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">2.</span>
                  <span>To'lov skrinshotini oling</span>
                </div>
                <div className="flex items-start gap-2 t-small text-muted">
                  <span className="text-primary font-bold shrink-0">3.</span>
                  <span>Skrinshotni <b className="text-text">@ulugbek_aliboyev</b> ga yuboring</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="p-4 pt-0 space-y-2">
              <a
                href={`https://t.me/${card.admin_username?.replace("@", "") || "ulugbek_aliboyev"}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary block text-center flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>Adminga skrinshot yuborish</span>
              </a>

              <button
                onClick={() => setOpenPay(false)}
                className="btn btn-ghost"
              >
                Keyinroq
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/teaser/page.tsx — manual tolov")

# ═══════════════════════════════════════════════════════════
# 4. ADMIN PANEL — pending payments bo'limi
# ═══════════════════════════════════════════════════════════
ADMIN_PANEL = Path("qadam-miniapp/app/admin/page.tsx")
ap = ADMIN_PANEL.read_text(encoding="utf-8")

# Import qo'shish
if "getPendingPayments" not in ap:
    ap = ap.replace(
        "  getAdminFeedbacks,\n} from \"@/lib/api\";",
        "  getAdminFeedbacks,\n  getPendingPayments,\n  approvePayment,\n} from \"@/lib/api\";",
    )

    # State qo'shish
    ap = ap.replace(
        "  const [feedbacks, setFeedbacks] = useState<any[]>([]);",
        "  const [feedbacks, setFeedbacks] = useState<any[]>([]);\n  const [pending, setPending] = useState<any[]>([]);",
    )

    # Load funksiyasida pending qo'shish
    ap = ap.replace(
        "      const [ov, dl, tc, fb] = await Promise.all([\n        getAdminOverview(),\n        getAdminDaily(30),\n        getAdminTopCareers(15),\n        getAdminFeedbacks(30),\n      ]);",
        "      const [ov, dl, tc, fb, pd] = await Promise.all([\n        getAdminOverview(),\n        getAdminDaily(30),\n        getAdminTopCareers(15),\n        getAdminFeedbacks(30),\n        getPendingPayments().catch(() => ({ payments: [] })),\n      ]);",
    )

    ap = ap.replace(
        "      setFeedbacks(fb.feedbacks || []);",
        "      setFeedbacks(fb.feedbacks || []);\n      setPending(pd.payments || []);",
    )

    # UI qo'shish — Feedbacks'dan keyin
    ap = ap.replace(
        "      {/* Feedbacks */}",
        '''      {/* ═══ PENDING PAYMENTS ═══ */}
      {pending.length > 0 && (
        <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30 mb-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-amber-400 text-lg">💳</span>
            <h3 className="font-semibold text-sm">
              Kutilayotgan to'lovlar ({pending.length})
            </h3>
          </div>
          <div className="space-y-2">
            {pending.map((p) => (
              <div
                key={p.id}
                className="flex items-center justify-between p-3 rounded-xl bg-[var(--tg-bg)]"
              >
                <div>
                  <p className="text-xs font-medium">Payment #{p.id}</p>
                  <p className="text-[10px] text-[var(--tg-hint)]">
                    User: {p.user_id} · {p.amount_uzs.toLocaleString("uz")} so'm
                  </p>
                </div>
                <button
                  onClick={async () => {
                    try {
                      await approvePayment(p.id);
                      load();
                    } catch (e: any) {
                      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
                    }
                  }}
                  className="text-xs px-3 py-1.5 rounded-lg bg-emerald-500 text-white font-medium"
                >
                  Tasdiqlash
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Feedbacks */}''',
    )

    ADMIN_PANEL.write_text(ap, encoding="utf-8")
    print("[OK] app/admin/page.tsx — pending payments")
else:
    print("[SKIP] admin/page.tsx — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 5. api.ts — yangi funksiyalar
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

if "getPendingPayments" not in api:
    api += '''

export async function getPendingPayments() {
  const r = await api.get("/payments/manual/pending", {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function approvePayment(payment_id: number) {
  const r = await api.post("/payments/manual/approve", {
    init_data: getInitData(),
    payment_id,
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] api.ts — manual tolov funksiyalari")

# ═══════════════════════════════════════════════════════════
# 6. .env.example — yangi o'zgaruvchilar
# ═══════════════════════════════════════════════════════════
ENV = Path("qadam/.env.example")
env = ENV.read_text(encoding="utf-8")

if "CARD_NUMBER" not in env:
    env += '''

# ═══ Manual to'lov (karta) ═══
CARD_NUMBER=8600 0000 0000 0000
CARD_HOLDER=Ulugbek Aliboyev
CARD_BANK=Uzcard
ADMIN_CHAT_ID=
'''
    ENV.write_text(env, encoding="utf-8")
    print("[OK] .env.example — karta ozgaruvchilari")

print()
print("=" * 60)
print("Manual to'lov tizimi — TAYYOR!")
print("=" * 60)
print()
print("YANGI OQIM:")
print("  1. User 'Karta orqali to'lash' bosadi")
print("  2. Modal — karta raqami + summa")
print("  3. User to'lov qiladi, skrinshot oladi")
print("  4. 'Skrinshotni adminga yuborish' → @ulugbek_aliboyev")
print("  5. Admin bot'da xabar oladi → Tasdiqlash tugmasi")
print("  6. Tasdiqlanganda — user Stage 2'ga avtomatik o'tadi")
print()
print("KEYINGI:")
print("  1. Render ENV qo'shish:")
print("     CARD_NUMBER, CARD_HOLDER, CARD_BANK, ADMIN_CHAT_ID")
print("  2. git add -A")
print('  3. git commit -m "Manual payment via card"')
print("  4. git push")
print("  5. Render Manual Deploy (backend + bot)")
print("  6. Vercel auto")