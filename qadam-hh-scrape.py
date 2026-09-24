# -*- coding: utf-8 -*-
"""Qadam.io — HH.uz'dan real maosh ma'lumotlari."""
import httpx
import json
import statistics
import time
from pathlib import Path


# ═══════════════════════════════════════════════════════════
# HH.uz API — har bir kasb uchun
# ═══════════════════════════════════════════════════════════
HH_API = "https://api.hh.uz/vacancies"

# Kasb nomlari (HH.uz qidiruv uchun)
SEARCH_QUERIES = {
    "frontend_development": ["Frontend разработчик", "Frontend developer", "React разработчик"],
    "backend_development": ["Backend разработчик", "Python разработчик", "Java разработчик"],
    "mobile_development": ["Мобильный разработчик", "iOS разработчик", "Android разработчик"],
    "data_analytics": ["Data Analyst", "Аналитик данных"],
    "data_science": ["Data Scientist", "ML Engineer"],
    "ai_engineering": ["AI Engineer", "ML разработчик"],
    "devops_cloud": ["DevOps", "DevOps инженер"],
    "cybersecurity": ["Информационная безопасность", "Security Engineer"],
    "qa_automation": ["QA инженер", "Тестировщик", "QA Automation"],
    "ui_ux_design": ["UI/UX дизайнер", "UX дизайнер"],
    "graphic_design": ["Графический дизайнер"],
    "motion_design": ["Motion дизайнер", "Моушн дизайнер"],
    "smm_manager": ["SMM менеджер", "SMM специалист"],
    "performance_marketing": ["Performance маркетолог", "Таргетолог"],
    "seo": ["SEO специалист", "SEO специалист"],
    "content_marketing": ["Контент менеджер", "Копирайтер"],
    "product_management": ["Product Manager", "Продакт менеджер"],
    "project_management": ["Project Manager", "Проектный менеджер"],
    "business_analysis": ["Бизнес аналитик", "Business Analyst"],
    "it_b2b_sales": ["IT Sales", "Менеджер по продажам IT"],
    "customer_success": ["Customer Success", "Менеджер по работе с клиентами"],
}


def fetch_salaries(query: str, per_page: int = 100) -> list:
    """HH.uz'dan vakansiyalarni oladi."""
    salaries = []
    headers = {
        "User-Agent": "Qadam.io/1.0 (career intelligence platform)",
    }
    params = {
        "text": query,
        "area": 97,  # Uzbekistan
        "per_page": per_page,
        "only_with_salary": "true",
    }

    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(HH_API, params=params, headers=headers)
            if r.status_code != 200:
                return []
            data = r.json()
            items = data.get("items", [])
            for item in items:
                sal = item.get("salary")
                if not sal:
                    continue
                # Faqat so'mdagi maoshlar
                if sal.get("currency") != "UZS":
                    continue
                frm = sal.get("from") or 0
                to = sal.get("to") or 0
                if frm and to:
                    avg = (frm + to) // 2
                elif frm:
                    avg = frm
                elif to:
                    avg = to
                else:
                    continue
                salaries.append(avg)
    except Exception as e:
        print(f"    Xato: {e}")
    return salaries


def classify_by_level(salaries: list) -> dict:
    """Maoshlarni junior/mid/senior ga ajratadi."""
    if not salaries:
        return {}

    sorted_sal = sorted(salaries)
    n = len(sorted_sal)

    # Median va kvartillar asosida
    junior = sorted_sal[: n // 3] if n >= 3 else sorted_sal
    mid = sorted_sal[n // 3 : 2 * n // 3] if n >= 3 else sorted_sal
    senior = sorted_sal[2 * n // 3 :] if n >= 3 else sorted_sal

    def stats(arr):
        if not arr:
            return {"min": 0, "median": 0, "max": 0}
        return {
            "min": round(statistics.median(arr[: max(1, len(arr) // 3)]) / 1000) * 1000,
            "median": round(statistics.median(arr) / 1000) * 1000,
            "max": round(statistics.median(arr[-max(1, len(arr) // 3) :]) / 1000) * 1000,
        }

    return {
        "junior": stats(junior),
        "mid": stats(mid),
        "senior": stats(senior),
        "sample_size": n,
    }


def main():
    print("=" * 60)
    print("Qadam.io — HH.uz maosh scraping")
    print("=" * 60)
    print()

    results = {}

    for career, queries in SEARCH_QUERIES.items():
        print(f"[{career}] qidirilmoqda...")
        all_salaries = []
        for q in queries:
            sals = fetch_salaries(q, per_page=50)
            all_salaries.extend(sals)
            time.sleep(0.5)  # Rate limit

        if all_salaries:
            classified = classify_by_level(all_salaries)
            results[career] = classified
            stats = classified
            print(f"    Topildi: {stats['sample_size']} vakansiya")
            print(f"    Junior: {stats['junior']['min']:,}–{stats['junior']['max']:,}")
            print(f"    Mid: {stats['mid']['min']:,}–{stats['mid']['max']:,}")
            print(f"    Senior: {stats['senior']['min']:,}–{stats['senior']['max']:,}")
        else:
            print(f"    Malumot yoq")
        print()

    # Natijani saqlash
    out = Path("qadam/backend/data/salary_real.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({
            "source": "HH.uz API",
            "scraped_at": time.strftime("%Y-%m-%d"),
            "area": "Uzbekistan (97)",
            "salaries": results,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("=" * 60)
    print(f"Natija saqlandi: {out}")
    print(f"Jami: {len(results)} ta kasb")
    print("=" * 60)


if __name__ == "__main__":
    main()