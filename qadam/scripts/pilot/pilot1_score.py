"""Pilot 1 (Dasturlash golden sample): score answers sent via Telegram.

Input: a JSON file of anonymous participants, e.g.
  [{"id": "P1", "part1": "1-A, 2-C, ...", "part2": "...", "part4": "1-A-1, 2-B-3, ...", "part5": "1-A-1, 2-C-3"}]
Output: per participant, the result text to send back (Uzbek) plus a raw summary.
Rules follow docs/methodology/qadam-metodologiyasi-v0.1.md (claude-qadamio). Not wired into the app.

    python scripts/pilot/pilot1_score.py answers.json
    python scripts/pilot/pilot1_score.py --csv responses.csv   # Google Forms export
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


FORM = json.loads((Path(__file__).parent / "pilot1_form_data.json").read_text())
LEARN_OPTIONS = ["2", "3", "4", "6", "Bilmayman"], ["3", "5", "6", "9", "Bilmayman"]
EASE = ["Oson va qiziq", "Oson, lekin zerikarli", "Qiyin, lekin qiziq", "Qiyin va zerikarli"]


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip()).lower()


def from_csv(path: str) -> list[dict]:
    """Google Forms CSV -> the same participant dicts as the Telegram format.

    Columns are matched by question text (numbers in titles are ignored), answers by option text.
    Rows without consent (under 18 / declined) are skipped.
    """
    import csv
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    header, body = rows[0], rows[1:]
    title = {i: _norm(re.sub(r"^\d+\.\s*", "", h)) for i, h in enumerate(header)}

    def col(text: str, nth: int = 0) -> int | None:
        hits = [i for i, t in title.items() if t == _norm(text)]
        return hits[nth] if len(hits) > nth else None

    def letter(row, text, options, nth=0) -> str:
        c = col(text, nth)
        v = _norm(row[c]) if c is not None and c < len(row) else ""
        opts = [_norm(o) for o in options]
        return "ABCDE"[opts.index(v)] if v in opts else "E"

    people = []
    consent_col = next((i for i, t in title.items() if t.startswith("sinovda qatnashishga")), None)
    code_col = next((i for i, t in title.items() if t.startswith("o‘zingiz o‘ylab topgan kod")), None)
    for n, row in enumerate(body, 1):
        if consent_col is None or not row[consent_col].startswith("Ha"):
            continue
        p1 = [f"{i}-{letter(row, q['q'], q['o'])}" for i, q in enumerate(FORM["short"], 1)]
        p2 = [f"{i}-{letter(row, q['q'], q['o'])}" for i, q in enumerate(FORM["dev"], 1)]
        # "N-topshiriq siz uchun qanday bo‘ldi?" appears for tasks 1-4 and again for lessons 1-2
        ease_cols = [i for i, t in title.items() if t.endswith("topshiriq siz uchun qanday bo‘ldi?")]
        ease_vals = [str(EASE.index(row[c].strip()) + 1) if row[c].strip() in EASE else "" for c in ease_cols]
        p4 = [f"{i}-{letter(row, q['q'], q['o'])}-{ease_vals[i-1] if i-1 < len(ease_vals) else ''}"
              for i, q in enumerate(FORM["tasks"], 1)]
        l1 = letter(row, "TAKRORLA 2 marta: [2 qadam oldinga, 1 qadam orqaga]. Robot boshlang‘ich joyidan necha qadam oldinda bo‘ladi?", LEARN_OPTIONS[0])
        l2 = letter(row, "TAKRORLA 3 marta: [ TAKRORLA 2 marta: [1 qadam yur] ]. Robot jami necha qadam yuradi?", LEARN_OPTIONS[1])
        p5 = [f"1-{l1}-{ease_vals[4] if len(ease_vals) > 4 else ''}", f"2-{l2}-{ease_vals[5] if len(ease_vals) > 5 else ''}"]
        people.append({"id": (row[code_col].strip() if code_col is not None else "") or f"R{n}",
                       "part1": ", ".join(p1), "part2": ", ".join(p2), "part4": ", ".join(p4), "part5": ", ".join(p5)})
    return people


def main():
    if sys.argv[1] == "--csv":
        people = from_csv(sys.argv[2])
    else:
        people = json.loads(Path(sys.argv[1]).read_text())
    for p in people:
        r = score(p)
        print(f"=== {r['id']} ===")
        print(json.dumps({k: v for k, v in r.items() if k != "id"}, ensure_ascii=False))
        print(text(r))
        print()


if __name__ == "__main__":
    main()
