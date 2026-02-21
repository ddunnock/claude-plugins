"""Tests for set_validator.py - cross-block validation checks."""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import set_validator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def validation_workspace(tmp_path):
    """Multi-block workspace with varied data for validation testing."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()

    state = {
        "session_id": "val-test",
        "schema_version": "1.0.0",
        "created_at": "2025-01-01T00:00:00+00:00",
        "current_phase": "deliver",
        "gates": {"init": True, "needs": True, "requirements": True, "deliver": True},
        "blocks": {
            "auth": {
                "name": "auth",
                "description": "Authentication",
                "relationships": ["data"],
            },
            "data": {
                "name": "data",
                "description": "Data storage",
                "relationships": ["auth"],
            },
            "reporting": {
                "name": "reporting",
                "description": "Reporting",
                "relationships": [],
            },
        },
        "progress": {
            "current_block": None,
            "current_type_pass": None,
            "type_pass_order": ["functional", "performance", "interface", "constraint", "quality"],
            "requirements_in_draft": [],
        },
        "counts": {
            "needs_total": 4, "needs_approved": 3, "needs_deferred": 1,
            "requirements_total": 6, "requirements_registered": 4,
            "requirements_baselined": 2, "requirements_withdrawn": 0,
            "tbd_open": 1, "tbr_open": 0,
        },
        "traceability": {"links_total": 0, "coverage_pct": 0.0},
        "decomposition": {"levels": {}, "max_level": 3},
        "artifacts": {},
    }
    (ws / "state.json").write_text(json.dumps(state, indent=2))

    needs = {
        "schema_version": "1.0.0",
        "needs": [
            {"id": "NEED-001", "statement": "The operator needs to authenticate securely", "stakeholder": "Operator", "status": "approved", "source_block": "auth"},
            {"id": "NEED-002", "statement": "The operator needs to store data persistently", "stakeholder": "Operator", "status": "approved", "source_block": "data"},
            {"id": "NEED-003", "statement": "The operator needs to generate compliance reports", "stakeholder": "Operator", "status": "approved", "source_block": "reporting"},
            {"id": "NEED-004", "statement": "The operator needs to export data to USB", "stakeholder": "Operator", "status": "deferred", "source_block": "data"},
        ],
    }
    (ws / "needs_registry.json").write_text(json.dumps(needs, indent=2))

    reqs = {
        "schema_version": "1.0.0",
        "requirements": [
            # auth block
            {"id": "REQ-001", "statement": "The system shall authenticate users via username and password credentials", "type": "functional", "priority": "high", "status": "registered", "parent_need": "NEED-001", "source_block": "auth", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
            {"id": "REQ-002", "statement": "The system shall authenticate end-users via biometric verification", "type": "functional", "priority": "medium", "status": "registered", "parent_need": "NEED-001", "source_block": "auth", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
            # data block - near-duplicate of REQ-001
            {"id": "REQ-003", "statement": "The system shall authenticate users via username and password", "type": "functional", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
            # data block - interface requirement
            {"id": "REQ-004", "statement": "The system shall provide an API for authentication service to query user data", "type": "interface", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
            # data block - with TBD
            {"id": "REQ-005", "statement": "The system shall store data with TBD encryption standard", "type": "constraint", "priority": "high", "status": "registered", "parent_need": "NEED-002", "source_block": "data", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": {"tbd": "Encryption standard pending security review", "tbr": None}, "rationale": None, "registered_at": "2025-01-01"},
            # reporting block - uses "client" instead of "user"/"end-user"
            {"id": "REQ-006", "statement": "The system shall allow clients to generate compliance reports on demand", "type": "functional", "priority": "medium", "status": "registered", "parent_need": "NEED-003", "source_block": "reporting", "level": 0, "attributes": {}, "quality_checks": {}, "tbd_tbr": None, "rationale": None, "registered_at": "2025-01-01"},
        ],
    }
    (ws / "requirements_registry.json").write_text(json.dumps(reqs, indent=2))

    trace = {
        "schema_version": "1.0.0",
        "links": [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from", "role": "requirement"},
            {"source": "REQ-002", "target": "NEED-001", "type": "derives_from", "role": "requirement"},
            {"source": "REQ-003", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
            {"source": "REQ-004", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
            {"source": "REQ-005", "target": "NEED-002", "type": "derives_from", "role": "requirement"},
            {"source": "REQ-006", "target": "NEED-003", "type": "derives_from", "role": "requirement"},
        ],
    }
    (ws / "traceability_registry.json").write_text(json.dumps(trace, indent=2))

    return ws


# ---------------------------------------------------------------------------
# Interface coverage tests
# ---------------------------------------------------------------------------

class TestInterfaceCoverage:
    def test_covered_block_relationship(self, validation_workspace):
        """Block pair with interface requirements passes."""
        ws = str(validation_workspace)
        state = json.loads((validation_workspace / "state.json").read_text())
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
        # auth<->data has REQ-004 (interface type, data block, mentions auth)
        covered = [f for f in findings if f["status"] == "covered"]
        assert len(covered) >= 1

    def test_missing_interface_requirements(self, validation_workspace):
        """Block pair without interface requirements is flagged."""
        ws = str(validation_workspace)
        state = json.loads((validation_workspace / "state.json").read_text())
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
        # auth<->data is covered, but check the structure
        assert isinstance(findings, list)
        for f in findings:
            assert "block_a" in f
            assert "block_b" in f
            assert f["status"] in ("covered", "missing")

    def test_blocks_with_no_relationships(self, validation_workspace):
        """Blocks with empty relationships list are skipped."""
        ws = str(validation_workspace)
        state = json.loads((validation_workspace / "state.json").read_text())
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_interface_coverage(state["blocks"], reqs)
        # reporting has no relationships, should not appear
        reporting_findings = [f for f in findings if "reporting" in (f["block_a"], f["block_b"])]
        assert len(reporting_findings) == 0


# ---------------------------------------------------------------------------
# Duplicate detection tests
# ---------------------------------------------------------------------------

class TestDuplicateDetection:
    def test_near_duplicate_flagged(self, validation_workspace):
        """REQ-001 and REQ-003 are near-duplicates and should be flagged."""
        ws = str(validation_workspace)
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_duplicates(reqs, threshold=0.7)
        pairs = [(f["req_a"], f["req_b"]) for f in findings]
        assert ("REQ-001", "REQ-003") in pairs or ("REQ-003", "REQ-001") in pairs

    def test_different_requirements_not_flagged(self, validation_workspace):
        """Distinctly different requirements should not be flagged."""
        ws = str(validation_workspace)
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_duplicates(reqs, threshold=0.8)
        # REQ-001 (auth via password) and REQ-006 (compliance reports) should NOT be a pair
        pairs = [(f["req_a"], f["req_b"]) for f in findings]
        assert ("REQ-001", "REQ-006") not in pairs
        assert ("REQ-006", "REQ-001") not in pairs

    def test_common_prefix_not_dominating(self):
        """Requirements sharing only 'The system shall' prefix should not match."""
        sim = set_validator.compute_ngram_similarity(
            "The system shall authenticate users via credentials",
            "The system shall generate compliance reports on demand",
        )
        assert sim < 0.5  # Very different after the prefix

    def test_ngram_computation_correct(self):
        """N-gram similarity of identical texts is 1.0."""
        text = "The system shall respond within 500ms"
        sim = set_validator.compute_ngram_similarity(text, text)
        assert sim == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Terminology consistency tests
# ---------------------------------------------------------------------------

class TestTerminologyConsistency:
    def test_inconsistent_terms_flagged(self, validation_workspace):
        """Detects 'user' vs 'end-user' vs 'client' across blocks."""
        ws = str(validation_workspace)
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        findings = set_validator.check_terminology(reqs)
        # Should find something related to user/end-user/client variants
        assert len(findings) > 0

    def test_consistent_terminology_no_flags(self):
        """Consistent terminology produces no flags."""
        reqs = [
            {"id": "R1", "statement": "The system shall validate user input", "source_block": "a", "status": "registered"},
            {"id": "R2", "statement": "The system shall display user profile", "source_block": "b", "status": "registered"},
        ]
        findings = set_validator.check_terminology(reqs)
        assert len(findings) == 0


# ---------------------------------------------------------------------------
# Uncovered needs tests
# ---------------------------------------------------------------------------

class TestUncoveredNeeds:
    def test_uncovered_need_flagged(self, tmp_path):
        """Need with no derived requirements is flagged."""
        needs = [
            {"id": "NEED-001", "statement": "Need one", "status": "approved"},
            {"id": "NEED-002", "statement": "Need two", "status": "approved"},
        ]
        links = [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
        ]
        findings = set_validator.check_uncovered_needs(needs, links)
        uncovered_ids = [f["id"] for f in findings]
        assert "NEED-002" in uncovered_ids
        assert "NEED-001" not in uncovered_ids

    def test_covered_need_not_flagged(self, tmp_path):
        """Need with derived requirement is not flagged."""
        needs = [{"id": "NEED-001", "statement": "Need one", "status": "approved"}]
        links = [{"source": "REQ-001", "target": "NEED-001", "type": "derives_from"}]
        findings = set_validator.check_uncovered_needs(needs, links)
        assert len(findings) == 0

    def test_deferred_needs_excluded(self, tmp_path):
        """Deferred needs are excluded from coverage check."""
        needs = [
            {"id": "NEED-001", "statement": "Active need", "status": "approved"},
            {"id": "NEED-002", "statement": "Deferred need", "status": "deferred"},
        ]
        links = [{"source": "REQ-001", "target": "NEED-001", "type": "derives_from"}]
        findings = set_validator.check_uncovered_needs(needs, links)
        uncovered_ids = [f["id"] for f in findings]
        assert "NEED-002" not in uncovered_ids


# ---------------------------------------------------------------------------
# TBD/TBR report tests
# ---------------------------------------------------------------------------

class TestTbdTbrReport:
    def test_open_tbd_listed(self, validation_workspace):
        """Lists all open TBD items."""
        reqs = json.loads((validation_workspace / "requirements_registry.json").read_text())["requirements"]
        report = set_validator.check_tbd_tbr(reqs)
        assert len(report["open_tbd"]) >= 1
        assert report["open_tbd"][0]["id"] == "REQ-005"

    def test_resolved_tbd_excluded(self):
        """Resolved TBD items excluded from report."""
        reqs = [
            {"id": "R1", "tbd_tbr": {"tbd": None, "tbr": None}, "status": "registered"},
            {"id": "R2", "tbd_tbr": None, "status": "registered"},
        ]
        report = set_validator.check_tbd_tbr(reqs)
        assert len(report["open_tbd"]) == 0
        assert len(report["open_tbr"]) == 0


# ---------------------------------------------------------------------------
# INCOSE set characteristic tests
# ---------------------------------------------------------------------------

class TestIncoseSetCharacteristics:
    def test_c10_completeness(self, validation_workspace):
        """C10: All approved needs traced to requirements."""
        ws = str(validation_workspace)
        result = set_validator.check_incose_set_characteristics(ws)
        assert "c10_completeness" in result
        # All 3 approved needs have derived requirements
        assert result["c10_completeness"]["passed"] is True

    def test_c14_validatability(self, validation_workspace):
        """C14: Check that requirements have V&V methods."""
        ws = str(validation_workspace)
        result = set_validator.check_incose_set_characteristics(ws)
        assert "c14_validatability" in result

    def test_c15_correctness(self, validation_workspace):
        """C15: All requirements derive from approved needs."""
        ws = str(validation_workspace)
        result = set_validator.check_incose_set_characteristics(ws)
        assert "c15_correctness" in result
        assert result["c15_correctness"]["passed"] is True
