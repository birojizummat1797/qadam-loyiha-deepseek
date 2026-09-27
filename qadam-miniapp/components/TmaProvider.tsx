"use client";

import { useEffect } from "react";

export function TmaProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg) return;

    try {
      tg.ready();
      tg.expand();
      if (tg.setHeaderColor) tg.setHeaderColor("#0A0A0F");
      if (tg.setBackgroundColor) tg.setBackgroundColor("#0A0A0F");
    } catch (e) {
      console.log("TMA init:", e);
    }
  }, []);

  return <>{children}</>;
}
