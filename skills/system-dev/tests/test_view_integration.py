"""Integration tests for full view assembly pipeline.

Tests end-to-end: spec -> snapshot -> match -> organize -> validate -> output.
Verifies gap indicators for missing slot types and slot preservation (VIEW-10).
"""

import json
import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.schema_validator import SchemaValidator
from scripts.view_assembler import (
    assemble_view,
    capture_snapshot,
)

SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


@pytest.fixture
def workspace(tmp_path):
    """Create a fresh .system-dev/ workspace in a temp directory."""
    init_workspace(str(tmp_path))
    return str(tmp_path / ".system-dev")


@pytest.fixture
def api(workspace):
    """Create a SlotAPI instance with the temp workspace."""
    return SlotAPI(workspace, SCHEMAS_DIR)


@pytest.fixture
def populated_workspace(api):
    """Create components, interfaces, and contracts via SlotAPI.

    Returns dict with api and created slot IDs for reference.
    """
    # Create components
    comp1 = api.create("component", {"name": "Auth Service"})
    comp2 = api.create("component", {"name": "Database Service"})

    comp1_id = comp1["slot_id"]
    comp2_id = comp2["slot_id"]

    # Create interfaces referencing components
    intf1 = api.create("interface", {
        "name": "Auth API",
        "source_component": comp1_id,
        "target_component": comp2_id,
    })
    intf2 = api.create("interface", {
        "name": "DB Connection",
        "source_component": comp2_id,
        "target_component": comp1_id,
    })

    intf1_id = intf1["slot_id"]

    # Create contract referencing interface
    cntr1 = api.create("contract", {
        "name": "Auth API Contract",
        "interface_id": intf1_id,
        "component_id": comp1_id,
    })

    return {
        "api": api,
        "comp1_id": comp1_id,
        "comp2_id": comp2_id,
        "intf1_id": intf1_id,
        "intf2_id": intf2["slot_id"],
        "cntr1_id": cntr1["slot_id"],
    }


class TestAssembleViewIntegration:
    """End-to-end integration tests for assemble_view()."""

    def test_assemble_with_matching_components(self, populated_workspace, workspace):
        """Assemble a view with matching components returns them in sections."""
        api = populated_workspace["api"]
        spec = {
            "name": "test-components",
            "description": "All components",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        assert result["spec_name"] == "test-components"
        assert result["total_slots"] == 2
        assert result["total_gaps"] == 0

    def test_assemble_with_gaps(self, api, workspace):
        """Assemble a view with no matching slots produces gap indicators."""
        spec = {
            "name": "test-gaps",
            "description": "Looking for nonexistent slots",
            "scope_patterns": [
                {"pattern": "component:NonExistent*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        assert result["total_slots"] == 0
        assert result["total_gaps"] == 1
        assert len(result["gaps"]) == 1
        assert result["gaps"][0]["slot_type"] == "component"

    def test_assemble_mixed_matches_and_gaps(self, populated_workspace, workspace):
        """Assemble a view with both matches and gaps returns both."""
        api = populated_workspace["api"]
        spec = {
            "name": "test-mixed",
            "description": "Mix of existing and missing",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "requirement-ref:*", "slot_type": "requirement-ref"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        assert result["total_slots"] > 0
        assert result["total_gaps"] > 0
        assert len(result["sections"]) > 0
        assert len(result["gaps"]) > 0

    def test_output_validates_against_schema(self, populated_workspace, workspace):
        """Assembled view output validates against view.json schema (VIEW-06)."""
        api = populated_workspace["api"]
        spec = {
            "name": "test-validation",
            "description": "Schema validation test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        # Validate against view.json schema
        validator = SchemaValidator(SCHEMAS_DIR)
        errors = validator.validate("view", result)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_snapshot_consistency(self, populated_workspace, workspace):
        """Assembly uses a single snapshot (same snapshot_id)."""
        api = populated_workspace["api"]
        spec = {
            "name": "test-snapshot",
            "description": "Snapshot consistency",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        assert "snapshot_id" in result
        assert len(result["snapshot_id"]) > 0

    def test_slot_preservation(self, populated_workspace, workspace):
        """Assembly does NOT modify or delete existing slots (VIEW-10).

        Slot counts before and after assembly must be identical.
        """
        api = populated_workspace["api"]

        # Count slots before assembly
        before_components = len(api.query("component"))
        before_interfaces = len(api.query("interface"))
        before_contracts = len(api.query("contract"))

        spec = {
            "name": "test-preservation",
            "description": "Preservation test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
                {"pattern": "contract:*", "slot_type": "contract"},
            ],
        }
        assemble_view(api, spec, workspace, SCHEMAS_DIR)

        # Count slots after assembly
        after_components = len(api.query("component"))
        after_interfaces = len(api.query("interface"))
        after_contracts = len(api.query("contract"))

        assert before_components == after_components
        assert before_interfaces == after_interfaces
        assert before_contracts == after_contracts

    def test_gap_indicators_for_empty_workspace(self, api, workspace):
        """An empty workspace produces gap indicators for all requested types."""
        spec = {
            "name": "test-empty",
            "description": "Empty workspace",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
                {"pattern": "contract:*", "slot_type": "contract"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        assert result["total_slots"] == 0
        assert result["total_gaps"] == 3
        gap_types = {g["slot_type"] for g in result["gaps"]}
        assert gap_types == {"component", "interface", "contract"}

    def test_hierarchical_organization(self, populated_workspace, workspace):
        """Components, interfaces, and contracts are organized hierarchically."""
        api = populated_workspace["api"]
        spec = {
            "name": "test-hierarchy",
            "description": "Hierarchy test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
                {"pattern": "contract:*", "slot_type": "contract"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)

        # Sections should exist and contain slots
        assert len(result["sections"]) > 0
        total_in_sections = sum(len(s["slots"]) for s in result["sections"])
        assert total_in_sections == result["total_slots"]
