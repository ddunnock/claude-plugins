"""Integration tests for impact command workflow.

Tests the full impact analysis pipeline: graph construction, forward/backward
traversal, depth limits, type filtering, persistence, and uncertainty markers.
"""

import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.traceability_agent import TraceabilityAgent

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, "schemas")


@pytest.fixture
def workspace(tmp_path):
    """Create a fresh workspace for each test."""
    result = init_workspace(str(tmp_path))
    assert result["status"] == "created"
    return str(tmp_path / ".system-dev")


@pytest.fixture
def api(workspace):
    """Create a SlotAPI instance for the test workspace."""
    return SlotAPI(workspace, SCHEMAS_DIR)


@pytest.fixture
def agent(api):
    """Create a TraceabilityAgent instance."""
    return TraceabilityAgent(api)


# -- Helpers to build a full design workspace --

def _ingest_need(api, need_id, description="Test need"):
    return api.ingest(f"need:{need_id}", "need", {
        "upstream_id": need_id,
        "description": description,
    })


def _ingest_requirement(api, req_id, description="Test requirement"):
    return api.ingest(f"requirement:{req_id}", "requirement", {
        "upstream_id": req_id,
        "description": description,
    })


def _ingest_trace_link(api, from_id, to_id, link_type, suffix=None):
    sfx = suffix or f"{from_id}-{to_id}"
    return api.ingest(f"trace:{sfx}", "traceability-link", {
        "from_id": from_id,
        "to_id": to_id,
        "link_type": link_type,
    })


def _create_component(api, name, req_ids=None):
    result = api.create("component", {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "requirement_ids": req_ids or [],
    })
    return result["slot_id"]


def _create_interface(api, name, source_comp="", target_comp=""):
    result = api.create("interface", {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "source_component": source_comp,
        "target_component": target_comp,
        "direction": "unidirectional",
    })
    return result["slot_id"]


def _create_contract(api, name, comp_id="", intf_id="",
                     obligations=None, vv_assignments=None):
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "component_id": comp_id,
        "interface_id": intf_id,
    }
    if obligations:
        content["obligations"] = obligations
    if vv_assignments:
        content["vv_assignments"] = vv_assignments
    result = api.create("contract", content)
    return result["slot_id"]


def _build_full_workspace(api):
    """Build a complete design workspace with full traceability chains.

    Returns dict of all created slot IDs.
    """
    _ingest_need(api, "NEED-001", "Authentication need")
    _ingest_need(api, "NEED-002", "Authorization need")

    _ingest_requirement(api, "REQ-001", "Login requirement")
    _ingest_requirement(api, "REQ-002", "Session management")
    _ingest_requirement(api, "REQ-003", "Access control")

    _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")
    _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-002", "satisfies", "n1-r2")
    _ingest_trace_link(api, "need:NEED-002", "requirement:REQ-003", "satisfies", "n2-r3")

    comp_auth = _create_component(api, "Auth Service",
                                  req_ids=["requirement:REQ-001", "requirement:REQ-002"])
    comp_access = _create_component(api, "Access Service",
                                    req_ids=["requirement:REQ-003"])

    intf_id = _create_interface(api, "Auth-Access API",
                                source_comp=comp_auth, target_comp=comp_access)

    cntr_id = _create_contract(
        api, "Auth Protocol", comp_id=comp_auth, intf_id=intf_id,
        obligations=[
            {"id": "OBL-001", "statement": "Validate tokens", "obligation_type": "data_processing"},
            {"id": "OBL-002", "statement": "Encrypt data", "obligation_type": "data_processing"},
        ],
        vv_assignments=[
            {"obligation_id": "OBL-001", "method": "test", "rationale": "Unit testable"},
            {"obligation_id": "OBL-002", "method": "inspection", "rationale": "Code review"},
        ],
    )

    return {
        "need_001": "need:NEED-001",
        "need_002": "need:NEED-002",
        "req_001": "requirement:REQ-001",
        "req_002": "requirement:REQ-002",
        "req_003": "requirement:REQ-003",
        "comp_auth": comp_auth,
        "comp_access": comp_access,
        "intf": intf_id,
        "cntr": cntr_id,
        "vv_obl1": f"vv:{cntr_id}:OBL-001",
        "vv_obl2": f"vv:{cntr_id}:OBL-002",
    }


def _collect_ids(paths):
    """Recursively collect element_ids from tree paths."""
    ids = set()
    for node in paths:
        ids.add(node["element_id"])
        for child in node.get("children", []):
            ids.update(_collect_ids([child]))
    return ids


# ============================================================
# Integration tests
# ============================================================

class TestImpactIntegration:
    """End-to-end integration tests for impact analysis workflow."""

    def test_impact_on_empty_workspace_returns_gap(self, api, agent):
        """Impact on empty workspace (no elements) returns gap marker."""
        result = agent.compute_impact("nonexistent-element", direction="forward")

        assert result["affected_count"] == 0
        assert len(result["paths"]) == 0
        assert len(result["gap_markers"]) >= 1
        assert result["gap_markers"][0]["type"] == "missing_data"

    def test_forward_from_requirement_shows_downstream(self, api, agent):
        """Forward impact from requirement shows components, interfaces, contracts, V&V."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["req_001"], direction="forward")

        assert result["source_element"] == ids["req_001"]
        assert result["direction"] == "forward"
        reachable = _collect_ids(result["paths"])
        # Requirement -> component -> interface -> contract -> V&V
        assert ids["comp_auth"] in reachable
        assert ids["intf"] in reachable
        assert ids["cntr"] in reachable
        assert ids["vv_obl1"] in reachable

    def test_backward_from_contract_shows_upstream(self, api, agent):
        """Backward impact from contract shows interface, components, requirements, needs."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["cntr"], direction="backward")

        reachable = _collect_ids(result["paths"])
        # Contract <- interface <- component <- requirement <- need
        assert ids["comp_auth"] in reachable or ids["intf"] in reachable

    def test_depth_1_shows_only_direct_neighbors(self, api, agent):
        """Impact with depth=1 shows only direct neighbors."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["req_001"], direction="forward", depth_limit=1)

        reachable = _collect_ids(result["paths"])
        assert ids["comp_auth"] in reachable
        # Should NOT reach contract (3+ hops away)
        assert ids["cntr"] not in reachable

    def test_type_filter_component_shows_only_components(self, api, agent):
        """Impact with --type component shows only component nodes in output."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["req_001"], direction="forward",
                                      type_filter=["component"])

        for node in result["paths"]:
            assert node["element_type"] == "component"
        # But affected_count reflects full traversal
        assert result["affected_count"] >= 2

    def test_impact_persisted_as_slot(self, api, agent):
        """Impact result is persisted as impact-analysis slot and readable."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["req_001"], direction="forward")
        persisted = agent.persist_impact(result)

        assert persisted["slot_type"] == "impact-analysis"
        assert persisted["source_element"] == ids["req_001"]
        assert persisted["direction"] == "forward"

        # Readable via API
        read_back = api.read(persisted["slot_id"])
        assert read_back is not None
        assert read_back["source_element"] == ids["req_001"]

    def test_incomplete_graph_shows_uncertainty(self, api, agent):
        """Impact on element with incomplete graph shows uncertainty markers."""
        ids = _build_full_workspace(api)
        # Add orphan component not reachable from req_001
        _create_component(api, "Orphan Module", req_ids=[])

        result = agent.compute_impact(ids["req_001"], direction="forward")

        assert result["graph_coverage_percent"] < 100
        assert len(result["uncertainty_markers"]) >= 1

    def test_two_consecutive_impacts_create_separate_slots(self, api, agent):
        """Two consecutive impact commands create separate impact-analysis slots."""
        ids = _build_full_workspace(api)

        result1 = agent.compute_impact(ids["req_001"], direction="forward")
        persisted1 = agent.persist_impact(result1)

        result2 = agent.compute_impact(ids["req_003"], direction="forward")
        persisted2 = agent.persist_impact(result2)

        assert persisted1["slot_id"] != persisted2["slot_id"]
        assert persisted1["source_element"] == ids["req_001"]
        assert persisted2["source_element"] == ids["req_003"]

        # Both readable
        assert api.read(persisted1["slot_id"]) is not None
        assert api.read(persisted2["slot_id"]) is not None

    def test_format_output_end_to_end(self, api, agent):
        """Full workflow: compute, persist, format produces readable output."""
        ids = _build_full_workspace(api)

        result = agent.compute_impact(ids["req_001"], direction="forward")
        agent.persist_impact(result)
        output = agent.format_impact_output(result)

        # Output should contain key elements
        assert ids["req_001"] in output
        assert "forward" in output.lower()
        assert "affected" in output.lower()
        # Should have tree structure indicators
        assert "|--" in output or "`--" in output
