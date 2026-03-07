"""Initialize the .system-dev/ workspace directory structure.

Creates the Design Registry workspace with registry subdirectories,
empty journal, slot index, and configuration files.
"""

import os
from datetime import datetime, timezone

from scripts.shared_io import (
    atomic_write,
    cleanup_orphaned_temps,
    ensure_directory,
    validate_path,
)


def init_workspace(project_root: str) -> dict:
    """Create the .system-dev/ workspace with all required subdirectories and files.

    Creates:
        - .system-dev/registry/components/
        - .system-dev/registry/interfaces/
        - .system-dev/registry/contracts/
        - .system-dev/registry/requirement-refs/
        - .system-dev/journal.jsonl (empty)
        - .system-dev/index.json (initial schema)
        - .system-dev/config.json (initial config)

    If the workspace already exists, returns a warning without modifying anything.
    Runs cleanup_orphaned_temps() on startup for crash recovery.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        Dictionary with:
            - status: "created" or "exists"
            - paths: list of created paths (if status is "created")
            - warnings: list of warning messages (if any)
            - cleaned_temps: list of removed .tmp files (if any)

    References:
        SCAF-05 (workspace initialization), DREG-01 (design registry)
    """
    workspace_dir = os.path.join(project_root, ".system-dev")
    result = {
        "status": "",
        "paths": [],
        "warnings": [],
        "cleaned_temps": [],
    }

    # Check if workspace already exists
    if os.path.exists(workspace_dir):
        result["status"] = "exists"
        result["warnings"].append(
            f"Workspace already exists at {workspace_dir}. "
            "Use /system-dev:status to check current state."
        )
        # Still run cleanup on existing workspace
        result["cleaned_temps"] = cleanup_orphaned_temps(workspace_dir)
        return result

    # Validate project root path
    validate_path(project_root, project_root)

    # Create registry subdirectories
    registry_dirs = [
        "registry/components",
        "registry/interfaces",
        "registry/contracts",
        "registry/diagram",
        "registry/requirement-refs",
        "registry/needs",
        "registry/requirements",
        "registry/sources",
        "registry/assumptions",
        "registry/traceability-links",
        "registry/component-proposals",
        "view-specs",  # User-authored view specifications
        "templates",  # User-authored template overrides (.j2 files)
    ]

    created_paths = []
    for subdir in registry_dirs:
        dir_path = os.path.join(workspace_dir, subdir)
        validate_path(dir_path, project_root)
        ensure_directory(dir_path)
        created_paths.append(dir_path)

    # Create empty journal.jsonl
    journal_path = os.path.join(workspace_dir, "journal.jsonl")
    validate_path(journal_path, project_root)
    with open(journal_path, "w") as f:
        pass  # Create empty file
    created_paths.append(journal_path)

    # Create index.json with initial schema
    now = datetime.now(timezone.utc).isoformat()
    index_path = os.path.join(workspace_dir, "index.json")
    validate_path(index_path, project_root)
    index_data = {
        "schema_version": "1.0.0",
        "updated_at": now,
        "slots": {},
    }
    atomic_write(index_path, index_data)
    created_paths.append(index_path)

    # Create config.json with initial configuration
    config_path = os.path.join(workspace_dir, "config.json")
    validate_path(config_path, project_root)
    config_data = {
        "schema_version": "1.0.0",
        "workspace_version": "0.1.0",
        "created_at": now,
    }
    atomic_write(config_path, config_data)
    created_paths.append(config_path)

    # Run cleanup for any orphaned temps (crash recovery)
    result["cleaned_temps"] = cleanup_orphaned_temps(workspace_dir)

    result["status"] = "created"
    result["paths"] = created_paths
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize .system-dev/ workspace"
    )
    parser.add_argument(
        "--project-root",
        required=True,
        help="Path to the project root directory",
    )
    args = parser.parse_args()

    result = init_workspace(os.path.abspath(args.project_root))
    if result["status"] == "created":
        print("Workspace created successfully.")
        for path in result["paths"]:
            print(f"  {path}")
    elif result["status"] == "exists":
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    if result["cleaned_temps"]:
        print("Cleaned orphaned temp files:")
        for path in result["cleaned_temps"]:
            print(f"  {path}")
