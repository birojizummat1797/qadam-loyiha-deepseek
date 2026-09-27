"use client";

import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";

export function CloseButton() {
  const [inTelegram, setInTelegram] = useState(false);

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.initData && tg.initData.length > 10) setInTelegram(true);
  }, []);

  const handleClose = () => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg?.close) tg.close();
    else if (window.history.length > 1) window.history.back();
    else window.close();
  };

  if (!inTelegram) return null;

  return (
    <div className="mt-6 mb-2 no-print">
      <button onClick={handleClose} className="btn btn-secondary">
        <ArrowLeft className="w-4 h-4" />
        <span>Botga qaytish</span>
      </button>
      <p className="t-caption text-subtle text-center mt-3">
        Hisobotingiz saqlandi
      </p>
    </div>
  );
}
