"""Tests for registry.py -- SlotStorageEngine and SlotAPI."""

import json
import os

import pytest

from scripts.init_workspace import init_workspace
from scripts.registry import ConflictError, SlotAPI, SlotStorageEngine
from scripts.schema_validator import SchemaValidationError

# Resolve schemas/ relative to the project root
SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


@pytest.fixture
def workspace(tmp_path):
    """Create a fresh .system-dev/ workspace in a temp directory."""
    init_workspace(str(tmp_path))
    return str(tmp_path / ".system-dev")


@pytest.fixture
def api(workspace):
    """Create a SlotAPI instance with the temp workspace."""
    return SlotAPI(workspace, SCHEMAS_DIR)


@pytest.fixture
def storage(workspace):
    """Create a SlotStorageEngine instance with the temp workspace."""
    return SlotStorageEngine(workspace)


class TestSlotAPI:
    def test_create_slot(self, api, workspace):
        """Create a component, verify returned slot_id format, version=1, file on disk."""
        result = api.create("component", {"name": "Auth Service"})
        assert result["status"] == "created"
        assert result["slot_id"].startswith("comp-")
        assert result["version"] == 1

        # Verify file exists on disk
        slot = api.read(result["slot_id"])
        assert slot is not None
        assert slot["name"] == "Auth Service"

    def test_read_slot(self, api):
        """Create then read, verify content matches."""
        result = api.create("component", {"name": "Database"})
        slot = api.read(result["slot_id"])
        assert slot is not None
        assert slot["name"] == "Database"
        assert slot["version"] == 1
        assert slot["slot_type"] == "component"

    def test_update_slot(self, api):
        """Create, update, verify version incremented to 2."""
        result = api.create("component", {"name": "Original"})
        slot_id = result["slot_id"]

        update_result = api.update(slot_id, {"name": "Updated"})
        assert update_result["status"] == "updated"
        assert update_result["version"] == 2

        slot = api.read(slot_id)
        assert slot["name"] == "Updated"
        assert slot["version"] == 2

    def test_update_optimistic_locking(self, api):
        """Optimistic locking: first update succeeds, stale version rejected."""
        result = api.create("component", {"name": "Original"})
        slot_id = result["slot_id"]

        # Update with correct expected_version=1 succeeds
        api.update(slot_id, {"name": "V2"}, expected_version=1)

        # Update with stale expected_version=1 raises ConflictError (now v2)
        with pytest.raises(ConflictError) as exc_info:
            api.update(slot_id, {"name": "V3"}, expected_version=1)
        assert exc_info.value.expected_version == 1
        assert exc_info.value.actual_version == 2

    def test_delete_slot(self, api):
        """Create, delete, verify read returns None."""
        result = api.create("component", {"name": "Temp"})
        slot_id = result["slot_id"]

        delete_result = api.delete(slot_id)
        assert delete_result["status"] == "deleted"

        assert api.read(slot_id) is None

    def test_query_by_type(self, api):
        """Create 2 components and 1 interface, query components returns 2."""
        api.create("component", {"name": "Comp A"})
        api.create("component", {"name": "Comp B"})
        api.create("interface", {"name": "Intf A"})

        components = api.query("component")
        assert len(components) == 2

        interfaces = api.query("interface")
        assert len(interfaces) == 1

    def test_query_with_filter(self, api):
        """Create slots with different names, filter by name returns matching only."""
        api.create("component", {"name": "Alpha"})
        api.create("component", {"name": "Beta"})

        results = api.query("component", {"name": "Alpha"})
        assert len(results) == 1
        assert results[0]["name"] == "Alpha"

    def test_create_validates_schema(self, api):
        """Creating component missing 'name' raises SchemaValidationError."""
        with pytest.raises(SchemaValidationError):
            api.create("component", {})

    def test_update_validates_schema(self, api):
        """Updating with invalid content raises SchemaValidationError."""
        result = api.create("component", {"name": "Valid"})
        slot_id = result["slot_id"]

        with pytest.raises(SchemaValidationError):
            api.update(slot_id, {"name": ""})  # minLength=1 violation

    def test_create_generates_correct_id_prefix(self, api):
        """Each slot type gets the correct ID prefix."""
        comp = api.create("component", {"name": "C"})
        assert comp["slot_id"].startswith("comp-")

        intf = api.create("interface", {"name": "I"})
        assert intf["slot_id"].startswith("intf-")

        cntr = api.create("contract", {"name": "K"})
        assert cntr["slot_id"].startswith("cntr-")

        rref = api.create("requirement-ref", {"name": "R"})
        assert rref["slot_id"].startswith("rref-")


class TestSlotStorageEngine:
    def test_rebuild_index(self, api, workspace):
        """Create slots, corrupt index, rebuild, verify all slots recovered."""
        r1 = api.create("component", {"name": "A"})
        r2 = api.create("component", {"name": "B"})

        # Corrupt the index by emptying slots
        index_path = os.path.join(workspace, "index.json")
        with open(index_path, "w") as f:
            json.dump({"schema_version": "1.0.0", "updated_at": "", "slots": {}}, f)

        # Verify reads fail with corrupted index
        assert api.read(r1["slot_id"]) is None

        # Rebuild index from disk
        storage = SlotStorageEngine(workspace)
        result = storage.rebuild_index()
        assert result["rebuilt"] == 2

        # Verify reads work again
        slot1 = api.read(r1["slot_id"])
        slot2 = api.read(r2["slot_id"])
        assert slot1 is not None
        assert slot2 is not None
        assert slot1["name"] == "A"
        assert slot2["name"] == "B"

    def test_delete_nonexistent_returns_false(self, storage):
        """Deleting a nonexistent slot returns False."""
        assert storage.delete("comp-nonexistent") is False
