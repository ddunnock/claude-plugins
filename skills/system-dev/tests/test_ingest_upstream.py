"""Tests for upstream ingestion engine: ingestion, filtering, reports, re-ingestion."""

import json
import os
import time

import pytest

from scripts.init_workspace import init_workspace
from scripts.ingest_upstream import IngestResult, ingest_all
from scripts.registry import SlotAPI


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _schemas_dir() -> str:
    """Return absolute path to schemas/ directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


def create_fake_upstream(tmp_path, **overrides) -> str:
    """Create minimal .requirements-dev/ structure for testing.

    Returns the path to the upstream directory.
    """
    upstream = tmp_path / "upstream"
    upstream.mkdir()

    needs = overrides.get("needs", [
        {"id": "NEED-001", "statement": "System shall do X", "stakeholder": "Architect",
         "status": "registered", "registered_at": "2026-01-01T00:00:00Z"},
        {"id": "NEED-002", "statement": "System shall do Y", "stakeholder": "User",
         "status": "registered", "registered_at": "2026-01-01T00:00:00Z"},
    ])

    requirements = overrides.get("requirements", [
        {"id": "REQ-001", "statement": "Implement X", "type": "functional",
         "priority": "high", "status": "baselined", "parent_need": "NEED-001",
         "source_block": "INGS", "level": "system",
         "registered_at": "2026-01-01T00:00:00Z"},
        {"id": "REQ-002", "statement": "Implement Y", "type": "functional",
         "priority": "medium", "status": "baselined", "parent_need": "NEED-002",
         "source_block": "INGS", "level": "system",
         "registered_at": "2026-01-01T00:00:00Z"},
        {"id": "REQ-003", "statement": "Draft req", "type": "functional",
         "priority": "low", "status": "draft", "parent_need": "NEED-001",
         "source_block": "INGS", "level": "system",
         "registered_at": "2026-01-01T00:00:00Z"},
    ])

    sources = overrides.get("sources", [
        {"id": "SRC-001", "title": "Best Practices Guide", "url": "https://example.com",
         "type": "literature", "confidence": "high",
         "registered_at": "2026-01-01T00:00:00Z"},
    ])

    assumptions = overrides.get("assumptions", [
        {"id": "A-001", "statement": "Registry is shared", "category": "architectural",
         "status": "active", "related_requirements": ["REQ-001"],
         "registered_at": "2026-01-01T00:00:00Z"},
    ])

    links = overrides.get("links", [
        {"type": "derives_from", "from": "REQ-001", "to": "NEED-001",
         "rationale": "Implements", "registered_at": "2026-01-01T00:00:00Z"},
        {"type": "derives_from", "from": "REQ-002", "to": "NEED-002",
         "rationale": "Implements", "registered_at": "2026-01-01T00:00:00Z"},
    ])

    gates = overrides.get("gates", {"init": True, "needs": True, "requirements": True})

    (upstream / "needs_registry.json").write_text(json.dumps({"needs": needs}))
    (upstream / "requirements_registry.json").write_text(json.dumps({"requirements": requirements}))
    (upstream / "source_registry.json").write_text(json.dumps({"sources": sources}))
    (upstream / "assumptions_registry.json").write_text(json.dumps({"assumptions": assumptions}))
    (upstream / "traceability_matrix.json").write_text(json.dumps({"links": links}))
    (upstream / "state.json").write_text(json.dumps({"gates": gates}))

    return str(upstream)


def setup_workspace(tmp_path) -> str:
    """Initialize a workspace and return the .system-dev path."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    init_workspace(str(project_root))
    return str(project_root / ".system-dev")


# ---------------------------------------------------------------------------
# Tests: First-time ingestion
# ---------------------------------------------------------------------------


class TestFirstTimeIngestion:
    """Tests for initial ingestion from empty workspace."""

    def test_ingest_all_first_time(self, tmp_path):
        """Fresh workspace: all entries ingested with correct slot counts."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        # 2 needs + 2 reqs (1 draft skipped) + 1 source + 1 assumption + 2 links = 8
        assert result.total_ingested == 8
        assert result.created == 8
        assert result.updated == 0
        assert result.skipped == 1  # draft req
        assert result.conflicts == 0

    def test_status_filtering_draft_withdrawn(self, tmp_path):
        """Draft and withdrawn requirements are skipped."""
        reqs = [
            {"id": "REQ-001", "statement": "Active", "type": "functional",
             "priority": "high", "status": "baselined", "parent_need": "NEED-001",
             "source_block": "A", "level": "system", "registered_at": "2026-01-01T00:00:00Z"},
            {"id": "REQ-002", "statement": "Draft", "type": "functional",
             "priority": "low", "status": "draft", "parent_need": "NEED-001",
             "source_block": "A", "level": "system", "registered_at": "2026-01-01T00:00:00Z"},
            {"id": "REQ-003", "statement": "Withdrawn", "type": "functional",
             "priority": "low", "status": "withdrawn", "parent_need": "NEED-001",
             "source_block": "A", "level": "system", "registered_at": "2026-01-01T00:00:00Z"},
        ]
        upstream = create_fake_upstream(tmp_path, requirements=reqs)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.skipped == 2  # draft + withdrawn

    def test_translate_need_to_slot(self, tmp_path):
        """Need entry produces valid need slot with correct fields."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())
        slot = api.read("need:NEED-001")

        assert slot is not None
        assert slot["slot_type"] == "need"
        assert slot["upstream_id"] == "NEED-001"
        assert slot["description"] == "System shall do X"
        assert slot["stakeholder"] == "Architect"

    def test_translate_requirement_to_slot(self, tmp_path):
        """Requirement produces slot with derives_from cross-refs."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())
        slot = api.read("requirement:REQ-001")

        assert slot is not None
        assert slot["derives_from"] == ["need:NEED-001"]
        assert slot["requirement_type"] == "functional"

    def test_translate_source_to_slot(self, tmp_path):
        """Source with confidence level preserved (GAP-4)."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())
        slot = api.read("source:SRC-001")

        assert slot is not None
        assert slot["name"] == "Best Practices Guide"
        assert slot["confidence"] == "high"

    def test_provenance_metadata_on_all_slots(self, tmp_path):
        """Every ingested slot has provenance metadata."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())

        for slot_id in ["need:NEED-001", "requirement:REQ-001", "source:SRC-001"]:
            slot = api.read(slot_id)
            assert slot is not None, f"Slot {slot_id} not found"
            prov = slot.get("provenance")
            assert prov is not None, f"No provenance on {slot_id}"
            assert prov["source"] == "requirements-dev"
            assert "ingested_at" in prov
            assert "hash" in prov

    def test_gap_markers_applied(self, tmp_path):
        """Ingested entries have appropriate gap markers."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.gap_markers_added > 0

        api = SlotAPI(workspace, _schemas_dir())
        # Needs should have GAP-1, GAP-2
        need = api.read("need:NEED-001")
        assert need is not None
        markers = need.get("gap_markers", [])
        refs = [m["finding_ref"] for m in markers]
        assert "GAP-1" in refs
        assert "GAP-2" in refs


# ---------------------------------------------------------------------------
# Tests: Reports
# ---------------------------------------------------------------------------


class TestReports:
    """Tests for delta report, compatibility report, and manifest."""

    def test_delta_report_written(self, tmp_path):
        """After ingestion, delta-report.json exists with correct structure."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.delta_report_path is not None
        assert os.path.exists(result.delta_report_path)

        with open(result.delta_report_path) as f:
            report = json.load(f)

        assert report["schema_version"] == "1.0.0"
        assert "summary" in report
        assert "details" in report
        assert "added" in report["summary"]
        assert "modified" in report["summary"]

    def test_compatibility_report_written(self, tmp_path):
        """After ingestion, compatibility-report.json exists with finding counts."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.compatibility_report_path is not None
        assert os.path.exists(result.compatibility_report_path)

        with open(result.compatibility_report_path) as f:
            report = json.load(f)

        assert report["schema_version"] == "1.0.0"
        assert "findings" in report
        assert "total_gap_markers" in report
        assert report["total_gap_markers"] > 0

    def test_manifest_written(self, tmp_path):
        """After ingestion, ingestion-manifest.json exists with hashes."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        manifest_path = os.path.join(workspace, "ingestion-manifest.json")
        assert os.path.exists(manifest_path)

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert manifest["schema_version"] == "1.0.0"
        assert len(manifest["hashes"]) > 0
        assert manifest["upstream_path"] == upstream


# ---------------------------------------------------------------------------
# Tests: Re-ingestion
# ---------------------------------------------------------------------------


class TestReIngestion:
    """Tests for delta detection on re-ingestion."""

    def test_re_ingestion_unchanged(self, tmp_path):
        """Ingest twice with same data: second run shows all unchanged."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result1 = ingest_all(upstream, workspace, _schemas_dir())
        assert result1.created > 0

        result2 = ingest_all(upstream, workspace, _schemas_dir())
        assert result2.created == 0
        assert result2.updated == 0
        assert result2.total_ingested == 0

    def test_re_ingestion_with_changes(self, tmp_path):
        """Modify upstream data between runs: second run detects modifications."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        # Modify a need
        needs_path = os.path.join(upstream, "needs_registry.json")
        with open(needs_path) as f:
            data = json.load(f)
        data["needs"][0]["statement"] = "Modified statement"
        with open(needs_path, "w") as f:
            json.dump(data, f)

        result2 = ingest_all(upstream, workspace, _schemas_dir())
        assert result2.updated >= 1
        assert result2.total_ingested >= 1

    def test_conflict_preservation(self, tmp_path):
        """Locally edit an ingested slot (version > 1), re-ingest preserves edit."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        # Locally edit slot (bumps version to 2)
        api = SlotAPI(workspace, _schemas_dir())
        slot = api.read("need:NEED-001")
        assert slot is not None
        slot["description"] = "Locally edited description"
        api.update("need:NEED-001", slot, expected_version=1)

        # Modify upstream
        needs_path = os.path.join(upstream, "needs_registry.json")
        with open(needs_path) as f:
            data = json.load(f)
        data["needs"][0]["statement"] = "Changed upstream"
        with open(needs_path, "w") as f:
            json.dump(data, f)

        result2 = ingest_all(upstream, workspace, _schemas_dir())
        assert result2.conflicts >= 1

        # Verify local edit preserved
        slot_after = api.read("need:NEED-001")
        assert slot_after["description"] == "Locally edited description"


# ---------------------------------------------------------------------------
# Tests: Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Tests for partial ingestion and gate warnings."""

    def test_partial_ingestion_on_error(self, tmp_path):
        """Corrupt one registry file: other registries still ingest (XCUT-01)."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        # Corrupt requirements registry
        req_path = os.path.join(upstream, "requirements_registry.json")
        with open(req_path, "w") as f:
            f.write("{invalid json")

        result = ingest_all(upstream, workspace, _schemas_dir())

        # Other registries should still have ingested
        assert result.total_ingested > 0
        assert len(result.warnings) > 0
        assert any("requirements_registry" in w for w in result.warnings)

    def test_gate_warnings_but_still_ingests(self, tmp_path):
        """Incomplete upstream gates produce warnings but ingestion continues."""
        upstream = create_fake_upstream(
            tmp_path, gates={"init": True, "needs": True, "requirements": False}
        )
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.total_ingested > 0
        assert any("Gate warning" in w for w in result.warnings)

    def test_batch_journal_entry(self, tmp_path):
        """Journal has ONE batch entry, not hundreds of individual entries."""
        upstream = create_fake_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        journal_path = os.path.join(workspace, "journal.jsonl")
        with open(journal_path) as f:
            entries = [json.loads(line) for line in f if line.strip()]

        # Should have exactly 1 batch entry from ingestion
        ingest_entries = [e for e in entries if e["operation"] == "ingest"]
        assert len(ingest_entries) == 1
        assert ingest_entries[0]["slot_id"] == "ingestion-batch"


# ---------------------------------------------------------------------------
# Tests: Performance
# ---------------------------------------------------------------------------


class TestBulkPerformance:
    """Performance tests for bulk ingestion."""

    def test_bulk_performance_500_entries(self, tmp_path):
        """500 requirements ingested in < 5 seconds (REQ-246)."""
        reqs = []
        for i in range(500):
            reqs.append({
                "id": f"REQ-{i:04d}",
                "statement": f"Requirement {i}",
                "type": "functional",
                "priority": "high",
                "status": "baselined",
                "parent_need": "NEED-001",
                "source_block": "PERF",
                "level": "system",
                "registered_at": "2026-01-01T00:00:00Z",
            })

        upstream = create_fake_upstream(
            tmp_path,
            needs=[{"id": "NEED-001", "statement": "Perf need", "stakeholder": "Test",
                    "status": "registered", "registered_at": "2026-01-01T00:00:00Z"}],
            requirements=reqs,
            sources=[],
            assumptions=[],
            links=[],
        )
        workspace = setup_workspace(tmp_path)

        start = time.monotonic()
        result = ingest_all(upstream, workspace, _schemas_dir())
        elapsed = time.monotonic() - start

        assert elapsed < 5.0, f"Ingestion took {elapsed:.2f}s, expected < 5s"
        assert result.total_ingested >= 500
