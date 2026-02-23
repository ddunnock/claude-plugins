#!/usr/bin/env python3
"""Parse concept-dev JSON registries and validate artifacts.

Usage: python3 ingest_concept.py --concept-dir .concept-dev/ --output .requirements-dev/ingestion.json

Parses JSON registries (source_registry.json, assumption_registry.json, state.json)
and validates artifact presence. Markdown extraction is LLM-assisted via the
/reqdev:init command prompt.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

from shared_io import _atomic_write, _validate_dir_path, _validate_path

# Artifacts to check for presence
EXPECTED_ARTIFACTS = [
    "CONCEPT-DOCUMENT.md",
    "BLACKBOX.md",
    "SOLUTION-LANDSCAPE.md",
    "source_registry.json",
    "assumption_registry.json",
    "state.json",
]


def ingest(concept_path: str, output_path: str) -> dict:
    """Parse concept-dev JSON registries and validate artifact presence.

    Args:
        concept_path: Path to .concept-dev/ directory
        output_path: Path to write ingestion.json output

    Returns:
        dict with keys: source_refs, assumption_refs, gate_status,
        artifact_inventory, ingested_at
    """
    now = datetime.now(timezone.utc).isoformat()

    # Check if concept_path exists; if not, return fallback dict
    if not os.path.isdir(concept_path):
        fallback = {
            "ingested_at": now,
            "concept_path": None,
            "source_refs": [],
            "assumption_refs": [],
            "gate_status": {
                "all_passed": False,
                "gates": {},
                "warnings": ["No .concept-dev/ directory found"],
            },
            "artifact_inventory": {},
        }
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        _atomic_write(output_path, fallback)
        return fallback

    # Build artifact_inventory
    artifact_inventory = {}
    for artifact in EXPECTED_ARTIFACTS:
        artifact_inventory[artifact] = os.path.isfile(
            os.path.join(concept_path, artifact)
        )

    # Parse source_registry.json (graceful on malformed JSON)
    source_refs = []
    research_gaps = []
    citations = []
    source_path = os.path.join(concept_path, "source_registry.json")
    if os.path.isfile(source_path):
        try:
            with open(source_path) as f:
                source_data = json.load(f)
            source_refs = source_data.get("sources", [])
            research_gaps = source_data.get("gaps", [])
            citations = source_data.get("citations", [])
        except (json.JSONDecodeError, KeyError):
            print(
                "Warning: source_registry.json is malformed, skipping",
                file=sys.stderr,
            )

    # Parse assumption_registry.json (graceful on malformed JSON)
    assumption_refs = []
    ungrounded_claims = []
    assumption_path = os.path.join(concept_path, "assumption_registry.json")
    if os.path.isfile(assumption_path):
        try:
            with open(assumption_path) as f:
                assumption_data = json.load(f)
            assumption_refs = assumption_data.get("assumptions", [])
            ungrounded_claims = assumption_data.get("ungrounded_claims", [])
        except (json.JSONDecodeError, KeyError):
            print(
                "Warning: assumption_registry.json is malformed, skipping",
                file=sys.stderr,
            )

    # Parse state.json for gate status and skeptic findings (graceful on malformed JSON)
    gate_status = {"all_passed": False, "gates": {}, "warnings": []}
    skeptic_findings = {}
    state_path = os.path.join(concept_path, "state.json")
    if os.path.isfile(state_path):
        try:
            with open(state_path) as f:
                state_data = json.load(f)

            # BUG-1 fix: concept-dev stores gates as phases.{name}.gate_passed,
            # not as a flat "gates" dict. Support both formats.
            phases = state_data.get("phases", {})
            if phases:
                gates = {
                    name: phase.get("gate_passed", False)
                    for name, phase in phases.items()
                }
            else:
                gates = state_data.get("gates", {})

            # BUG-3 fix: empty gates should not report all_passed=True
            if not gates:
                gate_status["all_passed"] = False
                gate_status["warnings"].append(
                    "No gate information found in state.json"
                )
            else:
                gate_status["gates"] = gates
                failed = [name for name, passed in gates.items() if not passed]
                if failed:
                    gate_status["all_passed"] = False
                    for name in failed:
                        gate_status["warnings"].append(
                            f"Gate '{name}' not passed"
                        )
                else:
                    gate_status["all_passed"] = True

            # OPP-2: carry forward skeptic findings
            skeptic_findings = state_data.get("skeptic_findings", {})
        except (json.JSONDecodeError, KeyError):
            gate_status["warnings"].append("state.json is malformed")
    else:
        gate_status["warnings"].append("No state.json found in concept-dev directory")

    result = {
        "ingested_at": now,
        "concept_path": concept_path,
        "source_refs": source_refs,
        "assumption_refs": assumption_refs,
        "research_gaps": research_gaps,
        "ungrounded_claims": ungrounded_claims,
        "citations": citations,
        "skeptic_findings": skeptic_findings,
        "gate_status": gate_status,
        "artifact_inventory": artifact_inventory,
    }

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    _atomic_write(output_path, result)

    return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest concept-dev artifacts for requirements development"
    )
    parser.add_argument(
        "--concept-dir", required=True, type=_validate_dir_path, help="Path to .concept-dev/ directory"
    )
    parser.add_argument(
        "--output", required=True, type=lambda p: _validate_path(p, [".json"]), help="Path to write ingestion.json"
    )
    args = parser.parse_args()

    result = ingest(args.concept_dir, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
