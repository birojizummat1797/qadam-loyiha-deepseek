# -*- coding: utf-8 -*-
"""Fix v4 — admin callback + manual grant fallback."""
from pathlib import Path
import re

BACKEND = Path("qadam/backend")
BOT = Path("qadam/bot")

# ═══════════════════════════════════════════════════════════
# 1. BOT payment.py — logging + robust import
# ═══════════════════════════════════════════════════════════
BOT_PAY = BOT / "handlers/payment.py"

# Eski callback'larni olib tashlash
bp = BOT_PAY.read_text(encoding="utf-8")
bp = re.sub(
    r'# ═+\s*MANUAL TO.*$',
    '',
    bp,
    flags=re.DOTALL,
)

NEW_BP = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin callback (v4, robust)
# ═══════════════════════════════════════════════════════════════════

import os as _os
import logging as _logging

_log = _logging.getLogger("qadam.bot.payment")


def _is_admin(uid: int) -> bool:
    ids_str = _os.getenv("ADMIN_IDS", "")
    _log.info(f"_is_admin check: uid={uid} ADMIN_IDS={ids_str!r}")
    ids = set(int(x.strip()) for x in ids_str.split(",") if x.strip())
    return uid in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    _log.info(f"cb_approve START: from={callback.from_user.id} data={callback.data}")

    if not _is_admin(callback.from_user.id):
        _log.warning(f"cb_approve: not admin {callback.from_user.id}")
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.answer("Tasdiqlanmoqda...")

    try:
        payment_id = int(callback.data.split(":")[2])
    except Exception as e:
        _log.error(f"cb_approve parse: {e}")
        return

    try:
        from backend.db import SessionLocal
        from backend.models import Payment
        from backend.services.entitlement_service import grant_entitlement

        user_id = None
        stage1_id = None
        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if not p:
                _log.error(f"Payment {payment_id} topilmadi")
                try:
                    await callback.message.edit_caption(
                        caption=(callback.message.caption or "") + "\\n\\n⚠️ Payment topilmadi",
                    )
                except Exception:
                    pass
                return
            p.status = "paid"
            await s.commit()
            user_id = p.user_id
            stage1_id = p.stage1_result_id

        _log.info(f"Payment {payment_id} paid, user={user_id}")

        # Entitlement grant
        try:
            ent = await grant_entitlement(
                user_id=user_id,
                entitlement_key="premium_career_intelligence",
                source="manual_card",
                payment_reference=str(payment_id),
                plan_code="pci_39000_uzs",
                meta={"stage1_result_id": stage1_id},
            )
            _log.info(f"Entitlement granted: id={ent.id} user={user_id}")
        except Exception as e:
            _log.error(f"grant_entitlement xato: {e}")
            try:
                await callback.message.reply(f"⚠️ Entitlement xato: {str(e)[:150]}")
            except Exception:
                pass

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
                        web_app=WebAppInfo(url=f"{webapp}/deep-diagnostic"),
                    )
                ]])
                await callback.bot.send_message(
                    user_id,
                    "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
                    "Chuqur tahlilni boshlashingiz mumkin.",
                    reply_markup=kb,
                )
                _log.info(f"User {user_id} ga xabar yuborildi")
            except Exception as e:
                _log.error(f"User xabar xato: {e}")

        # Caption update
        try:
            new_caption = (callback.message.caption or "") + "\\n\\n✅ <b>TASDIQLANDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception as e:
            _log.error(f"caption update xato: {e}")

    except Exception as e:
        _log.error(f"cb_approve umumiy xato: {e}")
        import traceback
        _log.error(traceback.format_exc())
        try:
            await callback.message.reply(f"⚠️ Xato: {str(e)[:150]}")
        except Exception:
            pass


@router.callback_query(F.data.startswith("pay:reject:"))
async def cb_reject(callback: CallbackQuery):
    _log.info(f"cb_reject: from={callback.from_user.id} data={callback.data}")

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
                    "Skrinshot aniq emas yoki to'lov topilmadi. Qaytadan urinib ko'ring.",
                )
            except Exception:
                pass

        try:
            new_caption = (callback.message.caption or "") + "\\n\\n❌ <b>RAD ETILDI</b>"
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
        except Exception:
            pass
    except Exception as e:
        _log.error(f"cb_reject xato: {e}")
'''

BOT_PAY.write_text(bp.rstrip() + NEW_BP, encoding="utf-8")
print("[OK] bot/handlers/payment.py — logging + robust")

# ═══════════════════════════════════════════════════════════
# 2. BACKEND — dev grant endpoint (admin zaxira)
# ═══════════════════════════════════════════════════════════
ENT = BACKEND / "api/v1/entitlements.py"
e = ENT.read_text(encoding="utf-8")

if "dev-grant" not in e:
    e += '''

# ═══════════════════════════════════════════════════════════
# DEV — Admin manual grant (bot callback ishlamasa)
# ═══════════════════════════════════════════════════════════

from pydantic import BaseModel as _BaseModel


class DevGrantPayload(_BaseModel):
    init_data: str
    user_id: int
    entitlement_key: str = "premium_career_intelligence"


@router.post("/dev-grant")
async def dev_grant(payload: DevGrantPayload):
    """Admin-only: foydalanuvchiga to'g'ridan-to'g'ri entitlement berish."""
    admin = verify_init_data(payload.init_data)
    if not admin:
        raise HTTPException(401, "Invalid initData")

    import os as _os
    admin_ids = set(int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    if admin["id"] not in admin_ids:
        raise HTTPException(403, "Ruxsat yo'q")

    from backend.services.entitlement_service import grant_entitlement
    ent = await grant_entitlement(
        user_id=payload.user_id,
        entitlement_key=payload.entitlement_key,
        source="admin_manual",
        meta={"granted_by": admin["id"]},
    )
    return {"ok": True, "entitlement_id": ent.id, "user_id": payload.user_id}
'''
    ENT.write_text(e, encoding="utf-8")
    print("[OK] backend/api/v1/entitlements.py — /dev-grant")

# ═══════════════════════════════════════════════════════════
# 3. FRONTEND — /premium → /deep-diagnostic entitlement check
# ═══════════════════════════════════════════════════════════
PREMIUM = Path("qadam-miniapp/app/premium/page.tsx")
p = PREMIUM.read_text(encoding="utf-8")

# CTA tugmasi — entitlement check bilan
old_cta = '''                <button
                  onClick={() => router.push("/deep-diagnostic")}
                  className="btn btn-primary"
                >
                  Chuqur tahlilni boshlash
                </button>'''

new_cta = '''                <button
                  onClick={async () => {
                    try {
                      const r = await api.get("/api/v1/entitlements/check", {
                        params: {
                          init_data: getInitData(),
                          entitlement_key: "premium_career_intelligence",
                        },
                      });
                      if (r.data.active) {
                        router.push("/deep-diagnostic");
                      } else {
                        alert("To'lov hali tasdiqlanmagan. Iltimos, admin tasdiqini kuting.");
                      }
                    } catch (err) {
                      alert("Xatolik: " + err);
                    }
                  }}
                  className="btn btn-primary"
                >
                  Chuqur tahlilni boshlash
                </button>'''

if old_cta in p:
    p = p.replace(old_cta, new_cta)
    PREMIUM.write_text(p, encoding="utf-8")
    print("[OK] premium — entitlement check")

# ═══════════════════════════════════════════════════════════
# 4. ADMIN PANEL — dev-grant tugmasi
# ═══════════════════════════════════════════════════════════
ADMIN = Path("qadam-miniapp/app/admin/page.tsx")
a = ADMIN.read_text(encoding="utf-8")

# Import axios for direct call
if "axios" not in a:
    a = a.replace(
        'import { useEffect, useState } from "react";',
        'import { useEffect, useState } from "react";\nimport axios from "axios";\nimport { getInitData } from "@/lib/api";',
    )

# Check if pending payments section exists (from earlier)
if "getPendingPayments" in a:
    # Update to fetch manual payments via simple query
    pass

# Pending payments section — but if it's missing, add it
# Simplified: add a section that lists manual payments and allows grant
if "DEV: Grant Access" not in a:
    # Find Feedbacks heading to insert before
    a = a.replace(
        "      {/* Feedbacks */}",
        '''      {/* DEV: Manual grant section */}
      <ManualGrantSection />

      {/* Feedbacks */}''',
    )
    ADMIN.write_text(a, encoding="utf-8")
    print("[OK] admin panel — ManualGrantSection")

# Add ManualGrantSection component at end of file
if "function ManualGrantSection" not in a:
    a += '''

function ManualGrantSection() {
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const grant = async () => {
    if (!userId) return;
    setLoading(true);
    setMsg(null);
    try {
      const r = await axios.post(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/entitlements/dev-grant`,
        {
          init_data: getInitData(),
          user_id: Number(userId),
          entitlement_key: "premium_career_intelligence",
        }
      );
      setMsg("✅ Entitlement berildi: #" + r.data.entitlement_id);
    } catch (e: any) {
      setMsg("❌ " + (e?.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl p-4 bg-amber-500/10 border border-amber-500/30 mb-5">
      <h3 className="font-semibold text-sm mb-3">🔧 DEV: Premium qo\'lda berish</h3>
      <p className="text-[11px] text-[var(--tg-hint)] mb-3">
        Telegram ID kiriting. Admin sifatida to\'g\'ridan-to\'g\'ri premium beradi.
      </p>
      <div className="flex gap-2">
        <input
          type="number"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="User ID"
          className="flex-1 px-3 py-2 rounded-lg bg-[var(--tg-bg)] border border-[var(--tg-hint)]/20 text-sm"
        />
        <button
          onClick={grant}
          disabled={loading || !userId}
          className="px-4 py-2 rounded-lg bg-amber-500 text-white font-medium text-sm disabled:opacity-50"
        >
          {loading ? "..." : "Berish"}
        </button>
      </div>
      {msg && <p className="text-xs mt-2">{msg}</p>}
    </div>
  );
}
'''
    ADMIN.write_text(a, encoding="utf-8")
    print("[OK] admin — ManualGrantSection component")

print()
print("=" * 60)
print("Fix v4 — TAYYOR!")
print("=" * 60)
print()
print("Tuzatildi:")
print("  • Bot callback — logging + robust")
print("  • /dev-grant endpoint (admin zaxira)")
print("  • /premium → entitlement check")
print("  • Admin panel — Manual grant section")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix v4: admin callback logging + dev grant"')
print("  git push")
print("  Render Manual Deploy (backend + bot, clear cache)")
print("  Vercel auto")
print("  Webhook qayta o'rnatish (bot deploydan keyin)")
print()
print("WEBHOOK URL:")
print("  https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://qadam-bot-rppk.onrender.com/webhook&secret_token=qadam-secret-2026")