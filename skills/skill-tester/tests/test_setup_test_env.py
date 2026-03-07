"""Tests for setup_test_env.py validation and setup script.

Covers all five test categories:
  1. Unit tests
  2. Security tests
  3. Edge cases
  4. Performance tests
  5. Chaos tests
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from setup_test_env import (
    validate_skill_path,
    check_required_files,
    validate_plugin_json,
    count_scripts,
    create_session_structure,
    run_validation,
)


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

def test_validate_skill_path_valid(tmp_skill_dir):
    """validate_skill_path returns resolved path for valid directory."""
    resolved, errors, warnings = validate_skill_path(str(tmp_skill_dir))
    assert resolved == str(tmp_skill_dir.resolve())
    assert errors == []
    assert warnings == []


def test_validate_skill_path_resolves_relative(tmp_skill_dir):
    """validate_skill_path resolves relative paths correctly."""
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_skill_dir.parent)
        resolved, errors, warnings = validate_skill_path(tmp_skill_dir.name)
        assert resolved == str(tmp_skill_dir.resolve())
        assert errors == []
    finally:
        os.chdir(original_cwd)


def test_check_required_files_all_present(tmp_skill_dir):
    """check_required_files returns no errors when all files present."""
    file_status, errors, warnings = check_required_files(tmp_skill_dir)

    assert file_status["SKILL.md"] is True
    assert file_status[".claude-plugin/plugin.json"] is True
    assert file_status["SECURITY.md"] is True
    assert errors == []


def test_check_required_files_missing_skill_md(tmp_path):
    """check_required_files detects missing SKILL.md."""
    skill_dir = tmp_path / "incomplete-skill"
    skill_dir.mkdir()
    (skill_dir / ".claude-plugin").mkdir()

    file_status, errors, warnings = check_required_files(skill_dir)

    assert file_status["SKILL.md"] is False
    assert any("SKILL.md" in e for e in errors)


def test_validate_plugin_json_valid(tmp_skill_dir):
    """validate_plugin_json returns True for valid plugin.json."""
    is_valid, data, errors = validate_plugin_json(tmp_skill_dir)

    assert is_valid is True
    assert data["name"] == "test-skill"
    assert data["version"] == "1.0.0"
    assert errors == []


def test_validate_plugin_json_missing_file(tmp_path):
    """validate_plugin_json detects missing plugin.json."""
    skill_dir = tmp_path / "no-plugin"
    skill_dir.mkdir()

    is_valid, data, errors = validate_plugin_json(skill_dir)

    assert is_valid is False
    assert data == {}
    assert any("does not exist" in e for e in errors)


def test_count_scripts_finds_scripts(tmp_skill_dir):
    """count_scripts counts script files in the skill directory."""
    count = count_scripts(tmp_skill_dir)
    assert count == 1  # tmp_skill_dir has scripts/example.py


def test_count_scripts_empty_skill(minimal_skill_dir):
    """count_scripts returns 0 for skill with no scripts."""
    count = count_scripts(minimal_skill_dir)
    assert count == 0


def test_create_session_structure_creates_directories(tmp_path):
    """create_session_structure creates session and sandbox directories."""
    session_dir = tmp_path / "session"
    sandbox_path, errors = create_session_structure(str(session_dir))

    assert errors == []
    assert Path(session_dir).exists()
    assert Path(sandbox_path).exists()
    assert Path(sandbox_path).name == "sandbox"


def test_create_session_structure_creates_placeholders(tmp_path):
    """create_session_structure creates placeholder files."""
    session_dir = tmp_path / "session"
    sandbox_path, errors = create_session_structure(str(session_dir))

    assert errors == []
    assert (Path(session_dir) / "inventory.json").exists()
    assert (Path(session_dir) / "scan_results.json").exists()
    assert (Path(session_dir) / "api_log.jsonl").exists()
    assert (Path(session_dir) / "script_runs.jsonl").exists()


def test_run_validation_success(tmp_skill_dir, tmp_session_dir):
    """run_validation completes successfully for valid skill."""
    manifest = run_validation(
        str(tmp_skill_dir),
        str(tmp_session_dir),
        "full"
    )

    assert manifest["validation"]["path_valid"] is True
    assert manifest["validation"]["skill_md_present"] is True
    assert manifest["validation"]["plugin_json_valid"] is True
    assert len(manifest["errors"]) == 0


def test_run_validation_writes_manifest(tmp_skill_dir, tmp_session_dir):
    """run_validation writes manifest.json to session directory."""
    run_validation(str(tmp_skill_dir), str(tmp_session_dir), "full")

    manifest_path = tmp_session_dir / "manifest.json"
    assert manifest_path.exists()

    with open(manifest_path) as f:
        manifest = json.load(f)

    assert "validated_at" in manifest
    assert "skill_path" in manifest
    assert "validation" in manifest


# ---------------------------------------------------------------------------
# Security Tests
# ---------------------------------------------------------------------------

def test_validate_skill_path_rejects_traversal():
    """validate_skill_path rejects paths containing '..'."""
    resolved, errors, warnings = validate_skill_path("../../../etc")
    assert len(errors) > 0
    assert any("traversal" in e.lower() for e in errors)


def test_validate_skill_path_rejects_system_dirs():
    """validate_skill_path rejects system directories."""
    system_dirs = ["/bin", "/usr", "/etc", "/var"]

    for sys_dir in system_dirs:
        resolved, errors, warnings = validate_skill_path(sys_dir)
        # Should have errors about system directory
        assert len(errors) > 0
        assert any("system directory" in e.lower() for e in errors)


def test_validate_plugin_json_rejects_malicious_content(tmp_path):
    """validate_plugin_json safely handles malicious JSON content."""
    skill_dir = tmp_path / "malicious-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # Malicious content attempting code injection
    malicious_json = '{"name": "test", "version": "1.0", "__import__": "os"}'
    (plugin_dir / "plugin.json").write_text(malicious_json)

    is_valid, data, errors = validate_plugin_json(skill_dir)

    # Should detect missing required fields (description, skill)
    assert len(errors) > 0
    # Malicious fields are ignored (just loaded as strings)
    if "__import__" in data:
        assert isinstance(data["__import__"], str)


def test_run_validation_fails_on_traversal(tmp_session_dir):
    """run_validation raises ValueError for path traversal attempts."""
    with pytest.raises(ValueError, match="traversal|validation failed"):
        run_validation("../../../etc", str(tmp_session_dir), "full")


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

def test_validate_skill_path_nonexistent():
    """validate_skill_path detects non-existent paths."""
    resolved, errors, warnings = validate_skill_path("/nonexistent/path/to/skill")
    assert len(errors) > 0
    assert any("does not exist" in e.lower() for e in errors)


def test_validate_skill_path_file_not_directory(tmp_path):
    """validate_skill_path detects when path is a file, not directory."""
    test_file = tmp_path / "file.txt"
    test_file.write_text("not a directory")

    resolved, errors, warnings = validate_skill_path(str(test_file))
    assert len(errors) > 0
    assert any("not a directory" in e.lower() for e in errors)


def test_check_required_files_warns_missing_security_md(tmp_path):
    """check_required_files warns (not errors) for missing SECURITY.md."""
    skill_dir = tmp_path / "no-security-skill"
    skill_dir.mkdir()

    # Create required error-level files
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text("{}")
    (skill_dir / "SKILL.md").write_text("# Test")

    file_status, errors, warnings = check_required_files(skill_dir)

    assert file_status["SECURITY.md"] is False
    # SECURITY.md should generate warning, not error
    assert any("SECURITY.md" in w for w in warnings)


def test_validate_plugin_json_missing_required_fields(tmp_path):
    """validate_plugin_json detects missing required fields."""
    skill_dir = tmp_path / "incomplete-plugin-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # Valid JSON but missing required fields
    incomplete_data = {"name": "test"}  # missing version, description, skill
    (plugin_dir / "plugin.json").write_text(json.dumps(incomplete_data))

    is_valid, data, errors = validate_plugin_json(skill_dir)

    assert is_valid is False
    assert len(errors) >= 2  # version, description


def test_count_scripts_skips_test_files(tmp_path):
    """count_scripts excludes files in test directories."""
    skill_dir = tmp_path / "skill-with-tests"
    skill_dir.mkdir()

    # Create scripts directory with one script
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "main.py").write_text("#!/usr/bin/env python3\n")

    # Create tests directory with test scripts (should be skipped)
    tests_dir = skill_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("#!/usr/bin/env python3\n")

    count = count_scripts(skill_dir)
    assert count == 1  # Only scripts/main.py, not tests/test_main.py


def test_create_session_structure_idempotent(tmp_path):
    """create_session_structure can be called multiple times safely."""
    session_dir = tmp_path / "session"

    # First call
    sandbox_path1, errors1 = create_session_structure(str(session_dir))
    assert errors1 == []

    # Second call should succeed without errors
    sandbox_path2, errors2 = create_session_structure(str(session_dir))
    assert errors2 == []
    assert sandbox_path1 == sandbox_path2


def test_run_validation_with_warnings_succeeds(minimal_skill_dir, tmp_session_dir):
    """run_validation succeeds even with warnings (e.g., missing SECURITY.md)."""
    # minimal_skill_dir has no SECURITY.md, should generate warning
    manifest = run_validation(
        str(minimal_skill_dir),
        str(tmp_session_dir),
        "full"
    )

    # Should succeed despite warnings
    assert manifest["validation"]["path_valid"] is True
    # May have warnings about SECURITY.md
    assert len(manifest["errors"]) == 0


def test_validate_plugin_json_corrupted_json(invalid_plugin_json_skill):
    """validate_plugin_json handles corrupted JSON gracefully."""
    is_valid, data, errors = validate_plugin_json(invalid_plugin_json_skill)

    assert is_valid is False
    assert data == {}
    assert len(errors) > 0
    assert any("not valid JSON" in e for e in errors)


# ---------------------------------------------------------------------------
# Performance Tests
# ---------------------------------------------------------------------------

def test_count_scripts_large_skill(tmp_path):
    """count_scripts handles skills with many scripts efficiently."""
    import time

    skill_dir = tmp_path / "large-skill"
    skill_dir.mkdir()
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()

    # Create 100 script files
    for i in range(100):
        (scripts_dir / f"script_{i}.py").write_text(f"# Script {i}\n")

    start = time.monotonic()
    count = count_scripts(skill_dir)
    elapsed = time.monotonic() - start

    assert count == 100
    assert elapsed < 1.0, f"Took {elapsed:.2f}s, expected < 1s"


def test_create_session_structure_many_calls(tmp_path):
    """create_session_structure handles multiple sessions efficiently."""
    import time

    start = time.monotonic()
    for i in range(50):
        session_dir = tmp_path / f"session_{i}"
        sandbox_path, errors = create_session_structure(str(session_dir))
        assert errors == []

    elapsed = time.monotonic() - start
    assert elapsed < 5.0, f"Took {elapsed:.2f}s, expected < 5s"


# ---------------------------------------------------------------------------
# Chaos Tests
# ---------------------------------------------------------------------------

def test_validate_plugin_json_unreadable_file(tmp_path):
    """validate_plugin_json handles unreadable files gracefully."""
    import os

    skill_dir = tmp_path / "unreadable-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    plugin_file = plugin_dir / "plugin.json"
    plugin_file.write_text('{"name": "test"}')

    # Make file unreadable
    os.chmod(plugin_file, 0o000)

    try:
        is_valid, data, errors = validate_plugin_json(skill_dir)
        # Should handle gracefully
        assert is_valid is False
        assert len(errors) > 0
    finally:
        # Restore permissions for cleanup
        os.chmod(plugin_file, 0o644)


def test_create_session_structure_readonly_parent(tmp_path):
    """create_session_structure handles read-only parent directory."""
    import os

    readonly_parent = tmp_path / "readonly"
    readonly_parent.mkdir()
    session_dir = readonly_parent / "session"

    # Make parent read-only
    os.chmod(readonly_parent, 0o555)

    try:
        sandbox_path, errors = create_session_structure(str(session_dir))
        # Should report errors
        assert len(errors) > 0
    finally:
        # Restore permissions for cleanup
        os.chmod(readonly_parent, 0o755)


def test_run_validation_invalid_session_dir(tmp_skill_dir):
    """run_validation raises ValueError if session dir cannot be created."""
    # Use /dev/null as invalid session directory
    with pytest.raises(ValueError):
        run_validation(str(tmp_skill_dir), "/dev/null/invalid_session", "full")


def test_validate_skill_path_empty_string():
    """validate_skill_path handles empty string path."""
    resolved, errors, warnings = validate_skill_path("")
    assert len(errors) > 0


def test_validate_plugin_json_empty_file(tmp_path):
    """validate_plugin_json handles completely empty file."""
    skill_dir = tmp_path / "empty-plugin-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # Empty file
    (plugin_dir / "plugin.json").write_text("")

    is_valid, data, errors = validate_plugin_json(skill_dir)

    assert is_valid is False
    assert len(errors) > 0
    assert any("not valid JSON" in e for e in errors)