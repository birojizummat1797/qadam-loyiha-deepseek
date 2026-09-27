# -*- coding: utf-8 -*-
"""Fix v5 — admin tasdiqlash: callback + TEXT COMMANDS (fallback)."""
from pathlib import Path
import re

BOT = Path("qadam/bot")

# ═══════════════════════════════════════════════════════════
# 1. bot/main.py — payment_router aniq ulash + log
# ═══════════════════════════════════════════════════════════
MAIN = BOT / "main.py"
m = MAIN.read_text(encoding="utf-8")

# payment_router import bo'lishini ta'minlash
if "from bot.handlers.payment import" not in m:
    m = m.replace(
        "from bot.handlers import start as start_handlers",
        "from bot.handlers import start as start_handlers\n"
        "from bot.handlers.payment import router as payment_router",
    )

# include_router ni tekshirish
if "payment_router" not in m.split("dp.include_router")[0] or "dp.include_router(payment_router)" not in m:
    # include qatorini qo'shish
    if "dp.include_router(start_handlers.router)" in m:
        m = m.replace(
            "dp.include_router(start_handlers.router)",
            "dp.include_router(start_handlers.router)\n"
            "dp.include_router(payment_router)",
        )

# Log qo'shish — on_startup'da
if "_log.info(\"payment_router ulandi\")" not in m:
    m = m.replace(
        "dp.include_router(payment_router)",
        'dp.include_router(payment_router)\nlog.info("payment_router ulandi")',
        1,
    )

MAIN.write_text(m, encoding="utf-8")
print("[OK] bot/main.py — payment_router ulandi")

# ═══════════════════════════════════════════════════════════
# 2. payment.py — TEXT commands (/approve, /reject) qo'shish
# ═══════════════════════════════════════════════════════════
PAY = BOT / "handlers/payment.py"
p = PAY.read_text(encoding="utf-8")

# Eski text-command handler'larni olib tashlash (agar bor bo'lsa)
p = re.sub(
    r'# ═+\s*TEXT COMMANDS.*$',
    '',
    p,
    flags=re.DOTALL,
)

# Command import tekshirish
if "from aiogram.filters import Command" not in p:
    p = p.replace(
        "from aiogram import Router, F",
        "from aiogram import Router, F\nfrom aiogram.filters import Command",
    )

# File boshiga is_admin funksiyasi (agar yo'q bo'lsa)
if "def _is_admin" not in p:
    p = p.replace(
        "router = Router()",
        '''router = Router()


def _is_admin(uid: int) -> bool:
    import os as _os
    ids = set(int(x.strip()) for x in _os.getenv("ADMIN_IDS", "").split(",") if x.strip())
    return uid in ids
''',
        1,
    )

TEXT_COMMANDS = '''

# ═══════════════════════════════════════════════════════════════════
# TEXT COMMANDS — fallback (agar tugmalar ishlamasa)
# ═══════════════════════════════════════════════════════════════════

from aiogram.types import Message as _Message


async def _approve_impl(payment_id: int) -> dict:
    """Tasdiqlash logikasi."""
    from backend.db import SessionLocal
    from backend.models import Payment
    from backend.services.entitlement_service import grant_entitlement

    user_id = None
    async with SessionLocal() as s:
        pay = await s.get(Payment, payment_id)
        if not pay:
            return {"ok": False, "error": f"Payment #{payment_id} topilmadi"}
        pay.status = "paid"
        await s.commit()
        user_id = pay.user_id

    await grant_entitlement(
        user_id=user_id,
        entitlement_key="premium_career_intelligence",
        source="manual_card",
        payment_reference=str(payment_id),
    )
    return {"ok": True, "user_id": user_id}


async def _reject_impl(payment_id: int) -> dict:
    from backend.db import SessionLocal
    from backend.models import Payment

    user_id = None
    async with SessionLocal() as s:
        pay = await s.get(Payment, payment_id)
        if not pay:
            return {"ok": False, "error": f"Payment #{payment_id} topilmadi"}
        pay.status = "rejected"
        await s.commit()
        user_id = pay.user_id

    return {"ok": True, "user_id": user_id}


@router.message(Command("approve"))
async def cmd_approve(m: _Message):
    """Admin: /approve <payment_id> — to'lovni tasdiqlash."""
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    parts = (m.text or "").split()
    if len(parts) < 2:
        await m.answer("Format: /approve <payment_id>\\nMisol: /approve 5")
        return

    try:
        pid = int(parts[1])
    except ValueError:
        await m.answer("payment_id raqam bo'lishi kerak")
        return

    result = await _approve_impl(pid)
    if not result["ok"]:
        await m.answer(f"❌ {result['error']}")
        return

    await m.answer(f"✅ Payment #{pid} tasdiqlandi (user: {result['user_id']})")

    # Userga xabar
    try:
        from aiogram.types import (
            InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
        )
        import os as _os
        webapp = _os.getenv("WEBAPP_URL", "")
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🎯 Chuqur tahlilni boshlash",
                web_app=WebAppInfo(url=f"{webapp}/deep-diagnostic"),
            )
        ]])
        await m.bot.send_message(
            result["user_id"],
            "✅ <b>To'lovingiz tasdiqlandi!</b>\\n\\n"
            "Chuqur tahlilni boshlashingiz mumkin.",
            reply_markup=kb,
        )
    except Exception as e:
        import logging
        logging.error(f"User xabar xato: {e}")


@router.message(Command("reject"))
async def cmd_reject(m: _Message):
    """Admin: /reject <payment_id> — to'lovni rad etish."""
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    parts = (m.text or "").split()
    if len(parts) < 2:
        await m.answer("Format: /reject <payment_id>")
        return

    try:
        pid = int(parts[1])
    except ValueError:
        await m.answer("payment_id raqam bo'lishi kerak")
        return

    result = await _reject_impl(pid)
    if not result["ok"]:
        await m.answer(f"❌ {result['error']}")
        return

    await m.answer(f"❌ Payment #{pid} rad etildi")

    try:
        await m.bot.send_message(
            result["user_id"],
            "❌ <b>To'lov tasdiqlanmadi</b>\\n\\n"
            "Skrinshot aniq emas yoki to'lov topilmadi.",
        )
    except Exception:
        pass


@router.message(Command("pending"))
async def cmd_pending(m: _Message):
    """Admin: /pending — kutilayotgan to'lovlar."""
    if not _is_admin(m.from_user.id):
        await m.answer("Ruxsat yo'q")
        return

    from backend.db import SessionLocal
    from backend.models import Payment
    from sqlalchemy import select, desc

    async with SessionLocal() as s:
        rows = (await s.execute(
            select(Payment)
            .where(Payment.status == "pending")
            .order_by(desc(Payment.created_at))
            .limit(10)
        )).scalars().all()

    if not rows:
        await m.answer("Kutilayotgan to'lovlar yo'q")
        return

    text = "<b>Kutilayotgan to'lovlar:</b>\\n\\n"
    for r in rows:
        text += (
            f"🎫 #{r.id} — user <code>{r.user_id}</code>\\n"
            f"💰 {r.amount_uzs:,} so'm\\n"
            f"✅ /approve {r.id}\\n"
            f"❌ /reject {r.id}\\n\\n"
        )
    await m.answer(text)


# ═══════════════════════════════════════════════════════════════════
# CATCH-ALL callback logger (debug uchun)
# ═══════════════════════════════════════════════════════════════════

@router.callback_query()
async def cb_catch_all(callback):
    """Har qanday callback — log qilish (hech qaysi handler tutmasa)."""
    import logging
    logging.getLogger("qadam.bot.payment").warning(
        f"UNHANDLED callback: data={callback.data!r} from={callback.from_user.id}"
    )
    try:
        await callback.answer(f"Handler topilmadi: {callback.data}", show_alert=True)
    except Exception:
        pass
'''

PAY.write_text(p.rstrip() + TEXT_COMMANDS, encoding="utf-8")
print("[OK] bot/handlers/payment.py — /approve, /reject, /pending + catch-all")

# ═══════════════════════════════════════════════════════════
# 3. Bot commands ro'yxatiga qo'shish
# ═══════════════════════════════════════════════════════════
m = MAIN.read_text(encoding="utf-8")

if 'BotCommand(command="approve"' not in m:
    m = m.replace(
        'BotCommand(command="help", description="Yordam"),',
        'BotCommand(command="help", description="Yordam"),\n'
        '            BotCommand(command="pending", description="Kutilayotgan to\'lovlar"),\n'
        '            BotCommand(command="approve", description="To\'lovni tasdiqlash"),\n'
        '            BotCommand(command="reject", description="To\'lovni rad etish"),',
    )
    MAIN.write_text(m, encoding="utf-8")
    print("[OK] bot/main.py — commands ro'yxati")

print()
print("=" * 60)
print("Fix v5 — TAYYOR!")
print("=" * 60)
print()
print("YANGI matn buyruqlar (agar tugmalar ishlamasa):")
print("  /pending         — kutilayotgan to'lovlar ro'yxati")
print("  /approve <id>    — to'lovni tasdiqlash")
print("  /reject <id>     — to'lovni rad etish")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix v5: text commands for admin approve/reject"')
print("  git push")
print("  Render Manual Deploy (bot, clear cache)")
print("  Webhook qayta o'rnatish")