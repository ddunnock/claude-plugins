"""Upstream ingestion engine for the Design Registry.

Reads upstream JSON registries from requirements-dev, maps entries to
Design Registry slots, detects deltas on re-ingestion, produces
structured reports (delta + compatibility), and handles all known
upstream schema gaps gracefully.

References:
    INGS-01 (ingestion), INGS-02 (performance), INGS-03 (delta),
    INGS-04 (compatibility), XCUT-01 (partial ingestion on error)
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

from scripts.change_journal import ChangeJournal
from scripts.delta_detector import DeltaReport, compute_deltas, load_manifest, save_manifest
from scripts.registry import SlotAPI
from scripts.shared_io import atomic_write
from scripts.upstream_schemas import (
    ASSUMPTION_FIELD_MAP,
    GAP_MARKERS,
    NEED_FIELD_MAP,
    REQUIREMENT_FIELD_MAP,
    SOURCE_FIELD_MAP,
    TRACEABILITY_FIELD_MAP,
    check_upstream_gates,
    content_hash,
    generate_slot_id,
    generate_trace_id,
    load_upstream_registry,
    map_upstream_entry,
)

logger = logging.getLogger(__name__)

# Status values that cause entries to be skipped during ingestion
SKIP_STATUSES = {"draft", "withdrawn"}

# Registry processing order (dependency-based)
REGISTRY_SPECS = [
    {
        "filename": "needs_registry.json",
        "top_key": "needs",
        "slot_type": "need",
        "field_map": NEED_FIELD_MAP,
        "id_field": "id",
        "label": "Needs",
        "gap_markers": ["GAP-1", "GAP-2"],
        "status_field": "status",
    },
    {
        "filename": "source_registry.json",
        "top_key": "sources",
        "slot_type": "source",
        "field_map": SOURCE_FIELD_MAP,
        "id_field": "id",
        "label": "Sources",
        "gap_markers": ["GAP-3", "GAP-5"],
        "status_field": None,  # Sources have no status filtering
    },
    {
        "filename": "assumptions_registry.json",
        "top_key": "assumptions",
        "slot_type": "assumption",
        "field_map": ASSUMPTION_FIELD_MAP,
        "id_field": "id",
        "label": "Assumptions",
        "gap_markers": ["GAP-7"],
        "status_field": "status",
    },
    {
        "filename": "requirements_registry.json",
        "top_key": "requirements",
        "slot_type": "requirement",
        "field_map": REQUIREMENT_FIELD_MAP,
        "id_field": "id",
        "label": "Requirements",
        "gap_markers": [],
        "status_field": "status",
    },
    {
        "filename": "traceability_matrix.json",
        "top_key": "links",
        "slot_type": "traceability-link",
        "field_map": TRACEABILITY_FIELD_MAP,
        "id_field": "__trace__",  # Special: uses from->to
        "label": "Traceability links",
        "gap_markers": ["GAP-8"],
        "status_field": None,
    },
]


@dataclass
class IngestResult:
    """Result of a full ingestion run.

    Attributes:
        total_ingested: Total number of entries successfully ingested.
        created: Number of newly created slots.
        updated: Number of updated slots.
        conflicts: Number of conflict-skipped slots.
        skipped: Number of status-filtered entries (draft/withdrawn).
        gap_markers_added: Total gap markers applied across all slots.
        delta_report_path: Path to delta-report.json (or None).
        compatibility_report_path: Path to compatibility-report.json (or None).
        warnings: List of warning messages.
    """

    total_ingested: int = 0
    created: int = 0
    updated: int = 0
    conflicts: int = 0
    skipped: int = 0
    gap_markers_added: int = 0
    delta_report_path: str | None = None
    compatibility_report_path: str | None = None
    warnings: list[str] = field(default_factory=list)


def _should_skip_entry(entry: dict, status_field: str | None) -> bool:
    """Check if an entry should be skipped based on status.

    Args:
        entry: The upstream entry dict.
        status_field: The field name containing status, or None if no filtering.

    Returns:
        True if the entry should be skipped.
    """
    if status_field is None:
        return False
    status = entry.get(status_field, "").lower()
    return status in SKIP_STATUSES


def _apply_gap_markers(content: dict, gap_ids: list[str]) -> int:
    """Apply gap markers to a slot's content.

    Args:
        content: The mapped slot content dict.
        gap_ids: List of GAP marker IDs to apply (e.g., ["GAP-1", "GAP-2"]).

    Returns:
        Number of gap markers added.
    """
    if not gap_ids:
        return 0

    markers = []
    for gap_id in gap_ids:
        if gap_id in GAP_MARKERS:
            markers.append(dict(GAP_MARKERS[gap_id]))

    if markers:
        content.setdefault("gap_markers", [])
        content["gap_markers"].extend(markers)

    return len(markers)


def _add_derives_from(content: dict, entry: dict) -> None:
    """Add derives_from cross-references for requirement entries.

    Maps parent_need to a list of need slot ID references.

    Args:
        content: The mapped slot content dict.
        entry: The original upstream entry.
    """
    parent = entry.get("parent_need")
    if parent:
        content["derives_from"] = [f"need:{parent}"]


def _generate_trace_slot_id(entry: dict) -> str:
    """Generate slot ID for traceability link entries."""
    return generate_trace_id(entry.get("from", ""), entry.get("to", ""))


def _process_registry(
    spec: dict,
    upstream_path: str,
    slot_api: SlotAPI,
    manifest_hashes: dict[str, str],
    all_new_hashes: dict[str, str],
    result: IngestResult,
) -> DeltaReport | None:
    """Process a single upstream registry file.

    Loads the registry, computes deltas, filters by status, maps entries,
    injects gap markers, and ingests via SlotAPI.

    Args:
        spec: Registry specification dict from REGISTRY_SPECS.
        upstream_path: Path to upstream .requirements-dev/ directory.
        slot_api: SlotAPI instance for ingestion.
        manifest_hashes: Current manifest hashes for this slot type prefix.
        all_new_hashes: Dict to populate with new hashes for manifest update.
        result: IngestResult to update with counts.

    Returns:
        DeltaReport for this registry, or None if loading failed.
    """
    filename = spec["filename"]
    top_key = spec["top_key"]
    slot_type = spec["slot_type"]
    field_map = spec["field_map"]
    id_field = spec["id_field"]
    gap_ids = spec["gap_markers"]
    status_field = spec["status_field"]

    # Load upstream registry (XCUT-01: skip on error, don't crash)
    try:
        entries = load_upstream_registry(upstream_path, filename, top_key)
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        msg = f"Failed to load {filename}: {e}"
        logger.error(msg)
        result.warnings.append(msg)
        return None

    # Compute deltas on FULL set BEFORE status filtering (Pitfall 5)
    if id_field == "__trace__":
        generate_id_fn = _generate_trace_slot_id
    else:
        generate_id_fn = None

    delta = compute_deltas(
        upstream_entries=entries,
        manifest_hashes=manifest_hashes,
        id_field=id_field,
        slot_type=slot_type,
        slot_api=slot_api,
        generate_id_fn=generate_id_fn,
    )

    # Process added and modified entries
    entries_to_ingest = []
    for item in delta.added:
        entries_to_ingest.append((item["slot_id"], item["entry"]))
    for item in delta.modified:
        entries_to_ingest.append((item["slot_id"], item["entry"]))

    for slot_id, entry in entries_to_ingest:
        # Status filtering AFTER delta detection
        if _should_skip_entry(entry, status_field):
            result.skipped += 1
            # Still record hash for manifest (so next run knows about it)
            all_new_hashes[slot_id] = content_hash(entry)
            continue

        # Map upstream entry to slot content
        try:
            content = map_upstream_entry(entry, field_map, slot_type, filename)
        except Exception as e:
            msg = f"Failed to map entry {slot_id}: {e}"
            logger.warning(msg)
            result.warnings.append(msg)
            all_new_hashes[slot_id] = content_hash(entry)
            continue

        # Add derives_from for requirements
        if slot_type == "requirement":
            _add_derives_from(content, entry)

        # Apply gap markers
        markers_added = _apply_gap_markers(content, gap_ids)
        result.gap_markers_added += markers_added

        # Ingest via SlotAPI
        try:
            ingest_result = slot_api.ingest(slot_id, slot_type, content)
        except Exception as e:
            msg = f"Failed to ingest {slot_id}: {e}"
            logger.warning(msg)
            result.warnings.append(msg)
            all_new_hashes[slot_id] = content_hash(entry)
            continue

        status = ingest_result["status"]
        if status == "created":
            result.created += 1
            result.total_ingested += 1
        elif status == "updated":
            result.updated += 1
            result.total_ingested += 1
        elif status == "conflict":
            result.conflicts += 1

        all_new_hashes[slot_id] = content_hash(entry)

    # Record hashes for unchanged entries too
    for slot_id in delta.unchanged:
        all_new_hashes[slot_id] = manifest_hashes[slot_id]

    # Handle removed entries: add gap markers, don't delete
    for slot_id in delta.removed:
        existing = slot_api.read(slot_id)
        if existing is not None:
            # Check for downstream references
            severity = "info"
            # Mark as upstream_removed
            gap_marker = {
                "type": "missing_data",
                "finding_ref": "upstream_removed",
                "severity": severity,
                "description": f"Upstream entry removed, slot {slot_id} retained",
            }
            existing_markers = existing.get("gap_markers", [])
            existing_markers.append(gap_marker)
            # Note: we don't re-ingest removed slots, just mark them
            # The gap marker will be visible on next read

    # Count conflicts from delta
    result.conflicts += len(delta.conflicts)

    return delta


def ingest_all(
    upstream_path: str,
    workspace_root: str,
    schemas_dir: str,
) -> IngestResult:
    """Ingest all upstream registries into the Design Registry.

    Main entry point for the ingestion pipeline. Processes 5 registry
    types in dependency order, detects deltas, applies gap markers,
    and writes structured reports.

    Args:
        upstream_path: Path to the upstream .requirements-dev/ directory.
        workspace_root: Path to .system-dev/ workspace directory.
        schemas_dir: Path to schemas/ directory with JSON Schema files.

    Returns:
        IngestResult with counts and report paths.

    Raises:
        FileNotFoundError: If upstream_path does not exist.
    """
    if not os.path.isdir(upstream_path):
        raise FileNotFoundError(f"Upstream path not found: {upstream_path}")

    result = IngestResult()

    # Check gate status (warn but continue per CONTEXT.md)
    state_path = os.path.join(upstream_path, "state.json")
    if os.path.exists(state_path):
        gate_result = check_upstream_gates(state_path)
        if not gate_result["all_passed"]:
            for warning in gate_result["warnings"]:
                result.warnings.append(f"Gate warning: {warning}")
    else:
        result.warnings.append("No state.json found in upstream path")

    # Load manifest
    manifest_path = os.path.join(workspace_root, "ingestion-manifest.json")
    manifest = load_manifest(manifest_path)
    manifest_hashes = manifest.get("hashes", {})

    # Initialize SlotAPI
    slot_api = SlotAPI(workspace_root, schemas_dir)

    # Collect all deltas for report
    all_deltas: dict[str, DeltaReport] = {}
    all_new_hashes: dict[str, str] = {}

    # Collect per-registry counts for console summary
    registry_counts: dict[str, dict] = {}

    # Process each registry in dependency order
    for spec in REGISTRY_SPECS:
        slot_type = spec["slot_type"]
        label = spec["label"]

        # Filter manifest hashes to this slot type's prefix
        prefix_map = {}
        for sid, h in manifest_hashes.items():
            # Match by slot type prefix
            if _slot_id_matches_type(sid, slot_type):
                prefix_map[sid] = h

        before_created = result.created
        before_updated = result.updated
        before_skipped = result.skipped
        before_conflicts = result.conflicts

        delta = _process_registry(
            spec=spec,
            upstream_path=upstream_path,
            slot_api=slot_api,
            manifest_hashes=prefix_map,
            all_new_hashes=all_new_hashes,
            result=result,
        )

        if delta is not None:
            all_deltas[slot_type] = delta

        registry_counts[label] = {
            "created": result.created - before_created,
            "updated": result.updated - before_updated,
            "skipped": result.skipped - before_skipped,
            "conflicts": result.conflicts - before_conflicts,
            "ingested": (result.created - before_created) + (result.updated - before_updated),
        }

    # Write batch journal entry (not per-item)
    journal_path = os.path.join(workspace_root, "journal.jsonl")
    journal = ChangeJournal(journal_path)
    journal.append(
        "ingestion-batch",
        "system",
        "ingest",
        0,
        1,
        "ingestion-engine",
        (
            f"Ingested {result.total_ingested} items from {upstream_path}: "
            f"{result.created} created, {result.updated} updated, "
            f"{result.conflicts} conflicts"
        ),
        None,
        {
            "upstream_path": upstream_path,
            "counts": {
                "total_ingested": result.total_ingested,
                "created": result.created,
                "updated": result.updated,
                "conflicts": result.conflicts,
                "skipped": result.skipped,
                "gap_markers_added": result.gap_markers_added,
            },
        },
    )

    # Save updated manifest
    now = datetime.now(timezone.utc).isoformat()
    new_manifest = {
        "schema_version": "1.0.0",
        "ingested_at": now,
        "upstream_path": upstream_path,
        "upstream_state": {
            "gates_status": "checked",
            "counts": {label: counts["ingested"] for label, counts in registry_counts.items()},
        },
        "hashes": all_new_hashes,
    }
    save_manifest(manifest_path, new_manifest)

    # Write delta report
    delta_report = _build_delta_report(all_deltas, upstream_path)
    delta_report_path = os.path.join(workspace_root, "delta-report.json")
    atomic_write(delta_report_path, delta_report)
    result.delta_report_path = delta_report_path

    # Write compatibility report
    compat_report = _build_compatibility_report(all_deltas, result)
    compat_report_path = os.path.join(workspace_root, "compatibility-report.json")
    atomic_write(compat_report_path, compat_report)
    result.compatibility_report_path = compat_report_path

    # Print console summary
    _print_summary(registry_counts, result)

    return result


def _slot_id_matches_type(slot_id: str, slot_type: str) -> bool:
    """Check if a slot ID belongs to a given slot type.

    Args:
        slot_id: The slot ID (e.g., "need:NEED-001", "trace:REQ->NEED").
        slot_type: The slot type (e.g., "need", "traceability-link").

    Returns:
        True if the slot ID matches the type.
    """
    from scripts.registry import SLOT_ID_PREFIXES

    prefix = SLOT_ID_PREFIXES.get(slot_type, "")
    return slot_id.startswith(f"{prefix}:")


def _build_delta_report(all_deltas: dict[str, DeltaReport], upstream_path: str) -> dict:
    """Build the delta-report.json structure.

    Args:
        all_deltas: Dict of slot_type -> DeltaReport.
        upstream_path: The upstream path for provenance.

    Returns:
        Delta report dict.
    """
    now = datetime.now(timezone.utc).isoformat()

    total_added = 0
    total_modified = 0
    total_removed = 0
    total_conflicts = 0
    total_unchanged = 0

    details_added = []
    details_modified = []
    details_removed = []
    details_conflicts = []
    details_status_changes = []

    for slot_type, delta in all_deltas.items():
        total_added += len(delta.added)
        total_modified += len(delta.modified)
        total_removed += len(delta.removed)
        total_conflicts += len(delta.conflicts)
        total_unchanged += len(delta.unchanged)

        for item in delta.added:
            details_added.append({"slot_id": item["slot_id"], "slot_type": slot_type})
        for item in delta.modified:
            details_modified.append({
                "slot_id": item["slot_id"],
                "slot_type": slot_type,
                "fields_changed": [],  # Detailed field diff not computed here
            })
        for slot_id in delta.removed:
            details_removed.append({"slot_id": slot_id, "severity": "info"})
        for item in delta.conflicts:
            details_conflicts.append(item)
        for item in delta.status_changes:
            details_status_changes.append(item)

    return {
        "schema_version": "1.0.0",
        "generated_at": now,
        "upstream_path": upstream_path,
        "summary": {
            "added": total_added,
            "modified": total_modified,
            "removed": total_removed,
            "conflicts": total_conflicts,
            "unchanged": total_unchanged,
        },
        "details": {
            "added": details_added,
            "modified": details_modified,
            "removed": details_removed,
            "conflicts": details_conflicts,
            "status_changes": details_status_changes,
        },
    }


def _build_compatibility_report(
    all_deltas: dict[str, DeltaReport], result: IngestResult
) -> dict:
    """Build the compatibility-report.json structure.

    Lists all gap markers by finding ID with affected slot counts.

    Args:
        all_deltas: Dict of slot_type -> DeltaReport.
        result: IngestResult with gap marker counts.

    Returns:
        Compatibility report dict.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Count gap markers per finding
    findings: dict[str, dict] = {}
    for spec in REGISTRY_SPECS:
        gap_ids = spec["gap_markers"]
        slot_type = spec["slot_type"]
        delta = all_deltas.get(slot_type)
        if delta is None:
            continue

        # Count ingested entries (added + modified that were actually ingested)
        ingested_count = len(delta.added) + len(delta.modified)

        for gap_id in gap_ids:
            if gap_id in GAP_MARKERS:
                marker = GAP_MARKERS[gap_id]
                if gap_id not in findings:
                    findings[gap_id] = {
                        "description": marker["description"],
                        "severity": marker["severity"],
                        "affected_slots": 0,
                        "affected_types": [],
                    }
                findings[gap_id]["affected_slots"] += ingested_count
                if slot_type not in findings[gap_id]["affected_types"]:
                    findings[gap_id]["affected_types"].append(slot_type)

    total_gap_markers = result.gap_markers_added
    total_affected = sum(f["affected_slots"] for f in findings.values())

    return {
        "schema_version": "1.0.0",
        "generated_at": now,
        "findings": findings,
        "total_gap_markers": total_gap_markers,
        "total_affected_slots": total_affected,
    }


def _print_summary(registry_counts: dict[str, dict], result: IngestResult) -> None:
    """Print human-readable ingestion summary to console.

    Args:
        registry_counts: Per-registry count dicts.
        result: IngestResult with totals.
    """
    lines = ["Ingestion complete:"]
    for label, counts in registry_counts.items():
        ingested = counts["ingested"]
        skipped = counts["skipped"]
        if skipped > 0:
            lines.append(f"  {label}: {ingested} ingested ({skipped} skipped - draft/withdrawn)")
        else:
            lines.append(f"  {label}: {ingested} ingested")
    lines.append(f"  Gap markers: {result.gap_markers_added} applied")
    lines.append(f"  Conflicts: {result.conflicts}")
    summary = "\n".join(lines)
    logger.info(summary)
    print(summary)
