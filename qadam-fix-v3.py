# -*- coding: utf-8 -*-
"""Qadam.io — Fix v3: Bot menu + /premium page + Premium endpoints."""
from pathlib import Path

BACKEND = Path("qadam/backend")
FE = Path("qadam-miniapp")
BOT = Path("qadam/bot")

# ═══════════════════════════════════════════════════════════
# 1. BOT — welcome xabar + menu tugmalari yangilash
# ═══════════════════════════════════════════════════════════
START = BOT / "handlers/start.py"
START.write_text(r'''"""FTT § 4-5: Welcome flow + Mini App buttons (v3)."""
import os
from html import escape
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo,
)

router = Router()
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://qadam-loyiha-deepseek-eight.vercel.app")

WELCOME_TEXT = (
    "Assalomu alaykum, <b>{name}</b>!\n\n"
    "Men — <b>Qadam.io</b>, kasb va soha tanlashda yordamchi.\n\n"
    "Sizga mos yo'nalishni dalillar asosida aniqlash va shaxsiy "
    "yo'l xaritasi tuzishda yordam beraman.\n\n"
    "<b>3 daqiqa</b> — 13 savol — <b>bepul</b>."
)

PREMIUM_INTRO_TEXT = (
    "<b>Chuqur tahlil</b>\n\n"
    "Chuqur tahlil sizga:\n"
    "• 18 qo'shimcha savol\n"
    "• Top-5 mos yo'nalish\n"
    "• Fit va Readiness (har biri uchun)\n"
    "• Skill-gap tahlili\n"
    "• 6-12 oylik shaxsiy yo'l xaritasi\n"
    "• PDF hisobot\n\n"
    "Narx: <b>39 000 so'm</b> yoki <b>150 Stars</b>"
)

HELP_TEXT = (
    "<b>Qadam.io yordam</b>\n\n"
    "/start — boshidan boshlash\n"
    "/help — yordam\n\n"
    "Savollar: @ulugbek_aliboyev"
)


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎯 Bepul diagnostika",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/discovery"),
        )],
        [InlineKeyboardButton(
            text="💎 Chuqur tahlil (premium)",
            callback_data="diag:premium",
        )],
        [InlineKeyboardButton(
            text="ℹ️ Qadam.io qanday ishlaydi?",
            callback_data="info:how",
        )],
        [InlineKeyboardButton(
            text="🔐 Maxfiylik",
            callback_data="info:privacy",
        )],
    ])


def premium_intro_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Bepul diagnostikadan boshlash",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/discovery"),
        )],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="nav:back")],
    ])


def _safe_name(user) -> str:
    return escape(user.first_name or "do'stim")


@router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        WELCOME_TEXT.format(name=_safe_name(m.from_user)),
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(m: Message):
    await m.answer(HELP_TEXT)


@router.callback_query(F.data == "diag:premium")
async def cb_premium(q: CallbackQuery):
    await q.answer()
    try:
        await q.message.edit_text(PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb())
    except Exception:
        await q.message.answer(PREMIUM_INTRO_TEXT, reply_markup=premium_intro_kb())


@router.callback_query(F.data == "nav:back")
async def cb_back(q: CallbackQuery):
    await q.answer()
    try:
        await q.message.edit_text(
            WELCOME_TEXT.format(name=_safe_name(q.from_user)),
            reply_markup=main_menu_kb(),
        )
    except Exception:
        pass


@router.callback_query(F.data == "info:how")
async def cb_how(q: CallbackQuery):
    await q.answer()
    await q.message.answer(
        "<b>Qadam.io qanday ishlaydi?</b>\n\n"
        "1. Siz 13 ta savolga javob berasiz (3 daqiqa).\n"
        "2. Tizim javoblarni signallarga aylantiradi.\n"
        "3. Signallar 25+ kasbiy yo'nalish bilan taqqoslanadi.\n"
        "4. Sizga mos 3 ta yo'nalish va amaliy yo'l xaritasi beriladi.\n\n"
        "<i>Halol tahlil. Manipulyatsiyasiz.</i>"
    )


@router.callback_query(F.data == "info:privacy")
async def cb_privacy(q: CallbackQuery):
    await q.answer()
    await q.message.answer(
        "<b>Maxfiylik</b>\n\n"
        "Javoblaringiz faqat tahlil uchun ishlatiladi. "
        "Uchinchi shaxslarga ruxsatsiz uzatilmaydi."
    )


@router.message(Command("admin"))
async def cmd_admin(m: Message):
    admin_ids = set(
        int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    if m.from_user.id not in admin_ids:
        await m.answer("Ruxsat yo'q")
        return

    url = f"{WEBAPP_URL}/admin"
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Admin Panel", web_app=WebAppInfo(url=url))
    ]])
    await m.answer("Admin panel:", reply_markup=kb)
''', encoding="utf-8")
print("[OK] bot/handlers/start.py — yangi menu")

# ═══════════════════════════════════════════════════════════
# 2. BACKEND — premium manual-request endpoint
# ═══════════════════════════════════════════════════════════
PAYMENTS = BACKEND / "api/payments.py"
pay = PAYMENTS.read_text(encoding="utf-8")

# Eski manual endpoint'ni olib tashlash (agar bor bo'lsa)
import re
pay = re.sub(
    r'# ═+\s*MANUAL TO.*?(?=^@router\.|^class |\Z)',
    '',
    pay,
    flags=re.DOTALL | re.MULTILINE,
)

# Import tekshirish
if "UploadFile" not in pay:
    pay = pay.replace(
        "from fastapi import APIRouter, HTTPException, Request, Query",
        "from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form",
    )

NEW_MANUAL = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV v3 — discovery_session_id bilan
# ═══════════════════════════════════════════════════════════════════

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


@router.get("/manual/card-info")
async def get_card_info():
    """Karta ma'lumotlari."""
    return {
        "card": {
            "number": CARD_NUMBER,
            "holder": CARD_HOLDER,
            "bank": CARD_BANK,
            "amount": PRICE_UZS,
        }
    }


@router.post("/manual/upload-v2")
async def manual_upload_v2(
    init_data: str = Form(...),
    discovery_session_id: int = Form(...),
    screenshot: UploadFile = File(...),
):
    """
    User screenshot yuklaydi (Discovery session'ga bog'langan).
    """
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if screenshot.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(400, "Faqat rasm yuklang (JPG, PNG)")

    content = await screenshot.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "Rasm 5 MB dan oshmasin")

    # Payment yozuvi (discovery_session_id ni `stage1_result_id` ustunida saqlaymiz)
    async with SessionLocal() as s:
        p = Payment(
            user_id=user["id"],
            stage1_result_id=discovery_session_id,
            provider="manual_v2",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    # Adminga rasm + tugmalar
    try:
        from aiogram import Bot
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from aiogram.types import (
            BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
        )

        bot = Bot(
            os.getenv("BOT_TOKEN", ""),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        first_name = user.get("first_name") or "Nomalum"
        username = user.get("username") or "-"
        uid = user["id"]

        caption = (
            f"💳 <b>Yangi to'lov (v2)</b>\\n\\n"
            f"👤 <b>User:</b> {first_name}\\n"
            f"🔗 <b>Username:</b> @{username}\\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\\n"
            f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\\n"
            f"🎫 <b>Payment ID:</b> {payment_id}\\n"
            f"📊 <b>Discovery session:</b> {discovery_session_id}\\n\\n"
            f"Rasmni tekshirib tasdiqlang:"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay:approve:{payment_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay:reject:{payment_id}"),
            ],
        ])

        photo = BufferedInputFile(content, filename="screenshot.jpg")
        if ADMIN_CHAT_ID:
            await bot.send_photo(ADMIN_CHAT_ID, photo=photo, caption=caption, reply_markup=kb)

        await bot.session.close()
    except Exception as e:
        log.error(f"Admin xabar xato: {e}")

    return {"ok": True, "payment_id": payment_id, "status": "pending"}
'''

PAYMENTS.write_text(pay.rstrip() + NEW_MANUAL, encoding="utf-8")
print("[OK] backend/api/payments.py — /manual/upload-v2")

# ═══════════════════════════════════════════════════════════
# 3. BOT payment callback — entitlement grant
# ═══════════════════════════════════════════════════════════
BOT_PAY = BOT / "handlers/payment.py"
bot_pay = BOT_PAY.read_text(encoding="utf-8")

# Eski callback'larni olib tashlash
bot_pay = re.sub(
    r'# ═+\s*MANUAL TO.*$',
    '',
    bot_pay,
    flags=re.DOTALL,
)

CALLBACKS = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash (v3)
# ═══════════════════════════════════════════════════════════════════

import os as _os
import logging as _log

_logger = _log.getLogger("qadam.bot.payment")


def _is_admin(uid: int) -> bool:
    ids = set(int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    return uid in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Tasdiqlanmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    try:
        from backend.db import SessionLocal
        from backend.models import Payment
        from backend.services.entitlement_service import grant_entitlement

        user_id = None
        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if not p:
                await callback.message.edit_caption(
                    caption=(callback.message.caption or "") + "\\n\\n⚠️ Payment topilmadi"
                )
                return
            p.status = "paid"
            await s.commit()
            user_id = p.user_id

        # Entitlement grant
        await grant_entitlement(
            user_id=user_id,
            entitlement_key="premium_career_intelligence",
            source="manual_card",
            payment_reference=str(payment_id),
        )
        _logger.info(f"Payment {payment_id} paid, entitlement granted, user={user_id}")

        # Userga xabar
        if user_id:
            try:
                from aiogram.types import (
                    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
                )
                webapp = _os.getenv("WEBAPP_URL", "")
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="🎯 Chuqur tahlilni boshlash",
                        web_app=WebAppInfo(url=f"{webapp}/career-intelligence"),
                    )
                ]])
                await callback.bot.send_message(
                    user_id,
                    "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
                    "Endi chuqur tahlilni boshlashingiz mumkin.",
                    reply_markup=kb,
                )
            except Exception as e:
                _logger.error(f"User xabar xato: {e}")

        try:
            new_caption = (callback.message.caption or "") + "\\n\\n✅ <b>TASDIQLANDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception:
            pass

    except Exception as e:
        _logger.error(f"cb_approve xato: {e}")
        try:
            await callback.message.reply(f"⚠️ Xato: {str(e)[:100]}")
        except Exception:
            pass


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Rad etilmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception:
        return

    try:
        from backend.db import SessionLocal
        from backend.models import Payment

        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if p:
                p.status = "rejected"
                await s.commit()
                user_id = p.user_id
            else:
                user_id = None

        if user_id:
            try:
                await callback.bot.send_message(
                    user_id,
                    "❌ <b>To'lov tasdiqlanmadi</b>\\n\\n"
                    "Skrinshot aniq emas yoki to'lov topilmadi.",
                )
            except Exception:
                pass

        try:
            new_caption = (callback.message.caption or "") + "\\n\\n❌ <b>RAD ETILDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception:
            pass
    except Exception as e:
        _logger.error(f"cb_reject xato: {e}")
'''

BOT_PAY.write_text(bot_pay.rstrip() + CALLBACKS, encoding="utf-8")
print("[OK] bot/handlers/payment.py — approve/reject v3")

# ═══════════════════════════════════════════════════════════
# 4. FRONTEND — /premium page
# ═══════════════════════════════════════════════════════════
(FE / "app/premium").mkdir(exist_ok=True)

(FE / "app/premium/page.tsx").write_text(r'''"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Check, CreditCard, Copy, X, Upload, Loader2,
  CheckCircle2, Image as ImageIcon, Sparkles,
} from "lucide-react";
import { api, getInitData } from "@/lib/api";

export default function PremiumPage() {
  const router = useRouter();
  const [card, setCard] = useState<any>(null);
  const [openPay, setOpenPay] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const discoverySessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("discovery_session_id"))
    : null;

  useEffect(() => {
    api.get("/payments/manual/card-info")
      .then((r) => setCard(r.data.card))
      .catch(() => setError("Karta malumotlarini yuklab bolmadi"));
  }, []);

  const copyCard = () => {
    if (card?.number) {
      navigator.clipboard.writeText(card.number.replace(/\s/g, ""));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 5 * 1024 * 1024) {
      alert("Rasm hajmi 5 MB dan oshmasin");
      return;
    }
    setFile(f);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(f);
  };

  const handleSubmit = async () => {
    if (!file || !discoverySessionId) {
      alert("Iltimos, rasm tanlang");
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("init_data", getInitData());
      formData.append("discovery_session_id", String(discoverySessionId));
      formData.append("screenshot", file);

      const r = await api.post("/payments/manual/upload-v2", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (r.data.ok) setDone(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-8 pb-6">
        {/* Header */}
        <div className="mb-8 fade-in">
          <p className="t-caption text-primary mb-2">Chuqur tahlil</p>
          <h1 className="t-display mb-3">
            Shaxsiy kasb<br />yo&apos;l xaritasi
          </h1>
          <p className="t-small text-muted">
            Fit + Readiness, skill-gap, 6-12 oylik reja va PDF hisobot.
          </p>
        </div>

        {/* Features */}
        <div className="card-clean mb-6 fade-in fade-in-1">
          <ul className="space-y-2.5">
            {[
              "18 savol chuqur diagnostika",
              "Top-5 mos yo'nalish",
              "Fit + Readiness tahlili",
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
        </div>

        {/* Price */}
        <div className="card-clean mb-6 fade-in fade-in-2">
          <div className="flex items-baseline justify-between mb-1">
            <span className="t-small text-muted">Narx</span>
            <div className="text-right">
              <span className="t-title">39 000</span>
              <span className="t-small text-muted ml-1">so&apos;m</span>
            </div>
          </div>
          <p className="t-caption text-subtle">yoki 150 Stars</p>
        </div>

        {/* CTA */}
        <div className="fade-in fade-in-3">
          <button onClick={() => setOpenPay(true)} className="btn btn-primary">
            <CreditCard className="w-4 h-4" />
            <span>Karta orqali to&apos;lash</span>
          </button>
          <p className="t-caption text-subtle text-center mt-4">
            Admin tekshiradi va 5-10 daqiqada tasdiqlanadi
          </p>
        </div>

        {error && (
          <div className="card-clean border-[var(--color-danger)]/40 mt-4">
            <p className="t-small text-danger">{error}</p>
          </div>
        )}
      </div>

      {/* ═══ PAYMENT MODAL ═══ */}
      {openPay && card && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between sticky top-0 bg-[var(--color-surface)] z-10">
              <div>
                <h3 className="t-heading">
                  {done ? "Yuborildi" : "Karta orqali to'lash"}
                </h3>
                {!done && (
                  <p className="t-caption text-subtle mt-1">
                    Quyidagi kartaga o&apos;tkazing
                  </p>
                )}
              </div>
              <button
                onClick={() => { setOpenPay(false); setDone(false); }}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {done ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-5">
                  <CheckCircle2 className="w-8 h-8 text-success" />
                </div>
                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin tasdiqlagach sizga Telegram orqali xabar keladi.
                </p>
                <button
                  onClick={() => {
                    const tg = (window as any).Telegram?.WebApp;
                    if (tg?.close) tg.close();
                  }}
                  className="btn btn-primary"
                >
                  Botga qaytish
                </button>
              </div>
            ) : (
              <>
                <div className="p-5 space-y-4">
                  <div>
                    <p className="t-caption text-subtle mb-2">Karta raqami</p>
                    <button
                      onClick={copyCard}
                      className="w-full flex items-center justify-between p-4 rounded-xl bg-[var(--color-surface-2)] border border-[var(--color-border)]"
                    >
                      <span className="t-heading tabular-nums tracking-wider">
                        {card.number}
                      </span>
                      <span className="flex items-center gap-1.5 t-caption text-primary">
                        {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copied ? "Olindi" : "Nusxa"}</span>
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
                    <p className="t-caption text-primary mb-1">To&apos;lov summasi</p>
                    <p className="t-metric text-primary leading-none">
                      {card.amount.toLocaleString("uz")}
                      <span className="text-base ml-1">so&apos;m</span>
                    </p>
                  </div>

                  <div className="divider" />

                  <div>
                    <p className="t-caption text-subtle mb-3">To&apos;lov skrinshotini yuklang</p>
                    {!preview ? (
                      <button
                        onClick={() => fileRef.current?.click()}
                        className="w-full flex flex-col items-center justify-center gap-3 p-6 rounded-xl border-2 border-dashed border-[var(--color-border)] hover:border-primary transition bg-[var(--color-surface-2)]"
                      >
                        <div className="w-10 h-10 rounded-full bg-[var(--color-primary-soft)] flex items-center justify-center">
                          <Upload className="w-5 h-5 text-primary" />
                        </div>
                        <div className="text-center">
                          <p className="t-small font-medium">Rasm tanlash</p>
                          <p className="t-caption text-subtle mt-0.5">JPG, PNG · maks 5 MB</p>
                        </div>
                      </button>
                    ) : (
                      <div className="relative">
                        <img
                          src={preview}
                          alt="Screenshot"
                          className="w-full rounded-xl border border-[var(--color-border)] max-h-64 object-contain bg-[var(--color-surface-2)]"
                        />
                        <button
                          onClick={() => { setFile(null); setPreview(null); }}
                          className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/70 flex items-center justify-center"
                        >
                          <X className="w-4 h-4 text-white" />
                        </button>
                      </div>
                    )}
                    <input
                      ref={fileRef}
                      type="file"
                      accept="image/jpeg,image/png,image/webp"
                      onChange={handleFile}
                      className="hidden"
                    />
                  </div>
                </div>

                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={!file || uploading || !discoverySessionId}
                    className="btn btn-primary"
                  >
                    {uploading ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /><span>Yuborilmoqda...</span></>
                    ) : (
                      <><ImageIcon className="w-4 h-4" /><span>Skrinshotni yuborish</span></>
                    )}
                  </button>
                  {!discoverySessionId && (
                    <p className="t-caption text-danger text-center mt-2">
                      Discovery session topilmadi. Avval bepul diagnostikani o&apos;ting.
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/premium/page.tsx")

# ═══════════════════════════════════════════════════════════
# 5. /career-intelligence placeholder (keyingi batch)
# ═══════════════════════════════════════════════════════════
(FE / "app/career-intelligence").mkdir(exist_ok=True)

(FE / "app/career-intelligence/page.tsx").write_text(r'''"use client";

import { Sparkles } from "lucide-react";

export default function CareerIntelligencePage() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-10 text-center">
        <div className="w-16 h-16 rounded-full bg-[var(--color-primary-soft)] flex items-center justify-center mx-auto mb-6">
          <Sparkles className="w-8 h-8 text-primary" />
        </div>
        <h1 className="t-title mb-3">Chuqur tahlil</h1>
        <p className="t-small text-muted mb-6">
          Bu qism keyingi bosqichda qo&apos;shiladi. Hozircha sizning to&apos;lovingiz
          tasdiqlangan — natija tez orada tayyor bo&apos;ladi.
        </p>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/career-intelligence/page.tsx (placeholder)")

print()
print("=" * 60)
print("Fix v3 — TAYYOR!")
print("=" * 60)
print()
print("Tuzatildi:")
print("  1. Bot welcome xabar va menu tugmalari")
print("  2. Bepul diagnostika → /discovery")
print("  3. /premium sahifa (39 000 so'm + karta)")
print("  4. /career-intelligence placeholder")
print("  5. /payments/manual/upload-v2 endpoint")
print("  6. Bot callback — entitlement grant")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix v3: bot menu + premium page + entitlement grant"')
print("  git push")
print("  Render Manual Deploy (backend + bot)")
print("  Vercel auto")