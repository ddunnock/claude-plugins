"""Integration tests for interface discovery -> proposal -> approval flow end-to-end."""

import os

import pytest

from scripts.approval_gate import ApprovalGate
from scripts.init_workspace import init_workspace
from scripts.interface_agent import (
    InterfaceAgent,
    check_stale_interfaces,
    discover_interface_candidates,
)
from scripts.registry import SlotAPI

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, "schemas")
RULES_PATH = os.path.join(PROJECT_ROOT, "data", "approval-rules.json")


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
    """Create an InterfaceAgent instance."""
    return InterfaceAgent(api, SCHEMAS_DIR)


@pytest.fixture
def interface_gate(api):
    """Create an ApprovalGate for interface-proposals."""
    return ApprovalGate(api, RULES_PATH, "interface-proposal")


@pytest.fixture
def component_gate(api):
    """Create an ApprovalGate for component-proposals."""
    return ApprovalGate(api, RULES_PATH, "component-proposal")


def _setup_components_with_proposals(api, component_gate):
    """Set up 3 approved components via proposal flow with relationships.

    Returns dict mapping component names to their committed slot_ids.
    """
    # Create 3 component proposals with relationships
    proposals = []
    components_data = [
        {
            "name": "Auth Service",
            "description": "Handles authentication and authorization",
            "status": "proposed",
            "requirement_ids": ["requirement:REQ-001", "requirement:REQ-002"],
            "rationale": {"narrative": "Auth requirements grouped together"},
            "gap_markers": [],
            "relationships": [
                {
                    "target_proposal": "Data Manager",
                    "type": "data_flow",
                    "description": "Validates credentials against user store",
                }
            ],
            "decision": {
                "action": None,
                "decided_by": None,
                "decided_at": None,
                "notes": None,
                "rejection_rationale": None,
                "modifications": None,
                "committed_slot_id": None,
            },
            "proposal_session_id": "setup-session",
        },
        {
            "name": "Data Manager",
            "description": "Manages data storage and retrieval",
            "status": "proposed",
            "requirement_ids": ["requirement:REQ-003", "requirement:REQ-004"],
            "rationale": {"narrative": "Data management requirements grouped"},
            "gap_markers": [],
            "relationships": [
                {
                    "target_proposal": "Report Engine",
                    "type": "data_flow",
                    "description": "Provides data for report generation",
                }
            ],
            "decision": {
                "action": None,
                "decided_by": None,
                "decided_at": None,
                "notes": None,
                "rejection_rationale": None,
                "modifications": None,
                "committed_slot_id": None,
            },
            "proposal_session_id": "setup-session",
        },
        {
            "name": "Report Engine",
            "description": "Generates reports and dashboards",
            "status": "proposed",
            "requirement_ids": ["requirement:REQ-005", "requirement:REQ-006"],
            "rationale": {"narrative": "Reporting requirements grouped"},
            "gap_markers": [],
            "relationships": [],
            "decision": {
                "action": None,
                "decided_by": None,
                "decided_at": None,
                "notes": None,
                "rejection_rationale": None,
                "modifications": None,
                "committed_slot_id": None,
            },
            "proposal_session_id": "setup-session",
        },
    ]

    for data in components_data:
        result = api.create("component-proposal", data, "test")
        proposals.append(result)

    # Accept all proposals through the gate
    name_to_id = {}
    for proposal_result in proposals:
        pid = proposal_result["slot_id"]
        result = component_gate.decide(pid, "accept", {"notes": "Approved"})
        committed_id = result["committed_slot_id"]
        comp = api.read(committed_id)
        name_to_id[comp["name"]] = committed_id

    return name_to_id


class TestFullInterfaceDiscoveryAndApproval:
    def test_full_interface_discovery_and_approval(
        self, api, agent, interface_gate, component_gate
    ):
        """Set up 3 approved components with relationships, run discovery, create proposals, accept through gate."""
        _setup_components_with_proposals(api, component_gate)

        # Discover interface candidates
        data = agent.prepare()
        assert data["candidate_count"] >= 2  # Auth->Data and Data->Report
        assert data["component_count"] == 3

        # Enrich candidates (simulate Claude output)
        enriched = []
        for candidate in data["candidates"]:
            source_comp = api.read(candidate["source_component"])
            target_comp = api.read(candidate["target_component"])
            source_name = source_comp["name"] if source_comp else "Unknown"
            target_name = target_comp["name"] if target_comp else "Unknown"

            enriched.append({
                "name": f"{source_name}-to-{target_name}: data exchange",
                "description": candidate.get("description", "Interface between components"),
                "source_component": candidate["source_component"],
                "target_component": candidate["target_component"],
                "direction": "unidirectional",
                "protocol": "function_call",
                "data_format_schema": {
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                },
                "error_categories": [
                    {
                        "name": "validation_error",
                        "description": "Invalid input",
                        "expected_behavior": "Return error, no retry",
                    }
                ],
                "rationale": {
                    "narrative": f"Discovered via {candidate['discovery_method']}"
                },
                "requirement_ids": candidate.get("shared_requirement_ids", []),
                "gap_markers": [],
            })

        # Create proposals
        proposals = agent.create_proposals(enriched, "integration-session-001")
        assert len(proposals) >= 2

        # Accept all through approval gate
        for p in proposals:
            result = interface_gate.decide(p["slot_id"], "accept", {"notes": "Approved"})
            assert result["new_status"] == "accepted"
            assert "committed_slot_id" in result

            # Verify committed interface slot
            intf = api.read(result["committed_slot_id"])
            assert intf is not None
            assert intf["slot_type"] == "interface"
            assert intf["status"] == "approved"
            assert intf["direction"] == "unidirectional"
            assert intf["protocol"] == "function_call"


class TestStaleInterfaceDetection:
    def test_stale_interface_detection_after_component_update(
        self, api, agent, interface_gate, component_gate
    ):
        """Create approved interface, update source component, verify stale detection."""
        name_to_id = _setup_components_with_proposals(api, component_gate)

        # Create and accept an interface proposal
        auth_id = name_to_id["Auth Service"]
        data_id = name_to_id["Data Manager"]

        proposals = agent.create_proposals(
            [
                {
                    "name": "Auth-to-Data: credential check",
                    "description": "Validates credentials",
                    "source_component": auth_id,
                    "target_component": data_id,
                    "direction": "unidirectional",
                    "protocol": "function_call",
                    "data_format_schema": {},
                    "error_categories": [],
                    "rationale": {"narrative": "Auth needs data"},
                    "requirement_ids": [],
                    "gap_markers": [],
                }
            ],
            "stale-test-session",
        )

        result = interface_gate.decide(
            proposals[0]["slot_id"], "accept", {"notes": "OK"}
        )
        committed_intf_id = result["committed_slot_id"]

        # Update source component to make it newer
        auth_comp = api.read(auth_id)
        updated = dict(auth_comp)
        updated["description"] = "Updated auth service description"
        api.update(auth_id, updated, expected_version=auth_comp["version"])

        # Detect stale
        stale = check_stale_interfaces(api)
        assert len(stale) == 1
        assert stale[0]["slot_id"] == committed_intf_id
        assert "source component" in stale[0]["reason"]


class TestOrphanComponentReporting:
    def test_orphan_component_reporting(self, api, agent, component_gate):
        """Create component with no relationships, verify it appears in orphan list."""
        _setup_components_with_proposals(api, component_gate)

        # Add an isolated component (no relationships, no shared requirements)
        isolated = api.create(
            "component",
            {
                "name": "Isolated Service",
                "description": "A standalone component",
                "status": "approved",
                "requirement_ids": ["requirement:REQ-UNIQUE"],
                "rationale": {"narrative": "Standalone"},
                "gap_markers": [],
            },
            "test",
        )

        data = agent.prepare()
        assert isolated["slot_id"] in data["orphan_components"]

        # Verify the summary mentions orphans
        summary = agent.format_preparation_summary(data)
        assert "Orphan" in summary
        assert isolated["slot_id"] in summary


class TestApprovalGateWithInterfaceProposals:
    def test_approval_gate_with_interface_proposals(
        self, api, agent, interface_gate, component_gate
    ):
        """Create interface-proposal, accept/reject/modify through ApprovalGate."""
        name_to_id = _setup_components_with_proposals(api, component_gate)
        auth_id = name_to_id["Auth Service"]
        data_id = name_to_id["Data Manager"]
        report_id = name_to_id["Report Engine"]

        # Create 3 proposals
        interfaces = [
            {
                "name": "Auth-to-Data: cred check",
                "description": "Credential validation",
                "source_component": auth_id,
                "target_component": data_id,
                "direction": "unidirectional",
                "protocol": "function_call",
                "data_format_schema": {},
                "error_categories": [],
                "rationale": {"narrative": "Auth->Data"},
                "requirement_ids": [],
                "gap_markers": [],
            },
            {
                "name": "Data-to-Report: data feed",
                "description": "Data for reports",
                "source_component": data_id,
                "target_component": report_id,
                "direction": "unidirectional",
                "protocol": "event",
                "data_format_schema": {},
                "error_categories": [],
                "rationale": {"narrative": "Data->Report"},
                "requirement_ids": [],
                "gap_markers": [],
            },
            {
                "name": "Auth-to-Report: access control",
                "description": "Access check for reports",
                "source_component": auth_id,
                "target_component": report_id,
                "direction": "unidirectional",
                "protocol": "function_call",
                "data_format_schema": {},
                "error_categories": [],
                "rationale": {"narrative": "Auth->Report"},
                "requirement_ids": [],
                "gap_markers": [],
            },
        ]

        proposals = agent.create_proposals(interfaces, "gate-test-session")

        # Accept first
        r1 = interface_gate.decide(proposals[0]["slot_id"], "accept", {"notes": "Good"})
        assert r1["new_status"] == "accepted"
        assert r1["committed_slot_id"] is not None

        # Reject second
        r2 = interface_gate.decide(
            proposals[1]["slot_id"],
            "reject",
            {"rejection_rationale": "Not needed yet"},
        )
        assert r2["new_status"] == "rejected"

        # Modify third
        r3 = interface_gate.decide(
            proposals[2]["slot_id"],
            "modify",
            {"modifications": {"protocol": "event"}},
        )
        assert r3["new_status"] == "modified"

        # Accept the modified proposal
        r4 = interface_gate.decide(proposals[2]["slot_id"], "accept", {})
        assert r4["new_status"] == "accepted"
        committed = api.read(r4["committed_slot_id"])
        assert committed["protocol"] == "event"  # modification was applied


class TestDuplicatePairPrevention:
    def test_duplicate_pair_prevention(self, api):
        """Multiple discovery methods find same pair, only one candidate produced."""
        # Create components that share a requirement AND have a relationship
        shared_req = "requirement:REQ-SHARED"

        comp_a_result = api.create(
            "component",
            {
                "name": "Alpha",
                "description": "Alpha service",
                "status": "approved",
                "requirement_ids": [shared_req, "requirement:REQ-A"],
                "rationale": {"narrative": "Alpha"},
                "gap_markers": [],
            },
            "test",
        )
        comp_b_result = api.create(
            "component",
            {
                "name": "Beta",
                "description": "Beta service",
                "status": "approved",
                "requirement_ids": [shared_req, "requirement:REQ-B"],
                "rationale": {"narrative": "Beta"},
                "gap_markers": [],
            },
            "test",
        )

        # Also create accepted proposal with relationship pointing to Beta
        api.create(
            "component-proposal",
            {
                "name": "Alpha",
                "description": "Alpha proposal",
                "status": "accepted",
                "requirement_ids": [shared_req],
                "rationale": {"narrative": "Alpha proposal"},
                "gap_markers": [],
                "relationships": [
                    {
                        "target_proposal": "Beta",
                        "type": "data_flow",
                        "description": "Alpha sends to Beta",
                    }
                ],
                "decision": {
                    "action": "accept",
                    "decided_by": "developer",
                    "decided_at": "2026-01-01T00:00:00+00:00",
                    "notes": None,
                    "rejection_rationale": None,
                    "modifications": None,
                    "committed_slot_id": comp_a_result["slot_id"],
                },
                "proposal_session_id": "dedup-session",
            },
            "test",
        )
        api.create(
            "component-proposal",
            {
                "name": "Beta",
                "description": "Beta proposal",
                "status": "accepted",
                "requirement_ids": [shared_req],
                "rationale": {"narrative": "Beta proposal"},
                "gap_markers": [],
                "relationships": [],
                "decision": {
                    "action": "accept",
                    "decided_by": "developer",
                    "decided_at": "2026-01-01T00:00:00+00:00",
                    "notes": None,
                    "rejection_rationale": None,
                    "modifications": None,
                    "committed_slot_id": comp_b_result["slot_id"],
                },
                "proposal_session_id": "dedup-session",
            },
            "test",
        )

        candidates = discover_interface_candidates(api)
        # Should be exactly 1 candidate, not 2 (relationship + crossref)
        pairs = [
            frozenset([c["source_component"], c["target_component"]])
            for c in candidates
        ]
        target_pair = frozenset([comp_a_result["slot_id"], comp_b_result["slot_id"]])
        assert pairs.count(target_pair) == 1


class TestInterfaceWithGapMarkers:
    def test_interface_with_gap_markers(self, api, agent, interface_gate, component_gate):
        """Component with gap markers produces interface proposals with gap markers propagated."""
        name_to_id = _setup_components_with_proposals(api, component_gate)
        auth_id = name_to_id["Auth Service"]
        data_id = name_to_id["Data Manager"]

        gap_markers = [
            {
                "type": "missing_data",
                "finding_ref": "GAP-INTF-1",
                "severity": "medium",
                "description": "Protocol uncertain, needs design review",
            }
        ]

        proposals = agent.create_proposals(
            [
                {
                    "name": "Auth-to-Data: gap test",
                    "description": "Interface with gaps",
                    "source_component": auth_id,
                    "target_component": data_id,
                    "direction": "unidirectional",
                    "protocol": "function_call",
                    "data_format_schema": {},
                    "error_categories": [],
                    "rationale": {"narrative": "Test gap propagation"},
                    "requirement_ids": [],
                    "gap_markers": gap_markers,
                }
            ],
            "gap-test-session",
        )

        assert len(proposals[0]["gap_markers"]) == 1
        assert proposals[0]["gap_markers"][0]["finding_ref"] == "GAP-INTF-1"

        # Accept with gaps
        result = interface_gate.decide(
            proposals[0]["slot_id"], "accept", {"notes": "Accept with known gaps"}
        )
        committed = api.read(result["committed_slot_id"])
        assert committed is not None
        # Gap markers should be propagated to committed slot via generic field-copy
        assert len(committed.get("gap_markers", [])) == 1
