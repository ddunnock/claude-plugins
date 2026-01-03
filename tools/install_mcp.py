#!/usr/bin/env python3
"""
MCP Installer - Installs MCP plugins to ~/.claude/ for Claude Desktop

Usage:
    install_mcp.py <plugin-name.plugin> [--symlink]
    install_mcp.py <mcp-directory> [--symlink]

Options:
    --symlink    Create symlink instead of copying (for development)

Examples:
    install_mcp.py dist/session-memory.plugin
    install_mcp.py mcps/session-memory --symlink
"""

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"


def install_from_plugin_file(plugin_path: Path, use_symlink: bool = False) -> bool:
    """Install MCP from a .plugin file."""
    if not plugin_path.exists():
        print(f"Error: Plugin file not found: {plugin_path}")
        return False

    try:
        with zipfile.ZipFile(plugin_path, "r") as zf:
            # Read manifest
            try:
                manifest_data = zf.read("MANIFEST.json")
                manifest = json.loads(manifest_data)
            except KeyError:
                print("Error: MANIFEST.json not found in plugin")
                return False

            # Verify it's an MCP
            if manifest.get("type") != "mcp":
                print(f"Error: Not an MCP plugin (type is '{manifest.get('type')}')")
                return False

            plugin_name = manifest["name"]
            target_dir = CLAUDE_DIR / plugin_name

            # Check if already installed
            if target_dir.exists():
                response = input(f"{plugin_name} already installed at {target_dir}. Overwrite? [y/N] ")
                if response.lower() != "y":
                    print("Installation cancelled.")
                    return False
                if target_dir.is_symlink():
                    target_dir.unlink()
                else:
                    shutil.rmtree(target_dir)

            # Ensure ~/.claude exists
            CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

            # Extract contents
            print(f"Extracting to {target_dir}...")
            for member in zf.namelist():
                if member == "MANIFEST.json":
                    continue
                # Remove the top-level directory from the path
                parts = Path(member).parts
                if len(parts) > 1:
                    relative_path = Path(*parts[1:])
                    target_path = target_dir / relative_path

                    if member.endswith("/"):
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(target_path, "wb") as dst:
                            dst.write(src.read())
                        print(f"  Extracted: {relative_path}")

            print(f"\nInstalled {plugin_name} to {target_dir}")
            print_config_snippet(manifest, target_dir)
            return True

    except zipfile.BadZipFile:
        print(f"Error: Invalid plugin file: {plugin_path}")
        return False
    except Exception as e:
        print(f"Error installing plugin: {e}")
        return False


def install_from_directory(mcp_path: Path, use_symlink: bool = False) -> bool:
    """Install MCP from a directory (symlink or copy)."""
    mcp_path = mcp_path.resolve()

    if not mcp_path.exists():
        print(f"Error: MCP directory not found: {mcp_path}")
        return False

    # Read MCP.md to get metadata
    mcp_md = mcp_path / "MCP.md"
    if not mcp_md.exists():
        print("Error: MCP.md not found in directory")
        return False

    import re
    import yaml

    content = mcp_md.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        print("Error: Invalid MCP.md frontmatter")
        return False

    try:
        manifest = yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        print(f"Error parsing MCP.md: {e}")
        return False

    plugin_name = manifest.get("name", mcp_path.name)
    target_dir = CLAUDE_DIR / plugin_name

    # Check if already installed
    if target_dir.exists():
        response = input(f"{plugin_name} already installed at {target_dir}. Overwrite? [y/N] ")
        if response.lower() != "y":
            print("Installation cancelled.")
            return False
        if target_dir.is_symlink():
            target_dir.unlink()
        else:
            shutil.rmtree(target_dir)

    # Ensure ~/.claude exists
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

    if use_symlink:
        # Create symlink for development
        target_dir.symlink_to(mcp_path)
        print(f"Symlinked {target_dir} -> {mcp_path}")
    else:
        # Copy directory
        shutil.copytree(
            mcp_path,
            target_dir,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.pyc",
                ".git",
                ".DS_Store",
                "storage",
                "handoffs",
            ),
        )
        print(f"Copied to {target_dir}")

    print(f"\nInstalled {plugin_name} to {target_dir}")
    print_config_snippet(manifest, target_dir)
    return True


def print_config_snippet(manifest: dict, target_dir: Path):
    """Print Claude Desktop configuration snippet."""
    plugin_name = manifest["name"]
    entry_point = manifest.get("entry_point", "server.py")

    config = {
        "mcpServers": {
            plugin_name: {
                "command": "python3",
                "args": [str(target_dir / entry_point)]
            }
        }
    }

    print("\nAdd to Claude Desktop config (~/.config/claude/claude_desktop_config.json):")
    print(json.dumps(config, indent=2))

    # Check dependencies
    if manifest.get("dependencies"):
        deps = manifest["dependencies"]
        print(f"\nInstall dependencies:")
        print(f"  pip install {' '.join(deps)}")


def main():
    parser = argparse.ArgumentParser(
        description="Install MCP plugins to ~/.claude/ for Claude Desktop"
    )
    parser.add_argument(
        "source",
        help="Path to .plugin file or MCP directory"
    )
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Create symlink instead of copying (for development)"
    )
    args = parser.parse_args()

    source_path = Path(args.source)

    if source_path.suffix == ".plugin":
        # Install from plugin file
        success = install_from_plugin_file(source_path, args.symlink)
    elif source_path.is_dir():
        # Install from directory
        success = install_from_directory(source_path, args.symlink)
    else:
        print(f"Error: {source_path} is not a .plugin file or directory")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
