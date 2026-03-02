"""Version history reconstruction from the change journal.

Provides version history listing and past-version reconstruction
by replaying RFC 6902 diffs forward from the creation entry.

References:
    DREG-05 (version history), REQ-003..005, REQ-225..233, REQ-473
"""

import logging

from scripts.change_journal import ChangeJournal
from scripts.json_diff import apply_patch

logger = logging.getLogger(__name__)


class VersionManager:
    """Reconstructs version history from journal entries.

    Uses the ChangeJournal to look up slot mutations and reconstructs
    past versions by replaying RFC 6902 diffs forward from the creation
    entry to the target version.

    Args:
        journal: A ChangeJournal instance to query for slot history.
    """

    def __init__(self, journal: ChangeJournal):
        """Initialize with a ChangeJournal.

        Args:
            journal: The journal to query for version history.
        """
        self._journal = journal

    def get_history(self, slot_id: str) -> list[dict]:
        """Return version history for a slot.

        Each entry contains version metadata extracted from the journal:
        version number, timestamp, agent_id, summary, and operation.

        Args:
            slot_id: The slot identifier.

        Returns:
            List of version metadata dicts ordered chronologically,
            each with: version, timestamp, agent_id, summary, operation.
        """
        entries = self._journal.query_by_slot(slot_id)
        return [
            {
                "version": entry["version_after"],
                "timestamp": entry["timestamp"],
                "agent_id": entry["agent_id"],
                "summary": entry["summary"],
                "operation": entry["operation"],
            }
            for entry in entries
        ]

    def get_version(
        self, slot_id: str, version: int, current_content: dict
    ) -> dict | None:
        """Reconstruct a specific past version by forward-replaying diffs.

        Finds the creation entry (which contains the full initial object),
        then applies diffs forward through each subsequent version up to
        the target version.

        If journal entries are missing (truncated), returns None with a
        warning rather than failing (per Pitfall 1).

        Args:
            slot_id: The slot identifier.
            version: The target version number to reconstruct.
            current_content: The current slot content on disk.

        Returns:
            The reconstructed slot content dict at the target version,
            or None if reconstruction is not possible.
        """
        entries = self._journal.query_by_slot(slot_id)

        if not entries:
            logger.warning(
                "No journal entries for slot '%s'; history unavailable.",
                slot_id,
            )
            return None

        # Find the latest version from journal
        latest_version = max(e["version_after"] for e in entries)

        if version == latest_version:
            return current_content

        if version > latest_version or version < 1:
            logger.warning(
                "Requested version %d for slot '%s' but latest is %d.",
                version, slot_id, latest_version,
            )
            return None

        # Sort entries by version_after ascending for forward replay
        sorted_entries = sorted(
            entries, key=lambda e: e["version_after"]
        )

        # Find the creation entry (version_after == 1)
        create_entry = None
        for entry in sorted_entries:
            if entry["operation"] == "create" and entry["version_after"] == 1:
                create_entry = entry
                break

        if create_entry is None:
            logger.warning(
                "No creation entry found for slot '%s'; "
                "history unavailable before earliest journal entry.",
                slot_id,
            )
            return None

        # Start with the initial content from the create diff
        # The create diff is [{"op": "add", "path": "", "value": <full object>}]
        create_diff = create_entry.get("diff", [])
        if not create_diff or create_diff[0].get("op") != "add":
            logger.warning(
                "Malformed creation entry for slot '%s'.", slot_id
            )
            return None

        content = apply_patch({}, create_diff)

        if version == 1:
            return content

        # Apply diffs forward from v2 to target version
        for entry in sorted_entries:
            v = entry["version_after"]
            if v <= 1 or v > version:
                continue
            diff = entry.get("diff", [])
            try:
                content = apply_patch(content, diff)
            except Exception:
                logger.warning(
                    "Failed to apply diff for slot '%s' "
                    "version %d; history unavailable.",
                    slot_id, v,
                )
                return None

        return content

    def get_current_version(self, slot_id: str) -> int | None:
        """Return the latest version number from journal entries.

        Args:
            slot_id: The slot identifier.

        Returns:
            The latest version number, or None if no entries exist.
        """
        entries = self._journal.query_by_slot(slot_id)
        if not entries:
            return None
        return max(e["version_after"] for e in entries)
