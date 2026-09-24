# -*- coding: utf-8 -*-
"""QADAM — Mini App close button + auto-close after PDF."""
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# 1. CloseButton.tsx — yangi komponent
# ═══════════════════════════════════════════════════════════
CLOSE = Path("qadam-miniapp/components/CloseButton.tsx")

CLOSE.write_text(r'''"use client";

import { useEffect, useState } from "react";
import { X, ArrowLeft } from "lucide-react";

/**
 * Mini App'ni yopish tugmasi.
 * Faqat Telegram ichida ko'rinadi (brauzerda emas).
 */
export function CloseButton() {
  const [inTelegram, setInTelegram] = useState(false);

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData && tg.initData.length > 10) {
      setInTelegram(true);
    }
  }, []);

  const handleClose = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.close) {
      tg.close();
    } else if (window.history.length > 1) {
      window.history.back();
    } else {
      window.close();
    }
  };

  if (!inTelegram) return null;

  return (
    <div className="mt-8 mb-6 no-print">
      <button
        onClick={handleClose}
        className="w-full flex items-center justify-center gap-2 py-4 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold text-sm shadow-lg hover:opacity-90 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        Yopish va botga qaytish
      </button>
      <p className="text-[10px] text-[var(--tg-hint)] text-center mt-2">
        Hisobotingiz saqlandi
      </p>
    </div>
  );
}
''', encoding="utf-8")
print("[OK] components/CloseButton.tsx")


# ═══════════════════════════════════════════════════════════
# 2. PdfDownloader.tsx — PDF yuklangach auto-close (5 sek)
# ═══════════════════════════════════════════════════════════
PDF_COMP = Path("qadam-miniapp/components/PdfDownloader.tsx")
pdf_code = PDF_COMP.read_text(encoding="utf-8")

# Import'ni qo'shish
if "useEffect" not in pdf_code.split("\n")[2]:
    pdf_code = pdf_code.replace(
        'import { useState } from "react";',
        'import { useState, useEffect, useRef } from "react";',
    )

# Auto-close funksiyasini qo'shish
if "autoCloseTimer" not in pdf_code:
    # handleDownload funksiyasidan oldin qo'shamiz
    pdf_code = pdf_code.replace(
        "  // Print (PDF) tugmasi",
        '''  // Auto-close timer ref
  const autoCloseTimer = useRef<NodeJS.Timeout | null>(null);

  // Print (PDF) tugmasi''',
    )

    # window.onafterprint — auto-close qo'shish
    pdf_code = pdf_code.replace(
        "    // Print\n    setTimeout(() => {\n      window.print();\n    }, 150);",
        '''    // Print
    setTimeout(() => {
      window.print();

      // PDF saqlangandan keyin auto-close (10 sek kutish)
      const tg = (window as any).Telegram?.WebApp;
      if (tg?.close && tg?.initData && tg.initData.length > 10) {
        // Toast ko'rsatish
        const toast = document.createElement("div");
        toast.textContent = "✓ PDF tayyor. 10 sekunddan keyin botga qaytasiz...";
        toast.style.cssText = `
          position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
          background: #10b981; color: white; padding: 12px 24px; border-radius: 12px;
          font-size: 13px; z-index: 9999; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
          font-family: -apple-system, sans-serif; max-width: 90%; text-align: center;
        `;
        document.body.appendChild(toast);

        // 10 sek o'tib yopiladi
        autoCloseTimer.current = setTimeout(() => {
          toast.remove();
          tg.close();
        }, 10000);
      }
    }, 150);''',
    )

    # Cleanup
    pdf_code = pdf_code.replace(
        "  return (\n    <>",
        '''  // Cleanup
  useEffect(() => {
    return () => {
      if (autoCloseTimer.current) clearTimeout(autoCloseTimer.current);
    };
  }, []);

  return (
    <>''',
        1,
    )

PDF_COMP.write_text(pdf_code, encoding="utf-8")
print("[OK] components/PdfDownloader.tsx — auto-close")


# ═══════════════════════════════════════════════════════════
# 3. Report sahifasiga CloseButton qo'shish
# ═══════════════════════════════════════════════════════════
REPORT = Path("qadam-miniapp/app/report/[id]/page.tsx")
rep = REPORT.read_text(encoding="utf-8")

# Import
if "CloseButton" not in rep:
    rep = rep.replace(
        'import { PdfDownloader } from "@/components/PdfDownloader";',
        'import { PdfDownloader } from "@/components/PdfDownloader";\nimport { CloseButton } from "@/components/CloseButton";',
    )

# PDF tugmasidan keyin CloseButton
old_block = '''      <div className="mt-6">
        <PdfDownloader reportId={Number(id)} />
      </div>'''

new_block = '''      <div className="mt-6">
        <PdfDownloader reportId={Number(id)} />
      </div>

      <CloseButton />'''

if old_block in rep:
    rep = rep.replace(old_block, new_block)
    print("[OK] report/page.tsx — CloseButton qo'shildi")
else:
    print("[SKIP] report/page.tsx — block topilmadi (allaqachon bor)")

REPORT.write_text(rep, encoding="utf-8")


print()
print("=" * 60)
print("Close fix — tayyor!")
print("=" * 60)
print()
print("Endi:")
print("  1. Report sahifasining oxirida 'Yopish' tugmasi")
print("  2. PDF yuklangach 10 sek o'tib avtomatik yopiladi")
print("  3. Toast xabar: '✓ PDF tayyor. 10 sekunddan keyin botga qaytasiz...'")
print()
print("Keyingi: git push")