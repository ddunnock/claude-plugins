#!/usr/bin/env python3
"""
Memory File Selector Script

Selects appropriate memory files for a project based on:
- Detected tech stack (from detect_stack.py)
- User overrides
- Project requirements

Copies selected memory files from template location to project .claude/memory/
"""

import sys
import json
import os
import shutil
from pathlib import Path
from typing import TypedDict

# Import detect_stack if available, otherwise define the types
try:
    from detect_stack import detect_stack, DetectionResult
except ImportError:
    class DetectionResult(TypedDict):
        primary_language: str | None
        frameworks: list[str]
        detections: list[dict]
        memory_files: list[str]

    def detect_stack(project_path: str | Path) -> DetectionResult:
        """Stub for when module import fails."""
        return {
            "primary_language": None,
            "frameworks": [],
            "detections": [],
            "memory_files": [
                "constitution.md",
                "documentation.md",
                "git-cicd.md",
                "security.md",
            ]
        }


# All available memory files with descriptions
MEMORY_FILE_CATALOG = {
    # Universal (always included)
    "constitution.md": {
        "category": "universal",
        "description": "Core development principles and constraints",
        "required": True,
    },
    "documentation.md": {
        "category": "universal",
        "description": "Documentation standards and patterns",
        "required": True,
    },
    "git-cicd.md": {
        "category": "universal",
        "description": "Git workflow and CI/CD practices",
        "required": True,
    },
    "security.md": {
        "category": "universal",
        "description": "Security requirements and best practices",
        "required": True,
    },
    "testing.md": {
        "category": "universal",
        "description": "Testing strategies and standards",
        "required": True,
    },

    # Tech-specific
    "typescript.md": {
        "category": "language",
        "description": "TypeScript/JavaScript coding standards",
        "required": False,
        "triggers": ["typescript", "javascript", "node"],
    },
    "react-nextjs.md": {
        "category": "framework",
        "description": "React and Next.js patterns",
        "required": False,
        "triggers": ["react", "nextjs"],
    },
    "tailwind-shadcn.md": {
        "category": "styling",
        "description": "Tailwind CSS and shadcn/ui guidelines",
        "required": False,
        "triggers": ["tailwind", "shadcn"],
    },
    "python.md": {
        "category": "language",
        "description": "Python coding standards",
        "required": False,
        "triggers": ["python", "django", "flask", "fastapi"],
    },
    "rust.md": {
        "category": "language",
        "description": "Rust coding standards",
        "required": False,
        "triggers": ["rust"],
    },
}


# SelectionResult defined below copy_memory_files for forward reference


def get_universal_files() -> list[str]:
    """Return list of universal (always required) memory files."""
    return [
        name for name, info in MEMORY_FILE_CATALOG.items()
        if info.get("required", False)
    ]


def get_tech_specific_files(technologies: list[str]) -> list[str]:
    """Return tech-specific files triggered by detected technologies."""
    selected = []
    tech_set = set(technologies)

    for name, info in MEMORY_FILE_CATALOG.items():
        if info.get("required"):
            continue  # Skip universal files
        triggers = info.get("triggers", [])
        if any(t in tech_set for t in triggers):
            selected.append(name)

    return selected


def select_memory_files(
    project_path: str | Path,
    override_techs: list[str] | None = None,
    include_all: bool = False
) -> list[str]:
    """
    Select memory files based on project tech stack.

    Args:
        project_path: Path to project root
        override_techs: Optional list of technologies to use instead of detection
        include_all: If True, include all available memory files

    Returns:
        List of selected memory file names
    """
    if include_all:
        return list(MEMORY_FILE_CATALOG.keys())

    universal = get_universal_files()

    if override_techs:
        tech_specific = get_tech_specific_files(override_techs)
    else:
        detection = detect_stack(project_path)
        # Extract technologies from detections
        techs = [d["technology"] for d in detection.get("detections", [])]
        tech_specific = get_tech_specific_files(techs)

    # Combine and deduplicate
    all_files = list(dict.fromkeys(universal + tech_specific))
    return sorted(all_files)


def find_memory_template_source() -> Path | None:
    """
    Find the source location for memory file templates.

    Searches in order:
    1. Environment variable SPECKIT_MEMORY_SOURCE
    2. Skill's own assets/memory/ directory (self-contained)
    3. ~/.claude/memory-templates/ (user override)
    """
    # Check environment variable
    env_path = os.environ.get("SPECKIT_MEMORY_SOURCE")
    if env_path:
        path = Path(env_path)
        if path.is_dir():
            return path

    # Check skill's own assets/memory directory (self-contained)
    script_dir = Path(__file__).parent
    skill_memory_path = script_dir / ".." / "assets" / "memory"
    if skill_memory_path.is_dir():
        return skill_memory_path.resolve()

    # Check home directory (user override)
    home_path = Path.home() / ".claude" / "memory-templates"
    if home_path.is_dir():
        return home_path

    return None


class SelectionResult(TypedDict):
    selected: list[str]
    universal: list[str]
    tech_specific: list[str]
    source_path: str | None
    target_path: str
    copied: list[str]
    skipped: list[str]  # Existing files that were skipped (unchanged or customized)
    updated: list[str]  # Existing files that were updated (not customized by user)
    customized: list[str]  # Files the user has customized (preserved)
    errors: list[str]


def get_file_hash(path: Path) -> str:
    """Get a simple hash of file contents for comparison."""
    import hashlib
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


MANIFEST_FILENAME = ".manifest.json"


def load_manifest(target_dir: Path) -> dict[str, str]:
    """
    Load the hash manifest that tracks original template hashes.

    The manifest stores the hash of each file AT THE TIME IT WAS COPIED.
    This allows us to detect if the user has customized a file:
    - If current_hash == manifest_hash: user hasn't touched it, safe to update
    - If current_hash != manifest_hash: user has customized it, preserve it

    Returns:
        Dict mapping filename to original template hash
    """
    manifest_path = target_dir / MANIFEST_FILENAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def save_manifest(target_dir: Path, manifest: dict[str, str]) -> None:
    """Save the hash manifest to track original template hashes."""
    manifest_path = target_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def is_user_customized(
    target_file: Path,
    manifest: dict[str, str]
) -> bool:
    """
    Check if a file has been customized by the user.

    A file is considered customized if:
    - It exists in the manifest AND
    - Its current hash differs from the manifest hash

    If the file doesn't exist in manifest, it's a new file (not customized).
    """
    filename = target_file.name
    if filename not in manifest:
        return False  # No manifest entry = new file, not customized

    original_hash = manifest[filename]
    current_hash = get_file_hash(target_file)

    return current_hash != original_hash


def copy_memory_files(
    project_path: str | Path,
    files: list[str],
    source_path: str | Path | None = None,
    dry_run: bool = False,
    force: bool = False,
    preserve_customizations: bool = True
) -> SelectionResult:
    """
    Copy selected memory files to project .claude/memory/ directory.

    Idempotent: Safe to run on existing projects.
    - Tracks original template hashes in .manifest.json
    - Preserves user-customized files (detected via manifest comparison)
    - Updates unchanged files when template changes
    - Creates only missing files
    - Never deletes existing files

    Args:
        project_path: Path to project root
        files: List of memory file names to copy
        source_path: Optional source directory (auto-detected if None)
        dry_run: If True, don't actually copy files
        force: If True, overwrite ALL files including customized ones
        preserve_customizations: If True, preserve user-customized files (default)

    Returns:
        SelectionResult with details of the operation
    """
    project_path = Path(project_path).resolve()
    target_dir = project_path / ".claude" / "memory"

    # Find source
    if source_path:
        source_dir = Path(source_path).resolve()
    else:
        source_dir = find_memory_template_source()

    result: SelectionResult = {
        "selected": files,
        "universal": [f for f in files if MEMORY_FILE_CATALOG.get(f, {}).get("required")],
        "tech_specific": [f for f in files if not MEMORY_FILE_CATALOG.get(f, {}).get("required")],
        "source_path": str(source_dir) if source_dir else None,
        "target_path": str(target_dir),
        "copied": [],
        "skipped": [],
        "updated": [],
        "customized": [],
        "errors": [],
    }

    if not source_dir:
        result["errors"].append("Could not find memory template source directory")
        return result

    if not source_dir.is_dir():
        result["errors"].append(f"Source directory does not exist: {source_dir}")
        return result

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    # Load manifest for tracking customizations
    manifest = load_manifest(target_dir) if target_dir.exists() else {}
    manifest_updated = False

    for filename in files:
        source_file = source_dir / filename
        target_file = target_dir / filename

        if not source_file.exists():
            result["errors"].append(f"Source file not found: {filename}")
            continue

        source_hash = get_file_hash(source_file)

        # Check if target already exists
        if target_file.exists():
            target_hash = get_file_hash(target_file)

            if source_hash == target_hash:
                # Files are identical - skip (but ensure manifest is up to date)
                if filename not in manifest and not dry_run:
                    manifest[filename] = source_hash
                    manifest_updated = True
                result["skipped"].append(filename)
                continue

            # File differs - check if user has customized it
            if preserve_customizations and not force:
                if is_user_customized(target_file, manifest):
                    # User has modified this file - preserve their customizations
                    result["customized"].append(filename)
                    continue

            # File differs but user hasn't customized it (template changed)
            # OR force=True - update it
            action = "updated"
            result_list = result["updated"]
        else:
            # New file
            action = "copied"
            result_list = result["copied"]

        if dry_run:
            result_list.append(filename)
        else:
            try:
                shutil.copy2(source_file, target_file)
                result_list.append(filename)
                # Record the template hash in manifest
                manifest[filename] = source_hash
                manifest_updated = True
            except Exception as e:
                result["errors"].append(f"Failed to {action} {filename}: {e}")

    # Save updated manifest
    if manifest_updated and not dry_run:
        try:
            save_manifest(target_dir, manifest)
        except Exception as e:
            result["errors"].append(f"Failed to save manifest: {e}")

    return result


def generate_manifest(
    project_path: str | Path,
    files: list[str],
    detection_result: DetectionResult | None = None
) -> str:
    """
    Generate a manifest describing the selected memory files.

    Returns markdown content for .claude/memory/MANIFEST.md
    """
    lines = [
        "# Memory Files Manifest",
        "",
        "This file documents the memory files selected for this project.",
        "",
        "## Selection Criteria",
        "",
    ]

    if detection_result:
        primary = detection_result.get("primary_language", "Unknown")
        frameworks = detection_result.get("frameworks", [])
        lines.append(f"- **Primary Language**: {primary or 'Not detected'}")
        lines.append(f"- **Frameworks**: {', '.join(frameworks) if frameworks else 'None detected'}")
        lines.append("")

    lines.extend([
        "## Universal Files (Always Included)",
        "",
    ])

    universal = [f for f in files if MEMORY_FILE_CATALOG.get(f, {}).get("required")]
    for f in universal:
        desc = MEMORY_FILE_CATALOG.get(f, {}).get("description", "")
        lines.append(f"- `{f}` - {desc}")

    lines.append("")

    tech_specific = [f for f in files if not MEMORY_FILE_CATALOG.get(f, {}).get("required")]
    if tech_specific:
        lines.extend([
            "## Tech-Specific Files",
            "",
        ])
        for f in tech_specific:
            desc = MEMORY_FILE_CATALOG.get(f, {}).get("description", "")
            lines.append(f"- `{f}` - {desc}")
        lines.append("")

    lines.extend([
        "## Usage",
        "",
        "These files are referenced by speckit commands to ensure compliance with",
        "project standards. The `constitution.md` file contains the core principles",
        "that govern all development activities.",
        "",
    ])

    return "\n".join(lines)



def _validate_dir_path(dirpath: str, label: str) -> str:
    """Validate directory path: reject traversal. Returns resolved path."""
    resolved = os.path.realpath(dirpath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {dirpath}")
        sys.exit(1)
    return resolved

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Select and copy memory files for a project"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to project root (default: current directory)"
    )
    parser.add_argument(
        "--source",
        help="Source directory for memory templates"
    )
    parser.add_argument(
        "--techs",
        nargs="+",
        help="Override detected technologies"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="include_all",
        help="Include all available memory files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without copying"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_only",
        help="Only list selected files, don't copy"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite all files including customized ones"
    )

    args = parser.parse_args()

    args.project_path = _validate_dir_path(args.project_path, "project path")
    if args.source:
        args.source = _validate_dir_path(args.source, "source directory")

    # Select files
    files = select_memory_files(
        args.project_path,
        override_techs=args.techs,
        include_all=args.include_all
    )

    if args.list_only:
        if args.json:
            print(json.dumps({"selected": files}, indent=2))
        else:
            for f in files:
                print(f)
        return

    # Copy files
    result = copy_memory_files(
        args.project_path,
        files,
        source_path=args.source,
        dry_run=args.dry_run,
        force=args.force
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        prefix = "Would " if args.dry_run else ""

        if result["copied"]:
            print(f"{prefix}Copied (new):")
            for f in result["copied"]:
                print(f"  + {f}")

        if result["updated"]:
            print(f"\n{prefix}Updated (template changed):")
            for f in result["updated"]:
                print(f"  ~ {f}")

        if result["customized"]:
            print(f"\nPreserved (user customized):")
            for f in result["customized"]:
                print(f"  * {f}")

        if result["skipped"]:
            print(f"\nSkipped (unchanged):")
            for f in result["skipped"]:
                print(f"  = {f}")

        if result["errors"]:
            print("\nErrors:")
            for err in result["errors"]:
                print(f"  ! {err}")

        if not any([result["copied"], result["updated"], result["skipped"], result["customized"]]):
            print("No files to process.")


if __name__ == "__main__":
    main()
