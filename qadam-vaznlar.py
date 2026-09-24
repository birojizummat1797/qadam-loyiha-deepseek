# -*- coding: utf-8 -*-
"""Qadam.io — Fit/Readiness kalibrlash (v2)."""
from pathlib import Path
import json


DATA = Path("qadam/backend/data")
TAX = DATA / "taxonomy_v1.json"

tax = json.loads(TAX.read_text(encoding="utf-8"))

# ═══════════════════════════════════════════════════════════
# YANGI VAZNLAR — RIASEC + Industry asosida
# ═══════════════════════════════════════════════════════════
# Format: signal -> weight (1-5)
# 5 = CRITICAL (bu bo'lmasa — ishlamaydi)
# 4 = MUHIM (kuchli afzallik)
# 3 = FOYDALI (yaxshi qo'shimcha)
# 2 = MINOR (kichik afzallik)
# 1 = CONTEXT (kontekst)

NEW_WEIGHTS = {
    # ═══════════════════════════════════════════════════════
    # SOFTWARE CLUSTER
    # ═══════════════════════════════════════════════════════
    "foundation_programming": {
        "logical_thinking": 5,       # ⭐ ENG MUHIM
        "problem_solving": 5,
        "persistence": 4,
        "attention_to_detail": 4,
        "technical_interest": 3,
        "system_design": 2,
        "analytical": 2,
    },
    "frontend_development": {
        "visual_logic": 5,            # ⭐ UI sezgi
        "creative_design": 4,
        "logical_thinking": 4,
        "attention_to_detail": 4,
        "problem_solving": 3,
        "user_empathy": 3,
        "technical_interest": 3,
        "persistence": 3,
    },
    "backend_development": {
        "system_design": 5,           # ⭐ Tizim
        "logical_thinking": 5,
        "problem_solving": 5,
        "analytical": 4,
        "attention_to_detail": 4,
        "persistence": 3,
        "technical_interest": 3,
    },
    "mobile_development": {
        "problem_solving": 5,
        "logical_thinking": 4,
        "user_empathy": 4,            # ⭐ UX
        "creative_design": 3,
        "visual_logic": 3,
        "persistence": 3,
        "technical_interest": 3,
    },
    # ═══════════════════════════════════════════════════════
    # DATA & AI CLUSTER
    # ═══════════════════════════════════════════════════════
    "data_analytics": {
        "analytical": 5,              # ⭐
        "attention_to_detail": 5,
        "math_logic": 4,
        "logical_thinking": 4,
        "business_sense": 3,
        "persistence": 3,
    },
    "data_science": {
        "math_logic": 5,              # ⭐
        "analytical": 5,
        "logical_thinking": 4,
        "persistence": 4,
        "innovation": 3,
        "system_design": 3,
    },
    "ai_engineering": {
        "logical_thinking": 5,
        "system_design": 5,           # ⭐
        "problem_solving": 5,
        "math_logic": 4,
        "innovation": 4,
        "analytical": 3,
        "persistence": 3,
    },
    # ═══════════════════════════════════════════════════════
    # INFRA & SECURITY
    # ═══════════════════════════════════════════════════════
    "devops_cloud": {
        "system_design": 5,           # ⭐
        "technical_interest": 5,
        "analytical": 4,
        "attention_to_detail": 4,
        "persistence": 4,
        "logical_thinking": 3,
    },
    "cybersecurity": {
        "analytical": 5,              # ⭐
        "attention_to_detail": 5,
        "persistence": 5,
        "logical_thinking": 4,
        "system_design": 4,
        "technical_interest": 3,
    },
    "qa_automation": {
        "attention_to_detail": 5,     # ⭐
        "persistence": 4,
        "logical_thinking": 4,
        "problem_solving": 4,
        "analytical": 4,
        "technical_interest": 2,
    },
    # ═══════════════════════════════════════════════════════
    # DESIGN & CREATIVE
    # ═══════════════════════════════════════════════════════
    "ui_ux_design": {
        "user_empathy": 5,            # ⭐
        "creative_design": 5,
        "visual_logic": 5,
        "attention_to_detail": 4,
        "system_design": 3,
        "problem_solving": 3,
    },
    "product_design": {
        "creative_design": 5,
        "user_empathy": 5,            # ⭐
        "system_design": 4,
        "analytical": 4,
        "visual_logic": 4,
        "business_sense": 3,
        "attention_to_detail": 3,
    },
    "graphic_design": {
        "creative_design": 5,         # ⭐
        "visual_logic": 5,
        "attention_to_detail": 4,
        "persistence": 3,
    },
    "motion_design": {
        "creative_design": 5,         # ⭐
        "visual_logic": 5,
        "persistence": 4,
        "attention_to_detail": 4,
        "technical_interest": 2,
    },
    # ═══════════════════════════════════════════════════════
    # DIGITAL MARKETING
    # ═══════════════════════════════════════════════════════
    "smm_manager": {
        "user_empathy": 5,            # ⭐
        "creative_design": 4,
        "business_sense": 4,
        "analytical": 3,
        "persistence": 3,
    },
    "performance_marketing": {
        "analytical": 5,              # ⭐
        "business_sense": 5,
        "attention_to_detail": 4,
        "math_logic": 3,
        "persistence": 3,
        "innovation": 3,
    },
    "seo": {
        "attention_to_detail": 5,     # ⭐
        "persistence": 5,
        "analytical": 4,
        "logical_thinking": 3,
        "innovation": 2,
    },
    "content_marketing": {
        "creative_design": 4,         # ⭐
        "user_empathy": 4,
        "persistence": 4,
        "attention_to_detail": 4,
        "analytical": 3,
    },
    # ═══════════════════════════════════════════════════════
    # CONTENT & MEDIA
    # ═══════════════════════════════════════════════════════
    "video_content": {
        "creative_design": 5,         # ⭐
        "visual_logic": 5,
        "persistence": 4,
        "attention_to_detail": 3,
        "technical_interest": 2,
    },
    "brand_strategy": {
        "creative_design": 5,         # ⭐
        "business_sense": 4,
        "innovation": 4,
        "user_empathy": 4,
        "analytical": 3,
        "system_design": 3,
    },
    # ═══════════════════════════════════════════════════════
    # PRODUCT & PROJECT
    # ═══════════════════════════════════════════════════════
    "product_management": {
        "system_design": 5,           # ⭐
        "business_sense": 5,
        "analytical": 4,
        "user_empathy": 4,
        "innovation": 3,
        "persistence": 3,
    },
    "project_management": {
        "system_design": 5,           # ⭐
        "persistence": 5,
        "attention_to_detail": 4,
        "business_sense": 4,
        "user_empathy": 3,
    },
    "business_analysis": {
        "analytical": 5,              # ⭐
        "attention_to_detail": 5,
        "system_design": 4,
        "logical_thinking": 4,
        "business_sense": 4,
    },
    # ═══════════════════════════════════════════════════════
    # BUSINESS & SALES
    # ═══════════════════════════════════════════════════════
    "it_b2b_sales": {
        "business_sense": 5,          # ⭐
        "user_empathy": 5,
        "persistence": 5,
        "analytical": 3,
        "innovation": 3,
    },
    "customer_success": {
        "user_empathy": 5,            # ⭐
        "business_sense": 4,
        "attention_to_detail": 4,
        "persistence": 4,
        "system_design": 3,
    },
}

# ═══════════════════════════════════════════════════════════
# TAXONOMY'ni yangilash
# ═══════════════════════════════════════════════════════════
updated = 0
for cluster_key, cluster in tax["clusters"].items():
    for career_key, career in cluster["careers"].items():
        if career_key in NEW_WEIGHTS:
            career["signals"] = NEW_WEIGHTS[career_key]
            updated += 1
        else:
            print(f"  [!!] {career_key} — yangi vaznlar yo'q")

# Versiyani ko'tarish
tax["version"] = "v2.0"
tax["weighted_at"] = "2026-09-24"
tax["note"] = "RIASEC + industry asosida qayta kalibrlangan vaznlar"

TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=2), encoding="utf-8")

print()
print("=" * 60)
print(f"Jami: {updated} ta career yangilandi")
print("=" * 60)
print()
print("YANGI VAZNLAR ASOSI:")
print("  • RIASEC (Holland) modeli")
print("  • Industry real talablari (HH.uz vakansiyalar)")
print("  • 5 = critical, 4 = important, 3 = useful, 2 = minor")
print()
print("Keyingi: git push + Render Manual Deploy")