"""View assembly engine for constructing contextual views from registry slots.

Provides scope pattern matching, snapshot capture, gap indicator building,
and view specification loading. Views are ephemeral (not persisted as slots)
and assembled on demand from declarative view specifications.

All registry access is read-only through SlotAPI (XCUT-04, VIEW-10).
"""

from __future__ import annotations

import copy
import json
import logging
import os
import re
from datetime import datetime, timezone
from fnmatch import fnmatch
from uuid import uuid4

from scripts.registry import SLOT_TYPE_DIRS, SlotAPI
from scripts.schema_validator import SchemaValidator

logger = logging.getLogger(__name__)

# Default gap severity rules when no config file exists
_DEFAULT_GAP_RULES: dict = {
    "rules": [
        {"slot_type": "component", "severity": "warning"},
        {"slot_type": "interface", "severity": "warning"},
        {"slot_type": "contract", "severity": "info"},
        {"slot_type": "requirement-ref", "severity": "warning"},
        {"slot_type": "traceability-link", "severity": "info"},
    ]
}

# Maps slot types to actionable suggestions for gap indicators
_GAP_SUGGESTIONS: dict[str, str] = {
    "component": "Run /system-dev:decompose to create components.",
    "interface": "Run /system-dev:interface to discover interfaces.",
    "contract": "Run /system-dev:contract to define contracts.",
    "requirement-ref": "Run /system-dev:ingest to import requirements.",
    "traceability-link": "Run /system-dev:trace to create traceability links.",
}

_DEFAULT_SUGGESTION = "Create the missing slot using the appropriate /system-dev command."


def load_view_spec(
    spec_path: str, parameters: dict | None = None
) -> dict:
    """Load a view-spec JSON file and resolve parameter placeholders.

    Reads the spec from disk, then substitutes any {variable} placeholders
    in scope pattern strings with values from the parameters dict.

    Args:
        spec_path: Path to the view-spec JSON file.
        parameters: Dict of variable name -> value for substitution.
            Overrides any defaults in the spec's own parameters field.

    Returns:
        The loaded and resolved view spec dict.

    Raises:
        FileNotFoundError: If spec_path does not exist.
        ValueError: If a {variable} in a pattern has no value in parameters.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(spec_path) as f:
        spec = json.load(f)

    # Merge: caller parameters override spec defaults
    merged_params = dict(spec.get("parameters", {}))
    if parameters:
        merged_params.update(parameters)

    # Find all {variable} placeholders in patterns and resolve them
    for scope_pattern in spec.get("scope_patterns", []):
        pattern_str = scope_pattern.get("pattern", "")
        placeholders = re.findall(r"\{(\w+)\}", pattern_str)

        for placeholder in placeholders:
            if placeholder not in merged_params:
                raise ValueError(
                    f"Missing required parameter '{placeholder}' "
                    f"for pattern '{pattern_str}'. "
                    f"Available parameters: {sorted(merged_params.keys())}"
                )
            pattern_str = pattern_str.replace(
                f"{{{placeholder}}}", merged_params[placeholder]
            )

        scope_pattern["pattern"] = pattern_str

    return spec


def match_scope_pattern(
    pattern: str, slot_type: str, snapshot: dict
) -> list[dict]:
    """Match slots in a snapshot against a glob-like scope pattern.

    Pattern syntax: ``<slot_type>:<name_glob>`` where name_glob supports
    ``*`` (any chars) and ``?`` (single char) via Python's fnmatch module.

    Args:
        pattern: The scope pattern string (e.g., "component:Auth*").
        slot_type: The slot type to match against.
        snapshot: A snapshot dict from capture_snapshot().

    Returns:
        List of slot dicts whose name matches the glob pattern.
        Empty list if no matches (never raises on no matches).
    """
    # Extract the name glob from the pattern (after the colon)
    parts = pattern.split(":", 1)
    if len(parts) == 2:
        name_glob = parts[1]
    else:
        name_glob = "*"

    slots = snapshot.get("slots_by_type", {}).get(slot_type, [])

    return [
        slot for slot in slots
        if fnmatch(slot.get("name", ""), name_glob)
    ]


def capture_snapshot(api: SlotAPI) -> dict:
    """Capture a consistent snapshot of all registry slots via SlotAPI.

    Reads all slot types through api.query() to maintain XCUT-04 compliance.
    All data is deep-copied so the snapshot is immutable.

    Args:
        api: A SlotAPI instance for registry access.

    Returns:
        Dict with snapshot_id (uuid), captured_at (ISO timestamp),
        and slots_by_type (dict mapping slot_type to list of slot dicts).
    """
    snapshot_id = str(uuid4())
    captured_at = datetime.now(timezone.utc).isoformat()

    slots_by_type: dict[str, list[dict]] = {}

    for slot_type in SLOT_TYPE_DIRS:
        slots = api.query(slot_type)
        if slots:
            slots_by_type[slot_type] = copy.deepcopy(slots)

    return {
        "snapshot_id": snapshot_id,
        "captured_at": captured_at,
        "slots_by_type": slots_by_type,
    }


def build_gap_indicator(
    scope_pattern: str,
    slot_type: str,
    reason: str,
    gap_rules: dict | None = None,
) -> dict:
    """Create a gap indicator dict with configurable severity.

    Severity is determined by matching the slot_type against gap_rules.
    If no rules match or no rules provided, defaults to "warning".

    Args:
        scope_pattern: The scope pattern that expected but didn't find slots.
        slot_type: The slot type that was expected.
        reason: Human-readable explanation of why the gap exists.
        gap_rules: Optional gap rules config dict with a "rules" list.
            Each rule has "slot_type" and "severity" fields.

    Returns:
        Gap indicator dict with scope_pattern, slot_type, severity,
        reason, and suggestion fields.
    """
    # Determine severity from rules
    severity = "warning"  # default
    if gap_rules and "rules" in gap_rules:
        for rule in gap_rules["rules"]:
            if rule.get("slot_type") == slot_type:
                severity = rule.get("severity", "warning")
                break

    suggestion = _GAP_SUGGESTIONS.get(slot_type, _DEFAULT_SUGGESTION)

    return {
        "scope_pattern": scope_pattern,
        "slot_type": slot_type,
        "severity": severity,
        "reason": reason,
        "suggestion": suggestion,
    }


def load_gap_rules(workspace_root: str) -> dict:
    """Load gap severity rules from config or return defaults.

    Looks for gap-rules.json in the workspace root directory.
    If not found, returns default rules (XCUT-03 externalized config).

    Args:
        workspace_root: Path to the .system-dev/ directory.

    Returns:
        Dict with "rules" list, each entry having "slot_type" and "severity".
    """
    rules_path = os.path.join(workspace_root, "gap-rules.json")

    if os.path.exists(rules_path):
        with open(rules_path) as f:
            return json.load(f)

    return copy.deepcopy(_DEFAULT_GAP_RULES)


# System fields always included in field selection output
_SYSTEM_FIELDS = {"slot_id", "slot_type", "name", "version"}


def _apply_field_selection(
    slots: list[dict], fields: list[str] | None
) -> list[dict]:
    """Filter each slot dict to only include specified fields plus system fields.

    System fields (slot_id, slot_type, name, version) are always included
    regardless of the fields list.

    Args:
        slots: List of slot dicts to filter.
        fields: List of field names to include, or None to include all.

    Returns:
        List of filtered slot dicts (new dicts, originals unchanged).
    """
    if fields is None:
        return slots

    include = _SYSTEM_FIELDS | set(fields)
    return [
        {k: v for k, v in slot.items() if k in include}
        for slot in slots
    ]


def _organize_hierarchically(sections: list[dict]) -> list[dict]:
    """Reorganize flat section lists into a hierarchical tree structure.

    Components are roots. Interfaces with source_component or target_component
    matching a component's slot_id are nested under that component. Contracts
    with interface_id matching an interface are nested under that interface.
    Everything else goes in an "unlinked" section.

    Args:
        sections: List of section dicts, each with "slot_type" and "slots".

    Returns:
        Reorganized list of section dicts. The hierarchy is flattened back
        into sections format (compatible with view.json schema) but slots
        are grouped logically: component sections contain their related
        interfaces and contracts.
    """
    # Collect all slots by type
    components: list[dict] = []
    interfaces: list[dict] = []
    contracts: list[dict] = []
    other_slots: dict[str, list[dict]] = {}

    for section in sections:
        st = section["slot_type"]
        if st == "component":
            components.extend(section["slots"])
        elif st == "interface":
            interfaces.extend(section["slots"])
        elif st == "contract":
            contracts.extend(section["slots"])
        else:
            other_slots.setdefault(st, []).extend(section["slots"])

    # Build component ID set for parent matching
    comp_ids = {c["slot_id"] for c in components}

    # Match interfaces to components
    linked_interfaces: set[str] = set()
    comp_interface_map: dict[str, list[dict]] = {cid: [] for cid in comp_ids}

    for intf in interfaces:
        src = intf.get("source_component", "")
        tgt = intf.get("target_component", "")
        parent = None
        if src in comp_ids:
            parent = src
        elif tgt in comp_ids:
            parent = tgt

        if parent is not None:
            comp_interface_map[parent].append(intf)
            linked_interfaces.add(intf["slot_id"])

    # Match contracts to interfaces (within view scope)
    intf_ids = {i["slot_id"] for i in interfaces}
    linked_contracts: set[str] = set()
    intf_contract_map: dict[str, list[dict]] = {iid: [] for iid in intf_ids}

    for cntr in contracts:
        iid = cntr.get("interface_id", "")
        if iid in intf_ids:
            intf_contract_map[iid].append(cntr)
            linked_contracts.add(cntr["slot_id"])

    # Build result sections
    result: list[dict] = []

    # Component section with all components
    if components:
        result.append({"slot_type": "component", "slots": components})

    # Interface section: linked interfaces
    linked_intf_list = [i for i in interfaces if i["slot_id"] in linked_interfaces]
    if linked_intf_list:
        result.append({"slot_type": "interface", "slots": linked_intf_list})

    # Contract section: linked contracts
    linked_cntr_list = [c for c in contracts if c["slot_id"] in linked_contracts]
    if linked_cntr_list:
        result.append({"slot_type": "contract", "slots": linked_cntr_list})

    # Other typed sections
    for st, slots in other_slots.items():
        if slots:
            result.append({"slot_type": st, "slots": slots})

    # Unlinked: orphan interfaces and contracts
    unlinked: list[dict] = []
    unlinked.extend(i for i in interfaces if i["slot_id"] not in linked_interfaces)
    unlinked.extend(c for c in contracts if c["slot_id"] not in linked_contracts)

    if unlinked:
        result.append({"slot_type": "unlinked", "slots": unlinked})

    return result


def assemble_view(
    api: SlotAPI,
    spec: dict,
    workspace_root: str,
    schemas_dir: str,
) -> dict:
    """Assemble a contextual view from registry slots based on a view spec.

    This is the main assembly function. It captures a single snapshot for
    consistency (VIEW-07), matches scope patterns, builds gap indicators for
    missing slots, organizes results hierarchically, and validates the output
    against the view.json schema (VIEW-06).

    CRITICAL: This function ONLY reads from SlotAPI. It does NOT create,
    update, or delete any slots (VIEW-10).

    Args:
        api: A SlotAPI instance for registry access (read-only usage).
        spec: A view spec dict (must have name, description, scope_patterns).
        workspace_root: Path to the .system-dev/ directory.
        schemas_dir: Path to the schemas/ directory with JSON Schema files.

    Returns:
        Assembled view dict conforming to view.json schema.
    """
    # 1. Capture a single snapshot for consistent state (VIEW-07)
    snapshot = capture_snapshot(api)

    # 2. Load gap rules
    gap_rules = load_gap_rules(workspace_root)

    # 3. Process each scope pattern
    raw_sections: list[dict] = []
    gaps: list[dict] = []

    for scope_pattern in spec.get("scope_patterns", []):
        pattern = scope_pattern["pattern"]
        slot_type = scope_pattern["slot_type"]
        fields = scope_pattern.get("fields")

        matches = match_scope_pattern(pattern, slot_type, snapshot)

        if matches:
            # Apply field selection if specified
            filtered = _apply_field_selection(matches, fields)
            raw_sections.append({"slot_type": slot_type, "slots": filtered})
        else:
            gap = build_gap_indicator(
                scope_pattern=pattern,
                slot_type=slot_type,
                reason=f"No {slot_type} slots matching '{pattern}' found",
                gap_rules=gap_rules,
            )
            gaps.append(gap)

    # 4. Organize hierarchically
    sections = _organize_hierarchically(raw_sections)

    # 5. Build metadata
    total_slots = sum(len(s["slots"]) for s in sections)
    total_gaps = len(gaps)

    gap_summary = {"info": 0, "warning": 0, "error": 0}
    for gap in gaps:
        severity = gap.get("severity", "warning")
        if severity in gap_summary:
            gap_summary[severity] += 1

    assembled = {
        "spec_name": spec["name"],
        "assembled_at": datetime.now(timezone.utc).isoformat(),
        "snapshot_id": snapshot["snapshot_id"],
        "total_slots": total_slots,
        "total_gaps": total_gaps,
        "gap_summary": gap_summary,
        "sections": sections,
        "gaps": gaps,
    }

    # 6. Validate against view.json schema (VIEW-06)
    validator = SchemaValidator(schemas_dir)
    validator.validate_or_raise("view", assembled)

    return assembled
