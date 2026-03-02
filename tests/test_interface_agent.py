"""Unit tests for interface agent functions: discovery, deduplication, orphans, stale detection."""

import os
import time

import pytest

from scripts.init_workspace import init_workspace
from scripts.interface_agent import (
    InterfaceAgent,
    check_stale_interfaces,
    detect_orphan_components,
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


def _create_approved_component(api, name, requirement_ids=None, relationships=None):
    """Helper: create an approved component directly (bypassing proposal flow)."""
    content = {
        "name": name,
        "description": f"Test component: {name}",
        "status": "approved",
        "requirement_ids": requirement_ids or [],
        "rationale": {"narrative": f"Test rationale for {name}"},
        "gap_markers": [],
        "relationships": relationships or [],
    }
    result = api.create("component", content, "test")
    return result["slot_id"]


def _create_accepted_proposal(api, name, committed_slot_id, relationships=None):
    """Helper: create an accepted component-proposal with decision pointing to committed slot."""
    content = {
        "name": name,
        "description": f"Proposal for {name}",
        "status": "accepted",
        "requirement_ids": [],
        "rationale": {"narrative": f"Proposal rationale for {name}"},
        "gap_markers": [],
        "relationships": relationships or [],
        "decision": {
            "action": "accept",
            "decided_by": "developer",
            "decided_at": "2026-01-01T00:00:00+00:00",
            "notes": None,
            "rejection_rationale": None,
            "modifications": None,
            "committed_slot_id": committed_slot_id,
        },
        "proposal_session_id": "test-session",
    }
    result = api.create("component-proposal", content, "test")
    return result["slot_id"]


class TestDiscoverCandidatesFromRelationships:
    def test_discover_candidates_from_relationships(self, api):
        """Two components with accepted proposals having relationships produce 1 candidate."""
        comp_a_id = _create_approved_component(api, "Service A")
        comp_b_id = _create_approved_component(api, "Service B")

        # Create accepted proposal for A with relationship to B
        _create_accepted_proposal(
            api,
            "Service A",
            comp_a_id,
            relationships=[
                {
                    "target_proposal": "Service B",
                    "type": "data_flow",
                    "description": "Sends events to Service B",
                }
            ],
        )
        _create_accepted_proposal(api, "Service B", comp_b_id)

        candidates = discover_interface_candidates(api)
        assert len(candidates) == 1
        assert candidates[0]["discovery_method"] == "relationship"
        assert candidates[0]["relationship_type"] == "data_flow"
        # Both components should be in the candidate
        pair = {candidates[0]["source_component"], candidates[0]["target_component"]}
        assert pair == {comp_a_id, comp_b_id}

    def test_discover_candidates_deduplicates_pairs(self, api):
        """Bidirectional relationships produce 1 candidate, not 2."""
        comp_a_id = _create_approved_component(api, "Service A")
        comp_b_id = _create_approved_component(api, "Service B")

        # A -> B relationship
        _create_accepted_proposal(
            api,
            "Service A",
            comp_a_id,
            relationships=[
                {
                    "target_proposal": "Service B",
                    "type": "data_flow",
                    "description": "A sends to B",
                }
            ],
        )
        # B -> A relationship
        _create_accepted_proposal(
            api,
            "Service B",
            comp_b_id,
            relationships=[
                {
                    "target_proposal": "Service A",
                    "type": "data_flow",
                    "description": "B sends to A",
                }
            ],
        )

        candidates = discover_interface_candidates(api)
        assert len(candidates) == 1


class TestDiscoverCandidatesFromRequirementCrossrefs:
    def test_discover_candidates_from_requirement_crossrefs(self, api):
        """Two components sharing requirement_ids produce 1 candidate."""
        shared_req = "requirement:REQ-SHARED"
        _create_approved_component(
            api, "Service A", requirement_ids=[shared_req, "requirement:REQ-A"]
        )
        _create_approved_component(
            api, "Service B", requirement_ids=[shared_req, "requirement:REQ-B"]
        )

        candidates = discover_interface_candidates(api)
        assert len(candidates) == 1
        assert candidates[0]["discovery_method"] == "requirement_crossref"
        assert shared_req in candidates[0]["shared_requirement_ids"]

    def test_crossref_filters_crosscutting_requirements(self, api):
        """Requirement in 3+ components excluded from interface discovery."""
        crosscutting_req = "requirement:REQ-XCUT"
        _create_approved_component(
            api, "Service A", requirement_ids=[crosscutting_req]
        )
        _create_approved_component(
            api, "Service B", requirement_ids=[crosscutting_req]
        )
        _create_approved_component(
            api, "Service C", requirement_ids=[crosscutting_req]
        )

        candidates = discover_interface_candidates(api)
        # Cross-cutting requirement should NOT produce interface candidates
        assert len(candidates) == 0


class TestDetectOrphanComponents:
    def test_detect_orphan_components(self, api):
        """Component with no relationships or shared requirements detected as orphan."""
        comp_a_id = _create_approved_component(api, "Connected A")
        comp_b_id = _create_approved_component(api, "Connected B")
        orphan_id = _create_approved_component(api, "Lonely Orphan")

        # Create relationship between A and B only
        _create_accepted_proposal(
            api,
            "Connected A",
            comp_a_id,
            relationships=[
                {
                    "target_proposal": "Connected B",
                    "type": "data_flow",
                    "description": "A to B",
                }
            ],
        )
        _create_accepted_proposal(api, "Connected B", comp_b_id)

        candidates = discover_interface_candidates(api)
        orphans = detect_orphan_components(api, candidates)
        assert orphan_id in orphans
        assert comp_a_id not in orphans
        assert comp_b_id not in orphans


class TestInterfaceAgentCreateProposals:
    def test_create_proposals_validates_and_persists(self, api):
        """InterfaceAgent.create_proposals creates valid interface-proposal slots."""
        comp_a_id = _create_approved_component(api, "Service A")
        comp_b_id = _create_approved_component(api, "Service B")

        agent = InterfaceAgent(api, SCHEMAS_DIR)
        interfaces = [
            {
                "name": "Service A-to-Service B: data sync",
                "description": "Synchronizes data between A and B",
                "source_component": comp_a_id,
                "target_component": comp_b_id,
                "direction": "unidirectional",
                "protocol": "function_call",
                "data_format_schema": {
                    "type": "object",
                    "properties": {"entity_id": {"type": "string"}},
                },
                "error_categories": [
                    {
                        "name": "validation_error",
                        "description": "Invalid input data",
                        "expected_behavior": "Return error details, no retry",
                    }
                ],
                "rationale": {
                    "narrative": "Service A produces data consumed by Service B"
                },
                "requirement_ids": ["requirement:REQ-001"],
                "gap_markers": [],
            }
        ]

        proposals = agent.create_proposals(interfaces, "test-session-001")
        assert len(proposals) == 1
        p = proposals[0]
        assert p["slot_type"] == "interface-proposal"
        assert p["status"] == "proposed"
        assert p["source_component"] == comp_a_id
        assert p["target_component"] == comp_b_id
        assert p["direction"] == "unidirectional"
        assert p["protocol"] == "function_call"
        assert len(p["error_categories"]) == 1
        assert p["proposal_session_id"] == "test-session-001"


class TestCheckStaleInterfaces:
    def test_check_stale_interfaces_detects_changed_component(self, api):
        """Interface with older updated_at than its component flagged as stale."""
        comp_a_id = _create_approved_component(api, "Service A")
        comp_b_id = _create_approved_component(api, "Service B")

        # Create an approved interface
        intf_result = api.create(
            "interface",
            {
                "name": "A-to-B interface",
                "source_component": comp_a_id,
                "target_component": comp_b_id,
                "status": "approved",
            },
            "test",
        )

        # Update source component to make it newer than the interface
        comp_a = api.read(comp_a_id)
        updated = dict(comp_a)
        updated["description"] = "Updated description"
        api.update(comp_a_id, updated, expected_version=comp_a["version"])

        stale = check_stale_interfaces(api)
        assert len(stale) == 1
        assert stale[0]["slot_id"] == intf_result["slot_id"]
        assert "source component" in stale[0]["reason"]

    def test_check_stale_interfaces_none_stale(self, api):
        """No stale interfaces when timestamps are current."""
        comp_a_id = _create_approved_component(api, "Service A")
        comp_b_id = _create_approved_component(api, "Service B")

        # Create interface AFTER components (so it's newer)
        api.create(
            "interface",
            {
                "name": "A-to-B interface",
                "source_component": comp_a_id,
                "target_component": comp_b_id,
                "status": "approved",
            },
            "test",
        )

        stale = check_stale_interfaces(api)
        assert len(stale) == 0


class TestPerformance:
    def test_discover_candidates_100_components(self, api):
        """Discover candidates across 100 components runs under 1 second."""
        # Create 100 approved components with shared requirements to generate candidates
        comp_ids = []
        for i in range(100):
            comp_id = _create_approved_component(
                api,
                f"Component-{i:03d}",
                requirement_ids=[f"requirement:REQ-{i:03d}", f"requirement:REQ-{(i+1) % 100:03d}"],
            )
            comp_ids.append(comp_id)

        start = time.time()
        candidates = discover_interface_candidates(api)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Discovery took {elapsed:.2f}s, expected < 1s"
        # Each adjacent pair shares a requirement, so we expect ~100 candidates
        assert len(candidates) > 0
