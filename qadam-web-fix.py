# -*- coding: utf-8 -*-
"""QADAM Web fix — @tma.js/sdk ni olib tashlab, window.Telegram.WebApp ga o'tish."""
from pathlib import Path

ROOT = Path("qadam-miniapp")

FILES = {}

# ═══ 1. package.json ═══
FILES["package.json"] = """{
  "name": "qadam-miniapp",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "axios": "^1.7.9",
    "framer-motion": "^11.15.0",
    "lucide-react": "^0.469.0",
    "next": "15.1.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "zustand": "^5.0.2"
  },
  "devDependencies": {
    "@types/node": "^22.10.2",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.7.2"
  }
}
"""

# ═══ 2. layout.tsx ═══
FILES["app/layout.tsx"] = '''import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "QADAM - Kasb yonaltiruvchi tahlil",
  description: "Sizga mos kasb va sohani toping",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#0a0a0f",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uz">
      <head>
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
'''

# ═══ 3. TmaProvider.tsx ═══
FILES["components/TmaProvider.tsx"] = '''"use client";

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
'''

# ═══ 4. lib/api.ts ═══
FILES["lib/api.ts"] = '''import axios from "axios";

const BACKEND =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BACKEND });

export function getInitData(): string {
  if (typeof window === "undefined") return "";
  const tg = (window as any).Telegram?.WebApp;
  return tg?.initData || "";
}

export async function fetchQuestions() {
  const r = await api.get("/diagnostic/questions");
  return r.data;
}

export async function submitStage1(answers: Record<string, any>) {
  const r = await api.post("/diagnostic/stage1", {
    init_data: getInitData(),
    answers,
  });
  return r.data;
}

export async function submitStage2(
  stage1_result_id: number,
  answers: Record<string, any>
) {
  const r = await api.post("/diagnostic/stage2", {
    init_data: getInitData(),
    answers,
    stage1_result_id,
  });
  return r.data;
}

export async function fetchReport(id: number) {
  const r = await api.get(`/diagnostic/report/${id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function createPayment(
  stage1_result_id: number,
  provider: string
) {
  const r = await api.post("/payments/create", {
    init_data: getInitData(),
    stage1_result_id,
    provider,
  });
  return r.data;
}

export async function createStarsInvoice(stage1_result_id: number) {
  const r = await api.post("/payments/stars/invoice", {
    init_data: getInitData(),
    stage1_result_id,
    provider: "stars",
  });
  return r.data;
}

export async function checkPaid(stage1_result_id: number) {
  const r = await api.get(`/payments/check/${stage1_result_id}`, {
    params: { init_data: getInitData() },
  });
  return r.data;
}

export async function devUnlock(stage1_result_id: number) {
  const r = await api.post("/diagnostic/dev-unlock", {
    init_data: getInitData(),
    stage1_result_id,
  });
  return r.data;
}
'''

# ═══ 5. .npmrc ═══
FILES[".npmrc"] = "legacy-peer-deps=true\n"

# ═══ 6. globals.css — tekshirish va kerak bo'lsa yozish ═══
GLOBALS = ROOT / "app" / "globals.css"
if not GLOBALS.exists():
    FILES["app/globals.css"] = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --tg-bg: var(--tg-theme-bg-color, #0a0a0f);
  --tg-text: var(--tg-theme-text-color, #f5f5f7);
  --tg-hint: var(--tg-theme-hint-color, #9a9aa8);
  --tg-link: var(--tg-theme-link-color, #6366f1);
  --tg-button: var(--tg-theme-button-color, #6366f1);
  --tg-button-text: var(--tg-theme-button-text-color, #ffffff);
  --tg-secondary-bg: var(--tg-theme-secondary-bg-color, #13131a);
}

html, body {
  background: var(--tg-bg);
  color: var(--tg-text);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.btn-primary {
  background: var(--tg-button);
  color: var(--tg-button-text);
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  transition: opacity 0.15s;
  border: none;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.card {
  background: var(--tg-secondary-bg);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 12px;
}

.gradient-text {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
"""


def main():
    print("=" * 60)
    print("QADAM Web fix: fayllar qayta yozilmoqda")
    print("=" * 60)
    for path, content in FILES.items():
        full = ROOT / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] qadam-miniapp/" + path)
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yozildi!")

    # Tekshirish
    print()
    print("Tekshirish:")
    must_have = [
        "package.json",
        "app/layout.tsx",
        "app/globals.css",
        "components/TmaProvider.tsx",
        "lib/api.ts",
        ".npmrc",
    ]
    for p in must_have:
        full = ROOT / p
        if full.exists():
            size = full.stat().st_size
            print("  [OK] " + p + " (" + str(size) + " bayt)")
        else:
            print("  [YO'Q] " + p)


if __name__ == "__main__":
    main()