"""Integration tests for the trace workflow -- end-to-end graph building and chain validation."""

import os
import time

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.traceability_agent import TraceabilityAgent

# Paths relative to project root
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


# -- Helpers --

def _ingest_need(api, need_id, description="Test need"):
    return api.ingest(f"need:{need_id}", "need", {
        "upstream_id": need_id, "description": description,
    })


def _ingest_requirement(api, req_id, description="Test req", parent_need=None):
    content = {"upstream_id": req_id, "description": description}
    if parent_need:
        content["parent_need"] = parent_need
    return api.ingest(f"requirement:{req_id}", "requirement", content)


def _ingest_trace_link(api, from_id, to_id, link_type, suffix=None):
    suffix = suffix or f"{from_id}-{to_id}".replace(":", "_")
    return api.ingest(f"trace:{suffix}", "traceability-link", {
        "from_id": from_id, "to_id": to_id, "link_type": link_type,
    })


def _create_component(api, name, req_ids=None):
    result = api.create("component", {
        "name": name, "description": f"{name} desc",
        "status": "approved", "requirement_ids": req_ids or [],
    })
    return result["slot_id"]


def _create_interface(api, name, source_comp, target_comp, req_ids=None):
    content = {
        "name": name, "description": f"{name} desc",
        "status": "approved",
        "source_component": source_comp,
        "target_component": target_comp,
        "direction": "unidirectional",
    }
    if req_ids:
        content["requirement_ids"] = req_ids
    result = api.create("interface", content)
    return result["slot_id"]


def _create_contract(api, name, comp_id, intf_id, obligations=None, vv_assignments=None):
    content = {
        "name": name, "description": f"{name} desc",
        "status": "approved",
        "component_id": comp_id, "interface_id": intf_id,
    }
    if obligations:
        content["obligations"] = obligations
    if vv_assignments:
        content["vv_assignments"] = vv_assignments
    result = api.create("contract", content)
    return result["slot_id"]


def _build_complete_design(api):
    """Build a complete design graph: 2 needs, 2 reqs, 2 comps, 1 intf, 1 contract with V&V."""
    _ingest_need(api, "NEED-001", "User authentication")
    _ingest_need(api, "NEED-002", "Data storage")
    _ingest_requirement(api, "REQ-001", "Authenticate users", parent_need="need:NEED-001")
    _ingest_requirement(api, "REQ-002", "Store data securely", parent_need="need:NEED-002")

    _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")
    _ingest_trace_link(api, "need:NEED-002", "requirement:REQ-002", "satisfies", "n2-r2")

    comp_a = _create_component(api, "Auth Service", req_ids=["requirement:REQ-001"])
    comp_b = _create_component(api, "Storage Service", req_ids=["requirement:REQ-002"])

    intf_ab = _create_interface(api, "Auth-Storage API", comp_a, comp_b)

    cntr_a = _create_contract(
        api, "Auth Contract", comp_id=comp_a, intf_id=intf_ab,
        obligations=[{"id": "OBL-001", "statement": "Validate tokens", "obligation_type": "data_processing"}],
        vv_assignments=[{"obligation_id": "OBL-001", "method": "test", "rationale": "Unit testable"}],
    )
    cntr_b = _create_contract(
        api, "Storage Contract", comp_id=comp_b, intf_id=intf_ab,
        obligations=[{"id": "OBL-002", "statement": "Encrypt at rest", "obligation_type": "state_management"}],
        vv_assignments=[{"obligation_id": "OBL-002", "method": "inspection", "rationale": "Config review"}],
    )

    return {
        "comp_a": comp_a, "comp_b": comp_b, "intf_ab": intf_ab,
        "cntr_a": cntr_a, "cntr_b": cntr_b,
    }


# ============================================================
# Integration Tests
# ============================================================

class TestTraceWorkflowIntegration:
    """End-to-end integration tests for the trace workflow."""

    def test_empty_workspace_returns_empty_graph(self, api, agent):
        """Trace on empty workspace produces a graph with no chains."""
        graph = agent.build_or_refresh()
        output = agent.format_trace_output(graph)
        assert "0%" in output or "0/0" in output

    def test_complete_graph_shows_100_percent(self, api, agent):
        """Complete design graph shows 100% completeness."""
        _build_complete_design(api)

        graph = agent.build_or_refresh()
        output = agent.format_trace_output(graph)

        assert "100%" in output
        assert graph["completeness"]["percentage"] == 100.0
        assert graph["completeness"]["complete_chains"] == 2
        assert graph["completeness"]["broken_chains"] == 0

    def test_partial_graph_shows_gaps(self, api, agent):
        """Partial graph (needs + reqs only) shows 0% with critical gaps."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")

        graph = agent.build_or_refresh()

        assert graph["completeness"]["percentage"] == 0.0
        assert graph["completeness"]["broken_chains"] == 1

        gaps = graph["chain_report"]["gaps"]
        critical_gaps = [g for g in gaps if g["severity"] == "critical"]
        assert len(critical_gaps) >= 1
        assert any("component" in g.get("break_at_type", "") for g in critical_gaps)

    def test_adding_component_increases_completeness(self, api, agent):
        """Adding a component to partial graph shows progress (chain extends further)."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")

        graph1 = agent.build_or_refresh()
        gaps1 = graph1["chain_report"]["gaps"]
        break_level_1 = gaps1[0]["break_at_level"] if gaps1 else 0

        # Add component linked to requirement
        time.sleep(0.05)
        comp_id = _create_component(api, "Auth Service", req_ids=["requirement:REQ-001"])

        graph2 = agent.build_or_refresh()
        gaps2 = graph2["chain_report"]["gaps"]

        # Chain should now reach further (break at interface level, not component)
        if gaps2:
            break_level_2 = gaps2[0]["break_at_level"]
            assert break_level_2 > break_level_1

    def test_staleness_detection_end_to_end(self, api, agent):
        """Build graph, add new component, next trace call auto-rebuilds."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")

        graph1 = agent.build_or_refresh()
        built_at_1 = graph1["built_at"]
        node_count_1 = len(graph1["nodes"])

        time.sleep(0.05)
        _create_component(api, "New Service")

        graph2 = agent.build_or_refresh()
        assert graph2["built_at"] > built_at_1
        assert len(graph2["nodes"]) > node_count_1

    def test_divergence_reported_in_separate_section(self, api, agent):
        """Divergence between traceability-link and embedded field is reported separately."""
        _ingest_requirement(api, "REQ-001")
        comp_id = _create_component(api, "Auth", req_ids=["requirement:REQ-001"])

        # Create a trace link with a DIFFERENT edge type for the same pair
        _ingest_trace_link(api, "requirement:REQ-001", comp_id, "derives_from", "divergent")

        graph = agent.build_or_refresh()
        output = agent.format_trace_output(graph)

        divergences = graph["chain_report"]["divergences"]
        assert len(divergences) >= 1
        assert "Divergence" in output

    def test_orphan_component_reported_as_info(self, api, agent):
        """Orphan component not connected to any requirement is reported as info."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies", "n1-r1")

        # Orphan -- no requirement_ids
        _create_component(api, "Orphan Service", req_ids=[])

        graph = agent.build_or_refresh()
        output = agent.format_trace_output(graph)

        orphan_gaps = [g for g in graph["chain_report"]["gaps"]
                       if g.get("type") == "orphan" and g["severity"] == "info"]
        assert len(orphan_gaps) >= 1
        assert "Orphan" in output
