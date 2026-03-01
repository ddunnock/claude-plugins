"""Integration tests for decomposition + approval flow end-to-end."""

import os

import pytest

from scripts.approval_gate import ApprovalGate
from scripts.decomposition_agent import (
    DecompositionAgent,
    check_stale_components,
)
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI

# Paths relative to project root
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
    """Create a DecompositionAgent instance."""
    return DecompositionAgent(api, SCHEMAS_DIR)


@pytest.fixture
def gate(api):
    """Create an ApprovalGate instance."""
    return ApprovalGate(api, RULES_PATH, "component-proposal")


def _populate_requirements(api, count=10):
    """Populate workspace with realistic requirement and need slots across 3 source blocks."""
    blocks = ["AUTHENTICATION", "DATA-MANAGEMENT", "REPORTING"]
    needs = [
        ("NEED-001", "Users need secure authentication", "End User", "AUTHENTICATION"),
        ("NEED-002", "Admins need data management capabilities", "Admin", "DATA-MANAGEMENT"),
        ("NEED-003", "Stakeholders need reporting dashboards", "Manager", "REPORTING"),
    ]

    # Ingest needs
    for need_id, desc, stakeholder, block in needs:
        api.ingest(f"need:{need_id}", "need", {
            "upstream_id": need_id,
            "description": desc,
            "stakeholder": stakeholder,
            "source_block": block,
            "provenance": {
                "source": "requirements-dev",
                "upstream_file": "needs_registry.json",
                "ingested_at": "2026-01-01T00:00:00+00:00",
                "hash": f"hash-{need_id}",
            },
        })

    # Ingest requirements distributed across blocks
    req_data = [
        ("REQ-001", "User login with credentials", "AUTHENTICATION", "NEED-001"),
        ("REQ-002", "Session token management", "AUTHENTICATION", "NEED-001"),
        ("REQ-003", "Password reset flow", "AUTHENTICATION", "NEED-001"),
        ("REQ-004", "Multi-factor authentication", "AUTHENTICATION", "NEED-001"),
        ("REQ-005", "CRUD operations on data entities", "DATA-MANAGEMENT", "NEED-002"),
        ("REQ-006", "Data validation rules", "DATA-MANAGEMENT", "NEED-002"),
        ("REQ-007", "Data import/export", "DATA-MANAGEMENT", "NEED-002"),
        ("REQ-008", "Dashboard generation", "REPORTING", "NEED-003"),
        ("REQ-009", "Report scheduling", "REPORTING", "NEED-003"),
        ("REQ-010", "Data visualization widgets", "REPORTING", "NEED-003"),
    ]

    for req_id, desc, block, need in req_data[:count]:
        api.ingest(f"requirement:{req_id}", "requirement", {
            "upstream_id": req_id,
            "description": desc,
            "requirement_type": "functional",
            "source_block": block,
            "parent_need": need,
            "upstream_status": "active",
            "gap_markers": [],
            "derives_from": [],
            "provenance": {
                "source": "requirements-dev",
                "upstream_file": "requirements_registry.json",
                "ingested_at": "2026-01-01T00:00:00+00:00",
                "hash": f"hash-{req_id}",
            },
        })


def _make_components_from_data(data):
    """Simulate Claude's analysis by grouping requirements by source_block."""
    by_block = data["by_source_block"]
    components = []
    for block_name, reqs in by_block.items():
        req_ids = [r["slot_id"] for r in reqs]
        components.append({
            "name": f"{block_name.replace('-', ' ').title()} Service",
            "description": f"Handles {block_name.lower()} functionality",
            "requirement_ids": req_ids,
            "rationale": {
                "narrative": f"Groups all {block_name} requirements by functional coherence",
                "grouping_criteria": ["functional_coherence", "source_block_affinity"],
                "evidence": [
                    {"req_id": r["upstream_id"], "relevance": f"Part of {block_name}"}
                    for r in reqs
                ],
            },
            "relationships": [],
            "gap_markers": [],
        })
    return components


class TestEndToEndDecomposeApprove:
    def test_full_lifecycle_ingest_prepare_propose_accept(self, api, agent, gate):
        """End-to-end: ingest requirements -> prepare -> create proposals -> accept -> verify components."""
        _populate_requirements(api)

        # Prepare data
        data = agent.prepare()
        assert len(data["requirements"]) == 10
        assert data["gap_report"]["severity"] == "none"

        # Simulate Claude's analysis
        components = _make_components_from_data(data)
        assert len(components) == 3  # 3 source blocks

        # Create proposals
        proposals = agent.create_proposals(components, "session-e2e-001")
        assert len(proposals) == 3
        for p in proposals:
            assert p["status"] == "proposed"

        # Accept all via gate
        for p in proposals:
            result = gate.decide(p["slot_id"], "accept", {"notes": "Approved"})
            assert result["new_status"] == "accepted"
            assert "committed_slot_id" in result

            # Verify committed component exists
            comp = api.read(result["committed_slot_id"])
            assert comp is not None
            assert comp["slot_type"] == "component"
            assert comp["status"] == "approved"

    def test_reject_proposal_records_rationale(self, api, agent, gate):
        """Create proposals -> reject one -> verify status and rationale."""
        _populate_requirements(api)
        data = agent.prepare()
        components = _make_components_from_data(data)
        proposals = agent.create_proposals(components, "session-reject-001")

        # Reject the first proposal
        target = proposals[0]
        result = gate.decide(
            target["slot_id"],
            "reject",
            {"rejection_rationale": "Scope too broad, split into sub-components"},
        )
        assert result["new_status"] == "rejected"

        # Verify proposal is rejected
        rejected = api.read(target["slot_id"])
        assert rejected["status"] == "rejected"
        assert rejected["decision"]["rejection_rationale"] == "Scope too broad, split into sub-components"

    def test_modify_then_accept(self, api, agent, gate):
        """Create proposals -> modify one -> accept modified -> verify component from modified version."""
        _populate_requirements(api)
        data = agent.prepare()
        components = _make_components_from_data(data)
        proposals = agent.create_proposals(components, "session-modify-001")

        target = proposals[0]
        original_name = target["name"]

        # Modify the proposal
        gate.decide(
            target["slot_id"],
            "modify",
            {"modifications": {"name": "Refined " + original_name}},
        )

        # Accept the modified proposal
        result = gate.decide(target["slot_id"], "accept", {})
        assert result["new_status"] == "accepted"

        # Committed component has the modified name
        comp = api.read(result["committed_slot_id"])
        assert comp["name"] == "Refined " + original_name

    def test_gap_detection_with_incomplete_requirements(self, api, agent, gate):
        """Gap detection with incomplete requirements -> proposals include gap markers -> accept with gaps."""
        # Ingest requirements with gaps
        for i in range(6):
            gap_markers = []
            if i == 0:
                gap_markers = [
                    {"type": "missing_data", "finding_ref": "GAP-1",
                     "severity": "medium", "description": "Missing upstream data"}
                ]
            api.ingest(f"requirement:GAP-REQ-{i:03d}", "requirement", {
                "upstream_id": f"GAP-REQ-{i:03d}",
                "description": f"Gap test requirement {i}" if i > 0 else "",
                "requirement_type": "functional",
                "source_block": "GAP-BLOCK",
                "parent_need": "",
                "upstream_status": "active",
                "gap_markers": gap_markers,
                "derives_from": [],
                "provenance": {
                    "source": "requirements-dev",
                    "upstream_file": "requirements_registry.json",
                    "ingested_at": "2026-01-01T00:00:00+00:00",
                    "hash": f"hash-gap-{i}",
                },
            })

        data = agent.prepare()
        # Should have gaps (missing description on req 0, gap_markers on req 0)
        assert data["gap_report"]["gap_count"] > 0

        # Create proposal with inherited gap markers
        components = [{
            "name": "Gap-Aware Service",
            "description": "Service with known gaps",
            "requirement_ids": [f"requirement:GAP-REQ-{i:03d}" for i in range(6)],
            "rationale": {"narrative": "Grouped despite gaps"},
            "relationships": [],
            "gap_markers": [
                {"type": "missing_data", "finding_ref": "GAP-1",
                 "severity": "medium", "description": "Inherited from requirements"}
            ],
        }]

        proposals = agent.create_proposals(components, "session-gaps-001")
        assert len(proposals[0]["gap_markers"]) == 1

        # Accept with gaps
        result = gate.decide(proposals[0]["slot_id"], "accept", {"notes": "Accept with known gaps"})
        assert result["new_status"] == "accepted"

        # Component exists with gaps acknowledged
        comp = api.read(result["committed_slot_id"])
        assert comp is not None

    def test_coverage_summary_matches_actual_mapping(self, api, agent):
        """Coverage summary matches actual mapping (no double counting)."""
        _populate_requirements(api)
        data = agent.prepare()
        total = data["gap_report"]["total_requirements"]

        # Create proposals where some requirements overlap (shouldn't happen normally
        # but we verify deduplication)
        components = [
            {
                "name": "Service A",
                "description": "A",
                "requirement_ids": ["requirement:REQ-001", "requirement:REQ-002"],
                "rationale": {"narrative": "test"},
                "relationships": [],
                "gap_markers": [],
            },
            {
                "name": "Service B",
                "description": "B",
                "requirement_ids": ["requirement:REQ-002", "requirement:REQ-003"],  # REQ-002 overlaps
                "rationale": {"narrative": "test"},
                "relationships": [],
                "gap_markers": [],
            },
        ]

        proposals = agent.create_proposals(components, "session-coverage-001")
        summary = agent.format_coverage_summary(proposals, total)

        # REQ-001, REQ-002, REQ-003 = 3 unique mapped (not 4)
        assert "3/10 requirements mapped" in summary
        assert "7 unmapped" in summary

    def test_stale_component_detection_after_requirement_update(self, api, agent, gate):
        """Accept a proposal, update a referenced requirement, verify component is flagged stale."""
        _populate_requirements(api)
        data = agent.prepare()
        components = _make_components_from_data(data)

        # Create and accept one proposal
        proposals = agent.create_proposals(components, "session-stale-001")
        target = proposals[0]
        result = gate.decide(target["slot_id"], "accept", {})
        committed_id = result["committed_slot_id"]

        # Get a requirement referenced by this component
        comp = api.read(committed_id)
        parent_reqs = comp["parent_requirements"]
        assert len(parent_reqs) > 0

        # Update one of the referenced requirements (simulate re-ingestion)
        req_id = parent_reqs[0]
        req = api.read(req_id)
        updated = dict(req)
        updated["gap_markers"] = [
            {"type": "missing_data", "finding_ref": "NEW-GAP",
             "severity": "high", "description": "Newly discovered gap"}
        ]
        api.update(req_id, updated, expected_version=req["version"])

        # Check for stale components
        stale = check_stale_components(api)
        assert len(stale) >= 1

        stale_ids = [s["component_slot_id"] for s in stale]
        assert committed_id in stale_ids

        stale_entry = next(s for s in stale if s["component_slot_id"] == committed_id)
        assert req_id in stale_entry["affected_requirement_ids"]
