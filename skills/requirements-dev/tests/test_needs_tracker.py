"""Tests for needs_tracker.py -- stakeholder needs management."""
import json

import pytest

from needs_tracker import (
    add_need,
    defer_need,
    export_needs,
    list_needs,
    query_needs,
    reject_need,
    update_need,
)


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with state.json and empty needs registry."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    state = {
        "session_id": "test-abc",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "needs",
        "gates": {"init": True, "needs": False, "requirements": False, "deliver": False},
        "blocks": {"monitoring": "Dashboard block"},
        "progress": {
            "current_block": None,
            "current_type_pass": None,
            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
            "requirements_in_draft": [],
        },
        "counts": {
            "needs_total": 0,
            "needs_approved": 0,
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
    return str(ws)


def test_add_creates_need_with_correct_fields(workspace):
    """add creates NEED-001 with correct fields."""
    need_id = add_need(
        workspace,
        statement="The operator needs to monitor pipeline health",
        stakeholder="Pipeline Operator",
        source_block="monitoring",
    )
    assert need_id == "NEED-001"
    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
    need = registry["needs"][0]
    assert need["id"] == "NEED-001"
    assert need["statement"] == "The operator needs to monitor pipeline health"
    assert need["stakeholder"] == "Pipeline Operator"
    assert need["source_block"] == "monitoring"
    assert need["status"] == "approved"


def test_add_auto_increments_id(workspace):
    """add auto-increments ID (NEED-001, NEED-002, NEED-003)."""
    id1 = add_need(workspace, "Need one", "User", "block-a")
    id2 = add_need(workspace, "Need two", "User", "block-a")
    id3 = add_need(workspace, "Need three", "Admin", "block-b")
    assert id1 == "NEED-001"
    assert id2 == "NEED-002"
    assert id3 == "NEED-003"


def test_add_validates_uniqueness(workspace):
    """add rejects duplicate statement+stakeholder combination."""
    add_need(workspace, "The user needs X", "User", "block-a")
    with pytest.raises(ValueError, match="duplicate"):
        add_need(workspace, "the user needs x", "user", "block-a")  # case-insensitive


def test_add_syncs_counts_to_state(workspace):
    """add syncs needs_total count to state.json."""
    add_need(workspace, "Need one", "User", "block-a")
    add_need(workspace, "Need two", "Admin", "block-b")
    state = json.loads(open(f"{workspace}/state.json").read())
    assert state["counts"]["needs_total"] == 2
    assert state["counts"]["needs_approved"] == 2


def test_update_modifies_statement(workspace):
    """update modifies statement and preserves other fields."""
    add_need(workspace, "Original statement", "User", "block-a")
    update_need(workspace, "NEED-001", statement="Updated statement")
    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
    need = registry["needs"][0]
    assert need["statement"] == "Updated statement"
    assert need["stakeholder"] == "User"
    assert need["source_block"] == "block-a"


def test_defer_sets_status_with_rationale(workspace):
    """defer sets status='deferred' and requires rationale."""
    add_need(workspace, "Need one", "User", "block-a")
    defer_need(workspace, "NEED-001", rationale="Not in scope for MVP")
    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
    assert registry["needs"][0]["status"] == "deferred"
    assert registry["needs"][0]["rationale"] == "Not in scope for MVP"


def test_defer_without_rationale_raises_error(workspace):
    """defer without rationale raises error."""
    add_need(workspace, "Need one", "User", "block-a")
    with pytest.raises(ValueError, match="rationale"):
        defer_need(workspace, "NEED-001", rationale="")


def test_reject_sets_status_with_rationale(workspace):
    """reject sets status='rejected' and requires rationale."""
    add_need(workspace, "Need one", "User", "block-a")
    reject_need(workspace, "NEED-001", rationale="Out of scope")
    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
    assert registry["needs"][0]["status"] == "rejected"


def test_list_returns_needs_for_block(workspace):
    """list returns all needs for a given block."""
    add_need(workspace, "Need A", "User", "block-a")
    add_need(workspace, "Need B", "User", "block-b")
    add_need(workspace, "Need C", "Admin", "block-a")
    result = list_needs(workspace, block="block-a")
    assert len(result) == 2
    assert all(n["source_block"] == "block-a" for n in result)


def test_list_with_status_filter(workspace):
    """list with status filter returns only matching needs."""
    add_need(workspace, "Need A", "User", "block-a")
    add_need(workspace, "Need B", "Admin", "block-a")
    defer_need(workspace, "NEED-001", rationale="Later")
    result = list_needs(workspace, status="deferred")
    assert len(result) == 1
    assert result[0]["id"] == "NEED-001"


def test_query_by_source_ref(workspace):
    """query by concept_dev_refs returns needs linked to specific SRC-xxx."""
    add_need(
        workspace, "Need A", "User", "block-a",
        concept_dev_refs={"sources": ["SRC-001"], "assumptions": []},
    )
    add_need(workspace, "Need B", "Admin", "block-b")
    result = query_needs(workspace, source_ref="SRC-001")
    assert len(result) == 1
    assert result[0]["id"] == "NEED-001"


def test_export_produces_correct_structure(workspace):
    """export produces correct JSON structure."""
    add_need(workspace, "Need A", "User", "block-a")
    result = export_needs(workspace)
    assert "schema_version" in result
    assert "needs" in result
    assert len(result["needs"]) == 1


def test_schema_version_in_registry(workspace):
    """schema_version field present in registry output."""
    add_need(workspace, "Need A", "User", "block-a")
    registry = json.loads(open(f"{workspace}/needs_registry.json").read())
    assert registry["schema_version"] == "1.0.0"
