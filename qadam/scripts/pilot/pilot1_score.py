"""Pilot 1 (Dasturlash golden sample): score answers sent via Telegram.

Input: a JSON file of anonymous participants, e.g.
  [{"id": "P1", "part1": "1-A, 2-C, ...", "part2": "...", "part4": "1-A-1, 2-B-3, ...", "part5": "1-A-1, 2-C-3"}]
Output: per participant, the result text to send back (Uzbek) plus a raw summary.
Rules follow docs/methodology/qadam-metodologiyasi-v0.1.md (claude-qadamio). Not wired into the app.

    python scripts/pilot/pilot1_score.py answers.json
"""
import collections
import json
import re
import sys
from pathlib import Path

M = json.loads((Path(__file__).parent / "pilot1_mapping.json").read_text())


def parse(s: str) -> dict[int, list[str]]:
    """'1-A, 2-C-3' -> {1: ['A'], 2: ['C', '3']}"""
    out = {}
    for part in re.split(r"[,;\n]+", s or ""):
        bits = [b.strip().upper() for b in part.strip().split("-") if b.strip()]
        if len(bits) >= 2 and bits[0].isdigit():
            out[int(bits[0])] = bits[1:]
    return out


def tally(answers: dict, mapping: list, first: int, count: int) -> tuple[collections.Counter, int]:
    s, unmeasured = collections.Counter(), 0
    for i in range(first, first + count):
        a = (answers.get(i) or ["E"])[0]
        idx = "ABCD".find(a)
        if idx < 0:
            unmeasured += 1  # E / missing = not measured, never a minus
        else:
            s[mapping[i - first][idx]] += 1
    return s, unmeasured


def decide(s: collections.Counter, min_top: int, margin: int = 1):
    top = s.most_common(2) + [(None, 0), (None, 0)]
    if top[0][1] < min_top:
        return "unclear", []
    if top[0][1] - top[1][1] < margin:
        return "tie", [top[0][0], top[1][0]]
    return "clear", [top[0][0]]


def ease_text(code: str) -> str:
    return {"1": "oson va qiziq", "2": "oson, lekin zerikarli", "3": "qiyin, lekin qiziq",
            "4": "qiyin va zerikarli"}.get(code, "baholanmagan")


def score(p: dict) -> dict:
    a1, a2 = parse(p.get("part1", "")), parse(p.get("part2", ""))
    a4, a5 = parse(p.get("part4", "")), parse(p.get("part5", ""))
    cat, cat_un = tally(a1, M["short"], 1, 9)
    cat_kind, cat_top = decide(cat, 3)
    dev, dev_un = tally(a2, M["dev"], 1, 11)
    dev_kind, dev_top = decide(dev, 4)
    tasks = [((a4.get(i) or ["E"])[0], (a4.get(i) or ["E", ""])[1:2]) for i in range(1, 5)]
    learn = [((a5.get(i) or ["E"])[0], (a5.get(i) or ["E", ""])[1:2]) for i in range(1, 3)]
    return {"id": p.get("id"), "catalog": dict(cat), "catalog_unmeasured": cat_un, "catalog_result": [cat_kind, cat_top],
            "dev": dict(dev), "dev_unmeasured": dev_un, "dev_result": [dev_kind, dev_top],
            "tasks": [{"label": M["task_labels"][i], "answer": t[0], "correct": t[0] == M["tasks_correct"][i],
                       "ease": ease_text(t[1][0] if t[1] else "")} for i, t in enumerate(tasks)],
            "learn": [{"answer": t[0], "correct": t[0] == M["learn_correct"][i],
                       "ease": ease_text(t[1][0] if t[1] else "")} for i, t in enumerate(learn)]}


def text(r: dict) -> str:
    cn, dn = M["catalog_names"], M["dev_names"]
    lines = ["Natijangiz (sinov versiyasi):", ""]
    kind, top = r["catalog_result"]
    if kind == "clear":
        lines.append(f"• Sizga eng yaqin yo‘nalish: {cn[top[0]]}.")
    elif kind == "tie":
        lines.append(f"• Ikki yo‘nalishga teng yaqinlik ko‘rindi: {cn[top[0]]} va {cn[top[1]]}.")
    else:
        lines.append("• Hozircha javoblaringiz bo‘yicha aniq yo‘nalish ko‘rinmayapti.")
    kind, top = r["dev_result"]
    if kind == "clear":
        lines.append(f"• Sayt va ilovalar ichida sizni ko‘proq tortayotgani: {dn[top[0]]}.")
    elif kind == "tie":
        lines.append(f"• Sayt va ilovalar ichida ikki yo‘nalish teng: {dn[top[0]]} va {dn[top[1]]}.")
    else:
        lines.append("• Sayt va ilovalar ichida aniq tanlov ko‘rinmadi.")
    done = [t for t in r["tasks"] if t["correct"]]
    if done:
        lines.append("• Siz bajargan topshiriqlar: " + "; ".join(f"{t['label']} ({t['ease']})" for t in done) + ".")
    if sum(t["correct"] for t in r["learn"]) == 2:
        lines.append("• Yangi qoidani (TAKRORLA) o‘rganib, darhol murakkabroq vaziyatda ham qo‘lladingiz.")
    elif r["learn"][0]["correct"]:
        lines.append("• Yangi qoidani (TAKRORLA) o‘rganib, darhol qo‘lladingiz.")
    lines += ["", "Bu — bitta qisqa sinov natijasi, hukm emas. Signallarni Qadam o‘qiydi. Qarorni siz qilasiz."]
    return "\n".join(lines)


def main():
    people = json.loads(Path(sys.argv[1]).read_text())
    for p in people:
        r = score(p)
        print(f"=== {r['id']} ===")
        print(json.dumps({k: v for k, v in r.items() if k != "id"}, ensure_ascii=False))
        print(text(r))
        print()


if __name__ == "__main__":
    main()
