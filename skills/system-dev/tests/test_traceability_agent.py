"""Tests for traceability_agent.py -- graph construction, chain validation, staleness."""

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


# -- Helper functions to create test slots --

def _ingest_need(api, need_id, description="Test need"):
    """Ingest a need slot with deterministic ID."""
    return api.ingest(
        f"need:{need_id}",
        "need",
        {
            "upstream_id": need_id,
            "description": description,
        },
    )


def _ingest_requirement(api, req_id, description="Test requirement", parent_need=None):
    """Ingest a requirement slot with deterministic ID."""
    content = {
        "upstream_id": req_id,
        "description": description,
    }
    if parent_need:
        content["parent_need"] = parent_need
    return api.ingest(
        f"requirement:{req_id}",
        "requirement",
        content,
    )


def _create_component(api, name="Test Component", req_ids=None, relationships=None):
    """Create a committed component slot."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "requirement_ids": req_ids or [],
    }
    if relationships:
        content["relationships"] = relationships
    result = api.create("component", content)
    return result["slot_id"]


def _create_interface(api, name="Test Interface", source_comp="", target_comp="", req_ids=None):
    """Create a committed interface slot."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "source_component": source_comp,
        "target_component": target_comp,
        "direction": "unidirectional",
    }
    if req_ids:
        content["requirement_ids"] = req_ids
    result = api.create("interface", content)
    return result["slot_id"]


def _create_contract(api, name="Test Contract", comp_id="", intf_id="",
                     obligations=None, vv_assignments=None, req_ids=None):
    """Create a committed contract slot."""
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
    if req_ids:
        content["requirement_ids"] = req_ids
    result = api.create("contract", content)
    return result["slot_id"]


def _ingest_trace_link(api, from_id, to_id, link_type, link_id_suffix=None):
    """Ingest a traceability-link slot."""
    suffix = link_id_suffix or f"{from_id}-{to_id}"
    return api.ingest(
        f"trace:{suffix}",
        "traceability-link",
        {
            "from_id": from_id,
            "to_id": to_id,
            "link_type": link_type,
        },
    )


# ============================================================
# build_graph() tests
# ============================================================

class TestBuildGraph:
    """Tests for TraceabilityAgent.build_graph()."""

    def test_traceability_link_slots_create_edges(self, api, agent):
        """build_graph() with traceability-link slots creates edges with source='traceability-link'."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph = agent.build_graph()
        edges = graph["edges"]

        matching = [e for e in edges if e["from_id"] == "need:NEED-001"
                    and e["to_id"] == "requirement:REQ-001"]
        assert len(matching) >= 1
        assert matching[0]["source"] == "traceability-link"
        assert matching[0]["edge_type"] == "satisfies"

    def test_component_requirement_ids_create_allocated_to_edges(self, api, agent):
        """build_graph() with component having requirement_ids creates allocated_to edges."""
        _ingest_requirement(api, "REQ-001")
        comp_id = _create_component(api, "Auth Service", req_ids=["requirement:REQ-001"])

        graph = agent.build_graph()
        edges = graph["edges"]

        matching = [e for e in edges if e["from_id"] == "requirement:REQ-001"
                    and e["to_id"] == comp_id and e["edge_type"] == "allocated_to"]
        assert len(matching) == 1
        assert matching[0]["source"] == "embedded_field"

    def test_interface_boundary_of_edges(self, api, agent):
        """build_graph() with interface having source/target creates boundary_of edges."""
        comp_a = _create_component(api, "Component A")
        comp_b = _create_component(api, "Component B")
        intf_id = _create_interface(api, "A-B Interface", source_comp=comp_a, target_comp=comp_b)

        graph = agent.build_graph()
        edges = graph["edges"]

        boundary_edges = [e for e in edges if e["edge_type"] == "boundary_of"
                          and e["to_id"] == intf_id]
        assert len(boundary_edges) == 2
        from_ids = {e["from_id"] for e in boundary_edges}
        assert comp_a in from_ids
        assert comp_b in from_ids

    def test_contract_vv_assignments_create_synthetic_nodes(self, api, agent):
        """build_graph() with contract vv_assignments creates synthetic vv: nodes."""
        comp_id = _create_component(api, "Auth Service")
        intf_id = _create_interface(api, "Auth API", source_comp=comp_id, target_comp=comp_id)
        cntr_id = _create_contract(
            api, "Auth Contract", comp_id=comp_id, intf_id=intf_id,
            obligations=[{"id": "OBL-001", "statement": "Must validate", "obligation_type": "data_processing"}],
            vv_assignments=[{"obligation_id": "OBL-001", "method": "test", "rationale": "Testable"}],
        )

        graph = agent.build_graph()

        vv_node_id = f"vv:{cntr_id}:OBL-001"
        assert vv_node_id in graph["nodes"]
        assert graph["nodes"][vv_node_id]["type"] == "vv"

        vv_edges = [e for e in graph["edges"]
                    if e["from_id"] == cntr_id and e["to_id"] == vv_node_id]
        assert len(vv_edges) == 1
        assert vv_edges[0]["edge_type"] == "verified_by"

    def test_deduplication_prefers_traceability_link(self, api, agent):
        """build_graph() deduplicates edges, preferring traceability-link source."""
        _ingest_requirement(api, "REQ-001")
        comp_id = _create_component(api, "Auth", req_ids=["requirement:REQ-001"])
        # Same edge via explicit traceability-link
        _ingest_trace_link(api, "requirement:REQ-001", comp_id, "allocated_to", "req001-comp")

        graph = agent.build_graph()
        edges = graph["edges"]

        matching = [e for e in edges if e["from_id"] == "requirement:REQ-001"
                    and e["to_id"] == comp_id and e["edge_type"] == "allocated_to"]
        assert len(matching) == 1
        assert matching[0]["source"] == "traceability-link"

    def test_divergent_edges_flagged(self, api, agent):
        """build_graph() flags divergent edges (same from/to, different edge_type)."""
        _ingest_requirement(api, "REQ-001")
        comp_id = _create_component(api, "Auth", req_ids=["requirement:REQ-001"])
        # Same from/to but different edge_type via explicit link
        _ingest_trace_link(api, "requirement:REQ-001", comp_id, "derives_from", "divergent")

        graph = agent.build_graph()

        assert len(graph.get("chain_report", {}).get("divergences", [])) >= 1
        div = graph["chain_report"]["divergences"][0]
        assert div["from_id"] == "requirement:REQ-001"
        assert div["to_id"] == comp_id

    def test_forward_and_reverse_adjacency(self, api, agent):
        """build_graph() builds both forward and reverse adjacency dicts."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph = agent.build_graph()

        assert "requirement:REQ-001" in graph["_forward_adj"].get("need:NEED-001", {})
        assert "need:NEED-001" in graph["_reverse_adj"].get("requirement:REQ-001", {})


# ============================================================
# validate_chains() tests
# ============================================================

class TestValidateChains:
    """Tests for TraceabilityAgent.validate_chains()."""

    def test_complete_chain_detected(self, api, agent):
        """validate_chains() detects complete chain (need->req->comp->intf->cntr->vv)."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        comp_id = _create_component(api, "Auth", req_ids=["requirement:REQ-001"])
        intf_id = _create_interface(api, "Auth API", source_comp=comp_id, target_comp=comp_id)
        cntr_id = _create_contract(
            api, "Auth Contract", comp_id=comp_id, intf_id=intf_id,
            obligations=[{"id": "OBL-001", "statement": "Validate", "obligation_type": "data_processing"}],
            vv_assignments=[{"obligation_id": "OBL-001", "method": "test", "rationale": "Testable"}],
        )

        graph = agent.build_graph()
        report = agent.validate_chains(graph)

        complete = [c for c in report["chains"] if c["need_id"] == "need:NEED-001" and c["status"] == "complete"]
        assert len(complete) == 1

    def test_broken_chain_at_component_level(self, api, agent):
        """validate_chains() detects chain broken at component (need->req but no comp)."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph = agent.build_graph()
        report = agent.validate_chains(graph)

        gaps = [g for g in report["gaps"] if g["need_id"] == "need:NEED-001"]
        assert len(gaps) >= 1
        assert any(g["severity"] in ("critical", "warning") for g in gaps)

    def test_orphan_component_detected(self, api, agent):
        """validate_chains() detects orphan component as info severity."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")
        # Orphan component -- not connected to any requirement
        _create_component(api, "Orphan Service", req_ids=[])

        graph = agent.build_graph()
        report = agent.validate_chains(graph)

        orphans = [g for g in report["gaps"] if g["severity"] == "info" and "orphan" in g.get("type", "").lower()]
        assert len(orphans) >= 1

    def test_completeness_percentage(self, api, agent):
        """completeness percentage = complete_chains / total_chains * 100."""
        _ingest_need(api, "NEED-001")
        _ingest_need(api, "NEED-002")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        comp_id = _create_component(api, "Auth", req_ids=["requirement:REQ-001"])
        intf_id = _create_interface(api, "Auth API", source_comp=comp_id, target_comp=comp_id)
        _create_contract(
            api, "Auth Contract", comp_id=comp_id, intf_id=intf_id,
            obligations=[{"id": "OBL-001", "statement": "Validate", "obligation_type": "data_processing"}],
            vv_assignments=[{"obligation_id": "OBL-001", "method": "test", "rationale": "Testable"}],
        )

        graph = agent.build_graph()
        report = agent.validate_chains(graph)

        # NEED-001 has complete chain, NEED-002 has no chain at all
        assert report["completeness"]["total_chains"] == 2
        assert report["completeness"]["complete_chains"] == 1
        assert report["completeness"]["percentage"] == 50.0


# ============================================================
# check_staleness() tests
# ============================================================

class TestStaleness:
    """Tests for staleness checking and build_or_refresh."""

    def test_staleness_true_when_slot_newer(self, api, agent):
        """check_staleness() returns True when a slot updated_at > graph built_at."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph_slot = agent.build_or_refresh()
        built_at = graph_slot["built_at"]

        # Add a new component after graph was built
        time.sleep(0.05)
        _create_component(api, "New Component")

        assert agent.check_staleness(graph_slot) is True

    def test_staleness_false_when_all_older(self, api, agent):
        """check_staleness() returns False when all slots older than built_at."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph_slot = agent.build_or_refresh()

        assert agent.check_staleness(graph_slot) is False

    def test_build_or_refresh_creates_new_graph(self, api, agent):
        """build_or_refresh() creates new graph when none exists."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        result = agent.build_or_refresh()

        assert result["slot_id"] == "tgraph-current"
        assert result["slot_type"] == "traceability-graph"
        assert "built_at" in result
        assert "nodes" in result
        assert "edges" in result
        assert "completeness" in result
        assert "chain_report" in result

    def test_build_or_refresh_rebuilds_when_stale(self, api, agent):
        """build_or_refresh() rebuilds graph when stale."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        first = agent.build_or_refresh()
        first_built = first["built_at"]

        time.sleep(0.05)
        _create_component(api, "New Component")

        second = agent.build_or_refresh()
        assert second["built_at"] > first_built
        # New component should appear in nodes
        comp_nodes = [nid for nid, n in second["nodes"].items() if n["type"] == "component"]
        assert len(comp_nodes) >= 1

    def test_build_or_refresh_returns_existing_when_fresh(self, api, agent):
        """build_or_refresh() returns existing graph when not stale."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        first = agent.build_or_refresh()
        second = agent.build_or_refresh()

        assert second["built_at"] == first["built_at"]
        assert second["version"] == first["version"]


# ============================================================
# format_trace_output() tests
# ============================================================

class TestFormatOutput:
    """Tests for TraceabilityAgent.format_trace_output()."""

    def test_output_has_completeness_at_top(self, api, agent):
        """format_trace_output() shows completeness percentage at top."""
        _ingest_need(api, "NEED-001")
        _ingest_requirement(api, "REQ-001")
        _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")

        graph_slot = agent.build_or_refresh()
        output = agent.format_trace_output(graph_slot)

        # Completeness should appear in the first few lines
        lines = output.strip().split("\n")
        top_section = "\n".join(lines[:5])
        assert "%" in top_section


# ============================================================
# compute_impact() tests
# ============================================================

def _build_full_graph(api):
    """Build a full design graph for impact tests.

    Creates: 2 needs, 3 reqs, 2 components, 1 interface, 1 contract with V&V.
    Returns dict with all slot IDs.
    """
    _ingest_need(api, "NEED-001", "Authentication need")
    _ingest_need(api, "NEED-002", "Authorization need")
    _ingest_requirement(api, "REQ-001", "Login requirement")
    _ingest_requirement(api, "REQ-002", "Session requirement")
    _ingest_requirement(api, "REQ-003", "Access control requirement")

    _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-001", "satisfies")
    _ingest_trace_link(api, "need:NEED-001", "requirement:REQ-002", "satisfies")
    _ingest_trace_link(api, "need:NEED-002", "requirement:REQ-003", "satisfies")

    comp_a = _create_component(api, "Auth Service", req_ids=["requirement:REQ-001", "requirement:REQ-002"])
    comp_b = _create_component(api, "Access Service", req_ids=["requirement:REQ-003"])

    intf_id = _create_interface(api, "Auth-Access API", source_comp=comp_a, target_comp=comp_b)

    cntr_id = _create_contract(
        api, "Auth Protocol", comp_id=comp_a, intf_id=intf_id,
        obligations=[
            {"id": "OBL-001", "statement": "Validate tokens", "obligation_type": "data_processing"},
        ],
        vv_assignments=[
            {"obligation_id": "OBL-001", "method": "test", "rationale": "Unit testable"},
        ],
    )

    return {
        "need_001": "need:NEED-001",
        "need_002": "need:NEED-002",
        "req_001": "requirement:REQ-001",
        "req_002": "requirement:REQ-002",
        "req_003": "requirement:REQ-003",
        "comp_a": comp_a,
        "comp_b": comp_b,
        "intf": intf_id,
        "cntr": cntr_id,
        "vv_node": f"vv:{cntr_id}:OBL-001",
    }


class TestComputeImpact:
    """Tests for TraceabilityAgent.compute_impact()."""

    def test_forward_impact_returns_downstream(self, api, agent):
        """compute_impact forward from a requirement returns all downstream elements."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward")

        assert result["source_element"] == ids["req_001"]
        assert result["direction"] == "forward"
        assert result["affected_count"] >= 1
        # Should reach comp_a at minimum
        all_ids = _collect_element_ids(result["paths"])
        assert ids["comp_a"] in all_ids

    def test_backward_impact_returns_upstream(self, api, agent):
        """compute_impact backward from a contract returns all upstream elements."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["cntr"], direction="backward")

        assert result["direction"] == "backward"
        all_ids = _collect_element_ids(result["paths"])
        # Should reach at least the interface or component upstream
        assert ids["comp_a"] in all_ids or ids["intf"] in all_ids

    def test_both_direction_returns_union(self, api, agent):
        """compute_impact with direction='both' returns union of forward and backward."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["comp_a"], direction="both")

        assert result["direction"] == "both"
        all_ids = _collect_element_ids(result["paths"])
        # Should have both upstream (requirements) and downstream (interface, contract)
        assert len(all_ids) >= 2

    def test_depth_limit_1_returns_direct_neighbors(self, api, agent):
        """compute_impact with depth_limit=1 returns only direct neighbors."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward", depth_limit=1)

        all_ids = _collect_element_ids(result["paths"])
        # With depth 1, should get direct downstream (comp_a) but NOT deeper (intf, cntr, vv)
        assert ids["comp_a"] in all_ids
        # Contract is 3+ hops from requirement, should NOT be in depth-1 result
        assert ids["cntr"] not in all_ids

    def test_depth_limit_2_returns_neighbors_and_their_neighbors(self, api, agent):
        """compute_impact with depth_limit=2 goes two levels deep."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward", depth_limit=2)

        all_ids = _collect_element_ids(result["paths"])
        assert ids["comp_a"] in all_ids
        # Interface is 2 hops from requirement via component
        assert ids["intf"] in all_ids

    def test_depth_limit_none_traverses_entire_graph(self, api, agent):
        """compute_impact with depth_limit=None traverses entire reachable graph."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward", depth_limit=None)

        all_ids = _collect_element_ids(result["paths"])
        # Should eventually reach V&V node
        assert ids["vv_node"] in all_ids

    def test_type_filter_restricts_output_not_traversal(self, api, agent):
        """compute_impact with type_filter shows only filtered types but traverses all internally."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward", type_filter=["component"])

        # Output paths should only contain component nodes
        all_types = _collect_element_types(result["paths"])
        assert all(t == "component" for t in all_types)
        # But affected_count should reflect full traversal (all reachable nodes)
        assert result["affected_count"] >= 2  # At least comp + intf or more

    def test_cyclic_graph_terminates(self, api, agent):
        """compute_impact on a cyclic graph terminates and returns correct results."""
        ids = _build_full_graph(api)
        # Create a cycle: add traceability link from contract back to requirement
        _ingest_trace_link(api, ids["cntr"], ids["req_001"], "derives_from", "cycle-edge")

        result = agent.compute_impact(ids["req_001"], direction="forward")

        # Should terminate (not infinite loop) and have results
        assert result["affected_count"] >= 1
        assert result["source_element"] == ids["req_001"]

    def test_uncertainty_markers_when_orphan_nodes(self, api, agent):
        """compute_impact includes uncertainty markers when graph has unreachable nodes."""
        ids = _build_full_graph(api)
        # Create an orphan component not connected to anything from start_id
        _create_component(api, "Orphan Module", req_ids=[])

        result = agent.compute_impact(ids["req_001"], direction="forward")

        # Graph coverage < 100% because orphan is unreachable
        assert result["graph_coverage_percent"] < 100
        assert len(result["uncertainty_markers"]) >= 1

    def test_tree_structured_paths(self, api, agent):
        """compute_impact returns tree-structured paths with children arrays."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward")

        assert isinstance(result["paths"], list)
        assert len(result["paths"]) >= 1
        # Root should have children
        root = result["paths"][0]
        assert "children" in root
        assert "element_id" in root
        assert "element_type" in root
        assert "depth" in root

    def test_nonexistent_start_id_returns_empty_with_gap(self, api, agent):
        """compute_impact on nonexistent start_id returns empty result with gap_marker."""
        _build_full_graph(api)
        result = agent.compute_impact("nonexistent-id-xyz", direction="forward")

        assert result["affected_count"] == 0
        assert len(result["paths"]) == 0
        assert len(result["gap_markers"]) >= 1
        assert result["gap_markers"][0]["type"] == "missing_data"


class TestPersistImpact:
    """Tests for TraceabilityAgent.persist_impact()."""

    def test_persist_creates_impact_analysis_slot(self, api, agent):
        """persist_impact creates an impact-analysis slot in registry."""
        ids = _build_full_graph(api)
        impact_result = agent.compute_impact(ids["req_001"], direction="forward")

        persisted = agent.persist_impact(impact_result)

        assert persisted["slot_type"] == "impact-analysis"
        assert persisted["slot_id"].startswith("impact-")

        # Should be readable from API
        read_back = api.read(persisted["slot_id"])
        assert read_back is not None
        assert read_back["source_element"] == ids["req_001"]


class TestFormatImpactOutput:
    """Tests for TraceabilityAgent.format_impact_output()."""

    def test_format_impact_produces_tree_view(self, api, agent):
        """format_impact_output produces hierarchical tree view string."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward")
        output = agent.format_impact_output(result)

        assert isinstance(output, str)
        assert len(output) > 0
        # Should contain element IDs in the tree
        assert ids["req_001"] in output
        # Should contain affected count summary
        assert "affected" in output.lower() or "impact" in output.lower()

    def test_format_impact_shows_uncertainty_markers(self, api, agent):
        """format_impact_output shows uncertainty markers when present."""
        ids = _build_full_graph(api)
        _create_component(api, "Orphan", req_ids=[])
        result = agent.compute_impact(ids["req_001"], direction="forward")
        output = agent.format_impact_output(result)

        assert "uncertainty" in output.lower() or "coverage" in output.lower()

    def test_format_impact_notes_type_filter(self, api, agent):
        """format_impact_output notes which types were filtered when type_filter used."""
        ids = _build_full_graph(api)
        result = agent.compute_impact(ids["req_001"], direction="forward", type_filter=["component"])
        output = agent.format_impact_output(result)

        assert "filter" in output.lower() or "component" in output.lower()


# -- Test helpers for impact tests --

def _collect_element_ids(paths: list[dict]) -> set[str]:
    """Recursively collect all element_ids from tree-structured paths."""
    ids = set()
    for node in paths:
        ids.add(node["element_id"])
        if "children" in node and node["children"]:
            ids.update(_collect_element_ids(node["children"]))
    return ids


def _collect_element_types(paths: list[dict]) -> list[str]:
    """Recursively collect all element_types from tree-structured paths."""
    types = []
    for node in paths:
        types.append(node["element_type"])
        if "children" in node and node["children"]:
            types.extend(_collect_element_types(node["children"]))
    return types
