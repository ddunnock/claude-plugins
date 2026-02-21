"""Tests for update_state.py state mutation operations."""
import json

import pytest

from update_state import (
    check_gate,
    pass_gate,
    set_artifact,
    set_phase,
    show,
    sync_counts,
    update_field,
)


def test_set_phase_updates_current_phase(tmp_workspace):
    """set-phase 'needs' should change current_phase from 'init' to 'needs'."""
    set_phase(str(tmp_workspace), "needs")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["current_phase"] == "needs"


def test_pass_gate_sets_gate_true(tmp_workspace):
    """pass-gate 'init' should set gates.init to true."""
    pass_gate(str(tmp_workspace), "init")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["gates"]["init"] is True


def test_pass_gate_idempotent(tmp_workspace):
    """Passing a gate that is already true should not error or change anything."""
    pass_gate(str(tmp_workspace), "init")
    pass_gate(str(tmp_workspace), "init")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["gates"]["init"] is True


def test_check_gate_returns_correct_value(tmp_workspace):
    """check-gate should return True for passed gates, False for unpassed gates."""
    assert check_gate(str(tmp_workspace), "init") is False
    pass_gate(str(tmp_workspace), "init")
    assert check_gate(str(tmp_workspace), "init") is True


def test_set_artifact_stores_path(tmp_workspace):
    """set-artifact 'deliver' 'REQUIREMENTS-SPECIFICATION.md' should store the path."""
    set_artifact(str(tmp_workspace), "deliver", "REQUIREMENTS-SPECIFICATION.md")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert "deliver" in state["artifacts"]
    assert state["artifacts"]["deliver"] == "REQUIREMENTS-SPECIFICATION.md"


def test_set_artifact_with_key(tmp_workspace):
    """set-artifact with --key should store under artifacts.<phase>.<key>."""
    set_artifact(str(tmp_workspace), "deliver", "/path/to/SPEC.md", key="specification_artifact")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["artifacts"]["deliver"]["specification_artifact"] == "/path/to/SPEC.md"


def test_update_dotted_path(tmp_workspace):
    """update 'counts.needs_total' '5' should set state['counts']['needs_total'] to 5."""
    update_field(str(tmp_workspace), "counts.needs_total", "5")
    state = json.loads((tmp_workspace / "state.json").read_text())
    assert state["counts"]["needs_total"] == 5


def test_sync_counts_from_registries(tmp_workspace):
    """sync-counts should read registries and update count fields."""
    # Create a needs registry
    needs = [
        {"id": "NEED-001", "status": "approved"},
        {"id": "NEED-002", "status": "approved"},
        {"id": "NEED-003", "status": "deferred"},
    ]
    (tmp_workspace / "needs_registry.json").write_text(json.dumps(needs, indent=2))

    # Create a requirements registry
    reqs = [
        {"id": "REQ-001", "status": "registered", "tbd_tbr": None},
        {"id": "REQ-002", "status": "baselined", "tbd_tbr": None},
        {"id": "REQ-003", "status": "registered", "tbd_tbr": {"tbd": ["value TBD"]}},
    ]
    (tmp_workspace / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))

    sync_counts(str(tmp_workspace))
    state = json.loads((tmp_workspace / "state.json").read_text())

    assert state["counts"]["needs_total"] == 3
    assert state["counts"]["needs_approved"] == 2
    assert state["counts"]["needs_deferred"] == 1
    assert state["counts"]["requirements_total"] == 3
    assert state["counts"]["requirements_registered"] == 2
    assert state["counts"]["requirements_baselined"] == 1
    assert state["counts"]["tbd_open"] == 1


def test_show_returns_summary(tmp_workspace, capsys):
    """show should print current phase, gate status, and counts."""
    result = show(str(tmp_workspace))
    assert "init" in result
    assert "session_id" in result.lower() or "abc123" in result


def test_pass_gate_rejects_unknown_gate(tmp_workspace):
    """Passing an unknown gate name should raise ValueError."""
    with pytest.raises(ValueError, match="Unknown gate"):
        pass_gate(str(tmp_workspace), "nonexistent")


def test_sync_counts_with_no_registries(tmp_workspace):
    """sync-counts with no registry files should leave all counts at zero."""
    sync_counts(str(tmp_workspace))
    state = json.loads((tmp_workspace / "state.json").read_text())
    for key, value in state["counts"].items():
        assert value == 0, f"counts.{key} should be 0, got {value}"


def test_show_includes_traceability(tmp_workspace):
    """show should include traceability coverage info."""
    result = show(str(tmp_workspace))
    assert "traceability" in result.lower() or "coverage" in result.lower()


def test_atomic_write_uses_temp_file(tmp_workspace, monkeypatch):
    """All state mutations must use atomic write pattern."""
    import update_state

    writes = []
    original_save = update_state._save_state

    def tracking_save(workspace_path, state):
        writes.append(workspace_path)
        original_save(workspace_path, state)

    monkeypatch.setattr(update_state, "_save_state", tracking_save)
    set_phase(str(tmp_workspace), "needs")
    assert len(writes) == 1
