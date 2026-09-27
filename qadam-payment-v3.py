# -*- coding: utf-8 -*-
"""To'lov statusi polling + reliability."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. BACKEND — status endpoint qo'shish
# ═══════════════════════════════════════════════════════════
PAYMENTS = Path("qadam/backend/api/payments.py")
pay = PAYMENTS.read_text(encoding="utf-8")

if "/manual/status" not in pay:
    STATUS_ENDPOINT = '''

@router.get("/manual/status/{payment_id}")
async def manual_status(payment_id: int, init_data: str = Query(...)):
    """Mini App poll qiladi — to'lov tasdiqlanganmi?"""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p or p.user_id != user["id"]:
            raise HTTPException(404, "Payment topilmadi")

        stage2_ready = p.status == "paid"

        return {
            "payment_id": p.id,
            "status": p.status,
            "stage2_ready": stage2_ready,
        }
'''
    PAYMENTS.write_text(pay + STATUS_ENDPOINT, encoding="utf-8")
    print("[OK] backend — /manual/status endpoint")
else:
    print("[SKIP] backend — allaqachon bor")

# ═══════════════════════════════════════════════════════════
# 2. BOT callback — DB error handling + log
# ═══════════════════════════════════════════════════════════
BOT_PAY = Path("qadam/bot/handlers/payment.py")
bot_pay = BOT_PAY.read_text(encoding="utf-8")

# Eski callback'larni olib tashlash
import re
bot_pay = re.sub(
    r'# ═+\s*MANUAL TO.*$',
    '',
    bot_pay,
    flags=re.DOTALL,
)

NEW_CALLBACKS = '''

# ═══════════════════════════════════════════════════════════════════
# MANUAL TO'LOV — admin tasdiqlash v3 (reliable)
# ═══════════════════════════════════════════════════════════════════

import os as _os
import logging as _log

_logger = _log.getLogger("qadam.bot.payment")


def _is_admin(user_id: int) -> bool:
    ids = set(
        int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip()
    )
    return user_id in ids


@router.callback_query(F.data.startswith("pay:approve:"))
async def cb_approve(callback: CallbackQuery):
    _logger.info(f"cb_approve: from={callback.from_user.id} data={callback.data}")

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
        from backend.models import Payment, TestResult

        user_id = None
        async with SessionLocal() as s:
            p = await s.get(Payment, payment_id)
            if not p:
                _logger.error(f"Payment {payment_id} topilmadi")
                await callback.message.edit_caption(
                    caption=(callback.message.caption or "") + "\\n\\n⚠️ Payment topilmadi",
                )
                return

            p.status = "paid"
            s1 = await s.get(TestResult, p.stage1_result_id)
            if s1:
                s1.paid = True
            await s.commit()
            user_id = p.user_id

        _logger.info(f"Payment {payment_id} paid, user={user_id}")

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
                _logger.info(f"User {user_id} ga xabar yuborildi")
            except Exception as e:
                _logger.error(f"User xabar xato: {e}")

        # Admin xabarni yangilash
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
    _logger.info(f"cb_reject: from={callback.from_user.id} data={callback.data}")

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

    except Exception as e:
        _logger.error(f"cb_reject xato: {e}")
'''

BOT_PAY.write_text(bot_pay + NEW_CALLBACKS, encoding="utf-8")
print("[OK] bot/handlers/payment.py — callback v3 (log bilan)")

# ═══════════════════════════════════════════════════════════
# 3. api.ts — status polling
# ═══════════════════════════════════════════════════════════
API = Path("qadam-miniapp/lib/api.ts")
api = API.read_text(encoding="utf-8")

if "getPaymentStatus" not in api:
    api += '''

export async function getPaymentStatus(payment_id: number) {
  const r = await api.get(`/payments/manual/status/${payment_id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}
'''
    API.write_text(api, encoding="utf-8")
    print("[OK] api.ts — getPaymentStatus")

# ═══════════════════════════════════════════════════════════
# 4. TEASER — payment_id saqlash + polling
# ═══════════════════════════════════════════════════════════
TEASER = Path("qadam-miniapp/app/teaser/page.tsx")
teaser = TEASER.read_text(encoding="utf-8")

# Import
if "getPaymentStatus" not in teaser:
    teaser = teaser.replace(
        'import { getCardInfo, uploadPaymentScreenshot } from "@/lib/api";',
        'import { getCardInfo, uploadPaymentScreenshot, getPaymentStatus } from "@/lib/api";',
    )

# State qo'shish — useEffect va useRef bor
if "paymentId" not in teaser:
    teaser = teaser.replace(
        "  const fileRef = useRef<HTMLInputElement>(null);",
        "  const fileRef = useRef<HTMLInputElement>(null);\n  const [paymentId, setPaymentId] = useState<number | null>(null);\n  const [polling, setPolling] = useState(false);\n  const pollRef = useRef<NodeJS.Timeout | null>(null);",
    )

# handleSubmit'ni yangilash — payment_id saqlash + polling boshlash
old_submit = '''  const handleSubmit = async () => {
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
  };'''

new_submit = '''  const handleSubmit = async () => {
    if (!file || !stage1ResultId) return;
    setUploading(true);
    try {
      const res = await uploadPaymentScreenshot(stage1ResultId, file);
      setPaymentId(res.payment_id);
      setDone(true);
      setPolling(true);
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    } finally {
      setUploading(false);
    }
  };

  // Polling — to'lov tasdiqlanganini tekshirish
  useEffect(() => {
    if (!polling || !paymentId) return;

    const check = async () => {
      try {
        const r = await getPaymentStatus(paymentId);
        if (r.stage2_ready) {
          setPolling(false);
          router.push("/stage2");
        }
      } catch (e) {
        console.log("Status xato:", e);
      }
    };

    check();
    pollRef.current = setInterval(check, 3000);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [polling, paymentId, router]);'''

if old_submit in teaser:
    teaser = teaser.replace(old_submit, new_submit)
    print("[OK] teaser — polling qo'shildi")
else:
    print("[!!] teaser — pattern topilmadi")

# "done" holatidagi matnni yangilash
teaser = teaser.replace(
    '''                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin tekshirib, tasdiqlagach sizga avtomatik xabar keladi.
                  Shundan song chuqur tahlil ochiladi.
                </p>''',
    '''                <h3 className="t-heading mb-2">
                  {polling ? "Tekshirilmoqda..." : "Skrinshot yuborildi"}
                </h3>
                <p className="t-small text-muted mb-6">
                  {polling
                    ? "Admin tekshirmoqda. Tasdiqlanganda avtomatik Stage 2 ga otasiz."
                    : "Admin tekshirib, tasdiqlagach sizga avtomatik xabar keladi."}
                </p>
                {polling && (
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="t-small text-primary">
                      Kutilmoqda...
                    </span>
                  </div>
                )}''',
)

TEASER.write_text(teaser, encoding="utf-8")
print("[OK] teaser — xabar yangilandi")

print()
print("=" * 60)
print("Payment v3 — TAYYOR!")
print("=" * 60)
print()
print("YANGI:")
print("  • Mini App poll qiladi (har 3 sek)")
print("  • Admin tasdiqlaganda → user avtomatik Stage 2 ga otadi")
print("  • Bot callback log bilan (debug oson)")
print("  • /manual/status endpoint")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Payment v3: polling + logging"')
print("  git push")
print("  Render Manual Deploy (backend + bot)")