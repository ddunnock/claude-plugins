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
