"""Slot storage engine and API for the Design Registry.

Provides SlotStorageEngine for atomic persistence with index management,
and SlotAPI as the single entry point for all slot CRUD operations (XCUT-04).
"""

import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from scripts.schema_validator import SchemaValidationError, SchemaValidator
from scripts.shared_io import atomic_write, ensure_directory, validate_path

# Maps slot types to their registry subdirectory names
SLOT_TYPE_DIRS: dict[str, str] = {
    "component": "components",
    "interface": "interfaces",
    "contract": "contracts",
    "requirement-ref": "requirement-refs",
}

# Maps slot types to their ID prefixes
SLOT_ID_PREFIXES: dict[str, str] = {
    "component": "comp",
    "interface": "intf",
    "contract": "cntr",
    "requirement-ref": "rref",
}


class ConflictError(Exception):
    """Raised when optimistic locking detects a version mismatch.

    Attributes:
        slot_id: The slot that had a conflict.
        expected_version: The version the caller expected.
        actual_version: The version currently on disk.
    """

    def __init__(self, slot_id: str, expected: int, actual: int):
        super().__init__(
            f"Version conflict for '{slot_id}': expected v{expected}, found v{actual}"
        )
        self.slot_id = slot_id
        self.expected_version = expected
        self.actual_version = actual


class SlotStorageEngine:
    """Low-level storage engine for slot JSON files with index management.

    Handles reading, writing, deleting, and querying slot files on disk.
    All writes are atomic (temp file + fsync + rename). The index is
    updated on every mutation and can be rebuilt from filesystem scan.

    Args:
        workspace_root: Path to the .system-dev/ directory.
    """

    def __init__(self, workspace_root: str):
        """Initialize with .system-dev/ path.

        Args:
            workspace_root: Absolute path to .system-dev/ directory.

        Raises:
            FileNotFoundError: If workspace_root does not exist.
        """
        if not os.path.isdir(workspace_root):
            raise FileNotFoundError(
                f"Workspace not found: {workspace_root}. "
                "Run /system-dev:init first."
            )
        self._root = workspace_root
        self._registry_dir = os.path.join(workspace_root, "registry")
        self._index_path = os.path.join(workspace_root, "index.json")

    def _load_index(self) -> dict:
        """Load index.json from disk."""
        if not os.path.exists(self._index_path):
            return {"schema_version": "1.0.0", "updated_at": "", "slots": {}}
        with open(self._index_path) as f:
            return json.load(f)

    def _save_index(self, index: dict) -> None:
        """Save index.json atomically."""
        index["updated_at"] = datetime.now(timezone.utc).isoformat()
        atomic_write(self._index_path, index)

    def read(self, slot_id: str) -> dict | None:
        """Read a slot by ID from disk.

        Args:
            slot_id: The unique slot identifier.

        Returns:
            Parsed slot dict, or None if not found in the index.
        """
        index = self._load_index()
        entry = index.get("slots", {}).get(slot_id)
        if entry is None:
            return None

        filepath = os.path.join(self._root, entry["path"])
        if not os.path.exists(filepath):
            return None

        with open(filepath) as f:
            return json.load(f)

    def write(self, slot_id: str, slot_type: str, content: dict) -> dict:
        """Write slot file atomically and update index.

        Args:
            slot_id: The unique slot identifier.
            slot_type: The slot type (e.g., "component").
            content: The full slot content dict to persist.

        Returns:
            Dict with "path" key containing the relative path within workspace.

        Raises:
            ValueError: If slot_type is unknown or path traversal detected.
        """
        if slot_type not in SLOT_TYPE_DIRS:
            raise ValueError(f"Unknown slot type: '{slot_type}'")

        type_dir = SLOT_TYPE_DIRS[slot_type]
        relative_path = os.path.join("registry", type_dir, f"{slot_id}.json")
        filepath = os.path.join(self._root, relative_path)

        # Path traversal protection
        validate_path(filepath, self._root)

        # Ensure the type directory exists
        ensure_directory(os.path.dirname(filepath))

        # Atomic write the slot file
        atomic_write(filepath, content)

        # Update the index
        index = self._load_index()
        index["slots"][slot_id] = {
            "path": relative_path,
            "slot_type": slot_type,
            "version": content.get("version", 1),
            "updated_at": content.get("updated_at", ""),
        }
        self._save_index(index)

        return {"path": relative_path}

    def delete(self, slot_id: str) -> bool:
        """Delete slot file and remove from index.

        Args:
            slot_id: The unique slot identifier.

        Returns:
            True if deleted, False if slot was not found.
        """
        index = self._load_index()
        entry = index.get("slots", {}).get(slot_id)
        if entry is None:
            return False

        filepath = os.path.join(self._root, entry["path"])
        if os.path.exists(filepath):
            os.unlink(filepath)

        del index["slots"][slot_id]
        self._save_index(index)
        return True

    def query(self, slot_type: str, filters: dict | None = None) -> list[dict]:
        """Query slots by type with optional field=value filters.

        Args:
            slot_type: The slot type to query (e.g., "component").
            filters: Optional dict of field=value pairs for equality filtering.

        Returns:
            List of slot dicts matching the type and filters.
        """
        index = self._load_index()
        results = []

        for slot_id, entry in index.get("slots", {}).items():
            if entry["slot_type"] != slot_type:
                continue

            filepath = os.path.join(self._root, entry["path"])
            if not os.path.exists(filepath):
                continue

            with open(filepath) as f:
                slot = json.load(f)

            if filters:
                if all(slot.get(k) == v for k, v in filters.items()):
                    results.append(slot)
            else:
                results.append(slot)

        return results

    def rebuild_index(self) -> dict:
        """Rebuild index.json from filesystem scan.

        Walks registry/ subdirectories, reads each .json file, and
        reconstructs the index. Source of truth is files on disk.

        Returns:
            Dict with "rebuilt" count and "removed_stale" count.
        """
        old_index = self._load_index()
        old_slots = set(old_index.get("slots", {}).keys())

        new_slots: dict[str, dict] = {}

        for type_name, dir_name in SLOT_TYPE_DIRS.items():
            type_dir = os.path.join(self._registry_dir, dir_name)
            if not os.path.isdir(type_dir):
                continue

            for filename in os.listdir(type_dir):
                if not filename.endswith(".json"):
                    continue

                filepath = os.path.join(type_dir, filename)
                try:
                    with open(filepath) as f:
                        slot = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

                slot_id = slot.get("slot_id", filename[:-5])
                relative_path = os.path.join("registry", dir_name, filename)

                new_slots[slot_id] = {
                    "path": relative_path,
                    "slot_type": slot.get("slot_type", type_name),
                    "version": slot.get("version", 1),
                    "updated_at": slot.get("updated_at", ""),
                }

        new_index = {
            "schema_version": "1.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "slots": new_slots,
        }
        atomic_write(self._index_path, new_index)

        rebuilt = len(new_slots)
        found_ids = set(new_slots.keys())
        removed_stale = len(old_slots - found_ids)

        return {"rebuilt": rebuilt, "removed_stale": removed_stale}


class SlotAPI:
    """Single entry point for all slot CRUD operations (XCUT-04).

    Enforces validate-before-persist on every write, generates typed IDs,
    and handles optimistic locking for concurrent access.

    Args:
        workspace_root: Path to the .system-dev/ directory.
        schemas_dir: Path to the schemas/ directory with JSON Schema files.
    """

    def __init__(self, workspace_root: str, schemas_dir: str):
        """Initialize all subsystems.

        Args:
            workspace_root: Absolute path to .system-dev/ directory.
            schemas_dir: Absolute path to schemas/ directory.
        """
        self._storage = SlotStorageEngine(workspace_root)
        self._validator = SchemaValidator(schemas_dir)

    def create(
        self, slot_type: str, content: dict, agent_id: str = "user"
    ) -> dict:
        """Create a new slot with generated ID and version 1.

        Args:
            slot_type: The type of slot to create (e.g., "component").
            content: Slot content dict (slot_id, slot_type, version,
                created_at, updated_at will be set automatically).
            agent_id: Identifier of the creating agent.

        Returns:
            Dict with status, slot_id, and version.

        Raises:
            ValueError: If slot_type is unknown.
            SchemaValidationError: If content fails schema validation.
        """
        if slot_type not in SLOT_ID_PREFIXES:
            raise ValueError(
                f"Unknown slot type: '{slot_type}'. "
                f"Supported types: {sorted(SLOT_ID_PREFIXES.keys())}"
            )

        prefix = SLOT_ID_PREFIXES[slot_type]
        slot_id = f"{prefix}-{uuid4()}"
        now = datetime.now(timezone.utc).isoformat()

        content["slot_id"] = slot_id
        content["slot_type"] = slot_type
        content["version"] = 1
        content["created_at"] = now
        content["updated_at"] = now

        self._validator.validate_or_raise(slot_type, content)
        self._storage.write(slot_id, slot_type, content)

        return {"status": "created", "slot_id": slot_id, "version": 1}

    def read(self, slot_id: str) -> dict | None:
        """Read a slot by ID.

        Args:
            slot_id: The unique slot identifier.

        Returns:
            Parsed slot dict, or None if not found.
        """
        return self._storage.read(slot_id)

    def update(
        self,
        slot_id: str,
        content: dict,
        expected_version: int | None = None,
        agent_id: str = "user",
    ) -> dict:
        """Update an existing slot with optimistic locking.

        Args:
            slot_id: The unique slot identifier.
            content: Updated slot content fields.
            expected_version: If provided, reject update when current
                version does not match (optimistic locking).
            agent_id: Identifier of the updating agent.

        Returns:
            Dict with status, slot_id, and new version.

        Raises:
            KeyError: If slot_id does not exist.
            ConflictError: If expected_version does not match current.
            SchemaValidationError: If updated content fails validation.
        """
        current = self._storage.read(slot_id)
        if current is None:
            raise KeyError(f"Slot not found: '{slot_id}'")

        current_version = current["version"]
        if expected_version is not None and expected_version != current_version:
            raise ConflictError(slot_id, expected_version, current_version)

        new_version = current_version + 1
        now = datetime.now(timezone.utc).isoformat()

        # Preserve immutable fields from current slot
        content["slot_id"] = current["slot_id"]
        content["slot_type"] = current["slot_type"]
        content["created_at"] = current["created_at"]
        content["version"] = new_version
        content["updated_at"] = now

        self._validator.validate_or_raise(current["slot_type"], content)
        self._storage.write(slot_id, current["slot_type"], content)

        return {"status": "updated", "slot_id": slot_id, "version": new_version}

    def delete(self, slot_id: str, agent_id: str = "user") -> dict:
        """Delete a slot by ID.

        Args:
            slot_id: The unique slot identifier.
            agent_id: Identifier of the deleting agent.

        Returns:
            Dict with status and slot_id.

        Raises:
            KeyError: If slot_id does not exist.
        """
        deleted = self._storage.delete(slot_id)
        if not deleted:
            raise KeyError(f"Slot not found: '{slot_id}'")
        return {"status": "deleted", "slot_id": slot_id}

    def query(self, slot_type: str, filters: dict | None = None) -> list[dict]:
        """Query slots by type with optional filters.

        Args:
            slot_type: The slot type to query.
            filters: Optional dict of field=value equality filters.

        Returns:
            List of matching slot dicts.
        """
        return self._storage.query(slot_type, filters)
