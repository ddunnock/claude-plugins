"""Initialize requirements-dev workspace and state.json.

Usage: python3 init_session.py <project_path>

Creates .requirements-dev/ directory under project_path with an initialized
state.json. If workspace already exists, prints a message and exits without
overwriting (supports resume).
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from shared_io import _atomic_write, _validate_dir_path


WORKSPACE_DIR = ".requirements-dev"
TEMPLATE_FILENAME = "state.json"
CURRENT_SCHEMA_VERSION = "1.0.0"


def _get_template_path() -> str:
    """Return absolute path to templates/state.json relative to this script's location."""
    script_dir = Path(__file__).resolve().parent
    return str(script_dir.parent / "templates" / TEMPLATE_FILENAME)


def init_workspace(project_path: str) -> dict:
    """Create workspace and initialize state.json.

    Returns the initialized (or existing) state dict.
    """
    resolved_path = _validate_dir_path(project_path)
    ws_path = os.path.join(resolved_path, WORKSPACE_DIR)
    state_path = os.path.join(ws_path, "state.json")

    # Check for existing workspace (resume scenario)
    if os.path.isfile(state_path):
        with open(state_path) as f:
            existing_state = json.load(f)
        session_id = existing_state.get("session_id", "unknown")

        # Check schema version compatibility
        existing_version = existing_state.get("schema_version", "0.0.0")
        if existing_version != CURRENT_SCHEMA_VERSION:
            print(
                f"Warning: Existing state uses schema {existing_version}, "
                f"current code expects {CURRENT_SCHEMA_VERSION}. "
                "Some features may not work correctly.",
                file=sys.stderr,
            )

        print(
            f"Workspace already initialized (session: {session_id}). "
            "Use /reqdev:resume to continue."
        )
        return existing_state

    # Create workspace directory
    os.makedirs(ws_path, exist_ok=True)

    # Read template
    template_path = _get_template_path()
    with open(template_path) as f:
        state = json.load(f)

    # Populate session fields
    state["session_id"] = uuid.uuid4().hex
    state["created_at"] = datetime.now(timezone.utc).isoformat()

    # Write state atomically
    _atomic_write(state_path, state)

    print(f"Initialized requirements-dev workspace at {ws_path}")
    print(f"Session ID: {state['session_id']}")
    return state


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Initialize requirements-dev workspace")
    parser.add_argument("project_path", help="Path to the project root directory")
    args = parser.parse_args()

    init_workspace(args.project_path)


if __name__ == "__main__":
    main()
