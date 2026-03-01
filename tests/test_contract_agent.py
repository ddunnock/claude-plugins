"""Tests for contract_agent.py -- behavioral contract data prep, V&V assignment, and proposals."""

import os
import time

import pytest

from scripts.contract_agent import (
    ContractAgent,
    assign_vv_methods,
    check_stale_contracts,
    load_vv_rules,
    prepare_obligation_data,
)
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI

# Paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SCHEMAS_DIR = os.path.join(PROJECT_ROOT, "schemas")
VV_RULES_PATH = os.path.join(PROJECT_ROOT, "data", "vv-rules.json")


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
def vv_rules():
    """Load the real vv-rules.json config."""
    return load_vv_rules(VV_RULES_PATH)


def _create_approved_component(api, name="Test Component", req_ids=None):
    """Helper to create an approved component slot."""
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
    """Helper to create an approved interface slot."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "source_component": source_comp,
        "target_component": target_comp,
        "direction": "unidirectional",
        "data_format_schema": {},
        "error_categories": [],
    }
    result = api.create("interface", content)
    return result["slot_id"]


def _create_approved_contract(api, name="Test Contract", comp_id="", intf_id=""):
    """Helper to create an approved contract slot."""
    content = {
        "name": name,
        "description": f"{name} description",
        "status": "approved",
        "component_id": comp_id,
        "interface_id": intf_id,
        "obligations": [
            {
                "id": "OB-001",
                "statement": "SHALL process data",
                "obligation_type": "data_processing",
                "source_requirement_ids": ["requirement:REQ-001"],
            }
        ],
        "vv_assignments": [
            {
                "obligation_id": "OB-001",
                "method": "test",
                "rationale": "Default for data_processing",
            }
        ],
        "rationale": {"narrative": "Test contract"},
    }
    result = api.create("contract", content)
    return result["slot_id"]


def _ingest_requirement(api, req_id, description="A requirement", req_type="functional"):
    """Helper to ingest a requirement slot."""
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


# --- load_vv_rules tests ---


class TestLoadVvRules:
    def test_loads_valid_rules(self):
        """Loads vv-rules.json successfully."""
        rules = load_vv_rules(VV_RULES_PATH)
        assert "default_methods" in rules
        assert "override_policy" in rules
        assert rules["override_policy"] == "ai_with_rationale"

    def test_raises_on_missing_file(self):
        """Raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_vv_rules("/nonexistent/path/vv-rules.json")


# --- assign_vv_methods tests ---


class TestAssignVvMethods:
    def test_uses_defaults_for_known_types(self, vv_rules):
        """data_processing obligation gets 'test' method from defaults."""
        obligations = [
            {"id": "OB-1", "obligation_type": "data_processing"},
        ]
        assignments = assign_vv_methods(obligations, vv_rules)
        assert len(assignments) == 1
        assert assignments[0]["obligation_id"] == "OB-1"
        assert assignments[0]["method"] == "test"
        assert assignments[0]["is_override"] is False
        assert "Default for data_processing" in assignments[0]["rationale"]

    def test_unknown_type_defaults_to_test(self, vv_rules):
        """Unknown obligation_type gets 'test' fallback."""
        obligations = [
            {"id": "OB-2", "obligation_type": "unknown_category"},
        ]
        assignments = assign_vv_methods(obligations, vv_rules)
        assert assignments[0]["method"] == "test"
        assert "No default rule for unknown_category" in assignments[0]["rationale"]
        assert assignments[0]["is_override"] is False

    def test_all_default_types_covered(self, vv_rules):
        """Each of the 8 default types produces the correct method."""
        expected = {
            "data_processing": "test",
            "state_management": "test",
            "error_handling": "test",
            "interface_protocol": "demonstration",
            "configuration": "inspection",
            "logging": "inspection",
            "algorithmic": "analysis",
            "performance": "analysis",
        }
        obligations = [
            {"id": f"OB-{i}", "obligation_type": otype}
            for i, otype in enumerate(expected.keys())
        ]
        assignments = assign_vv_methods(obligations, vv_rules)
        assert len(assignments) == 8
        for assignment in assignments:
            ob_type = next(
                o["obligation_type"]
                for o in obligations
                if o["id"] == assignment["obligation_id"]
            )
            assert assignment["method"] == expected[ob_type], (
                f"{ob_type} should map to {expected[ob_type]}, got {assignment['method']}"
            )


# --- prepare_obligation_data tests ---


class TestPrepareObligationData:
    def test_groups_by_component(self, api):
        """2 components with different requirements produce separate groupings."""
        _ingest_requirement(api, "REQ-A1", description="Auth req 1")
        _ingest_requirement(api, "REQ-A2", description="Auth req 2")
        _ingest_requirement(api, "REQ-B1", description="Data req 1")

        comp_a = _create_approved_component(
            api, "Auth Service", ["requirement:REQ-A1", "requirement:REQ-A2"]
        )
        comp_b = _create_approved_component(
            api, "Data Service", ["requirement:REQ-B1"]
        )

        data = prepare_obligation_data(api)
        assert data["total_components"] == 2

        comp_names = [c["component_name"] for c in data["components"]]
        assert "Auth Service" in comp_names
        assert "Data Service" in comp_names

        auth_comp = next(c for c in data["components"] if c["component_name"] == "Auth Service")
        assert len(auth_comp["requirements"]) == 2

        data_comp = next(c for c in data["components"] if c["component_name"] == "Data Service")
        assert len(data_comp["requirements"]) == 1

    def test_includes_interfaces(self, api):
        """Approved interfaces appear in component data."""
        comp_id = _create_approved_component(api, "Comp A")
        intf_id = _create_approved_interface(api, "API Endpoint", source_comp=comp_id)

        data = prepare_obligation_data(api)
        assert data["total_interfaces"] == 1
        comp = data["components"][0]
        assert len(comp["interfaces"]) == 1
        assert comp["interfaces"][0]["name"] == "API Endpoint"

    def test_empty_when_no_approved_components(self, api):
        """Returns empty data when no approved components exist."""
        data = prepare_obligation_data(api)
        assert data["total_components"] == 0
        assert data["components"] == []

    def test_gap_markers_for_missing_requirements(self, api):
        """Components referencing missing requirements get gap markers."""
        _create_approved_component(api, "Orphan Comp", ["requirement:MISSING-REQ"])

        data = prepare_obligation_data(api)
        assert len(data["gaps"]) >= 1
        assert any("MISSING-REQ" in g for g in data["gaps"])


# --- ContractAgent.create_proposals tests ---


class TestCreateProposals:
    def _make_agent(self, api):
        return ContractAgent(api, SCHEMAS_DIR, VV_RULES_PATH)

    def test_bundles_vv_assignments(self, api):
        """Created contract-proposal has both obligations and vv_assignments."""
        agent = self._make_agent(api)
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": "Data Processing Contract",
                "description": "Handles data processing obligations",
                "obligations": [
                    {
                        "id": "OB-001",
                        "statement": "SHALL process input data within 500ms",
                        "obligation_type": "data_processing",
                        "source_requirement_ids": ["requirement:REQ-001"],
                    }
                ],
                "rationale": "Derived from data processing requirements",
            }
        ]

        proposals = agent.create_proposals(contracts, "session-001")
        assert len(proposals) == 1
        p = proposals[0]
        assert p["slot_type"] == "contract-proposal"
        assert len(p["obligations"]) == 1
        assert len(p["vv_assignments"]) == 1
        assert p["vv_assignments"][0]["method"] == "test"
        assert p["vv_assignments"][0]["obligation_id"] == "OB-001"

    def test_applies_ai_overrides(self, api):
        """Claude override replaces default V&V for specific obligation."""
        agent = self._make_agent(api)
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": "Override Contract",
                "description": "Tests V&V override",
                "obligations": [
                    {
                        "id": "OB-010",
                        "statement": "SHALL validate config format",
                        "obligation_type": "configuration",
                        "source_requirement_ids": ["requirement:REQ-010"],
                    }
                ],
                "rationale": "Config validation contract",
                "vv_overrides": [
                    {
                        "obligation_id": "OB-010",
                        "method": "test",
                        "rationale": "Config validation is better verified via automated test than inspection",
                    }
                ],
            }
        ]

        proposals = agent.create_proposals(contracts, "session-002")
        p = proposals[0]
        vv = p["vv_assignments"][0]
        # Default for configuration is "inspection", but override changes to "test"
        assert vv["method"] == "test"
        assert vv["is_override"] is True
        assert "automated test" in vv["rationale"]

    def test_string_rationale_converted(self, api):
        """String rationale is auto-converted to dict with narrative key."""
        agent = self._make_agent(api)
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": "Simple Contract",
                "description": "Simple",
                "obligations": [],
                "rationale": "Just a string narrative",
            }
        ]

        proposals = agent.create_proposals(contracts, "session-003")
        assert proposals[0]["rationale"]["narrative"] == "Just a string narrative"

    def test_requirement_ids_collected_from_obligations(self, api):
        """Requirement IDs are collected from obligation source_requirement_ids."""
        agent = self._make_agent(api)
        contracts = [
            {
                "component_id": "comp-fake",
                "interface_id": "intf-fake",
                "name": "Multi-req Contract",
                "description": "Multiple requirements",
                "obligations": [
                    {
                        "id": "OB-A",
                        "statement": "SHALL do A",
                        "obligation_type": "data_processing",
                        "source_requirement_ids": ["requirement:REQ-001", "requirement:REQ-002"],
                    },
                    {
                        "id": "OB-B",
                        "statement": "SHALL do B",
                        "obligation_type": "error_handling",
                        "source_requirement_ids": ["requirement:REQ-002", "requirement:REQ-003"],
                    },
                ],
                "rationale": "Multi-req",
            }
        ]

        proposals = agent.create_proposals(contracts, "session-004")
        req_ids = proposals[0]["requirement_ids"]
        # REQ-002 appears in both obligations but should be deduplicated
        assert req_ids == ["requirement:REQ-001", "requirement:REQ-002", "requirement:REQ-003"]


# --- check_stale_contracts tests ---


class TestCheckStaleContracts:
    def test_detects_changed_interface(self, api):
        """Contract with older updated_at than interface is flagged stale."""
        comp_id = _create_approved_component(api, "Comp")
        intf_id = _create_approved_interface(api, "API", source_comp=comp_id)
        contract_id = _create_approved_contract(api, "My Contract", comp_id, intf_id)

        # Update the interface (making it newer than the contract)
        intf = api.read(intf_id)
        updated_intf = dict(intf)
        updated_intf["description"] = "Updated interface description"
        api.update(intf_id, updated_intf, expected_version=intf["version"])

        stale = check_stale_contracts(api)
        assert len(stale) == 1
        assert stale[0]["slot_id"] == contract_id
        assert stale[0]["interface_id"] == intf_id
        assert "updated after contract" in stale[0]["reason"]

    def test_no_cascade_back(self, api):
        """Contract change does NOT flag interface as stale (one-level only)."""
        comp_id = _create_approved_component(api, "Comp")
        intf_id = _create_approved_interface(api, "API", source_comp=comp_id)
        contract_id = _create_approved_contract(api, "My Contract", comp_id, intf_id)

        # Update the contract (making it newer than the interface)
        contract = api.read(contract_id)
        updated_contract = dict(contract)
        updated_contract["description"] = "Updated contract"
        api.update(contract_id, updated_contract, expected_version=contract["version"])

        # check_stale_contracts only checks interface->contract direction
        stale = check_stale_contracts(api)
        assert len(stale) == 0

    def test_no_stale_when_contract_is_newer(self, api):
        """No stale flag when contract is newer than interface."""
        comp_id = _create_approved_component(api, "Comp")
        intf_id = _create_approved_interface(api, "API", source_comp=comp_id)

        # Create contract AFTER interface -- contract should be newer
        _create_approved_contract(api, "Fresh Contract", comp_id, intf_id)

        stale = check_stale_contracts(api)
        assert len(stale) == 0

    def test_returns_empty_when_no_contracts(self, api):
        """Returns empty list when no approved contracts exist."""
        stale = check_stale_contracts(api)
        assert stale == []


# --- Performance test ---


class TestPerformance:
    def test_assign_vv_100_obligations(self, vv_rules):
        """100 obligations V&V assignment runs under 0.5 seconds."""
        obligations = [
            {"id": f"OB-{i:03d}", "obligation_type": "data_processing"}
            for i in range(100)
        ]

        start = time.time()
        assignments = assign_vv_methods(obligations, vv_rules)
        elapsed = time.time() - start

        assert len(assignments) == 100
        assert elapsed < 0.5, f"Took {elapsed:.3f}s, expected < 0.5s"


# --- format_preparation_summary tests ---


class TestFormatPreparationSummary:
    def test_summary_includes_counts(self, api):
        """Summary includes component, interface, and requirement counts."""
        agent = ContractAgent(api, SCHEMAS_DIR, VV_RULES_PATH)
        data = {
            "total_components": 3,
            "total_interfaces": 5,
            "total_requirements": 12,
            "components": [],
            "gaps": [],
        }
        summary = agent.format_preparation_summary(data)
        assert "3 approved" in summary
        assert "5 approved" in summary
        assert "12 mapped" in summary
