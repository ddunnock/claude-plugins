#!/usr/bin/env python3
"""Shared I/O utilities for skill-tester scripts.

Provides atomic file writes, path validation, and safe JSON handling.
Based on the proven pattern from skill-writer/scripts/shared_io.py.

Usage:
    from shared_io import (
        _atomic_write, _validate_path, _validate_dir_path,
        _load_json, _save_json, _validate_json_schema,
    )
"""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def _reject_traversal(path: str) -> None:
    """Raise ValueError if path contains '..' traversal segments.

    Args:
        path: The path string to check.

    Raises:
        ValueError: If path contains '..' segments.
    """
    if ".." in Path(path).parts:
        raise ValueError(f"Path traversal rejected: {path}")


def _check_boundary(resolved: str, boundary: str) -> None:
    """Raise ValueError if resolved path is outside the boundary directory.

    Args:
        resolved: The resolved absolute path to check.
        boundary: The boundary directory path.

    Raises:
        ValueError: If resolved path is outside boundary.
    """
    boundary_resolved = os.path.realpath(boundary)
    if resolved != boundary_resolved and not resolved.startswith(boundary_resolved + os.sep):
        raise ValueError(f"Path '{resolved}' is outside boundary '{boundary_resolved}'")


def _atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically using temp-file-then-rename pattern.

    Args:
        filepath: Target file path for the JSON output.
        data: Dictionary to serialize as JSON.

    Raises:
        OSError: If the target directory does not exist.
        TypeError: If data is not JSON-serializable.
    """
    target_dir = os.path.dirname(os.path.abspath(filepath))
    fd = NamedTemporaryFile(
        mode="w",
        dir=target_dir,
        suffix=".tmp",
        delete=False,
    )
    try:
        json.dump(data, fd, indent=2)
        fd.write("\n")
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.chmod(fd.name, 0o600)
        os.replace(fd.name, filepath)
    except Exception:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def _validate_path(path: str, boundary: str | None = None,
                   allowed_extensions: list[str] | None = None) -> str:
    """Validate and resolve a file path.

    Rejects paths containing '..' traversal. Optionally checks that the
    resolved path starts with a boundary directory and has an allowed extension.

    Args:
        path: The file path to validate.
        boundary: If provided, the resolved path must start with this directory.
        allowed_extensions: If provided, the file extension must be in this list.

    Returns:
        The resolved absolute path.

    Raises:
        ValueError: If validation fails.
    """
    _reject_traversal(path)
    resolved = os.path.realpath(path)

    if boundary:
        _check_boundary(resolved, boundary)

    if allowed_extensions:
        ext = os.path.splitext(resolved)[1].lower()
        if ext not in allowed_extensions:
            raise ValueError(f"Extension '{ext}' not in {allowed_extensions}")

    return resolved


def _validate_dir_path(path: str, boundary: str | None = None) -> str:
    """Validate and resolve a directory path. Reject '..' traversal.

    Args:
        path: The directory path to validate.
        boundary: If provided, the resolved path must start with this directory.

    Returns:
        The resolved absolute path.

    Raises:
        ValueError: If path contains '..' traversal or is outside boundary.
    """
    _reject_traversal(path)
    resolved = os.path.realpath(path)

    if boundary:
        _check_boundary(resolved, boundary)

    return resolved


def _validate_json_schema(data: dict, schema: dict) -> list[str]:
    """Validate a dict against a simple field schema.

    Schema format: each key maps to {"required": bool, "type": type_or_tuple}.
    Type can be a single type or tuple of types (e.g., (str, type(None)) for nullable).

    Args:
        data: The dictionary to validate.
        schema: Schema definition mapping field names to constraints.

    Returns:
        List of error strings. Empty list means valid.
    """
    if not isinstance(data, dict):
        return [f"Expected dict, got {type(data).__name__}"]

    errors = []
    for field, rules in schema.items():
        required = rules.get("required", False)
        expected_type = rules.get("type")

        if field not in data:
            if required:
                errors.append(f"Missing required field: '{field}'")
            continue

        value = data[field]
        if expected_type is None:
            continue

        if value is None:
            is_nullable = isinstance(expected_type, tuple) and type(None) in expected_type
            if not is_nullable:
                errors.append(f"Field '{field}': got None but field is not nullable")
        elif not isinstance(value, expected_type):
            actual = type(value).__name__
            if isinstance(expected_type, tuple):
                expected_names = "/".join(t.__name__ for t in expected_type)
            else:
                expected_names = expected_type.__name__
            errors.append(f"Field '{field}': expected {expected_names}, got {actual}")

    return errors


def _load_json(path: str, schema: dict | None = None) -> dict:
    """Load and parse a JSON file safely, with optional schema validation.

    Note:
        This function uses raw ``open()`` deliberately. Callers are
        responsible for validating *path* at the system boundary (via
        ``_validate_path`` or ``_validate_dir_path``) before invoking
        this helper.  This boundary-validation pattern avoids redundant
        checks on every internal read.

    Args:
        path: Path to the JSON file.
        schema: If provided, validate the loaded data against this schema.

    Returns:
        Parsed dictionary from the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        ValueError: If schema validation fails.
    """
    with open(path) as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}, got {type(data).__name__}")

    if schema is not None:
        errors = _validate_json_schema(data, schema)
        if errors:
            raise ValueError(
                f"Schema validation failed for {path}: {'; '.join(errors)}"
            )

    return data


def _save_json(path: str, data: dict, schema: dict | None = None) -> None:
    """Save data to a JSON file atomically, with optional schema validation.

    Validates against the schema before writing to prevent persisting
    invalid data.

    Args:
        path: Target file path.
        data: Dictionary to serialize.
        schema: If provided, validate data before writing.

    Raises:
        ValueError: If schema validation fails (file is NOT written).
    """
    if schema is not None:
        errors = _validate_json_schema(data, schema)
        if errors:
            raise ValueError(
                f"Schema validation failed before writing {path}: {'; '.join(errors)}"
            )

    _atomic_write(path, data)


def _append_jsonl(path: str, entry: dict, schema: dict | None = None,
                  boundary: str | None = None) -> None:
    """Append a JSON entry to a JSONL file with optional schema validation.

    Validates the path, optionally validates the entry against a schema
    (logging a warning on failure but still writing), then appends
    ``json.dumps(entry) + "\\n"`` to the file.

    Args:
        path: Target JSONL file path.
        entry: Dictionary to serialize as a single JSON line.
        schema: If provided, validate entry before writing. Warns on
            failure but still writes the entry.
        boundary: If provided, validate that the resolved path starts
            with this directory.
    """
    resolved = _validate_path(path, boundary=boundary)

    if schema is not None:
        errors = _validate_json_schema(entry, schema)
        if errors:
            import logging
            logging.warning(
                "Schema validation warning for %s: %s",
                path, "; ".join(errors),
            )

    with open(resolved, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")