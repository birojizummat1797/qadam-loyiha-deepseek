# -*- coding: utf-8 -*-
"""QADAM - barcha data JSON fayllarini qayta yozadi."""
import json
from pathlib import Path

BASE = Path("qadam/backend/data")
FILES = {}


def add(path, obj):
    """JSON obyektni yozadi."""
    FILES[path] = json.dumps(obj, ensure_ascii=False, indent=2)


# ═══════════════ signals_v1.json ═══════════════
add("signals_v1.json", {
    "version": "v1.0",
    "signals": {
        "logical_thinking": {"uz": "Mantiqiy fikrlash"},
        "problem_solving": {"uz": "Muammo hal qilish"},
        "technical_interest": {"uz": "Texnikaga qiziqish"},
        "creative_design": {"uz": "Ijodiy dizayn"},
        "visual_logic": {"uz": "Vizual mantiq"},
        "user_empathy": {"uz": "Empatiya"},
        "system_design": {"uz": "Tizimli fikrlash"},
        "analytical": {"uz": "Tahliliy fikrlash"},
        "persistence": {"uz": "Qatiyat"},
        "math_logic": {"uz": "Matematik mantiq"},
        "attention_to_detail": {"uz": "Detallarga etibor"},
        "business_sense": {"uz": "Biznes hissi"},
        "innovation": {"uz": "Innovatsiya"},
    }
})

# ═══════════════ taxonomy_v1.json ═══════════════
add("taxonomy_v1.json", {
    "version": "v1.0",
    "clusters": {
        "software": {
            "uz": "Dasturlash",
            "careers": {
                "foundation_programming": {
                    "uz": "Foundation Programming",
                    "signals": {"logical_thinking": 5, "problem_solving": 5, "persistence": 4, "technical_interest": 4, "system_design": 3, "analytical": 3},
                    "prerequisites": {"device": "required", "english": "A2"},
                    "learning_months": 4, "pathway_type": "entry"
                },
                "frontend_development": {
                    "uz": "Frontend Development",
                    "signals": {"logical_thinking": 4, "visual_logic": 5, "creative_design": 4, "problem_solving": 4, "persistence": 4, "technical_interest": 4, "attention_to_detail": 4, "user_empathy": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 6, "pathway_type": "role"
                },
                "backend_development": {
                    "uz": "Backend Development",
                    "signals": {"logical_thinking": 5, "system_design": 5, "problem_solving": 5, "analytical": 4, "persistence": 4, "technical_interest": 4, "attention_to_detail": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 8, "pathway_type": "role"
                },
                "mobile_development": {
                    "uz": "Mobile Development",
                    "signals": {"logical_thinking": 4, "problem_solving": 4, "user_empathy": 4, "creative_design": 3, "visual_logic": 3, "persistence": 4, "technical_interest": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 7, "pathway_type": "role"
                },
            }
        },
        "data_ai": {
            "uz": "Data & AI",
            "careers": {
                "data_analytics": {
                    "uz": "Data Analytics",
                    "signals": {"analytical": 5, "math_logic": 4, "attention_to_detail": 5, "logical_thinking": 4, "business_sense": 3, "persistence": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 5, "pathway_type": "role"
                },
                "data_science": {
                    "uz": "Data Science",
                    "signals": {"math_logic": 5, "analytical": 5, "persistence": 4, "logical_thinking": 4, "innovation": 3, "system_design": 3},
                    "prerequisites": {"device": "required", "english": "B2"},
                    "learning_months": 12, "pathway_type": "advanced"
                },
                "ai_engineering": {
                    "uz": "AI Engineering",
                    "signals": {"logical_thinking": 5, "system_design": 5, "innovation": 4, "math_logic": 4, "problem_solving": 5, "persistence": 4, "analytical": 4},
                    "prerequisites": {"device": "required", "english": "B2"},
                    "learning_months": 12, "pathway_type": "advanced"
                },
            }
        },
        "infra_security": {
            "uz": "Infra & Security",
            "careers": {
                "devops_cloud": {
                    "uz": "DevOps / Cloud",
                    "signals": {"system_design": 5, "analytical": 4, "persistence": 4, "technical_interest": 5, "attention_to_detail": 4, "logical_thinking": 4},
                    "prerequisites": {"device": "required", "english": "B2"},
                    "learning_months": 10, "pathway_type": "role"
                },
                "cybersecurity": {
                    "uz": "Cybersecurity",
                    "signals": {"analytical": 5, "attention_to_detail": 5, "persistence": 5, "logical_thinking": 4, "technical_interest": 4, "system_design": 4},
                    "prerequisites": {"device": "required", "english": "B2"},
                    "learning_months": 10, "pathway_type": "role"
                },
                "qa_automation": {
                    "uz": "QA / Test Automation",
                    "signals": {"attention_to_detail": 5, "logical_thinking": 4, "persistence": 4, "problem_solving": 4, "technical_interest": 3, "analytical": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 5, "pathway_type": "entry"
                },
            }
        },
        "design_creative": {
            "uz": "Dizayn",
            "careers": {
                "ui_ux_design": {
                    "uz": "UI/UX Design",
                    "signals": {"creative_design": 5, "user_empathy": 5, "visual_logic": 5, "attention_to_detail": 4, "system_design": 3, "problem_solving": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 6, "pathway_type": "role"
                },
                "product_design": {
                    "uz": "Product Design",
                    "signals": {"creative_design": 5, "user_empathy": 5, "system_design": 4, "visual_logic": 4, "analytical": 4, "business_sense": 3, "attention_to_detail": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 10, "pathway_type": "advanced"
                },
                "graphic_design": {
                    "uz": "Graphic Design",
                    "signals": {"creative_design": 5, "visual_logic": 5, "attention_to_detail": 4, "persistence": 3},
                    "prerequisites": {"device": "required", "english": "A2"},
                    "learning_months": 4, "pathway_type": "entry"
                },
                "motion_design": {
                    "uz": "Motion Design",
                    "signals": {"creative_design": 5, "visual_logic": 5, "persistence": 4, "technical_interest": 3, "attention_to_detail": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 6, "pathway_type": "role"
                },
            }
        },
        "digital_marketing": {
            "uz": "Marketing",
            "careers": {
                "smm_manager": {
                    "uz": "SMM Manager",
                    "signals": {"creative_design": 4, "user_empathy": 5, "business_sense": 4, "analytical": 3, "persistence": 3},
                    "prerequisites": {"device": "smartphone_ok", "english": "A2"},
                    "learning_months": 3, "pathway_type": "entry"
                },
                "performance_marketing": {
                    "uz": "Performance Marketing",
                    "signals": {"analytical": 5, "business_sense": 4, "attention_to_detail": 4, "math_logic": 3, "persistence": 4, "innovation": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 5, "pathway_type": "role"
                },
                "seo": {
                    "uz": "SEO Specialist",
                    "signals": {"analytical": 4, "attention_to_detail": 5, "persistence": 5, "logical_thinking": 3, "innovation": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 5, "pathway_type": "role"
                },
                "content_marketing": {
                    "uz": "Content Marketing",
                    "signals": {"creative_design": 4, "user_empathy": 4, "analytical": 3, "persistence": 4, "attention_to_detail": 4},
                    "prerequisites": {"device": "smartphone_ok"},
                    "learning_months": 3, "pathway_type": "entry"
                },
            }
        },
        "content_media": {
            "uz": "Media",
            "careers": {
                "video_content": {
                    "uz": "Video Content",
                    "signals": {"creative_design": 5, "visual_logic": 5, "persistence": 4, "technical_interest": 3, "attention_to_detail": 3},
                    "prerequisites": {"device": "smartphone_ok"},
                    "learning_months": 4, "pathway_type": "entry"
                },
                "brand_strategy": {
                    "uz": "Brand Strategy",
                    "signals": {"creative_design": 5, "business_sense": 4, "user_empathy": 4, "analytical": 3, "innovation": 4, "system_design": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 8, "pathway_type": "advanced"
                },
            }
        },
        "product_project": {
            "uz": "Product & Project",
            "careers": {
                "product_management": {
                    "uz": "Product Management",
                    "signals": {"system_design": 5, "business_sense": 5, "analytical": 4, "user_empathy": 4, "innovation": 3, "persistence": 4},
                    "prerequisites": {"device": "required", "english": "B2"},
                    "learning_months": 12, "pathway_type": "advanced"
                },
                "project_management": {
                    "uz": "Project Management",
                    "signals": {"system_design": 5, "attention_to_detail": 4, "persistence": 5, "business_sense": 4, "user_empathy": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 6, "pathway_type": "role"
                },
                "business_analysis": {
                    "uz": "Business Analysis",
                    "signals": {"analytical": 5, "system_design": 4, "attention_to_detail": 5, "logical_thinking": 4, "business_sense": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 6, "pathway_type": "role"
                },
            }
        },
        "business_sales": {
            "uz": "Business & Sales",
            "careers": {
                "it_b2b_sales": {
                    "uz": "IT / B2B Sales",
                    "signals": {"business_sense": 5, "user_empathy": 5, "persistence": 5, "innovation": 3, "analytical": 3},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 4, "pathway_type": "entry"
                },
                "customer_success": {
                    "uz": "Customer Success",
                    "signals": {"user_empathy": 5, "business_sense": 4, "attention_to_detail": 4, "system_design": 3, "persistence": 4},
                    "prerequisites": {"device": "required", "english": "B1"},
                    "learning_months": 4, "pathway_type": "entry"
                },
            }
        },
    }
})

# ═══════════════ questions_v1.json ═══════════════
add("questions_v1.json", {
    "version": "v1.0",
    "stage_1": {
        "questions": [
            {"id": "s1_q1", "type": "single_choice", "text": "Hozir hayotingizning qaysi bosqichidasiz?", "options": [
                {"v": "school", "l": "Maktab bitiruvchisi"},
                {"v": "student", "l": "Talaba"},
                {"v": "working_student", "l": "Talaba va ishlayapman"},
                {"v": "young_pro", "l": "Yosh mutaxassis"},
                {"v": "switcher", "l": "Kasbni ozgartirmoqchiman"},
                {"v": "dissatisfied", "l": "Ishimdan qoniqmayman"},
                {"v": "unemployed", "l": "Ishsizman"}
            ]},
            {"id": "s1_q2", "type": "single_choice", "text": "Sizni eng kop nima qiynaydi?", "options": [
                {"v": "dont_know_career", "l": "Qaysi kasb menga mosligini bilmayman"},
                {"v": "wrong_path", "l": "Tanlagan yolim mos emas"},
                {"v": "low_income", "l": "Daromadim yetarli emas"},
                {"v": "no_direction", "l": "Nimadan boshlashni bilmayman"},
                {"v": "study_waste", "l": "Oqishga kop pul sarfladim"},
                {"v": "future_fear", "l": "Kelajagim uchun qorquv"}
            ]},
            {"id": "s1_q3", "type": "single_choice", "text": "Siz uchun eng muhim narsa?", "options": [
                {"v": "income", "l": "Yuqori daromad"},
                {"v": "stability", "l": "Barqarorlik"},
                {"v": "growth", "l": "Osish va rivojlanish"},
                {"v": "freedom", "l": "Erkinlik"},
                {"v": "impact", "l": "Jamiyatga foyda"},
                {"v": "creation", "l": "Ijod"}
            ]},
            {"id": "s1_q4", "type": "single_choice", "text": "Qaysi ish sizni oziga tortadi?", "options": [
                {"v": "tech", "l": "Texnika va texnologiya"},
                {"v": "creative", "l": "Ijod, dizayn"},
                {"v": "people", "l": "Odamlar bilan muloqot"},
                {"v": "analysis", "l": "Tahlil, raqamlar"},
                {"v": "business", "l": "Biznes, savdo"},
                {"v": "systems", "l": "Tartib, tizim"}
            ]},
            {"id": "s1_q5", "type": "multi_select", "max": 4, "text": "Qaysi sohalar qiziqtiradi?", "options": [
                {"v": "software", "l": "Dasturlash"},
                {"v": "data_ai", "l": "Data va AI"},
                {"v": "design", "l": "Dizayn"},
                {"v": "marketing", "l": "Marketing"},
                {"v": "media", "l": "Media"},
                {"v": "product", "l": "Product"},
                {"v": "business", "l": "Biznes"},
                {"v": "security", "l": "Xavfsizlik"},
                {"v": "unknown", "l": "Hali aniq emas"}
            ]},
            {"id": "s1_q6", "type": "single_choice", "text": "Kuniga qancha vaqt?", "options": [
                {"v": "lt_1h", "l": "1 soatdan kam"},
                {"v": "1h", "l": "1 soat"},
                {"v": "2_3h", "l": "2-3 soat"},
                {"v": "4h_plus", "l": "4+ soat"},
                {"v": "full_time", "l": "Toliq kun"}
            ]},
            {"id": "s1_q7", "type": "single_choice", "text": "Qaysi qurilma?", "options": [
                {"v": "laptop", "l": "Noutbuk bor"},
                {"v": "smartphone_only", "l": "Faqat smartfon"},
                {"v": "both", "l": "Ikkalasi"},
                {"v": "none", "l": "Yoq"}
            ]},
            {"id": "s1_q8", "type": "single_choice", "text": "Ingliz tilingiz?", "options": [
                {"v": "none", "l": "Bilmayman"},
                {"v": "a2", "l": "A1-A2"},
                {"v": "b1", "l": "B1"},
                {"v": "b2", "l": "B2"},
                {"v": "c1", "l": "C1+"}
            ]}
        ]
    },
    "stage_2": {
        "dimensions": {
            "goal": {"questions": [
                {"id": "s2_q1", "text": "Keyingi 3 yilda professional bolishni xohlayman.", "maps_to": {"signal": "persistence", "weight": 1.0}},
                {"id": "s2_q2", "text": "Soham uzoq muddatli istiqbolga ega bolishi muhim.", "maps_to": {"signal": "business_sense", "weight": 1.0}}
            ]},
            "interest": {"questions": [
                {"id": "s2_q3", "text": "Texnikani yigish menga zavq beradi.", "maps_to": {"signal": "technical_interest", "weight": 1.5}},
                {"id": "s2_q4", "text": "Tadqiqot va tahlil qiziqarli.", "maps_to": {"signal": "analytical", "weight": 1.5}},
                {"id": "s2_q5", "text": "Rasm chizish, dizayn mening ifodam.", "maps_to": {"signal": "creative_design", "weight": 1.5}},
                {"id": "s2_q6", "text": "Odamlarga yordam berish yoqadi.", "maps_to": {"signal": "user_empathy", "weight": 1.5}},
                {"id": "s2_q7", "text": "Loyihani boshqarish menga mos.", "maps_to": {"signal": "business_sense", "weight": 1.5}}
            ]},
            "aptitude": {"questions": [
                {"id": "s2_q8", "text": "Raqamlar va formulalar bilan erkin ishlayman.", "maps_to": {"signal": "math_logic", "weight": 1.5}},
                {"id": "s2_q9", "text": "Muammoni qismlarga bolib yechaman.", "maps_to": {"signal": "problem_solving", "weight": 1.5}},
                {"id": "s2_q10", "text": "Kop qismli tizimni tasavvur qila olaman.", "maps_to": {"signal": "system_design", "weight": 1.5}}
            ]},
            "skills": {"questions": [
                {"id": "s2_q11", "text": "Biror sohada amaliy konikmaga egaman.", "maps_to": {"signal": "persistence", "weight": 1.0}},
                {"id": "s2_q12", "text": "Mustaqil organishga odatlanganman.", "maps_to": {"signal": "persistence", "weight": 1.0}}
            ]},
            "values": {"questions": [
                {"id": "s2_q13", "text": "Ishim jamiyatga foyda keltirishi muhim.", "maps_to": {"signal": "user_empathy", "weight": 1.0}},
                {"id": "s2_q14", "text": "Erkin uslubni afzal koraman.", "maps_to": {"signal": "innovation", "weight": 1.0}}
            ]},
            "work_style": {"questions": [
                {"id": "s2_q15", "text": "Yakka ishlashni afzal koraman.", "maps_to": {"signal": "system_design", "weight": 0.8}},
                {"id": "s2_q16", "text": "Ozgaruvchan muhitda ishlashni yaxshi koraman.", "maps_to": {"signal": "innovation", "weight": 1.0}}
            ]},
            "constraints": {"questions": [
                {"id": "s2_q17", "text": "Moliyaviy cheklovim bor.", "maps_to": {"constraint": "finance", "weight": 1.0}}
            ]},
            "resilience": {"questions": [
                {"id": "s2_q18", "text": "Qiyinchilikka chidashga tayyorman.", "maps_to": {"signal": "persistence", "weight": 1.5}}
            ]}
        }
    }
})

# ═══════════════ roadmap_kb_v1.json ═══════════════
add("roadmap_kb_v1.json", {
    "version": "v1.1",
    "careers": {
        "foundation_programming": {
            "uz": "Foundation Programming",
            "why": "Dasturlash asoslari - har qanday IT yonalishga kirish eshigi.",
            "skill_gap": ["Python yoki JavaScript", "Algoritmik fikrlash", "Git", "Terminal", "Kichik loyihalar"],
            "roadmap": {
                "first_steps": ["Bepul kursni boshlash (CS50)", "VS Code va Python ornatish", "Birinchi Hello World"],
                "phases": [
                    {"period": "0-1 oy", "goal": "Sintaksis", "actions": ["Ozgaruvchilar, shartlar", "Funksiyalar", "Kuniga 1 soat"]},
                    {"period": "1-3 oy", "goal": "Algoritmik fikrlash", "actions": ["LeetCode Easy", "Git", "3-5 mini-loyiha"]},
                    {"period": "3-6 oy", "goal": "Yonalish tanlash", "actions": ["Frontend/Backend", "GitHub portfolio", "Junior vakansiya"]}
                ],
                "milestones": ["10 masala", "Birinchi loyiha", "Birinchi suhbat"]
            },
            "projects": ["Kalkulyator", "Todo", "Weather app"],
            "resources": [
                {"name": "CS50", "url": "https://cs50.harvard.edu/x/"},
                {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/"}
            ],
            "risks": ["Video bilan cheklanish", "Tutorial hell", "Yolgizlik"],
            "market_context": {"demand": "yuqori"}
        },
        "frontend_development": {
            "uz": "Frontend Development",
            "why": "Frontend - foydalanuvchi koradigan qism.",
            "skill_gap": ["HTML CSS JS", "React yoki Vue", "Responsive", "API", "Git"],
            "roadmap": {
                "first_steps": ["HTML+CSS 2 hafta", "JS ES6+", "Birinchi statik sayt"],
                "phases": [
                    {"period": "0-2 oy", "goal": "Asoslar", "actions": ["HTML CSS", "JavaScript DOM", "3-5 sayt"]},
                    {"period": "2-4 oy", "goal": "React", "actions": ["React hooks", "Tailwind", "API", "2-3 SPA"]},
                    {"period": "4-6 oy", "goal": "Portfolio", "actions": ["3-4 loyiha", "Deploy", "Junior ariza"]}
                ],
                "milestones": ["Birinchi sayt", "Birinchi React", "Birinchi offer"]
            },
            "projects": ["Portfolio", "Ob-havo app", "Dashboard"],
            "resources": [
                {"name": "MDN", "url": "https://developer.mozilla.org/"},
                {"name": "roadmap.sh/frontend", "url": "https://roadmap.sh/frontend"}
            ],
            "risks": ["Framework erta", "Portfolio yoq"],
            "market_context": {"demand": "yuqori"}
        },
        "ui_ux_design": {
            "uz": "UI/UX Design",
            "why": "Ijodiy did va empatiya bu sohada asosiy qurol.",
            "skill_gap": ["Figma", "Dizayn nazariyasi", "User research", "Wireframe", "Portfolio"],
            "roadmap": {
                "first_steps": ["Figma ornatish", "Dribbble tahlil", "Birinchi ekran"],
                "phases": [
                    {"period": "0-1 oy", "goal": "Figma", "actions": ["Auto-layout", "Rang tipografiya", "5-10 mashq"]},
                    {"period": "1-3 oy", "goal": "UX", "actions": ["User flow", "Design systems", "1-2 loyiha"]},
                    {"period": "3-6 oy", "goal": "Portfolio", "actions": ["3-4 case study", "Behance", "Junior ariza"]}
                ],
                "milestones": ["Birinchi ekran", "Birinchi case", "Birinchi mijoz"]
            },
            "projects": ["Bank redesign", "E-commerce UX", "Portfolio"],
            "resources": [
                {"name": "Figma Learn", "url": "https://help.figma.com/"},
                {"name": "Refactoring UI", "url": "https://www.refactoringui.com/"}
            ],
            "risks": ["Funksionallikni unutish", "Case study yoq"],
            "market_context": {"demand": "orta-yuqori"}
        },
        "smm_manager": {
            "uz": "SMM Manager",
            "why": "Ijod, muloqot va tahlil birlashmasi.",
            "skill_gap": ["Kontent strategiya", "Algoritmlar", "Canva", "Copywriting", "Analitika"],
            "roadmap": {
                "first_steps": ["Shaxsiy sahifa kontent reja", "Canva 5-10 post", "Bepul kurslar"],
                "phases": [
                    {"period": "0-1 oy", "goal": "Asoslar", "actions": ["Post story reel", "Canva", "Sahifa auditi"]},
                    {"period": "1-3 oy", "goal": "Amaliyot", "actions": ["1 real mijoz", "30 kun reja", "Analitika"]},
                    {"period": "3-6 oy", "goal": "Professional", "actions": ["3-5 mijoz", "Tools", "Case study"]}
                ],
                "milestones": ["30 kun reja", "Birinchi mijoz", "Birinchi viral"]
            },
            "projects": ["Shaxsiy sahifa", "Kichik biznes SMM", "Kampaniya"],
            "resources": [
                {"name": "Meta Blueprint", "url": "https://www.facebook.com/business/learn"},
                {"name": "Canva Design School", "url": "https://www.canva.com/designschool/"}
            ],
            "risks": ["Natijasiz aktivlik", "Trendlar kora-kora"],
            "market_context": {"demand": "yuqori"}
        },
        "data_analytics": {
            "uz": "Data Analytics",
            "why": "Tahlil, detal va tizimli yondashuv qimmatli.",
            "skill_gap": ["Excel", "SQL", "Tableau/Power BI", "Statistika", "Python"],
            "roadmap": {
                "first_steps": ["Excel chuqur", "SQL kursi", "Birinchi dataset"],
                "phases": [
                    {"period": "0-1 oy", "goal": "Excel+SQL", "actions": ["Pivot VLOOKUP", "SELECT JOIN", "Kaggle dataset"]},
                    {"period": "1-3 oy", "goal": "Vizualizatsiya", "actions": ["Tableau", "Statistika", "Dashboard"]},
                    {"period": "3-6 oy", "goal": "Portfolio", "actions": ["3-4 loyiha", "Python pandas", "Junior ariza"]}
                ],
                "milestones": ["Birinchi SQL", "Birinchi dashboard", "Birinchi offer"]
            },
            "projects": ["Savdo tahlil", "Open data", "Dashboard"],
            "resources": [
                {"name": "Kaggle Learn", "url": "https://www.kaggle.com/learn"},
                {"name": "Mode SQL", "url": "https://mode.com/sql-tutorial/"}
            ],
            "risks": ["Tool organib biznes tushunmaslik", "Statistikasiz xulosa"],
            "market_context": {"demand": "yuqori"}
        }
    }
})


def main():
    print("=" * 60)
    print("QADAM fix2: data JSON fayllari qayta yozilmoqda")
    print("=" * 60)
    for path, content in FILES.items():
        full = BASE / path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        size = len(content.encode("utf-8"))
        print("  [OK] {} ({} bayt)".format(path, size))
    print()
    print("Jami: " + str(len(FILES)) + " ta fayl yozildi!")

    # Tekshirish
    print()
    print("Tekshirish:")
    for path in FILES.keys():
        full = BASE / path
        try:
            with open(full, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("  [VALID] " + path)
        except Exception as e:
            print("  [XATO] " + path + " - " + str(e))


if __name__ == "__main__":
    main()