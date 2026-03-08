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
    resolve_project_report_root,
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
    is_valid, data, errors, warnings = validate_plugin_json(tmp_skill_dir)

    assert is_valid is True
    assert data["name"] == "test-skill"
    assert data["version"] == "1.0.0"
    assert errors == []


def test_validate_plugin_json_missing_file(tmp_path):
    """validate_plugin_json detects missing plugin.json."""
    skill_dir = tmp_path / "no-plugin"
    skill_dir.mkdir()

    is_valid, data, errors, warnings = validate_plugin_json(skill_dir)

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
    import platform
    if platform.system() == "Windows":
        system_dirs = [r"C:\Windows", r"C:\Windows\System32"]
    else:
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

    is_valid, data, errors, warnings = validate_plugin_json(skill_dir)

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

    is_valid, data, errors, warnings = validate_plugin_json(skill_dir)

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
    is_valid, data, errors, warnings = validate_plugin_json(invalid_plugin_json_skill)

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
        is_valid, data, errors, warnings = validate_plugin_json(skill_dir)
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

    is_valid, data, errors, warnings = validate_plugin_json(skill_dir)

    assert is_valid is False
    assert len(errors) > 0
    assert any("not valid JSON" in e for e in errors)


# ---------------------------------------------------------------------------
# Plugin JSON Schema Validation Tests
# ---------------------------------------------------------------------------

def test_validate_plugin_json_wrong_type_name(tmp_path):
    """validate_plugin_json detects wrong type for 'name' field."""
    skill_dir = tmp_path / "wrong-type-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": 123, "version": "1.0.0", "description": "test"}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is False
    assert any("'name'" in e and "wrong type" in e for e in errors)


def test_validate_plugin_json_wrong_type_keywords(tmp_path):
    """validate_plugin_json detects wrong type for 'keywords' field."""
    skill_dir = tmp_path / "bad-keywords-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "keywords": "should-be-a-list"}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is False
    assert any("'keywords'" in e and "wrong type" in e for e in errors)


def test_validate_plugin_json_unknown_fields_warned(tmp_path):
    """validate_plugin_json warns about unknown fields."""
    skill_dir = tmp_path / "unknown-fields-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "bogus_field": "surprise", "extra": 42}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, warnings = validate_plugin_json(skill_dir)
    assert is_valid is True  # unknown fields are warnings, not errors
    assert any("bogus_field" in w and "unknown" in w for w in warnings)
    assert any("extra" in w and "unknown" in w for w in warnings)


def test_validate_plugin_json_author_nested_validation(tmp_path):
    """validate_plugin_json validates nested author object."""
    skill_dir = tmp_path / "bad-author-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # author present but missing required 'name' field
    data = {"name": "test", "version": "1.0.0", "description": "test",
            "author": {"email": "test@example.com"}}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is False
    assert any("'author'" in e and "'name'" in e for e in errors)


def test_validate_plugin_json_author_wrong_subfield_type(tmp_path):
    """validate_plugin_json detects wrong type in author subfields."""
    skill_dir = tmp_path / "bad-author-type-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "author": {"name": 42}}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is False
    assert any("author.name" in e and "wrong type" in e for e in errors)


def test_validate_plugin_json_polymorphic_commands_string(tmp_path):
    """validate_plugin_json accepts string for commands field."""
    skill_dir = tmp_path / "commands-string-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()
    (skill_dir / "commands").mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "commands": "commands/"}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_plugin_json_polymorphic_commands_list(tmp_path):
    """validate_plugin_json accepts list for commands field."""
    skill_dir = tmp_path / "commands-list-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()
    cmd_dir = skill_dir / "commands"
    cmd_dir.mkdir()
    (cmd_dir / "hello.md").write_text("# Hello")

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "commands": ["commands/hello.md"]}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_plugin_json_nonexistent_component_path_warned(tmp_path):
    """validate_plugin_json warns about component paths that don't exist."""
    skill_dir = tmp_path / "missing-path-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "scripts": ["scripts/nonexistent.py"]}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, warnings = validate_plugin_json(skill_dir)
    assert is_valid is True  # non-existent paths are warnings, not errors
    assert any("non-existent" in w and "nonexistent.py" in w for w in warnings)


def test_validate_plugin_json_hooks_as_object(tmp_path):
    """validate_plugin_json accepts dict for hooks field."""
    skill_dir = tmp_path / "hooks-object-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "hooks": {"PostToolUse": []}}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is True


def test_validate_plugin_json_hooks_as_string(tmp_path):
    """validate_plugin_json accepts string path for hooks field."""
    skill_dir = tmp_path / "hooks-string-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    data = {"name": "test", "version": "1.0.0", "description": "test",
            "hooks": "hooks/hooks.json"}
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is True


def test_validate_plugin_json_complete_valid_schema(tmp_path):
    """validate_plugin_json passes for a fully-populated valid plugin.json."""
    skill_dir = tmp_path / "full-schema-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()
    (skill_dir / "commands").mkdir()
    (skill_dir / "agents").mkdir()
    (skill_dir / "skills").mkdir()

    data = {
        "name": "full-plugin",
        "version": "1.2.0",
        "description": "A fully specified plugin",
        "author": {"name": "Test Author", "email": "test@example.com"},
        "homepage": "https://example.com",
        "repository": "https://github.com/test/plugin",
        "license": "MIT",
        "keywords": ["test", "full"],
        "commands": "commands/",
        "agents": "agents/",
        "skills": "skills/",
    }
    (plugin_dir / "plugin.json").write_text(json.dumps(data))

    is_valid, _, errors, warnings = validate_plugin_json(skill_dir)
    assert is_valid is True
    assert len(errors) == 0
    # No unknown field warnings for official schema fields
    unknown_warnings = [w for w in warnings if "unknown" in w]
    assert len(unknown_warnings) == 0


def test_validate_plugin_json_non_object_root(tmp_path):
    """validate_plugin_json rejects non-object JSON root."""
    skill_dir = tmp_path / "array-root-skill"
    skill_dir.mkdir()
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    (plugin_dir / "plugin.json").write_text('["not", "an", "object"]')

    is_valid, _, errors, _ = validate_plugin_json(skill_dir)
    assert is_valid is False
    assert any("must be a JSON object" in e for e in errors)


# ---------------------------------------------------------------------------
# resolve_project_report_root Tests
# ---------------------------------------------------------------------------

def test_resolve_project_report_root_git_repo(tmp_path):
    """resolve_project_report_root finds git root and returns .claude/tests/."""
    import subprocess
    # Create a git repo
    repo = tmp_path / "my-project"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)
    # Create .claude dir
    (repo / ".claude").mkdir()
    skill_dir = repo / "skills" / "my-skill"
    skill_dir.mkdir(parents=True)

    report_root, warnings = resolve_project_report_root(str(skill_dir))
    assert report_root == str(repo / ".claude" / "tests")
    assert warnings == []


def test_resolve_project_report_root_no_claude_dir(tmp_path):
    """resolve_project_report_root warns when .claude/ doesn't exist."""
    import subprocess
    repo = tmp_path / "no-claude-project"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True)

    report_root, warnings = resolve_project_report_root(str(repo))
    assert report_root == str(repo / ".claude" / "tests")
    assert any("No .claude/ directory" in w for w in warnings)


def test_resolve_project_report_root_not_git_repo(tmp_path):
    """resolve_project_report_root falls back to skill_path when not in git repo."""
    non_repo = tmp_path / "not-a-repo"
    non_repo.mkdir()

    report_root, warnings = resolve_project_report_root(str(non_repo))
    assert report_root == str(non_repo / ".claude" / "tests")
    assert any("Not a git repository" in w for w in warnings)