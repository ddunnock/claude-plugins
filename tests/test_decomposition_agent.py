"""Tests for decomposition_agent.py -- structural decomposition data prep, gap detection, and proposals."""

import os
import time

import pytest

from scripts.decomposition_agent import (
    DecompositionAgent,
    check_stale_components,
    detect_requirement_gaps,
    prepare_requirement_data,
)
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI

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


def _ingest_requirement(api, req_id, description="A requirement", source_block="BLOCK-1",
                        gap_markers=None, upstream_status="active", parent_need="",
                        derives_from=None):
    """Helper to ingest a requirement slot."""
    content = {
        "upstream_id": req_id,
        "description": description,
        "requirement_type": "functional",
        "source_block": source_block,
        "parent_need": parent_need,
        "upstream_status": upstream_status,
        "gap_markers": gap_markers or [],
        "derives_from": derives_from or [],
        "provenance": {
            "source": "requirements-dev",
            "upstream_file": "requirements_registry.json",
            "ingested_at": "2026-01-01T00:00:00+00:00",
            "hash": "abc123",
        },
    }
    slot_id = f"requirement:{req_id}"
    return api.ingest(slot_id, "requirement", content)


def _ingest_need(api, need_id, description="A stakeholder need", stakeholder="Developer",
                 source_block="BLOCK-1"):
    """Helper to ingest a need slot."""
    content = {
        "upstream_id": need_id,
        "description": description,
        "stakeholder": stakeholder,
        "source_block": source_block,
        "provenance": {
            "source": "requirements-dev",
            "upstream_file": "needs_registry.json",
            "ingested_at": "2026-01-01T00:00:00+00:00",
            "hash": "def456",
        },
    }
    slot_id = f"need:{need_id}"
    return api.ingest(slot_id, "need", content)


# --- detect_requirement_gaps tests ---


class TestDetectRequirementGaps:
    def test_no_gaps_returns_severity_none(self, api):
        """No gaps returns severity 'none'."""
        reqs = [
            {"slot_id": "r1", "description": "desc", "source_block": "B1", "gap_markers": []},
            {"slot_id": "r2", "description": "desc", "source_block": "B2", "gap_markers": []},
        ]
        result = detect_requirement_gaps(reqs)
        assert result["severity"] == "none"
        assert result["gap_count"] == 0
        assert result["total_requirements"] == 2

    def test_missing_descriptions_detected(self, api):
        """Missing descriptions are detected and severity calculated."""
        reqs = [
            {"slot_id": "r1", "description": "", "source_block": "B1", "gap_markers": []},
            {"slot_id": "r2", "description": "valid", "source_block": "B2", "gap_markers": []},
            {"slot_id": "r3", "description": "valid", "source_block": "B3", "gap_markers": []},
            {"slot_id": "r4", "description": "valid", "source_block": "B4", "gap_markers": []},
            {"slot_id": "r5", "description": "valid", "source_block": "B5", "gap_markers": []},
            {"slot_id": "r6", "description": "valid", "source_block": "B6", "gap_markers": []},
        ]
        result = detect_requirement_gaps(reqs)
        assert result["missing_descriptions"] == ["r1"]
        # 1/6 = 16.7% < 20% threshold, so severity is "medium"
        assert result["severity"] == "medium"
        assert result["gap_count"] == 1

    def test_high_severity_when_over_20_percent_gaps(self):
        """High severity when > 20% of requirements have gaps."""
        reqs = [
            {"slot_id": f"r{i}", "description": "", "source_block": "", "gap_markers": []}
            for i in range(5)
        ] + [
            {"slot_id": f"r{i}", "description": "ok", "source_block": "B1", "gap_markers": []}
            for i in range(5, 10)
        ]
        # 5 missing descriptions out of 10 = 50% > 20% = high
        result = detect_requirement_gaps(reqs)
        assert result["severity"] == "high"
        assert result["gap_count"] == 5

    def test_existing_gap_markers_counted_as_incomplete(self):
        """Requirements with existing gap_markers are counted as incomplete."""
        reqs = [
            {"slot_id": "r1", "description": "ok", "source_block": "B1",
             "gap_markers": [{"type": "missing_data", "finding_ref": "GAP-1",
                              "severity": "medium", "description": "test"}]},
            {"slot_id": "r2", "description": "ok", "source_block": "B2", "gap_markers": []},
            {"slot_id": "r3", "description": "ok", "source_block": "B3", "gap_markers": []},
            {"slot_id": "r4", "description": "ok", "source_block": "B4", "gap_markers": []},
            {"slot_id": "r5", "description": "ok", "source_block": "B5", "gap_markers": []},
            {"slot_id": "r6", "description": "ok", "source_block": "B6", "gap_markers": []},
        ]
        result = detect_requirement_gaps(reqs)
        assert result["incomplete_slots"] == ["r1"]
        assert result["gap_count"] == 1
        # 1/6 = 16.7% < 20% threshold, so severity is "medium"
        assert result["severity"] == "medium"

    def test_empty_requirements_list(self):
        """Empty requirements list returns severity 'none'."""
        result = detect_requirement_gaps([])
        assert result["total_requirements"] == 0
        assert result["severity"] == "none"
        assert result["gap_count"] == 0


# --- check_stale_components tests ---


class TestCheckStaleComponents:
    def test_returns_empty_when_no_accepted_components(self, api):
        """Returns empty list when no accepted components exist."""
        result = check_stale_components(api)
        assert result == []

    def test_detects_stale_when_requirement_updated_after_component(self, api):
        """Detects component as stale when a referenced requirement has newer updated_at."""
        # Ingest a requirement
        _ingest_requirement(api, "REQ-001", description="Auth requirement")
        req_slot = api.read("requirement:REQ-001")

        # Create a component referencing it (via approval gate accept simulation)
        comp_content = {
            "name": "Auth Service",
            "description": "Handles authentication",
            "status": "approved",
            "parent_requirements": ["requirement:REQ-001"],
            "rationale": "Groups auth requirements",
        }
        comp_result = api.create("component", comp_content)
        comp_id = comp_result["slot_id"]

        # Now update the requirement (simulating re-ingestion with changes)
        updated_content = dict(req_slot)
        updated_content["description"] = "Updated auth requirement with new details"
        api.update("requirement:REQ-001", updated_content, expected_version=1)

        # Check for stale components
        stale = check_stale_components(api)
        assert len(stale) == 1
        assert stale[0]["component_slot_id"] == comp_id
        assert "requirement:REQ-001" in stale[0]["affected_requirement_ids"]

    def test_detects_stale_when_requirement_has_new_gap_markers(self, api):
        """Detects component as stale when a referenced requirement has new gap_markers."""
        _ingest_requirement(api, "REQ-002", description="Data requirement")

        # Create component
        comp_content = {
            "name": "Data Service",
            "description": "Handles data",
            "status": "approved",
            "parent_requirements": ["requirement:REQ-002"],
            "rationale": "Groups data requirements",
        }
        api.create("component", comp_content)

        # Update requirement with gap markers
        req_slot = api.read("requirement:REQ-002")
        updated = dict(req_slot)
        updated["gap_markers"] = [
            {"type": "missing_data", "finding_ref": "GAP-1",
             "severity": "medium", "description": "Missing field"}
        ]
        api.update("requirement:REQ-002", updated, expected_version=req_slot["version"])

        stale = check_stale_components(api)
        assert len(stale) == 1
        assert "gap_markers" in stale[0]["stale_reason"]

    def test_does_not_flag_when_requirements_unchanged(self, api):
        """Does not flag component when referenced requirements are unchanged."""
        _ingest_requirement(api, "REQ-003", description="Stable requirement")

        # Read the requirement to get its updated_at
        req_slot = api.read("requirement:REQ-003")

        # Create component AFTER the requirement (so component is newer)
        comp_content = {
            "name": "Stable Service",
            "description": "Stable",
            "status": "approved",
            "parent_requirements": ["requirement:REQ-003"],
            "rationale": "Groups stable requirements",
        }
        api.create("component", comp_content)

        stale = check_stale_components(api)
        assert len(stale) == 0


# --- prepare_requirement_data tests ---


class TestPrepareRequirementData:
    def test_extracts_fields_from_requirement_slots(self, api):
        """Extracts the required fields from requirement slots."""
        _ingest_requirement(api, "REQ-010", description="Test requirement",
                            source_block="AUTH", parent_need="NEED-001")

        data = prepare_requirement_data(api)
        assert len(data["requirements"]) == 1
        req = data["requirements"][0]
        assert req["slot_id"] == "requirement:REQ-010"
        assert req["upstream_id"] == "REQ-010"
        assert req["description"] == "Test requirement"
        assert req["source_block"] == "AUTH"
        assert req["parent_need"] == "NEED-001"

    def test_groups_by_source_block(self, api):
        """Groups requirements by source_block."""
        _ingest_requirement(api, "REQ-020", source_block="AUTH")
        _ingest_requirement(api, "REQ-021", source_block="AUTH")
        _ingest_requirement(api, "REQ-022", source_block="DATA")

        data = prepare_requirement_data(api)
        by_block = data["by_source_block"]
        assert len(by_block["AUTH"]) == 2
        assert len(by_block["DATA"]) == 1

    def test_includes_needs_for_context(self, api):
        """Includes need slots for context."""
        _ingest_need(api, "NEED-001", description="Users need auth",
                     stakeholder="End User")

        data = prepare_requirement_data(api)
        assert len(data["needs"]) == 1
        need = data["needs"][0]
        assert need["slot_id"] == "need:NEED-001"
        assert need["description"] == "Users need auth"
        assert need["stakeholder"] == "End User"

    def test_gap_report_included(self, api):
        """Gap report is included in prepared data."""
        _ingest_requirement(api, "REQ-030", description="Complete req")

        data = prepare_requirement_data(api)
        assert "gap_report" in data
        assert data["gap_report"]["total_requirements"] == 1


# --- DecompositionAgent.create_proposals tests ---


class TestCreateProposals:
    def _make_agent(self, api):
        return DecompositionAgent(api, SCHEMAS_DIR)

    def test_creates_component_proposal_slots_with_correct_schema(self, api):
        """Creates component-proposal slots with correct schema."""
        agent = self._make_agent(api)
        components = [
            {
                "name": "Auth Service",
                "description": "Handles authentication and authorization",
                "requirement_ids": ["requirement:REQ-001", "requirement:REQ-002"],
                "rationale": {
                    "narrative": "Groups authentication concerns",
                    "grouping_criteria": ["functional_coherence"],
                    "evidence": [{"req_id": "REQ-001", "relevance": "direct"}],
                },
                "relationships": [],
                "gap_markers": [],
            }
        ]

        proposals = agent.create_proposals(components, "session-001")
        assert len(proposals) == 1
        p = proposals[0]
        assert p["slot_type"] == "component-proposal"
        assert p["name"] == "Auth Service"
        assert p["status"] == "proposed"
        assert p["version"] == 1

    def test_all_proposals_share_session_id(self, api):
        """All proposals share the same session_id."""
        agent = self._make_agent(api)
        components = [
            {"name": f"Service {i}", "description": f"Desc {i}",
             "requirement_ids": [], "rationale": {"narrative": "test"},
             "relationships": [], "gap_markers": []}
            for i in range(3)
        ]

        proposals = agent.create_proposals(components, "session-xyz")
        for p in proposals:
            assert p["proposal_session_id"] == "session-xyz"

    def test_requirement_ids_and_rationale_preserved(self, api):
        """Requirement IDs and rationale are preserved (Pitfall 5)."""
        agent = self._make_agent(api)
        components = [
            {
                "name": "Data Pipeline",
                "description": "Processes data",
                "requirement_ids": ["requirement:REQ-100", "requirement:REQ-101"],
                "rationale": {
                    "narrative": "Data processing pipeline groups ETL requirements",
                    "grouping_criteria": ["data_affinity", "pipeline_stage"],
                    "evidence": [
                        {"req_id": "REQ-100", "relevance": "primary ETL requirement"},
                        {"req_id": "REQ-101", "relevance": "validation step"},
                    ],
                },
                "relationships": [],
                "gap_markers": [],
            }
        ]

        proposals = agent.create_proposals(components, "session-001")
        p = proposals[0]
        assert p["requirement_ids"] == ["requirement:REQ-100", "requirement:REQ-101"]
        assert p["rationale"]["narrative"] == "Data processing pipeline groups ETL requirements"
        assert len(p["rationale"]["evidence"]) == 2
        assert p["rationale"]["evidence"][0]["req_id"] == "REQ-100"

    def test_gap_markers_from_requirements_inherited(self, api):
        """Gap markers from requirements are inherited into proposals."""
        agent = self._make_agent(api)
        gap = {
            "type": "missing_data",
            "finding_ref": "GAP-1",
            "severity": "medium",
            "description": "Missing upstream data",
        }
        components = [
            {
                "name": "Gappy Service",
                "description": "Has gaps",
                "requirement_ids": [],
                "rationale": {"narrative": "test"},
                "relationships": [],
                "gap_markers": [gap],
            }
        ]

        proposals = agent.create_proposals(components, "session-001")
        assert len(proposals[0]["gap_markers"]) == 1
        assert proposals[0]["gap_markers"][0]["finding_ref"] == "GAP-1"

    def test_string_rationale_converted_to_dict(self, api):
        """String rationale is auto-converted to dict with narrative key."""
        agent = self._make_agent(api)
        components = [
            {
                "name": "Simple Service",
                "description": "Simple",
                "requirement_ids": [],
                "rationale": "Just a string narrative",
                "relationships": [],
                "gap_markers": [],
            }
        ]

        proposals = agent.create_proposals(components, "session-001")
        assert proposals[0]["rationale"]["narrative"] == "Just a string narrative"


# --- format_coverage_summary tests ---


class TestFormatCoverageSummary:
    def test_correct_mapping_count(self, api):
        """Coverage summary shows correct mapped/unmapped counts."""
        agent = DecompositionAgent(api, SCHEMAS_DIR)
        proposals = [
            {"requirement_ids": ["req1", "req2"]},
            {"requirement_ids": ["req3"]},
        ]
        summary = agent.format_coverage_summary(proposals, 5)
        assert "3/5 requirements mapped" in summary
        assert "2 unmapped" in summary

    def test_all_mapped(self, api):
        """When all requirements are mapped, no unmapped shown."""
        agent = DecompositionAgent(api, SCHEMAS_DIR)
        proposals = [
            {"requirement_ids": ["req1", "req2", "req3"]},
        ]
        summary = agent.format_coverage_summary(proposals, 3)
        assert "3/3 requirements mapped" in summary
        assert "unmapped" not in summary

    def test_deduplication(self, api):
        """Duplicate requirement IDs across proposals are deduplicated."""
        agent = DecompositionAgent(api, SCHEMAS_DIR)
        proposals = [
            {"requirement_ids": ["req1", "req2"]},
            {"requirement_ids": ["req2", "req3"]},  # req2 appears in both
        ]
        summary = agent.format_coverage_summary(proposals, 4)
        assert "3/4 requirements mapped" in summary  # 3 unique, not 4


# --- format_proposal_narrative tests ---


class TestFormatProposalNarrative:
    def test_narrative_blocks_format_with_summary_first(self, api):
        """Narrative blocks use summary-first density format."""
        agent = DecompositionAgent(api, SCHEMAS_DIR)
        proposals = [
            {
                "name": "Auth Service",
                "description": "Handles authentication",
                "requirement_ids": ["req1", "req2"],
                "rationale": {
                    "narrative": "Groups auth-related requirements for cohesive handling.",
                    "evidence": [
                        {"req_id": "REQ-001", "relevance": "core auth"},
                        {"req_id": "REQ-002", "relevance": "session management"},
                    ],
                },
            }
        ]
        output = agent.format_proposal_narrative(proposals)
        assert "## Auth Service" in output
        assert "Handles authentication" in output
        assert "Requirements: 2" in output
        assert "Groups auth-related" in output
        assert "REQ-001: core auth" in output
        assert "REQ-002: session management" in output

    def test_multiple_proposals_separated_by_dividers(self, api):
        """Multiple proposals are separated by dividers."""
        agent = DecompositionAgent(api, SCHEMAS_DIR)
        proposals = [
            {"name": "Service A", "description": "A", "requirement_ids": [],
             "rationale": {"narrative": "Test A"}},
            {"name": "Service B", "description": "B", "requirement_ids": [],
             "rationale": {"narrative": "Test B"}},
        ]
        output = agent.format_proposal_narrative(proposals)
        assert "---" in output
        assert "## Service A" in output
        assert "## Service B" in output


# --- Performance test ---


class TestPerformance:
    def test_200_requirements_prepare_under_2_seconds(self, api):
        """200 requirements prepare_requirement_data in < 2 seconds."""
        # Ingest 200 requirements
        for i in range(200):
            _ingest_requirement(
                api, f"PERF-{i:03d}",
                description=f"Performance test requirement {i}",
                source_block=f"BLOCK-{i % 5}",
            )

        start = time.time()
        data = prepare_requirement_data(api)
        elapsed = time.time() - start

        assert len(data["requirements"]) == 200
        assert len(data["by_source_block"]) == 5
        assert elapsed < 2.0, f"Took {elapsed:.2f}s, expected < 2s"
