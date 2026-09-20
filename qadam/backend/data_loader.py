import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load(name):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_taxonomy():
    return _load("taxonomy_v1.json")


def load_questions():
    return _load("questions_v1.json")


def load_signals():
    return _load("signals_v1.json")


def load_roadmap_kb():
    return _load("roadmap_kb_v1.json")


def get_versions():
    return {
        "taxonomy": "v1.0",
        "questions": "v1.0",
        "signals": "v1.0",
        "roadmap_kb": "v1.1",
        "ai_prompt": "v1.0",
    }
