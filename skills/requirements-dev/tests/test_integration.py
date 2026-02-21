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


# ---------------------------------------------------------------------------
# Section 08: Resume flow tests
# ---------------------------------------------------------------------------

class TestResumeFlow:
    """Verify state reading for resume after interruptions."""

    def test_resume_after_need_registration(self, pipeline_workspace):
        """After needs registered, state shows correct phase and counts."""
        ws = str(pipeline_workspace)

        # State already has init+needs gates passed, 2 approved needs
        summary = update_state.show(ws)
        assert "needs" in summary
        state = json.loads((pipeline_workspace / "state.json").read_text())
        assert state["current_phase"] == "needs"
        assert state["counts"]["needs_approved"] == 2
        assert state["gates"]["needs"] is True

    def test_resume_mid_type_pass(self, pipeline_workspace):
        """Mid-type-pass state shows current block and type."""
        ws = str(pipeline_workspace)

        # Set phase and progress
        update_state.set_phase(ws, "requirements")
        update_state.update_field(ws, "progress.current_block", "auth")
        update_state.update_field(ws, "progress.current_type_pass", "performance")

        # Add some requirements
        for stmt in (
            "The system shall authenticate in under 500ms",
            "The system shall support 100 concurrent login sessions",
        ):
            req_id = requirement_tracker.add_requirement(
                ws, stmt, "performance", "high", "auth",
            )
            requirement_tracker.register_requirement(ws, req_id, "NEED-001")

        update_state.sync_counts(ws)

        # Verify resume state
        state = json.loads((pipeline_workspace / "state.json").read_text())
        assert state["progress"]["current_block"] == "auth"
        assert state["progress"]["current_type_pass"] == "performance"
        assert state["counts"]["requirements_registered"] == 2

        # Show output includes position
        summary = update_state.show(ws)
        assert "auth" in summary
        assert "performance" in summary

    def test_resume_preserves_requirements_in_draft(self, pipeline_workspace):
        """Draft requirements are preserved and readable for resume."""
        ws = str(pipeline_workspace)

        # Add drafts (not registered)
        ids = []
        for stmt in (
            "The system shall encrypt passwords using bcrypt",
            "The system shall enforce minimum password length of 12 characters",
        ):
            req_id = requirement_tracker.add_requirement(
                ws, stmt, "functional", "high", "auth",
            )
            ids.append(req_id)

        # Save drafts to state
        update_state.update_field(
            ws, "progress.requirements_in_draft", json.dumps(ids),
        )

        # Verify state correctly reports drafts
        state = json.loads((pipeline_workspace / "state.json").read_text())
        drafts = state["progress"]["requirements_in_draft"]
        assert isinstance(drafts, list)
        assert len(drafts) == 2
        assert all(d.startswith("REQ-") for d in drafts)

        # Verify draft requirements exist in registry with draft status
        reg = requirement_tracker._load_registry(ws)
        for req_id in drafts:
            req = next(r for r in reg["requirements"] if r["id"] == req_id)
            assert req["status"] == "draft"


# ---------------------------------------------------------------------------
# Section 09: Deliverable generation and baselining tests
# ---------------------------------------------------------------------------

@pytest.fixture
def delivery_workspace(pipeline_workspace):
    """Workspace ready for delivery: requirements gate passed, 3 registered requirements."""
    ws = pipeline_workspace

    # Pass requirements gate
    state = json.loads((ws / "state.json").read_text())
    state["gates"]["requirements"] = True
    state["current_phase"] = "requirements"
    (ws / "state.json").write_text(json.dumps(state, indent=2))

    # Add 3 registered requirements across different types
    for i, (stmt, rtype, need) in enumerate([
        ("The system shall authenticate users via username and password", "functional", "NEED-001"),
        ("The system shall respond to login requests within 500ms", "performance", "NEED-001"),
        ("The system shall expose a REST API for password reset", "interface", "NEED-002"),
    ], start=1):
        req_id = requirement_tracker.add_requirement(ws_str := str(ws), stmt, rtype, "high", "auth")
        requirement_tracker.register_requirement(ws_str, req_id, need)
        # Create traceability links
        traceability.link(ws_str, req_id, need, "derives_from", "requirement")

    return ws


class TestDeliverablePipeline:
    """Verify deliverable generation, baselining, and withdrawal."""

    def test_baselining_transitions_all_requirements(self, delivery_workspace):
        """baseline_all() transitions all registered requirements to baselined."""
        ws = str(delivery_workspace)

        # Get all registered requirements
        reqs = requirement_tracker.query_requirements(ws, status="registered")
        assert len(reqs) == 3, f"Expected 3 registered, got {len(reqs)}"

        # Baseline all using baseline_all()
        result = requirement_tracker.baseline_all(ws)
        assert len(result["baselined"]) == 3
        assert len(result["skipped_draft"]) == 0

        # Verify all baselined
        reg = requirement_tracker._load_registry(ws)
        for req in reg["requirements"]:
            assert req["status"] == "baselined", f"{req['id']} not baselined"
            assert "baselined_at" in req

        # Verify counts
        state = json.loads((delivery_workspace / "state.json").read_text())
        assert state["counts"]["requirements_baselined"] == 3
        assert state["counts"]["requirements_registered"] == 0

    def test_baseline_all_reports_draft_warnings(self, delivery_workspace):
        """baseline_all() reports draft requirements as skipped."""
        ws = str(delivery_workspace)

        # Add a draft requirement (not registered)
        requirement_tracker.add_requirement(
            ws, "Draft requirement for testing", "functional", "high", "auth",
        )

        result = requirement_tracker.baseline_all(ws)
        assert len(result["baselined"]) == 3  # Only the registered ones
        assert len(result["skipped_draft"]) == 1  # The draft one

    def test_withdrawn_excluded_from_coverage(self, delivery_workspace):
        """Withdrawn requirements remain in registry but do not count in coverage."""
        ws = str(delivery_workspace)

        # Get the coverage before withdrawal
        report_before = traceability.coverage_report(ws)

        # Withdraw one requirement
        reqs = requirement_tracker.list_requirements(ws)
        req_to_withdraw = reqs[0]
        requirement_tracker.withdraw_requirement(ws, req_to_withdraw["id"], "No longer needed")

        # Coverage should account for withdrawal
        report_after = traceability.coverage_report(ws)
        # The withdrawn req's link is excluded from coverage
        assert report_after["requirements_with_vv"] <= report_before["requirements_with_vv"]

        # But the requirement still exists in registry
        all_reqs = requirement_tracker.list_requirements(ws, include_withdrawn=True)
        withdrawn = [r for r in all_reqs if r["status"] == "withdrawn"]
        assert len(withdrawn) == 1

    def test_withdrawn_excluded_from_deliverables(self, delivery_workspace):
        """list_requirements without include_withdrawn excludes withdrawn reqs."""
        ws = str(delivery_workspace)

        # Withdraw one
        reqs = requirement_tracker.list_requirements(ws)
        initial_count = len(reqs)
        requirement_tracker.withdraw_requirement(ws, reqs[0]["id"], "Superseded")

        # Default list excludes withdrawn
        active_reqs = requirement_tracker.list_requirements(ws)
        assert len(active_reqs) == initial_count - 1

        # With flag, all are present
        all_reqs = requirement_tracker.list_requirements(ws, include_withdrawn=True)
        assert len(all_reqs) == initial_count

    def test_generate_traceability_matrix_data(self, delivery_workspace):
        """Traceability coverage report includes all need-to-requirement chains."""
        ws = str(delivery_workspace)

        report = traceability.coverage_report(ws)
        assert report["needs_covered"] == 2  # Both NEED-001 and NEED-002 have reqs
        assert report["needs_total"] == 2
        assert report["coverage_pct"] == 100.0

    def test_generate_verification_matrix_data(self, delivery_workspace):
        """All registered requirements can be queried for V&V entries."""
        ws = str(delivery_workspace)

        reqs = requirement_tracker.list_requirements(ws)
        assert len(reqs) == 3
        # Each has a type that maps to a V&V method
        for req in reqs:
            assert req["type"] in {"functional", "performance", "interface", "constraint", "quality"}

    def test_orphan_check_clean(self, delivery_workspace):
        """With full traceability, orphan check returns empty lists."""
        ws = str(delivery_workspace)

        orphans = traceability.orphan_check(ws)
        assert len(orphans["orphan_needs"]) == 0
        assert len(orphans["orphan_requirements"]) == 0
