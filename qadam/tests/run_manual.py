import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.signals import signals_from_answers
from engine.ranking import rank_careers
from engine.roadmap import build_full_report
from data_loader import load_taxonomy, load_questions
from tests.profiles import PROFILES

SIGNAL_UZ = {
    "logical_thinking": "Mantiq",
    "problem_solving": "Muammo hal",
    "technical_interest": "Texnika",
    "creative_design": "Ijodiy dizayn",
    "visual_logic": "Vizual mantiq",
    "user_empathy": "Empatiya",
    "system_design": "Tizim",
    "analytical": "Tahlil",
    "persistence": "Qatiyat",
    "math_logic": "Matematika",
    "attention_to_detail": "Detal",
    "business_sense": "Biznes",
    "innovation": "Innovatsiya",
}


def sep(ch="=", n=70):
    print(ch * n)


def run_profile(profile):
    sep()
    print("[PROFIL] " + profile["name"])
    sep("-")
    print(profile["description"])
    print()

    questions = load_questions()
    taxonomy = load_taxonomy()
    constraints = {
        "time": profile["stage1"]["s1_q6"],
        "device": profile["stage1"]["s1_q7"],
        "english": profile["stage1"]["s1_q8"],
    }

    signals = signals_from_answers(profile["stage2"], questions)
    top_signals = sorted(
        [(k, v["score"]) for k, v in signals.items() if v.get("score") is not None],
        key=lambda x: -x[1],
    )[:5]

    print("KUCHLI SIGNALLAR:")
    for k, v in top_signals:
        bar = "#" * int(v * 20)
        print("   {:<18} {:<20} {:.0f}%".format(SIGNAL_UZ.get(k, k), bar, v * 100))

    print()
    print("CHEKLOVLAR:")
    print("   Vaqt:      " + str(constraints["time"]))
    print("   Qurilma:   " + str(constraints["device"]))
    print("   Ingliz:    " + str(constraints["english"]))

    ranking = rank_careers(signals, taxonomy, constraints, min_coverage=0.5, top_n=5)

    print()
    print("TOP-5 (confidence: " + ranking["confidence"] + "):")
    for i, c in enumerate(ranking["ranked"], 1):
        warn = ""
        if c["has_hard_barrier"]:
            warn = " [HARD BARRIER]"
        elif c["barriers"]:
            warn = " [" + str(len(c["barriers"])) + " soft]"
        rm_mark = "" if c.get("has_roadmap", False) else " [roadmap tez orada]"
        print()
        print("   {}. {} ({}){}{}".format(i, c["career_uz"], c["cluster_uz"], warn, rm_mark))
        print("      Fit: {:.1f}%  |  Readiness: {:.1f}%  |  Coverage: {:.0f}%".format(
            c["fit"], c["readiness"], c["coverage"] * 100
        ))

    if not ranking["ranked"]:
        print()
        print("Natija yoq")
        return

    top = ranking["ranked"][0]
    print()
    print("=" * 70)
    print("TOP-1: " + top["career_uz"])
    print("=" * 70)

    report = build_full_report([top], constraints, taxonomy)
    c = report["careers"][0]
    rm = c["roadmap"]

    print()
    print("NEGA BU MOS:")
    print("   " + rm.get("why_this_path", "Malumot yoq"))

    if rm.get("is_placeholder"):
        print()
        print("(Diqqat: bu yonalish uchun batafsil roadmap hali tayyor emas)")
        return

    if rm.get("barrier_resolutions"):
        print()
        print("TOSIQLARNI HAL QILISH:")
        for b in rm["barrier_resolutions"]:
            print("   - [" + b["level"].upper() + "] " + b["action"])

    print()
    print("BIRINCHI 3 QADAM:")
    for i, a in enumerate(rm.get("first_3_actions", []), 1):
        print("   {}. {}".format(i, a))

    print()
    print("ROADMAP:")
    for phase in rm.get("phases", []):
        print()
        print("   [{}] {}".format(phase["period"], phase["goal"]))
        for a in phase["actions"]:
            print("      - " + a)

    print()
    print("MILESTONES:")
    for m in rm.get("milestones", []):
        print("   + " + m)

    if rm.get("risks"):
        print()
        print("EHTIYOT BOLING:")
        for r in rm["risks"]:
            print("   - " + r)

    print()


def main():
    print()
    sep()
    print("QADAM - 5 PROFIL TESTI")
    sep()
    print()
    for profile in PROFILES:
        run_profile(profile)
    sep()
    print("Barcha profillar muvaffaqiyatli qayta ishlandi")
    sep()
    print()


if __name__ == "__main__":
    main()