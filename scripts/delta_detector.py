"""Delta detection for upstream registry re-ingestion.

Compares upstream registry entries against a persisted manifest of
content hashes to classify entries as added, modified, removed,
unchanged, or conflicting. Supports status transition detection
(Pitfall 5: detect status changes BEFORE filtering).

References:
    INGS-03 (delta detection), REQ-237 (performance)
"""

import json
import logging
import os
from dataclasses import dataclass, field

from scripts.shared_io import atomic_write
from scripts.upstream_schemas import content_hash, generate_slot_id, generate_trace_id

logger = logging.getLogger(__name__)


@dataclass
class DeltaReport:
    """Result of delta detection between upstream and manifest.

    Attributes:
        added: Entries present upstream but not in manifest.
        modified: Entries whose content hash changed.
        removed: Slot IDs in manifest but no longer upstream.
        unchanged: Slot IDs with identical content hashes.
        conflicts: Modified entries where local edits exist (version > 1).
        status_changes: Entries whose status field changed.
    """

    added: list[dict] = field(default_factory=list)
    modified: list[dict] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    status_changes: list[dict] = field(default_factory=list)


def load_manifest(manifest_path: str) -> dict:
    """Load ingestion manifest from disk.

    If the manifest file does not exist, returns an empty manifest
    structure (first-time ingestion scenario).

    Args:
        manifest_path: Path to .system-dev/ingestion-manifest.json.

    Returns:
        Manifest dict with schema_version, ingested_at, upstream_path,
        upstream_state, and hashes.
    """
    if not os.path.exists(manifest_path):
        return {
            "schema_version": "1.0.0",
            "ingested_at": None,
            "upstream_path": None,
            "upstream_state": {"gates_status": None, "counts": {}},
            "hashes": {},
        }

    with open(manifest_path) as f:
        return json.load(f)


def save_manifest(manifest_path: str, manifest: dict) -> None:
    """Save ingestion manifest atomically.

    Args:
        manifest_path: Path to .system-dev/ingestion-manifest.json.
        manifest: The manifest dict to persist.
    """
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    atomic_write(manifest_path, manifest)


def compute_deltas(
    upstream_entries: list[dict],
    manifest_hashes: dict[str, str],
    id_field: str,
    slot_type: str,
    slot_api: object | None = None,
    generate_id_fn: object | None = None,
) -> DeltaReport:
    """Compute deltas between upstream entries and the manifest.

    Runs delta detection on the FULL upstream set BEFORE any status
    filtering (Pitfall 5). For each modified entry, checks if local
    edits exist (slot version > 1) and classifies as conflict instead.

    Args:
        upstream_entries: List of upstream registry entry dicts.
        manifest_hashes: Dict mapping slot_id -> content_hash from manifest.
        id_field: The field name containing the entry ID (e.g., "id").
        slot_type: The slot type for ID generation (e.g., "need").
        slot_api: Optional SlotAPI for conflict detection (read slot version).
        generate_id_fn: Optional custom ID generator. If None, uses
            generate_slot_id for standard types or a trace-specific
            generator for traceability links.

    Returns:
        DeltaReport with classified entries.
    """
    report = DeltaReport()
    seen_slot_ids: set[str] = set()

    for entry in upstream_entries:
        # Generate slot ID
        if generate_id_fn is not None:
            slot_id = generate_id_fn(entry)
        elif id_field == "__trace__":
            # Traceability links use from->to as ID
            slot_id = generate_trace_id(entry.get("from", ""), entry.get("to", ""))
        else:
            upstream_id = entry.get(id_field)
            if upstream_id is None:
                logger.warning(
                    "Entry missing id_field '%s', skipping: %s", id_field, entry
                )
                continue
            slot_id = generate_slot_id(slot_type, upstream_id)

        seen_slot_ids.add(slot_id)
        new_hash = content_hash(entry)
        old_hash = manifest_hashes.get(slot_id)

        if old_hash is None:
            # New entry
            report.added.append({"slot_id": slot_id, "entry": entry})
        elif old_hash == new_hash:
            # Unchanged
            report.unchanged.append(slot_id)
        else:
            # Hash changed -- check for local edits (conflict detection)
            is_conflict = False
            if slot_api is not None:
                existing = slot_api.read(slot_id)
                if existing is not None and existing.get("version", 1) > 1:
                    is_conflict = True

            if is_conflict:
                report.conflicts.append(
                    {
                        "slot_id": slot_id,
                        "reason": "Local edits exist (version > 1) and upstream changed",
                    }
                )
            else:
                report.modified.append(
                    {
                        "slot_id": slot_id,
                        "entry": entry,
                        "old_hash": old_hash,
                        "new_hash": new_hash,
                    }
                )

        # Pitfall 5: Detect status changes
        old_status = entry.get("_prev_status")  # populated by caller if re-ingesting
        new_status = entry.get("status")
        if old_status is not None and new_status is not None and old_status != new_status:
            report.status_changes.append(
                {
                    "slot_id": slot_id,
                    "old_status": old_status,
                    "new_status": new_status,
                }
            )

    # Detect removals: in manifest but not in upstream
    for slot_id in manifest_hashes:
        if slot_id not in seen_slot_ids:
            report.removed.append(slot_id)

    return report
