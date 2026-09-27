# -*- coding: utf-8 -*-
"""Manual to'lov v2 — screenshot Mini App ichida, avtomatik."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — /payments/manual/upload (rasm qabul qilish)
# ═══════════════════════════════════════════════════════════
PAYMENTS = Path("qadam/backend/api/payments.py")
pay = PAYMENTS.read_text(encoding="utf-8")

# Eski manual endpoint'ni olib tashlash
import re
pay = re.sub(
    r'# ═+\s*MANUAL TO.*?(?=^@router\.|^class |\Z)',
    '',
    pay,
    flags=re.DOTALL | re.MULTILINE,
)

# Yangi toza manual endpoint
MANUAL = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV v2 — screenshot Mini App ichida yuklanadi
# ═══════════════════════════════════════════════════════════════════

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Qadam.io")
CARD_BANK = os.getenv("CARD_BANK", "Uzcard")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))


@router.get("/manual/card-info")
async def get_card_info():
    """Karta ma'lumotlari (frontend uchun)."""
    return {
        "card": {
            "number": CARD_NUMBER,
            "holder": CARD_HOLDER,
            "bank": CARD_BANK,
            "amount": PRICE_UZS,
        }
    }


@router.post("/manual/upload")
async def manual_upload(
    init_data: str = Form(...),
    stage1_result_id: int = Form(...),
    screenshot: UploadFile = File(...),
):
    """
    User screenshot yuklaydi — Mini App ichida.
    Backend: rasmni adminga bot orqali yuboradi + payment yozadi.
    """
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    # Rasm tekshiruvi
    if screenshot.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(400, "Faqat rasm fayl yuklang (JPG, PNG)")

    content = await screenshot.read()
    if len(content) > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(400, "Rasm hajmi 5 MB dan oshmasin")

    async with SessionLocal() as s:
        s1 = await s.get(TestResult, stage1_result_id)
        if not s1 or s1.user_id != user["id"]:
            raise HTTPException(404, "Stage 1 topilmadi")
        if s1.paid:
            raise HTTPException(409, "Allaqachon to'langan")

        p = Payment(
            user_id=user["id"],
            stage1_result_id=stage1_result_id,
            provider="manual",
            amount_uzs=PRICE_UZS,
            status="pending",
        )
        s.add(p)
        await s.commit()
        await s.refresh(p)
        payment_id = p.id

    # Adminga bot orqali rasm + tugmalar
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
        user_id = user["id"]

        caption = (
            f"💳 <b>Yangi to'lov</b>\\n\\n"
            f"👤 <b>User:</b> {first_name}\\n"
            f"🔗 <b>Username:</b> @{username}\\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\\n"
            f"💰 <b>Summa:</b> {PRICE_UZS:,} so'm\\n"
            f"🎫 <b>Payment ID:</b> {payment_id}\\n\\n"
            f"Rasmni tekshiring va tasdiqlang:"
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
        ])

        photo = BufferedInputFile(content, filename="screenshot.jpg")
        if ADMIN_CHAT_ID:
            await bot.send_photo(
                ADMIN_CHAT_ID,
                photo=photo,
                caption=caption,
                reply_markup=kb,
            )

        await bot.session.close()
    except Exception as e:
        log.error(f"Adminga rasm yuborishda xato: {e}")

    return {"ok": True, "payment_id": payment_id, "status": "pending"}


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

    # Userga xabar
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
'''

# Imports qo'shish
if "from fastapi import" in pay and "UploadFile" not in pay.split("\n")[10]:
    pay = pay.replace(
        "from fastapi import APIRouter, HTTPException, Request, Query",
        "from fastapi import APIRouter, HTTPException, Request, Query, UploadFile, File, Form",
    )

PAYMENTS.write_text(pay + MANUAL, encoding="utf-8")
print("[OK] backend/api/payments.py — /manual/upload + /manual/approve")

# ═══════════════════════════════════════════════════════════
# 2. BOT — approve/reject callback
# ═══════════════════════════════════════════════════════════
BOT_PAY = Path("qadam/bot/handlers/payment.py")
bot_pay = BOT_PAY.read_text(encoding="utf-8")

# Eski manual callback'larni olib tashlash
import re
bot_pay = re.sub(
    r'# ═+\s*MANUAL TO.*$',
    '',
    bot_pay,
    flags=re.DOTALL,
)

NEW_CALLBACKS = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash (v2)
# ═══════════════════════════════════════════════════════════════════

import os as _os


def _is_admin(user_id: int) -> bool:
    ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    return user_id in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[2])

    from backend.db import SessionLocal
    from backend.models import Payment, TestResult

    user_id = None
    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p:
            await callback.answer("Payment topilmadi", show_alert=True)
            return
        p.status = "paid"
        s1 = await s.get(TestResult, p.stage1_result_id)
        if s1:
            s1.paid = True
        await s.commit()
        user_id = p.user_id

    # Userga avtomatik xabar
    if user_id:
        try:
            from aiogram.types import (
                InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
            )
            webapp = _os.getenv("WEBAPP_URL", "")
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🎯 Chuqur tahlilni boshlash",
                    web_app=WebAppInfo(url=f"{webapp}/stage2"),
                )
            ]])
            await callback.bot.send_message(
                user_id,
                "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
                "Endi 18 ta chuqur savolga javob bering va shaxsiy "
                "yo'l xaritangizni oling.",
                reply_markup=kb,
            )
        except Exception as e:
            import logging
            logging.error(f"User xabar yuborishda xato: {e}")

    # Xabarni yangilash
    try:
        new_caption = (callback.message.caption or "") + "\\n\\n✅ <b>TASDIQLANDI</b>"
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
    except Exception:
        pass

    await callback.answer("Tasdiqlandi ✅")


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    if not _is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yoq", show_alert=True)
        return

    payment_id = int(callback.data.split(":")[2])

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

    # Userga xabar (rad etildi)
    if user_id:
        try:
            await callback.bot.send_message(
                user_id,
                "❌ <b>To'lov tasdiqlanmadi</b>\\n\\n"
                "Skrinshot aniq emas yoki to'lov topilmadi. "
                "Iltimos, qaytadan urinib ko'ring.",
            )
        except Exception:
            pass

    try:
        new_caption = (callback.message.caption or "") + "\\n\\n❌ <b>RAD ETILDI</b>"
        await callback.message.edit_caption(caption=new_caption, reply_markup=None)
    except Exception:
        pass

    await callback.answer("Rad etildi")
'''

BOT_PAY.write_text(bot_pay + NEW_CALLBACKS, encoding="utf-8")
print("[OK] bot/handlers/payment.py — callback v2")

# ═══════════════════════════════════════════════════════════
# 3. api.ts — upload funksiyasi
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

# Eski manual funksiyalarni olib tashlash
api = re.sub(
    r'export async function getPendingPayments.*?(?=export |\Z)',
    '',
    api,
    flags=re.DOTALL,
)
api = re.sub(
    r'export async function approvePayment.*?(?=export |\Z)',
    '',
    api,
    flags=re.DOTALL,
)

NEW_API = '''

export async function getCardInfo() {
  const r = await api.get("/payments/manual/card-info");
  return r.data;
}

export async function uploadPaymentScreenshot(
  stage1_result_id: number,
  file: File
) {
  const formData = new FormData();
  formData.append("init_data", getInitData());
  formData.append("stage1_result_id", String(stage1_result_id));
  formData.append("screenshot", file);

  const r = await api.post("/payments/manual/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return r.data;
}
'''
API.write_text(api + NEW_API, encoding="utf-8")
print("[OK] api.ts — upload funksiyasi")

# ═══════════════════════════════════════════════════════════
# 4. TEASER — file upload modal
# ═══════════════════════════════════════════════════════════
TEASER = Path("qadam-miniapp/app/teaser/page.tsx")

TEASER.write_text(r'''"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Lock, Check, Sparkles, CreditCard, X, Copy,
  Upload, Loader2, CheckCircle2, Image as ImageIcon,
} from "lucide-react";
import { useStore } from "@/lib/store";
import { getCardInfo, uploadPaymentScreenshot } from "@/lib/api";

export default function TeaserPage() {
  const router = useRouter();
  const teaser = useStore((s) => s.stage1Teaser);
  const stage1ResultId = useStore((s) => s.stage1ResultId);

  const [openPay, setOpenPay] = useState(false);
  const [card, setCard] = useState<any>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [done, setDone] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getCardInfo()
      .then((r) => setCard(r.card))
      .catch(() => {});
  }, []);

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
    if (!file || !stage1ResultId) return;
    setUploading(true);
    try {
      await uploadPaymentScreenshot(stage1ResultId, file);
      setDone(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
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
              <div key={s.key} className="flex items-center justify-between py-2">
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
              onClick={() => setOpenPay(true)}
              className="btn btn-primary"
            >
              <CreditCard className="w-4 h-4" />
              <span>Karta orqali to'lash</span>
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
          <div className="w-full max-w-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="p-5 border-b border-[var(--color-border)] flex items-center justify-between sticky top-0 bg-[var(--color-surface)] z-10">
              <div>
                <h3 className="t-heading">
                  {done ? "Yuborildi" : "Karta orqali to'lash"}
                </h3>
                {!done && (
                  <p className="t-caption text-subtle mt-1">
                    Quyidagi kartaga o'tkazing
                  </p>
                )}
              </div>
              <button
                onClick={() => {
                  setOpenPay(false);
                  setFile(null);
                  setPreview(null);
                  setDone(false);
                }}
                className="w-8 h-8 rounded-full flex items-center justify-center text-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* DONE state */}
            {done ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-[var(--color-success-soft)] flex items-center justify-center mx-auto mb-5">
                  <CheckCircle2 className="w-8 h-8 text-success" />
                </div>
                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin tekshirib, tasdiqlagach sizga avtomatik xabar keladi.
                  Shundan song chuqur tahlil ochiladi.
                </p>
                <button
                  onClick={() => {
                    setOpenPay(false);
                    setFile(null);
                    setPreview(null);
                    setDone(false);
                  }}
                  className="btn btn-primary"
                >
                  Yopish
                </button>
              </div>
            ) : (
              <>
                <div className="p-5 space-y-4">
                  {/* Card number */}
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
                        {copied ? (
                          <Check className="w-3.5 h-3.5" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                        <span>{copied ? "Olindi" : "Nusxa"}</span>
                      </span>
                    </button>
                  </div>

                  {/* Card meta */}
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

                  {/* Amount */}
                  <div className="p-4 rounded-xl bg-[var(--color-primary-soft)] border border-primary/30">
                    <p className="t-caption text-primary mb-1">To'lov summasi</p>
                    <p className="t-metric text-primary leading-none">
                      {card.amount.toLocaleString("uz")}
                      <span className="text-base ml-1">so'm</span>
                    </p>
                  </div>

                  <div className="divider" />

                  {/* Screenshot upload */}
                  <div>
                    <p className="t-caption text-subtle mb-3">
                      To'lov skrinshotini yuklang
                    </p>

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
                          <p className="t-caption text-subtle mt-0.5">
                            JPG, PNG · maks 5 MB
                          </p>
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
                          onClick={() => {
                            setFile(null);
                            setPreview(null);
                          }}
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

                {/* Submit */}
                <div className="p-4 pt-0">
                  <button
                    onClick={handleSubmit}
                    disabled={!file || uploading}
                    className="btn btn-primary"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Yuborilmoqda...</span>
                      </>
                    ) : (
                      <>
                        <ImageIcon className="w-4 h-4" />
                        <span>Skrinshotni yuborish</span>
                      </>
                    )}
                  </button>
                  <p className="t-caption text-subtle text-center mt-3">
                    Admin tasdiqlagach avtomatik xabar keladi
                  </p>
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
print("[OK] app/teaser/page.tsx — file upload")

# ═══════════════════════════════════════════════════════════
# 5. Req — python-multipart (file upload uchun)
# ═══════════════════════════════════════════════════════════
REQ = Path("qadam/requirements.txt")
req = REQ.read_text(encoding="utf-8")

if "python-multipart" not in req:
    req += "\npython-multipart==0.0.17\n"
    REQ.write_text(req, encoding="utf-8")
    print("[OK] requirements.txt — python-multipart")

print()
print("=" * 60)
print("Manual to'lov v2 — TAYYOR!")
print("=" * 60)
print()
print("YANGI OQIM (to'liq Telegram ichida):")
print("  1. User 'Karta orqali to'lash' bosadi")
print("  2. Modal — karta raqami + screenshot yuklash")
print("  3. User screenshot tanlaydi (Mini App ichida)")
print("  4. 'Skrinshotni yuborish' → backend")
print("  5. Backend → adminga BOT orqali rasm + tugmalar")
print("  6. Admin [Tasdiqlash] bosadi")
print("  7. User avtomatik xabar oladi + Stage 2 ochiladi")
print()
print("KEYINGI:")
print("  1. Render ENV: CARD_NUMBER, CARD_HOLDER, CARD_BANK, ADMIN_CHAT_ID")
print("  2. git add -A")
print('  3. git commit -m "Manual payment v2: screenshot in mini app"')
print("  4. git push")
print("  5. Render Manual Deploy (backend + bot)")