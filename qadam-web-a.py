# -*- coding: utf-8 -*-
"""QADAM Web generator - Qism A: config + types + api + layout"""
from pathlib import Path

ROOT = Path("qadam-miniapp")
FILES = {}


def add(path, content):
    FILES[path] = content.strip() + "\n"


# ═══ package.json ═══
add("package.json", r'''
{
  "name": "qadam-miniapp",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@tma.js/sdk": "^2.0.0",
    "@tma.js/sdk-react": "^2.0.0",
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
''')

# ═══ next.config.js ═══
add("next.config.js", r'''
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

module.exports = nextConfig;
''')

# ═══ tsconfig.json ═══
add("tsconfig.json", r'''
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
''')

# ═══ tailwind.config.ts ═══
add("tailwind.config.ts", r'''
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
export default config;
''')

# ═══ postcss.config.js ═══
add("postcss.config.js", r'''
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
''')

# ═══ .env.local ═══
add(".env.local", r'''
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_BOT_USERNAME=qadam_bot
''')

# ═══ .gitignore ═══
add(".gitignore", r'''
node_modules/
.next/
out/
.env.local
.DS_Store
*.log
''')

# ═══ next-env.d.ts ═══
add("next-env.d.ts", r'''
/// <reference types="next" />
/// <reference types="next/image-types/global" />
''')

# ═══ lib/types.ts ═══
add("lib/types.ts", r'''
export type Question = {
  id: string;
  text: string;
  type?: "single_choice" | "multi_select" | "likert";
  options?: { v: string; l: string }[];
  max?: number;
};

export type TopSignal = {
  key: string;
  score: number;
  confidence: number;
};

export type Barrier = {
  type: string;
  level: "hard" | "soft";
  path?: string;
};

export type CareerItem = {
  career_id: string;
  career_uz: string;
  cluster_uz: string;
  fit: number;
  readiness: number;
  coverage: number;
  learning_months?: number;
  barriers: Barrier[];
  has_hard_barrier: boolean;
  has_roadmap?: boolean;
};

export type TeaserResponse = {
  stage1_result_id: number;
  top_2_signals: TopSignal[];
  top_2_careers: CareerItem[];
  locked_count: number;
  confidence: string;
};

export type AIExplanation = {
  source: "ai" | "fallback";
  summary: string;
  why_this_fits: string[];
  risks: string[];
  next_step_emphasis: string;
};

export type RoadmapItem = {
  career_id: string;
  career_uz: string;
  why_this_path: string;
  gaps: string[];
  phases: { period: string; goal: string; actions: string[] }[];
  first_3_actions: string[];
  barrier_resolutions: { barrier_type: string; level: string; action: string }[];
  milestones: string[];
  risks: string[];
  resources: { name: string; url: string }[];
  projects: string[];
  is_placeholder?: boolean;
};

export type ReportCareer = {
  career: {
    id: string;
    uz: string;
    cluster: string;
    cluster_uz: string;
    pathway_type?: string;
    learning_months?: number;
  };
  fit: number;
  readiness: number;
  coverage: number;
  barriers: Barrier[];
  has_hard_barrier: boolean;
  roadmap: RoadmapItem;
};

export type FullReport = {
  id: number;
  stage: string;
  profile: any;
  roadmap: { careers: ReportCareer[] };
  ai: AIExplanation | null;
  versions: Record<string, string>;
  created_at: string;
};
''')

# ═══ lib/api.ts ═══
add("lib/api.ts", r'''
import axios from "axios";
import { initData } from "@tma.js/sdk";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BACKEND });

function getInitData(): string {
  try {
    return initData.raw() || "";
  } catch {
    return "";
  }
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

export async function createPayment(stage1_result_id: number, provider: string) {
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

export { getInitData };
''')

# ═══ lib/store.ts ═══
add("lib/store.ts", r'''
import { create } from "zustand";
import { persist } from "zustand/middleware";

type State = {
  stage1ResultId: number | null;
  stage1Teaser: any | null;
  paid: boolean;
  setStage1: (id: number, teaser: any) => void;
  setPaid: (v: boolean) => void;
  reset: () => void;
};

export const useStore = create<State>()(
  persist(
    (set) => ({
      stage1ResultId: null,
      stage1Teaser: null,
      paid: false,
      setStage1: (id, teaser) =>
        set({ stage1ResultId: id, stage1Teaser: teaser }),
      setPaid: (v) => set({ paid: v }),
      reset: () =>
        set({ stage1ResultId: null, stage1Teaser: null, paid: false }),
    }),
    { name: "qadam-store" }
  )
);
''')

# ═══ components/TmaProvider.tsx ═══
add("components/TmaProvider.tsx", r'''
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
''')

# ═══ app/layout.tsx ═══
add("app/layout.tsx", r'''
import type { Metadata, Viewport } from "next";
import { TmaProvider } from "@/components/TmaProvider";
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
      <body>
        <TmaProvider>{children}</TmaProvider>
      </body>
    </html>
  );
}
''')

# ═══ app/globals.css ═══
add("app/globals.css", r'''
@tailwind base;
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

html,
body {
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
''')


def main():
    print("=" * 60)
    print("QADAM Web: Qism A - config + types + api")
    print("=" * 60)
    for path, content in FILES.items():
        full = ROOT / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] " + path)
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yaratildi!")


if __name__ == "__main__":
    main()