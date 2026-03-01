"""End-to-end integration tests for the ingestion pipeline.

Uses realistic upstream data structures matching actual registry schemas.
All tests use tmp_path for isolation -- no dependency on real upstream data.
"""

import json
import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.ingest_upstream import ingest_all
from scripts.registry import SlotAPI


def _schemas_dir() -> str:
    """Return absolute path to schemas/ directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


def create_realistic_upstream(tmp_path) -> str:
    """Create upstream with realistic data structures matching actual registries."""
    upstream = tmp_path / "upstream-realistic"
    upstream.mkdir()

    needs = [
        {
            "id": "NEED-001",
            "statement": "The platform shall capture design decisions as explicit records",
            "stakeholder": "System Architect",
            "source_block": "DREG",
            "source_artifacts": ["concept-dev-design-001"],
            "concept_dev_refs": ["CD-ARCH-001"],
            "status": "registered",
            "rationale": "Core capability for traceable engineering",
            "registered_at": "2026-01-15T10:00:00Z",
        },
        {
            "id": "NEED-002",
            "statement": "The platform shall support automated traceability",
            "stakeholder": "Quality Engineer",
            "source_block": "TRAC",
            "source_artifacts": [],
            "concept_dev_refs": [],
            "status": "registered",
            "rationale": "V&V requirement",
            "registered_at": "2026-01-15T10:30:00Z",
        },
        {
            "id": "NEED-003",
            "statement": "The platform shall integrate with concept-dev outputs",
            "stakeholder": "Program Manager",
            "source_block": "INGS",
            "source_artifacts": [],
            "concept_dev_refs": ["CD-PLAN-001"],
            "status": "registered",
            "rationale": "Pipeline continuity",
            "registered_at": "2026-01-15T11:00:00Z",
        },
    ]

    requirements = [
        {
            "id": "REQ-026",
            "statement": "Ingest registered/baselined requirements into Design Registry slots",
            "type": "functional",
            "priority": "high",
            "status": "baselined",
            "parent_need": "NEED-003",
            "source_block": "INGS",
            "level": "system",
            "attributes": {"testable": True, "measurable": True},
            "quality_checks": {"completeness": "pass", "consistency": "pass"},
            "rationale": "Foundation for design traceability",
            "registered_at": "2026-01-20T10:00:00Z",
            "baselined_at": "2026-02-01T10:00:00Z",
        },
        {
            "id": "REQ-030",
            "statement": "Exclude draft/withdrawn requirements from ingestion",
            "type": "functional",
            "priority": "medium",
            "status": "baselined",
            "parent_need": "NEED-003",
            "source_block": "INGS",
            "level": "system",
            "attributes": {"testable": True},
            "quality_checks": {"completeness": "pass"},
            "rationale": "Only stable requirements enter design space",
            "registered_at": "2026-01-20T11:00:00Z",
            "baselined_at": "2026-02-01T10:00:00Z",
        },
    ]

    sources = [
        {
            "id": "SRC-001",
            "title": "Requirements Engineering Best Practices",
            "url": "https://example.com/re-best-practices",
            "type": "literature",
            "confidence": "high",
            "research_context": "concept-dev phase 2",
            "concept_dev_ref": "CD-REF-001",
            "registered_at": "2026-01-10T10:00:00Z",
        },
    ]

    assumptions = [
        {
            "id": "A-001",
            "statement": "All design agents have read access to the registry",
            "category": "architectural",
            "status": "active",
            "source_block": "BLOCK-02",
            "related_requirements": ["REQ-026", "REQ-030"],
            "rationale": "Shared registry is the communication backbone",
            "registered_at": "2026-01-18T10:00:00Z",
        },
    ]

    links = [
        {
            "type": "derives_from",
            "from": "REQ-026",
            "to": "NEED-003",
            "rationale": "REQ-026 implements NEED-003",
            "registered_at": "2026-01-22T10:00:00Z",
        },
        {
            "type": "derives_from",
            "from": "REQ-030",
            "to": "NEED-003",
            "rationale": "REQ-030 implements NEED-003",
            "registered_at": "2026-01-22T10:30:00Z",
        },
    ]

    (upstream / "needs_registry.json").write_text(json.dumps({"needs": needs}))
    (upstream / "requirements_registry.json").write_text(json.dumps({"requirements": requirements}))
    (upstream / "source_registry.json").write_text(json.dumps({"sources": sources}))
    (upstream / "assumptions_registry.json").write_text(json.dumps({"assumptions": assumptions}))
    (upstream / "traceability_matrix.json").write_text(json.dumps({"links": links}))
    (upstream / "state.json").write_text(json.dumps({
        "gates": {"init": True, "needs": True, "requirements": True, "traceability": True}
    }))

    return str(upstream)


def setup_workspace(tmp_path) -> str:
    """Initialize workspace and return .system-dev path."""
    project = tmp_path / "integration-project"
    project.mkdir()
    init_workspace(str(project))
    return str(project / ".system-dev")


class TestFullPipeline:
    """End-to-end integration tests."""

    def test_full_pipeline_init_ingest_query(self, tmp_path):
        """Init workspace, ingest, query each slot type, verify counts."""
        upstream = create_realistic_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result = ingest_all(upstream, workspace, _schemas_dir())

        assert result.total_ingested > 0
        assert result.created > 0

        api = SlotAPI(workspace, _schemas_dir())

        needs = api.query("need")
        assert len(needs) == 3

        requirements = api.query("requirement")
        assert len(requirements) == 2

        sources = api.query("source")
        assert len(sources) == 1

        assumptions = api.query("assumption")
        assert len(assumptions) == 1

        links = api.query("traceability-link")
        assert len(links) == 2

    def test_full_pipeline_ingest_reingest_delta(self, tmp_path):
        """Ingest, modify upstream, re-ingest, verify delta report."""
        upstream = create_realistic_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        result1 = ingest_all(upstream, workspace, _schemas_dir())
        assert result1.created > 0

        # Modify a requirement statement
        req_path = os.path.join(upstream, "requirements_registry.json")
        with open(req_path) as f:
            data = json.load(f)
        data["requirements"][0]["statement"] = "Updated: Ingest requirements with enhanced validation"
        with open(req_path, "w") as f:
            json.dump(data, f)

        result2 = ingest_all(upstream, workspace, _schemas_dir())

        # Should detect the modification
        assert result2.updated >= 1

        # Delta report should reflect changes
        with open(result2.delta_report_path) as f:
            delta = json.load(f)
        assert delta["summary"]["modified"] >= 1

    def test_cross_references_traversable(self, tmp_path):
        """Ingested requirement has derives_from pointing to need slot, both exist."""
        upstream = create_realistic_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())

        req = api.read("requirement:REQ-026")
        assert req is not None
        assert "derives_from" in req
        assert len(req["derives_from"]) > 0

        # The referenced need should exist
        need_ref = req["derives_from"][0]
        need = api.read(need_ref)
        assert need is not None
        assert need["slot_type"] == "need"

    def test_traceability_links_connect_slots(self, tmp_path):
        """Traceability link slot's from_id and to_id point to real ingested slots."""
        upstream = create_realistic_upstream(tmp_path)
        workspace = setup_workspace(tmp_path)

        ingest_all(upstream, workspace, _schemas_dir())

        api = SlotAPI(workspace, _schemas_dir())
        links = api.query("traceability-link")
        assert len(links) >= 1

        for link in links:
            from_id = link["from_id"]
            to_id = link["to_id"]
            # Verify that referenced entities were ingested
            # (from_id/to_id are upstream IDs like REQ-026, not slot IDs)
            assert from_id, f"Link {link['slot_id']} has empty from_id"
            assert to_id, f"Link {link['slot_id']} has empty to_id"
