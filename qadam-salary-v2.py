# -*- coding: utf-8 -*-
"""Qadam.io — Maosh strukturasi v2 (USD + omillar)."""
from pathlib import Path
import json


DATA = Path("qadam/backend/data")
TAX = DATA / "taxonomy_v1.json"


# ═══════════════════════════════════════════════════════════
# MAOSH STRUKTURASI (USD/oy)
# ═══════════════════════════════════════════════════════════
SALARY_USD = {
    # ═══════════════ SOFTWARE ═══════════════
    "foundation_programming": {
        "junior": (300, 500),
        "middle": (800, 1400),
        "senior": (1400, 3000),
    },
    "frontend_development": {
        "junior": (300, 500),
        "middle": (800, 1500),
        "senior": (1500, 3500),
    },
    "backend_development": {
        "junior": (350, 600),
        "middle": (900, 1600),
        "senior": (1600, 3800),
    },
    "mobile_development": {
        "junior": (300, 500),
        "middle": (800, 1500),
        "senior": (1500, 3200),
    },
    # ═══════════════ DATA & AI ═══════════════
    "data_analytics": {
        "junior": (350, 550),
        "middle": (800, 1400),
        "senior": (1400, 2800),
    },
    "data_science": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3500),
    },
    "ai_engineering": {
        "junior": (500, 800),
        "middle": (1200, 2200),
        "senior": (2200, 4500),
    },
    # ═══════════════ INFRA & SECURITY ═══════════════
    "devops_cloud": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 4000),
    },
    "cybersecurity": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3800),
    },
    "qa_automation": {
        "junior": (250, 400),
        "middle": (600, 1200),
        "senior": (1200, 2500),
    },
    # ═══════════════ DESIGN ═══════════════
    "ui_ux_design": {
        "junior": (250, 450),
        "middle": (700, 1300),
        "senior": (1300, 2800),
    },
    "product_design": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3500),
    },
    "graphic_design": {
        "junior": (200, 350),
        "middle": (500, 1000),
        "senior": (1000, 2000),
    },
    "motion_design": {
        "junior": (250, 450),
        "middle": (700, 1300),
        "senior": (1300, 2500),
    },
    # ═══════════════ MARKETING ═══════════════
    "smm_manager": {
        "junior": (200, 350),
        "middle": (500, 900),
        "senior": (900, 1800),
    },
    "performance_marketing": {
        "junior": (300, 500),
        "middle": (700, 1400),
        "senior": (1400, 3000),
    },
    "seo": {
        "junior": (250, 450),
        "middle": (600, 1200),
        "senior": (1200, 2400),
    },
    "content_marketing": {
        "junior": (200, 350),
        "middle": (500, 1000),
        "senior": (1000, 2000),
    },
    # ═══════════════ CONTENT & MEDIA ═══════════════
    "video_content": {
        "junior": (200, 400),
        "middle": (600, 1200),
        "senior": (1200, 2500),
    },
    "brand_strategy": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3500),
    },
    # ═══════════════ PRODUCT & PROJECT ═══════════════
    "product_management": {
        "junior": (500, 800),
        "middle": (1200, 2200),
        "senior": (2200, 4500),
    },
    "project_management": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3500),
    },
    "business_analysis": {
        "junior": (400, 700),
        "middle": (1000, 1800),
        "senior": (1800, 3200),
    },
    # ═══════════════ BUSINESS & SALES ═══════════════
    "it_b2b_sales": {
        "junior": (300, 500),
        "middle": (800, 1500),
        "senior": (1500, 3500),
    },
    "customer_success": {
        "junior": (300, 500),
        "middle": (700, 1300),
        "senior": (1300, 2500),
    },
}


# ═══════════════════════════════════════════════════════════
# DAROMADGA TA'SIR QILUVCHI OMILLAR
# ═══════════════════════════════════════════════════════════
INCOME_FACTORS = {
    "uz": "Daromadga tasir qiluvchi omillar",
    "note": "Bu omillar maoshni 1.5x dan 3x gacha oshirishi mumkin",
    "factors": [
        {
            "name": "Freelance",
            "icon": "briefcase",
            "boost": "+30-100%",
            "desc": "Asosiy ishdan tashqari loyihalar. Upwork, Fiverr, mahalliy mijozlar.",
        },
        {
            "name": "Remote (xalqaro)",
            "icon": "globe",
            "boost": "+50-200%",
            "desc": "AQSh, Yevropa kompaniyalari bilan masofadan ishlash. Ingliz tili B2+.",
        },
        {
            "name": "Kuchli portfolio",
            "icon": "folder",
            "boost": "+20-40%",
            "desc": "3-5 real loyiha GitHub/Behance'da. Case study bilan.",
        },
        {
            "name": "Ingliz tili B2-C1",
            "icon": "language",
            "boost": "+15-30%",
            "desc": "Xalqaro mijozlar, remote ish, dokumentatsiya.",
        },
        {
            "name": "Nisha mutaxassisligi",
            "icon": "target",
            "boost": "+20-50%",
            "desc": "Fintech, healthcare, AI kabi tor nishada ekspert.",
        },
        {
            "name": "Sertifikatlar",
            "icon": "award",
            "boost": "+10-20%",
            "desc": "AWS, Google, Meta, PMI va h.k. tan olingan sertifikatlar.",
        },
        {
            "name": "Networking",
            "icon": "users",
            "boost": "+15-30%",
            "desc": "Telegram jamoalar, meetup'lar, LinkedIn faol profili.",
        },
        {
            "name": "Ochiq manba (open source)",
            "icon": "code",
            "boost": "+20-40%",
            "desc": "GitHub'da mashhur loyihalarga hissa qo'shish.",
        },
    ],
}


# ═══════════════════════════════════════════════════════════
# TAXONOMY'ga qo'shish
# ═══════════════════════════════════════════════════════════
tax = json.loads(TAX.read_text(encoding="utf-8"))

updated = 0
for cluster_key, cluster in tax["clusters"].items():
    for career_key, career in cluster["careers"].items():
        if career_key in SALARY_USD:
            junior, middle, senior = SALARY_USD[career_key]
            career["salary_usd"] = {
                "junior": {"min": junior[0], "max": junior[1]},
                "middle": {"min": middle[0], "max": middle[1]},
                "senior": {"min": senior[0], "max": senior[1]},
            }
            updated += 1

# Umumiy omillar (root'da)
tax["income_factors"] = INCOME_FACTORS
tax["version"] = "v2.2"
tax["salary_updated_at"] = "2026-09-24"
tax["salary_note"] = "USD/oy, O'zbekiston bozori uchun real oraliq (2025-2026)"

TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=2), encoding="utf-8")

print()
print("=" * 60)
print(f"Jami: {updated} ta career'ga maosh (USD) qoshildi")
print("=" * 60)
print()
print("Maosh oraligi:")
print("  Junior: $250-800")
print("  Middle: $500-2,200")
print("  Senior: $900-4,500")
print()
print("Omillar:", len(INCOME_FACTORS["factors"]), "ta")
for f in INCOME_FACTORS["factors"]:
    print(f"  • {f['name']} — {f['boost']}")
print()
print("Keyingi: frontend'da 'Daromad salohiyati' bolimini qoshish")