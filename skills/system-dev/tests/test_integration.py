"""End-to-end integration tests for the full Design Registry lifecycle.

Tests the complete flow: init workspace -> create slot -> read -> update ->
query -> history -> version reconstruction -> delete -> journal query.
"""

import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import ConflictError, SlotAPI
from scripts.schema_validator import SchemaValidationError

# Path to the schemas/ directory shipped with the skill
SCHEMAS_DIR = os.path.join(os.path.dirname(__file__), "..", "schemas")


def _make_api(tmp_path) -> SlotAPI:
    """Helper: init workspace and create SlotAPI in tmp_path."""
    init_workspace(str(tmp_path))
    workspace = str(tmp_path / ".system-dev")
    return SlotAPI(workspace, SCHEMAS_DIR)


class TestFullLifecycle:
    """Full end-to-end lifecycle test."""

    def test_full_lifecycle(self, tmp_path):
        """Complete lifecycle: create -> read -> update -> query -> history -> reconstruct -> delete -> journal."""
        api = _make_api(tmp_path)

        # Create a component
        result = api.create("component", {"name": "Widget", "description": "A widget"}, agent_id="test-agent")
        assert result["status"] == "created"
        slot_id = result["slot_id"]
        assert result["version"] == 1
        assert slot_id.startswith("comp-")

        # Read it
        slot = api.read(slot_id)
        assert slot is not None
        assert slot["name"] == "Widget"
        assert slot["version"] == 1

        # Update with optimistic locking
        result2 = api.update(
            slot_id,
            {"name": "Widget v2", "description": "Updated widget"},
            expected_version=1,
            agent_id="test-agent",
        )
        assert result2["status"] == "updated"
        assert result2["version"] == 2

        # Read updated
        slot2 = api.read(slot_id)
        assert slot2["name"] == "Widget v2"
        assert slot2["version"] == 2

        # Query components
        components = api.query("component")
        assert len(components) == 1
        assert components[0]["slot_id"] == slot_id

        # Check history
        history = api.history(slot_id)
        assert len(history) == 2
        assert history[0]["operation"] == "create"
        assert history[0]["version"] == 1
        assert history[1]["operation"] == "update"
        assert history[1]["version"] == 2

        # Reconstruct version 1
        v1 = api.get_version(slot_id, 1)
        assert v1 is not None
        assert v1["name"] == "Widget"
        assert v1["version"] == 1

        # Delete
        result3 = api.delete(slot_id, agent_id="test-agent")
        assert result3["status"] == "deleted"
        assert api.read(slot_id) is None

        # Journal has 3 entries: create, update, delete
        journal = api.journal_query()
        assert len(journal) == 3
        assert journal[0]["operation"] == "create"
        assert journal[1]["operation"] == "update"
        assert journal[2]["operation"] == "delete"

        # Time range query (broad range covering all entries)
        ranged = api.journal_query(start="2020-01-01T00:00:00", end="2030-01-01T00:00:00")
        assert len(ranged) == 3

        # Time range query (future, no results)
        empty = api.journal_query(start="2099-01-01T00:00:00", end="2099-12-31T00:00:00")
        assert len(empty) == 0


class TestSchemaRejectionNoJournal:
    """Schema validation errors should not produce journal entries."""

    def test_schema_rejection_no_journal_entry(self, tmp_path):
        """Invalid create produces SchemaValidationError and no journal entry."""
        api = _make_api(tmp_path)

        # Try to create without required 'name' field
        with pytest.raises(SchemaValidationError):
            api.create("component", {"description": "Missing name"})

        # Journal should be empty
        journal = api.journal_query()
        assert len(journal) == 0


class TestOptimisticLockingNoJournal:
    """Conflict errors should not produce journal entries."""

    def test_optimistic_locking_no_journal_entry(self, tmp_path):
        """ConflictError on update produces no journal entry for the failed attempt."""
        api = _make_api(tmp_path)

        # Create v1
        result = api.create("component", {"name": "Widget"})
        slot_id = result["slot_id"]

        # Update to v2
        api.update(slot_id, {"name": "Widget v2"}, expected_version=1)

        # Try update with stale expected_version=1 (current is v2)
        with pytest.raises(ConflictError):
            api.update(slot_id, {"name": "Widget v3"}, expected_version=1)

        # Journal should have exactly 2 entries (create + update), not 3
        journal = api.journal_query()
        assert len(journal) == 2
        assert journal[0]["operation"] == "create"
        assert journal[1]["operation"] == "update"


class TestMultipleSlotTypes:
    """Test that all slot types work correctly."""

    def test_multiple_slot_types(self, tmp_path):
        """Create one of each type, verify correct ID prefixes, queries, and journal."""
        api = _make_api(tmp_path)

        types_and_prefixes = {
            "component": "comp-",
            "interface": "intf-",
            "contract": "cntr-",
            "requirement-ref": "rref-",
        }

        created_ids = {}
        for slot_type, prefix in types_and_prefixes.items():
            result = api.create(slot_type, {"name": f"Test {slot_type}"})
            assert result["slot_id"].startswith(prefix)
            created_ids[slot_type] = result["slot_id"]

        # Query each type returns 1 result
        for slot_type in types_and_prefixes:
            results = api.query(slot_type)
            assert len(results) == 1
            assert results[0]["slot_type"] == slot_type

        # Journal has 4 entries
        journal = api.journal_query()
        assert len(journal) == 4


class TestJournalSurvivesRestart:
    """Journal data persists across SlotAPI instances."""

    def test_journal_survives_restart(self, tmp_path):
        """Data from first session is visible in second session."""
        # First session
        api1 = _make_api(tmp_path)
        result = api1.create("component", {"name": "Persistent"})
        slot_id = result["slot_id"]
        api1.update(slot_id, {"name": "Persistent v2"}, expected_version=1)

        # Second session (new SlotAPI instance, same workspace)
        workspace = str(tmp_path / ".system-dev")
        api2 = SlotAPI(workspace, SCHEMAS_DIR)

        # History from first session is visible
        history = api2.history(slot_id)
        assert len(history) == 2

        # Journal entries from first session are visible
        journal = api2.journal_query()
        assert len(journal) == 2

        # Version reconstruction still works
        v1 = api2.get_version(slot_id, 1)
        assert v1 is not None
        assert v1["name"] == "Persistent"
