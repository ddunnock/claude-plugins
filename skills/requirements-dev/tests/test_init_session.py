"""Tests for init_session.py workspace initialization."""
import json

import pytest

from init_session import init_workspace


def test_init_creates_workspace_directory(tmp_path):
    """Calling init with a project path creates .requirements-dev/ under that path."""
    result = init_workspace(str(tmp_path))
    ws = tmp_path / ".requirements-dev"
    assert ws.is_dir()


def test_init_creates_state_json_from_template(tmp_path):
    """state.json is created with a non-empty session_id and schema_version '1.0.0'."""
    result = init_workspace(str(tmp_path))
    state_file = tmp_path / ".requirements-dev" / "state.json"
    assert state_file.exists()

    state = json.loads(state_file.read_text())
    assert state["session_id"] != ""
    assert len(state["session_id"]) == 32  # uuid4 hex
    assert state["schema_version"] == "1.0.0"
    assert state["created_at"] != ""


def test_init_state_has_zero_counts(tmp_path):
    """All count fields in the initialized state.json must be zero."""
    init_workspace(str(tmp_path))
    state = json.loads((tmp_path / ".requirements-dev" / "state.json").read_text())

    for key, value in state["counts"].items():
        assert value == 0, f"counts.{key} should be 0, got {value}"


def test_init_state_has_null_progress(tmp_path):
    """progress.current_block and progress.current_type_pass must be null on init."""
    init_workspace(str(tmp_path))
    state = json.loads((tmp_path / ".requirements-dev" / "state.json").read_text())

    assert state["progress"]["current_block"] is None
    assert state["progress"]["current_type_pass"] is None


def test_init_does_not_overwrite_existing_workspace(tmp_path):
    """If .requirements-dev/ already exists with a state.json, init must not overwrite it."""
    # First init
    init_workspace(str(tmp_path))
    state_file = tmp_path / ".requirements-dev" / "state.json"
    original_state = json.loads(state_file.read_text())
    original_session_id = original_state["session_id"]

    # Second init -- should preserve original
    result = init_workspace(str(tmp_path))
    state = json.loads(state_file.read_text())
    assert state["session_id"] == original_session_id


def test_init_validates_path_rejects_traversal(tmp_path):
    """CLI rejects paths containing '..' traversal at argparse level."""
    import subprocess
    from pathlib import Path
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    result = subprocess.run(
        ["python3", "init_session.py", str(tmp_path / ".." / "evil")],
        capture_output=True, text=True, cwd=str(scripts_dir),
    )
    assert result.returncode != 0
