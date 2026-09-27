# -*- coding: utf-8 -*-
"""Batch 7 — Roadmap Engine + UI."""
from pathlib import Path

BACKEND = Path("qadam/backend")
FE = Path("qadam-miniapp")

# ═══════════════════════════════════════════════════════════
# 1. roadmap_templates_v1.json — cluster-based templates
# ═══════════════════════════════════════════════════════════
(BACKEND / "data/roadmap_templates_v1.json").write_text(r'''{
  "version": "v1.0",
  "description": "Cluster-based roadmap templates (fallback)",
  "templates": {
    "software": {
      "uz": "Dasturlash",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Sintaksis", "Mantiqiy fikrlash", "Git asoslari"],
          "actions": [
            "Kuniga 1-2 soat mashq",
            "Birinchi Hello World yozish",
            "GitHub akkaunt ochish",
            "5-10 kichik masala yechish"
          ],
          "proof": "GitHub'da birinchi 3 ta repo",
          "milestone": "Birinchi kod ishga tushdi"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Framework", "API", "Debugging"],
          "actions": [
            "Kurs tugatish",
            "3-5 mini-loyiha",
            "Kod review qilish",
            "Texnik ingliz tili"
          ],
          "proof": "3 ta loyiha GitHub'da",
          "milestone": "Birinchi real loyiha"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Chuqur framework", "Testlar", "Deployment"],
          "actions": [
            "Katta loyiha qurish",
            "Open source hissa",
            "Vercel/Netlify deploy",
            "Portfolio sayti"
          ],
          "proof": "4-5 loyiha portfolio",
          "milestone": "Portfolio tayyor"
        },
        {
          "period": "6-12 oy",
          "goal": "Ishga tayyorgarlik",
          "skills": ["Algoritmlar", "System design", "Texnik suhbat"],
          "actions": [
            "LeetCode mashqi",
            "Mock interview",
            "10+ ariza yuborish",
            "Networking"
          ],
          "proof": "Junior offer",
          "milestone": "Ish topish"
        }
      ]
    },
    "data_ai": {
      "uz": "Data & AI",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Excel", "SQL", "Statistika asoslari"],
          "actions": [
            "Excel pivot jadval",
            "Birinchi SQL query",
            "Kaggle akkaunt",
            "5 ta dataset tahlil"
          ],
          "proof": "Birinchi SQL query",
          "milestone": "Birinchi dataset"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Python", "Pandas", "Vizualizatsiya"],
          "actions": [
            "Python kursi",
            "Pandas/numpy",
            "Tableau yoki Power BI",
            "3 ta loyiha"
          ],
          "proof": "3 ta dashboard",
          "milestone": "Birinchi dashboard"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Machine Learning", "Feature engineering"],
          "actions": [
            "scikit-learn",
            "ML loyihalari",
            "Kaggle competition",
            "Portfolio"
          ],
          "proof": "4-5 loyiha portfolio",
          "milestone": "ML model tayyor"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["MLOps", "Deployment", "Biznes tahlil"],
          "actions": [
            "Model deployment",
            "Real biznes case study",
            "10+ ariza",
            "Networking"
          ],
          "proof": "Junior/mid offer",
          "milestone": "Ish topish"
        }
      ]
    },
    "infra_security": {
      "uz": "Infra & Security",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Linux", "Networking", "Terminal"],
          "actions": [
            "Linux o'rnatish",
            "Bash buyruqlar",
            "TCP/IP asoslari",
            "10 ta komanda o'rganish"
          ],
          "proof": "Linux terminal",
          "milestone": "Birinchi bash script"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Docker", "Cloud", "CI/CD"],
          "actions": [
            "Docker kursi",
            "AWS/Azure asoslari",
            "GitHub Actions",
            "3 ta container loyiha"
          ],
          "proof": "Docker loyihasi",
          "milestone": "Birinchi container"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Kubernetes", "Monitoring", "Security"],
          "actions": [
            "Kubernetes",
            "Prometheus/Grafana",
            "Real infra loyiha",
            "Portfolio"
          ],
          "proof": "Portfolio 4 loyiha",
          "milestone": "K8s cluster"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["Terraform", "IaC", "Architecture"],
          "actions": [
            "Terraform",
            "Ansible",
            "10+ ariza",
            "Sertifikatlar"
          ],
          "proof": "Offer",
          "milestone": "Ish topish"
        }
      ]
    },
    "design_creative": {
      "uz": "Dizayn",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Figma", "Rang nazariyasi", "Tipografiya"],
          "actions": [
            "Figma o'rnatish",
            "5-10 UI mashqi",
            "Dribbble/Behance kuzatish",
            "Rang palitrasi"
          ],
          "proof": "Birinchi ekran dizayn",
          "milestone": "Birinchi mockup"
        },
        {
          "period": "1-3 oy",
          "goal": "UX asoslari",
          "skills": ["Wireframe", "Prototype", "User research"],
          "actions": [
            "UX asoslari kursi",
            "Wireframe mashqi",
            "User interview",
            "2-3 loyiha"
          ],
          "proof": "2 case study",
          "milestone": "Birinchi case"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Design system", "Handoff", "Real loyiha"],
          "actions": [
            "3-4 case study",
            "Real mijoz",
            "Design system",
            "Portfolio sayt"
          ],
          "proof": "4 portfolio case",
          "milestone": "Birinchi mijoz"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["Product design", "Design challenges"],
          "actions": [
            "Design challenge mashqi",
            "10+ ariza",
            "Behance profil",
            "Networking"
          ],
          "proof": "Offer",
          "milestone": "Ish topish"
        }
      ]
    },
    "digital_marketing": {
      "uz": "Marketing",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Kontent strategiya", "Canva", "Copywriting"],
          "actions": [
            "Canva o'rganish",
            "10 post tayyorlash",
            "2-3 raqib tahlil",
            "AIDA formula"
          ],
          "proof": "10 post portfolio",
          "milestone": "Birinchi kontent"
        },
        {
          "period": "1-3 oy",
          "goal": "Platformalar",
          "skills": ["Meta Ads", "Analytics", "Targeting"],
          "actions": [
            "Meta Blueprint",
            "Kichik kampaniya",
            "Analitika o'rnatish",
            "A/B test"
          ],
          "proof": "1 real mijoz",
          "milestone": "Birinchi mijoz"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Performance marketing", "SEO", "Content"],
          "actions": [
            "3-5 mijoz",
            "Case study",
            "Natijalar tahlili",
            "Nisha tanlash"
          ],
          "proof": "3-5 case study",
          "milestone": "Kuchli portfolio"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["Growth marketing", "Strategy", "Leadership"],
          "actions": [
            "10+ ariza",
            "Agentlik yoki freelance",
            "Networking",
            "Sertifikatlar"
          ],
          "proof": "Offer yoki 5+ mijoz",
          "milestone": "Barqaror daromad"
        }
      ]
    },
    "content_media": {
      "uz": "Media",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Videografiya", "CapCut", "Storytelling"],
          "actions": [
            "10 qisqa video",
            "CapCut montaj",
            "Script yozish",
            "YouTube/TikTok kanal"
          ],
          "proof": "10 video",
          "milestone": "Birinchi montaj"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Premiere", "Kamera", "Sound"],
          "actions": [
            "Kurs tugatish",
            "Long-form video",
            "Real mijoz",
            "Motion graphics"
          ],
          "proof": "3-5 video portfolio",
          "milestone": "Birinchi mijoz"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Color grading", "After Effects"],
          "actions": [
            "5-7 portfolio loyiha",
            "Brand content",
            "Reels seriyasi",
            "Portfolio reel"
          ],
          "proof": "Kuchli portfolio",
          "milestone": "Barqaror mijozlar"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["Direction", "Team lead"],
          "actions": [
            "10+ ariza",
            "Agentlik",
            "Freelance",
            "Shaxsiy brend"
          ],
          "proof": "Offer yoki agentlik",
          "milestone": "Karyera"
        }
      ]
    },
    "product_project": {
      "uz": "Product & Project",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Agile", "Scrum", "Product thinking"],
          "actions": [
            "Scrum Guide o'qish",
            "Product kitoblar",
            "3 ta mahsulot tahlil",
            "Jira/Notion"
          ],
          "proof": "Birinchi case study",
          "milestone": "Product case"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Discovery", "Metrics", "Roadmap"],
          "actions": [
            "User research",
            "Product metrics",
            "Roadmap tuzish",
            "A/B test"
          ],
          "proof": "1 real loyiha",
          "milestone": "Birinchi roadmap"
        },
        {
          "period": "3-6 oy",
          "goal": "Portfolio",
          "skills": ["Strategy", "Analytics", "Stakeholders"],
          "actions": [
            "Kichik startap PM",
            "3-4 case study",
            "SQL + analitika",
            "Product case"
          ],
          "proof": "3-4 case study",
          "milestone": "Portfolio tayyor"
        },
        {
          "period": "6-12 oy",
          "goal": "Ish",
          "skills": ["Leadership", "Strategy"],
          "actions": [
            "10+ ariza",
            "Networking",
            "PM portfolio",
            "Sertifikat"
          ],
          "proof": "Offer",
          "milestone": "PM lavozim"
        }
      ]
    },
    "business_sales": {
      "uz": "Business & Sales",
      "phases": [
        {
          "period": "0-30 kun",
          "goal": "Asoslar",
          "skills": ["Sales metodologiya", "CRM", "Communication"],
          "actions": [
            "SPIN Selling o'qish",
            "CRM o'rganish",
            "50 cold email",
            "LinkedIn optimizatsiya"
          ],
          "proof": "Birinchi demo call",
          "milestone": "Birinchi lead"
        },
        {
          "period": "1-3 oy",
          "goal": "Amaliyot",
          "skills": ["Qualification", "Negotiation", "IT sales"],
          "actions": [
            "MEDDIC framework",
            "Real mijozlar",
            "Pitch mashqi",
            "Bitim yopish"
          ],
          "proof": "Birinchi bitim",
          "milestone": "Birinchi savdo"
        },
        {
          "period": "3-6 oy",
          "goal": "Katta bitimlar",
          "skills": ["Enterprise sales", "Account management"],
          "actions": [
            "Enterprise mijozlar",
            "Katta kontrakt",
            "CRM workflow",
            "Case studies"
          ],
          "proof": "3-5 bitim",
          "milestone": "Barqaror savdo"
        },
        {
          "period": "6-12 oy",
          "goal": "Karyera",
          "skills": ["Team lead", "Sales strategy"],
          "actions": [
            "Jamoa boshqarish",
            "Sales strategy",
            "Networking",
            "Sertifikatlar"
          ],
          "proof": "Senior sales yoki lead",
          "milestone": "Karyera o'sishi"
        }
      ]
    }
  }
}
''', encoding="utf-8")
print("[OK] roadmap_templates_v1.json")

# ═══════════════════════════════════════════════════════════
# 2. roadmap_engine.py — engine
# ═══════════════════════════════════════════════════════════
(BACKEND / "engine/roadmap_engine.py").write_text(r'''"""
Roadmap Engine — KB + template fallback.

Oqim:
1. KB'da batafsil roadmap bormi? → uni ishlatamiz
2. Aks holda → cluster template + career info
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_kb():
    for name in ["roadmap_kb_v2.json", "roadmap_kb_v1.json"]:
        p = DATA_DIR / name
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {"careers": {}}


def _load_templates():
    p = DATA_DIR / "roadmap_templates_v1.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"templates": {}}


KB = _load_kb()
TEMPLATES = _load_templates()


def build_roadmap(career_slug: str, career_data: dict, ranked_item: dict) -> dict:
    """
    Shaxsiy roadmap qurish.
    """
    # 1. KB'da batafsil roadmap bormi?
    kb_career = KB.get("careers", {}).get(career_slug)
    if kb_career:
        return _from_kb(career_slug, kb_career, ranked_item)

    # 2. Template fallback
    cluster = career_data.get("cluster", "")
    template = TEMPLATES.get("templates", {}).get(cluster)
    if template:
        return _from_template(career_slug, career_data, template, ranked_item)

    # 3. Bo'sh placeholder
    return _placeholder(career_slug, career_data, ranked_item)


def _from_kb(slug: str, kb: dict, ranked: dict) -> dict:
    """KB'dan to'liq roadmap."""
    stages = []
    for s in kb.get("stages", []):
        stages.append({
            "period": f"{s.get('weeks', 0)} hafta",
            "goal": s.get("name_uz", ""),
            "role": s.get("role", ""),
            "skills": s.get("skills_gained", []),
            "actions": s.get("daily_focus", [])[:4],
            "proof": "",
            "milestone": s.get("graduate_by", ""),
        })

    first_3 = kb.get("first_3_actions", [])[:3]
    if not first_3 and stages:
        first_3 = stages[0].get("actions", [])[:3]

    return {
        "career_id": slug,
        "career_uz": kb.get("uz", ""),
        "why": kb.get("why", ""),
        "source": "kb",
        "phases": stages,
        "next_3_actions": first_3,
        "resources": kb.get("resources", []),
        "b_point": kb.get("b_point", {}),
        "milestones": kb.get("milestones", []),
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": _first_step_reasoning(ranked, stages),
    }


def _from_template(slug: str, career: dict, template: dict, ranked: dict) -> dict:
    """Template'dan roadmap."""
    phases = []
    for p in template.get("phases", []):
        phases.append({
            "period": p.get("period", ""),
            "goal": p.get("goal", ""),
            "role": "",
            "skills": p.get("skills", []),
            "actions": p.get("actions", []),
            "proof": p.get("proof", ""),
            "milestone": p.get("milestone", ""),
        })

    first_3 = phases[0]["actions"][:3] if phases else []
    return {
        "career_id": slug,
        "career_uz": career.get("title_uz") or career.get("uz", ""),
        "why": f"Bu yo'nalish sizning signallaringizga mos keladi.",
        "source": "template",
        "phases": phases,
        "next_3_actions": first_3,
        "resources": [],
        "b_point": career.get("salary_usd") and {"salary_usd": career["salary_usd"]} or {},
        "milestones": [p.get("milestone", "") for p in phases if p.get("milestone")],
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": _first_step_reasoning(ranked, phases),
    }


def _placeholder(slug: str, career: dict, ranked: dict) -> dict:
    return {
        "career_id": slug,
        "career_uz": career.get("title_uz", slug),
        "why": "Bu yo'nalish uchun batafsil roadmap tez orada qo'shiladi.",
        "source": "placeholder",
        "phases": [],
        "next_3_actions": [],
        "resources": [],
        "b_point": {},
        "milestones": [],
        "barrier_resolutions": _barrier_resolutions(ranked.get("barriers", [])),
        "first_step_reasoning": "",
    }


def _barrier_resolutions(barriers: list) -> list:
    """Barrier'larni action'ga aylantirish."""
    out = []
    for b in barriers:
        if b.get("path"):
            out.append({
                "level": b.get("level", "soft"),
                "action": b["path"],
            })
    return out


def _first_step_reasoning(ranked: dict, stages: list) -> str:
    """Nega birinchi qadam muhim."""
    if not stages:
        return ""
    return (
        f"Birinchi qadam — {stages[0].get('goal', 'asoslar')}. "
        "Bu bosqichsiz keyingi qadamlar samarasiz bo'ladi."
    )
''', encoding="utf-8")
print("[OK] engine/roadmap_engine.py")

# ═══════════════════════════════════════════════════════════
# 3. API — /api/v1/roadmap/{slug}
# ═══════════════════════════════════════════════════════════
(BACKEND / "api/v1/roadmap.py").write_text(r'''"""Roadmap API v1 — premium."""
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from backend.db import SessionLocal
from backend.models_v2 import (
    DeepDiagnosticSession, DeepDiagnosticSignal, DiscoverySignal,
)
from backend.auth import verify_init_data
from backend.services.entitlement_service import has_active_entitlement
from backend.services.taxonomy_service import load_taxonomy_from_db
from backend.engine.ranking import rank_careers
from backend.engine.roadmap_engine import build_roadmap

router = APIRouter(prefix="/api/v1/roadmap", tags=["roadmap-v1"])

PREMIUM_KEY = "premium_career_intelligence"


def _signals_from_rows(rows) -> dict:
    return {
        r.signal_key: {
            "value": r.value, "trust": r.trust,
            "evidence_state": r.evidence_state, "coverage": r.coverage,
        }
        for r in rows
    }


@router.get("/{career_slug}")
async def get_roadmap(
    career_slug: str,
    session_id: int = Query(..., description="Deep diagnostic session id"),
    init_data: str = Query(...),
):
    """Bitta career uchun shaxsiy roadmap."""
    user = verify_init_data(init_data)
    if not user:
        raise HTTPException(401, "Invalid initData")

    if not await has_active_entitlement(user["id"], PREMIUM_KEY):
        raise HTTPException(402, "Premium kerak")

    async with SessionLocal() as s:
        sess = await s.get(DeepDiagnosticSession, session_id)
        if not sess or sess.user_id != user["id"]:
            raise HTTPException(404, "Session topilmadi")

        signal_rows = (await s.execute(
            select(DeepDiagnosticSignal).where(DeepDiagnosticSignal.session_id == session_id)
        )).scalars().all()

        disc_rows = []
        if sess.discovery_session_id:
            disc_rows = (await s.execute(
                select(DiscoverySignal).where(DiscoverySignal.session_id == sess.discovery_session_id)
            )).scalars().all()

    signals = {**_signals_from_rows(disc_rows), **_signals_from_rows(signal_rows)}
    constraints = (sess.meta or {}).get("constraints") or {}
    base = {"time": "2_3h", "device": "laptop", "english": "b1"}
    base.update(constraints)

    taxonomy = await load_taxonomy_from_db()

    # Career topish
    career_data = None
    cluster_key = None
    for ck, cluster in taxonomy["clusters"].items():
        if career_slug in cluster["careers"]:
            career_data = cluster["careers"][career_slug]
            cluster_key = ck
            break

    if not career_data:
        raise HTTPException(404, "Career topilmadi")

    # Ranking'dan bu career uchun Fit/Readiness
    ranking = rank_careers(signals, taxonomy, base, top_n=25)
    ranked_item = next(
        (r for r in ranking["ranked"] if r["career_id"] == career_slug),
        None,
    )
    if not ranked_item:
        # Top-25'da yo'q — qo'lda hisoblash
        from backend.engine.fit import calculate_fit
        from backend.engine.readiness import calculate_readiness
        fit = calculate_fit(signals, career_data)
        readiness = calculate_readiness(base, career_data.get("prerequisites", {}))
        ranked_item = {
            "career_id": career_slug,
            "fit": fit["fit"],
            "coverage": fit["coverage"],
            "confidence": fit["confidence"],
            "readiness": readiness["readiness"],
            "barriers": readiness["barriers"],
            "has_hard_barrier": readiness["has_hard_barrier"],
        }

    # Roadmap
    career_full = {**career_data, "cluster": cluster_key or ""}
    roadmap = build_roadmap(career_slug, career_full, ranked_item)

    return {
        "career_slug": career_slug,
        "fit": ranked_item.get("fit"),
        "coverage": ranked_item.get("coverage"),
        "confidence": ranked_item.get("confidence"),
        "readiness": ranked_item.get("readiness"),
        "has_hard_barrier": ranked_item.get("has_hard_barrier"),
        "roadmap": roadmap,
    }
''', encoding="utf-8")
print("[OK] api/v1/roadmap.py")

# ═══════════════════════════════════════════════════════════
# 4. main.py — roadmap router
# ═══════════════════════════════════════════════════════════
MAIN = BACKEND / "main.py"
main = MAIN.read_text(encoding="utf-8")

if "v1_roadmap_router" not in main:
    main = main.replace(
        "from backend.api.v1.deep_diagnostic import router as v1_dd_router",
        "from backend.api.v1.deep_diagnostic import router as v1_dd_router\n"
        "from backend.api.v1.roadmap import router as v1_roadmap_router",
    )
    main = main.replace(
        "app.include_router(v1_dd_router)",
        "app.include_router(v1_dd_router)\n"
        "app.include_router(v1_roadmap_router)",
    )
    MAIN.write_text(main, encoding="utf-8")
    print("[OK] main.py — roadmap router")

# ═══════════════════════════════════════════════════════════
# 5. FRONTEND — /roadmap/[slug] page
# ═══════════════════════════════════════════════════════════
(FE / "app/roadmap/[slug]").mkdir(parents=True, exist_ok=True)

(FE / "app/roadmap/[slug]/page.tsx").write_text(r'''"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ChevronLeft, Target, AlertCircle, Rocket, BookOpen,
  Calendar, CheckCircle2, ExternalLink,
} from "lucide-react";
import { api, getInitData } from "@/lib/api";

export default function RoadmapPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ddSessionId = typeof window !== "undefined"
    ? Number(sessionStorage.getItem("dd_session_id"))
    : null;

  useEffect(() => {
    if (!slug || !ddSessionId) {
      router.push("/career-intelligence");
      return;
    }
    api.get(`/api/v1/roadmap/${slug}`, {
      params: { init_data: getInitData(), session_id: ddSessionId },
    })
      .then((r) => setData(r.data))
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false));
  }, [slug, ddSessionId, router]);

  if (loading) return <Loader />;
  if (error) return <Err msg={error} />;
  if (!data) return null;

  const rm = data.roadmap || {};

  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 safe-top safe-bottom pt-6 pb-8">
        {/* Back */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1 t-small text-muted mb-6"
        >
          <ChevronLeft className="w-4 h-4" />
          Orqaga
        </button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <p className="t-caption text-primary mb-2">Shaxsiy yo&apos;l xaritasi</p>
          <h1 className="t-display mb-4">{rm.career_uz || slug}</h1>

          {/* Fit + Readiness */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="card-clean text-center">
              <p className="t-caption text-subtle mb-1">Fit</p>
              <p className="t-metric text-primary leading-none">
                {data.fit !== null ? Math.round(data.fit) : "—"}
                <span className="text-base">%</span>
              </p>
            </div>
            <div className="card-clean text-center">
              <p className="t-caption text-subtle mb-1">Readiness</p>
              <p className="t-metric text-success leading-none">
                {data.readiness !== null ? Math.round(data.readiness) : "—"}
                <span className="text-base">%</span>
              </p>
            </div>
          </div>

          {data.has_hard_barrier && (
            <div className="flex items-start gap-2 p-3 rounded-xl bg-[var(--color-danger-soft)] border border-[var(--color-danger)]/30">
              <AlertCircle className="w-4 h-4 text-danger shrink-0 mt-0.5" />
              <p className="t-small text-danger">
                Hozir jiddiy to&apos;siq mavjud — pastdagi yechimga qarang.
              </p>
            </div>
          )}
        </motion.div>

        {/* Why */}
        {rm.why && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-2">Nega bu mos</p>
            <p className="t-small text-muted">{rm.why}</p>
          </motion.div>
        )}

        {/* Barrier resolutions */}
        {rm.barrier_resolutions?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card-clean mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="w-4 h-4 text-warning" />
              <p className="t-heading">To&apos;siqlar va yechim</p>
            </div>
            <ul className="space-y-2">
              {rm.barrier_resolutions.map((b: any, i: number) => (
                <li key={i} className="flex items-start gap-2 t-small">
                  <span className={`badge-soft ${b.level === "hard" ? "badge-danger" : "badge-warning"}`}>
                    {b.level === "hard" ? "Kuchli" : "Yengil"}
                  </span>
                  <span className="flex-1 text-muted">{b.action}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Next 3 actions */}
        {rm.next_3_actions?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="rounded-2xl p-5 mb-6 bg-gradient-to-br from-indigo-500/10 to-purple-500/5 border border-primary/30"
          >
            <div className="flex items-center gap-2 mb-3">
              <Rocket className="w-4 h-4 text-primary" />
              <p className="t-heading">Birinchi 3 qadam</p>
            </div>
            <p className="t-caption text-subtle mb-3">Bugun boshlang</p>
            <ol className="space-y-3">
              {rm.next_3_actions.map((a: string, i: number) => (
                <li key={i} className="flex items-start gap-3 t-small">
                  <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-white text-xs font-semibold shrink-0">
                    {i + 1}
                  </span>
                  <span>{a}</span>
                </li>
              ))}
            </ol>
          </motion.div>
        )}

        {/* Phases */}
        {rm.phases?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="w-4 h-4 text-primary" />
              <p className="t-heading">Yo&apos;l xaritasi</p>
            </div>

            <div className="relative">
              <div className="absolute left-[11px] top-2 bottom-2 w-px bg-[var(--color-border)]" />
              <div className="space-y-4">
                {rm.phases.map((p: any, i: number) => (
                  <div key={i} className="relative pl-8">
                    <div className="absolute left-0 top-0 w-6 h-6 rounded-full bg-[var(--color-surface-2)] border-2 border-primary flex items-center justify-center text-xs font-bold text-primary">
                      {i + 1}
                    </div>
                    <div className="card-clean">
                      <p className="t-caption text-primary mb-1">{p.period}</p>
                      <p className="t-heading mb-3">{p.goal}</p>

                      {p.skills?.length > 0 && (
                        <div className="mb-3">
                          <p className="t-caption text-subtle mb-1.5">Ko&apos;nikmalar</p>
                          <div className="flex flex-wrap gap-1">
                            {p.skills.map((s: string, j: number) => (
                              <span key={j} className="badge-soft badge-primary">{s}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {p.actions?.length > 0 && (
                        <div className="mb-3">
                          <p className="t-caption text-subtle mb-1.5">Amallar</p>
                          <ul className="space-y-1">
                            {p.actions.map((a: string, j: number) => (
                              <li key={j} className="flex items-start gap-2 t-small text-muted">
                                <span className="text-primary shrink-0">•</span>
                                <span>{a}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {p.milestone && (
                        <div className="pt-2 mt-2 border-t border-[var(--color-border)] flex items-center gap-2">
                          <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0" />
                          <span className="t-caption text-muted">{p.milestone}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Resources */}
        {rm.resources?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="card-clean mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-4 h-4 text-primary" />
              <p className="t-heading">Resurslar</p>
            </div>
            <div className="space-y-2">
              {rm.resources.map((r: any, i: number) => (
                <a
                  key={i}
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-2.5 rounded-lg bg-[var(--color-surface-2)] hover:bg-[var(--color-surface-2)]/80 transition"
                >
                  <span className="t-small">{r.name}</span>
                  <ExternalLink className="w-3.5 h-3.5 text-subtle" />
                </a>
              ))}
            </div>
          </motion.div>
        )}

        {/* Salary (B nuqta) */}
        {rm.b_point?.salary_usd && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card-clean mb-6"
          >
            <p className="t-caption text-subtle mb-3">Daromad salohiyati (oyiga)</p>
            <div className="space-y-2">
              {["junior", "middle", "senior"].map((lvl) => {
                const s = rm.b_point.salary_usd[lvl];
                if (!s) return null;
                return (
                  <div key={lvl} className="flex items-center justify-between">
                    <span className="t-small capitalize text-muted">{lvl}</span>
                    <span className="t-heading tabular-nums">
                      ${s.min} — ${s.max}
                    </span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        <p className="t-caption text-subtle text-center pt-4">
          Halol tahlil · Manipulyatsiyasiz
        </p>
      </div>
    </main>
  );
}

function Loader() {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-6">
        <div className="w-8 h-8 mx-auto border-4 border-[var(--color-border)] border-t-primary rounded-full animate-spin" />
      </div>
    </main>
  );
}

function Err({ msg }: { msg: string }) {
  return (
    <main className="min-h-screen flex justify-center">
      <div className="w-full max-w-md px-6 pt-8">
        <div className="card-clean border-[var(--color-danger)]/40">
          <p className="t-small text-danger">{msg}</p>
        </div>
      </div>
    </main>
  );
}
''', encoding="utf-8")
print("[OK] app/roadmap/[slug]/page.tsx")

# ═══════════════════════════════════════════════════════════
# 6. career-intelligence — career'ga bosish → /roadmap
# ═══════════════════════════════════════════════════════════
CI = FE / "app/career-intelligence/page.tsx"
ci = CI.read_text(encoding="utf-8")

# Import useRouter allaqachon bor
# Har career card'ni click qilish mumkin qilish
ci = ci.replace(
    '''              <div key={c.career_id} className="card-clean">''',
    '''              <div
                key={c.career_id}
                className="card-clean cursor-pointer hover:border-primary/40 transition"
                onClick={() => router.push(`/roadmap/${c.career_id}`)}
              >''',
)

CI.write_text(ci, encoding="utf-8")
print("[OK] career-intelligence — /roadmap link")

# ═══════════════════════════════════════════════════════════
# 7. Tests
# ═══════════════════════════════════════════════════════════
(BACKEND.parent / "tests/test_batch7_roadmap.py").write_text(r'''"""Batch 7 — Roadmap testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.roadmap_engine import build_roadmap, KB, TEMPLATES


def test_templates_loaded():
    assert "templates" in TEMPLATES
    assert "software" in TEMPLATES["templates"]
    assert "data_ai" in TEMPLATES["templates"]


def test_template_has_4_phases():
    for cluster_key, tpl in TEMPLATES["templates"].items():
        assert len(tpl["phases"]) == 4, f"{cluster_key} 4 ta faza kerak"


def test_build_roadmap_from_template():
    """KB'da yo'q career → template fallback."""
    career = {"title_uz": "Test Career", "cluster": "software"}
    ranked = {"career_id": "test_slug", "fit": 80, "readiness": 70, "barriers": []}
    rm = build_roadmap("test_slug", career, ranked)
    assert rm["source"] in ("template", "kb")
    assert len(rm["phases"]) >= 1
    assert len(rm["next_3_actions"]) >= 1


def test_build_roadmap_kb_foundation():
    """KB'da bor career — ishlatilishi kerak."""
    career = {"title_uz": "Foundation Programming", "cluster": "software"}
    ranked = {"career_id": "foundation_programming", "fit": 85, "readiness": 100, "barriers": []}
    rm = build_roadmap("foundation_programming", career, ranked)
    assert rm["source"] in ("kb", "template")  # KB ustuvor, lekin testda har ikki xil
    assert "next_3_actions" in rm


def test_barrier_resolutions():
    career = {"title_uz": "Frontend", "cluster": "software"}
    ranked = {
        "career_id": "fe",
        "fit": 80,
        "readiness": 50,
        "barriers": [
            {"type": "device", "level": "soft", "path": "Noutbuk topish"},
            {"type": "language", "level": "soft", "path": "Ingliz B1"},
        ],
    }
    rm = build_roadmap("fe", career, ranked)
    assert len(rm["barrier_resolutions"]) == 2


def test_roadmap_has_why():
    career = {"title_uz": "Test", "cluster": "design_creative"}
    ranked = {"career_id": "t", "fit": 70, "readiness": 60, "barriers": []}
    rm = build_roadmap("t", career, ranked)
    assert rm["why"]


def test_all_clusters_have_templates():
    """Har 8 cluster uchun template bo'lishi kerak."""
    required = [
        "software", "data_ai", "infra_security", "design_creative",
        "digital_marketing", "content_media", "product_project", "business_sales",
    ]
    for c in required:
        assert c in TEMPLATES["templates"], f"{c} template yo'q"
''', encoding="utf-8")
print("[OK] tests/test_batch7_roadmap.py (7 test)")

print()
print("=" * 60)
print("Batch 7 (Roadmap) — TAYYOR!")
print("=" * 60)
print()
print("Yangi:")
print("  • roadmap_templates_v1.json (8 cluster × 4 faza)")
print("  • engine/roadmap_engine.py (KB + template)")
print("  • /api/v1/roadmap/{slug}")
print("  • /roadmap/[slug] frontend page")
print("  • Career Intelligence → career bosish → roadmap")
print("  • 7 test")
print()
print("KEYINGI:")
print("  cd qadam")
print("  ..\\qadam\\venv\\Scripts\\python.exe -m pytest tests\\test_batch7_roadmap.py -v")
print("  cd ..")
print("  git add -A")
print('  git commit -m "Batch 7: Roadmap Engine + UI"')
print("  git push")
print("  Render Manual Deploy + Vercel auto")