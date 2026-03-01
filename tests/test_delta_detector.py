"""Tests for delta detection: classification, conflicts, manifest, performance."""

import json
import os
import time

import pytest

from scripts.delta_detector import DeltaReport, compute_deltas, load_manifest, save_manifest
from scripts.upstream_schemas import content_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_manifest(hashes: dict) -> dict:
    """Create a valid manifest dict with given hashes."""
    return {
        "schema_version": "1.0.0",
        "ingested_at": "2026-01-01T00:00:00Z",
        "upstream_path": "/fake/upstream",
        "upstream_state": {"gates_status": "checked", "counts": {}},
        "hashes": hashes,
    }


def make_entry(entry_id: str, statement: str = "test", **extra) -> dict:
    """Create a minimal upstream entry."""
    entry = {"id": entry_id, "statement": statement}
    entry.update(extra)
    return entry


class FakeSlotAPI:
    """Minimal SlotAPI mock for conflict detection tests."""

    def __init__(self, slots: dict | None = None):
        self._slots = slots or {}

    def read(self, slot_id: str) -> dict | None:
        return self._slots.get(slot_id)


# ---------------------------------------------------------------------------
# Tests: Delta classification
# ---------------------------------------------------------------------------


class TestDeltaClassification:
    """Tests for compute_deltas entry classification."""

    def test_delta_classification_all_added(self):
        """Empty manifest means all entries are classified as added."""
        entries = [make_entry("NEED-001"), make_entry("NEED-002")]
        report = compute_deltas(entries, {}, "id", "need")

        assert len(report.added) == 2
        assert len(report.modified) == 0
        assert len(report.removed) == 0
        assert len(report.unchanged) == 0

    def test_delta_classification_unchanged(self):
        """Same hashes means all entries are classified as unchanged."""
        entries = [make_entry("NEED-001"), make_entry("NEED-002")]
        hashes = {
            "need:NEED-001": content_hash(entries[0]),
            "need:NEED-002": content_hash(entries[1]),
        }
        report = compute_deltas(entries, hashes, "id", "need")

        assert len(report.added) == 0
        assert len(report.modified) == 0
        assert len(report.removed) == 0
        assert len(report.unchanged) == 2

    def test_delta_classification_modified(self):
        """Changed hash classifies entry as modified."""
        entry = make_entry("NEED-001", statement="original")
        hashes = {"need:NEED-001": "old_hash_that_wont_match"}

        report = compute_deltas([entry], hashes, "id", "need")

        assert len(report.modified) == 1
        assert report.modified[0]["slot_id"] == "need:NEED-001"
        assert report.modified[0]["old_hash"] == "old_hash_that_wont_match"
        assert report.modified[0]["new_hash"] == content_hash(entry)

    def test_delta_classification_removed(self):
        """Entry in manifest but not upstream is classified as removed."""
        entries = [make_entry("NEED-001")]
        hashes = {
            "need:NEED-001": content_hash(entries[0]),
            "need:NEED-002": "some_hash",
        }
        report = compute_deltas(entries, hashes, "id", "need")

        assert len(report.removed) == 1
        assert "need:NEED-002" in report.removed

    def test_delta_classification_mixed(self):
        """Combination of added, modified, removed, unchanged."""
        entry_unchanged = make_entry("NEED-001", statement="unchanged")
        entry_modified = make_entry("NEED-002", statement="new statement")
        entry_added = make_entry("NEED-003", statement="brand new")

        hashes = {
            "need:NEED-001": content_hash(entry_unchanged),
            "need:NEED-002": "old_hash",
            "need:NEED-004": "removed_hash",
        }

        entries = [entry_unchanged, entry_modified, entry_added]
        report = compute_deltas(entries, hashes, "id", "need")

        assert len(report.added) == 1
        assert report.added[0]["slot_id"] == "need:NEED-003"
        assert len(report.modified) == 1
        assert report.modified[0]["slot_id"] == "need:NEED-002"
        assert len(report.removed) == 1
        assert "need:NEED-004" in report.removed
        assert len(report.unchanged) == 1
        assert "need:NEED-001" in report.unchanged

    def test_conflict_detection(self):
        """Modified entry with slot version > 1 becomes conflict."""
        entry = make_entry("NEED-001", statement="changed upstream")
        hashes = {"need:NEED-001": "old_hash"}

        # Fake slot with version > 1 (locally edited)
        fake_api = FakeSlotAPI(
            {"need:NEED-001": {"version": 3, "slot_id": "need:NEED-001"}}
        )

        report = compute_deltas([entry], hashes, "id", "need", slot_api=fake_api)

        assert len(report.conflicts) == 1
        assert report.conflicts[0]["slot_id"] == "need:NEED-001"
        assert "version > 1" in report.conflicts[0]["reason"]
        assert len(report.modified) == 0

    def test_status_transition_detection(self):
        """Entry with _prev_status detects status change."""
        entry = make_entry("REQ-001", status="withdrawn", _prev_status="baselined")
        hashes = {"requirement:REQ-001": "old_hash"}

        report = compute_deltas([entry], hashes, "id", "requirement")

        assert len(report.status_changes) == 1
        assert report.status_changes[0]["old_status"] == "baselined"
        assert report.status_changes[0]["new_status"] == "withdrawn"


# ---------------------------------------------------------------------------
# Tests: Manifest I/O
# ---------------------------------------------------------------------------


class TestManifest:
    """Tests for manifest load/save operations."""

    def test_load_manifest_missing_file(self, tmp_path):
        """Missing manifest file returns empty manifest, not crash."""
        manifest = load_manifest(str(tmp_path / "nonexistent.json"))

        assert manifest["schema_version"] == "1.0.0"
        assert manifest["ingested_at"] is None
        assert manifest["hashes"] == {}

    def test_save_and_load_manifest_roundtrip(self, tmp_path):
        """Save then load preserves all data."""
        original = make_manifest({"need:NEED-001": "abc123", "need:NEED-002": "def456"})
        path = str(tmp_path / "manifest.json")

        save_manifest(path, original)
        loaded = load_manifest(path)

        assert loaded["schema_version"] == original["schema_version"]
        assert loaded["hashes"] == original["hashes"]
        assert loaded["ingested_at"] == original["ingested_at"]


# ---------------------------------------------------------------------------
# Tests: Performance
# ---------------------------------------------------------------------------


class TestDeltaPerformance:
    """Performance tests for delta detection."""

    def test_delta_performance_500_entries(self):
        """500 entries delta computed in < 2 seconds (REQ-237)."""
        entries = [make_entry(f"NEED-{i:04d}", statement=f"Need {i}") for i in range(500)]
        # Half unchanged, half modified
        hashes = {}
        for i, entry in enumerate(entries):
            if i < 250:
                hashes[f"need:NEED-{i:04d}"] = content_hash(entry)
            else:
                hashes[f"need:NEED-{i:04d}"] = "stale_hash"

        start = time.monotonic()
        report = compute_deltas(entries, hashes, "id", "need")
        elapsed = time.monotonic() - start

        assert elapsed < 2.0, f"Delta computation took {elapsed:.2f}s, expected < 2s"
        assert len(report.unchanged) == 250
        assert len(report.modified) == 250
