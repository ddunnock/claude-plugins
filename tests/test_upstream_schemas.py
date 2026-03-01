"""Tests for upstream field mapping, gap markers, hashing, and gate status."""

import json
import os
import tempfile

import pytest

from scripts.upstream_schemas import (
    ASSUMPTION_FIELD_MAP,
    GAP_MARKERS,
    HASH_EXCLUDE_KEYS,
    NEED_FIELD_MAP,
    REQUIREMENT_FIELD_MAP,
    SOURCE_FIELD_MAP,
    TRACEABILITY_FIELD_MAP,
    check_upstream_gates,
    content_hash,
    generate_slot_id,
    generate_trace_id,
    load_upstream_registry,
    map_upstream_entry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_need_entry() -> dict:
    """Create a sample upstream need entry."""
    return {
        "id": "NEED-001",
        "statement": "The system shall support design decisions",
        "stakeholder": "System Architect",
        "source_block": "BLOCK-01",
        "source_artifacts": ["concept-dev-001"],
        "concept_dev_refs": ["ref-001"],
        "status": "registered",
        "rationale": "Core capability",
        "registered_at": "2026-01-15T10:00:00Z",
    }


def _make_requirement_entry() -> dict:
    """Create a sample upstream requirement entry."""
    return {
        "id": "REQ-026",
        "statement": "Ingest registered/baselined requirements into slots",
        "type": "functional",
        "priority": "high",
        "status": "baselined",
        "parent_need": "NEED-001",
        "source_block": "INGS",
        "level": "system",
        "attributes": {"testable": True, "measurable": True},
        "quality_checks": {"completeness": "pass", "consistency": "pass"},
        "rationale": "Foundation for design traceability",
        "registered_at": "2026-01-20T10:00:00Z",
        "baselined_at": "2026-02-01T10:00:00Z",
    }


def _make_source_with_title() -> dict:
    """Create a source entry using 'title' field (SCHEMA-1)."""
    return {
        "id": "SRC-001",
        "title": "Requirements Engineering Best Practices",
        "url": "https://example.com/re-best-practices",
        "type": "literature",
        "confidence": "high",
        "research_context": "concept-dev phase 2",
        "concept_dev_ref": "CD-REF-001",
        "registered_at": "2026-01-10T10:00:00Z",
    }


def _make_source_with_name() -> dict:
    """Create a source entry using 'name' field (SCHEMA-1 alternate)."""
    return {
        "id": "SRC-002",
        "name": "Industry Survey Results",
        "url": "https://example.com/survey",
        "type": "survey",
        "confidence": "medium",
        "registered_at": "2026-01-12T10:00:00Z",
    }


def _make_assumption_entry() -> dict:
    """Create a sample upstream assumption entry."""
    return {
        "id": "A-001",
        "statement": "All design agents have read access to the registry",
        "category": "architectural",
        "status": "active",
        "source_block": "BLOCK-02",
        "related_requirements": ["REQ-026", "REQ-030"],
        "rationale": "Shared registry is the communication backbone",
        "registered_at": "2026-01-18T10:00:00Z",
    }


def _make_traceability_entry() -> dict:
    """Create a sample upstream traceability link entry."""
    return {
        "type": "derives_from",
        "from": "REQ-026",
        "to": "NEED-001",
        "rationale": "REQ-026 implements NEED-001",
        "registered_at": "2026-01-22T10:00:00Z",
    }


# ---------------------------------------------------------------------------
# Test: Field mapping
# ---------------------------------------------------------------------------


class TestFieldMapping:
    """Tests for map_upstream_entry with various entity types."""

    def test_map_need_entry(self):
        """Map a complete need entry, verify all fields mapped correctly."""
        entry = _make_need_entry()
        result = map_upstream_entry(entry, NEED_FIELD_MAP, "need", "needs_registry.json")

        assert result["upstream_id"] == "NEED-001"
        assert result["description"] == "The system shall support design decisions"
        assert result["stakeholder"] == "System Architect"
        assert result["source_block"] == "BLOCK-01"
        assert result["source_artifacts"] == ["concept-dev-001"]
        assert result["concept_dev_refs"] == ["ref-001"]
        assert result["upstream_status"] == "registered"
        assert result["rationale"] == "Core capability"
        assert result["upstream_registered_at"] == "2026-01-15T10:00:00Z"

    def test_map_requirement_entry(self):
        """Map a requirement, verify all fields including derives_from cross-refs."""
        entry = _make_requirement_entry()
        result = map_upstream_entry(
            entry, REQUIREMENT_FIELD_MAP, "requirement", "requirements_registry.json"
        )

        assert result["upstream_id"] == "REQ-026"
        assert result["description"] == "Ingest registered/baselined requirements into slots"
        assert result["requirement_type"] == "functional"
        assert result["priority"] == "high"
        assert result["upstream_status"] == "baselined"
        assert result["parent_need"] == "NEED-001"
        assert result["source_block"] == "INGS"
        assert result["decomposition_level"] == "system"
        assert result["upstream_attributes"] == {"testable": True, "measurable": True}
        assert result["quality_checks"] == {"completeness": "pass", "consistency": "pass"}
        assert result["upstream_registered_at"] == "2026-01-20T10:00:00Z"
        assert result["upstream_baselined_at"] == "2026-02-01T10:00:00Z"

    def test_map_source_with_title(self):
        """Map source with 'title' field (SCHEMA-1)."""
        entry = _make_source_with_title()
        result = map_upstream_entry(
            entry, SOURCE_FIELD_MAP, "source", "source_registry.json"
        )

        assert result["name"] == "Requirements Engineering Best Practices"
        assert result["upstream_id"] == "SRC-001"
        assert result["url"] == "https://example.com/re-best-practices"
        assert result["source_type"] == "literature"
        assert result["confidence"] == "high"
        assert result["research_context"] == "concept-dev phase 2"
        assert result["concept_dev_ref"] == "CD-REF-001"

    def test_map_source_with_name(self):
        """Map source with 'name' field (SCHEMA-1 alternate)."""
        entry = _make_source_with_name()
        result = map_upstream_entry(
            entry, SOURCE_FIELD_MAP, "source", "source_registry.json"
        )

        assert result["name"] == "Industry Survey Results"
        assert result["upstream_id"] == "SRC-002"
        assert result["source_type"] == "survey"
        assert result["confidence"] == "medium"

    def test_provenance_metadata(self):
        """Mapped entry contains provenance with source, file, timestamp, and hash."""
        entry = _make_need_entry()
        result = map_upstream_entry(entry, NEED_FIELD_MAP, "need", "needs_registry.json")

        assert "provenance" in result
        prov = result["provenance"]
        assert prov["source"] == "requirements-dev"
        assert prov["upstream_file"] == "needs_registry.json"
        assert "ingested_at" in prov
        assert "hash" in prov
        assert len(prov["hash"]) == 64  # SHA-256 hex digest

    def test_missing_optional_fields_not_in_result(self):
        """Optional fields missing from upstream are not present in mapped result."""
        entry = {"id": "NEED-002", "statement": "Minimal need"}
        result = map_upstream_entry(entry, NEED_FIELD_MAP, "need", "needs_registry.json")

        assert result["upstream_id"] == "NEED-002"
        assert result["description"] == "Minimal need"
        assert "stakeholder" not in result
        assert "source_block" not in result


# ---------------------------------------------------------------------------
# Test: Gap markers
# ---------------------------------------------------------------------------


class TestGapMarkers:
    """Tests for GAP_MARKERS definitions."""

    def test_gap_marker_format(self):
        """All gap markers have required fields: type, finding_ref, severity, description."""
        required_fields = {"type", "finding_ref", "severity", "description"}
        valid_types = {"missing_data", "schema_mismatch", "known_bug"}
        valid_severities = {"low", "medium", "high"}

        for gap_id, marker in GAP_MARKERS.items():
            assert required_fields.issubset(marker.keys()), (
                f"{gap_id} missing fields: {required_fields - marker.keys()}"
            )
            assert marker["type"] in valid_types, (
                f"{gap_id} has invalid type: {marker['type']}"
            )
            assert marker["severity"] in valid_severities, (
                f"{gap_id} has invalid severity: {marker['severity']}"
            )
            assert marker["finding_ref"] == gap_id

    def test_gap_markers_cover_expected_findings(self):
        """GAP_MARKERS covers GAP-1, GAP-2, GAP-3, GAP-5, GAP-7, GAP-8."""
        expected = {"GAP-1", "GAP-2", "GAP-3", "GAP-5", "GAP-7", "GAP-8"}
        assert set(GAP_MARKERS.keys()) == expected


# ---------------------------------------------------------------------------
# Test: Content hashing
# ---------------------------------------------------------------------------


class TestContentHash:
    """Tests for content_hash determinism and exclusion."""

    def test_content_hash_deterministic(self):
        """Same input gives same hash."""
        entry = _make_need_entry()
        h1 = content_hash(entry)
        h2 = content_hash(entry)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_content_hash_excludes_timestamps(self):
        """Changing excluded keys (timestamps) doesn't change hash."""
        entry = _make_need_entry()
        h1 = content_hash(entry)

        entry_modified = dict(entry)
        entry_modified["registered_at"] = "2099-12-31T23:59:59Z"
        h2 = content_hash(entry_modified)

        assert h1 == h2

    def test_content_hash_changes_on_content_change(self):
        """Changing non-excluded fields changes the hash."""
        entry = _make_need_entry()
        h1 = content_hash(entry)

        entry_modified = dict(entry)
        entry_modified["statement"] = "Different statement"
        h2 = content_hash(entry_modified)

        assert h1 != h2

    def test_content_hash_custom_excludes(self):
        """Custom exclude_keys parameter works."""
        entry = {"a": 1, "b": 2, "c": 3}
        h1 = content_hash(entry, exclude_keys=set())
        h2 = content_hash(entry, exclude_keys={"c"})
        assert h1 != h2


# ---------------------------------------------------------------------------
# Test: Gate status checking
# ---------------------------------------------------------------------------


class TestGateStatus:
    """Tests for check_upstream_gates with various schemas."""

    def _write_state(self, tmpdir: str, data: dict) -> str:
        """Write a state.json file and return its path."""
        path = os.path.join(tmpdir, "state.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_gate_status_correct_schema(self):
        """Flat 'gates' dict with all passing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_state(tmpdir, {
                "gates": {"init": True, "needs": True, "requirements": True}
            })
            result = check_upstream_gates(path)

            assert result["all_passed"] is True
            assert result["gates"] == {"init": True, "needs": True, "requirements": True}
            assert result["warnings"] == []

    def test_gate_status_correct_schema_with_failures(self):
        """Flat 'gates' dict with some failing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_state(tmpdir, {
                "gates": {"init": True, "needs": True, "requirements": False}
            })
            result = check_upstream_gates(path)

            assert result["all_passed"] is False
            assert len(result["warnings"]) == 1
            assert "requirements" in result["warnings"][0]

    def test_gate_status_concept_dev_schema(self):
        """Nested 'phases' dict (BUG-1 workaround)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_state(tmpdir, {
                "phases": {
                    "init": {"gate_passed": True},
                    "needs": {"gate_passed": True},
                    "requirements": {"gate_passed": False},
                }
            })
            result = check_upstream_gates(path)

            assert result["all_passed"] is False
            assert result["gates"]["init"] is True
            assert result["gates"]["requirements"] is False

    def test_gate_status_empty_gates(self):
        """Empty gates dict -- BUG-3 handling."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_state(tmpdir, {"gates": {}})
            result = check_upstream_gates(path)

            assert result["all_passed"] is False
            assert "empty" in result["warnings"][0].lower()

    def test_gate_status_missing_gates(self):
        """No gate info at all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self._write_state(tmpdir, {"version": "1.0"})
            result = check_upstream_gates(path)

            assert result["all_passed"] is False
            assert "No gate information" in result["warnings"][0]


# ---------------------------------------------------------------------------
# Test: Registry loading
# ---------------------------------------------------------------------------


class TestLoadUpstreamRegistry:
    """Tests for load_upstream_registry."""

    def test_load_upstream_registry_missing_key(self):
        """KeyError raised for missing top_key, NOT silent .get()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_registry.json")
            with open(filepath, "w") as f:
                json.dump({"wrong_key": []}, f)

            with pytest.raises(KeyError, match="Expected key 'needs'"):
                load_upstream_registry(tmpdir, "test_registry.json", "needs")

    def test_load_upstream_registry_missing_file(self):
        """FileNotFoundError for missing registry file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError, match="not found"):
                load_upstream_registry(tmpdir, "nonexistent.json", "needs")

    def test_load_upstream_registry_success(self):
        """Successfully load registry with correct top_key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {"needs": [{"id": "NEED-001"}, {"id": "NEED-002"}]}
            filepath = os.path.join(tmpdir, "needs_registry.json")
            with open(filepath, "w") as f:
                json.dump(data, f)

            result = load_upstream_registry(tmpdir, "needs_registry.json", "needs")
            assert len(result) == 2
            assert result[0]["id"] == "NEED-001"


# ---------------------------------------------------------------------------
# Test: Slot ID generation
# ---------------------------------------------------------------------------


class TestGenerateSlotId:
    """Tests for generate_slot_id and generate_trace_id."""

    def test_generate_slot_id(self):
        """Verify naming convention for each ingestion type."""
        assert generate_slot_id("need", "NEED-001") == "need:NEED-001"
        assert generate_slot_id("requirement", "REQ-026") == "requirement:REQ-026"
        assert generate_slot_id("source", "SRC-003") == "source:SRC-003"
        assert generate_slot_id("assumption", "A-001") == "assumption:A-001"
        assert generate_slot_id("traceability-link", "TRACE-001") == "trace:TRACE-001"

    def test_generate_slot_id_original_types(self):
        """Original Phase 1 types still work."""
        assert generate_slot_id("component", "MY-COMP") == "comp:MY-COMP"
        assert generate_slot_id("interface", "MY-INTF") == "intf:MY-INTF"

    def test_generate_slot_id_unknown_type(self):
        """Unknown slot type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown slot type"):
            generate_slot_id("nonexistent", "ID-001")

    def test_generate_trace_id(self):
        """Traceability link IDs derived from from_id and to_id."""
        result = generate_trace_id("REQ-001", "NEED-003")
        assert result == "trace:REQ-001->NEED-003"
