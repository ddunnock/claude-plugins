"""Tests for cross-cutting notes registry (notes_tracker.py)."""
import json

import pytest

from notes_tracker import (
    add_note,
    check_gate,
    dismiss_note,
    export_notes,
    list_notes,
    resolve_note,
    summary,
)


class TestAddNote:
    def test_add_basic(self, tmp_workspace):
        note_id = add_note(
            str(tmp_workspace),
            text="Performance concern: latency target needs benchmarking",
            origin_phase="needs",
            target_phase="research",
        )
        assert note_id == "NOTE-001"

    def test_add_with_all_fields(self, tmp_workspace):
        note_id = add_note(
            str(tmp_workspace),
            text="Interface constraint spotted",
            origin_phase="needs",
            target_phase="requirements",
            related_ids=["NEED-001", "NEED-003"],
            category="interface",
        )
        assert note_id == "NOTE-001"
        notes = list_notes(str(tmp_workspace))
        assert len(notes) == 1
        assert notes[0]["related_ids"] == ["NEED-001", "NEED-003"]
        assert notes[0]["category"] == "interface"
        assert notes[0]["status"] == "open"

    def test_sequential_ids(self, tmp_workspace):
        id1 = add_note(str(tmp_workspace), "First", "needs", "requirements")
        id2 = add_note(str(tmp_workspace), "Second", "needs", "requirements")
        id3 = add_note(str(tmp_workspace), "Third", "requirements", "validate")
        assert id1 == "NOTE-001"
        assert id2 == "NOTE-002"
        assert id3 == "NOTE-003"

    def test_invalid_origin_phase(self, tmp_workspace):
        with pytest.raises(ValueError, match="Invalid origin_phase"):
            add_note(str(tmp_workspace), "text", "bogus", "requirements")

    def test_invalid_target_phase(self, tmp_workspace):
        with pytest.raises(ValueError, match="Invalid target_phase"):
            add_note(str(tmp_workspace), "text", "needs", "bogus")

    def test_invalid_category(self, tmp_workspace):
        with pytest.raises(ValueError, match="Invalid category"):
            add_note(str(tmp_workspace), "text", "needs", "requirements", category="bogus")

    def test_syncs_state_counts(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note 1", "needs", "requirements")
        add_note(str(tmp_workspace), "Note 2", "needs", "validate")
        state = json.loads((tmp_workspace / "state.json").read_text())
        assert state["counts"]["notes_total"] == 2
        assert state["counts"]["notes_open"] == 2
        assert state["counts"]["notes_resolved"] == 0


class TestResolveNote:
    def test_resolve_basic(self, tmp_workspace):
        add_note(str(tmp_workspace), "Perf concern", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Addressed in REQ-015", "REQ-015")
        notes = list_notes(str(tmp_workspace))
        assert notes[0]["status"] == "resolved"
        assert notes[0]["resolution"] == "Addressed in REQ-015"
        assert notes[0]["resolved_by"] == "REQ-015"
        assert notes[0]["resolved_at"] != ""

    def test_resolve_without_resolved_by(self, tmp_workspace):
        add_note(str(tmp_workspace), "Observation", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Handled during requirements pass")
        notes = list_notes(str(tmp_workspace))
        assert notes[0]["status"] == "resolved"
        assert notes[0]["resolved_by"] == ""

    def test_resolve_empty_resolution_fails(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note", "needs", "requirements")
        with pytest.raises(ValueError, match="resolution text is required"):
            resolve_note(str(tmp_workspace), "NOTE-001", "")

    def test_resolve_already_resolved_fails(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Done")
        with pytest.raises(ValueError, match="already resolved"):
            resolve_note(str(tmp_workspace), "NOTE-001", "Again")

    def test_resolve_not_found(self, tmp_workspace):
        with pytest.raises(ValueError, match="Note not found"):
            resolve_note(str(tmp_workspace), "NOTE-999", "oops")

    def test_resolve_syncs_counts(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note 1", "needs", "requirements")
        add_note(str(tmp_workspace), "Note 2", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Done")
        state = json.loads((tmp_workspace / "state.json").read_text())
        assert state["counts"]["notes_open"] == 1
        assert state["counts"]["notes_resolved"] == 1


class TestDismissNote:
    def test_dismiss_basic(self, tmp_workspace):
        add_note(str(tmp_workspace), "Concern", "needs", "requirements")
        dismiss_note(str(tmp_workspace), "NOTE-001", "Not applicable after design change")
        notes = list_notes(str(tmp_workspace))
        assert notes[0]["status"] == "dismissed"
        assert notes[0]["dismiss_rationale"] == "Not applicable after design change"

    def test_dismiss_empty_rationale_fails(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note", "needs", "requirements")
        with pytest.raises(ValueError, match="rationale is required"):
            dismiss_note(str(tmp_workspace), "NOTE-001", "  ")

    def test_dismiss_already_dismissed_fails(self, tmp_workspace):
        add_note(str(tmp_workspace), "Note", "needs", "requirements")
        dismiss_note(str(tmp_workspace), "NOTE-001", "Nope")
        with pytest.raises(ValueError, match="already dismissed"):
            dismiss_note(str(tmp_workspace), "NOTE-001", "Again")


class TestListNotes:
    def test_list_all(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements", category="performance")
        add_note(str(tmp_workspace), "N2", "requirements", "validate", category="interface")
        assert len(list_notes(str(tmp_workspace))) == 2

    def test_filter_by_status(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        add_note(str(tmp_workspace), "N2", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Done")
        assert len(list_notes(str(tmp_workspace), status="open")) == 1
        assert len(list_notes(str(tmp_workspace), status="resolved")) == 1

    def test_filter_by_target_phase(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        add_note(str(tmp_workspace), "N2", "needs", "validate")
        assert len(list_notes(str(tmp_workspace), target_phase="requirements")) == 1
        assert len(list_notes(str(tmp_workspace), target_phase="validate")) == 1

    def test_filter_by_category(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements", category="performance")
        add_note(str(tmp_workspace), "N2", "needs", "requirements", category="interface")
        assert len(list_notes(str(tmp_workspace), category="performance")) == 1

    def test_combined_filters(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements", category="performance")
        add_note(str(tmp_workspace), "N2", "needs", "requirements", category="interface")
        add_note(str(tmp_workspace), "N3", "needs", "validate", category="performance")
        result = list_notes(str(tmp_workspace), target_phase="requirements", category="performance")
        assert len(result) == 1
        assert result[0]["text"] == "N1"


class TestCheckGate:
    def test_gate_ready_no_notes(self, tmp_workspace):
        result = check_gate(str(tmp_workspace), "requirements")
        assert result["ready"] is True
        assert result["open_notes"] == []

    def test_gate_ready_all_resolved(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Done")
        result = check_gate(str(tmp_workspace), "requirements")
        assert result["ready"] is True
        assert result["resolved_count"] == 1

    def test_gate_blocked_open_notes(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        add_note(str(tmp_workspace), "N2", "needs", "requirements")
        result = check_gate(str(tmp_workspace), "requirements")
        assert result["ready"] is False
        assert len(result["open_notes"]) == 2

    def test_gate_ignores_other_phases(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "validate")
        result = check_gate(str(tmp_workspace), "requirements")
        assert result["ready"] is True  # note targets validate, not requirements

    def test_gate_mixed_statuses(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        add_note(str(tmp_workspace), "N2", "needs", "requirements")
        add_note(str(tmp_workspace), "N3", "needs", "requirements")
        resolve_note(str(tmp_workspace), "NOTE-001", "Done")
        dismiss_note(str(tmp_workspace), "NOTE-002", "N/A")
        result = check_gate(str(tmp_workspace), "requirements")
        assert result["ready"] is False
        assert len(result["open_notes"]) == 1
        assert result["total_targeting"] == 3


class TestSummary:
    def test_empty(self, tmp_workspace):
        result = summary(str(tmp_workspace))
        assert result["total"] == 0
        assert result["open"] == 0

    def test_grouped_by_target(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        add_note(str(tmp_workspace), "N2", "needs", "validate")
        add_note(str(tmp_workspace), "N3", "requirements", "validate")
        resolve_note(str(tmp_workspace), "NOTE-002", "Done")
        result = summary(str(tmp_workspace))
        assert result["total"] == 3
        assert result["open"] == 2
        assert result["resolved"] == 1
        assert "requirements" in result["by_target_phase"]
        assert "validate" in result["by_target_phase"]
        assert result["by_target_phase"]["requirements"]["open"] == 1
        assert result["by_target_phase"]["validate"]["open"] == 1
        assert result["by_target_phase"]["validate"]["resolved"] == 1


class TestExport:
    def test_export(self, tmp_workspace):
        add_note(str(tmp_workspace), "N1", "needs", "requirements")
        result = export_notes(str(tmp_workspace))
        assert result["schema_version"] == "1.0.0"
        assert len(result["notes"]) == 1


class TestEmptyRegistry:
    def test_list_empty(self, tmp_workspace):
        assert list_notes(str(tmp_workspace)) == []

    def test_summary_empty(self, tmp_workspace):
        result = summary(str(tmp_workspace))
        assert result["total"] == 0

    def test_export_empty(self, tmp_workspace):
        result = export_notes(str(tmp_workspace))
        assert result["notes"] == []
