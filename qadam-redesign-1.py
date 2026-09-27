# -*- coding: utf-8 -*-
"""Qadam.io — Redesign v3: Design System + Welcome (minimal, premium)."""
from pathlib import Path

FRONTEND = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. globals.css — Design tokens
# ═══════════════════════════════════════════════════════════
GLOBALS = FRONTEND / "app/globals.css"

GLOBALS.write_text(r'''@tailwind base;
@tailwind components;
@tailwind utilities;

/* ═══════════════════════════════════════════════════════════
   QADAM.IO — DESIGN TOKENS
   Professional, minimal, premium
   ═══════════════════════════════════════════════════════════ */

:root {
  /* ─── Background & Surface (Dark default) ─── */
  --color-bg: #0A0A0F;
  --color-surface: #14141A;
  --color-surface-2: #1C1C24;
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-strong: rgba(255, 255, 255, 0.16);

  /* ─── Text ─── */
  --color-text: #F5F5F7;
  --color-text-muted: #8A8A95;
  --color-text-subtle: #5A5A65;

  /* ─── Brand ─── */
  --color-primary: #6366F1;
  --color-primary-hover: #7C7FF2;
  --color-primary-soft: rgba(99, 102, 241, 0.12);

  /* ─── Semantic ─── */
  --color-success: #10B981;
  --color-success-soft: rgba(16, 185, 129, 0.12);
  --color-warning: #F59E0B;
  --color-warning-soft: rgba(245, 158, 11, 0.12);
  --color-danger: #EF4444;
  --color-danger-soft: rgba(239, 68, 68, 0.12);

  /* ─── Spacing ─── */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;

  /* ─── Radius ─── */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* ─── Motion ─── */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --duration-slow: 400ms;
}

/* ═══════════════════════════════════════════════════════════
   LIGHT MODE
   ═══════════════════════════════════════════════════════════ */
body[data-theme="light"] {
  --color-bg: #FFFFFF;
  --color-surface: #FAFAFB;
  --color-surface-2: #F4F4F6;
  --color-border: rgba(0, 0, 0, 0.08);
  --color-border-strong: rgba(0, 0, 0, 0.16);

  --color-text: #0A0A0F;
  --color-text-muted: #6B7280;
  --color-text-subtle: #9CA3AF;

  --color-primary: #4F46E5;
  --color-primary-hover: #4338CA;
  --color-primary-soft: rgba(79, 70, 229, 0.08);
}

/* ═══════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════ */
* {
  box-sizing: border-box;
}

html, body {
  background: var(--color-bg);
  color: var(--color-text);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-feature-settings: "cv02", "cv03", "cv04", "cv11";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

body {
  overflow-x: hidden;
}

/* ═══════════════════════════════════════════════════════════
   TYPOGRAPHY
   ═══════════════════════════════════════════════════════════ */
.t-display {
  font-size: 32px;
  line-height: 1.15;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.t-title {
  font-size: 22px;
  line-height: 1.25;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.t-heading {
  font-size: 17px;
  line-height: 1.35;
  font-weight: 600;
  letter-spacing: -0.005em;
}

.t-body {
  font-size: 15px;
  line-height: 1.55;
  font-weight: 400;
}

.t-small {
  font-size: 13px;
  line-height: 1.5;
  font-weight: 400;
}

.t-caption {
  font-size: 11px;
  line-height: 1.4;
  font-weight: 500;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.t-metric {
  font-size: 40px;
  line-height: 1;
  font-weight: 700;
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
}

/* ═══════════════════════════════════════════════════════════
   UTILITY
   ═══════════════════════════════════════════════════════════ */
.text-muted { color: var(--color-text-muted); }
.text-subtle { color: var(--color-text-subtle); }
.text-primary { color: var(--color-primary); }

.bg-surface { background: var(--color-surface); }
.bg-surface-2 { background: var(--color-surface-2); }

.border-default { border-color: var(--color-border); }

/* ═══════════════════════════════════════════════════════════
   BUTTON — base styles
   ═══════════════════════════════════════════════════════════ */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 56px;
  padding: 0 24px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.005em;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease);
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.btn:active {
  transform: scale(0.98);
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.btn-primary {
  background: var(--color-primary);
  color: #FFFFFF;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  width: 100%;
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-surface-2);
}

.btn-ghost {
  background: transparent;
  color: var(--color-text-muted);
  width: 100%;
  height: 44px;
  font-weight: 500;
}

.btn-ghost:hover:not(:disabled) {
  color: var(--color-text);
}

/* ═══════════════════════════════════════════════════════════
   FADE ANIMATION — subtle, professional
   ═══════════════════════════════════════════════════════════ */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fade-in var(--duration-base) var(--ease) both;
}

.fade-in-1 { animation-delay: 60ms; }
.fade-in-2 { animation-delay: 120ms; }
.fade-in-3 { animation-delay: 180ms; }
.fade-in-4 { animation-delay: 240ms; }
.fade-in-5 { animation-delay: 300ms; }

/* ═══════════════════════════════════════════════════════════
   SAFE AREA (Telegram)
   ═══════════════════════════════════════════════════════════ */
.safe-top { padding-top: max(16px, env(safe-area-inset-top)); }
.safe-bottom { padding-bottom: max(16px, env(safe-area-inset-bottom)); }

/* ═══════════════════════════════════════════════════════════
   PRINT (PDF fallback)
   ═══════════════════════════════════════════════════════════ */
@media print {
  *, *::before, *::after {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    animation: none !important;
    transition: none !important;
  }

  @page { size: A4; margin: 12mm 14mm; }

  body { background: white !important; color: black !important; }

  .no-print { display: none !important; }
}
''', encoding="utf-8")
print("[OK] globals.css — Design tokens")

# ═══════════════════════════════════════════════════════════
# 2. tailwind.config.ts — tokens bilan extend
# ═══════════════════════════════════════════════════════════
TAILWIND = FRONTEND / "tailwind.config.ts"

TAILWIND.write_text(r'''import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
        "surface-2": "var(--color-surface-2)",
        text: "var(--color-text)",
        muted: "var(--color-text-muted)",
        subtle: "var(--color-text-subtle)",
        primary: "var(--color-primary)",
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        danger: "var(--color-danger)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Inter', 'system-ui', 'sans-serif'],
      },
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
''', encoding="utf-8")
print("[OK] tailwind.config.ts")

# ═══════════════════════════════════════════════════════════
# 3. layout.tsx — toza, minimal
# ═══════════════════════════════════════════════════════════
LAYOUT = FRONTEND / "app/layout.tsx"

LAYOUT.write_text(r'''import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qadam.io — Kasb va soha tahlili",
  description: "Professional yo'lingizni dalillar bilan aniqlang",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: "#0A0A0F",
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
      <body data-theme="dark">{children}</body>
    </html>
  );
}
''', encoding="utf-8")
print("[OK] layout.tsx")

# ═══════════════════════════════════════════════════════════
# 4. TmaProvider — soddaroq
# ═══════════════════════════════════════════════════════════
TMA = FRONTEND / "components/TmaProvider.tsx"

TMA.write_text(r'''"use client";

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
''', encoding="utf-8")
print("[OK] TmaProvider.tsx")

# ═══════════════════════════════════════════════════════════
# 5. app/page.tsx — Welcome (minimal, premium)
# ═══════════════════════════════════════════════════════════
PAGE = FRONTEND / "app/page.tsx"

PAGE.write_text(r'''"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col px-6 safe-top safe-bottom">
      {/* ═══ LOGO MARK ═══ */}
      <div className="pt-8 pb-12 fade-in">
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <span className="text-white font-bold text-lg tracking-tight">Q</span>
        </div>
      </div>

      {/* ═══ MAIN CONTENT ═══ */}
      <div className="flex-1 flex flex-col">
        {/* Headline */}
        <h1 className="t-display mb-5 fade-in fade-in-1">
          Professional yo'lingizni
          <br />
          taxmin bilan emas,
          <br />
          <span className="text-primary">dalillar bilan</span> aniqlang.
        </h1>

        {/* Subtext */}
        <p className="t-body text-muted mb-10 max-w-[340px] fade-in fade-in-2">
          Qadam.io profilingizni tahlil qiladi, sizga mos kasblarni aniqlaydi
          va amaliy yo'l xaritasi tuzadi.
        </p>

        {/* Feature points — no cards, just list */}
        <ul className="space-y-4 mb-10 fade-in fade-in-3">
          {[
            "8 savol — 3 daqiqa",
            "Fit va Readiness tahlili",
            "Shaxsiy 6 oylik yo'l xaritasi",
          ].map((text, i) => (
            <li
              key={i}
              className="flex items-center gap-3 text-[14px] text-muted"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
              <span>{text}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* ═══ ACTIONS ═══ */}
      <div className="space-y-3 pb-4 fade-in fade-in-4">
        <Link href="/stage1" className="block">
          <button className="btn btn-primary">
            Boshlash
            <ArrowRight className="w-4 h-4" strokeWidth={2.5} />
          </button>
        </Link>

        <button className="btn btn-ghost">
          Qadam.io qanday ishlaydi?
        </button>
      </div>

      {/* ═══ TRUST LINE ═══ */}
      <p className="text-center t-caption text-subtle pb-4 fade-in fade-in-5">
        Halol tahlil · Manipulyatsiyasiz
      </p>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/page.tsx — Welcome")

print()
print("=" * 60)
print("Redesign v3 — Tayyor!")
print("=" * 60)
print()
print("Yangi tamoyillar:")
print("  • Minimal, professional, premium")
print("  • Katta typography, whitespace")
print("  • Bir ekran = bir action")
print("  • Fade animatsiya (bounce/glow yo'q)")
print("  • Dark default, light mode architecture")
print("  • Design tokens CSS variables'da")
print()
print("KEYINGI:")
print("  git add -A")
print('  git commit -m "Redesign v3: design system + minimal welcome"')
print("  git push")
print("  Vercel redeploy (cache'siz)")