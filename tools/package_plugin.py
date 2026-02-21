#!/usr/bin/env python3
"""
Plugin Packager - Creates distributable .plugin files for both skills and MCPs

Usage:
    package_plugin.py <path/to/plugin-folder> [output-directory]

Examples:
    package_plugin.py skills/documentation-architect
    package_plugin.py mcps/session-memory ./dist
"""

import os
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from validate_plugin import validate_plugin, parse_frontmatter


def get_plugin_metadata(plugin_path: Path, plugin_type: str) -> dict:
    """Extract metadata from plugin manifest."""
    if plugin_type == "skill":
        manifest_file = plugin_path / "SKILL.md"
    else:
        manifest_file = plugin_path / "MCP.md"

    if not manifest_file.exists():
        return {"name": plugin_path.name, "type": plugin_type}

    content = manifest_file.read_text()
    frontmatter, _ = parse_frontmatter(content)

    if frontmatter is None:
        return {"name": plugin_path.name, "type": plugin_type}

    metadata = {
        "name": frontmatter.get("name", plugin_path.name),
        "type": plugin_type,
        "description": frontmatter.get("description", ""),
    }

    # Add MCP-specific fields
    if plugin_type == "mcp":
        if "entry_point" in frontmatter:
            metadata["entry_point"] = frontmatter["entry_point"]
        if "dependencies" in frontmatter:
            metadata["dependencies"] = frontmatter["dependencies"]
        if "config_file" in frontmatter:
            metadata["config_file"] = frontmatter["config_file"]

    return metadata


def package_plugin(plugin_path: Path, output_dir: Path | None = None) -> Path | None:
    """
    Package a plugin folder into a .plugin file.

    Args:
        plugin_path: Path to the plugin folder
        output_dir: Optional output directory for the .plugin file

    Returns:
        Path to the created .plugin file, or None if error
    """
    plugin_path = Path(os.path.realpath(str(plugin_path))).resolve()

    # Validate plugin folder exists
    if not plugin_path.exists():
        print(f"Error: Plugin folder not found: {plugin_path}")
        return None

    if not plugin_path.is_dir():
        print(f"Error: Path is not a directory: {plugin_path}")
        return None

    # Run validation before packaging
    print("Validating plugin...")
    valid, message, plugin_type = validate_plugin(plugin_path)
    if not valid:
        print(f"Validation failed: {message}")
        print("Please fix the validation errors before packaging.")
        return None
    print(f"{message}\n")

    # Get plugin metadata
    metadata = get_plugin_metadata(plugin_path, plugin_type)
    plugin_name = metadata["name"]

    # Add packaging metadata
    metadata["version"] = "1.0.0"
    metadata["packaged_at"] = datetime.now(timezone.utc).isoformat()
    metadata["packaged_by"] = "package_plugin.py v1.0"

    # Determine output location
    if output_dir:
        output_path = Path(os.path.realpath(str(output_dir))).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    plugin_filename = output_path / f"{plugin_name}.plugin"

    # Files/directories to exclude
    exclude_patterns = {
        "__pycache__",
        ".git",
        ".DS_Store",
        "*.pyc",
        "storage",  # MCP runtime storage
        "handoffs",  # MCP handoffs
    }

    def should_exclude(path: Path) -> bool:
        """Check if a path should be excluded from packaging."""
        for pattern in exclude_patterns:
            if pattern.startswith("*"):
                if path.name.endswith(pattern[1:]):
                    return True
            elif path.name == pattern:
                return True
        return False

    # Create the .plugin file (zip format)
    try:
        with zipfile.ZipFile(plugin_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Write manifest
            manifest_json = json.dumps(metadata, indent=2)
            zipf.writestr("MANIFEST.json", manifest_json)
            print(f"  Added: MANIFEST.json")

            # Walk through the plugin directory
            for file_path in plugin_path.rglob("*"):
                # Skip excluded files/directories
                if any(should_exclude(p) for p in file_path.parents) or should_exclude(file_path):
                    continue

                if file_path.is_file():
                    # Calculate the relative path within the zip
                    arcname = Path(plugin_name) / file_path.relative_to(plugin_path)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

        print(f"\nSuccessfully packaged {plugin_type} to: {plugin_filename}")
        print(f"\nManifest:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        return plugin_filename

    except Exception as e:
        print(f"Error creating .plugin file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: package_plugin.py <path/to/plugin-folder> [output-directory]")
        print("\nExamples:")
        print("  package_plugin.py skills/documentation-architect")
        print("  package_plugin.py mcps/session-memory ./dist")
        sys.exit(1)

    plugin_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"Packaging plugin: {plugin_path}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print()

    result = package_plugin(plugin_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
