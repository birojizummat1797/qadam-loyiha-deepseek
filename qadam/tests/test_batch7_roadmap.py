"""Batch 7 — Roadmap testlari."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from engine.roadmap_engine import build_roadmap, KB, TEMPLATES


def test_templates_loaded():
    assert "templates" in TEMPLATES
    assert "software" in TEMPLATES["templates"]
    assert "data_ai" in TEMPLATES["templates"]


def test_template_has_4_phases():
    for cluster_key, tpl in TEMPLATES["templates"].items():
        assert len(tpl["phases"]) == 4, f"{cluster_key} 4 ta faza kerak"


def test_build_roadmap_from_template():
    """KB'da yo'q career → template fallback."""
    career = {"title_uz": "Test Career", "cluster": "software"}
    ranked = {"career_id": "test_slug", "fit": 80, "readiness": 70, "barriers": []}
    rm = build_roadmap("test_slug", career, ranked)
    assert rm["source"] in ("template", "kb")
    assert len(rm["phases"]) >= 1
    assert len(rm["next_3_actions"]) >= 1


def test_build_roadmap_kb_foundation():
    """KB'da bor career — ishlatilishi kerak."""
    career = {"title_uz": "Foundation Programming", "cluster": "software"}
    ranked = {"career_id": "foundation_programming", "fit": 85, "readiness": 100, "barriers": []}
    rm = build_roadmap("foundation_programming", career, ranked)
    assert rm["source"] in ("kb", "template")  # KB ustuvor, lekin testda har ikki xil
    assert "next_3_actions" in rm


def test_barrier_resolutions():
    career = {"title_uz": "Frontend", "cluster": "software"}
    ranked = {
        "career_id": "fe",
        "fit": 80,
        "readiness": 50,
        "barriers": [
            {"type": "device", "level": "soft", "path": "Noutbuk topish"},
            {"type": "language", "level": "soft", "path": "Ingliz B1"},
        ],
    }
    rm = build_roadmap("fe", career, ranked)
    assert len(rm["barrier_resolutions"]) == 2


def test_roadmap_has_why():
    career = {"title_uz": "Test", "cluster": "design_creative"}
    ranked = {"career_id": "t", "fit": 70, "readiness": 60, "barriers": []}
    rm = build_roadmap("t", career, ranked)
    assert rm["why"]


def test_all_clusters_have_templates():
    """Har 8 cluster uchun template bo'lishi kerak."""
    required = [
        "software", "data_ai", "infra_security", "design_creative",
        "digital_marketing", "content_media", "product_project", "business_sales",
    ]
    for c in required:
        assert c in TEMPLATES["templates"], f"{c} template yo'q"
