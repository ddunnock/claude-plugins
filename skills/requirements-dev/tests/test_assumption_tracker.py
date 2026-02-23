"""Tests for assumption_tracker.py -- assumption lifecycle management."""
import json

import pytest

from assumption_tracker import (
    add_assumption,
    challenge_assumption,
    import_from_ingestion,
    invalidate_assumption,
    list_assumptions,
    reaffirm_assumption,
    summary,
)


@pytest.fixture
def workspace(tmp_path):
    """Create a minimal workspace directory."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    return str(ws)


def _seed_ingestion(ws, assumption_refs):
    """Helper: write ingestion.json with given assumption_refs."""
    data = {"assumption_refs": assumption_refs, "source_refs": []}
    with open(f"{ws}/ingestion.json", "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Import from ingestion
# ---------------------------------------------------------------------------

class TestImportFromIngestion:
    def test_import_creates_local_copies(self, workspace):
        """Imported assumptions get new ASN-xxx IDs and origin='concept-dev'."""
        _seed_ingestion(workspace, [
            {"id": "A-001", "description": "Assumption one", "category": "feasibility", "impact_level": "high"},
            {"id": "A-002", "description": "Assumption two"},
        ])
        result = import_from_ingestion(workspace)
        assert result["imported_count"] == 2
        assert result["skipped_count"] == 0

        assumptions = list_assumptions(workspace)
        assert len(assumptions) == 2
        assert assumptions[0]["id"] == "ASN-001"
        assert assumptions[0]["origin"] == "concept-dev"
        assert assumptions[0]["original_id"] == "A-001"
        assert assumptions[0]["status"] == "active"

    def test_import_skips_duplicates(self, workspace):
        """Re-importing same assumptions does not create duplicates."""
        _seed_ingestion(workspace, [{"id": "A-001", "description": "Test"}])
        import_from_ingestion(workspace)
        result = import_from_ingestion(workspace)
        assert result["imported_count"] == 0
        assert result["skipped_count"] == 1
        assert len(list_assumptions(workspace)) == 1

    def test_import_no_ingestion_file(self, workspace):
        """Gracefully handles missing ingestion.json."""
        result = import_from_ingestion(workspace)
        assert result["imported_count"] == 0
        assert "warning" in result or result["skipped_count"] == 0

    def test_import_maps_fields(self, workspace):
        """Fields are correctly mapped from concept-dev schema."""
        _seed_ingestion(workspace, [
            {"id": "A-001", "description": "Test assumption", "category": "technology",
             "impact_level": "critical", "basis": "Engineering judgment"},
        ])
        import_from_ingestion(workspace)
        a = list_assumptions(workspace)[0]
        assert a["statement"] == "Test assumption"
        assert a["category"] == "technology"
        assert a["impact"] == "critical"
        assert a["basis"] == "Engineering judgment"

    def test_import_invalid_category_defaults(self, workspace):
        """Invalid category from concept-dev defaults to 'other'."""
        _seed_ingestion(workspace, [
            {"id": "A-001", "description": "Test", "category": "nonexistent_cat"},
        ])
        import_from_ingestion(workspace)
        a = list_assumptions(workspace)[0]
        assert a["category"] == "other"

    def test_import_invalid_impact_defaults(self, workspace):
        """Invalid impact from concept-dev defaults to 'medium'."""
        _seed_ingestion(workspace, [
            {"id": "A-001", "description": "Test", "impact_level": "extreme"},
        ])
        import_from_ingestion(workspace)
        a = list_assumptions(workspace)[0]
        assert a["impact"] == "medium"


# ---------------------------------------------------------------------------
# Add new assumption
# ---------------------------------------------------------------------------

class TestAddAssumption:
    def test_add_new(self, workspace):
        """Adding a new assumption returns an ID and persists."""
        asn_id = add_assumption(
            workspace, "System will have <100ms latency",
            "feasibility", "high", "Based on prototype benchmarks",
        )
        assert asn_id == "ASN-001"
        assumptions = list_assumptions(workspace)
        assert len(assumptions) == 1
        assert assumptions[0]["origin"] == "requirements-dev"
        assert assumptions[0]["original_id"] is None

    def test_add_invalid_category(self, workspace):
        """Invalid category raises ValueError."""
        with pytest.raises(ValueError, match="Invalid category"):
            add_assumption(workspace, "Test", "bogus", "high", "basis")

    def test_add_invalid_impact(self, workspace):
        """Invalid impact raises ValueError."""
        with pytest.raises(ValueError, match="Invalid impact"):
            add_assumption(workspace, "Test", "feasibility", "extreme", "basis")

    def test_sequential_ids(self, workspace):
        """IDs increment correctly."""
        id1 = add_assumption(workspace, "First", "scope", "low", "basis")
        id2 = add_assumption(workspace, "Second", "scope", "low", "basis")
        assert id1 == "ASN-001"
        assert id2 == "ASN-002"


# ---------------------------------------------------------------------------
# Challenge / Invalidate / Reaffirm
# ---------------------------------------------------------------------------

class TestLifecycleTransitions:
    def test_challenge(self, workspace):
        """Challenge sets status and records reason + evidence."""
        add_assumption(workspace, "Test", "scope", "high", "basis")
        challenge_assumption(workspace, "ASN-001", "New data contradicts", "benchmark results")
        a = list_assumptions(workspace)[0]
        assert a["status"] == "challenged"
        assert a["challenge_reason"] == "New data contradicts"
        assert a["challenge_evidence"] == "benchmark results"

    def test_invalidate(self, workspace):
        """Invalidate sets status and records reason."""
        add_assumption(workspace, "Test", "scope", "high", "basis")
        invalidate_assumption(workspace, "ASN-001", "Proven false by testing")
        a = list_assumptions(workspace)[0]
        assert a["status"] == "invalidated"
        assert a["challenge_reason"] == "Proven false by testing"

    def test_reaffirm(self, workspace):
        """Reaffirm sets status after challenge."""
        add_assumption(workspace, "Test", "scope", "high", "basis")
        challenge_assumption(workspace, "ASN-001", "Questioned during review")
        reaffirm_assumption(workspace, "ASN-001", "Confirmed by SME")
        a = list_assumptions(workspace)[0]
        assert a["status"] == "reaffirmed"
        assert a["challenge_reason"] == "Confirmed by SME"

    def test_challenge_nonexistent(self, workspace):
        """Challenging nonexistent assumption raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            challenge_assumption(workspace, "ASN-999", "reason")

    def test_invalidate_nonexistent(self, workspace):
        """Invalidating nonexistent assumption raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            invalidate_assumption(workspace, "ASN-999", "reason")

    def test_reaffirm_nonexistent(self, workspace):
        """Reaffirming nonexistent assumption raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            reaffirm_assumption(workspace, "ASN-999")


# ---------------------------------------------------------------------------
# List with filters
# ---------------------------------------------------------------------------

class TestListAssumptions:
    def test_filter_by_status(self, workspace):
        """Filter by status returns only matching."""
        add_assumption(workspace, "A1", "scope", "high", "basis")
        add_assumption(workspace, "A2", "scope", "low", "basis")
        challenge_assumption(workspace, "ASN-001", "reason")
        active = list_assumptions(workspace, status="active")
        challenged = list_assumptions(workspace, status="challenged")
        assert len(active) == 1
        assert active[0]["id"] == "ASN-002"
        assert len(challenged) == 1
        assert challenged[0]["id"] == "ASN-001"

    def test_filter_by_origin(self, workspace):
        """Filter by origin separates concept-dev from requirements-dev."""
        _seed_ingestion(workspace, [{"id": "A-001", "description": "Imported"}])
        import_from_ingestion(workspace)
        add_assumption(workspace, "Local", "scope", "low", "basis")
        concept = list_assumptions(workspace, origin="concept-dev")
        reqdev = list_assumptions(workspace, origin="requirements-dev")
        assert len(concept) == 1
        assert len(reqdev) == 1

    def test_combined_filters(self, workspace):
        """Both status and origin filters applied together."""
        _seed_ingestion(workspace, [{"id": "A-001", "description": "Imported"}])
        import_from_ingestion(workspace)
        add_assumption(workspace, "Local", "scope", "low", "basis")
        challenge_assumption(workspace, "ASN-001", "reason")  # concept-dev challenged
        result = list_assumptions(workspace, status="active", origin="requirements-dev")
        assert len(result) == 1
        assert result[0]["id"] == "ASN-002"


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class TestSummary:
    def test_summary_counts(self, workspace):
        """Summary returns correct counts by status, origin, impact."""
        _seed_ingestion(workspace, [
            {"id": "A-001", "description": "Imp1", "impact_level": "high"},
            {"id": "A-002", "description": "Imp2", "impact_level": "critical"},
        ])
        import_from_ingestion(workspace)
        add_assumption(workspace, "Local", "scope", "low", "basis")
        challenge_assumption(workspace, "ASN-001", "reason")

        s = summary(workspace)
        assert s["total"] == 3
        assert s["by_status"]["active"] == 2
        assert s["by_status"]["challenged"] == 1
        assert s["by_origin"]["concept-dev"] == 2
        assert s["by_origin"]["requirements-dev"] == 1
        assert s["high_impact_active"] == 1  # ASN-002 is critical+active

    def test_empty_summary(self, workspace):
        """Summary with no assumptions returns all zeros."""
        s = summary(workspace)
        assert s["total"] == 0
        assert s["high_impact_active"] == 0
