#!/usr/bin/env python3
"""
Initialize a concept development session.

Creates the .concept-dev/ workspace directory and initializes state.json.
"""

import json
import argparse
import uuid
from datetime import datetime
from pathlib import Path

TEMPLATE_STATE = Path(__file__).parent.parent / "templates" / "state.json"


def init_session(project_dir: str, project_name: str = None, description: str = None) -> dict:
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
        with open(state_path, "r") as f:
            existing = json.load(f)
        print(f"Session already exists: {existing['session']['id']}")
        print(f"  Project: {existing['session'].get('project_name', 'unnamed')}")
        print(f"  Phase: {existing.get('current_phase', 'none')}")
        print(f"  Last updated: {existing['session'].get('last_updated', 'unknown')}")
        return existing

    # Create workspace
    workspace.mkdir(parents=True, exist_ok=True)

    # Load template
    with open(TEMPLATE_STATE, "r") as f:
        state = json.load(f)

    # Initialize session metadata
    now = datetime.now().isoformat()
    state["session"]["id"] = str(uuid.uuid4())[:8]
    state["session"]["created_at"] = now
    state["session"]["last_updated"] = now
    state["session"]["project_name"] = project_name
    state["session"]["description"] = description

    # Write state
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Session initialized: {state['session']['id']}")
    print(f"  Workspace: {workspace}")
    print(f"  State file: {state_path}")

    return state


def main():
    parser = argparse.ArgumentParser(description="Initialize concept development session")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory (default: current)")
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--description", help="Project description")

    args = parser.parse_args()
    init_session(args.project_dir, args.name, args.description)


if __name__ == "__main__":
    main()
