"""Signal labels have one source: backend signals_v1.json (PM gate, 2026-10-03).

Mini App and PDF must show exactly the backend label; the website snapshot is
checked in claude-qadamio (tests/unit/career-snapshot.test.ts).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.data_loader import load_signals

ROOT = Path(__file__).parent.parent.parent
BACKEND = {k: v["uz"] for k, v in load_signals()["signals"].items()}


def test_backend_labels_have_no_known_typos():
    assert BACKEND["persistence"] == "Qat’iyat"
    assert BACKEND["attention_to_detail"] == "Detallarga e’tibor"
    assert len(BACKEND) == 13


def test_miniapp_labels_are_a_verbatim_copy():
    data = json.loads((ROOT / "qadam-miniapp" / "lib" / "signal-labels.json").read_text(encoding="utf-8"))
    assert data["labels"] == BACKEND


def test_miniapp_has_no_own_signal_label_maps():
    for f in (ROOT / "qadam-miniapp").glob("**/*.tsx"):
        if "node_modules" in f.parts or ".next" in f.parts:
            continue
        assert "SIGNAL_UZ" not in f.read_text(encoding="utf-8"), f


def test_pdf_uses_backend_labels():
    from backend.pdf_report import SIGNAL_UZ

    assert SIGNAL_UZ == BACKEND
