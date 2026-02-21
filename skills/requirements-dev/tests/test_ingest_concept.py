"""Tests for ingest_concept.py -- concept-dev artifact ingestion."""
import json

import pytest

from ingest_concept import ingest


@pytest.fixture
def concept_dev_dir(tmp_path):
    """Create a mock .concept-dev/ directory with valid artifacts."""
    cd = tmp_path / ".concept-dev"
    cd.mkdir()

    # state.json with all gates passed
    state = {
        "session": {"id": "test-abc"},
        "current_phase": "complete",
        "gates": {"problem": True, "concept": True, "architecture": True, "landscape": True},
    }
    (cd / "state.json").write_text(json.dumps(state))

    # source_registry.json
    sources = {
        "schema_version": "1.0.0",
        "sources": [{"id": "SRC-001", "title": "Test Source", "type": "document"}],
    }
    (cd / "source_registry.json").write_text(json.dumps(sources))

    # assumption_registry.json
    assumptions = {
        "schema_version": "1.0.0",
        "assumptions": [
            {"id": "ASN-001", "statement": "Test assumption", "status": "approved"}
        ],
    }
    (cd / "assumption_registry.json").write_text(json.dumps(assumptions))

    # Markdown artifacts (presence checked, not parsed by script)
    (cd / "CONCEPT-DOCUMENT.md").write_text("# Concept Document\n")
    (cd / "BLACKBOX.md").write_text("# Blackbox\n")

    return tmp_path


def test_ingest_valid_directory_returns_source_refs(concept_dev_dir, tmp_path):
    """ingest() with valid concept-dev directory returns source_refs."""
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert len(result["source_refs"]) == 1
    assert result["source_refs"][0]["id"] == "SRC-001"


def test_ingest_valid_directory_returns_assumption_refs(concept_dev_dir, tmp_path):
    """ingest() with valid concept-dev directory returns assumption_refs."""
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert len(result["assumption_refs"]) == 1
    assert result["assumption_refs"][0]["id"] == "ASN-001"


def test_ingest_reports_correct_gate_status(concept_dev_dir, tmp_path):
    """ingest() with all gates passed reports correct gate_status."""
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert result["gate_status"]["all_passed"] is True
    assert result["gate_status"]["warnings"] == []


def test_ingest_missing_source_registry(concept_dev_dir, tmp_path):
    """ingest() with missing source_registry.json returns empty source_refs."""
    (concept_dev_dir / ".concept-dev" / "source_registry.json").unlink()
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert result["source_refs"] == []


def test_ingest_missing_assumption_registry(concept_dev_dir, tmp_path):
    """ingest() with missing assumption_registry.json returns empty assumption_refs."""
    (concept_dev_dir / ".concept-dev" / "assumption_registry.json").unlink()
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert result["assumption_refs"] == []


def test_ingest_failed_gates_reports_warnings(concept_dev_dir, tmp_path):
    """ingest() with failed gates includes warnings in gate_status."""
    state_path = concept_dev_dir / ".concept-dev" / "state.json"
    state = json.loads(state_path.read_text())
    state["gates"]["architecture"] = False
    state_path.write_text(json.dumps(state))
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert result["gate_status"]["all_passed"] is False
    assert any("architecture" in w for w in result["gate_status"]["warnings"])


def test_ingest_missing_concept_dev_returns_fallback(tmp_path):
    """ingest() with no .concept-dev/ returns graceful fallback dict."""
    nonexistent = str(tmp_path / "does-not-exist")
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(nonexistent, str(output))
    assert result["source_refs"] == []
    assert result["assumption_refs"] == []
    assert result["gate_status"]["all_passed"] is False
    assert len(result["gate_status"]["warnings"]) > 0
    assert result["artifact_inventory"] == {}


def test_ingest_validates_path_rejects_traversal(tmp_path):
    """ingest() rejects paths containing '..' traversal."""
    bad_path = str(tmp_path / ".." / "escape")
    output = str(tmp_path / "ingestion.json")
    with pytest.raises(SystemExit):
        ingest(bad_path, output)


def test_ingest_output_contains_artifact_inventory(concept_dev_dir, tmp_path):
    """ingest() output includes artifact_inventory listing which files exist."""
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    inv = result["artifact_inventory"]
    assert inv["CONCEPT-DOCUMENT.md"] is True
    assert inv["BLACKBOX.md"] is True
    assert inv["SOLUTION-LANDSCAPE.md"] is False
    assert inv["source_registry.json"] is True
    assert inv["assumption_registry.json"] is True
    assert inv["state.json"] is True


def test_ingest_writes_output_file(concept_dev_dir, tmp_path):
    """ingest() writes the result to the specified output path."""
    output = tmp_path / "out" / "ingestion.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = ingest(str(concept_dev_dir / ".concept-dev"), str(output))
    assert output.exists()
    written = json.loads(output.read_text())
    assert written["source_refs"] == result["source_refs"]
