"""Tests for workspace initialization and shared I/O utilities."""

import json
import os
import sys

import pytest

# Add project root to path so we can import scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.init_workspace import init_workspace
from scripts.shared_io import (
    atomic_write,
    cleanup_orphaned_temps,
    validate_path,
)


class TestInitWorkspace:
    """Tests for init_workspace function."""

    def test_init_creates_workspace(self, tmp_path):
        """init_workspace creates all required directories and files."""
        result = init_workspace(str(tmp_path))

        assert result["status"] == "created"
        assert len(result["paths"]) > 0

        # Verify directories
        workspace = tmp_path / ".system-dev"
        assert workspace.is_dir()
        assert (workspace / "registry" / "components").is_dir()
        assert (workspace / "registry" / "interfaces").is_dir()
        assert (workspace / "registry" / "contracts").is_dir()
        assert (workspace / "registry" / "requirement-refs").is_dir()

        # Verify files
        assert (workspace / "journal.jsonl").is_file()
        assert (workspace / "index.json").is_file()
        assert (workspace / "config.json").is_file()

        # Verify journal is empty
        assert (workspace / "journal.jsonl").read_text() == ""

    def test_init_existing_workspace_warns(self, tmp_path):
        """init_workspace returns warning when workspace already exists."""
        # First init
        result1 = init_workspace(str(tmp_path))
        assert result1["status"] == "created"

        # Second init
        result2 = init_workspace(str(tmp_path))
        assert result2["status"] == "exists"
        assert len(result2["warnings"]) > 0
        assert "already exists" in result2["warnings"][0]

    def test_init_index_json_valid(self, tmp_path):
        """index.json has correct initial schema."""
        init_workspace(str(tmp_path))

        index_path = tmp_path / ".system-dev" / "index.json"
        data = json.loads(index_path.read_text())

        assert data["schema_version"] == "1.0.0"
        assert "updated_at" in data
        assert data["slots"] == {}

    def test_init_config_json_valid(self, tmp_path):
        """config.json has correct initial schema."""
        init_workspace(str(tmp_path))

        config_path = tmp_path / ".system-dev" / "config.json"
        data = json.loads(config_path.read_text())

        assert data["schema_version"] == "1.0.0"
        assert data["workspace_version"] == "0.1.0"
        assert "created_at" in data


class TestInitWorkspaceViewSpecs:
    """Tests for view-specs directory creation in init_workspace."""

    def test_init_creates_view_specs_directory(self, tmp_path):
        """init_workspace creates .system-dev/view-specs/ directory."""
        result = init_workspace(str(tmp_path))

        assert result["status"] == "created"
        workspace = tmp_path / ".system-dev"
        assert (workspace / "view-specs").is_dir()

    def test_init_view_specs_in_created_paths(self, tmp_path):
        """init_workspace returns view-specs path in created paths list."""
        result = init_workspace(str(tmp_path))

        view_specs_path = str(tmp_path / ".system-dev" / "view-specs")
        assert view_specs_path in result["paths"]

    def test_existing_workspace_does_not_fail_with_view_specs(self, tmp_path):
        """Existing workspace (status=exists) does not fail due to view-specs."""
        # First init creates workspace
        result1 = init_workspace(str(tmp_path))
        assert result1["status"] == "created"

        # Second init should return exists without error
        result2 = init_workspace(str(tmp_path))
        assert result2["status"] == "exists"
        assert len(result2["warnings"]) > 0


class TestAtomicWrite:
    """Tests for atomic_write function."""

    def test_atomic_write_creates_file(self, tmp_path):
        """atomic_write creates a file with correct JSON content."""
        filepath = str(tmp_path / "test.json")
        data = {"key": "value", "number": 42}

        atomic_write(filepath, data)

        assert os.path.exists(filepath)
        with open(filepath) as f:
            loaded = json.load(f)
        assert loaded == data


class TestValidatePath:
    """Tests for validate_path function."""

    def test_validate_path_rejects_traversal(self, tmp_path):
        """validate_path raises ValueError for path traversal attempts."""
        workspace_root = str(tmp_path / "workspace")
        os.makedirs(workspace_root)

        # Attempt to traverse outside workspace
        malicious_path = os.path.join(workspace_root, "..", "..", "etc", "passwd")

        with pytest.raises(ValueError, match="Path traversal detected"):
            validate_path(malicious_path, workspace_root)

    def test_validate_path_accepts_valid_path(self, tmp_path):
        """validate_path accepts paths within the workspace."""
        workspace_root = str(tmp_path / "workspace")
        os.makedirs(workspace_root)

        valid_path = os.path.join(workspace_root, "registry", "components")
        result = validate_path(valid_path, workspace_root)

        assert result.startswith(os.path.realpath(workspace_root))


class TestCleanupOrphanedTemps:
    """Tests for cleanup_orphaned_temps function."""

    def test_cleanup_orphaned_temps(self, tmp_path):
        """cleanup_orphaned_temps removes .tmp files and returns their paths."""
        # Create some .tmp files
        tmp_file1 = tmp_path / "orphan1.tmp"
        tmp_file2 = tmp_path / "subdir" / "orphan2.tmp"
        os.makedirs(tmp_path / "subdir")
        tmp_file1.write_text("orphaned")
        tmp_file2.write_text("orphaned")

        # Also create a non-.tmp file that should not be removed
        keep_file = tmp_path / "keep.json"
        keep_file.write_text("{}")

        cleaned = cleanup_orphaned_temps(str(tmp_path))

        assert len(cleaned) == 2
        assert not tmp_file1.exists()
        assert not tmp_file2.exists()
        assert keep_file.exists()
