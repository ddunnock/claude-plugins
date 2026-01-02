#!/usr/bin/env python3
"""
README and CHANGELOG Generator Script

Generates and updates README.md and CHANGELOG.md following best practices.

Usage:
    python readme_generator.py [project_path] [--init] [--changelog VERSION]

Features:
- Generate README.md from project analysis
- Update CHANGELOG.md following Keep a Changelog format
- Extract project metadata from package.json, pyproject.toml, etc.
- Link to documentation in docs/
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict


class ProjectMetadata(TypedDict):
    """Project metadata extracted from config files."""
    name: str
    description: str | None
    version: str | None
    license: str | None
    author: str | None
    repository: str | None
    keywords: list[str]
    has_cli: bool
    has_docs: bool


class ChangelogEntry(TypedDict):
    """A changelog version entry."""
    version: str
    date: str
    added: list[str]
    changed: list[str]
    deprecated: list[str]
    removed: list[str]
    fixed: list[str]
    security: list[str]


@dataclass
class ReadmeSection:
    """A section of the README."""
    title: str
    content: str
    order: int


def extract_metadata(project_path: Path) -> ProjectMetadata:
    """Extract project metadata from config files."""
    metadata: ProjectMetadata = {
        "name": project_path.name,
        "description": None,
        "version": None,
        "license": None,
        "author": None,
        "repository": None,
        "keywords": [],
        "has_cli": False,
        "has_docs": (project_path / "docs").exists(),
    }

    # Try package.json (Node.js)
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text())
            metadata["name"] = data.get("name", metadata["name"])
            metadata["description"] = data.get("description")
            metadata["version"] = data.get("version")
            metadata["license"] = data.get("license")
            metadata["author"] = data.get("author")
            metadata["repository"] = data.get("repository", {}).get("url") if isinstance(data.get("repository"), dict) else data.get("repository")
            metadata["keywords"] = data.get("keywords", [])
            metadata["has_cli"] = "bin" in data
        except Exception:
            pass

    # Try pyproject.toml (Python)
    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib
            data = tomllib.loads(pyproject.read_text())
            project = data.get("project", {})
            metadata["name"] = project.get("name", metadata["name"])
            metadata["description"] = project.get("description")
            metadata["version"] = project.get("version")
            metadata["license"] = project.get("license", {}).get("text") if isinstance(project.get("license"), dict) else project.get("license")
            metadata["author"] = project.get("authors", [{}])[0].get("name") if project.get("authors") else None
            metadata["keywords"] = project.get("keywords", [])
            metadata["has_cli"] = bool(project.get("scripts"))
        except Exception:
            pass

    # Try Cargo.toml (Rust)
    cargo = project_path / "Cargo.toml"
    if cargo.exists():
        try:
            content = cargo.read_text()
            # Simple TOML parsing for key fields
            name_match = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if name_match:
                metadata["name"] = name_match.group(1)
            version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if version_match:
                metadata["version"] = version_match.group(1)
            desc_match = re.search(r'^description\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if desc_match:
                metadata["description"] = desc_match.group(1)
            metadata["has_cli"] = "[[bin]]" in content
        except Exception:
            pass

    return metadata


def generate_readme(metadata: ProjectMetadata, project_path: Path) -> str:
    """Generate README.md content."""
    lines = []

    # Title
    lines.append(f"# {metadata['name']}")
    lines.append("")

    # Badges (placeholder)
    # lines.append("[![License](badge-url)](license-url)")
    # lines.append("")

    # Description
    if metadata["description"]:
        lines.append(f"> {metadata['description']}")
        lines.append("")

    # Quick description paragraph
    lines.extend([
        "## Overview",
        "",
        f"[Brief description of what {metadata['name']} does and why it exists.]",
        "",
    ])

    # Installation
    lines.extend([
        "## Installation",
        "",
    ])

    if (project_path / "package.json").exists():
        lines.extend([
            "```bash",
            f"npm install {metadata['name']}",
            "```",
            "",
        ])
    elif (project_path / "pyproject.toml").exists():
        lines.extend([
            "```bash",
            f"pip install {metadata['name']}",
            "```",
            "",
        ])
    elif (project_path / "Cargo.toml").exists():
        lines.extend([
            "```bash",
            f"cargo install {metadata['name']}",
            "```",
            "",
        ])
    else:
        lines.extend([
            "[Installation instructions]",
            "",
        ])

    # Quick Start
    lines.extend([
        "## Quick Start",
        "",
        "```",
        "[Quick start example]",
        "```",
        "",
    ])

    # Documentation links
    if metadata["has_docs"]:
        lines.extend([
            "## Documentation",
            "",
            "- [Getting Started](docs/user/getting-started/)",
            "- [User Guides](docs/user/guides/)",
            "- [API Reference](docs/developer/reference/api/)",
            "- [Contributing](docs/developer/contributing/)",
            "",
        ])

    # Features
    lines.extend([
        "## Features",
        "",
        "- [Feature 1]",
        "- [Feature 2]",
        "- [Feature 3]",
        "",
    ])

    # Contributing
    lines.extend([
        "## Contributing",
        "",
    ])
    if metadata["has_docs"]:
        lines.append("See [Contributing Guide](docs/developer/contributing/getting-started.md).")
    else:
        lines.append("[Contribution guidelines]")
    lines.append("")

    # License
    lines.extend([
        "## License",
        "",
    ])
    if metadata["license"]:
        lines.append(f"{metadata['license']} - see [LICENSE](LICENSE) for details.")
    else:
        lines.append("[License information]")
    lines.append("")

    return "\n".join(lines)


def parse_changelog(content: str) -> list[ChangelogEntry]:
    """Parse existing CHANGELOG.md into entries."""
    entries = []

    # Split by version headers
    version_pattern = r"^## \[([^\]]+)\](?: - (\d{4}-\d{2}-\d{2}))?$"
    current_entry = None
    current_section = None

    for line in content.split("\n"):
        version_match = re.match(version_pattern, line)
        if version_match:
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                "version": version_match.group(1),
                "date": version_match.group(2) or "",
                "added": [],
                "changed": [],
                "deprecated": [],
                "removed": [],
                "fixed": [],
                "security": [],
            }
            current_section = None
        elif line.startswith("### ") and current_entry:
            section_name = line[4:].lower()
            if section_name in current_entry:
                current_section = section_name
        elif line.startswith("- ") and current_entry and current_section:
            current_entry[current_section].append(line[2:])

    if current_entry:
        entries.append(current_entry)

    return entries


def generate_changelog_entry(version: str, changes: dict | None = None) -> str:
    """Generate a changelog entry."""
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"## [{version}] - {date}",
        "",
    ]

    if changes:
        sections = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
        for section in sections:
            items = changes.get(section.lower(), [])
            if items:
                lines.append(f"### {section}")
                lines.append("")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")
    else:
        lines.extend([
            "### Added",
            "",
            "- [New feature or functionality]",
            "",
        ])

    return "\n".join(lines)


def generate_changelog(metadata: ProjectMetadata) -> str:
    """Generate initial CHANGELOG.md."""
    lines = [
        "# Changelog",
        "",
        "All notable changes to this project will be documented in this file.",
        "",
        "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
        "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
        "",
        "## [Unreleased]",
        "",
        "### Added",
        "",
        "- Initial project setup",
        "",
    ]

    if metadata["version"]:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines.extend([
            f"## [{metadata['version']}] - {date}",
            "",
            "### Added",
            "",
            "- Initial release",
            "",
        ])

    # Add comparison links at bottom
    if metadata["repository"]:
        repo = metadata["repository"].rstrip("/").replace(".git", "")
        lines.extend([
            f"[Unreleased]: {repo}/compare/v{metadata['version'] or '0.0.0'}...HEAD",
        ])
        if metadata["version"]:
            lines.append(f"[{metadata['version']}]: {repo}/releases/tag/v{metadata['version']}")

    return "\n".join(lines)


def update_changelog(changelog_path: Path, version: str, changes: dict | None = None) -> str:
    """Update existing CHANGELOG.md with new entry."""
    if not changelog_path.exists():
        return generate_changelog({"name": "", "version": version, "repository": None})

    content = changelog_path.read_text()

    # Find [Unreleased] section and insert new version after it
    new_entry = generate_changelog_entry(version, changes)

    # Insert after [Unreleased] section header
    unreleased_pattern = r"(## \[Unreleased\].*?)(\n## \[)"
    match = re.search(unreleased_pattern, content, re.DOTALL)

    if match:
        # Insert new entry before previous version
        updated = content[:match.end(1)] + "\n\n" + new_entry + content[match.start(2):]
    else:
        # No previous versions, insert after Unreleased
        unreleased_idx = content.find("## [Unreleased]")
        if unreleased_idx >= 0:
            # Find end of Unreleased section (next ## or end)
            next_section = content.find("\n## [", unreleased_idx + 1)
            if next_section < 0:
                next_section = len(content)
            updated = content[:next_section] + "\n" + new_entry + content[next_section:]
        else:
            # No Unreleased section, prepend
            updated = content + "\n" + new_entry

    return updated


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate and update README.md and CHANGELOG.md"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to project root (default: current directory)"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize README.md (will not overwrite existing)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files"
    )
    parser.add_argument(
        "--changelog",
        metavar="VERSION",
        help="Add changelog entry for VERSION"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output metadata as JSON instead of generating files"
    )

    args = parser.parse_args()
    project_path = Path(args.project_path).resolve()

    # Extract metadata
    metadata = extract_metadata(project_path)

    if args.json:
        print(json.dumps(metadata, indent=2))
        return

    print(f"Project: {metadata['name']}")
    print(f"Version: {metadata['version'] or 'unknown'}")
    print(f"Has CLI: {metadata['has_cli']}")
    print(f"Has Docs: {metadata['has_docs']}")
    print()

    if args.init:
        readme_path = project_path / "README.md"
        changelog_path = project_path / "CHANGELOG.md"

        if readme_path.exists() and not args.force:
            print(f"README.md already exists. Use --force to overwrite.")
        else:
            readme_content = generate_readme(metadata, project_path)
            print("Generated README.md:")
            print("-" * 40)
            print(readme_content)
            print("-" * 40)

            if args.force or not readme_path.exists():
                readme_path.write_text(readme_content)
                print(f"\nWrote: {readme_path}")

        if changelog_path.exists() and not args.force:
            print(f"\nCHANGELOG.md already exists. Use --force to overwrite.")
        else:
            changelog_content = generate_changelog(metadata)
            print("\nGenerated CHANGELOG.md:")
            print("-" * 40)
            print(changelog_content)
            print("-" * 40)

            if args.force or not changelog_path.exists():
                changelog_path.write_text(changelog_content)
                print(f"\nWrote: {changelog_path}")

    elif args.changelog:
        changelog_path = project_path / "CHANGELOG.md"

        if not changelog_path.exists():
            print("No CHANGELOG.md found. Use --init first.")
            sys.exit(1)

        updated = update_changelog(changelog_path, args.changelog)
        print(f"Updated CHANGELOG.md with version {args.changelog}:")
        print("-" * 40)
        print(updated)
        print("-" * 40)

        changelog_path.write_text(updated)
        print(f"\nWrote: {changelog_path}")

    else:
        # Just show what would be generated
        readme_content = generate_readme(metadata, project_path)
        print("Would generate README.md:")
        print("-" * 40)
        print(readme_content)
        print("-" * 40)
        print("\nUse --init to create files")


if __name__ == "__main__":
    main()
