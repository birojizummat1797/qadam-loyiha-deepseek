"use client";

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
