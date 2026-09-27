# -*- coding: utf-8 -*-
"""Payment v5 — polling olib tashlash, sodda va ishonchli."""
from pathlib import Path
import re

TEASER = Path("qadam-miniapp/app/teaser/page.tsx")
t = TEASER.read_text(encoding="utf-8")

# 1. Polling useEffect'ni butunlay olib tashlash
t = re.sub(
    r'  // Polling — to\'lov tasdiqlanganini tekshirish.*?\}, \[polling, paymentId, router\]\);\n',
    '',
    t,
    flags=re.DOTALL,
)

# 2. manualCheck funksiyasini olib tashlash
t = re.sub(
    r'  const manualCheck = async \(\) => \{.*?\n  \};\n',
    '',
    t,
    flags=re.DOTALL,
)

# 3. Polling state'larni olib tashlash
t = t.replace(
    "  const [polling, setPolling] = useState(false);\n  const [lastCheck, setLastCheck] = useState<string>('');\n  const [checkError, setCheckError] = useState<string>('');\n  const [checksCount, setChecksCount] = useState(0);",
    "",
)
t = t.replace(
    "  const [polling, setPolling] = useState(false);\n  const [lastCheck, setLastCheck] = useState<string>('');\n  const [checkError, setCheckError] = useState<string>('');\n  const [checksCount, setChecksCount] = useState(0);\n  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);",
    "",
)
t = t.replace(
    "  const [paymentId, setPaymentId] = useState<number | null>(null);\n  const [polling, setPolling] = useState(false);",
    "  const [paymentId, setPaymentId] = useState<number | null>(null);",
)

# 4. handleSubmit — polling boshlash olib tashlash
t = t.replace(
    "      const res = await uploadPaymentScreenshot(stage1ResultId, file);\n      setPaymentId(res.payment_id);\n      setDone(true);\n      setPolling(true);",
    "      const res = await uploadPaymentScreenshot(stage1ResultId, file);\n      setPaymentId(res.payment_id);\n      setDone(true);",
)

# 5. Done UI — polling blokini olib tashlash, "Botga qaytish" qo'shish
t = re.sub(
    r'                \{polling && \(.*?\n                \)\}',
    '',
    t,
    flags=re.DOTALL,
)

# 6. "Skrinshot yuborildi" xabarini yangilash
t = t.replace(
    '''                <h3 className="t-heading mb-2">
                  {polling ? "Tekshirilmoqda..." : "Skrinshot yuborildi"}
                </h3>
                <p className="t-small text-muted mb-6">
                  {polling
                    ? "Admin tekshirmoqda. Tasdiqlanganda avtomatik Stage 2 ga otasiz."
                    : "Admin tekshirib, tasdiqlagach sizga avtomatik xabar keladi."}
                </p>''',
    '''                <h3 className="t-heading mb-2">Skrinshot yuborildi</h3>
                <p className="t-small text-muted mb-6">
                  Admin tekshiradi va <b className="text-text">5-10 daqiqa</b> ichida
                  sizga Telegram bot orqali xabar yuboriladi.
                  Xabardagi tugma orqali chuqur tahlilga o'tasiz.
                </p>''',
)

# 7. "Yopish" tugmasini "Botga qaytish" qilib o'zgartirish
old_close = '''                <button
                  onClick={() => {
                    setOpenPay(false);
                    setFile(null);
                    setPreview(null);
                    setDone(false);
                  }}
                  className="btn btn-primary"
                >
                  Yopish
                </button>'''

new_close = '''                <a
                  href={`https://t.me/${(window as any).Telegram?.WebApp?.initDataUnsafe?.user?.username ? "kelajakkailkqadam_bot" : "kelajakkailkqadam_bot"}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary block text-center"
                  onClick={() => {
                    setTimeout(() => {
                      (window as any).Telegram?.WebApp?.close?.();
                    }, 300);
                  }}
                >
                  Botga qaytish
                </a>
                <button
                  onClick={() => {
                    setOpenPay(false);
                    setFile(null);
                    setPreview(null);
                    setDone(false);
                  }}
                  className="btn btn-ghost mt-2"
                >
                  Yopish
                </button>'''

t = t.replace(old_close, new_close)

# 8. useEffect'da getPaymentStatus import olib tashlash (endi kerakmas)
t = t.replace(
    'import { getCardInfo, uploadPaymentScreenshot, getPaymentStatus } from "@/lib/api";',
    'import { getCardInfo, uploadPaymentScreenshot } from "@/lib/api";',
)

TEASER.write_text(t, encoding="utf-8")
print("[OK] teaser — polling olib tashlandi")

# ═══════════════════════════════════════════════════════════
# Backend — status endpoint saqlanadi (kelajakda kerak bo'lishi mumkin)
# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("Payment v5 — TAYYOR!")
print("=" * 60)
print()
print("YANGI OQIM:")
print("  1. User screenshot yuboradi")
print("  2. Modal: 'Skrinshot yuborildi. 5-10 daqiqa ichida xabar keladi.'")
print("  3. User 'Botga qaytish' bosadi → Mini App yopiladi")
print("  4. Admin bot'da [Tasdiqlash] bosadi")
print("  5. User bot'da xabar oladi: 'Tasdiqlandi!' + [Stage 2 havola]")
print("  6. User havolani bosadi → Stage 2 ochiladi")
print()
print("Polling YO'Q = Network Error YO'Q")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Payment v5: remove polling, bot notification only"')
print("  git push")
print("  Vercel auto")