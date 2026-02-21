"""Tests for subsystem decomposition logic."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import decompose


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def decomposition_workspace(tmp_path):
    """Workspace with baselined requirements ready for decomposition."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()

    state = {
        "session_id": "decomp-test",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "deliver",
        "gates": {"init": True, "needs": True, "requirements": True, "deliver": True},
        "blocks": {
            "dependency-tracker": {
                "name": "dependency-tracker",
                "description": "Dependency tracking subsystem",
                "relationships": [],
                "level": 0,
            },
        },
        "progress": {
            "current_block": None,
            "current_type_pass": None,
            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
            "requirements_in_draft": [],
        },
        "counts": {
            "needs_total": 1, "needs_approved": 1, "needs_deferred": 0,
            "requirements_total": 3, "requirements_registered": 0,
            "requirements_baselined": 3, "requirements_withdrawn": 0,
            "tbd_open": 0, "tbr_open": 0,
        },
        "traceability": {"links_total": 0, "coverage_pct": 0.0},
        "decomposition": {"levels": {}, "max_level": 3},
        "artifacts": {},
    }
    (ws / "state.json").write_text(json.dumps(state, indent=2))

    reqs = {
        "schema_version": "1.0.0",
        "requirements": [
            {"id": "REQ-001", "statement": "The system shall track dependency graphs", "type": "functional", "priority": "high", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
            {"id": "REQ-002", "statement": "The system shall detect circular dependencies", "type": "functional", "priority": "high", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
            {"id": "REQ-003", "statement": "The system shall compute critical path", "type": "functional", "priority": "medium", "status": "baselined", "source_block": "dependency-tracker", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01", "baselined_at": "2025-01-02"},
        ],
    }
    (ws / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))

    trace = {"schema_version": "1.0.0", "links": []}
    (ws / "traceability_registry.json").write_text(json.dumps(trace, indent=2))

    needs = {"schema_version": "1.0.0", "needs": [
        {"id": "NEED-001", "statement": "Track dependencies", "stakeholder": "Dev", "status": "approved"},
    ]}
    (ws / "needs_registry.json").write_text(json.dumps(needs, indent=2))

    return ws


# ---------------------------------------------------------------------------
# Baseline validation tests
# ---------------------------------------------------------------------------

class TestValidateBaseline:
    def test_baselined_block_passes(self, decomposition_workspace):
        """Block with all baselined requirements passes validation."""
        ws = str(decomposition_workspace)
        assert decompose.validate_baseline(ws, "dependency-tracker") is True

    def test_non_baselined_block_fails(self, decomposition_workspace):
        """Block with registered (not baselined) requirements fails."""
        ws = str(decomposition_workspace)
        reqs = json.loads((decomposition_workspace / "requirements_registry.json").read_text())
        reqs["requirements"][0]["status"] = "registered"
        (decomposition_workspace / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))
        assert decompose.validate_baseline(ws, "dependency-tracker") is False


# ---------------------------------------------------------------------------
# Allocation tests
# ---------------------------------------------------------------------------

class TestAllocation:
    def test_allocate_creates_traces(self, decomposition_workspace):
        """Allocation creates allocated_to links in traceability registry."""
        ws = str(decomposition_workspace)
        # Register sub-blocks first
        decompose.register_sub_blocks(ws, "dependency-tracker", [
            {"name": "graph-engine", "description": "Graph processing"},
            {"name": "cycle-detector", "description": "Cycle detection"},
        ], level=1)

        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph traversal core")
        decompose.allocate_requirement(ws, "REQ-002", "cycle-detector", "Cycle detection core")

        trace = json.loads((decomposition_workspace / "traceability_registry.json").read_text())
        alloc_links = [l for l in trace["links"] if l["type"] == "allocated_to"]
        assert len(alloc_links) == 2
        targets = {l["target"] for l in alloc_links}
        assert "graph-engine" in targets
        assert "cycle-detector" in targets

    def test_allocation_coverage_incomplete(self, decomposition_workspace):
        """Coverage validation flags unallocated requirements."""
        ws = str(decomposition_workspace)
        decompose.register_sub_blocks(ws, "dependency-tracker", [
            {"name": "graph-engine", "description": "Graph processing"},
        ], level=1)
        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph core")
        # REQ-002 and REQ-003 not allocated

        result = decompose.validate_allocation_coverage(ws, "dependency-tracker")
        assert result["coverage"] < 1.0
        assert "REQ-002" in result["unallocated"]
        assert "REQ-003" in result["unallocated"]

    def test_allocation_coverage_complete(self, decomposition_workspace):
        """Coverage validation passes when all requirements allocated."""
        ws = str(decomposition_workspace)
        decompose.register_sub_blocks(ws, "dependency-tracker", [
            {"name": "graph-engine", "description": "Graph processing"},
            {"name": "cycle-detector", "description": "Cycle detection"},
        ], level=1)
        decompose.allocate_requirement(ws, "REQ-001", "graph-engine", "Graph core")
        decompose.allocate_requirement(ws, "REQ-002", "cycle-detector", "Cycle detection")
        decompose.allocate_requirement(ws, "REQ-003", "graph-engine", "Critical path uses graph")

        result = decompose.validate_allocation_coverage(ws, "dependency-tracker")
        assert result["coverage"] == pytest.approx(1.0)
        assert result["unallocated"] == []


# ---------------------------------------------------------------------------
# Sub-block registration tests
# ---------------------------------------------------------------------------

class TestSubBlockRegistration:
    def test_sub_blocks_registered_with_level(self, decomposition_workspace):
        """Sub-blocks are registered in state.json with correct level."""
        ws = str(decomposition_workspace)
        decompose.register_sub_blocks(ws, "dependency-tracker", [
            {"name": "graph-engine", "description": "Graph processing"},
            {"name": "cycle-detector", "description": "Cycle detection"},
            {"name": "critical-path-calc", "description": "Critical path"},
        ], level=1)

        state = json.loads((decomposition_workspace / "state.json").read_text())
        assert "graph-engine" in state["blocks"]
        assert state["blocks"]["graph-engine"]["level"] == 1
        assert "cycle-detector" in state["blocks"]
        assert "critical-path-calc" in state["blocks"]


# ---------------------------------------------------------------------------
# Max level tests
# ---------------------------------------------------------------------------

class TestMaxLevel:
    def test_max_level_prevents_deep_decomposition(self, decomposition_workspace):
        """Decomposition beyond max_level=3 is blocked."""
        ws = str(decomposition_workspace)
        assert decompose.check_max_level(ws, 3) is False

    def test_within_max_level_allowed(self, decomposition_workspace):
        """Decomposition within max_level is allowed."""
        ws = str(decomposition_workspace)
        assert decompose.check_max_level(ws, 0) is True
        assert decompose.check_max_level(ws, 2) is True


# ---------------------------------------------------------------------------
# Decomposition state tests
# ---------------------------------------------------------------------------

class TestDecompositionState:
    def test_state_tracks_decomposition(self, decomposition_workspace):
        """Decomposition state tracks parent_block and sub_blocks."""
        ws = str(decomposition_workspace)
        decompose.register_sub_blocks(ws, "dependency-tracker", [
            {"name": "graph-engine", "description": "Graph processing"},
            {"name": "cycle-detector", "description": "Cycle detection"},
            {"name": "critical-path-calc", "description": "Critical path"},
        ], level=1)
        decompose.update_decomposition_state(ws, 1, "dependency-tracker",
            ["graph-engine", "cycle-detector", "critical-path-calc"], 1.0)

        state = json.loads((decomposition_workspace / "state.json").read_text())
        level_1 = state["decomposition"]["levels"]["1"]
        assert level_1["parent_block"] == "dependency-tracker"
        assert level_1["sub_blocks"] == ["graph-engine", "cycle-detector", "critical-path-calc"]
        assert level_1["allocation_coverage"] == pytest.approx(1.0)
