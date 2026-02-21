"""Shared test fixtures for requirements-dev tests."""
import json

import pytest


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary .requirements-dev/ workspace with initialized state.json.

    Returns the path to the .requirements-dev/ directory.
    """
    workspace = tmp_path / ".requirements-dev"
    workspace.mkdir()

    # Load state template and initialize
    template_path = (
        pytest.importorskip("pathlib").Path(__file__).parent.parent
        / "templates"
        / "state.json"
    )
    state = json.loads(template_path.read_text())
    state["session_id"] = "test-session-001"
    state["created_at"] = "2025-01-01T00:00:00Z"

    state_file = workspace / "state.json"
    state_file.write_text(json.dumps(state, indent=2))

    return workspace
