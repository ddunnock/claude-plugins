"""Integration tests for the requirements pipeline.

Tests owned by section-07 (requirements command): full pipeline flows.
Tests owned by section-08 (status/resume): TBD.
Tests owned by section-09 (deliverables): TBD.
"""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import needs_tracker
import quality_rules
import requirement_tracker
import traceability
import update_state


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pipeline_workspace(tmp_path):
    """Workspace with init+needs gates passed and 2 approved needs."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    state = {
        "session_id": "integ-test",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "needs",
        "gates": {"init": True, "needs": True, "requirements": False, "deliver": False},
        "blocks": {"auth": {"name": "auth", "description": "Authentication block"}},
        "progress": {
            "current_block": None,
            "current_type_pass": None,
            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
            "requirements_in_draft": [],
        },
        "counts": {
            "needs_total": 2,
            "needs_approved": 2,
            "needs_deferred": 0,
            "requirements_total": 0,
            "requirements_registered": 0,
            "requirements_baselined": 0,
            "requirements_withdrawn": 0,
            "tbd_open": 0,
            "tbr_open": 0,
        },
        "traceability": {"links_total": 0, "coverage_pct": 0.0},
        "decomposition": {"levels": {}, "max_level": 3},
        "artifacts": {},
    }
    (ws / "state.json").write_text(json.dumps(state, indent=2))

    needs_reg = {
        "schema_version": "1.0.0",
        "needs": [
            {
                "id": "NEED-001",
                "statement": "The operator needs to authenticate via secure credentials",
                "stakeholder": "Operator",
                "status": "approved",
                "source_block": "auth",
                "source_artifacts": [],
                "concept_dev_refs": {"sources": [], "assumptions": []},
                "rationale": None,
                "registered_at": "2025-01-01T00:00:00+00:00",
            },
            {
                "id": "NEED-002",
                "statement": "The operator needs to reset their password without admin help",
                "stakeholder": "Operator",
                "status": "approved",
                "source_block": "auth",
                "source_artifacts": [],
                "concept_dev_refs": {"sources": [], "assumptions": []},
                "rationale": None,
                "registered_at": "2025-01-01T00:00:00+00:00",
            },
        ],
    }
    (ws / "needs_registry.json").write_text(json.dumps(needs_reg, indent=2))

    reqs_reg = {"schema_version": "1.0.0", "requirements": []}
    (ws / "requirements_registry.json").write_text(json.dumps(reqs_reg, indent=2))

    trace_reg = {"schema_version": "1.0.0", "links": []}
    (ws / "traceability_registry.json").write_text(json.dumps(trace_reg, indent=2))

    return ws


# ---------------------------------------------------------------------------
# Section 07: Full pipeline tests
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """Verify need -> requirement -> quality check -> register -> trace -> coverage."""

    def test_full_pipeline_need_to_traced_requirement(self, pipeline_workspace):
        """Complete flow: quality check -> add -> register -> trace -> coverage."""
        ws = str(pipeline_workspace)

        # 1. Quality check on a clean requirement statement
        statement = "The system shall authenticate users via username and password credentials"
        violations = quality_rules.check_requirement(statement)
        assert len(violations) == 0, f"Unexpected violations: {[v.rule_id for v in violations]}"

        # 2. Add requirement (draft)
        req_id = requirement_tracker.add_requirement(
            ws, statement, "functional", "high", "auth", level=0,
        )
        assert req_id.startswith("REQ-")

        # Verify draft status
        reg = requirement_tracker._load_registry(ws)
        req = next(r for r in reg["requirements"] if r["id"] == req_id)
        assert req["status"] == "draft"

        # 3. Register (transition to registered)
        requirement_tracker.register_requirement(ws, req_id, "NEED-001")
        reg = requirement_tracker._load_registry(ws)
        req = next(r for r in reg["requirements"] if r["id"] == req_id)
        assert req["status"] == "registered"
        assert req["parent_need"] == "NEED-001"

        # 4. Create traceability link
        traceability.link(ws, req_id, "NEED-001", "derives_from", "requirement")

        # 5. Check coverage
        report = traceability.coverage_report(ws)
        assert report["coverage_pct"] > 0
        assert report["needs_covered"] >= 1

    def test_pipeline_quality_violation_then_resolve(self, pipeline_workspace):
        """Violation blocks registration; resolution allows it."""
        ws = str(pipeline_workspace)

        # 1. Check a statement with ambiguous language (R7 - "appropriate")
        bad_statement = "The system shall provide appropriate handling of errors"
        violations = quality_rules.check_requirement(bad_statement)
        assert len(violations) > 0, "Expected violations for ambiguous language"
        rule_ids = {v.rule_id for v in violations}
        assert "R7" in rule_ids, f"Expected R7 violation, got: {rule_ids}"

        # 2. Check a clean replacement
        good_statement = "The system shall return structured JSON error responses with HTTP status codes"
        violations = quality_rules.check_requirement(good_statement)
        assert len(violations) == 0, f"Unexpected violations: {[v.rule_id for v in violations]}"

        # 3. Proceed with registration using the clean statement
        req_id = requirement_tracker.add_requirement(
            ws, good_statement, "functional", "high", "auth", level=0,
        )
        requirement_tracker.register_requirement(ws, req_id, "NEED-001")

        reg = requirement_tracker._load_registry(ws)
        req = next(r for r in reg["requirements"] if r["id"] == req_id)
        assert req["status"] == "registered"

    def test_pipeline_tbd_tracking(self, pipeline_workspace):
        """TBD values are tracked through registration and reflected in counts."""
        ws = str(pipeline_workspace)

        # 1. Add requirement
        statement = "The system shall respond to authentication requests within TBD milliseconds"
        req_id = requirement_tracker.add_requirement(
            ws, statement, "performance", "high", "auth", level=0,
        )

        # 2. Set TBD field on the requirement
        requirement_tracker.update_requirement(
            ws, req_id,
            tbd_tbr={"tbd": "Response time target pending load testing", "tbr": None},
        )

        # 3. Register
        requirement_tracker.register_requirement(ws, req_id, "NEED-001")

        # 4. Sync counts
        update_state.sync_counts(ws)

        # 5. Verify state reflects TBD
        state = json.loads((pipeline_workspace / "state.json").read_text())
        assert state["counts"]["tbd_open"] >= 1


class TestSyncCountsRegression:
    """Regression tests for sync_counts with dict-wrapped registries."""

    def test_sync_counts_handles_dict_wrapped_registries(self, pipeline_workspace):
        """sync_counts correctly extracts inner lists from registry dicts."""
        ws = str(pipeline_workspace)

        # Add a requirement and register it
        req_id = requirement_tracker.add_requirement(
            ws, "The system shall authenticate users", "functional", "high", "auth",
        )
        requirement_tracker.register_requirement(ws, req_id, "NEED-001")

        # Run sync_counts (this is what previously failed with dict-wrapped registries)
        update_state.sync_counts(ws)

        state = json.loads((pipeline_workspace / "state.json").read_text())
        assert state["counts"]["needs_total"] == 2
        assert state["counts"]["needs_approved"] == 2
        assert state["counts"]["requirements_total"] == 1
        assert state["counts"]["requirements_registered"] == 1

    def test_update_requirement_rejects_unknown_fields(self, pipeline_workspace):
        """update_requirement raises ValueError for unknown field names."""
        ws = str(pipeline_workspace)
        req_id = requirement_tracker.add_requirement(
            ws, "The system shall validate inputs", "functional", "high", "auth",
        )
        with pytest.raises(ValueError, match="Unknown field"):
            requirement_tracker.update_requirement(ws, req_id, nonexistent_field="value")


class TestMeteredInteractionState:
    """Verify state tracking for metered interaction flow."""

    def test_progress_tracking_after_registration(self, pipeline_workspace):
        """After registering requirements, state.json progress reflects position."""
        ws = str(pipeline_workspace)

        # Set progress tracking fields
        update_state.update_field(ws, "progress.current_block", "auth")
        update_state.update_field(ws, "progress.current_type_pass", "functional")

        # Add and register 2 requirements
        for stmt in (
            "The system shall validate user credentials against the identity store",
            "The system shall lock accounts after 5 consecutive failed login attempts",
        ):
            req_id = requirement_tracker.add_requirement(
                ws, stmt, "functional", "high", "auth",
            )
            requirement_tracker.register_requirement(ws, req_id, "NEED-001")

        # Sync and check
        update_state.sync_counts(ws)
        state = json.loads((pipeline_workspace / "state.json").read_text())

        assert state["progress"]["current_block"] == "auth"
        assert state["progress"]["current_type_pass"] == "functional"
        assert state["counts"]["requirements_registered"] == 2
        assert state["counts"]["requirements_total"] == 2

    def test_type_pass_transition(self, pipeline_workspace):
        """Current type pass updates correctly when transitioning."""
        ws = str(pipeline_workspace)

        # Start at functional
        update_state.update_field(ws, "progress.current_block", "auth")
        update_state.update_field(ws, "progress.current_type_pass", "functional")

        # Transition to performance
        update_state.update_field(ws, "progress.current_type_pass", "performance")

        state = json.loads((pipeline_workspace / "state.json").read_text())
        assert state["progress"]["current_type_pass"] == "performance"

    def test_requirements_in_draft_tracking(self, pipeline_workspace):
        """Draft requirement IDs are tracked in state for session resume."""
        ws = str(pipeline_workspace)

        # Add a requirement (stays draft)
        req_id = requirement_tracker.add_requirement(
            ws,
            "The system shall issue JWT tokens upon successful authentication",
            "functional", "high", "auth",
        )

        # Track draft in progress
        update_state.update_field(
            ws, "progress.requirements_in_draft", json.dumps([req_id]),
        )

        state = json.loads((pipeline_workspace / "state.json").read_text())
        drafts = state["progress"]["requirements_in_draft"]
        assert isinstance(drafts, list), f"Expected list, got {type(drafts)}"
        assert req_id in drafts
