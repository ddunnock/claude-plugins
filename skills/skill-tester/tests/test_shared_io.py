"""Tests for shared_io.py utility functions.

Covers all five test categories:
  1. Unit tests
  2. Security tests
  3. Edge cases
  4. Performance tests
  5. Chaos tests
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from shared_io import (
    _reject_traversal,
    _check_boundary,
    _atomic_write,
    _validate_path,
    _validate_dir_path,
    _validate_json_schema,
    _load_json,
    _save_json,
)


# ---------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------

def test_reject_traversal_clean_path():
    """_reject_traversal accepts paths without '..' segments."""
    _reject_traversal("/safe/path/to/file.json")  # Should not raise


def test_reject_traversal_rejects_dotdot():
    """_reject_traversal raises ValueError for paths containing '..'."""
    with pytest.raises(ValueError, match="traversal"):
        _reject_traversal("../secret/file.json")


def test_check_boundary_within_boundary(tmp_path):
    """_check_boundary accepts paths within the boundary directory."""
    boundary = str(tmp_path)
    resolved = str(tmp_path / "subdir" / "file.json")
    _check_boundary(resolved, boundary)  # Should not raise


def test_check_boundary_rejects_outside(tmp_path):
    """_check_boundary raises ValueError for paths outside boundary."""
    boundary = str(tmp_path / "allowed")
    boundary_path = Path(boundary)
    boundary_path.mkdir()
    outside = str(tmp_path / "forbidden" / "file.json")
    with pytest.raises(ValueError, match="outside boundary"):
        _check_boundary(outside, str(boundary_path.resolve()))


def test_atomic_write_creates_file(tmp_path):
    """_atomic_write creates a file with correct JSON content."""
    target = str(tmp_path / "output.json")
    data = {"status": "ok", "count": 42}
    _atomic_write(target, data)

    assert Path(target).exists()
    with open(target) as f:
        loaded = json.load(f)
    assert loaded == data


def test_atomic_write_replaces_existing(tmp_path):
    """_atomic_write overwrites an existing file atomically."""
    target = str(tmp_path / "output.json")
    Path(target).write_text('{"old": "data"}', encoding="utf-8")

    new_data = {"new": "data"}
    _atomic_write(target, new_data)

    with open(target) as f:
        loaded = json.load(f)
    assert loaded == new_data


def test_validate_path_basic(tmp_path):
    """_validate_path resolves and validates a clean file path."""
    test_file = tmp_path / "test.json"
    test_file.write_text("{}", encoding="utf-8")
    resolved = _validate_path(str(test_file))
    assert resolved == str(test_file.resolve())


def test_validate_dir_path_basic(tmp_path):
    """_validate_dir_path resolves and validates a clean directory path."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()
    resolved = _validate_dir_path(str(test_dir))
    assert resolved == str(test_dir.resolve())


def test_validate_json_schema_valid():
    """_validate_json_schema returns empty list for valid data."""
    schema = {
        "name": {"required": True, "type": str},
        "count": {"required": True, "type": int},
    }
    data = {"name": "test", "count": 5}
    errors = _validate_json_schema(data, schema)
    assert errors == []


def test_validate_json_schema_missing_required():
    """_validate_json_schema detects missing required fields."""
    schema = {
        "name": {"required": True, "type": str},
        "count": {"required": True, "type": int},
    }
    data = {"name": "test"}  # missing 'count'
    errors = _validate_json_schema(data, schema)
    assert len(errors) == 1
    assert "count" in errors[0]
    assert "Missing required field" in errors[0]


def test_load_json_valid_file(tmp_path):
    """_load_json reads and parses a valid JSON file."""
    test_file = tmp_path / "data.json"
    data = {"key": "value", "number": 123}
    test_file.write_text(json.dumps(data), encoding="utf-8")

    loaded = _load_json(str(test_file))
    assert loaded == data


def test_save_json_writes_valid_file(tmp_path):
    """_save_json writes JSON atomically with correct content."""
    target = tmp_path / "output.json"
    data = {"status": "success", "items": [1, 2, 3]}

    _save_json(str(target), data)

    assert target.exists()
    with open(target) as f:
        loaded = json.load(f)
    assert loaded == data


# ---------------------------------------------------------------------------
# Security Tests
# ---------------------------------------------------------------------------

def test_validate_path_rejects_traversal():
    """_validate_path raises ValueError for paths containing '..'."""
    with pytest.raises(ValueError, match="traversal"):
        _validate_path("../secret/file.json")


def test_validate_path_rejects_bad_extension(tmp_path):
    """_validate_path raises ValueError for disallowed extensions."""
    test_file = tmp_path / "file.exe"
    test_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="not in"):
        _validate_path(str(test_file), allowed_extensions=[".json", ".txt"])


def test_validate_dir_path_rejects_traversal():
    """_validate_dir_path raises ValueError for paths containing '..'."""
    with pytest.raises(ValueError, match="traversal"):
        _validate_dir_path("../../../etc")


def test_validate_path_with_boundary_rejects_outside(tmp_path):
    """_validate_path with boundary rejects paths outside boundary."""
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    forbidden = tmp_path / "forbidden"
    forbidden.mkdir()
    test_file = forbidden / "file.json"
    test_file.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="outside boundary"):
        _validate_path(str(test_file), boundary=str(allowed.resolve()))


def test_validate_json_schema_detects_type_mismatch():
    """_validate_json_schema detects type mismatches."""
    schema = {
        "count": {"required": True, "type": int},
    }
    data = {"count": "not an int"}  # wrong type
    errors = _validate_json_schema(data, schema)
    assert len(errors) == 1
    assert "count" in errors[0]
    assert "expected" in errors[0].lower()


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

def test_validate_json_schema_optional_field_missing():
    """_validate_json_schema allows missing optional fields."""
    schema = {
        "name": {"required": True, "type": str},
        "description": {"required": False, "type": str},
    }
    data = {"name": "test"}  # missing optional 'description'
    errors = _validate_json_schema(data, schema)
    assert errors == []


def test_validate_json_schema_nullable_field():
    """_validate_json_schema accepts None for nullable fields."""
    schema = {
        "name": {"required": True, "type": (str, type(None))},
    }
    data = {"name": None}
    errors = _validate_json_schema(data, schema)
    assert errors == []


def test_validate_json_schema_not_a_dict():
    """_validate_json_schema rejects non-dict data."""
    schema = {"name": {"required": True, "type": str}}
    data = ["not", "a", "dict"]
    errors = _validate_json_schema(data, schema)
    assert len(errors) == 1
    assert "Expected dict" in errors[0]


def test_load_json_missing_file(tmp_path):
    """_load_json raises FileNotFoundError for missing files."""
    missing = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        _load_json(str(missing))


def test_load_json_corrupted_file(tmp_path):
    """_load_json raises json.JSONDecodeError for corrupted JSON."""
    corrupted = tmp_path / "corrupted.json"
    corrupted.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        _load_json(str(corrupted))


def test_load_json_with_schema_validation_fails(tmp_path):
    """_load_json with schema raises ValueError if data is invalid."""
    test_file = tmp_path / "data.json"
    data = {"name": "test"}  # missing 'count'
    test_file.write_text(json.dumps(data), encoding="utf-8")

    schema = {
        "name": {"required": True, "type": str},
        "count": {"required": True, "type": int},
    }

    with pytest.raises(ValueError, match="Schema validation failed"):
        _load_json(str(test_file), schema=schema)


def test_save_json_with_schema_validation_fails(tmp_path):
    """_save_json with schema raises ValueError before writing invalid data."""
    target = tmp_path / "output.json"
    data = {"name": "test"}  # missing 'count'

    schema = {
        "name": {"required": True, "type": str},
        "count": {"required": True, "type": int},
    }

    with pytest.raises(ValueError, match="Schema validation failed"):
        _save_json(str(target), data, schema=schema)

    # Verify file was NOT created
    assert not target.exists()


def test_atomic_write_empty_dict(tmp_path):
    """_atomic_write handles empty dictionary correctly."""
    target = str(tmp_path / "empty.json")
    _atomic_write(target, {})

    assert Path(target).exists()
    with open(target) as f:
        loaded = json.load(f)
    assert loaded == {}


def test_validate_path_relative_path(tmp_path):
    """_validate_path resolves relative paths correctly."""
    test_file = tmp_path / "relative.json"
    test_file.write_text("{}", encoding="utf-8")

    # Change to tmp_path and use relative path
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        resolved = _validate_path("relative.json")
        assert resolved == str(test_file.resolve())
    finally:
        os.chdir(original_cwd)


# ---------------------------------------------------------------------------
# Performance Tests
# ---------------------------------------------------------------------------

def test_atomic_write_multiple_calls(tmp_path):
    """_atomic_write handles 100 successive writes without degradation."""
    import time
    target = str(tmp_path / "perf_test.json")
    start = time.monotonic()

    for i in range(100):
        _atomic_write(target, {"iteration": i})

    elapsed = time.monotonic() - start
    assert elapsed < 5.0, f"Took {elapsed:.2f}s, expected < 5s"

    # Verify final content
    with open(target) as f:
        loaded = json.load(f)
    assert loaded["iteration"] == 99


def test_validate_json_schema_large_dict():
    """_validate_json_schema handles dictionaries with many fields."""
    schema = {f"field_{i}": {"required": True, "type": str} for i in range(100)}
    data = {f"field_{i}": f"value_{i}" for i in range(100)}

    errors = _validate_json_schema(data, schema)
    assert errors == []


# ---------------------------------------------------------------------------
# Chaos Tests
# ---------------------------------------------------------------------------

def test_atomic_write_readonly_directory(tmp_path):
    """_atomic_write raises OSError for read-only target directory."""
    import os
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    target = str(readonly_dir / "file.json")

    # Make directory read-only
    os.chmod(readonly_dir, 0o555)

    try:
        with pytest.raises(OSError):
            _atomic_write(target, {"data": "test"})
    finally:
        # Restore permissions for cleanup
        os.chmod(readonly_dir, 0o755)


def test_load_json_not_a_dict(tmp_path):
    """_load_json raises ValueError if JSON is not an object."""
    test_file = tmp_path / "array.json"
    test_file.write_text('["array", "not", "object"]', encoding="utf-8")

    with pytest.raises(ValueError, match="Expected JSON object"):
        _load_json(str(test_file))


def test_save_json_non_serializable_data(tmp_path):
    """_save_json raises TypeError for non-JSON-serializable data."""
    target = tmp_path / "output.json"

    # Python set is not JSON-serializable
    data = {"items": {1, 2, 3}}

    with pytest.raises(TypeError):
        _save_json(str(target), data)

    # Verify file was NOT created
    assert not target.exists()