# -*- coding: utf-8 -*-
"""Payment v4 — polling fix + manual refresh + debug log."""
from pathlib import Path
import re

TEASER = Path("qadam-miniapp/app/teaser/page.tsx")
t = TEASER.read_text(encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 1. `NodeJS.Timeout` → `ReturnType<typeof setInterval>`
# ═══════════════════════════════════════════════════════════
t = t.replace(
    "const pollRef = useRef<NodeJS.Timeout | null>(null);",
    "const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);",
)

# ═══════════════════════════════════════════════════════════
# 2. State'ga qo'shimcha: lastCheck, checkError
# ═══════════════════════════════════════════════════════════
if "lastCheck" not in t:
    t = t.replace(
        "  const [polling, setPolling] = useState(false);",
        "  const [polling, setPolling] = useState(false);\n  const [lastCheck, setLastCheck] = useState<string>('');\n  const [checkError, setCheckError] = useState<string>('');\n  const [checksCount, setChecksCount] = useState(0);",
    )

# ═══════════════════════════════════════════════════════════
# 3. Polling'ni yangilash — 1 sek, log, error, manual check
# ═══════════════════════════════════════════════════════════
old_polling = '''  // Polling — to'lov tasdiqlanganini tekshirish
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

new_polling = '''  // Polling — to'lov tasdiqlanganini tekshirish (1 sek)
  useEffect(() => {
    if (!polling || !paymentId) return;

    let stopped = false;

    const check = async () => {
      if (stopped) return;
      try {
        const r = await getPaymentStatus(paymentId);
        console.log("[poll]", paymentId, r.status, r.stage2_ready);
        setLastCheck(new Date().toLocaleTimeString("uz"));
        setChecksCount((c) => c + 1);
        setCheckError("");

        if (r.stage2_ready) {
          stopped = true;
          setPolling(false);
          if (pollRef.current) clearInterval(pollRef.current);
          router.push("/stage2");
        }
      } catch (e: any) {
        const msg = e?.response?.data?.detail || e.message;
        console.error("[poll] xato:", msg);
        setCheckError(msg);
      }
    };

    check();
    pollRef.current = setInterval(check, 1000);

    return () => {
      stopped = true;
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [polling, paymentId, router]);

  const manualCheck = async () => {
    if (!paymentId) return;
    try {
      const r = await getPaymentStatus(paymentId);
      console.log("[manual]", r);
      if (r.stage2_ready) {
        setPolling(false);
        router.push("/stage2");
      } else {
        setLastCheck(new Date().toLocaleTimeString("uz"));
        alert(`Holat: ${r.status}`);
      }
    } catch (e: any) {
      alert("Xatolik: " + (e?.response?.data?.detail || e.message));
    }
  };'''

if old_polling in t:
    t = t.replace(old_polling, new_polling)
    print("[OK] polling yangilandi (1 sek + manual + log)")
else:
    print("[!!] polling pattern topilmadi")

# ═══════════════════════════════════════════════════════════
# 4. Done UI'ni yangilash — status ko'rsatish
# ═══════════════════════════════════════════════════════════
old_done_ui = '''                {polling && (
                  <div className="flex items-center justify-center gap-2 mb-4">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="t-small text-primary">
                      Kutilmoqda...
                    </span>
                  </div>
                )}'''

new_done_ui = '''                {polling && (
                  <div className="space-y-3 mb-4">
                    <div className="flex items-center justify-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin text-primary" />
                      <span className="t-small text-primary">
                        Kutilmoqda...
                      </span>
                    </div>
                    <p className="t-caption text-subtle text-center">
                      Tekshiruv: {checksCount} marta
                      {lastCheck && ` · Oxirgi: ${lastCheck}`}
                    </p>
                    {checkError && (
                      <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                        <p className="t-caption text-red-400 text-center">
                          Xato: {checkError}
                        </p>
                      </div>
                    )}
                    <button
                      onClick={manualCheck}
                      className="w-full py-2 rounded-lg border border-[var(--color-border)] t-small text-muted"
                    >
                      Holatni yangilash
                    </button>
                    <button
                      onClick={() => router.push("/stage2")}
                      className="w-full py-2 rounded-lg t-caption text-subtle"
                    >
                      (Test uchun: Stage 2 ga otish)
                    </button>
                  </div>
                )}'''

if old_done_ui in t:
    t = t.replace(old_done_ui, new_done_ui)
    print("[OK] done UI yangilandi")

TEASER.write_text(t, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 5. BACKEND — status endpoint'ga debug log
# ═══════════════════════════════════════════════════════════
PAYMENTS = Path("qadam/backend/api/payments.py")
pay = PAYMENTS.read_text(encoding="utf-8")

# Status endpoint yangilash
pay = pay.replace(
    '''@router.get("/manual/status/{payment_id}")
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
        }''',
    '''@router.get("/manual/status/{payment_id}")
async def manual_status(payment_id: int, init_data: str = Query(...)):
    """Mini App poll qiladi — to'lov tasdiqlanganmi?"""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    async with SessionLocal() as s:
        p = await s.get(Payment, payment_id)
        if not p:
            log.warning(f"status: payment {payment_id} topilmadi")
            raise HTTPException(404, "Payment topilmadi")
        if p.user_id != user["id"]:
            log.warning(f"status: user mismatch {p.user_id} != {user['id']}")
            raise HTTPException(404, "Payment topilmadi")

        stage2_ready = p.status == "paid"
        log.info(f"status poll: id={payment_id} status={p.status} ready={stage2_ready}")

        return {
            "payment_id": p.id,
            "status": p.status,
            "stage2_ready": stage2_ready,
        }''',
)

PAYMENTS.write_text(pay, encoding="utf-8")
print("[OK] backend — status endpoint'ga log qo'shildi")

print()
print("=" * 60)
print("Payment v4 — TAYYOR!")
print("=" * 60)
print()
print("Tuzatildi:")
print("  • NodeJS.Timeout → ReturnType (xato yo'q)")
print("  • Polling: 1 sekund")
print("  • Tekshiruv soni ko'rsatiladi")
print("  • Xato ko'rsatiladi")
print("  • 'Holatni yangilash' tugmasi")
print("  • '(Test: Stage 2 ga otish)' tugmasi")
print("  • Backend log: status poll")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Payment v4: polling fix + debug"')
print("  git push")
print("  Render Manual Deploy (backend)")
print("  Vercel auto")