#!/usr/bin/env python3
"""
Tech Stack Detection Script

Deterministic detection of project technology stack by analyzing:
- Configuration files (package.json, pyproject.toml, Cargo.toml, etc.)
- File extensions present in the project
- Framework-specific patterns

Returns structured JSON with detected technologies and confidence levels.
"""

import json
import os
import sys
from pathlib import Path
from typing import TypedDict


class StackDetection(TypedDict):
    technology: str
    confidence: str  # HIGH, MEDIUM, LOW
    indicators: list[str]


class DetectionResult(TypedDict):
    primary_language: str | None
    frameworks: list[str]
    detections: list[StackDetection]
    memory_files: list[str]


# Detection patterns: file/pattern -> (technology, confidence)
CONFIG_INDICATORS = {
    # TypeScript
    "tsconfig.json": ("typescript", "HIGH"),
    "tsconfig.*.json": ("typescript", "HIGH"),
    ".ts": ("typescript", "MEDIUM"),
    ".tsx": ("typescript", "HIGH"),

    # JavaScript/Node
    "package.json": ("node", "HIGH"),
    ".js": ("javascript", "LOW"),
    ".mjs": ("javascript", "MEDIUM"),

    # React/Next.js
    "next.config.js": ("nextjs", "HIGH"),
    "next.config.mjs": ("nextjs", "HIGH"),
    "next.config.ts": ("nextjs", "HIGH"),
    ".next/": ("nextjs", "HIGH"),
    "app/layout.tsx": ("nextjs", "HIGH"),
    "pages/_app.tsx": ("nextjs", "HIGH"),
    "pages/_app.js": ("nextjs", "HIGH"),

    # Tailwind
    "tailwind.config.js": ("tailwind", "HIGH"),
    "tailwind.config.ts": ("tailwind", "HIGH"),
    "tailwind.config.mjs": ("tailwind", "HIGH"),

    # Python
    "pyproject.toml": ("python", "HIGH"),
    "setup.py": ("python", "HIGH"),
    "requirements.txt": ("python", "HIGH"),
    "Pipfile": ("python", "HIGH"),
    "poetry.lock": ("python", "HIGH"),
    ".py": ("python", "MEDIUM"),

    # Rust
    "Cargo.toml": ("rust", "HIGH"),
    "Cargo.lock": ("rust", "HIGH"),
    ".rs": ("rust", "MEDIUM"),

    # Testing frameworks
    "jest.config.js": ("jest", "HIGH"),
    "jest.config.ts": ("jest", "HIGH"),
    "vitest.config.ts": ("vitest", "HIGH"),
    "pytest.ini": ("pytest", "HIGH"),
    "conftest.py": ("pytest", "HIGH"),
    ".pytest_cache/": ("pytest", "MEDIUM"),
}

# Package.json dependency patterns
PACKAGE_DEPENDENCIES = {
    "react": ("react", "HIGH"),
    "react-dom": ("react", "HIGH"),
    "next": ("nextjs", "HIGH"),
    "@next/": ("nextjs", "MEDIUM"),
    "tailwindcss": ("tailwind", "HIGH"),
    "@tailwindcss/": ("tailwind", "MEDIUM"),
    "typescript": ("typescript", "HIGH"),
    "jest": ("jest", "HIGH"),
    "@jest/": ("jest", "MEDIUM"),
    "vitest": ("vitest", "HIGH"),
    "@testing-library/": ("testing-library", "HIGH"),
    "playwright": ("playwright", "HIGH"),
    "@playwright/": ("playwright", "MEDIUM"),
    "cypress": ("cypress", "HIGH"),
    "shadcn": ("shadcn", "HIGH"),
    "@radix-ui/": ("shadcn", "MEDIUM"),
}

# pyproject.toml dependency patterns
PYTHON_DEPENDENCIES = {
    "pytest": ("pytest", "HIGH"),
    "django": ("django", "HIGH"),
    "flask": ("flask", "HIGH"),
    "fastapi": ("fastapi", "HIGH"),
    "sqlalchemy": ("sqlalchemy", "MEDIUM"),
}

# Technology to memory file mapping
TECH_TO_MEMORY = {
    "typescript": "typescript.md",
    "javascript": "typescript.md",  # Use TS guidelines for JS too
    "node": "typescript.md",
    "react": "react-nextjs.md",
    "nextjs": "react-nextjs.md",
    "tailwind": "tailwind-shadcn.md",
    "shadcn": "tailwind-shadcn.md",
    "python": "python.md",
    "rust": "rust.md",
    "jest": "testing.md",
    "vitest": "testing.md",
    "pytest": "testing.md",
    "playwright": "testing.md",
    "cypress": "testing.md",
    "testing-library": "testing.md",
}

# Universal memory files (always included)
UNIVERSAL_MEMORY = [
    "constitution.md",
    "documentation.md",
    "git-cicd.md",
    "security.md",
]


def detect_by_config_files(project_path: Path) -> list[StackDetection]:
    """Detect technologies by presence of configuration files."""
    detections: list[StackDetection] = []
    found: dict[str, StackDetection] = {}

    for pattern, (tech, confidence) in CONFIG_INDICATORS.items():
        # Handle directory patterns
        if pattern.endswith("/"):
            check_path = project_path / pattern.rstrip("/")
            if check_path.is_dir():
                if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                    found[tech] = {
                        "technology": tech,
                        "confidence": confidence,
                        "indicators": [f"Directory: {pattern}"]
                    }
                elif tech in found:
                    found[tech]["indicators"].append(f"Directory: {pattern}")
        # Handle glob patterns
        elif "*" in pattern:
            matches = list(project_path.glob(pattern))
            if matches:
                indicator = f"Files matching: {pattern}"
                if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                    found[tech] = {
                        "technology": tech,
                        "confidence": confidence,
                        "indicators": [indicator]
                    }
                elif tech in found:
                    found[tech]["indicators"].append(indicator)
        # Handle extension patterns
        elif pattern.startswith("."):
            # Search for files with this extension (limit depth for performance)
            matches = list(project_path.glob(f"**/*{pattern}"))[:5]
            if matches:
                indicator = f"Extension: {pattern} ({len(matches)}+ files)"
                if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                    found[tech] = {
                        "technology": tech,
                        "confidence": confidence,
                        "indicators": [indicator]
                    }
        # Handle exact file names
        else:
            check_path = project_path / pattern
            if check_path.exists():
                indicator = f"File: {pattern}"
                if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                    found[tech] = {
                        "technology": tech,
                        "confidence": confidence,
                        "indicators": [indicator]
                    }
                elif tech in found:
                    found[tech]["indicators"].append(indicator)

    return list(found.values())


def detect_by_package_json(project_path: Path) -> list[StackDetection]:
    """Detect technologies from package.json dependencies."""
    detections: list[StackDetection] = []
    package_json_path = project_path / "package.json"

    if not package_json_path.exists():
        return detections

    try:
        with open(package_json_path) as f:
            package = json.load(f)
    except (json.JSONDecodeError, IOError):
        return detections

    all_deps = {}
    for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
        all_deps.update(package.get(dep_type, {}))

    found: dict[str, StackDetection] = {}

    for dep_name in all_deps:
        for pattern, (tech, confidence) in PACKAGE_DEPENDENCIES.items():
            if dep_name == pattern or dep_name.startswith(pattern):
                indicator = f"package.json: {dep_name}"
                if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                    found[tech] = {
                        "technology": tech,
                        "confidence": confidence,
                        "indicators": [indicator]
                    }
                elif tech in found:
                    found[tech]["indicators"].append(indicator)

    return list(found.values())


def detect_by_pyproject(project_path: Path) -> list[StackDetection]:
    """Detect technologies from pyproject.toml dependencies."""
    detections: list[StackDetection] = []
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        return detections

    try:
        content = pyproject_path.read_text()
    except IOError:
        return detections

    found: dict[str, StackDetection] = {}
    content_lower = content.lower()

    for pattern, (tech, confidence) in PYTHON_DEPENDENCIES.items():
        if pattern in content_lower:
            indicator = f"pyproject.toml: {pattern}"
            if tech not in found or _confidence_rank(confidence) > _confidence_rank(found[tech]["confidence"]):
                found[tech] = {
                    "technology": tech,
                    "confidence": confidence,
                    "indicators": [indicator]
                }
            elif tech in found:
                found[tech]["indicators"].append(indicator)

    return list(found.values())


def _confidence_rank(confidence: str) -> int:
    """Convert confidence string to numeric rank for comparison."""
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(confidence, 0)


def merge_detections(detections: list[StackDetection]) -> list[StackDetection]:
    """Merge duplicate technologies, keeping highest confidence."""
    merged: dict[str, StackDetection] = {}

    for detection in detections:
        tech = detection["technology"]
        if tech not in merged:
            merged[tech] = detection.copy()
        else:
            existing = merged[tech]
            if _confidence_rank(detection["confidence"]) > _confidence_rank(existing["confidence"]):
                existing["confidence"] = detection["confidence"]
            existing["indicators"].extend(detection["indicators"])

    # Deduplicate indicators
    for detection in merged.values():
        detection["indicators"] = list(dict.fromkeys(detection["indicators"]))

    return list(merged.values())


def determine_primary_language(detections: list[StackDetection]) -> str | None:
    """Determine the primary programming language."""
    language_priority = ["typescript", "python", "rust", "javascript"]

    tech_map = {d["technology"]: d for d in detections}

    for lang in language_priority:
        if lang in tech_map:
            return lang

    return None


def determine_frameworks(detections: list[StackDetection]) -> list[str]:
    """Extract framework technologies from detections."""
    frameworks = ["nextjs", "react", "tailwind", "shadcn", "django", "flask", "fastapi"]
    return [d["technology"] for d in detections if d["technology"] in frameworks]


def select_memory_files(detections: list[StackDetection]) -> list[str]:
    """Select appropriate memory files based on detected technologies."""
    memory_files = set(UNIVERSAL_MEMORY)

    for detection in detections:
        tech = detection["technology"]
        if tech in TECH_TO_MEMORY:
            memory_files.add(TECH_TO_MEMORY[tech])

    # Sort for deterministic output
    return sorted(memory_files)


def detect_stack(project_path: str | Path) -> DetectionResult:
    """
    Main detection function.

    Args:
        project_path: Path to project root directory

    Returns:
        DetectionResult with primary language, frameworks, all detections, and memory files
    """
    project_path = Path(project_path).resolve()

    if not project_path.is_dir():
        return {
            "primary_language": None,
            "frameworks": [],
            "detections": [],
            "memory_files": UNIVERSAL_MEMORY.copy()
        }

    # Collect all detections
    all_detections = []
    all_detections.extend(detect_by_config_files(project_path))
    all_detections.extend(detect_by_package_json(project_path))
    all_detections.extend(detect_by_pyproject(project_path))

    # Merge and deduplicate
    merged = merge_detections(all_detections)

    # Sort by confidence then alphabetically for deterministic output
    merged.sort(key=lambda d: (-_confidence_rank(d["confidence"]), d["technology"]))

    return {
        "primary_language": determine_primary_language(merged),
        "frameworks": determine_frameworks(merged),
        "detections": merged,
        "memory_files": select_memory_files(merged)
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        project_path = os.getcwd()
    else:
        project_path = sys.argv[1]

    result = detect_stack(project_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
