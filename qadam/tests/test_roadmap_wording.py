"""Roadmap wording: describe the path, never judge the user (owner direction 2026-10-04).

- No claims about the user's traits in static text ("Sizning kreativligingiz…"):
  the same text is shown to everyone, so it cannot be a reason about *them*.
- No success promises, guarantees, ability verdicts or exclamations.
- Outcomes describe what the path prepares for (applying), not a position won.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

ROOT = Path(__file__).parent.parent
DATA = ROOT / "backend" / "data"
MINIAPP = ROOT.parent / "qadam-miniapp"

FORBIDDEN = {
    "trait claim about the user": re.compile(r"\bSizning\s+\w+(ingiz|ingiz)\b", re.I),
    "success promise": re.compile(r"muvaffaqiyat|kafolat|albatta|shubhasiz", re.I),
    "ability verdict": re.compile(r"qobiliyat\w*\s+yo['’]q|bo['’]la olmaysiz|imkonsiz", re.I),
    "exclamation": re.compile(r"!"),
    "position won": re.compile(r"\blavozimi\b"),
}


def visible_strings(obj, path=""):
    skip = {"url", "lang", "salary_uzs", "salary_usd", "junior_salary_uzs", "remote_salary_usd", "income_factors"}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip:
                yield from visible_strings(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from visible_strings(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


@pytest.mark.parametrize("kb", ["roadmap_kb_v2.json", "roadmap_kb_v1.json"])
def test_kb_has_no_verdicts_or_promises(kb):
    data = json.loads((DATA / kb).read_text(encoding="utf-8"))
    bad = [
        (rule, path, text)
        for path, text in visible_strings(data["careers"])
        for rule, rx in FORBIDDEN.items()
        if rx.search(text)
    ]
    assert not bad, "\n".join(f"{r}: {p}: {t}" for r, p, t in bad[:20])


STRICT_LABELS = [
    "Nega bu yo&apos;nalish ko&apos;rsatildi", "Hal qilish kerak", "Yaxshilash kerak",
    "stage'ga shart", "Bugun boshlang",
]


@pytest.mark.parametrize("rel", ["components/RoadmapView.tsx", "app/roadmap/[slug]/page.tsx"])
def test_miniapp_labels_are_not_strict(rel):
    src = (MINIAPP / rel).read_text(encoding="utf-8")
    assert not [label for label in STRICT_LABELS if label in src]


def test_pdf_and_placeholder_labels():
    pdf = (ROOT / "backend" / "pdf_report.py").read_text(encoding="utf-8")
    assert "ko\\'rsatildi" not in pdf and "stage'ga shart" not in pdf
    roadmap = (ROOT / "backend" / "engine" / "roadmap.py").read_text(encoding="utf-8")
    assert "signallaringizga mos" not in roadmap
