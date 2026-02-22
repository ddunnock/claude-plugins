"""Tests for requirement_tracker.py."""
import json

import pytest

from requirement_tracker import (
    add_requirement,
    baseline_requirement,
    export_requirements,
    list_requirements,
    query_requirements,
    register_requirement,
    split_requirement,
    update_requirement,
    withdraw_requirement,
)

VALID_TYPES = ["functional", "performance", "interface", "constraint", "quality"]
VALID_PRIORITIES = ["high", "medium", "low"]


def _add_need(ws, need_id="NEED-001", statement="The operator needs monitoring"):
    """Helper to seed a need in needs_registry.json."""
    reg = {"schema_version": "1.0.0", "needs": [
        {"id": need_id, "statement": statement, "stakeholder": "Operator",
         "source_block": "monitoring", "status": "approved", "rationale": None}
    ]}
    (ws / "needs_registry.json").write_text(json.dumps(reg))


def test_add_creates_req_with_correct_fields(tmp_workspace):
    req_id = add_requirement(
        str(tmp_workspace), "The API shall respond within 200ms",
        type="performance", priority="high", source_block="api-gateway",
    )
    assert req_id == "REQ-001"
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    req = reg["requirements"][0]
    assert req["statement"] == "The API shall respond within 200ms"
    assert req["type"] == "performance"
    assert req["priority"] == "high"
    assert req["status"] == "draft"


def test_add_auto_increments_id(tmp_workspace):
    id1 = add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
    id2 = add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="blk")
    id3 = add_requirement(str(tmp_workspace), "Req 3", type="functional", priority="high", source_block="blk")
    assert id1 == "REQ-001"
    assert id2 == "REQ-002"
    assert id3 == "REQ-003"


def test_add_validates_type(tmp_workspace):
    with pytest.raises(ValueError, match="type"):
        add_requirement(str(tmp_workspace), "Req", type="invalid", priority="high", source_block="blk")


def test_add_validates_priority(tmp_workspace):
    with pytest.raises(ValueError, match="priority"):
        add_requirement(str(tmp_workspace), "Req", type="functional", priority="critical", source_block="blk")


def test_register_transitions_to_registered(tmp_workspace):
    _add_need(tmp_workspace)
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    assert reg["requirements"][0]["status"] == "registered"
    assert reg["requirements"][0]["parent_need"] == "NEED-001"


def test_register_requires_parent_need(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    with pytest.raises(ValueError, match="parent_need"):
        register_requirement(str(tmp_workspace), "REQ-001", parent_need="")


def test_baseline_transitions_from_registered(tmp_workspace):
    _add_need(tmp_workspace)
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
    baseline_requirement(str(tmp_workspace), "REQ-001")
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    assert reg["requirements"][0]["status"] == "baselined"


def test_baseline_on_non_registered_raises_error(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    with pytest.raises(ValueError, match="registered"):
        baseline_requirement(str(tmp_workspace), "REQ-001")


def test_withdraw_sets_status_with_rationale(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Superseded")
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    assert reg["requirements"][0]["status"] == "withdrawn"
    assert reg["requirements"][0]["rationale"] == "Superseded"


def test_withdraw_without_rationale_raises_error(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    with pytest.raises(ValueError, match="rationale"):
        withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="")


def test_withdraw_preserves_requirement(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Obsolete")
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    assert len(reg["requirements"]) == 1  # not deleted


def test_list_excludes_withdrawn_by_default(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
    add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="blk")
    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Gone")
    result = list_requirements(str(tmp_workspace))
    assert len(result) == 1
    assert result[0]["id"] == "REQ-002"


def test_list_with_include_withdrawn(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
    withdraw_requirement(str(tmp_workspace), "REQ-001", rationale="Gone")
    result = list_requirements(str(tmp_workspace), include_withdrawn=True)
    assert len(result) == 1
    assert result[0]["status"] == "withdrawn"


def test_query_by_type(tmp_workspace):
    add_requirement(str(tmp_workspace), "Perf req", type="performance", priority="high", source_block="blk")
    add_requirement(str(tmp_workspace), "Func req", type="functional", priority="high", source_block="blk")
    result = query_requirements(str(tmp_workspace), type="performance")
    assert len(result) == 1
    assert result[0]["type"] == "performance"


def test_query_by_source_block(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="api")
    add_requirement(str(tmp_workspace), "Req 2", type="functional", priority="high", source_block="db")
    result = query_requirements(str(tmp_workspace), source_block="api")
    assert len(result) == 1
    assert result[0]["source_block"] == "api"


def test_query_by_level(tmp_workspace):
    add_requirement(str(tmp_workspace), "Sys req", type="functional", priority="high", source_block="blk")
    add_requirement(str(tmp_workspace), "Sub req", type="functional", priority="high", source_block="blk", level=1)
    result = query_requirements(str(tmp_workspace), level=0)
    assert len(result) == 1


def test_update_modifies_attributes(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    update_requirement(str(tmp_workspace), "REQ-001", attributes={"A6_verification_method": "system test"})
    reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
    assert reg["requirements"][0]["attributes"]["A6_verification_method"] == "system test"


def test_export_produces_correct_structure(tmp_workspace):
    add_requirement(str(tmp_workspace), "Req", type="functional", priority="high", source_block="blk")
    result = export_requirements(str(tmp_workspace))
    assert "schema_version" in result
    assert "requirements" in result
    assert len(result["requirements"]) == 1


def test_sync_counts_updates_state(tmp_workspace):
    _add_need(tmp_workspace)
    add_requirement(str(tmp_workspace), "Req 1", type="functional", priority="high", source_block="blk")
    register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["counts"]["requirements_total"] == 1
    assert state["counts"]["requirements_registered"] == 1


# --- Split requirement tests ---


class TestSplitRequirement:
    def test_split_withdraws_original_and_creates_new(self, tmp_workspace):
        """split withdraws the original and creates N new draft requirements."""
        add_requirement(str(tmp_workspace), "The system shall encrypt data and log access",
                        type="functional", priority="high", source_block="security")
        result = split_requirement(
            str(tmp_workspace), "REQ-001",
            ["The system shall encrypt all data at rest.",
             "The system shall log all access attempts within 5 seconds."],
        )
        assert result["withdrawn"] == "REQ-001"
        assert len(result["created"]) == 2
        assert result["created"] == ["REQ-002", "REQ-003"]

        # Original should be withdrawn
        reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
        original = next(r for r in reg["requirements"] if r["id"] == "REQ-001")
        assert original["status"] == "withdrawn"
        assert "Split" in original["rationale"]

    def test_split_inherits_metadata(self, tmp_workspace):
        """split copies type, priority, source_block, and level to new requirements."""
        add_requirement(str(tmp_workspace), "Combined req",
                        type="performance", priority="medium", source_block="api", level=1)
        result = split_requirement(
            str(tmp_workspace), "REQ-001",
            ["Part A", "Part B"],
        )
        reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
        for new_id in result["created"]:
            req = next(r for r in reg["requirements"] if r["id"] == new_id)
            assert req["type"] == "performance"
            assert req["priority"] == "medium"
            assert req["source_block"] == "api"
            assert req["level"] == 1
            assert req["status"] == "draft"

    def test_split_records_split_from_attribute(self, tmp_workspace):
        """split records split_from in each new requirement's attributes."""
        add_requirement(str(tmp_workspace), "Combined req",
                        type="functional", priority="high", source_block="blk")
        result = split_requirement(
            str(tmp_workspace), "REQ-001",
            ["Part A", "Part B"],
        )
        reg = json.loads((tmp_workspace / "requirements_registry.json").read_text())
        for new_id in result["created"]:
            req = next(r for r in reg["requirements"] if r["id"] == new_id)
            assert req["attributes"]["split_from"] == "REQ-001"

    def test_split_inherits_parent_need(self, tmp_workspace):
        """split returns the inherited parent_need from the original."""
        _add_need(tmp_workspace)
        add_requirement(str(tmp_workspace), "Combined req",
                        type="functional", priority="high", source_block="blk")
        register_requirement(str(tmp_workspace), "REQ-001", parent_need="NEED-001")
        result = split_requirement(
            str(tmp_workspace), "REQ-001",
            ["Part A", "Part B"],
        )
        assert result["parent_need"] == "NEED-001"

    def test_split_requires_at_least_two_statements(self, tmp_workspace):
        """split with fewer than 2 statements raises ValueError."""
        add_requirement(str(tmp_workspace), "Req",
                        type="functional", priority="high", source_block="blk")
        with pytest.raises(ValueError, match="at least 2"):
            split_requirement(str(tmp_workspace), "REQ-001", ["Only one"])

    def test_split_requires_rationale(self, tmp_workspace):
        """split with empty rationale raises ValueError."""
        add_requirement(str(tmp_workspace), "Req",
                        type="functional", priority="high", source_block="blk")
        with pytest.raises(ValueError, match="rationale"):
            split_requirement(str(tmp_workspace), "REQ-001",
                              ["A", "B"], rationale="")

    def test_split_syncs_counts(self, tmp_workspace):
        """split updates counts in state.json correctly."""
        add_requirement(str(tmp_workspace), "Combined req",
                        type="functional", priority="high", source_block="blk")
        split_requirement(str(tmp_workspace), "REQ-001",
                          ["Part A", "Part B", "Part C"])
        state = json.loads((tmp_workspace / "state.json").read_text())
        assert state["counts"]["requirements_total"] == 4  # 1 withdrawn + 3 new
        assert state["counts"]["requirements_withdrawn"] == 1

    def test_split_three_way(self, tmp_workspace):
        """split into 3 statements creates 3 new requirements."""
        add_requirement(str(tmp_workspace), "A and B and C",
                        type="functional", priority="high", source_block="blk")
        result = split_requirement(
            str(tmp_workspace), "REQ-001",
            ["Part A", "Part B", "Part C"],
        )
        assert len(result["created"]) == 3

    def test_split_not_found(self, tmp_workspace):
        """split on nonexistent ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            split_requirement(str(tmp_workspace), "REQ-999",
                              ["A", "B"])
