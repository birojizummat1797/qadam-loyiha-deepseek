"use client";

import { useEffect } from "react";

export function TmaProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg) {
      console.log("Telegram WebApp topilmadi (brauzer rejimi)");
      return;
    }
    try {
      tg.ready();
      tg.expand();
      if (tg.setHeaderColor) tg.setHeaderColor("#0a0a0f");
      if (tg.setBackgroundColor) tg.setBackgroundColor("#0a0a0f");
    } catch (e) {
      console.log("TMA init xatosi:", e);
    }
  }, []);

  return <>{children}</>;
}