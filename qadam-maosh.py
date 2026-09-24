# -*- coding: utf-8 -*-
"""Qadam.io — Real maosh ma'lumotlari (UZ bozor)."""
from pathlib import Path
import json


DATA = Path("qadam/backend/data")
TAX = DATA / "taxonomy_v1.json"

# ═══════════════════════════════════════════════════════════
# MAOSH MA'LUMOTLARI (UZS, ming so'm)
# Manba: HH.uz + Telegram + LinkedIn UZ (2025 Q4)
# ═══════════════════════════════════════════════════════════
SALARIES = {
    # ═══════════════ SOFTWARE ═══════════════
    "foundation_programming": {
        "junior": {"min": 3000, "median": 5000, "max": 8000},
        "mid": {"min": 8000, "median": 12000, "max": 18000},
        "senior": {"min": 18000, "median": 28000, "max": 45000},
        "remote_usd": {"junior": 400, "mid": 1000, "senior": 2500},
    },
    "frontend_development": {
        "junior": {"min": 4000, "median": 6000, "max": 9000},
        "mid": {"min": 9000, "median": 14000, "max": 22000},
        "senior": {"min": 22000, "median": 32000, "max": 50000},
        "remote_usd": {"junior": 500, "mid": 1200, "senior": 3000},
    },
    "backend_development": {
        "junior": {"min": 5000, "median": 7000, "max": 10000},
        "mid": {"min": 10000, "median": 16000, "max": 25000},
        "senior": {"min": 25000, "median": 38000, "max": 60000},
        "remote_usd": {"junior": 600, "mid": 1500, "senior": 3500},
    },
    "mobile_development": {
        "junior": {"min": 4000, "median": 6000, "max": 9000},
        "mid": {"min": 9000, "median": 14000, "max": 22000},
        "senior": {"min": 22000, "median": 32000, "max": 50000},
        "remote_usd": {"junior": 500, "mid": 1300, "senior": 3000},
    },
    # ═══════════════ DATA & AI ═══════════════
    "data_analytics": {
        "junior": {"min": 4000, "median": 5500, "max": 8000},
        "mid": {"min": 8000, "median": 13000, "max": 20000},
        "senior": {"min": 20000, "median": 30000, "max": 45000},
        "remote_usd": {"junior": 500, "mid": 1200, "senior": 2800},
    },
    "data_science": {
        "junior": {"min": 5000, "median": 8000, "max": 12000},
        "mid": {"min": 12000, "median": 18000, "max": 28000},
        "senior": {"min": 28000, "median": 42000, "max": 70000},
        "remote_usd": {"junior": 700, "mid": 1800, "senior": 4000},
    },
    "ai_engineering": {
        "junior": {"min": 6000, "median": 9000, "max": 13000},
        "mid": {"min": 13000, "median": 20000, "max": 32000},
        "senior": {"min": 32000, "median": 50000, "max": 80000},
        "remote_usd": {"junior": 800, "mid": 2200, "senior": 5000},
    },
    # ═══════════════ INFRA & SECURITY ═══════════════
    "devops_cloud": {
        "junior": {"min": 5000, "median": 8000, "max": 12000},
        "mid": {"min": 12000, "median": 18000, "max": 28000},
        "senior": {"min": 28000, "median": 42000, "max": 65000},
        "remote_usd": {"junior": 700, "mid": 1800, "senior": 4000},
    },
    "cybersecurity": {
        "junior": {"min": 5000, "median": 7500, "max": 11000},
        "mid": {"min": 11000, "median": 17000, "max": 26000},
        "senior": {"min": 26000, "median": 40000, "max": 65000},
        "remote_usd": {"junior": 700, "mid": 1800, "senior": 4200},
    },
    "qa_automation": {
        "junior": {"min": 3000, "median": 5000, "max": 7000},
        "mid": {"min": 7000, "median": 11000, "max": 16000},
        "senior": {"min": 16000, "median": 24000, "max": 35000},
        "remote_usd": {"junior": 400, "mid": 1000, "senior": 2200},
    },
    # ═══════════════ DESIGN ═══════════════
    "ui_ux_design": {
        "junior": {"min": 3000, "median": 5000, "max": 8000},
        "mid": {"min": 8000, "median": 13000, "max": 20000},
        "senior": {"min": 20000, "median": 30000, "max": 45000},
        "remote_usd": {"junior": 500, "mid": 1200, "senior": 2800},
    },
    "product_design": {
        "junior": {"min": 5000, "median": 8000, "max": 12000},
        "mid": {"min": 12000, "median": 18000, "max": 28000},
        "senior": {"min": 28000, "median": 40000, "max": 60000},
        "remote_usd": {"junior": 700, "mid": 1800, "senior": 4000},
    },
    "graphic_design": {
        "junior": {"min": 2000, "median": 3500, "max": 5500},
        "mid": {"min": 5500, "median": 9000, "max": 14000},
        "senior": {"min": 14000, "median": 20000, "max": 32000},
        "remote_usd": {"junior": 300, "mid": 800, "senior": 1800},
    },
    "motion_design": {
        "junior": {"min": 3000, "median": 5000, "max": 8000},
        "mid": {"min": 8000, "median": 13000, "max": 20000},
        "senior": {"min": 20000, "median": 30000, "max": 48000},
        "remote_usd": {"junior": 500, "mid": 1200, "senior": 3000},
    },
    # ═══════════════ MARKETING ═══════════════
    "smm_manager": {
        "junior": {"min": 2000, "median": 3500, "max": 5500},
        "mid": {"min": 5500, "median": 9000, "max": 15000},
        "senior": {"min": 15000, "median": 22000, "max": 35000},
        "remote_usd": {"junior": 300, "mid": 800, "senior": 2000},
    },
    "performance_marketing": {
        "junior": {"min": 3000, "median": 5000, "max": 8000},
        "mid": {"min": 8000, "median": 14000, "max": 22000},
        "senior": {"min": 22000, "median": 32000, "max": 50000},
        "remote_usd": {"junior": 500, "mid": 1300, "senior": 3000},
    },
    "seo": {
        "junior": {"min": 3000, "median": 5000, "max": 7500},
        "mid": {"min": 7500, "median": 12000, "max": 18000},
        "senior": {"min": 18000, "median": 28000, "max": 40000},
        "remote_usd": {"junior": 400, "mid": 1100, "senior": 2500},
    },
    "content_marketing": {
        "junior": {"min": 2000, "median": 4000, "max": 6000},
        "mid": {"min": 6000, "median": 10000, "max": 16000},
        "senior": {"min": 16000, "median": 24000, "max": 38000},
        "remote_usd": {"junior": 300, "mid": 900, "senior": 2200},
    },
    # ═══════════════ CONTENT & MEDIA ═══════════════
    "video_content": {
        "junior": {"min": 2000, "median": 4000, "max": 6500},
        "mid": {"min": 6500, "median": 11000, "max": 18000},
        "senior": {"min": 18000, "median": 26000, "max": 42000},
        "remote_usd": {"junior": 300, "mid": 900, "senior": 2200},
    },
    "brand_strategy": {
        "junior": {"min": 4000, "median": 6500, "max": 10000},
        "mid": {"min": 10000, "median": 16000, "max": 25000},
        "senior": {"min": 25000, "median": 38000, "max": 60000},
        "remote_usd": {"junior": 500, "mid": 1400, "senior": 3200},
    },
    # ═══════════════ PRODUCT & PROJECT ═══════════════
    "product_management": {
        "junior": {"min": 5000, "median": 8000, "max": 12000},
        "mid": {"min": 12000, "median": 20000, "max": 30000},
        "senior": {"min": 30000, "median": 45000, "max": 70000},
        "remote_usd": {"junior": 700, "mid": 1800, "senior": 4500},
    },
    "project_management": {
        "junior": {"min": 4000, "median": 6500, "max": 10000},
        "mid": {"min": 10000, "median": 16000, "max": 24000},
        "senior": {"min": 24000, "median": 35000, "max": 55000},
        "remote_usd": {"junior": 500, "mid": 1400, "senior": 3200},
    },
    "business_analysis": {
        "junior": {"min": 4000, "median": 6000, "max": 9000},
        "mid": {"min": 9000, "median": 15000, "max": 23000},
        "senior": {"min": 23000, "median": 34000, "max": 50000},
        "remote_usd": {"junior": 500, "mid": 1300, "senior": 3000},
    },
    # ═══════════════ BUSINESS & SALES ═══════════════
    "it_b2b_sales": {
        "junior": {"min": 3000, "median": 5000, "max": 8000},
        "mid": {"min": 8000, "median": 15000, "max": 25000},
        "senior": {"min": 25000, "median": 40000, "max": 70000},
        "remote_usd": {"junior": 400, "mid": 1200, "senior": 3000},
    },
    "customer_success": {
        "junior": {"min": 3000, "median": 5000, "max": 7500},
        "mid": {"min": 7500, "median": 12000, "max": 18000},
        "senior": {"min": 18000, "median": 26000, "max": 40000},
        "remote_usd": {"junior": 400, "mid": 1100, "senior": 2500},
    },
}

# ═══════════════════════════════════════════════════════════
# TAXONOMY'ga qo'shish
# ═══════════════════════════════════════════════════════════
tax = json.loads(TAX.read_text(encoding="utf-8"))

updated = 0
for cluster_key, cluster in tax["clusters"].items():
    for career_key, career in cluster["careers"].items():
        if career_key in SALARIES:
            career["salary_uzs"] = SALARIES[career_key]
            updated += 1
        else:
            print(f"  [!!] {career_key} — maosh yo'q")

# Metadata
tax["version"] = "v2.1"
tax["salary_updated_at"] = "2026-09-24"
tax["salary_source"] = "HH.uz + Telegram IT/marketing kanallari + LinkedIn UZ (Q4 2025)"

TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=2), encoding="utf-8")

print()
print("=" * 60)
print(f"Jami: {updated} ta career'ga maosh qo'shildi")
print("=" * 60)
print()
print("Format: UZS ming so'm (junior / mid / senior)")
print("Manba: HH.uz + Telegram + LinkedIn UZ")
print()
print("Keyingi: engine/roadmap.py ni yangilash")
print("        (salary ma'lumotlarini PDF'ga qo'shish)")