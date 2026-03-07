"""RFC 6902 JSON diff and patch utilities.

Computes JSON patch operations between two dictionaries and applies
patches for version reconstruction. No third-party dependencies.

References:
    DREG-06 (change journal diffs), DREG-05 (version reconstruction)
"""

import copy


def json_diff(old: dict | None, new: dict, _prefix: str = "") -> list[dict]:
    """Compute RFC 6902-style JSON patch operations between old and new dicts.

    Produces add, remove, and replace operations. Nested dicts are recursed;
    arrays and other values are treated as atomic (replaced entirely).
    Keys are sorted for deterministic output.

    Args:
        old: The original dict, or None for a full-object add.
        new: The updated dict.
        _prefix: Internal path prefix for recursion (do not set manually).

    Returns:
        List of RFC 6902 patch operation dicts, each with:
            - op: "add", "remove", or "replace"
            - path: JSON Pointer path (e.g., "/name", "/nested/field")
            - value: The new value (absent for "remove")
    """
    if old is None:
        return [{"op": "add", "path": "", "value": new}]

    ops: list[dict] = []
    all_keys = sorted(old.keys() | new.keys())

    for key in all_keys:
        path = f"{_prefix}/{key}"

        if key not in old:
            ops.append({"op": "add", "path": path, "value": new[key]})
        elif key not in new:
            ops.append({"op": "remove", "path": path})
        elif old[key] != new[key]:
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                ops.extend(json_diff(old[key], new[key], _prefix=path))
            else:
                ops.append({"op": "replace", "path": path, "value": new[key]})

    return ops


def apply_patch(base: dict, patch: list[dict]) -> dict:
    """Apply RFC 6902 patch operations to a base dict.

    Handles add, remove, and replace operations. Navigates nested paths
    by splitting on "/". Does not mutate the input base dict.

    Args:
        base: The base dict to patch (not mutated).
        patch: List of RFC 6902 operation dicts.

    Returns:
        A new dict with all patch operations applied.

    Raises:
        KeyError: If a remove or replace targets a non-existent path.
        ValueError: If an unknown operation is encountered.
    """
    result = copy.deepcopy(base)

    for op_entry in patch:
        op = op_entry["op"]
        path = op_entry.get("path", "")

        # Full-object replacement (path is empty)
        if path == "":
            if op == "add":
                return copy.deepcopy(op_entry["value"])
            continue

        # Split path into segments, skipping the leading empty string
        parts = [p for p in path.split("/") if p]

        if op in ("add", "replace"):
            _set_nested(result, parts, op_entry["value"])
        elif op == "remove":
            _remove_nested(result, parts)
        else:
            raise ValueError(f"Unknown patch operation: '{op}'")

    return result


def _set_nested(obj: dict, parts: list[str], value) -> None:
    """Set a value at a nested path in a dict.

    Args:
        obj: The dict to modify in place.
        parts: Path segments (e.g., ["nested", "field"]).
        value: The value to set.
    """
    for part in parts[:-1]:
        obj = obj[part]
    obj[parts[-1]] = value


def _remove_nested(obj: dict, parts: list[str]) -> None:
    """Remove a key at a nested path in a dict.

    Args:
        obj: The dict to modify in place.
        parts: Path segments (e.g., ["nested", "field"]).

    Raises:
        KeyError: If the path does not exist.
    """
    for part in parts[:-1]:
        obj = obj[part]
    del obj[parts[-1]]
