"use client";

import { useEffect } from "react";

export function TmaProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const initTMA = async () => {
      try {
        const sdk = await import("@tma.js/sdk");
        if (sdk.init) sdk.init();
        if (sdk.miniApp) {
          sdk.miniApp.ready();
          sdk.miniApp.expand();
        }
        if (sdk.themeParams && sdk.themeParams.bindCssVars) {
          sdk.themeParams.bindCssVars();
        }
      } catch (e) {
        // TMA ishlamasa - brauzer rejimida davom
        console.log("TMA init skipped:", e);
      }
    };
    initTMA();
  }, []);

  return <>{children}</>;
}
