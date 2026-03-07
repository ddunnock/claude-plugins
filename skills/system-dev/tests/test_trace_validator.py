"""Tests for trace_validator.py -- write-time trace enforcement."""

import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.trace_validator import TraceValidator

SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


@pytest.fixture
def workspace(tmp_path):
    """Create a fresh .system-dev/ workspace in a temp directory."""
    init_workspace(str(tmp_path))
    return str(tmp_path / ".system-dev")


@pytest.fixture
def api(workspace):
    """SlotAPI WITHOUT trace_validator (backward compat)."""
    return SlotAPI(workspace, SCHEMAS_DIR)


@pytest.fixture
def trace_api(workspace):
    """SlotAPI WITH trace_validator enabled."""
    return SlotAPI(workspace, SCHEMAS_DIR, trace_validator=TraceValidator())


@pytest.fixture
def validator():
    """Standalone TraceValidator instance."""
    return TraceValidator()


# ---------------------------------------------------------------------------
# TraceValidator.validate() unit tests
# ---------------------------------------------------------------------------


class TestTraceValidatorUnit:
    def test_component_missing_requirement_ids(self, validator, api):
        """Component without requirement_ids returns missing_trace_field warning."""
        content = {"name": "Auth Service"}
        warnings = validator.validate("component", content, api)
        assert len(warnings) >= 1
        field_warning = next(
            w for w in warnings if w["type"] == "missing_trace_field" and w["field"] == "requirement_ids"
        )
        assert field_warning is not None

    def test_interface_missing_source_component(self, validator, api):
        """Interface without source_component returns warning."""
        content = {"name": "Auth API"}
        warnings = validator.validate("interface", content, api)
        field_names = [w["field"] for w in warnings if w["type"] == "missing_trace_field"]
        assert "source_component" in field_names

    def test_interface_missing_target_component(self, validator, api):
        """Interface without target_component returns warning."""
        content = {"name": "Auth API"}
        warnings = validator.validate("interface", content, api)
        field_names = [w["field"] for w in warnings if w["type"] == "missing_trace_field"]
        assert "target_component" in field_names

    def test_contract_missing_fields(self, validator, api):
        """Contract without component_id, interface_id, requirement_ids returns warnings."""
        content = {"name": "Auth Contract"}
        warnings = validator.validate("contract", content, api)
        field_names = [w["field"] for w in warnings if w["type"] == "missing_trace_field"]
        assert "component_id" in field_names
        assert "interface_id" in field_names
        assert "requirement_ids" in field_names

    def test_contract_with_valid_refs_no_warnings(self, validator, api):
        """Contract with all valid references returns empty list."""
        # Create referenced slots first
        comp_result = api.create("component", {"name": "Auth Service"})
        intf_result = api.create("interface", {"name": "Auth API"})
        req_result = api.create("requirement-ref", {"name": "REQ-042", "upstream_id": "REQ-042"})

        content = {
            "name": "Auth Contract",
            "component_id": comp_result["slot_id"],
            "interface_id": intf_result["slot_id"],
            "requirement_ids": [req_result["slot_id"]],
        }
        warnings = validator.validate("contract", content, api)
        assert warnings == []

    def test_need_is_exempt(self, validator, api):
        """Need type returns empty list (upstream type exempt)."""
        warnings = validator.validate("need", {"name": "Stakeholder Need"}, api)
        assert warnings == []

    def test_requirement_is_exempt(self, validator, api):
        """Requirement type returns empty list (upstream type exempt)."""
        warnings = validator.validate("requirement", {"name": "REQ-042"}, api)
        assert warnings == []

    def test_source_is_exempt(self, validator, api):
        """Source type returns empty list."""
        warnings = validator.validate("source", {}, api)
        assert warnings == []

    def test_assumption_is_exempt(self, validator, api):
        """Assumption type returns empty list."""
        warnings = validator.validate("assumption", {}, api)
        assert warnings == []

    def test_traceability_link_is_exempt(self, validator, api):
        """Traceability-link type returns empty list."""
        warnings = validator.validate("traceability-link", {}, api)
        assert warnings == []

    def test_broken_reference_warning(self, validator, api):
        """Component with nonexistent requirement_ids returns broken_reference warning."""
        content = {"name": "Auth Service", "requirement_ids": ["nonexistent-id-1234"]}
        warnings = validator.validate("component", content, api)
        broken = [w for w in warnings if w["type"] == "broken_reference"]
        assert len(broken) >= 1
        assert broken[0]["ref_id"] == "nonexistent-id-1234"

    def test_empty_requirement_ids_is_missing(self, validator, api):
        """Empty requirement_ids list counts as missing."""
        content = {"name": "Auth Service", "requirement_ids": []}
        warnings = validator.validate("component", content, api)
        missing = [w for w in warnings if w["type"] == "missing_trace_field" and w["field"] == "requirement_ids"]
        assert len(missing) == 1

    def test_interface_broken_source_component(self, validator, api):
        """Interface with nonexistent source_component returns broken_reference."""
        content = {
            "name": "Auth API",
            "source_component": "comp-nonexistent",
            "target_component": "comp-also-nonexistent",
            "requirement_ids": ["req-nope"],
        }
        warnings = validator.validate("interface", content, api)
        broken = [w for w in warnings if w["type"] == "broken_reference"]
        broken_fields = [w["field"] for w in broken]
        assert "source_component" in broken_fields
        assert "target_component" in broken_fields


# ---------------------------------------------------------------------------
# SlotAPI integration tests
# ---------------------------------------------------------------------------


class TestSlotAPITraceIntegration:
    def test_create_component_without_trace_fields_adds_gap_markers(self, trace_api):
        """SlotAPI.create with trace_validator adds gap_markers for missing trace fields."""
        result = trace_api.create("component", {"name": "Auth Service"})
        slot = trace_api.read(result["slot_id"])
        assert slot is not None
        gap_markers = slot.get("gap_markers", [])
        assert len(gap_markers) >= 1
        types = [gm["type"] for gm in gap_markers]
        assert "missing_trace_field" in types

    def test_create_component_with_trace_fields_no_gap_markers(self, trace_api):
        """Component with valid requirement_ids gets no trace gap markers."""
        # Create a requirement-ref to reference
        req_result = trace_api.create("requirement-ref", {"name": "REQ-042", "upstream_id": "REQ-042"})
        result = trace_api.create(
            "component",
            {"name": "Auth Service", "requirement_ids": [req_result["slot_id"]]},
        )
        slot = trace_api.read(result["slot_id"])
        gap_markers = slot.get("gap_markers", [])
        # No trace-related gap markers (may have none at all)
        trace_markers = [gm for gm in gap_markers if gm["type"] in ("missing_trace_field", "broken_reference")]
        assert trace_markers == []

    def test_update_triggers_trace_validation(self, trace_api):
        """SlotAPI.update also triggers trace validation and adds gap_markers."""
        result = trace_api.create("component", {"name": "Auth Service"})
        # Update without requirement_ids
        update_result = trace_api.update(
            result["slot_id"],
            {"name": "Auth Service v2"},
            expected_version=1,
        )
        assert update_result["status"] == "updated"
        slot = trace_api.read(result["slot_id"])
        gap_markers = slot.get("gap_markers", [])
        assert any(gm["type"] == "missing_trace_field" for gm in gap_markers)

    def test_need_ingest_no_gap_markers(self, trace_api):
        """Ingesting a need with trace_validator enabled adds no trace gap markers."""
        result = trace_api.ingest(
            "need:NEED-001",
            "need",
            {"description": "Stakeholder Need", "upstream_id": "NEED-001"},
        )
        slot = trace_api.read(result["slot_id"])
        gap_markers = slot.get("gap_markers", [])
        trace_markers = [gm for gm in gap_markers if gm["type"] in ("missing_trace_field", "broken_reference")]
        assert trace_markers == []

    def test_without_trace_validator_no_gap_markers(self, api):
        """SlotAPI without trace_validator (default) adds no gap markers."""
        result = api.create("component", {"name": "Auth Service"})
        slot = api.read(result["slot_id"])
        gap_markers = slot.get("gap_markers", [])
        assert gap_markers == [] or all(
            gm["type"] not in ("missing_trace_field", "broken_reference") for gm in gap_markers
        )

    def test_gap_markers_have_correct_structure(self, trace_api):
        """Gap markers from trace validation have required fields."""
        result = trace_api.create("component", {"name": "Auth Service"})
        slot = trace_api.read(result["slot_id"])
        gap_markers = slot.get("gap_markers", [])
        for gm in gap_markers:
            assert "type" in gm
            assert "finding_ref" in gm
            assert "severity" in gm
            assert "description" in gm

    def test_create_succeeds_even_with_trace_warnings(self, trace_api):
        """Trace warnings never block slot creation (warn-but-allow)."""
        result = trace_api.create("component", {"name": "No Traces At All"})
        assert result["status"] == "created"
        assert result["version"] == 1
        # Slot is persisted despite trace warnings
        slot = trace_api.read(result["slot_id"])
        assert slot is not None


class TestBackwardCompatibility:
    def test_existing_api_pattern_unchanged(self, api):
        """SlotAPI without trace_validator works exactly as before."""
        # Component
        result = api.create("component", {"name": "Test"})
        assert result["status"] == "created"
        # Interface
        result = api.create("interface", {"name": "Test API"})
        assert result["status"] == "created"
        # Contract
        result = api.create("contract", {"name": "Test Contract"})
        assert result["status"] == "created"
