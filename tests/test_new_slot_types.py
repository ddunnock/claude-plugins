"""Tests for traceability-graph and impact-analysis slot type registration."""

import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import SLOT_ID_PREFIXES, SLOT_TYPE_DIRS, SlotAPI
from scripts.schema_validator import SchemaValidationError

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


class TestTraceabilityGraphSlotType:
    def test_create_traceability_graph_succeeds(self, api):
        """Create a traceability-graph slot with valid content."""
        result = api.create(
            "traceability-graph",
            {
                "nodes": {},
                "edges": [],
                "completeness": {
                    "total_chains": 0,
                    "complete_chains": 0,
                    "percentage": 0.0,
                    "broken_chains": 0,
                    "orphan_count": 0,
                },
                "chain_report": {"chains": [], "gaps": [], "divergences": []},
            },
        )
        assert result["status"] == "created"
        assert result["slot_id"].startswith("tgraph-")
        assert result["version"] == 1

    def test_traceability_graph_registered_in_dirs(self):
        """Verify traceability-graph is in SLOT_TYPE_DIRS."""
        assert "traceability-graph" in SLOT_TYPE_DIRS
        assert SLOT_TYPE_DIRS["traceability-graph"] == "traceability-graphs"

    def test_traceability_graph_registered_in_prefixes(self):
        """Verify traceability-graph has correct prefix."""
        assert "traceability-graph" in SLOT_ID_PREFIXES
        assert SLOT_ID_PREFIXES["traceability-graph"] == "tgraph"

    def test_traceability_graph_read_back(self, api):
        """Create and read back a traceability-graph slot."""
        result = api.create(
            "traceability-graph",
            {
                "nodes": {"need:NEED-001": {"type": "need", "name": "Test Need"}},
                "edges": [
                    {
                        "from_id": "need:NEED-001",
                        "to_id": "requirement:REQ-042",
                        "edge_type": "derives_from",
                        "source": "traceability-link",
                    }
                ],
            },
        )
        slot = api.read(result["slot_id"])
        assert slot is not None
        assert slot["slot_type"] == "traceability-graph"
        assert len(slot["edges"]) == 1


class TestImpactAnalysisSlotType:
    def test_create_impact_analysis_succeeds(self, api):
        """Create an impact-analysis slot with valid content."""
        result = api.create(
            "impact-analysis",
            {
                "source_element": "comp-abc123",
                "direction": "forward",
                "depth_limit": None,
                "type_filter": None,
                "paths": [],
                "affected_count": 0,
                "uncertainty_markers": [],
                "graph_coverage_percent": 100.0,
            },
        )
        assert result["status"] == "created"
        assert result["slot_id"].startswith("impact-")
        assert result["version"] == 1

    def test_impact_analysis_registered_in_dirs(self):
        """Verify impact-analysis is in SLOT_TYPE_DIRS."""
        assert "impact-analysis" in SLOT_TYPE_DIRS
        assert SLOT_TYPE_DIRS["impact-analysis"] == "impact-analyses"

    def test_impact_analysis_registered_in_prefixes(self):
        """Verify impact-analysis has correct prefix."""
        assert "impact-analysis" in SLOT_ID_PREFIXES
        assert SLOT_ID_PREFIXES["impact-analysis"] == "impact"

    def test_impact_analysis_rejects_invalid_direction(self, api):
        """Schema validation rejects invalid direction enum value."""
        with pytest.raises(SchemaValidationError) as exc_info:
            api.create(
                "impact-analysis",
                {
                    "source_element": "comp-abc123",
                    "direction": "sideways",
                    "paths": [],
                    "affected_count": 0,
                },
            )
        assert any(
            "direction" in str(e.get("path", "")) or "sideways" in str(e.get("message", ""))
            for e in exc_info.value.errors
        )

    def test_impact_analysis_read_back(self, api):
        """Create and read back an impact-analysis slot."""
        result = api.create(
            "impact-analysis",
            {
                "source_element": "comp-abc123",
                "direction": "both",
                "paths": [
                    {
                        "element_id": "intf-xyz",
                        "element_type": "interface",
                        "element_name": "Auth API",
                        "depth": 1,
                        "relationship": "communicates_with",
                    }
                ],
                "affected_count": 1,
                "graph_coverage_percent": 85.5,
            },
        )
        slot = api.read(result["slot_id"])
        assert slot is not None
        assert slot["direction"] == "both"
        assert slot["affected_count"] == 1


class TestExistingTypesUnaffected:
    def test_component_still_works(self, api):
        """Existing component type still creates and validates correctly."""
        result = api.create("component", {"name": "Test Component"})
        assert result["status"] == "created"
        assert result["slot_id"].startswith("comp-")

    def test_interface_still_works(self, api):
        """Existing interface type still creates correctly."""
        result = api.create("interface", {"name": "Test Interface"})
        assert result["status"] == "created"
        assert result["slot_id"].startswith("intf-")

    def test_contract_still_works(self, api):
        """Existing contract type still creates correctly."""
        result = api.create("contract", {"name": "Test Contract"})
        assert result["status"] == "created"
        assert result["slot_id"].startswith("cntr-")
