# -*- coding: utf-8 -*-
"""Admin page.tsx — getPendingPayments/approvePayment olib tashlash."""
from pathlib import Path

ADMIN = Path("qadam-miniapp/app/admin/page.tsx")
ap = ADMIN.read_text(encoding="utf-8")

# 1. Import'dan olib tashlash
ap = ap.replace(
    "  getAdminFeedbacks,\n  getPendingPayments,\n  approvePayment,\n} from \"@/lib/api\";",
    "  getAdminFeedbacks,\n} from \"@/lib/api\";",
)

# 2. Pending state olib tashlash
ap = ap.replace(
    "  const [feedbacks, setFeedbacks] = useState<any[]>([]);\n  const [pending, setPending] = useState<any[]>([]);",
    "  const [feedbacks, setFeedbacks] = useState<any[]>([]);",
)

# 3. Promise.all'da getPendingPayments olib tashlash
ap = ap.replace(
    "      const [ov, dl, tc, fb, pd] = await Promise.all([\n        getAdminOverview(),\n        getAdminDaily(30),\n        getAdminTopCareers(15),\n        getAdminFeedbacks(30),\n        getPendingPayments().catch(() => ({ payments: [] })),\n      ]);",
    "      const [ov, dl, tc, fb] = await Promise.all([\n        getAdminOverview(),\n        getAdminDaily(30),\n        getAdminTopCareers(15),\n        getAdminFeedbacks(30),\n      ]);",
)

# 4. setPending olib tashlash
ap = ap.replace(
    "      setFeedbacks(fb.feedbacks || []);\n      setPending(pd.payments || []);",
    "      setFeedbacks(fb.feedbacks || []);",
)

# 5. PENDING PAYMENTS UI blokni olib tashlash
import re
ap = re.sub(
    r'\{/\* ═══ PENDING PAYMENTS ═══ \*/\}.*?\{/\* Feedbacks \*/\}',
    '{/* Feedbacks */}',
    ap,
    flags=re.DOTALL,
)

ADMIN.write_text(ap, encoding="utf-8")
print("[OK] admin/page.tsx — tozalandi")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Fix: admin page imports"')
print("  git push")