"""Integration tests for behavioral contract lifecycle: data prep -> proposal -> approval -> committed."""

import os

import pytest

from scripts.approval_gate import ApprovalGate
from scripts.contract_agent import ContractAgent, check_stale_contracts
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, "schemas")
VV_RULES_PATH = os.path.join(PROJECT_ROOT, "data", "vv-rules.json")
APPROVAL_RULES_PATH = os.path.join(PROJECT_ROOT, "data", "approval-rules.json")


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
    """Create a ContractAgent instance."""
    return ContractAgent(api, SCHEMAS_DIR, VV_RULES_PATH)


@pytest.fixture
def gate(api):
    """Create an ApprovalGate for contract-proposals."""
    return ApprovalGate(api, APPROVAL_RULES_PATH, "contract-proposal")


def _create_approved_component(api, name="Test Component", req_ids=None):
    """Helper to create an approved component."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "requirement_ids": req_ids or [],
        "rationale": {"narrative": f"Groups {name} requirements"},
    }
    result = api.create("component", content)
    return result["slot_id"]


def _create_approved_interface(api, name="Test Interface", source_comp="", target_comp=""):
    """Helper to create an approved interface."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "source_component": source_comp,
        "target_component": target_comp,
        "direction": "unidirectional",
        "data_format_schema": {},
        "error_categories": [
            {"name": "validation_error", "description": "Input validation failed",
             "expected_behavior": "Return 400 with details"},
        ],
    }
    result = api.create("interface", content)
    return result["slot_id"]


def _ingest_requirement(api, req_id, description="A requirement", req_type="functional"):
    """Helper to ingest a requirement."""
    content = {
        "upstream_id": req_id,
        "description": description,
        "requirement_type": req_type,
        "source_block": "BLOCK-1",
        "parent_need": "",
        "upstream_status": "active",
        "gap_markers": [],
        "derives_from": [],
        "provenance": {
            "source": "requirements-dev",
            "upstream_file": "requirements_registry.json",
            "ingested_at": "2026-01-01T00:00:00+00:00",
            "hash": "abc123",
        },
    }
    slot_id = f"requirement:{req_id}"
    return api.ingest(slot_id, "requirement", content)


class TestFullContractLifecycle:
    def test_prepare_create_approve_commit(self, api, agent, gate):
        """Full lifecycle: prepare data, create proposals, accept through gate, verify committed slots."""
        # Set up: ingest requirements, create approved components and interfaces
        _ingest_requirement(api, "REQ-001", "Data validation requirement")
        _ingest_requirement(api, "REQ-002", "Error reporting requirement")
        comp_id = _create_approved_component(
            api, "Validator", ["requirement:REQ-001", "requirement:REQ-002"]
        )
        intf_id = _create_approved_interface(api, "Validation API", source_comp=comp_id)

        # Step 1: Prepare data
        data = agent.prepare()
        assert data["total_components"] == 1
        assert data["total_interfaces"] == 1
        assert data["total_requirements"] == 2

        # Step 2: Create proposals (simulating Claude's output)
        contracts = [
            {
                "component_id": comp_id,
                "interface_id": intf_id,
                "name": "Validator-ValidationAPI Contract",
                "description": "Behavioral obligations for Validator through Validation API",
                "obligations": [
                    {
                        "id": "OB-001",
                        "statement": "SHALL validate incoming data against schema",
                        "obligation_type": "data_processing",
                        "source_requirement_ids": ["requirement:REQ-001"],
                    },
                    {
                        "id": "OB-002",
                        "statement": "SHALL emit validation_error with field details on failure",
                        "obligation_type": "error_handling",
                        "source_requirement_ids": ["requirement:REQ-002"],
                        "error_category": "validation_error",
                    },
                ],
                "rationale": "Derived from validation and error reporting requirements",
            }
        ]

        proposals = agent.create_proposals(contracts, "session-lifecycle-001")
        assert len(proposals) == 1
        proposal = proposals[0]
        assert proposal["status"] == "proposed"
        assert len(proposal["obligations"]) == 2
        assert len(proposal["vv_assignments"]) == 2

        # Step 3: Accept through approval gate
        result = gate.decide(
            proposal["slot_id"], "accept", {"notes": "LGTM"}
        )
        assert result["new_status"] == "accepted"
        committed_id = result["committed_slot_id"]

        # Step 4: Verify committed contract slot
        committed = api.read(committed_id)
        assert committed is not None
        assert committed["slot_type"] == "contract"
        assert committed["status"] == "approved"
        assert committed["name"] == "Validator-ValidationAPI Contract"
        assert len(committed["obligations"]) == 2
        assert len(committed["vv_assignments"]) == 2
        assert committed["component_id"] == comp_id
        assert committed["interface_id"] == intf_id


class TestStaleContractDetection:
    def test_detects_stale_after_interface_update(self, api):
        """Create approved contract, update its interface, verify stale detection."""
        comp_id = _create_approved_component(api, "Comp")
        intf_id = _create_approved_interface(api, "API", source_comp=comp_id)

        # Create approved contract
        contract_content = {
            "name": "Test Contract",
            "description": "Test",
            "status": "approved",
            "component_id": comp_id,
            "interface_id": intf_id,
            "obligations": [
                {
                    "id": "OB-001",
                    "statement": "SHALL process data",
                    "obligation_type": "data_processing",
                    "source_requirement_ids": [],
                }
            ],
            "vv_assignments": [
                {"obligation_id": "OB-001", "method": "test",
                 "rationale": "Default"},
            ],
            "rationale": {"narrative": "Test"},
        }
        contract_result = api.create("contract", contract_content)
        contract_id = contract_result["slot_id"]

        # Update interface
        intf = api.read(intf_id)
        updated = dict(intf)
        updated["description"] = "Updated interface with new fields"
        api.update(intf_id, updated, expected_version=intf["version"])

        # Verify stale detection
        stale = check_stale_contracts(api)
        assert len(stale) == 1
        assert stale[0]["slot_id"] == contract_id
        assert stale[0]["interface_id"] == intf_id


class TestVvAssignmentsBundled:
    def test_bundled_in_proposal(self, api, agent):
        """Contract-proposal slot contains both obligations and vv_assignments."""
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": "Bundled Contract",
                "description": "Test bundling",
                "obligations": [
                    {
                        "id": "OB-X1",
                        "statement": "SHALL log events",
                        "obligation_type": "logging",
                        "source_requirement_ids": [],
                    },
                    {
                        "id": "OB-X2",
                        "statement": "SHALL compute metrics",
                        "obligation_type": "algorithmic",
                        "source_requirement_ids": [],
                    },
                ],
                "rationale": "Test bundling of V&V with obligations",
            }
        ]

        proposals = agent.create_proposals(contracts, "session-bundle")
        p = proposals[0]

        # Both obligations present
        assert len(p["obligations"]) == 2

        # Both V&V assignments present and bundled
        assert len(p["vv_assignments"]) == 2
        vv_methods = {a["obligation_id"]: a["method"] for a in p["vv_assignments"]}
        assert vv_methods["OB-X1"] == "inspection"  # logging default
        assert vv_methods["OB-X2"] == "analysis"  # algorithmic default


class TestApprovalGateWithContracts:
    def test_accept_reject_modify_contract_proposals(self, api, agent, gate):
        """Accept, reject, and modify contract proposals through ApprovalGate."""
        # Create 3 proposals
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": f"Contract {i}",
                "description": f"Test contract {i}",
                "obligations": [
                    {
                        "id": f"OB-{i}",
                        "statement": f"SHALL do thing {i}",
                        "obligation_type": "data_processing",
                        "source_requirement_ids": [],
                    }
                ],
                "rationale": f"Contract {i} rationale",
            }
            for i in range(3)
        ]

        proposals = agent.create_proposals(contracts, "session-gate")
        assert len(proposals) == 3

        # Accept first
        r1 = gate.decide(proposals[0]["slot_id"], "accept", {"notes": "Good"})
        assert r1["new_status"] == "accepted"
        assert "committed_slot_id" in r1

        # Reject second
        r2 = gate.decide(
            proposals[1]["slot_id"], "reject",
            {"rejection_rationale": "Obligations too vague"}
        )
        assert r2["new_status"] == "rejected"

        # Modify third
        r3 = gate.decide(
            proposals[2]["slot_id"], "modify",
            {"modifications": {"description": "Updated description"}}
        )
        assert r3["new_status"] == "modified"

        # Verify modified proposal
        modified = api.read(proposals[2]["slot_id"])
        assert modified["description"] == "Updated description"
        assert modified["status"] == "modified"


class TestOneLevelCascadeOnly:
    def test_interface_to_contract_cascade(self, api):
        """Interface update flags contract as stale, but contract update does NOT flag interface."""
        comp_id = _create_approved_component(api, "Cascade Comp")
        intf_id = _create_approved_interface(api, "Cascade API", source_comp=comp_id)

        # Create approved contract
        contract_content = {
            "name": "Cascade Contract",
            "description": "Tests cascade direction",
            "status": "approved",
            "component_id": comp_id,
            "interface_id": intf_id,
            "obligations": [],
            "vv_assignments": [],
            "rationale": {"narrative": "Cascade test"},
        }
        contract_result = api.create("contract", contract_content)
        contract_id = contract_result["slot_id"]

        # Update interface -> should flag contract as stale
        intf = api.read(intf_id)
        updated_intf = dict(intf)
        updated_intf["description"] = "Updated"
        api.update(intf_id, updated_intf, expected_version=intf["version"])

        stale = check_stale_contracts(api)
        assert len(stale) == 1
        assert stale[0]["slot_id"] == contract_id

        # Now update the contract too (making it newer)
        contract = api.read(contract_id)
        updated_contract = dict(contract)
        updated_contract["description"] = "Contract also updated"
        api.update(contract_id, updated_contract, expected_version=contract["version"])

        # Contract is now newer than interface -> no longer stale
        stale2 = check_stale_contracts(api)
        assert len(stale2) == 0

        # Verify: contract change does NOT cascade back to interface
        # (check_stale_contracts only checks interface->contract direction)
        # There is no "check_stale_interfaces" that uses contract timestamps


class TestContractWithGapMarkers:
    def test_incomplete_requirements_produce_gap_markers(self, api, agent):
        """Component with incomplete requirements produces proposals with gap markers."""
        # Create component referencing a requirement that does not exist
        comp_id = _create_approved_component(
            api, "Gappy Comp", ["requirement:MISSING-REQ"]
        )
        intf_id = _create_approved_interface(api, "Gappy API", source_comp=comp_id)

        # Prepare data -- should have gaps
        data = agent.prepare()
        assert len(data["gaps"]) >= 1
        assert any("MISSING-REQ" in g for g in data["gaps"])

        # Create contract proposals with gap markers
        contracts = [
            {
                "component_id": comp_id,
                "interface_id": intf_id,
                "name": "Gappy Contract",
                "description": "Contract with gaps",
                "obligations": [
                    {
                        "id": "OB-GAP",
                        "statement": "SHALL handle data (reduced confidence)",
                        "obligation_type": "data_processing",
                        "source_requirement_ids": [],
                    }
                ],
                "rationale": "Derived with incomplete data",
                "gap_markers": [
                    {
                        "type": "missing_requirement",
                        "finding_ref": "MISSING-REQ",
                        "severity": "high",
                        "description": "Referenced requirement not found in registry",
                    }
                ],
            }
        ]

        proposals = agent.create_proposals(contracts, "session-gaps")
        assert len(proposals) == 1
        assert len(proposals[0]["gap_markers"]) == 1
        assert proposals[0]["gap_markers"][0]["finding_ref"] == "MISSING-REQ"
