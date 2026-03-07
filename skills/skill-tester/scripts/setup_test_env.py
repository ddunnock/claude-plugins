#!/usr/bin/env python3
"""setup_test_env.py — Validate skill structure and initialize test environment.

Runs comprehensive validation checks before skill testing begins:
  1. Thorough path validation (reject traversal, verify existence)
  2. Structural pre-validation (SKILL.md, plugin.json, SECURITY.md)
  3. Session directory scaffolding with full structure
  4. Sandbox environment setup for isolated script execution

Must complete before inventory phase (Phase 2). Outputs manifest.json to
the session directory with validation results.

Usage:
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup_test_env.py \\
    --skill-path /path/to/skill \\
    --session-dir sessions/my-skill_20260306_120000 \\
    --mode full
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Import shared utilities (located in same directory)
from shared_io import (
    _validate_dir_path,
    _validate_path,
    _save_json,
    _load_json,
)
from schemas import MANIFEST_SCHEMA


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FILES = {
    "SKILL.md": {"severity": "error", "description": "Skill instructions file"},
    ".claude-plugin/plugin.json": {"severity": "error", "description": "Plugin manifest"},
    "SECURITY.md": {"severity": "warning", "description": "Security documentation"},
}

VALID_MODES = {"full", "audit", "trace", "report"}

PLACEHOLDER_FILES = [
    "inventory.json",
    "scan_results.json",
    "api_log.jsonl",
    "script_runs.jsonl",
    "security_report.json",
    "code_review.json",
    "prompt_lint.json",
    "prompt_review.json",
    "report.html",
]

REPORT_ROOT_CHOICES = ["sessions/", "~/.claude/tests/", ".claude/tests/"]


# ---------------------------------------------------------------------------
# Path Validation
# ---------------------------------------------------------------------------

def validate_skill_path(skill_path: str) -> tuple[str, list[str], list[str]]:
    """Validate the skill directory path thoroughly.

    Args:
        skill_path: User-supplied path to skill directory.

    Returns:
        Tuple of (resolved_path, errors, warnings).
        resolved_path is the absolute path string.
        errors is a list of validation error messages.
        warnings is a list of validation warning messages.
    """
    errors = []
    warnings = []

    # Check for empty string
    if not skill_path or not skill_path.strip():
        errors.append("Skill path cannot be empty")
        return "", errors, warnings

    try:
        resolved = _validate_dir_path(skill_path)
    except ValueError as e:
        errors.append(f"Path validation failed: {e}")
        return "", errors, warnings

    # Check if path exists
    if not Path(resolved).exists():
        errors.append(f"Skill path does not exist: {resolved}")
        return resolved, errors, warnings

    if not Path(resolved).is_dir():
        errors.append(f"Skill path is not a directory: {resolved}")
        return resolved, errors, warnings

    # Check permissions
    if not os.access(resolved, os.R_OK):
        errors.append(f"Skill directory is not readable: {resolved}")

    if not os.access(resolved, os.X_OK):
        warnings.append(f"Skill directory is not executable (may affect directory listing)")

    # Check for system directories (defensive check)
    # Resolve system dirs too — macOS symlinks e.g. /var -> /private/var
    system_dirs = {"/", "/bin", "/usr", "/etc", "/var", "/sys", "/proc", "/dev"}
    resolved_system_dirs = {os.path.realpath(d) for d in system_dirs} | system_dirs
    if resolved in resolved_system_dirs:
        errors.append(f"Refusing to test system directory: {resolved}")

    return resolved, errors, warnings


# ---------------------------------------------------------------------------
# Structural Validation
# ---------------------------------------------------------------------------

def check_required_files(skill_root: Path) -> tuple[dict, list[str], list[str]]:
    """Check for required files in the skill directory.

    Args:
        skill_root: Resolved Path to the skill directory.

    Returns:
        Tuple of (file_status, errors, warnings).
        file_status is a dict mapping filenames to presence booleans.
        errors is a list of missing required files.
        warnings is a list of missing optional files.
    """
    errors = []
    warnings = []
    file_status = {}

    for filename, info in REQUIRED_FILES.items():
        file_path = skill_root / filename
        exists = file_path.exists()
        file_status[filename] = exists

        if not exists:
            message = f"Required file missing: {filename} — {info['description']}"
            if info["severity"] == "error":
                errors.append(message)
            else:
                warnings.append(message)

    return file_status, errors, warnings


def validate_plugin_json(skill_root: Path) -> tuple[bool, dict, list[str]]:
    """Validate the plugin.json file structure.

    Args:
        skill_root: Resolved Path to the skill directory.

    Returns:
        Tuple of (is_valid, plugin_data, errors).
        is_valid is True if plugin.json parses and has required fields.
        plugin_data is the parsed JSON (empty dict if invalid).
        errors is a list of validation error messages.
    """
    plugin_path = skill_root / ".claude-plugin" / "plugin.json"
    errors = []

    if not plugin_path.exists():
        return False, {}, ["plugin.json does not exist"]

    try:
        with open(plugin_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"plugin.json is not valid JSON: {e}")
        return False, {}, errors
    except OSError as e:
        errors.append(f"Cannot read plugin.json: {e}")
        return False, {}, errors

    # Check required fields
    required_fields = ["name", "version", "description"]
    for field in required_fields:
        if field not in data:
            errors.append(f"plugin.json missing required field: '{field}'")

    if errors:
        return False, data, errors

    return True, data, []


def count_scripts(skill_root: Path) -> int:
    """Count the number of script files in the skill directory.

    Args:
        skill_root: Resolved Path to the skill directory.

    Returns:
        Number of script files found.
    """
    script_extensions = {".py", ".sh", ".js", ".ts", ".bash"}
    count = 0
    for file_path in skill_root.rglob("*"):
        if file_path.is_file() and file_path.suffix in script_extensions:
            # Skip test files and directories
            relative_parts = file_path.relative_to(skill_root).parts
            if not any(part.startswith("test") for part in relative_parts):
                count += 1
    return count


# ---------------------------------------------------------------------------
# Session Directory Setup
# ---------------------------------------------------------------------------

def create_session_structure(session_dir: str, sandbox_subdir: str = "sandbox") -> tuple[str, list[str]]:
    """Create the full session directory structure with placeholders.

    Args:
        session_dir: Path to the session directory.
        sandbox_subdir: Name of the sandbox subdirectory.

    Returns:
        Tuple of (sandbox_path, errors).
        sandbox_path is the absolute path to the sandbox directory.
        errors is a list of setup error messages.
    """
    errors = []
    session_path = Path(session_dir).resolve()

    # Create main session directory
    try:
        session_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        errors.append(f"Cannot create session directory: {e}")
        return "", errors

    # Create sandbox directory
    sandbox_path = session_path / sandbox_subdir
    try:
        sandbox_path.mkdir(exist_ok=True)
    except OSError as e:
        errors.append(f"Cannot create sandbox directory: {e}")
        return str(sandbox_path), errors

    # Create placeholder files (empty or minimal content)
    for filename in PLACEHOLDER_FILES:
        file_path = session_path / filename
        if not file_path.exists():
            try:
                if filename.endswith(".json"):
                    file_path.write_text("{}\n", encoding="utf-8")
                elif filename.endswith(".jsonl"):
                    file_path.write_text("", encoding="utf-8")
                elif filename.endswith(".html"):
                    file_path.write_text("<!DOCTYPE html>\n<html><head><title>Report Pending</title></head><body><p>Report generation pending...</p></body></html>\n", encoding="utf-8")
            except OSError as e:
                errors.append(f"Cannot create placeholder {filename}: {e}")

    return str(sandbox_path), errors


# ---------------------------------------------------------------------------
# Main Validation Flow
# ---------------------------------------------------------------------------

def run_validation(skill_path: str, session_dir: str, mode: str,
                   report_root: str | None = None) -> dict:
    """Execute all validation checks and set up test environment.

    Args:
        skill_path: User-supplied path to skill directory.
        session_dir: Path to session directory for output.
        mode: Analysis mode (full, audit, trace, report).
        report_root: Optional report root choice (e.g. "~/.claude/tests/").

    Returns:
        Manifest dictionary with validation results.

    Raises:
        ValueError: If critical validation checks fail.
    """
    all_errors = []
    all_warnings = []

    # Step 1: Validate skill path
    print("[setup_test_env] Step 1/5: Validating skill path...", file=sys.stderr)
    resolved_path, path_errors, path_warnings = validate_skill_path(skill_path)
    all_errors.extend(path_errors)
    all_warnings.extend(path_warnings)

    if path_errors:
        # Critical failure — cannot proceed
        raise ValueError(f"Path validation failed: {'; '.join(path_errors)}")

    skill_root = Path(resolved_path)

    # Step 2: Check required files
    print("[setup_test_env] Step 2/5: Checking required files...", file=sys.stderr)
    file_status, file_errors, file_warnings = check_required_files(skill_root)
    all_errors.extend(file_errors)
    all_warnings.extend(file_warnings)

    # Step 3: Validate plugin.json
    print("[setup_test_env] Step 3/5: Validating plugin.json...", file=sys.stderr)
    plugin_valid, plugin_data, plugin_errors = validate_plugin_json(skill_root)
    all_errors.extend(plugin_errors)

    # Step 4: Count scripts
    print("[setup_test_env] Step 4/5: Counting scripts...", file=sys.stderr)
    script_count = count_scripts(skill_root)
    print(f"  Found {script_count} script file(s)", file=sys.stderr)

    # Step 5: Create session structure
    print("[setup_test_env] Step 5/5: Creating session structure...", file=sys.stderr)
    sandbox_path, setup_errors = create_session_structure(session_dir)
    all_errors.extend(setup_errors)

    if setup_errors:
        raise ValueError(f"Session setup failed: {'; '.join(setup_errors)}")

    # Build manifest
    manifest = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "skill_path": resolved_path,
        "session_dir": str(Path(session_dir).resolve()),
        "validation": {
            "path_valid": not bool(path_errors),
            "skill_md_present": file_status.get("SKILL.md", False),
            "plugin_json_present": file_status.get(".claude-plugin/plugin.json", False),
            "plugin_json_valid": plugin_valid,
            "security_md_present": file_status.get("SECURITY.md", False),
            "scripts_count": script_count,
            "sandbox_path": sandbox_path,
        },
        "errors": all_errors,
        "warnings": all_warnings,
    }

    if report_root:
        manifest["report_root"] = report_root

    # Write manifest.json
    manifest_path = Path(session_dir) / "manifest.json"
    try:
        _save_json(str(manifest_path), manifest, schema=MANIFEST_SCHEMA)
        print(f"[setup_test_env] Manifest written to {manifest_path}", file=sys.stderr)
    except ValueError as e:
        raise ValueError(f"Manifest schema validation failed: {e}")

    # Report summary
    print(f"[setup_test_env] Validation complete:", file=sys.stderr)
    print(f"  Errors: {len(all_errors)}", file=sys.stderr)
    print(f"  Warnings: {len(all_warnings)}", file=sys.stderr)
    print(f"  Sandbox: {sandbox_path}", file=sys.stderr)

    if all_errors:
        raise ValueError(f"Validation failed with {len(all_errors)} error(s)")

    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point for the script CLI."""
    parser = argparse.ArgumentParser(
        description="Skill Tester — Test Environment Setup and Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Validates skill structure and creates session directory with\n"
            "full scaffolding. Must run before inventory phase."
        ),
    )
    parser.add_argument(
        "--skill-path",
        required=True,
        help="Path to the skill directory to validate.",
    )
    parser.add_argument(
        "--session-dir",
        required=True,
        help="Session directory path for output files.",
    )
    parser.add_argument(
        "--mode",
        choices=list(VALID_MODES),
        default="full",
        help="Analysis mode (default: full).",
    )
    parser.add_argument(
        "--report-root",
        choices=REPORT_ROOT_CHOICES,
        default=None,
        help="Report root directory (default: sessions/).",
    )

    args = parser.parse_args()

    try:
        manifest = run_validation(
            args.skill_path, args.session_dir, args.mode,
            report_root=args.report_root,
        )
        # Output summary to stdout for Claude to parse
        summary = {
            "status": "success",
            "errors": len(manifest["errors"]),
            "warnings": len(manifest["warnings"]),
            "sandbox": manifest["validation"]["sandbox_path"],
        }
        print(json.dumps(summary, indent=2))
        sys.exit(0)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        summary = {"status": "failed", "error": str(e)}
        print(json.dumps(summary, indent=2))
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()