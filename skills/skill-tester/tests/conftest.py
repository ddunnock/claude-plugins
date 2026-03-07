"""Shared test fixtures for skill-tester tests."""
import json
from pathlib import Path

import pytest


@pytest.fixture
def tmp_skill_dir(tmp_path):
    """Create a temporary skill directory with standard structure.

    Returns:
        Path to the temporary skill directory.
    """
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()

    # Create .claude-plugin directory
    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # Create plugin.json
    plugin_data = {
        "name": "test-skill",
        "version": "1.0.0",
        "description": "A test skill for validation",
        "skill": "SKILL.md",
        "scripts": ["scripts/example.py"],
    }
    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_data, indent=2))

    # Create SKILL.md
    skill_md_content = """---
name: test-skill
description: A test skill
version: 1.0.0
---

# Test Skill

This is a test skill.

<security>
  <rule name="test">Test security rule</rule>
</security>

<paths>
  <pattern name="script">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/example.py</pattern>
</paths>

<workflow>
  <phase name="test" sequence="1">
    <objective>Test objective</objective>
  </phase>
</workflow>

<behavior>
  <rule id="B1" priority="high">Test behavior rule</rule>
</behavior>
"""
    (skill_dir / "SKILL.md").write_text(skill_md_content)

    # Create SECURITY.md
    (skill_dir / "SECURITY.md").write_text("# Security\n\nTest security documentation.")

    # Create scripts directory with example script
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "example.py").write_text("#!/usr/bin/env python3\nprint('Hello')\n")

    return skill_dir


@pytest.fixture
def tmp_session_dir(tmp_path):
    """Create a temporary session directory.

    Returns:
        Path to the temporary session directory.
    """
    session_dir = tmp_path / "sessions" / "test-skill_20260306_120000"
    session_dir.mkdir(parents=True)
    return session_dir


@pytest.fixture
def minimal_skill_dir(tmp_path):
    """Create a minimal skill directory with only required files.

    Returns:
        Path to the minimal skill directory.
    """
    skill_dir = tmp_path / "minimal-skill"
    skill_dir.mkdir()

    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    plugin_data = {
        "name": "minimal-skill",
        "version": "1.0.0",
        "description": "Minimal test skill",
        "skill": "SKILL.md",
    }
    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_data, indent=2))

    (skill_dir / "SKILL.md").write_text("---\nname: minimal\n---\n# Minimal\n")

    return skill_dir


@pytest.fixture
def invalid_plugin_json_skill(tmp_path):
    """Create a skill directory with invalid plugin.json.

    Returns:
        Path to the skill directory.
    """
    skill_dir = tmp_path / "invalid-plugin-skill"
    skill_dir.mkdir()

    plugin_dir = skill_dir / ".claude-plugin"
    plugin_dir.mkdir()

    # Invalid JSON
    (plugin_dir / "plugin.json").write_text("{not valid json")

    (skill_dir / "SKILL.md").write_text("# Test\n")

    return skill_dir