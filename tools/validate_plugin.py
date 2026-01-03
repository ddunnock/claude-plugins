#!/usr/bin/env python3
"""
Plugin Validator - Validates both skills (SKILL.md) and MCPs (MCP.md)

Usage:
    validate_plugin.py <plugin_directory>

Examples:
    validate_plugin.py skills/documentation-architect
    validate_plugin.py mcps/session-memory
"""

import re
import sys
from pathlib import Path

import yaml

# Reserved words that cannot appear in plugin names
RESERVED_WORDS = {"anthropic", "claude"}

# Allowed properties for SKILL.md frontmatter
SKILL_ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata"}

# Required and optional properties for MCP.md frontmatter
MCP_REQUIRED_PROPERTIES = {"name", "description", "type", "entry_point"}
MCP_OPTIONAL_PROPERTIES = {"dependencies", "config_file", "version"}
MCP_ALLOWED_PROPERTIES = MCP_REQUIRED_PROPERTIES | MCP_OPTIONAL_PROPERTIES


def detect_plugin_type(plugin_path: Path) -> str:
    """Detect plugin type from directory structure."""
    skill_md = plugin_path / "SKILL.md"
    mcp_md = plugin_path / "MCP.md"
    server_py = plugin_path / "server.py"

    if skill_md.exists():
        return "skill"
    elif mcp_md.exists():
        return "mcp"
    elif server_py.exists():
        # Legacy MCP without MCP.md - still support but warn
        print("Warning: MCP detected without MCP.md manifest. Consider adding MCP.md.")
        return "mcp-legacy"
    else:
        return "unknown"


def validate_name(name: str, dir_name: str) -> tuple[bool, str]:
    """Validate plugin name against naming conventions."""
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"

    name = name.strip()
    if not name:
        return False, "Name cannot be empty"

    # Check naming convention (hyphen-case: lowercase with hyphens)
    if not re.match(r"^[a-z0-9-]+$", name):
        return (
            False,
            f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)",
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return (
            False,
            f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens",
        )

    # Check name length (max 64 characters)
    if len(name) > 64:
        return (
            False,
            f"Name is too long ({len(name)} characters). Maximum is 64 characters.",
        )

    # Check for reserved words
    for reserved in RESERVED_WORDS:
        if reserved in name:
            return (
                False,
                f"Name '{name}' contains reserved word '{reserved}'. "
                f"Names cannot contain: {', '.join(sorted(RESERVED_WORDS))}",
            )

    # Check name matches directory name
    if name != dir_name:
        return (
            False,
            f"Name '{name}' does not match directory name '{dir_name}'. "
            f"Plugin name must match the directory name.",
        )

    return True, ""


def validate_description(description: str) -> tuple[bool, str]:
    """Validate plugin description."""
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"

    description = description.strip()
    if not description:
        return False, "Description cannot be empty"

    # Check for angle brackets
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets (< or >)"

    # Check description length (max 1024 characters)
    if len(description) > 1024:
        return (
            False,
            f"Description is too long ({len(description)} characters). Maximum is 1024 characters.",
        )

    return True, ""


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from content."""
    if not content.startswith("---"):
        return None, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return None, "Frontmatter must be a YAML dictionary"
        return frontmatter, ""
    except yaml.YAMLError as e:
        return None, f"Invalid YAML in frontmatter: {e}"


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """Validate a skill plugin."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    frontmatter, error = parse_frontmatter(content)
    if frontmatter is None:
        return False, error

    # Check for unexpected properties
    unexpected_keys = set(frontmatter.keys()) - SKILL_ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(SKILL_ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Validate name
    valid, error = validate_name(frontmatter["name"], skill_path.name)
    if not valid:
        return False, error

    # Validate description
    valid, error = validate_description(frontmatter["description"])
    if not valid:
        return False, error

    return True, "Skill is valid!"


def validate_mcp(mcp_path: Path) -> tuple[bool, str]:
    """Validate an MCP plugin."""
    mcp_md = mcp_path / "MCP.md"
    if not mcp_md.exists():
        return False, "MCP.md not found"

    content = mcp_md.read_text()
    frontmatter, error = parse_frontmatter(content)
    if frontmatter is None:
        return False, error

    # Check for unexpected properties
    unexpected_keys = set(frontmatter.keys()) - MCP_ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in MCP.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(MCP_ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    for field in MCP_REQUIRED_PROPERTIES:
        if field not in frontmatter:
            return False, f"Missing '{field}' in frontmatter"

    # Validate type is 'mcp'
    if frontmatter["type"] != "mcp":
        return False, f"Invalid type: expected 'mcp', got '{frontmatter['type']}'"

    # Validate name
    valid, error = validate_name(frontmatter["name"], mcp_path.name)
    if not valid:
        return False, error

    # Validate description
    valid, error = validate_description(frontmatter["description"])
    if not valid:
        return False, error

    # Verify entry_point exists
    entry_point = mcp_path / frontmatter["entry_point"]
    if not entry_point.exists():
        return False, f"Entry point not found: {frontmatter['entry_point']}"

    # Verify config_file exists if specified
    if "config_file" in frontmatter:
        config_file = mcp_path / frontmatter["config_file"]
        if not config_file.exists():
            return False, f"Config file not found: {frontmatter['config_file']}"

    return True, "MCP is valid!"


def validate_plugin(plugin_path: Path) -> tuple[bool, str, str]:
    """
    Validate any plugin type.

    Returns:
        Tuple of (valid, message, plugin_type)
    """
    plugin_type = detect_plugin_type(plugin_path)

    if plugin_type == "skill":
        valid, message = validate_skill(plugin_path)
        return valid, message, "skill"
    elif plugin_type == "mcp":
        valid, message = validate_mcp(plugin_path)
        return valid, message, "mcp"
    elif plugin_type == "mcp-legacy":
        # Legacy MCP without MCP.md - check for server.py only
        server_py = plugin_path / "server.py"
        if server_py.exists():
            return True, "Legacy MCP (server.py) found. Consider adding MCP.md manifest.", "mcp"
        return False, "server.py not found", "mcp"
    else:
        return False, "Unknown plugin type: no SKILL.md or MCP.md found", "unknown"


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_plugin.py <plugin_directory>")
        print("\nExamples:")
        print("  validate_plugin.py skills/documentation-architect")
        print("  validate_plugin.py mcps/session-memory")
        sys.exit(1)

    plugin_path = Path(sys.argv[1]).resolve()

    if not plugin_path.exists():
        print(f"Error: Plugin directory not found: {plugin_path}")
        sys.exit(1)

    if not plugin_path.is_dir():
        print(f"Error: Path is not a directory: {plugin_path}")
        sys.exit(1)

    valid, message, plugin_type = validate_plugin(plugin_path)
    print(f"Plugin type: {plugin_type}")
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
