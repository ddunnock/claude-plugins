"""Tests for the append-only JSONL change journal."""

import json
import os

import pytest

from scripts.change_journal import ChangeJournal


class TestChangeJournal:
    """Tests for ChangeJournal class."""

    def test_append_creates_entry(self, tmp_path):
        """Append creates a JSONL line with all required fields."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        entry = journal.append(
            slot_id="comp-123",
            slot_type="component",
            operation="create",
            version_before=0,
            version_after=1,
            agent_id="test-agent",
            summary="Created component",
            old_content=None,
            new_content={"name": "Widget"},
        )

        # Verify returned entry
        assert entry["slot_id"] == "comp-123"
        assert entry["slot_type"] == "component"
        assert entry["operation"] == "create"
        assert entry["version_before"] == 0
        assert entry["version_after"] == 1
        assert entry["agent_id"] == "test-agent"
        assert entry["summary"] == "Created component"
        assert "timestamp" in entry
        assert "diff" in entry

        # Verify file content
        with open(journal_path) as f:
            lines = f.readlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["slot_id"] == "comp-123"

    def test_append_includes_diff(self, tmp_path):
        """Verify diff field contains RFC 6902 ops."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        # Create entry
        entry = journal.append(
            slot_id="comp-123",
            slot_type="component",
            operation="create",
            version_before=0,
            version_after=1,
            agent_id="test",
            summary="Created",
            old_content=None,
            new_content={"name": "Widget"},
        )
        assert entry["diff"] == [{"op": "add", "path": "", "value": {"name": "Widget"}}]

        # Update entry
        entry2 = journal.append(
            slot_id="comp-123",
            slot_type="component",
            operation="update",
            version_before=1,
            version_after=2,
            agent_id="test",
            summary="Updated",
            old_content={"name": "Widget"},
            new_content={"name": "Widget v2"},
        )
        assert any(op["op"] == "replace" for op in entry2["diff"])

    def test_query_by_slot(self, tmp_path):
        """Query returns correct subset for a slot ID."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        # Append entries for two different slots
        journal.append("comp-1", "component", "create", 0, 1, "a", "c1", None, {"n": 1})
        journal.append("comp-2", "component", "create", 0, 1, "a", "c2", None, {"n": 2})
        journal.append("comp-1", "component", "update", 1, 2, "a", "u1", {"n": 1}, {"n": 3})

        result = journal.query_by_slot("comp-1")
        assert len(result) == 2
        assert all(e["slot_id"] == "comp-1" for e in result)

        result2 = journal.query_by_slot("comp-2")
        assert len(result2) == 1

    def test_query_time_range(self, tmp_path):
        """Time range query filters entries correctly."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        # Append entries (timestamps are auto-generated close together)
        journal.append("comp-1", "component", "create", 0, 1, "a", "c1", None, {"n": 1})

        # Get the timestamp from the first entry to build range
        entries = journal.query_all()
        ts = entries[0]["timestamp"]

        # Query with range that includes all entries
        result = journal.query_time_range("2020-01-01T00:00:00", "2030-01-01T00:00:00")
        assert len(result) == 1

        # Query with range that excludes all entries (far future)
        result_empty = journal.query_time_range("2099-01-01T00:00:00", "2099-12-31T00:00:00")
        assert len(result_empty) == 0

    def test_corrupt_last_line_handled(self, tmp_path):
        """Corrupt last line is skipped gracefully."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        # Write valid entries
        journal.append("comp-1", "component", "create", 0, 1, "a", "c", None, {"n": 1})
        journal.append("comp-1", "component", "update", 1, 2, "a", "u", {"n": 1}, {"n": 2})

        # Append corrupt data
        with open(journal_path, "a") as f:
            f.write("this is not valid json\n")

        # query_all should skip the corrupt line
        result = journal.query_all()
        assert len(result) == 2
        assert result[0]["operation"] == "create"
        assert result[1]["operation"] == "update"

    def test_empty_journal_returns_empty(self, tmp_path):
        """Query on non-existent file returns empty list."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        assert journal.query_all() == []
        assert journal.query_by_slot("comp-1") == []
        assert journal.query_time_range("2020-01-01", "2030-01-01") == []

    def test_empty_existing_file_returns_empty(self, tmp_path):
        """Query on empty existing file returns empty list."""
        journal_path = str(tmp_path / "journal.jsonl")
        with open(journal_path, "w") as f:
            pass  # Create empty file

        journal = ChangeJournal(journal_path)
        assert journal.query_all() == []

    def test_delete_entry_diff(self, tmp_path):
        """Delete operation produces correct diff."""
        journal_path = str(tmp_path / "journal.jsonl")
        journal = ChangeJournal(journal_path)

        entry = journal.append(
            slot_id="comp-1",
            slot_type="component",
            operation="delete",
            version_before=2,
            version_after=0,
            agent_id="test",
            summary="Deleted",
            old_content={"name": "Widget"},
            new_content=None,
        )
        assert entry["diff"] == [{"op": "remove", "path": "", "value": {"name": "Widget"}}]
