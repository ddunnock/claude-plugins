"""Tests for version history reconstruction from journal."""

import pytest

from scripts.change_journal import ChangeJournal
from scripts.version_manager import VersionManager


class TestVersionManager:
    """Tests for VersionManager class."""

    def test_get_history(self, tmp_path):
        """Get history returns version metadata for all mutations."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        # Create and update
        journal.append("comp-1", "component", "create", 0, 1, "agent-a", "Created", None, {"name": "W"})
        journal.append("comp-1", "component", "update", 1, 2, "agent-b", "Updated", {"name": "W"}, {"name": "W2"})

        history = vm.get_history("comp-1")
        assert len(history) == 2
        assert history[0]["version"] == 1
        assert history[0]["operation"] == "create"
        assert history[0]["agent_id"] == "agent-a"
        assert history[1]["version"] == 2
        assert history[1]["operation"] == "update"
        assert history[1]["agent_id"] == "agent-b"

    def test_get_version_reconstruction(self, tmp_path):
        """Reconstruct v1 from journal when current is v2."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        v1_content = {"name": "Widget", "status": "proposed"}
        v2_content = {"name": "Widget v2", "status": "approved"}

        journal.append("comp-1", "component", "create", 0, 1, "a", "Created", None, v1_content)
        journal.append("comp-1", "component", "update", 1, 2, "a", "Updated", v1_content, v2_content)

        # Reconstruct v1
        result = vm.get_version("comp-1", 1, v2_content)
        assert result is not None
        assert result["name"] == "Widget"
        assert result["status"] == "proposed"

    def test_get_version_current_returns_current(self, tmp_path):
        """Requesting current version returns current_content."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        current = {"name": "Widget"}
        journal.append("comp-1", "component", "create", 0, 1, "a", "Created", None, current)

        result = vm.get_version("comp-1", 1, current)
        assert result == current

    def test_get_version_missing_returns_none(self, tmp_path):
        """Request version with no journal entries returns None."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        result = vm.get_version("comp-nonexistent", 1, {"name": "test"})
        assert result is None

    def test_get_version_future_returns_none(self, tmp_path):
        """Request version beyond latest returns None."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        journal.append("comp-1", "component", "create", 0, 1, "a", "Created", None, {"name": "W"})

        result = vm.get_version("comp-1", 5, {"name": "W"})
        assert result is None

    def test_get_current_version(self, tmp_path):
        """Get current version returns latest version number."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        journal.append("comp-1", "component", "create", 0, 1, "a", "Created", None, {"name": "W"})
        journal.append("comp-1", "component", "update", 1, 2, "a", "Updated", {"name": "W"}, {"name": "W2"})

        assert vm.get_current_version("comp-1") == 2

    def test_get_current_version_none(self, tmp_path):
        """Get current version returns None if no entries."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        assert vm.get_current_version("comp-nonexistent") is None

    def test_get_history_empty(self, tmp_path):
        """Get history for non-existent slot returns empty list."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        assert vm.get_history("comp-nonexistent") == []

    def test_multi_version_reconstruction(self, tmp_path):
        """Reconstruct multiple past versions through v1->v2->v3."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)
        vm = VersionManager(journal)

        v1 = {"name": "A", "count": 1}
        v2 = {"name": "B", "count": 1}
        v3 = {"name": "B", "count": 3}

        journal.append("comp-1", "component", "create", 0, 1, "a", "v1", None, v1)
        journal.append("comp-1", "component", "update", 1, 2, "a", "v2", v1, v2)
        journal.append("comp-1", "component", "update", 2, 3, "a", "v3", v2, v3)

        # Reconstruct v1
        r1 = vm.get_version("comp-1", 1, v3)
        assert r1 == v1

        # Reconstruct v2
        r2 = vm.get_version("comp-1", 2, v3)
        assert r2 == v2

        # Current v3
        r3 = vm.get_version("comp-1", 3, v3)
        assert r3 == v3
