"""Tests for approval_gate.py -- generic approval gate engine with declarative state transitions."""

import os
import time

import pytest

from scripts.approval_gate import ApprovalGate, load_approval_rules, validate_transition
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
def rules():
    """Load the approval rules config."""
    return load_approval_rules(RULES_PATH)


@pytest.fixture
def gate(api):
    """Create an ApprovalGate instance for component-proposals."""
    return ApprovalGate(api, RULES_PATH, "component-proposal")


def _make_proposal(api, name="Auth Service", session_id="session-001", **overrides):
    """Helper to create a component-proposal via SlotAPI."""
    content = {
        "name": name,
        "description": f"Handles {name.lower()} functionality",
        "status": "proposed",
        "requirement_ids": ["requirement:REQ-001", "requirement:REQ-002"],
        "rationale": {
            "narrative": f"{name} groups authentication concerns",
            "grouping_criteria": ["functional_coherence"],
            "evidence": [{"req_id": "REQ-001", "relevance": "direct"}],
        },
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
        "proposal_session_id": session_id,
        "extensions": {},
    }
    content.update(overrides)
    result = api.create("component-proposal", content)
    return result["slot_id"]


# --- load_approval_rules tests ---


class TestLoadApprovalRules:
    def test_loads_valid_config(self, rules):
        """Loads approval rules with expected structure."""
        assert "states" in rules
        assert "schema_version" in rules
        assert len(rules["states"]) == 4
        assert set(rules["states"].keys()) == {
            "proposed",
            "accepted",
            "rejected",
            "modified",
        }

    def test_file_not_found_raises(self):
        """Missing rules file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_approval_rules("/nonexistent/path.json")


# --- validate_transition tests ---


class TestValidateTransition:
    def test_valid_accept_from_proposed(self, rules):
        """Accept from proposed state is valid."""
        is_valid, error = validate_transition(rules, "proposed", "accept", {})
        assert is_valid is True
        assert error == ""

    def test_valid_reject_with_rationale(self, rules):
        """Reject from proposed with rejection_rationale is valid."""
        is_valid, error = validate_transition(
            rules, "proposed", "reject", {"rejection_rationale": "Too broad"}
        )
        assert is_valid is True

    def test_invalid_action_from_terminal_state(self, rules):
        """Any action from terminal (accepted) state is invalid."""
        is_valid, error = validate_transition(rules, "accepted", "reject", {})
        assert is_valid is False
        assert "terminal" in error

    def test_missing_required_field(self, rules):
        """Reject without rejection_rationale fails validation."""
        is_valid, error = validate_transition(rules, "proposed", "reject", {})
        assert is_valid is False
        assert "rejection_rationale" in error

    def test_invalid_action_for_state(self, rules):
        """Modify is not valid from rejected state."""
        is_valid, error = validate_transition(rules, "rejected", "modify", {})
        assert is_valid is False
        assert "not valid" in error

    def test_unknown_state(self, rules):
        """Unknown state returns invalid."""
        is_valid, error = validate_transition(rules, "nonexistent", "accept", {})
        assert is_valid is False
        assert "Unknown state" in error


# --- ApprovalGate.decide tests ---


class TestApprovalGateDecide:
    def test_accept_creates_component_and_updates_proposal(self, gate, api):
        """Accept creates a committed component slot and updates proposal to accepted."""
        proposal_id = _make_proposal(api)
        result = gate.decide(proposal_id, "accept", {"notes": "Looks good"})

        assert result["action"] == "accept"
        assert result["new_status"] == "accepted"
        assert "committed_slot_id" in result

        # Verify committed component exists
        committed = api.read(result["committed_slot_id"])
        assert committed is not None
        assert committed["slot_type"] == "component"
        assert committed["status"] == "approved"
        assert committed["name"] == "Auth Service"

        # Verify proposal updated
        proposal = api.read(proposal_id)
        assert proposal["status"] == "accepted"
        assert proposal["decision"]["action"] == "accept"
        assert proposal["decision"]["committed_slot_id"] == result["committed_slot_id"]

    def test_reject_updates_proposal_with_rationale(self, gate, api):
        """Reject sets proposal to rejected and records rejection_rationale."""
        proposal_id = _make_proposal(api)
        result = gate.decide(
            proposal_id,
            "reject",
            {"rejection_rationale": "Scope too broad", "notes": "Split it up"},
        )

        assert result["action"] == "reject"
        assert result["new_status"] == "rejected"
        assert "committed_slot_id" not in result

        proposal = api.read(proposal_id)
        assert proposal["status"] == "rejected"
        assert proposal["decision"]["rejection_rationale"] == "Scope too broad"
        assert proposal["decision"]["notes"] == "Split it up"

    def test_reject_requires_rationale(self, gate, api):
        """Reject without rejection_rationale raises ValueError."""
        proposal_id = _make_proposal(api)
        with pytest.raises(ValueError, match="Missing required fields"):
            gate.decide(proposal_id, "reject", {})

    def test_modify_applies_modifications(self, gate, api):
        """Modify applies changes to proposal fields and sets status to modified."""
        proposal_id = _make_proposal(api)
        result = gate.decide(
            proposal_id,
            "modify",
            {"modifications": {"name": "Auth & Identity Service"}},
        )

        assert result["new_status"] == "modified"

        proposal = api.read(proposal_id)
        assert proposal["status"] == "modified"
        assert proposal["name"] == "Auth & Identity Service"
        assert proposal["decision"]["modifications"] == {
            "name": "Auth & Identity Service"
        }

    def test_modified_proposal_can_be_accepted(self, gate, api):
        """A modified proposal can transition to accepted."""
        proposal_id = _make_proposal(api)

        # First modify
        gate.decide(
            proposal_id,
            "modify",
            {"modifications": {"name": "Refined Auth Service"}},
        )

        # Then accept the modified proposal
        result = gate.decide(proposal_id, "accept", {})
        assert result["new_status"] == "accepted"
        assert "committed_slot_id" in result

        # Committed component has the modified name
        committed = api.read(result["committed_slot_id"])
        assert committed["name"] == "Refined Auth Service"

    def test_nonexistent_proposal_raises(self, gate):
        """Deciding on a nonexistent proposal raises KeyError."""
        with pytest.raises(KeyError, match="Proposal not found"):
            gate.decide("cprop-nonexistent", "accept", {})

    def test_invalid_transition_raises(self, gate, api):
        """Invalid transition (e.g., accept on accepted) raises ValueError."""
        proposal_id = _make_proposal(api)
        gate.decide(proposal_id, "accept", {})

        with pytest.raises(ValueError, match="terminal"):
            gate.decide(proposal_id, "accept", {})

    def test_accept_atomic_ordering(self, gate, api):
        """Component is created BEFORE proposal is updated (Pitfall 2).

        If we read proposal at version 1, the committed component already exists.
        This verifies the ordering: create component first, then update proposal.
        """
        proposal_id = _make_proposal(api)
        result = gate.decide(proposal_id, "accept", {})

        # Component exists (was created first)
        committed = api.read(result["committed_slot_id"])
        assert committed is not None
        assert committed["version"] == 1

        # Proposal was updated after (version incremented)
        proposal = api.read(proposal_id)
        assert proposal["version"] == 2


# --- batch_decide tests ---


class TestBatchDecide:
    def test_processes_multiple_proposals(self, gate, api):
        """Batch decide processes multiple proposals successfully."""
        ids = [_make_proposal(api, name=f"Service {i}") for i in range(3)]
        decisions = [
            {"proposal_id": ids[0], "action": "accept", "decision_data": {}},
            {
                "proposal_id": ids[1],
                "action": "reject",
                "decision_data": {"rejection_rationale": "Not needed"},
            },
            {
                "proposal_id": ids[2],
                "action": "modify",
                "decision_data": {"modifications": {"name": "Updated Service 2"}},
            },
        ]

        results = gate.batch_decide(decisions)
        assert len(results) == 3
        assert results[0]["new_status"] == "accepted"
        assert results[1]["new_status"] == "rejected"
        assert results[2]["new_status"] == "modified"

    def test_stops_on_error_returns_partial(self, gate, api):
        """Batch decide stops on first error and returns partial results."""
        good_id = _make_proposal(api, name="Good Service")
        decisions = [
            {"proposal_id": good_id, "action": "accept", "decision_data": {}},
            {
                "proposal_id": "cprop-nonexistent",
                "action": "accept",
                "decision_data": {},
            },
            {
                "proposal_id": "cprop-also-nonexistent",
                "action": "accept",
                "decision_data": {},
            },
        ]

        results = gate.batch_decide(decisions)
        assert len(results) == 2  # Processed 1 success + 1 error, stopped before 3rd
        assert results[0]["new_status"] == "accepted"
        assert "error" in results[1]


# --- get_pending tests ---


class TestGetPending:
    def test_returns_only_actionable_proposals(self, gate, api):
        """get_pending returns proposed and modified proposals, not accepted/rejected."""
        p1 = _make_proposal(api, name="Pending 1")
        p2 = _make_proposal(api, name="Pending 2")
        p3 = _make_proposal(api, name="To Accept")
        p4 = _make_proposal(api, name="To Reject")

        # Accept p3 and reject p4
        gate.decide(p3, "accept", {})
        gate.decide(p4, "reject", {"rejection_rationale": "Not needed"})

        pending = gate.get_pending()
        pending_ids = {p["slot_id"] for p in pending}
        assert p1 in pending_ids
        assert p2 in pending_ids
        assert p3 not in pending_ids
        assert p4 not in pending_ids

    def test_includes_modified_proposals(self, gate, api):
        """Modified proposals are actionable and included in get_pending."""
        p1 = _make_proposal(api, name="To Modify")
        gate.decide(p1, "modify", {"modifications": {"name": "Modified Service"}})

        pending = gate.get_pending()
        pending_ids = {p["slot_id"] for p in pending}
        assert p1 in pending_ids


# --- Generic type handling tests ---


class TestGenericTypeHandling:
    def test_gate_uses_proposal_type_parameter(self, api):
        """Gate works with proposal_type parameter, not hardcoded type."""
        gate = ApprovalGate(api, RULES_PATH, "component-proposal")
        assert gate._proposal_type == "component-proposal"
        assert gate._committed_type == "component"

    def test_committed_type_derived_from_proposal_type(self, api):
        """Committed type strips '-proposal' suffix from proposal type."""
        gate = ApprovalGate(api, RULES_PATH, "component-proposal")
        assert gate._committed_type == "component"


# --- Performance test ---


class TestPerformance:
    def test_batch_50_proposals_under_5_seconds(self, gate, api):
        """50 proposals batch_decide in under 5 seconds."""
        ids = [_make_proposal(api, name=f"Perf Service {i}") for i in range(50)]
        decisions = [
            {"proposal_id": pid, "action": "accept", "decision_data": {}}
            for pid in ids
        ]

        start = time.time()
        results = gate.batch_decide(decisions)
        elapsed = time.time() - start

        assert len(results) == 50
        assert all("error" not in r for r in results)
        assert elapsed < 5.0, f"Batch took {elapsed:.2f}s, expected < 5s"
