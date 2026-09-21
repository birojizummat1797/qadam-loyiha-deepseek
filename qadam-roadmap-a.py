# -*- coding: utf-8 -*-
"""QADAM Roadmap KB v2.0 — Part A: foundation + frontend."""
import json
from pathlib import Path

ROOT = Path("qadam/backend/data")

CAREERS = {}

# ═══════════════════════════════════════════════════════════
# 1. FOUNDATION PROGRAMMING
# ═══════════════════════════════════════════════════════════
CAREERS["foundation_programming"] = {
    "uz": "Foundation Programming",
    "cluster": "software",
    "cluster_uz": "Dasturlash",
    "why": "Dasturlash asoslari — har qanday IT yo'nalishga kirish eshigi. Bu bosqich sizga mantiqiy fikrlash, muammoni bo'laklarga bo'lish va kod yozish tajribasini beradi.",
    "b_point": {
        "junior_salary_uzs": "3-6 mln so'm",
        "remote_salary_usd": "$300-600/oy",
        "outcomes": [
            "Junior dasturchi lavozimiga ariza berish imkoniyati",
            "Keyingi yo'nalish (Frontend/Backend/Mobile) tanlash imkoniyati",
            "GitHub'da 3-5 ta loyiha",
            "Texnik suhbatga tayyorlik",
        ],
        "next_step": "Yo'nalish tanlash (Frontend/Backend/Mobile) → Stage 5",
    },
    "stages": [
        {
            "n": 0, "name": "ORIENTATION", "name_uz": "Yo'nalishni aniqlash",
            "weeks": 1, "role": "Tadqiqotchi", "daily_hours": "1-2 soat",
            "graduate_by": "Vositalar tayyor, reja aniq",
            "constraints": [
                ["Noutbuk yo'q", "Kutubxona, do'st, ijaraga olish, grantlar"],
                ["Qaysi tildan boshlashni bilmayman", "Python yoki JavaScript — ikkalasi ham mos"],
                ["Qo'rquv: 'Men qila olamanmi?'", "Har kuni 30 daqiqa kod yozish — 7 kunda o'tadi"],
            ],
            "daily_focus": [
                "30 daqiqa: Python yoki JS haqida video",
                "30 daqiqa: VS Code o'rnatish va sozlash",
                "30 daqiqa: Birinchi 'Hello World'",
                "30 daqiqa: GitHub akkaunt ochish",
            ],
            "signs_right": [
                "VS Code o'rnatildi va ishlayapti",
                "Birinchi kod yozildi va ishga tushdi",
                "GitHub akkaunt ochildi",
            ],
            "signs_wrong": [
                "Faqat video ko'rish, kod yozmaslik",
                "Qaysi tildan boshlashni 5 kundan ko'p o'ylash",
                "Boshqa kursga o'tib ketish",
            ],
            "graduate_criteria": [
                "VS Code + Git o'rnatilgan",
                "Birinchi 'Hello World' ishga tushdi",
                "GitHub akkaunt mavjud",
                "Kuniga 1 soat o'rganish odat",
            ],
            "challenges": [
                "Faqat nazariya — kod yozmaslik",
                "Mukammal kursni qidirish — vaqt yo'qotish",
            ],
            "skills_gained": ["VS Code muhiti", "Git asoslari", "Terminal asoslari"],
        },
        {
            "n": 1, "name": "SYNTAX BASICS", "name_uz": "Sintaksis asoslari",
            "weeks": 4, "role": "O'rganuvchi", "daily_hours": "1-2 soat",
            "graduate_by": "Ozgaruvchilar, shartlar, tsikllar",
            "constraints": [
                ["Ingliz tili past", "O'zbek/rus tilidagi kurslar bor"],
                ["Vaqt kam", "Ertalab 1 soat yoki kechqurun 1 soat"],
                ["Motivatsiya tushadi", "Har kuni amaliyot — progress ko'rinadi"],
            ],
            "daily_focus": [
                "20 daqiqa: Yangi tushunchani o'rganish",
                "40 daqiqa: Kod yozish mashqi",
                "20 daqiqa: Xatolarni tuzatish",
                "40 daqiqa: Amaliy mini-loyiha",
            ],
            "signs_right": [
                "Ozgaruvchilar va shartlarni tushunaman",
                "50+ qator kod yozishim mumkin",
                "Xatoliklar chiqsa, o'zim tuzataman",
            ],
            "signs_wrong": [
                "Kod yozmasdan faqat video ko'rish",
                "Xatolikdan qo'rqib, yordam so'rash",
                "Kursning yarmida tashlab ketish",
            ],
            "graduate_criteria": [
                "Ozgaruvchilar, shartlar (if/else), tsikllar (for/while) tushunasiz",
                "Funksiyalar yozishni bilasiz",
                "Massiv va obyektlar bilan ishlay olasiz",
                "20+ ta kichik mashq bajarildi",
            ],
            "challenges": [
                "2-haftada 'qiyin' hissi — bu normal",
                "Xatoliklar ko'p — sabr kerak",
            ],
            "skills_gained": ["Sintaksis", "Mantiqiy fikrlash", "Debugging"],
        },
        {
            "n": 2, "name": "PROBLEM SOLVING", "name_uz": "Muammo hal qilish",
            "weeks": 8, "role": "Amaliyotchi", "daily_hours": "2 soat",
            "graduate_by": "LeetCode Easy va algoritmik fikrlash",
            "constraints": [
                ["Murakkab masalalar qo'rqitadi", "Easy darajadan boshla, keyin Medium"],
                ["Vaqt kam", "Kuniga 1 masala — 8 haftada 56 masala"],
                ["Algoritm bilmayman", "Har kuni 1 yangi algoritm o'rganish"],
            ],
            "daily_focus": [
                "30 daqiqa: Yangi algoritm o'rganish",
                "60 daqiqa: 1-2 masala yechish (LeetCode Easy)",
                "30 daqiqa: Kodni GitHub'ga yuklash",
            ],
            "signs_right": [
                "LeetCode'da 50+ masala yechildi",
                "Noma'lum masalaga yondasha olaman",
                "Big O notation tushunaman",
            ],
            "signs_wrong": [
                "Masala yechmasdan ko'chirib olish",
                "Bir xil turdagi masalalarga yopishib qolish",
                "Algoritmni tushunmasdan yodlash",
            ],
            "graduate_criteria": [
                "50+ LeetCode Easy masala yechildi",
                "Asosiy algoritmlar: sort, search, hash",
                "Ma'lumotlar tuzilmasi: array, object, set",
                "Git bilan ishlashni bilasiz",
            ],
            "challenges": [
                "Bir masalani 2 soat yechish — normal",
                "Yechilmay qolgan masala — keyin qaytish",
            ],
            "skills_gained": ["Algoritmik fikrlash", "Git", "Problem solving"],
        },
        {
            "n": 3, "name": "MINI PROJECTS", "name_uz": "Kichik loyihalar",
            "weeks": 8, "role": "Builder", "daily_hours": "2-3 soat",
            "graduate_by": "3-5 ta real loyiha",
            "constraints": [
                ["Loyiha g'oyasi yo'q", "Tutorial loyihalardan boshlash"],
                ["Mukammal bo'lmasa qo'rqaman", "MVP tushunchasi — 20% funksiya, 80% qiymat"],
                ["Vaqt kam", "Haftada 1 loyiha — 8 haftada 8 loyiha"],
            ],
            "daily_focus": [
                "30 daqiqa: Loyiha rejasini o'ylash",
                "120 daqiqa: Kod yozish",
                "30 daqiqa: GitHub'ga push",
            ],
            "signs_right": [
                "3+ loyiha GitHub'da",
                "Har biri README bilan",
                "Deploy qilingan (Vercel, Netlify)",
            ],
            "signs_wrong": [
                "Bitta loyihani 3 oy qilish",
                "README yozmaslik",
                "GitHub'ga yuklamaslik",
            ],
            "graduate_criteria": [
                "3-5 ta loyiha GitHub'da",
                "Har birida README bor",
                "Kamida 2 tasi live (deploy)",
                "Kod review qabul qiladi",
            ],
            "challenges": [
                "Mukammalchilik hissi — MVP bilan cheklanish",
                "Tutorial hell — o'zingiz kod yozishni boshlang",
            ],
            "skills_gained": ["Loyiha boshqaruvi", "Deploy", "README", "Git workflow"],
        },
        {
            "n": 4, "name": "DIRECTION CHOICE", "name_uz": "Yo'nalish tanlash",
            "weeks": 4, "role": "Candidate", "daily_hours": "2-3 soat",
            "graduate_by": "Junior ariza + texnik suhbat",
            "constraints": [
                ["Ishonchsizlik", "Portfolio va GitHub ko'rsatish"],
                ["Reject qo'rquvi", "10 ta ariza → 1 offer — normal"],
                ["Texnik suhbatga tayyor emasman", "Mock interview mashqi"],
            ],
            "daily_focus": [
                "60 daqiqa: Yo'nalish bo'yicha chuqur bilim",
                "60 daqiqa: Portfolio yaxshilash",
                "60 daqiqa: Junior vakansiyalarga ariza",
            ],
            "signs_right": [
                "Yo'nalish aniq (Frontend/Backend/Mobile)",
                "Portfolio tayyor",
                "10+ ariza yuborildi",
                "Texnik suhbatdan o'tdim",
            ],
            "signs_wrong": [
                "Barcha yo'nalishlarni bir vaqtda urinish",
                "Portfolio'siz ariza berish",
                "Rejectdan keyin tushkunlik",
            ],
            "graduate_criteria": [
                "Yo'nalish tanlandi",
                "Portfolio 4+ loyiha",
                "LinkedIn profili to'ldirilgan",
                "10+ ariza yuborilgan",
                "1+ texnik suhbat o'tkazilgan",
            ],
            "challenges": [
                "Rejectlar — 90% normal",
                "Imposter syndrome — hammada bor",
            ],
            "skills_gained": ["Texnik suhbat", "Portfolio", "Networking"],
        },
    ],
    "calendar_30d": [
        {"w": 1, "theme": "Vositalar + sintaksis", "days": [
            "Du: VS Code + Python ornatish, Hello World",
            "Se: Ozgaruvchilar, print, input",
            "Ch: Shartlar (if/else), mantiqiy operatorlar",
            "Pa: Tsikllar (for/while)",
            "Ju: Funksiyalar — birinchi yozish",
            "Sh: Amaliyot: kalkulyator",
            "Ya: Dam olish",
        ]},
        {"w": 2, "theme": "Malumot tuzilmalari", "days": [
            "Du: List va tuple",
            "Se: Dictionary va set",
            "Ch: String metodlari",
            "Pa: Xatoliklarni tutish (try/except)",
            "Ju: Modul va paket",
            "Sh: Amaliyot: todo list (CLI)",
            "Ya: Dam olish",
        ]},
        {"w": 3, "theme": "Fayllar va OOP", "days": [
            "Du: Faylni o'qish/yozish",
            "Se: JSON bilan ishlash",
            "Ch: OOP: class va object",
            "Pa: OOP: metod va inheritance",
            "Ju: Amaliyot: weather app (API)",
            "Sh: Git chuqur: branch, merge",
            "Ya: Dam olish",
        ]},
        {"w": 4, "theme": "Mini loyiha + portfolio", "days": [
            "Du: Loyiha rejasini tuzish",
            "Se: Kod yozishni boshlash",
            "Ch: Kod davom etish",
            "Pa: Test va debug",
            "Ju: README yozish",
            "Sh: GitHub'ga push + deploy",
            "Ya: Portfolio'ga qo'shish",
        ]},
    ],
    "first_3_actions": [
        "VS Code va Python'ni o'rnatish (bugun, 30 daqiqa)",
        "Birinchi 'Hello World' dasturini yozish va ishga tushirish (bugun, 15 daqiqa)",
        "GitHub akkaunt ochish va birinchi repo yaratish (bugun, 15 daqiqa)",
    ],
    "mentor_path": [
        "O'zbek Telegram guruhlar: @uzbekdev, @python_uz",
        "GitHub'da boshqa dasturchilarni kuzatish",
        "Reddit: r/learnprogramming, r/Python",
        "Local: Toshkentdagi IT-hub, coworking",
    ],
    "resources": [
        {"name": "CS50 (Harvard)", "url": "https://cs50.harvard.edu/x/", "lang": "EN"},
        {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "lang": "EN"},
        {"name": "roadmap.sh", "url": "https://roadmap.sh/", "lang": "EN"},
        {"name": "LeetCode", "url": "https://leetcode.com/", "lang": "EN"},
    ],
    "milestones": [
        {"week": 1, "milestone": "Birinchi kod ishga tushdi"},
        {"week": 4, "milestone": "50+ qator kod yozildi"},
        {"week": 8, "milestone": "Birinchi mini-loyiha tayyor"},
        {"week": 16, "milestone": "3+ loyiha GitHub'da"},
        {"week": 24, "milestone": "Birinchi texnik suhbat"},
    ],
}

# ═══════════════════════════════════════════════════════════
# 2. FRONTEND DEVELOPMENT
# ═══════════════════════════════════════════════════════════
CAREERS["frontend_development"] = {
    "uz": "Frontend Development",
    "cluster": "software",
    "cluster_uz": "Dasturlash",
    "why": "Frontend — foydalanuvchi ko'radigan qism. Sizning vizual didingiz, tizimli fikrlashingiz va foydalanuvchi ehtiyojini tushunishingiz bu yo'nalishda kuchli ustunlik beradi.",
    "b_point": {
        "junior_salary_uzs": "4-8 mln so'm",
        "remote_salary_usd": "$500-1500/oy",
        "outcomes": [
            "Junior Frontend Developer lavozimi",
            "Freelance loyihalar (Upwork, Fiverr)",
            "Startup'larda ishlash imkoniyati",
            "Remote ish (xalqaro kompaniyalar)",
        ],
        "next_step": "Middle Frontend (React/Vue chuqur) → 1-2 yil",
    },
    "stages": [
        {
            "n": 0, "name": "SETUP", "name_uz": "Tayyorgarlik",
            "weeks": 1, "role": "Tadqiqotchi", "daily_hours": "1-2 soat",
            "graduate_by": "Muhit tayyor",
            "constraints": [
                ["Noutbuk yo'q", "Kutubxona, do'st, ijaraga olish"],
                ["Dizaynni bilmayman", "Figma ornatib, oddiy mockup bilan boshlash"],
                ["Ingliz past", "MDN'ning o'zbekcha tarjimasi bor"],
            ],
            "daily_focus": [
                "30 daqiqa: VS Code va brauzer sozlash",
                "30 daqiqa: Figma akkaunt",
                "30 daqiqa: HTML teglar",
                "30 daqiqa: Birinchi sahifa",
            ],
            "signs_right": [
                "VS Code o'rnatildi",
                "Chrome DevTools bilan tanishdim",
                "Figma akkaunt bor",
            ],
            "signs_wrong": [
                "Framework'ni erta o'rganish",
                "Dizayn kursiga o'tib ketish",
            ],
            "graduate_criteria": [
                "VS Code + Live Server o'rnatilgan",
                "Brauzer DevTools bilan tanishdim",
                "Figma akkaunt mavjud",
                "GitHub akkaunt",
            ],
            "challenges": [
                "Framework tanlash vasvasasi",
                "Mukammal kursni qidirish",
            ],
            "skills_gained": ["VS Code", "Chrome DevTools", "Figma basics"],
        },
        {
            "n": 1, "name": "HTML + CSS", "name_uz": "Asosiy markup",
            "weeks": 4, "role": "O'rganuvchi", "daily_hours": "2 soat",
            "graduate_by": "Statik saytlar",
            "constraints": [
                ["CSS chalkash", "Box model, Flexbox, Grid tartib bilan"],
                ["Dizayn qobiliyati yo'q", "Mashhur saytlarni nusxalash"],
                ["Responsive qiyin", "Mobile-first yondashuv"],
            ],
            "daily_focus": [
                "30 daqiqa: Yangi teg/atribut",
                "60 daqiqa: Mashq — sahifa qurish",
                "30 daqiqa: Mobile moslashtirish",
            ],
            "signs_right": [
                "3+ statik sahifa qurildi",
                "Flexbox va Grid tushunaman",
                "Mobile'da ham yaxshi ko'rinadi",
            ],
            "signs_wrong": [
                "CSS framework'iga (Bootstrap) bog'lanib qolish",
                "Dizaynni ko'chirib olish — CSS'ni yozmaslik",
            ],
            "graduate_criteria": [
                "Semantik HTML tushunasiz",
                "Flexbox va Grid ishlatib sahifa qura olasiz",
                "Responsive dizayn (media queries)",
                "3+ statik sayt GitHub'da",
            ],
            "challenges": [
                "CSS'da chalkashish — normal",
                "Dizayn nusxalash — bosqich",
            ],
            "skills_gained": ["HTML5", "CSS3", "Flexbox", "Grid", "Responsive"],
        },
        {
            "n": 2, "name": "JAVASCRIPT", "name_uz": "JavaScript asoslari",
            "weeks": 6, "role": "Amaliyotchi", "daily_hours": "2-3 soat",
            "graduate_by": "Interaktiv sahifalar",
            "constraints": [
                ["JS qiyin ko'rinadi", "Kichikdan boshlash"],
                ["DOM tushunmayman", "Har kuni DOM mashqi"],
                ["Async/Promise chalkash", "Keyinroq — asoslardan keyin"],
            ],
            "daily_focus": [
                "30 daqiqa: Sintaksis mashqi",
                "90 daqiqa: DOM bilan ishlash",
                "60 daqiqa: Kichik loyiha",
            ],
            "signs_right": [
                "DOM elementlarini o'zgartira olaman",
                "Event listener'larni tushunaman",
                "Fetch bilan API'dan malumot olaman",
            ],
            "signs_wrong": [
                "jQuery'ga o'tib ketish",
                "React'ga erta o'tish",
                "Async'ni tushunmasdan tashlab ketish",
            ],
            "graduate_criteria": [
                "JS ES6+ sintaksisi",
                "DOM manipulation",
                "Event handling",
                "Fetch API",
                "3-5 loyiha (weather, todo, calculator)",
            ],
            "challenges": [
                "Async/Promise — 4-hafta qiyin",
                "Debugging — sabr kerak",
            ],
            "skills_gained": ["JavaScript ES6+", "DOM", "Fetch", "LocalStorage"],
        },
        {
            "n": 3, "name": "REACT", "name_uz": "Zamonaviy framework",
            "weeks": 8, "role": "Builder", "daily_hours": "3 soat",
            "graduate_by": "SPA loyihalar",
            "constraints": [
                ["JSX chalkash", "Har kuni komponent yozish"],
                ["State boshqarish qiyin", "Oddiy state → keyin Context"],
                ["Routing murakkab", "React Router bilan tanishish"],
            ],
            "daily_focus": [
                "60 daqiqa: Yangi konseptsiya",
                "120 daqiqa: Komponent yozish",
                "60 daqiqa: API integratsiya",
            ],
            "signs_right": [
                "Komponentlar yarata olaman",
                "useState va useEffect ishlataman",
                "API'dan malumot olib ko'rsataman",
            ],
            "signs_wrong": [
                "Class component'larga o'tish",
                "Redux'ga erta o'tish",
                "Faqat tutorial loyihalar",
            ],
            "graduate_criteria": [
                "React hooks chuqur",
                "React Router",
                "API bilan ishlash",
                "Tailwind CSS",
                "3+ React loyiha",
            ],
            "challenges": [
                "Props drilling — keyin Context",
                "State ko'p — useReducer keyinroq",
            ],
            "skills_gained": ["React", "Hooks", "React Router", "Tailwind", "Vite"],
        },
        {
            "n": 4, "name": "PORTFOLIO + JOB", "name_uz": "Ishga tayyorlanish",
            "weeks": 6, "role": "Candidate", "daily_hours": "3 soat",
            "graduate_by": "Junior Frontend offer",
            "constraints": [
                ["Portfolio kuchsiz", "3-4 loyiha + case study"],
                ["Reject qo'rquvi", "10 ariza → 1 offer"],
                ["Texnik suhbatga tayyor emasman", "Mock interview"],
            ],
            "daily_focus": [
                "60 daqiqa: Portfolio yaxshilash",
                "60 daqiqa: Algoritmik mashq",
                "60 daqiqa: Ariza + networking",
            ],
            "signs_right": [
                "Portfolio live va tez ishlaydi",
                "GitHub faol (har kuni commit)",
                "LinkedIn profili tayyor",
                "5+ ariza yuborildi",
            ],
            "signs_wrong": [
                "Yangi framework o'rganish (bir joyda to'xta!)",
                "Mukammal loyiha qidirish",
                "Faqat mahalliy kompaniyalar",
            ],
            "graduate_criteria": [
                "Portfolio 4+ loyiha (Vercel'da)",
                "GitHub profil faol",
                "LinkedIn + Telegram profili",
                "10+ ariza yuborilgan",
                "1+ texnik suhbat",
            ],
            "challenges": [
                "Imposter syndrome — normal",
                "Rejectlar — 90%",
            ],
            "skills_gained": ["Portfolio", "Texnik suhbat", "Soft skills"],
        },
    ],
    "calendar_30d": [
        {"w": 1, "theme": "HTML asoslari", "days": [
            "Du: HTML tuzilma, doctype, teglar",
            "Se: Matn, ro'yxatlar, havolalar",
            "Ch: Rasmlar, jadval, forma",
            "Pa: Semantik HTML (header, main, footer)",
            "Ju: Amaliyot: shaxsiy profil sahifa",
            "Sh: Saytni GitHub Pages'ga deploy",
            "Ya: Dam olish",
        ]},
        {"w": 2, "theme": "CSS asoslari", "days": [
            "Du: Selektorlar, ranglar, shriftlar",
            "Se: Box model (padding, margin, border)",
            "Ch: Display, position",
            "Pa: Flexbox chuqur",
            "Ju: Grid chuqur",
            "Sh: Amaliyot: landing page",
            "Ya: Dam olish",
        ]},
        {"w": 3, "theme": "Responsive + animatsiya", "days": [
            "Du: Media queries",
            "Se: Mobile-first yondashuv",
            "Ch: CSS variables",
            "Pa: Transitions va animations",
            "Ju: Hover va focus effektlari",
            "Sh: Amaliyot: portfolio sayt",
            "Ya: Dam olish",
        ]},
        {"w": 4, "theme": "Loyiha + Git workflow", "days": [
            "Du: Figma'da dizayn qilish",
            "Se: HTML strukturasi",
            "Ch: CSS styling",
            "Pa: Responsive moslashtirish",
            "Ju: Git branch bilan ishlash",
            "Sh: Vercel'ga deploy + README",
            "Ya: Portfolio'ga qo'shish",
        ]},
    ],
    "first_3_actions": [
        "VS Code + Live Server o'rnatish (bugun, 15 daqiqa)",
        "Birinchi HTML sahifani yozish va brauzerda ochish (bugun, 30 daqiqa)",
        "GitHub Pages'ga deploy qilib ko'rish (bugun, 30 daqiqa)",
    ],
    "mentor_path": [
        "@uzbekdev, @frontend_uz — Telegram guruhlar",
        "Frontend Masters — bepul kurslar",
        "Local: Toshkentdagi Frontend meetup'lar",
    ],
    "resources": [
        {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/", "lang": "EN"},
        {"name": "roadmap.sh/frontend", "url": "https://roadmap.sh/frontend", "lang": "EN"},
        {"name": "freeCodeCamp Frontend", "url": "https://www.freecodecamp.org/", "lang": "EN"},
        {"name": "Frontend Masters", "url": "https://frontendmasters.com/", "lang": "EN"},
    ],
    "milestones": [
        {"week": 1, "milestone": "Birinchi HTML sahifa"},
        {"week": 4, "milestone": "Responsive landing page"},
        {"week": 8, "milestone": "Birinchi JS interaktiv sahifa"},
        {"week": 16, "milestone": "Birinchi React loyiha"},
        {"week": 24, "milestone": "Junior offer"},
    ],
}


def main():
    out_file = ROOT / "roadmap_kb_v2_part_a.json"
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "version": "v2.0",
            "note": "Part A — foundation_programming, frontend_development",
            "careers": CAREERS,
        }, f, ensure_ascii=False, indent=2)
    print("=" * 60)
    print("QADAM Roadmap Part A — yaratildi")
    print("=" * 60)
    print("  [OK] " + str(out_file))
    print("  Careers: " + ", ".join(CAREERS.keys()))
    print()
    print("Keyingi qadam: qadam-roadmap-b.py ni ishga tushiring")


if __name__ == "__main__":
    main()