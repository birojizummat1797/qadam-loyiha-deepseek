# -*- coding: utf-8 -*-
"""QADAM Roadmap KB v2.0 — Part B: data_analytics, ui_ux_design, smm_manager."""
import json
from pathlib import Path

ROOT = Path("qadam/backend/data")
CAREERS = {}

# ═══════════════════════════════════════════════════════════
# 1. DATA ANALYTICS
# ═══════════════════════════════════════════════════════════
CAREERS["data_analytics"] = {
    "uz": "Data Analytics",
    "cluster": "data_ai",
    "cluster_uz": "Data & AI",
    "why": "Sizning tahliliy fikrlashingiz, detallarga e'tiboringiz va tizimli yondashuvingiz bu sohada eng qimmatli ko'nikmalar. Data Analyst — bu biznes qarorlarini raqamlar bilan asoslash san'ati.",
    "b_point": {
        "junior_salary_uzs": "4-7 mln so'm",
        "remote_salary_usd": "$500-1200/oy",
        "outcomes": [
            "Junior Data Analyst lavozimi",
            "Fintech/bank/e-commerce'da ishlash",
            "Remote analytics ishi",
            "Data Science'ga o'tish imkoniyati",
        ],
        "next_step": "Data Science yoki Analytics Engineer → 1-2 yil",
    },
    "stages": [
        {"n": 0, "name": "SETUP", "name_uz": "Tayyorgarlik", "weeks": 1, "role": "Tadqiqotchi", "daily_hours": "1-2 soat",
         "graduate_by": "Muhit tayyor",
         "constraints": [
             ["Excel'dan boshqa bilmayman", "SQL va visualization'dan boshlash"],
             ["Statistika qiyin", "Boshlang'ich daraja yetarli"],
         ],
         "daily_focus": [
             "30 daqiqa: Excel chuqur o'rganish (pivot, lookup)",
             "30 daqiqa: SQL nima — video",
             "30 daqiqa: Kaggle akkaunt ochish",
         ],
         "signs_right": ["Excel pivot jadval qila olaman", "Kaggle akkaunt bor"],
         "signs_wrong": ["Python'ga erta o'tish", "Statistikani yodlash"],
         "graduate_criteria": ["Excel chuqur", "SQL nima tushunaman", "Kaggle akkaunt"],
         "challenges": ["Statistika qo'rqitiradi"],
         "skills_gained": ["Excel advanced", "SQL basics", "Kaggle"]},
        {"n": 1, "name": "EXCEL + SQL", "name_uz": "Asosiy vositalar", "weeks": 4, "role": "O'rganuvchi", "daily_hours": "2 soat",
         "graduate_by": "SQL querylar va Excel tahlil",
         "constraints": [
             ["SQL chalkash", "SELECT → JOIN tartibida"],
             ["Katta dataset qo'rqitadi", "100 qatordan boshlash"],
         ],
         "daily_focus": [
             "30 daqiqa: Excel formula + pivot",
             "60 daqiqa: SQL query yozish",
             "30 daqiqa: Dataset bilan amaliyot",
         ],
         "signs_right": ["SELECT, WHERE, GROUP BY yozaman", "Excel'da dashboard quraman"],
         "signs_wrong": ["Hammani bir vaqtda o'rganish", "Faqat video"],
         "graduate_criteria": [
             "Excel: pivot, VLOOKUP, chart",
             "SQL: SELECT, JOIN, GROUP BY, HAVING",
             "10+ SQL query mashqi",
             "Kaggle'da 2-3 dataset tahlil",
         ],
         "challenges": ["SQL JOIN tushunish", "Excel formulalari"],
         "skills_gained": ["Excel", "SQL asoslari", "Data thinking"]},
        {"n": 2, "name": "VISUALIZATION", "name_uz": "Vizualizatsiya", "weeks": 6, "role": "Amaliyotchi", "daily_hours": "2-3 soat",
         "graduate_by": "Dashboard va statistik tahlil",
         "constraints": [
             ["Tableau pullik", "Power BI yoki Google Data Studio (bepul)"],
             ["Statistika tushunmayman", "Mean, median, korrelyatsiya yetarli"],
         ],
         "daily_focus": [
             "60 daqiqa: Tableau yoki Power BI mashqi",
             "60 daqiqa: Statistik tushunchalar",
             "60 daqiqa: Dashboard loyiha",
         ],
         "signs_right": [
             "Tableau'da dashboard quraman",
             "Mean, median, mode tushunaman",
             "Korrelyatsiya va trend tahlil qila olaman",
         ],
         "signs_wrong": ["Faqat chiroyli chart qilish", "Statistikani tushunmaslik"],
         "graduate_criteria": [
             "Tableau yoki Power BI'da 3+ dashboard",
             "Statistika asoslari",
             "Korrelyatsiya, distribution tahlil",
             "Business case study",
         ],
         "challenges": ["Statistika — sabr kerak", "Dashboard dizayni"],
         "skills_gained": ["Tableau", "Power BI", "Statistika", "Business sense"]},
        {"n": 3, "name": "PORTFOLIO", "name_uz": "Portfolio loyihalar", "weeks": 6, "role": "Builder", "daily_hours": "3 soat",
         "graduate_by": "3-4 real loyiha",
         "constraints": [
             ["Loyiha g'oyasi yo'q", "Ochiq datasetlar (Kaggle, UZ Stat)"],
             ["Katta loyiha qo'rqitadi", "Kichikdan boshlash"],
         ],
         "daily_focus": [
             "120 daqiqa: Loyiha bilan ishlash",
             "30 daqiqa: Python pandas asoslari",
             "30 daqiqa: Portfolio yozish (case study)",
         ],
         "signs_right": [
             "3-4 portfolio loyiha",
             "Har biri biznes savolga javob beradi",
             "Storytelling bilan taqdim etish",
         ],
         "signs_wrong": ["Ko'chirilgan loyihalar", "Dataset bilan cheklanish"],
         "graduate_criteria": [
             "3-4 portfolio loyiha (GitHub + Tableau Public)",
             "Python pandas asoslari",
             "Case study yozilgan",
             "Business tushuncha",
         ],
         "challenges": ["Loyiha tanlash", "Storytelling"],
         "skills_gained": ["Python pandas", "Storytelling", "Portfolio"]},
        {"n": 4, "name": "JOB READY", "name_uz": "Ishga tayyorlanish", "weeks": 4, "role": "Candidate", "daily_hours": "3 soat",
         "graduate_by": "Junior Data Analyst offer",
         "constraints": [
             ["SQL test qiyin", "LeetCode SQL mashqi"],
             ["Business tushunmayman", "Case study o'rganish"],
         ],
         "daily_focus": [
             "60 daqiqa: SQL/Python mashqi",
             "60 daqiqa: Portfolio polish",
             "60 daqiqa: Ariza va LinkedIn",
         ],
         "signs_right": ["Portfolio tayyor", "10+ ariza", "Texnik suhbatdan o'tdim"],
         "signs_wrong": ["Faqat mahalliy ariza", "Portfolio'siz"],
         "graduate_criteria": ["Portfolio tayyor", "10+ ariza", "1+ texnik suhbat", "SQL test o'tish"],
         "challenges": ["Rejectlar", "Case study savollari"],
         "skills_gained": ["Texnik suhbat", "Business analytics", "Storytelling"]},
    ],
    "calendar_30d": [
        {"w": 1, "theme": "Excel chuqur", "days": [
            "Du: Excel interfeys, katak, formulalar",
            "Se: Sort, filter, conditional formatting",
            "Ch: VLOOKUP, INDEX-MATCH",
            "Pa: Pivot table",
            "Ju: Chart va visualization",
            "Sh: Amaliyot: savdo dashboard",
            "Ya: Dam",
        ]},
        {"w": 2, "theme": "SQL asoslari", "days": [
            "Du: SELECT, WHERE",
            "Se: ORDER BY, LIMIT",
            "Ch: GROUP BY, HAVING",
            "Pa: INNER JOIN",
            "Ju: LEFT/RIGHT JOIN",
            "Sh: Amaliyot: Kaggle dataset",
            "Ya: Dam",
        ]},
        {"w": 3, "theme": "Statistika + vizualizatsiya", "days": [
            "Du: Mean, median, mode",
            "Se: Distribution, outlier",
            "Ch: Korrelyatsiya",
            "Pa: Tableau o'rnatish",
            "Ju: Tableau dashboard",
            "Sh: Amaliyot: savdo tahlil",
            "Ya: Dam",
        ]},
        {"w": 4, "theme": "Loyiha + portfolio", "days": [
            "Du: Dataset tanlash",
            "Se: Data tozalash",
            "Ch: SQL bilan tahlil",
            "Pa: Tableau dashboard",
            "Ju: Insights yozish",
            "Sh: Portfolio case study",
            "Ya: GitHub'ga push",
        ]},
    ],
    "first_3_actions": [
        "Excel'ni ochib, pivot jadval bilan tanishish (bugun, 20 daqiqa)",
        "Kaggle akkaunt ochish (bugun, 10 daqiqa)",
        "Birinchi SQL query yozish (bugun, 30 daqiqa)",
    ],
    "mentor_path": [
        "Telegram: @data_uz, @uzbekistan_ds",
        "Local: Data meetup'lar Toshkentda",
        "Kaggle competitions",
    ],
    "resources": [
        {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn", "lang": "EN"},
        {"name": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "lang": "EN"},
        {"name": "Tableau Public", "url": "https://public.tableau.com/", "lang": "EN"},
    ],
    "milestones": [
        {"week": 1, "milestone": "Birinchi pivot jadval"},
        {"week": 4, "milestone": "Birinchi SQL query"},
        {"week": 10, "milestone": "Birinchi dashboard"},
        {"week": 16, "milestone": "Portfolio loyiha"},
        {"week": 20, "milestone": "Junior offer"},
    ],
}

# ═══════════════════════════════════════════════════════════
# 2. UI/UX DESIGN
# ═══════════════════════════════════════════════════════════
CAREERS["ui_ux_design"] = {
    "uz": "UI/UX Design",
    "cluster": "design_creative",
    "cluster_uz": "Dizayn",
    "why": "Sizning ijodiy didingiz, vizual mantig'ingiz va foydalanuvchi ehtiyojini tushunishingiz bu sohada asosiy qurolingiz. UI/UX — estetika va psixologiya kesishmasi.",
    "b_point": {
        "junior_salary_uzs": "3-7 mln so'm",
        "remote_salary_usd": "$500-1500/oy",
        "outcomes": [
            "Junior UI/UX Designer lavozimi",
            "Freelance dizayn loyihalar",
            "Startup'larda Product Designer",
            "Portfolio case study'lar",
        ],
        "next_step": "Product Designer → 1-2 yil",
    },
    "stages": [
        {"n": 0, "name": "SETUP", "name_uz": "Tayyorgarlik", "weeks": 1, "role": "Tadqiqotchi", "daily_hours": "1-2 soat",
         "graduate_by": "Figma o'rnatilgan",
         "constraints": [["Dizayn bilmayman", "Dribbble, Behance'dan boshlash"], ["Noutbuk yo'q", "Kutubxona yoki do'st"]],
         "daily_focus": ["30 daqiqa: Figma o'rnatish", "60 daqiqa: Mashhur dizaynlarni tahlil", "30 daqiqa: Birinchi ekran"],
         "signs_right": ["Figma o'rnatildi", "Dribbble akkaunt", "5+ dizayn saqlandi"],
         "signs_wrong": ["Illustrator'ga o'tish", "Kursga yozilish"],
         "graduate_criteria": ["Figma akkaunt", "Dribbble akkaunt", "Birinchi ekran"],
         "challenges": ["Qaysi vositadan boshlash"],
         "skills_gained": ["Figma interface", "Vizual kuzatuv"]},
        {"n": 1, "name": "FIGMA BASICS", "name_uz": "Figma asoslari", "weeks": 4, "role": "O'rganuvchi", "daily_hours": "2 soat",
         "graduate_by": "5-10 ekran dizayn",
         "constraints": [["Rang tanlash qiyin", "Material/Human Interface palette"], ["Tipografiya bilmayman", "Google Fonts + Type Scale"]],
         "daily_focus": ["60 daqiqa: Figma mashqi", "60 daqiqa: Dizayn nazariyasi", "30 daqiqa: Mashhur saytlar tahlil"],
         "signs_right": ["Auto-layout ishlataman", "Component yarata olaman", "Rang uyg'unligi"],
         "signs_wrong": ["Faqat Dribbble ko'rish", "Mashq qilmaslik"],
         "graduate_criteria": ["Figma: auto-layout, component", "Rang nazariyasi", "Tipografiya", "5-10 UI mashqi"],
         "challenges": ["Rang tanlash", "Layout chalkash"],
         "skills_gained": ["Figma", "Rang nazariyasi", "Tipografiya"]},
        {"n": 2, "name": "UX FUNDAMENTALS", "name_uz": "UX asoslari", "weeks": 6, "role": "Amaliyotchi", "daily_hours": "3 soat",
         "graduate_by": "User research va prototyping",
         "constraints": [["User research qiyin", "5 ta do'st bilan intervyu"], ["Wireframe chalkash", "Oddiy sketch'dan boshlash"]],
         "daily_focus": ["60 daqiqa: User flow", "60 daqiqa: Wireframe", "60 daqiqa: Prototype"],
         "signs_right": ["User interview o'tkazdim", "Persona yarata olaman", "Interactive prototype"],
         "signs_wrong": ["UX'ni tashlab vizual dizaynga o'tish", "User'siz dizayn"],
         "graduate_criteria": ["User research asoslari", "Persona, journey map", "Wireframe, prototype", "1-2 case study"],
         "challenges": ["User bilan ishlash", "Prototype murakkab"],
         "skills_gained": ["User research", "Wireframe", "Prototype", "Design systems"]},
        {"n": 3, "name": "PORTFOLIO", "name_uz": "Portfolio case study", "weeks": 8, "role": "Builder", "daily_hours": "3 soat",
         "graduate_by": "3-4 case study",
         "constraints": [["Real loyiha yo'q", "Bepul yoki arzon mijoz"], ["Case study qanday yozish", "UX Collective'dan o'rganish"]],
         "daily_focus": ["120 daqiqa: Case study yozish", "60 daqiqa: Figma polish", "60 daqiqa: Real mijoz loyiha"],
         "signs_right": ["3-4 chuqur case study", "Behance/Dribbble profil", "1+ real mijoz"],
         "signs_wrong": ["Faqat chiroyli ekranlar", "Tadqiqotsiz case study"],
         "graduate_criteria": ["3-4 case study", "Behance/Dribbble profil", "1+ real loyiha", "Portfolio sayt"],
         "challenges": ["Real mijoz topish", "Case study yozish"],
         "skills_gained": ["Case study", "Portfolio", "Mijoz bilan ishlash"]},
        {"n": 4, "name": "JOB READY", "name_uz": "Ishga tayyorlanish", "weeks": 4, "role": "Candidate", "daily_hours": "3 soat",
         "graduate_by": "Junior UI/UX offer",
         "constraints": [["Design challenge qiyin", "Dribbble challenge mashqi"], ["Reject qo'rquvi", "10 ariza → 1 offer"]],
         "daily_focus": ["60 daqiqa: Portfolio polish", "60 daqiqa: Design challenge", "60 daqiqa: Networking"],
         "signs_right": ["Portfolio tayyor", "10+ ariza", "Design test o'tdim"],
         "signs_wrong": ["Portfolio'siz ariza", "Faqat mahalliy"],
         "graduate_criteria": ["Portfolio tayyor", "10+ ariza", "1+ design test", "Portfolio sayt"],
         "challenges": ["Rejectlar", "Design challenge"],
         "skills_gained": ["Portfolio", "Design test", "Networking"]},
    ],
    "calendar_30d": [
        {"w": 1, "theme": "Figma + asoslar", "days": ["Du: Figma interfeys", "Se: Frame, shape", "Ch: Text, typography", "Pa: Auto-layout", "Ju: Component", "Sh: 5 ekran mashqi", "Ya: Dam"]},
        {"w": 2, "theme": "Rang va dizayn", "days": ["Du: Rang nazariyasi", "Se: Gradient", "Ch: Icons", "Pa: Images", "Ju: Material Design", "Sh: Birinchi app dizayn", "Ya: Dam"]},
        {"w": 3, "theme": "UX asoslari", "days": ["Du: User research", "Se: Persona", "Ch: User flow", "Pa: Wireframe", "Ju: Prototype", "Sh: Case study #1", "Ya: Dam"]},
        {"w": 4, "theme": "Portfolio", "days": ["Du: Dizayn sayqal", "Se: Mockup", "Ch: Case study yozish", "Pa: Behance profil", "Ju: Portfolio sayt", "Sh: Real mijoz topish", "Ya: Portfolio live"]},
    ],
    "first_3_actions": ["Figma akkaunt ochish (bugun, 5 daqiqa)", "Dribbble'dan 10 ta dizayn saqlash (bugun, 20 daqiqa)", "Birinchi mobil ekran dizayn (bugun, 40 daqiqa)"],
    "mentor_path": ["Telegram: @uzdesign, @uiux_uz", "Dribbble weekly challenges", "Local: Tashkent Design Meetup"],
    "resources": [
        {"name": "Figma Learn", "url": "https://help.figma.com/", "lang": "EN"},
        {"name": "Refactoring UI", "url": "https://www.refactoringui.com/", "lang": "EN"},
        {"name": "Laws of UX", "url": "https://lawsofux.com/", "lang": "EN"},
    ],
    "milestones": [
        {"week": 1, "milestone": "Birinchi ekran"},
        {"week": 4, "milestone": "10+ ekran portfolio"},
        {"week": 10, "milestone": "Birinchi case study"},
        {"week": 18, "milestone": "Behance portfolio"},
        {"week": 22, "milestone": "Junior offer"},
    ],
}

# ═══════════════════════════════════════════════════════════
# 3. SMM MANAGER
# ═══════════════════════════════════════════════════════════
CAREERS["smm_manager"] = {
    "uz": "SMM Manager",
    "cluster": "digital_marketing",
    "cluster_uz": "Marketing",
    "why": "Sizning kreativligingiz va odamlar bilan muloqot qobiliyatingiz bu sohada muvaffaqiyat keltiradi. SMM — ham ijod, ham tahlil, ham psixologiya.",
    "b_point": {
        "junior_salary_uzs": "3-6 mln so'm",
        "remote_salary_usd": "$300-1000/oy",
        "outcomes": [
            "Junior SMM Manager lavozimi",
            "Freelance mijozlar (3-5 ta)",
            "Agentlikda ishlash",
            "O'z brendini rivojlantirish",
        ],
        "next_step": "Performance Marketing yoki Brand Strategy",
    },
    "stages": [
        {"n": 0, "name": "SETUP", "name_uz": "Tayyorgarlik", "weeks": 1, "role": "Tadqiqotchi", "daily_hours": "1-2 soat",
         "graduate_by": "Akkaunt va kontent reja",
         "constraints": [["Ijod qiyin", "Mashhur postlardan andoza"], ["Smartfon yetarli", "Canva + shaxsiy akkaunt"]],
         "daily_focus": ["30 daqiqa: SMM asoslari", "30 daqiqa: Canva o'rganish", "60 daqiqa: Kontent tahlil"],
         "signs_right": ["Canva o'rnatildi", "3+ sahifa tahlil qildim", "Kontent g'oyalar bor"],
         "signs_wrong": ["Faqat Story ko'rish", "Post chiqarmaslik"],
         "graduate_criteria": ["Canva akkaunt", "Kontent tahlil", "Post g'oyalar"],
         "challenges": ["Ijod boshlash", "Nimadan boshlash"],
         "skills_gained": ["Canva", "Content thinking"]},
        {"n": 1, "name": "CANVA + CONTENT", "name_uz": "Vizual va kontent", "weeks": 3, "role": "O'rganuvchi", "daily_hours": "2 soat",
         "graduate_by": "10+ post",
         "constraints": [["Dizayn qobiliyati yo'q", "Canva templates"], ["Copywriting bilmayman", "AIDA formulasini o'rganish"]],
         "daily_focus": ["30 daqiqa: Dizayn asoslari", "30 daqiqa: Copywriting", "60 daqiqa: Post tayyorlash"],
         "signs_right": ["10+ post tayyor", "Canva'da erkin ishlayman", "Copywriting asoslari"],
         "signs_wrong": ["Ko'chirilgan kontent", "Faqat video"],
         "graduate_criteria": ["Canva: post, story, reel", "10+ kontent tayyorlangan", "Copywriting formulalari"],
         "challenges": ["Ijod quruqligi", "Dizayn"],
         "skills_gained": ["Canva advanced", "Copywriting", "Content creation"]},
        {"n": 2, "name": "PLATFORM BASICS", "name_uz": "Platformalar", "weeks": 4, "role": "Amaliyotchi", "daily_hours": "2 soat",
         "graduate_by": "30-kunlik kontent reja",
         "constraints": [["Algoritm o'zgaradi", "Instagram/Meta Blueprint"], ["Analitika qiyin", "Meta Insights'dan boshlash"]],
         "daily_focus": ["30 daqiqa: Instagram/TikTok", "30 daqiqa: Telegram", "60 daqiqa: Kontent post"],
         "signs_right": ["Post schedule tuzaman", "Algoritm tushunaman", "Story/Reels ishlataman"],
         "signs_wrong": ["Faqat Story", "Scheduling'siz"],
         "graduate_criteria": ["3+ platformada post", "Scheduling (Later/Buffer)", "Analytics ko'ra olaman"],
         "challenges": ["Algoritm tushunish", "Kontent reja"],
         "skills_gained": ["Meta platforms", "Analytics", "Content scheduling"]},
        {"n": 3, "name": "REAL CLIENT", "name_uz": "Birinchi mijoz", "weeks": 6, "role": "Builder", "daily_hours": "3 soat",
         "graduate_by": "1+ real mijoz portfolio",
         "constraints": [["Mijoz qanday topish", "Do'st, oila, kichik biznes"], ["Case study yozish", "Before/after screenshot"]],
         "daily_focus": ["30 daqiqa: Mijoz aloqa", "60 daqiqa: Kontent", "60 daqiqa: Analytics"],
         "signs_right": ["1+ real mijoz", "Kontent reja tayyor", "Case study yozdim"],
         "signs_wrong": ["Faqat shaxsiy akkaunt", "Natijasiz postlar"],
         "graduate_criteria": ["1+ real mijoz", "Kontent reja tuzilgan", "3+ case study", "Analitika bilan hisobot"],
         "challenges": ["Mijoz topish", "Natija kutish"],
         "skills_gained": ["Client work", "Case study", "Reporting"]},
        {"n": 4, "name": "JOB READY", "name_uz": "Ishga tayyorlanish", "weeks": 4, "role": "Candidate", "daily_hours": "3 soat",
         "graduate_by": "Junior SMM offer",
         "constraints": [["Narx qancha?", "Mahalliy bozor: 3-6 mln"], ["Reject", "10 murojaat → 1 mijoz"]],
         "daily_focus": ["60 daqiqa: Portfolio", "60 daqiqa: Ariza", "60 daqiqa: Networking"],
         "signs_right": ["Portfolio tayyor", "10+ ariza", "1+ mijoz"],
         "signs_wrong": ["Portfolio'siz", "Narxni past qo'yish"],
         "graduate_criteria": ["Portfolio 5+ case study", "10+ ariza/murojaat", "3-5 mijoz", "Narx belgilangan"],
         "challenges": ["Narx", "Reject"],
         "skills_gained": ["Selling", "Portfolio", "Client management"]},
    ],
    "calendar_30d": [
        {"w": 1, "theme": "Canva + asoslar", "days": ["Du: Canva interfeys", "Se: Post template", "Ch: Story design", "Pa: Reels template", "Ju: Rang + shrift", "Sh: 10 post tayyor", "Ya: Dam"]},
        {"w": 2, "theme": "Copywriting", "days": ["Du: AIDA formula", "Se: PAS formula", "Ch: Hook yozish", "Pa: CTA yozish", "Ju: Storytelling", "Sh: 10 post copy", "Ya: Dam"]},
        {"w": 3, "theme": "Platformalar", "days": ["Du: Instagram algoritm", "Se: TikTok", "Ch: Telegram", "Pa: YouTube Shorts", "Ju: Facebook", "Sh: 30 kunlik reja", "Ya: Dam"]},
        {"w": 4, "theme": "Birinchi mijoz", "days": ["Du: Portfolio sahifasi", "Se: Mijoz topish", "Ch: Pitch yozish", "Pa: Birinchi hamkorlik", "Ju: Kontent reja", "Sh: Analytics hisobot", "Ya: Case study"]},
    ],
    "first_3_actions": ["Canva akkaunt ochish (bugun, 5 daqiqa)", "3 ta raqib sahifani tahlil qilish (bugun, 30 daqiqa)", "Birinchi 3 ta postni tayyorlash (bugun, 45 daqiqa)"],
    "mentor_path": ["Telegram: @smm_uz, @marketing_uz", "Meta Blueprint", "Local: Marketing meetup'lar"],
    "resources": [
        {"name": "Meta Blueprint", "url": "https://www.facebook.com/business/learn", "lang": "EN"},
        {"name": "Canva Design School", "url": "https://www.canva.com/designschool/", "lang": "EN"},
        {"name": "HubSpot Academy", "url": "https://academy.hubspot.com/", "lang": "EN"},
    ],
    "milestones": [
        {"week": 1, "milestone": "10 post tayyor"},
        {"week": 3, "milestone": "30 kunlik reja"},
        {"week": 6, "milestone": "Birinchi mijoz"},
        {"week": 12, "milestone": "3+ mijoz portfolio"},
        {"week": 16, "milestone": "Junior offer"},
    ],
}


def main():
    out_file = ROOT / "roadmap_kb_v2_part_b.json"
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "version": "v2.0",
            "note": "Part B — data_analytics, ui_ux_design, smm_manager",
            "careers": CAREERS,
        }, f, ensure_ascii=False, indent=2)
    print("=" * 60)
    print("QADAM Roadmap Part B — yaratildi")
    print("=" * 60)
    print("  [OK] " + str(out_file))
    print("  Careers: " + ", ".join(CAREERS.keys()))
    print()
    print("Keyingi qadam: qadam-roadmap-c.py (birlashtirish + frontend)")


if __name__ == "__main__":
    main()