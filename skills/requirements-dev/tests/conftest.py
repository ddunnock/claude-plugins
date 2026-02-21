"""Shared test fixtures for requirements-dev tests."""
import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary .requirements-dev/ workspace with initialized state.json.

    Returns the path to the .requirements-dev/ directory.
    """
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    state = {
        "session_id": "abc123",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "init",
        "gates": {"init": False, "needs": False, "requirements": False, "deliver": False},
        "blocks": {},
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
    return ws
