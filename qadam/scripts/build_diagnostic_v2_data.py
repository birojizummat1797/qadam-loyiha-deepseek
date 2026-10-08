"""Build backend/data/diagnostic_v2.json from the founder-reviewed specs in claude-qadamio.

Usage:
    python scripts/build_diagnostic_v2_data.py /path/to/claude-qadamio/docs/specs

The specs (Markdown) are the source of truth for question wording; this script
only parses them, attaches stable IDs and validates the structure. Re-run it
whenever the specs change, then commit the regenerated JSON.
"""
import json
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "backend" / "data" / "diagnostic_v2.json"

NONE_LABEL = "Bilmayman / bu yerda menga mosi yo‘q"
TASK_NONE_LABEL = "Bilmayman"
LETTERS = "ABCDE"

# Catalog order and IDs follow docs/decisions/2026-10-05-catalog-9x25.md and
# docs/specs/2026-10-07-catalog-id-mapping.md (claude-qadamio).
CATALOGS = [
    ("software", "Dasturlash", [
        ("frontend_development", "Frontend dasturchi", "Frontend"),
        ("backend_development", "Backend dasturchi", "Backend"),
        ("mobile_development", "Mobil dasturchi", "Mobil"),
        ("qa_automation", "QA / test mutaxassisi", "QA / test"),
    ]),
    ("data_ai", "Ma’lumotlar va sun’iy intellekt", [
        ("data_analytics", "Data analitik", "Data analitik"),
        ("data_science", "AI va Data Science muhandisi", "AI va Data Science"),
        ("database_specialist", "Ma’lumotlar bazasi mutaxassisi", "Ma’lumotlar bazasi"),
    ]),
    ("infra_security", "Tizimlar, tarmoq va xavfsizlik", [
        ("system_network_admin", "Tizim va tarmoq ma’muri", "Tizim va tarmoq ma’muri"),
        ("devops_cloud", "DevOps / Cloud muhandisi", "DevOps / Cloud"),
        ("cybersecurity", "Kiberxavfsizlik mutaxassisi", "Kiberxavfsizlik"),
    ]),
    ("design_creative", "Raqamli dizayn", [
        ("ui_ux_design", "UI/UX dizayner", "UI/UX dizayner"),
        ("graphic_design", "Grafik dizayner", "Grafik dizayner"),
    ]),
    ("digital_marketing", "Raqamli marketing", [
        ("smm_manager", "SMM menejer", "SMM menejer"),
        ("performance_marketing", "Target (performance) marketolog", "Target marketolog"),
        ("seo", "SEO mutaxassisi", "SEO mutaxassisi"),
    ]),
    ("content_media", "Kontent va media", [
        ("video_motion", "Video va motion kontent mutaxassisi", "Video va motion"),
        ("content_copywriting", "Kontent va kopirayting mutaxassisi", "Kontent va kopirayting"),
    ]),
    ("product_project", "Mahsulot va loyiha boshqaruvi", [
        ("product_management", "Product menejer", "Product menejer"),
        ("project_management", "Loyiha menejeri", "Loyiha menejeri"),
        ("business_analysis", "Biznes-analitik", "Biznes-analitik"),
    ]),
    ("business_sales", "Sotuv va mijozlar bilan ishlash", [
        ("sales_manager", "Sotuv menejeri", "Sotuv menejeri"),
        ("customer_success", "Customer Success mutaxassisi", "Customer Success"),
    ]),
    ("finance_office", "Moliya va raqamli ofis", [
        ("accountant", "Buxgalter", "Buxgalter"),
        ("fintech_specialist", "Fintech mutaxassisi", "Fintech"),
        ("spreadsheet_specialist", "Excel va Google Sheets mutaxassisi", "Excel / Sheets"),
    ]),
]
CAT_BY_NAME = {name: cid for cid, name, _ in CATALOGS}
CAREER_BY_TAG = {tag: car for _, _, cars in CATALOGS for car, _, tag in cars}

# Golden-sample file and section per catalog (section title prefix, or None for a one-catalog file).
GOLDEN = {
    "software": ("2026-10-05-dasturlash-golden-sample.md", None),
    "data_ai": ("2026-10-07-golden-samples-batch-1.md", "## 1. "),
    "infra_security": ("2026-10-07-golden-samples-batch-1.md", "## 2. "),
    "design_creative": ("2026-10-07-golden-samples-batch-1.md", "## 3. "),
    "digital_marketing": ("2026-10-07-golden-samples-batch-2.md", "## 1. "),
    "content_media": ("2026-10-07-golden-samples-batch-2.md", "## 2. "),
    "product_project": ("2026-10-07-golden-samples-batch-2.md", "## 3. "),
    "business_sales": ("2026-10-07-golden-samples-batch-2.md", "## 4. "),
    "finance_office": ("2026-10-07-golden-samples-batch-2.md", "## 5. "),
}

EASE = {
    "text": "Bu siz uchun qanday bo‘ldi?",
    "options": [
        {"id": "easy_interesting", "label": "Oson va qiziq"},
        {"id": "easy_boring", "label": "Oson, lekin zerikarli"},
        {"id": "hard_interesting", "label": "Qiyin, lekin qiziq"},
        {"id": "hard_boring", "label": "Qiyin va zerikarli"},
    ],
}

Q_HEAD = re.compile(r"^\*\*(\d+)\.\s+(.+?)\*\*\s*$")
OPT = re.compile(r"^- ([A-E])\)\s+(.+?)\s*$")
TAG = re.compile(r"^(.*?)\s+—\s+\*([^*]+)\*$")


def clean(s: str) -> str:
    return s.replace("\\*", "*").strip()


def parse_choice_block(lines, start):
    """Parse '**N. text**' + '- A) …' options from lines[start:]. Returns (num, text, opts, next_index)."""
    m = Q_HEAD.match(lines[start])
    num, text = int(m.group(1)), clean(m.group(2))
    opts, i = [], start + 1
    while i < len(lines) and (lines[i].startswith("- ") or not lines[i].strip()):
        om = OPT.match(lines[i])
        if om:
            opts.append((om.group(1), clean(om.group(2))))
        elif lines[i].strip() == "" and opts:
            break
        i += 1
    return num, text, opts, i


def parse_discovery(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        if Q_HEAD.match(line):
            num, text, opts, _ = parse_choice_block(lines, i)
            options = []
            for letter, label in opts:
                if letter == "E":
                    assert label.startswith("Bilmayman"), (num, label)
                    continue
                tm = TAG.match(label)
                assert tm, (num, label)
                options.append({"id": f"D2_Q{num:02d}_{letter}", "label": tm.group(1), "catalog": CAT_BY_NAME[tm.group(2)]})
            assert len(options) == 4, num
            options.append({"id": f"D2_Q{num:02d}_E", "label": NONE_LABEL, "catalog": None})
            out.append({"id": f"D2_Q{num:02d}", "text": text, "options": options})
    assert len(out) == 9, len(out)
    return out


def parse_deep(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    a_part, style, readiness = {}, [], []
    section, cat = None, None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("### 4."):
            name = re.match(r"^### 4\.\d+\.\s+(.+?)\s+\(", line).group(1)
            cat, section = CAT_BY_NAME[name], "A"
            a_part[cat] = []
        elif line.startswith("## 5."):
            section = "B"
        elif line.startswith("## 6."):
            section = "C"
        elif line.startswith("## 7."):
            section = None
        if section and Q_HEAD.match(line):
            num, text, opts, nxt = parse_choice_block(lines, i)
            if section == "A":
                options = []
                for letter, label in opts:
                    if letter == "E":
                        continue
                    tm = TAG.match(label)
                    assert tm, (cat, num, label)
                    options.append({"id": f"{cat}_A{num:02d}_{letter}", "label": tm.group(1), "career": CAREER_BY_TAG[tm.group(2)]})
                assert len(options) == 4, (cat, num)
                options.append({"id": f"{cat}_A{num:02d}_E", "label": NONE_LABEL, "career": None})
                a_part[cat].append({"id": f"{cat}_A{num:02d}", "text": text, "options": options})
            else:
                prefix = "B" if section == "B" else "C"
                options = [{"id": f"DV2_{prefix}{num:02d}_{letter}", "label": label} for letter, label in opts if letter != "E"]
                options.append({"id": f"DV2_{prefix}{num:02d}_E", "label": NONE_LABEL})
                (style if section == "B" else readiness).append({"id": f"DV2_{prefix}{num:02d}", "text": text, "options": options})
            i = nxt
            continue
        i += 1
    assert set(a_part) == {c for c, _, _ in CATALOGS}
    assert all(len(v) == 11 for v in a_part.values())
    assert len(style) == 5 and len(readiness) == 3, (len(style), len(readiness))
    return a_part, style, readiness


INLINE_OPT = re.compile(r"([A-E])\)\s+(.+?)(?=\s+·\s+[A-E]\)|$)")


def parse_options_block(lines, i):
    """Options as '- A) x ✔' lines or one inline '- A) x ✔ · B) y · …' line."""
    opts = []
    while i < len(lines) and lines[i].startswith("- "):
        body = lines[i][2:]
        if " · " in body and re.match(r"^[A-E]\)", body):
            for m in INLINE_OPT.finditer(body):
                opts.append((m.group(1), m.group(2).strip()))
        else:
            m = OPT.match(lines[i])
            opts.append((m.group(1), m.group(2).strip()))
        i += 1
    return opts, i


def to_task_options(prefix, opts):
    out, correct = [], None
    for letter, label in opts:
        if letter == "E":
            assert label.startswith("Bilmayman"), label
            continue
        is_correct = label.endswith("✔")
        label = clean(label.rstrip("✔").strip())
        if is_correct:
            assert correct is None, (prefix, "two correct answers")
            correct = f"{prefix}_{letter}"
        out.append({"id": f"{prefix}_{letter}", "label": label})
    assert len(out) == 4 and correct, (prefix, out, correct)
    out.append({"id": f"{prefix}_E", "label": TASK_NONE_LABEL})
    return out, correct


def section_lines(path: Path, header_prefix):
    lines = path.read_text(encoding="utf-8").splitlines()
    if header_prefix is None:
        return lines
    start = next(i for i, line in enumerate(lines) if line.startswith(header_prefix))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def parse_golden(lines, cat):
    tasks, lesson_text, lesson_qs = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        tm = re.match(r"^\*\*T(\d)\.\s+(.+?)\*\*", line)
        om = re.match(r"^\*\*O(\d)\.\*\*\s+(.+)$", line)
        if tm:
            n, title = int(tm.group(1)), clean(tm.group(2))
            i += 1
            text = []
            while not lines[i].startswith("- "):
                if lines[i].startswith("> "):
                    text.append(clean(lines[i][2:]))
                i += 1
            opts, i = parse_options_block(lines, i)
            options, correct = to_task_options(f"{cat}_T{n}", opts)
            tasks.append({"id": f"{cat}_T{n}", "title": title, "text": "\n".join(text), "options": options, "correct": correct})
            continue
        if line.startswith("**Mini-dars"):
            i += 1
            while i < len(lines) and not lines[i].startswith("**O"):
                if lines[i].startswith("> "):
                    lesson_text.append(clean(lines[i][2:]))
                i += 1
            continue
        if om:
            n, text = int(om.group(1)), [clean(om.group(2))]
            i += 1
            while not lines[i].startswith("- "):
                if lines[i].startswith("> "):
                    text.append(clean(lines[i][2:]))
                i += 1
            opts, i = parse_options_block(lines, i)
            options, correct = to_task_options(f"{cat}_O{n}", opts)
            lesson_qs.append({"id": f"{cat}_O{n}", "text": "\n".join(text), "options": options, "correct": correct})
            continue
        i += 1
    assert len(tasks) == 4, (cat, len(tasks))
    assert len(lesson_qs) == 2 and lesson_text, (cat, len(lesson_qs))
    return tasks, {"text": "\n".join(lesson_text), "questions": lesson_qs}


def main(spec_dir: Path):
    discovery = parse_discovery(spec_dir / "2026-10-05-discovery-v2-draft.md")
    a_part, style, readiness = parse_deep(spec_dir / "2026-10-05-deep-v2-draft.md")
    catalogs = []
    for cid, name, careers in CATALOGS:
        fname, header = GOLDEN[cid]
        tasks, lesson = parse_golden(section_lines(spec_dir / fname, header), cid)
        catalogs.append({
            "id": cid,
            "uz": name,
            "careers": [{"id": car, "uz": uz} for car, uz, _ in careers],
            "questions": a_part[cid],
            "tasks": tasks,
            "lesson": lesson,
        })
    data = {
        "version": "v2.0-draft",
        "status": "draft — founder review; not linked from the main flow",
        "sources": [
            "claude-qadamio docs/specs/2026-10-05-discovery-v2-draft.md",
            "claude-qadamio docs/specs/2026-10-05-deep-v2-draft.md",
            "claude-qadamio docs/specs/2026-10-05-dasturlash-golden-sample.md",
            "claude-qadamio docs/specs/2026-10-07-golden-samples-batch-1.md",
            "claude-qadamio docs/specs/2026-10-07-golden-samples-batch-2.md",
        ],
        "none_label": NONE_LABEL,
        "discovery": {"questions": discovery},
        "catalogs": catalogs,
        "style": style,
        "readiness": readiness,
        "ease": EASE,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT}: discovery {len(discovery)}, catalogs {len(catalogs)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
