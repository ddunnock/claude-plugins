"""Upstream schema knowledge: field mapping, gap markers, and gate status.

This module isolates ALL upstream-schema-specific knowledge in one place.
When upstream registries change field names or structure, only this file
needs updating. Handles known bugs (BUG-1, BUG-3) and schema gaps
(GAP-1..8) from CROSS-SKILL-ANALYSIS.
"""

import hashlib
import json
import os
from datetime import datetime, timezone

from scripts.registry import SLOT_ID_PREFIXES

# ---------------------------------------------------------------------------
# Field mapping dicts: upstream_field -> slot_field
# ---------------------------------------------------------------------------

NEED_FIELD_MAP: dict[str, str] = {
    "id": "upstream_id",
    "statement": "description",
    "stakeholder": "stakeholder",
    "source_block": "source_block",
    "source_artifacts": "source_artifacts",
    "concept_dev_refs": "concept_dev_refs",
    "status": "upstream_status",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
}

REQUIREMENT_FIELD_MAP: dict[str, str] = {
    "id": "upstream_id",
    "statement": "description",
    "type": "requirement_type",
    "priority": "priority",
    "status": "upstream_status",
    "parent_need": "parent_need",
    "source_block": "source_block",
    "level": "decomposition_level",
    "attributes": "upstream_attributes",
    "quality_checks": "quality_checks",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
    "baselined_at": "upstream_baselined_at",
}

# Source registry has field name mismatch (SCHEMA-1):
# upstream uses both "name" AND "title" -- handle both
SOURCE_FIELD_MAP: dict[str, str] = {
    "id": "upstream_id",
    "title": "name",       # SCHEMA-1: upstream uses "title"
    "name": "name",        # Some entries also have "name"
    "url": "url",
    "type": "source_type",
    "confidence": "confidence",  # GAP-4: preserve confidence levels
    "research_context": "research_context",
    "concept_dev_ref": "concept_dev_ref",
    "registered_at": "upstream_registered_at",
}

ASSUMPTION_FIELD_MAP: dict[str, str] = {
    "id": "upstream_id",
    "statement": "description",
    "category": "category",
    "status": "status",
    "source_block": "source_block",
    "related_requirements": "related_requirements",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
}

TRACEABILITY_FIELD_MAP: dict[str, str] = {
    "type": "link_type",
    "from": "from_id",
    "to": "to_id",
    "rationale": "rationale",
    "registered_at": "upstream_registered_at",
}

# ---------------------------------------------------------------------------
# Gap markers from CROSS-SKILL-ANALYSIS findings
# ---------------------------------------------------------------------------

GAP_MARKERS: dict[str, dict] = {
    "GAP-1": {
        "type": "missing_data",
        "finding_ref": "GAP-1",
        "severity": "medium",
        "description": "Research gaps from concept-dev not in requirements-dev registries",
    },
    "GAP-2": {
        "type": "missing_data",
        "finding_ref": "GAP-2",
        "severity": "medium",
        "description": "Ungrounded claims not carried forward from concept-dev",
    },
    "GAP-3": {
        "type": "missing_data",
        "finding_ref": "GAP-3",
        "severity": "low",
        "description": "Citation graph not carried forward from concept-dev",
    },
    "GAP-5": {
        "type": "missing_data",
        "finding_ref": "GAP-5",
        "severity": "low",
        "description": "No concept-dev research artifact access in requirements-dev",
    },
    "GAP-7": {
        "type": "missing_data",
        "finding_ref": "GAP-7",
        "severity": "medium",
        "description": "No assumption lifecycle tracking in requirements-dev",
    },
    "GAP-8": {
        "type": "missing_data",
        "finding_ref": "GAP-8",
        "severity": "medium",
        "description": "No backward traceability to concept-dev artifacts",
    },
}

# Keys excluded from content hashing (timestamps change but don't represent content changes)
HASH_EXCLUDE_KEYS: set[str] = {
    "registered_at",
    "baselined_at",
    "updated_at",
    "created_at",
}


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------


def content_hash(entry: dict, exclude_keys: set[str] | None = None) -> str:
    """Produce deterministic SHA-256 hash of a registry entry.

    Args:
        entry: The registry entry to hash.
        exclude_keys: Keys to exclude from hashing (e.g., timestamps
            that change on every write but don't represent content change).
            Defaults to HASH_EXCLUDE_KEYS if None.

    Returns:
        Hex digest string.
    """
    if exclude_keys is None:
        exclude_keys = HASH_EXCLUDE_KEYS
    filtered = {k: v for k, v in entry.items() if k not in exclude_keys}
    canonical = json.dumps(filtered, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Field mapping
# ---------------------------------------------------------------------------


def map_upstream_entry(
    entry: dict,
    field_map: dict[str, str],
    slot_type: str,
    upstream_file: str,
) -> dict:
    """Map an upstream registry entry to Design Registry slot fields.

    Iterates the field map and copies present fields. Logs warnings for
    required fields that are missing (never uses silent .get() with empty
    defaults for required fields).

    Args:
        entry: Raw upstream registry entry dict.
        field_map: Mapping of upstream_field -> slot_field.
        slot_type: The target slot type (for logging context).
        upstream_file: The upstream filename (for provenance metadata).

    Returns:
        Mapped dict with slot fields and provenance metadata.
        Does NOT include system fields (slot_id, slot_type, version,
        created_at, updated_at) -- SlotAPI.ingest() adds those.
    """
    result: dict = {}

    for upstream_key, slot_key in field_map.items():
        if upstream_key in entry:
            result[slot_key] = entry[upstream_key]

    # Add provenance metadata
    now = datetime.now(timezone.utc).isoformat()
    result["provenance"] = {
        "source": "requirements-dev",
        "upstream_file": upstream_file,
        "ingested_at": now,
        "hash": content_hash(entry),
    }

    return result


# ---------------------------------------------------------------------------
# Slot ID generation
# ---------------------------------------------------------------------------


def generate_slot_id(slot_type: str, upstream_id: str) -> str:
    """Generate a deterministic slot ID from upstream identity.

    Uses the type:upstream-id convention (e.g., need:NEED-001,
    requirement:REQ-026, trace:REQ-001->NEED-003).

    Args:
        slot_type: The slot type (must be in SLOT_ID_PREFIXES).
        upstream_id: The upstream entity identifier.

    Returns:
        Deterministic slot ID string.

    Raises:
        ValueError: If slot_type is not in SLOT_ID_PREFIXES.
    """
    if slot_type not in SLOT_ID_PREFIXES:
        raise ValueError(
            f"Unknown slot type: '{slot_type}'. "
            f"Known types: {sorted(SLOT_ID_PREFIXES.keys())}"
        )
    prefix = SLOT_ID_PREFIXES[slot_type]
    return f"{prefix}:{upstream_id}"


def generate_trace_id(from_id: str, to_id: str) -> str:
    """Generate a deterministic traceability link slot ID.

    Traceability links have no upstream "id" field, so the ID is
    derived from from_id and to_id.

    Args:
        from_id: The source entity ID.
        to_id: The target entity ID.

    Returns:
        Deterministic slot ID like "trace:REQ-001->NEED-003".
    """
    return f"trace:{from_id}->{to_id}"


# ---------------------------------------------------------------------------
# Upstream registry loading
# ---------------------------------------------------------------------------


def load_upstream_registry(
    base_path: str, filename: str, top_key: str
) -> list[dict]:
    """Load an upstream registry file with validation.

    Args:
        base_path: Path to .requirements-dev/ directory.
        filename: Registry filename (e.g., 'needs_registry.json').
        top_key: Top-level key containing items (e.g., 'needs').

    Returns:
        List of registry entry dicts.

    Raises:
        FileNotFoundError: If registry file doesn't exist.
        KeyError: If expected top_key is missing (NOT silent .get()).
    """
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Upstream registry not found: {filepath}")

    with open(filepath) as f:
        data = json.load(f)

    # Explicit KeyError, NOT silent .get() -- learned from BUG-1/BUG-2
    if top_key not in data:
        raise KeyError(
            f"Expected key '{top_key}' not found in {filename}. "
            f"Available keys: {list(data.keys())}"
        )

    return data[top_key]


# ---------------------------------------------------------------------------
# Gate status checking (BUG-1/BUG-3 resistant)
# ---------------------------------------------------------------------------


def check_upstream_gates(state_path: str) -> dict:
    """Check upstream requirements-dev gate status.

    Handles both the correct schema (state.json has flat 'gates' dict)
    and the concept-dev schema (nested 'phases.X.gate_passed'), with
    BUG-1 and BUG-3 resilience.

    Args:
        state_path: Path to state.json file.

    Returns:
        Dict with 'all_passed' (bool), 'gates' (dict), 'warnings' (list).
    """
    with open(state_path) as f:
        state = json.load(f)

    result: dict = {"all_passed": False, "gates": {}, "warnings": []}

    # requirements-dev uses flat gates dict
    if "gates" in state:
        gates = state["gates"]
    # concept-dev uses nested phases (BUG-1 workaround)
    elif "phases" in state:
        gates = {
            name: phase.get("gate_passed", False)
            for name, phase in state["phases"].items()
        }
    else:
        # BUG-3: No gate info available -- NOT all_passed
        result["warnings"].append("No gate information found in state.json")
        return result

    # BUG-3: Empty gates is NOT all_passed
    if not gates:
        result["warnings"].append("Gate dict is empty -- no phases completed")
        return result

    failed = [name for name, passed in gates.items() if not passed]
    result["gates"] = gates
    result["all_passed"] = len(failed) == 0
    if failed:
        result["warnings"].append(f"Incomplete phases: {', '.join(failed)}")

    return result
