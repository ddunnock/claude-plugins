"""Tests for source_tracker.py."""
import json

from source_tracker import add_source, export_sources, list_sources


def test_add_creates_source_with_correct_fields(tmp_workspace):
    src_id = add_source(str(tmp_workspace), "Study A", "https://example.com", "research")
    assert src_id == "SRC-001"
    reg = json.loads((tmp_workspace / "source_registry.json").read_text())
    assert reg["sources"][0]["title"] == "Study A"
    assert reg["sources"][0]["type"] == "research"


def test_add_auto_increments_id(tmp_workspace):
    id1 = add_source(str(tmp_workspace), "S1", "https://a.com", "research")
    id2 = add_source(str(tmp_workspace), "S2", "https://b.com", "standard")
    assert id1 == "SRC-001"
    assert id2 == "SRC-002"


def test_add_stores_research_context(tmp_workspace):
    add_source(str(tmp_workspace), "Study", "https://a.com", "research", research_context="REQ-001")
    reg = json.loads((tmp_workspace / "source_registry.json").read_text())
    assert reg["sources"][0]["research_context"] == "REQ-001"


def test_add_stores_concept_dev_ref(tmp_workspace):
    add_source(str(tmp_workspace), "Study", "https://a.com", "concept_dev", concept_dev_ref="SRC-005")
    reg = json.loads((tmp_workspace / "source_registry.json").read_text())
    assert reg["sources"][0]["concept_dev_ref"] == "SRC-005"


def test_list_returns_all_sources(tmp_workspace):
    add_source(str(tmp_workspace), "S1", "https://a.com", "research")
    add_source(str(tmp_workspace), "S2", "https://b.com", "standard")
    result = list_sources(str(tmp_workspace))
    assert len(result) == 2


def test_export_has_schema_version(tmp_workspace):
    add_source(str(tmp_workspace), "S1", "https://a.com", "research")
    result = export_sources(str(tmp_workspace))
    assert result["schema_version"] == "1.0.0"
    assert len(result["sources"]) == 1
