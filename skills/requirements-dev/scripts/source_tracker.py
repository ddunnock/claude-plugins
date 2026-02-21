#!/usr/bin/env python3
"""Source registry management adapted from concept-dev.

Usage:
    python3 source_tracker.py --workspace <path> add --title "..." --url "..." --type research
    python3 source_tracker.py --workspace <path> list
    python3 source_tracker.py --workspace <path> export

Manages source references used during requirements development.
"""
import argparse
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path

REGISTRY_FILENAME = "source_registry.json"
SCHEMA_VERSION = "1.0.0"


@dataclass
class Source:
    id: str
    title: str
    url: str
    type: str  # research, standard, stakeholder, concept_dev
    research_context: str = ""
    concept_dev_ref: str = ""
    metadata: dict = field(default_factory=dict)
    registered_at: str = ""


def _load_registry(workspace: str) -> dict:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {"schema_version": SCHEMA_VERSION, "sources": []}


def _save_registry(workspace: str, registry: dict) -> None:
    path = os.path.join(workspace, REGISTRY_FILENAME)
    _atomic_write(path, registry)


def _next_id(registry: dict) -> str:
    existing = registry.get("sources", [])
    if not existing:
        return "SRC-001"
    max_num = 0
    for src in existing:
        try:
            num = int(src["id"].split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            continue
    return f"SRC-{max_num + 1:03d}"


def add_source(
    workspace: str,
    title: str,
    url: str,
    type: str,
    research_context: str = "",
    concept_dev_ref: str = "",
) -> str:
    """Add a source to the registry. Returns the assigned ID."""

    registry = _load_registry(workspace)
    src = Source(
        id=_next_id(registry),
        title=title,
        url=url,
        type=type,
        research_context=research_context,
        concept_dev_ref=concept_dev_ref,
        registered_at=datetime.now(timezone.utc).isoformat(),
    )
    registry["sources"].append(asdict(src))
    _save_registry(workspace, registry)
    return src.id


def list_sources(workspace: str) -> list[dict]:
    """List all sources."""

    registry = _load_registry(workspace)
    return registry["sources"]


def export_sources(workspace: str) -> dict:
    """Export full registry as dict."""

    return _load_registry(workspace)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage source registry")
    parser.add_argument("--workspace", required=True, type=_validate_dir_path, help="Path to .requirements-dev/ directory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    sp = subparsers.add_parser("add")
    sp.add_argument("--title", required=True)
    sp.add_argument("--url", required=True)
    sp.add_argument("--type", required=True)
    sp.add_argument("--research-context", default="")
    sp.add_argument("--concept-dev-ref", default="")

    # list
    subparsers.add_parser("list")

    # export
    subparsers.add_parser("export")

    args = parser.parse_args()

    if args.command == "add":
        src_id = add_source(
            args.workspace, args.title, args.url, args.type,
            args.research_context, args.concept_dev_ref,
        )
        print(json.dumps({"id": src_id}))
    elif args.command == "list":
        result = list_sources(args.workspace)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        result = export_sources(args.workspace)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
