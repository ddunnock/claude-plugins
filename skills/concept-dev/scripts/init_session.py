#!/usr/bin/env python3
"""
Initialize a concept development session.

Creates the .concept-dev/ workspace directory and initializes state.json.
"""

import sys
import os
import json
import argparse
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

TEMPLATE_STATE = Path(__file__).parent.parent / "templates" / "state.json"


def init_session(
    project_dir: str,
    project_name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Initialize a new concept-dev session workspace.

    Args:
        project_dir: Root directory where .concept-dev/ will be created
        project_name: Optional project name
        description: Optional project description

    Returns:
        Initialized state dict
    """
    workspace = Path(project_dir) / ".concept-dev"
    state_path = workspace / "state.json"

    if state_path.exists():
        existing = json.loads(state_path.read_text())
        print(f"Session already exists: {existing['session']['id']}")
        print(f"  Project: {existing['session'].get('project_name', 'unnamed')}")
        print(f"  Phase: {existing.get('current_phase', 'none')}")
        print(f"  Last updated: {existing['session'].get('last_updated', 'unknown')}")
        return existing

    workspace.mkdir(parents=True, exist_ok=True)

    state = json.loads(TEMPLATE_STATE.read_text())

    now = datetime.now().isoformat()
    state["session"]["id"] = str(uuid.uuid4())[:8]
    state["session"]["created_at"] = now
    state["session"]["last_updated"] = now
    state["session"]["project_name"] = project_name
    state["session"]["description"] = description

    # Write to temp then rename for atomicity (consistent with update_state.py)
    tmp_path = state_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(state, indent=2))
    tmp_path.rename(state_path)

    print(f"Session initialized: {state['session']['id']}")
    print(f"  Workspace: {workspace}")
    print(f"  State file: {state_path}")

    return state



def _validate_dir_path(dirpath: str, label: str) -> str:
    """Validate directory path: reject traversal. Returns resolved path."""
    resolved = os.path.realpath(dirpath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {dirpath}")
        sys.exit(1)
    return resolved

def main():
    parser = argparse.ArgumentParser(description="Initialize concept development session")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory (default: current)")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")

    args = parser.parse_args()

    args.project_dir = _validate_dir_path(args.project_dir, "project directory")
    init_session(args.project_dir, args.name, args.description)


if __name__ == "__main__":
    main()
