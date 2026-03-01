"""Slot storage engine and API for the Design Registry.

Provides SlotStorageEngine for atomic persistence with index management,
and SlotAPI as the single entry point for all slot CRUD operations (XCUT-04).
Every mutation is automatically journaled with RFC 6902 diffs (DREG-06),
and version history is queryable (DREG-05).
"""

import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from scripts.change_journal import ChangeJournal
from scripts.schema_validator import SchemaValidationError, SchemaValidator
from scripts.shared_io import atomic_write, ensure_directory, validate_path
from scripts.version_manager import VersionManager

# Maps slot types to their registry subdirectory names
SLOT_TYPE_DIRS: dict[str, str] = {
    "component": "components",
    "interface": "interfaces",
    "contract": "contracts",
    "requirement-ref": "requirement-refs",
    "need": "needs",
    "requirement": "requirements",
    "source": "sources",
    "assumption": "assumptions",
    "traceability-link": "traceability-links",
    "component-proposal": "component-proposals",
}

# Maps slot types to their ID prefixes
SLOT_ID_PREFIXES: dict[str, str] = {
    "component": "comp",
    "interface": "intf",
    "contract": "cntr",
    "requirement-ref": "rref",
    "need": "need",
    "requirement": "requirement",
    "source": "source",
    "assumption": "assumption",
    "traceability-link": "trace",
    "component-proposal": "cprop",
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
    handles optimistic locking, and automatically journals every mutation
    with RFC 6902 diffs. Supports version history queries and past-version
    reconstruction.

    Args:
        workspace_root: Path to the .system-dev/ directory.
        schemas_dir: Path to the schemas/ directory with JSON Schema files.
        journal_path: Optional path to journal.jsonl (defaults to
            workspace_root/journal.jsonl).
    """

    def __init__(
        self,
        workspace_root: str,
        schemas_dir: str,
        journal_path: str | None = None,
    ):
        """Initialize all subsystems including journal and version manager.

        Args:
            workspace_root: Absolute path to .system-dev/ directory.
            schemas_dir: Absolute path to schemas/ directory.
            journal_path: Optional override for journal file location.
        """
        self._storage = SlotStorageEngine(workspace_root)
        self._validator = SchemaValidator(schemas_dir)

        if journal_path is None:
            journal_path = os.path.join(workspace_root, "journal.jsonl")
        self._journal = ChangeJournal(journal_path)
        self._versions = VersionManager(self._journal)

    def create(
        self, slot_type: str, content: dict, agent_id: str = "user"
    ) -> dict:
        """Create a new slot with generated ID and version 1.

        Validates content, persists to storage, and appends a journal entry
        with the full object as an RFC 6902 add operation.

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

        self._journal.append(
            slot_id,
            slot_type,
            "create",
            0,
            1,
            agent_id,
            f"Created {slot_type} '{content.get('name', slot_id)}'",
            None,
            content,
        )

        return {"status": "created", "slot_id": slot_id, "version": 1}

    def ingest(
        self,
        slot_id: str,
        slot_type: str,
        content: dict,
        agent_id: str = "ingestion-engine",
    ) -> dict:
        """Ingest an upstream entity as a slot with a deterministic ID.

        Unlike create(), this method accepts a pre-determined slot_id
        (e.g., "need:NEED-001") rather than auto-generating one. It is
        designed for bulk ingestion from upstream registries.

        Conflict handling:
        - If slot exists with version > 1 (manually edited), SKIP to
          preserve local edits. Returns status "conflict".
        - If slot exists with version 1 (still at ingested version),
          treat as update: increment version, preserve created_at.
        - If slot does not exist, create with version 1.

        Does NOT write individual journal entries -- the caller writes
        a batch summary entry after all ingestion is complete.

        Args:
            slot_id: Deterministic slot ID (e.g., "need:NEED-001").
            slot_type: The slot type (e.g., "need", "requirement").
            content: Mapped slot content (without system fields).
            agent_id: Identifier of the ingesting agent.

        Returns:
            Dict with status ("created", "updated", or "conflict"),
            slot_id, and version.

        Raises:
            ValueError: If slot_type is unknown.
            SchemaValidationError: If content fails schema validation.
        """
        if slot_type not in SLOT_TYPE_DIRS:
            raise ValueError(
                f"Unknown slot type: '{slot_type}'. "
                f"Supported types: {sorted(SLOT_TYPE_DIRS.keys())}"
            )

        now = datetime.now(timezone.utc).isoformat()

        # Check if slot already exists
        existing = self._storage.read(slot_id)

        if existing is not None:
            if existing["version"] > 1:
                # Manually edited -- do not overwrite
                return {
                    "status": "conflict",
                    "slot_id": slot_id,
                    "version": existing["version"],
                }

            # Still at ingested version -- update in place
            new_version = existing["version"] + 1
            content["slot_id"] = slot_id
            content["slot_type"] = slot_type
            content["version"] = new_version
            content["created_at"] = existing["created_at"]
            content["updated_at"] = now

            self._validator.validate_or_raise(slot_type, content)
            self._storage.write(slot_id, slot_type, content)

            return {
                "status": "updated",
                "slot_id": slot_id,
                "version": new_version,
            }

        # New slot -- create with version 1
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

        Captures old content before write, persists the update, then
        appends a journal entry with the field-level RFC 6902 diff.

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

        # Capture old content for diff before mutation
        old_content = dict(current)

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

        self._journal.append(
            slot_id,
            current["slot_type"],
            "update",
            current_version,
            new_version,
            agent_id,
            f"Updated {current['slot_type']} '{slot_id}' to v{new_version}",
            old_content,
            content,
        )

        return {"status": "updated", "slot_id": slot_id, "version": new_version}

    def delete(self, slot_id: str, agent_id: str = "user") -> dict:
        """Delete a slot by ID.

        Reads the slot before deletion to capture content and version
        for the journal entry, then deletes and journals.

        Args:
            slot_id: The unique slot identifier.
            agent_id: Identifier of the deleting agent.

        Returns:
            Dict with status and slot_id.

        Raises:
            KeyError: If slot_id does not exist.
        """
        # Read before delete to capture content for journal
        current = self._storage.read(slot_id)
        if current is None:
            raise KeyError(f"Slot not found: '{slot_id}'")

        slot_type = current["slot_type"]
        version = current["version"]
        old_content = dict(current)

        deleted = self._storage.delete(slot_id)
        if not deleted:
            raise KeyError(f"Slot not found: '{slot_id}'")

        self._journal.append(
            slot_id,
            slot_type,
            "delete",
            version,
            0,
            agent_id,
            f"Deleted {slot_type} '{slot_id}'",
            old_content,
            None,
        )

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

    def history(self, slot_id: str) -> list[dict]:
        """Return version history for a slot.

        Args:
            slot_id: The unique slot identifier.

        Returns:
            List of version metadata dicts with version, timestamp,
            agent_id, summary, and operation.
        """
        return self._versions.get_history(slot_id)

    def get_version(self, slot_id: str, version: int) -> dict | None:
        """Reconstruct a specific past version of a slot.

        Reads the current content from storage, then delegates to the
        version manager for reconstruction via journal diffs.

        Args:
            slot_id: The unique slot identifier.
            version: The target version number to reconstruct.

        Returns:
            The reconstructed slot content dict, or None if the slot
            does not exist or reconstruction is not possible.
        """
        current = self._storage.read(slot_id)
        if current is None:
            return None
        return self._versions.get_version(slot_id, version, current)

    def journal_query(
        self, start: str | None = None, end: str | None = None
    ) -> list[dict]:
        """Query journal entries, optionally filtered by time range.

        Args:
            start: ISO 8601 UTC timestamp for range start (inclusive).
            end: ISO 8601 UTC timestamp for range end (inclusive).

        Returns:
            List of journal entry dicts matching the criteria.
        """
        if start is not None and end is not None:
            return self._journal.query_time_range(start, end)
        return self._journal.query_all()
