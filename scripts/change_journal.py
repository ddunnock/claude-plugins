"""Append-only JSONL change journal for the Design Registry.

Records every slot mutation with timestamps, agent IDs, operation details,
and RFC 6902 diffs. Supports time-range and per-slot queries.

References:
    DREG-06 (change journal), REQ-207..214, REQ-406, REQ-471, REQ-479
"""

import json
import logging
import os
from datetime import datetime, timezone

from scripts.json_diff import json_diff

logger = logging.getLogger(__name__)


class ChangeJournal:
    """Append-only JSONL change journal.

    Each mutation to the Design Registry produces one JSON line in the
    journal file. Entries are immutable once written. The journal
    supports queries by slot ID and by UTC time range.

    Args:
        journal_path: Path to the journal.jsonl file.
    """

    def __init__(self, journal_path: str):
        """Initialize with path to journal file.

        Args:
            journal_path: Absolute or relative path to journal.jsonl.
                Created on first append if it does not exist.
        """
        self._path = journal_path

    def append(
        self,
        slot_id: str,
        slot_type: str,
        operation: str,
        version_before: int,
        version_after: int,
        agent_id: str,
        summary: str,
        old_content: dict | None,
        new_content: dict | None,
    ) -> dict:
        """Append a journal entry with RFC 6902 diff. Flushes and fsyncs.

        Args:
            slot_id: The slot identifier.
            slot_type: The slot type (e.g., "component").
            operation: The operation type ("create", "update", "delete").
            version_before: Slot version before the operation (0 for create).
            version_after: Slot version after the operation (0 for delete).
            agent_id: Identifier of the agent performing the operation.
            summary: Human-readable summary of the change.
            old_content: Previous slot content (None for create).
            new_content: New slot content (None for delete).

        Returns:
            The journal entry dict that was written.
        """
        # Compute RFC 6902 diff
        if operation == "delete":
            diff = [{"op": "remove", "path": "", "value": old_content}]
        elif old_content is None:
            diff = json_diff(None, new_content)
        else:
            diff = json_diff(old_content, new_content)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "slot_id": slot_id,
            "slot_type": slot_type,
            "operation": operation,
            "version_before": version_before,
            "version_after": version_after,
            "agent_id": agent_id,
            "summary": summary,
            "diff": diff,
        }

        line = json.dumps(entry, separators=(",", ":")) + "\n"

        with open(self._path, "a") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        return entry

    def query_by_slot(self, slot_id: str) -> list[dict]:
        """Return all journal entries for a given slot_id, ordered by timestamp.

        Args:
            slot_id: The slot identifier to filter by.

        Returns:
            List of matching journal entry dicts, ordered chronologically.
        """
        return [e for e in self.query_all() if e["slot_id"] == slot_id]

    def query_time_range(self, start: str, end: str) -> list[dict]:
        """Return entries within UTC time range [start, end] inclusive.

        ISO 8601 timestamps are lexicographically sortable, so string
        comparison is used for range filtering.

        Args:
            start: ISO 8601 UTC timestamp for range start (inclusive).
            end: ISO 8601 UTC timestamp for range end (inclusive).

        Returns:
            List of matching journal entry dicts.
        """
        return [
            e for e in self.query_all()
            if start <= e["timestamp"] <= end
        ]

    def query_all(self) -> list[dict]:
        """Return all journal entries. Handles corrupt last line gracefully.

        Per Pitfall 2: wraps each line parse in try/except. If the last
        line is corrupt (partial write from crash), logs a warning and
        skips it. Only the last line can be corrupt in an append-only journal.

        Returns:
            List of all valid journal entry dicts.
        """
        if not os.path.exists(self._path):
            return []

        entries: list[dict] = []
        lines: list[str] = []

        with open(self._path) as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                if i == len(lines) - 1:
                    logger.warning(
                        "Corrupt last line in journal at %s, skipping: %s",
                        self._path,
                        line[:100],
                    )
                else:
                    logger.warning(
                        "Corrupt line %d in journal at %s, skipping: %s",
                        i + 1,
                        self._path,
                        line[:100],
                    )

        return entries
