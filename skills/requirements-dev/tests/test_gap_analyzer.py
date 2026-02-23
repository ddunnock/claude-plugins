"""Tests for gap_analyzer.py -- coverage gap detection."""
import json

import pytest

from gap_analyzer import (
    analyze,
    block_asymmetry,
    block_need_coverage,
    block_type_matrix,
    concept_coverage,
    interface_coverage,
    need_sufficiency,
    priority_alignment,
    vv_coverage,
)


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace with state.json and registries."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir()
    state = {
        "session_id": "test-gap",
        "schema_version": "1.0.0",
        "current_phase": "requirements",
        "gates": {"init": True, "needs": True, "requirements": False},
        "blocks": {
            "auth": {"name": "auth", "description": "Authentication", "relationships": ["data"]},
            "data": {"name": "data", "description": "Data storage", "relationships": ["auth"]},
            "logging": {"name": "logging", "description": "Logging", "relationships": []},
        },
        "counts": {},
        "traceability": {},
        "decomposition": {"levels": {}, "max_level": 3},
        "artifacts": {},
    }
    (ws / "state.json").write_text(json.dumps(state, indent=2))
    return str(ws)


def _seed_needs(ws, needs):
    """Helper: write needs_registry.json."""
    reg = {"schema_version": "1.0.0", "needs": needs}
    with open(f"{ws}/needs_registry.json", "w") as f:
        json.dump(reg, f, indent=2)


def _seed_requirements(ws, reqs):
    """Helper: write requirements_registry.json."""
    reg = {"schema_version": "1.0.0", "requirements": reqs}
    with open(f"{ws}/requirements_registry.json", "w") as f:
        json.dump(reg, f, indent=2)


def _seed_traceability(ws, links):
    """Helper: write traceability_registry.json."""
    reg = {"schema_version": "1.0.0", "links": links}
    with open(f"{ws}/traceability_registry.json", "w") as f:
        json.dump(reg, f, indent=2)


def _seed_ingestion(ws, sources=None, assumptions=None):
    """Helper: write ingestion.json."""
    data = {"source_refs": sources or [], "assumption_refs": assumptions or []}
    with open(f"{ws}/ingestion.json", "w") as f:
        json.dump(data, f, indent=2)


def _make_req(req_id, rtype="functional", priority="high", block="auth", status="registered"):
    return {
        "id": req_id, "statement": f"Req {req_id}", "type": rtype,
        "priority": priority, "source_block": block, "status": status,
        "parent_need": None, "level": 0, "attributes": {},
        "quality_checks": {}, "tbd_tbr": None, "rationale": None,
    }


def _make_need(need_id, block="auth", status="approved", refs=None):
    return {
        "id": need_id, "statement": f"Need {need_id}", "stakeholder": "User",
        "source_block": block, "status": status, "rationale": None,
        "source_artifacts": [], "concept_dev_refs": refs or {},
    }


# ---------------------------------------------------------------------------
# Block × Type Matrix
# ---------------------------------------------------------------------------

class TestBlockTypeMatrix:
    def test_full_coverage(self, workspace):
        """Block with all 5 types has no gaps."""
        reqs = [_make_req(f"REQ-{i+1}", rtype=t, block="auth")
                for i, t in enumerate(["functional", "performance", "interface", "constraint", "quality"])]
        _seed_requirements(workspace, reqs)
        result = block_type_matrix(workspace)
        auth_gaps = [g for g in result["gaps"] if g["block"] == "auth"]
        assert len(auth_gaps) == 0

    def test_partial_gaps(self, workspace):
        """Block with only functional reqs has 4 missing types."""
        _seed_requirements(workspace, [_make_req("REQ-001", "functional", block="auth")])
        result = block_type_matrix(workspace)
        auth_gap = next(g for g in result["gaps"] if g["block"] == "auth")
        assert set(auth_gap["missing_types"]) == {"performance", "interface", "constraint", "quality"}

    def test_empty_block(self, workspace):
        """Block with zero reqs shows all 5 types missing."""
        _seed_requirements(workspace, [])
        result = block_type_matrix(workspace)
        logging_gap = next(g for g in result["gaps"] if g["block"] == "logging")
        assert len(logging_gap["missing_types"]) == 5

    def test_block_filter(self, workspace):
        """Filtering to a single block only returns that block."""
        _seed_requirements(workspace, [_make_req("REQ-001", "functional", block="auth")])
        result = block_type_matrix(workspace, block_filter="auth")
        assert "auth" in result["matrix"]
        assert "data" not in result["matrix"]

    def test_withdrawn_excluded(self, workspace):
        """Withdrawn requirements are not counted."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", "functional", block="auth", status="registered"),
            _make_req("REQ-002", "performance", block="auth", status="withdrawn"),
        ])
        result = block_type_matrix(workspace)
        assert result["matrix"]["auth"]["performance"] == 0


# ---------------------------------------------------------------------------
# Concept Coverage
# ---------------------------------------------------------------------------

class TestConceptCoverage:
    def test_no_ingestion(self, workspace):
        """Gracefully handles missing ingestion.json."""
        result = concept_coverage(workspace)
        assert result["available"] is False

    def test_all_covered(self, workspace):
        """All sources referenced by needs."""
        _seed_ingestion(workspace,
                        sources=[{"id": "SRC-001"}, {"id": "SRC-002"}],
                        assumptions=[{"id": "ASN-001"}])
        _seed_needs(workspace, [
            _make_need("NEED-001", refs={"sources": ["SRC-001", "SRC-002"], "assumptions": ["ASN-001"]}),
        ])
        result = concept_coverage(workspace)
        assert result["uncovered_sources"] == []
        assert result["uncovered_assumptions"] == []

    def test_uncovered_sources(self, workspace):
        """Unlinked sources are flagged."""
        _seed_ingestion(workspace,
                        sources=[{"id": "SRC-001"}, {"id": "SRC-002"}, {"id": "SRC-003"}])
        _seed_needs(workspace, [
            _make_need("NEED-001", refs={"sources": ["SRC-001"]}),
        ])
        result = concept_coverage(workspace)
        assert result["sources_total"] == 3
        assert result["sources_covered"] == 1
        assert set(result["uncovered_sources"]) == {"SRC-002", "SRC-003"}

    def test_uncovered_assumptions(self, workspace):
        """Unlinked assumptions are flagged."""
        _seed_ingestion(workspace, assumptions=[{"id": "ASN-001"}, {"id": "ASN-002"}])
        _seed_needs(workspace, [_make_need("NEED-001")])
        result = concept_coverage(workspace)
        assert result["assumptions_total"] == 2
        assert len(result["uncovered_assumptions"]) == 2


# ---------------------------------------------------------------------------
# Block Asymmetry
# ---------------------------------------------------------------------------

class TestBlockAsymmetry:
    def test_symmetric_pair(self, workspace):
        """Related blocks with similar counts are not flagged."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", block="auth"),
            _make_req("REQ-002", block="auth"),
            _make_req("REQ-003", block="data"),
            _make_req("REQ-004", block="data"),
        ])
        result = block_asymmetry(workspace)
        auth_data = next(p for p in result["pairs"]
                         if set([p["block_a"], p["block_b"]]) == {"auth", "data"})
        assert auth_data["asymmetric"] is False

    def test_asymmetric_pair(self, workspace):
        """Related blocks with severe imbalance are flagged."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", block="auth"),
            _make_req("REQ-002", block="auth"),
            _make_req("REQ-003", block="auth"),
            _make_req("REQ-004", block="auth"),
            _make_req("REQ-005", block="auth"),
            # data has 0 reqs
        ])
        result = block_asymmetry(workspace)
        auth_data = next(p for p in result["pairs"]
                         if set([p["block_a"], p["block_b"]]) == {"auth", "data"})
        assert auth_data["asymmetric"] is True

    def test_unrelated_blocks_not_checked(self, workspace):
        """Blocks without relationships are not in pairs."""
        _seed_requirements(workspace, [])
        result = block_asymmetry(workspace)
        pair_blocks = set()
        for p in result["pairs"]:
            pair_blocks.add(p["block_a"])
            pair_blocks.add(p["block_b"])
        # logging has no relationships
        assert "logging" not in pair_blocks


# ---------------------------------------------------------------------------
# V&V Coverage
# ---------------------------------------------------------------------------

class TestVVCoverage:
    def test_all_have_vv(self, workspace):
        """100% coverage when all reqs have verified_by links."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", "functional"),
            _make_req("REQ-002", "performance"),
        ])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "vv-001", "type": "verified_by"},
            {"source": "REQ-002", "target": "vv-002", "type": "verified_by"},
        ])
        result = vv_coverage(workspace)
        assert result["overall_pct"] == 100.0

    def test_some_missing(self, workspace):
        """Missing V&V methods are flagged by type."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", "functional"),
            _make_req("REQ-002", "performance"),
        ])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "vv-001", "type": "verified_by"},
        ])
        result = vv_coverage(workspace)
        assert result["by_type"]["performance"]["without_vv"] == 1
        assert result["by_type"]["performance"]["missing_ids"] == ["REQ-002"]
        assert result["overall_pct"] == 50.0

    def test_empty_reqs(self, workspace):
        """No requirements gives 0% coverage."""
        _seed_requirements(workspace, [])
        _seed_traceability(workspace, [])
        result = vv_coverage(workspace)
        assert result["overall_pct"] == 0.0


# ---------------------------------------------------------------------------
# Priority Alignment
# ---------------------------------------------------------------------------

class TestPriorityAlignment:
    def test_aligned(self, workspace):
        """High-priority need with high-priority req: no misalignment."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [_make_req("REQ-001", priority="high")])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
        ])
        result = priority_alignment(workspace)
        assert result["count"] == 0

    def test_misaligned(self, workspace):
        """Need with only low-priority reqs is flagged."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [_make_req("REQ-001", priority="low")])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
        ])
        result = priority_alignment(workspace)
        assert result["count"] == 1
        assert result["misalignments"][0]["gap_direction"] == "need_underserved"


# ---------------------------------------------------------------------------
# Need Sufficiency
# ---------------------------------------------------------------------------

class TestNeedSufficiency:
    def test_well_covered(self, workspace):
        """Need with 3 derived reqs is well covered."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [
            _make_req("REQ-001"), _make_req("REQ-002"), _make_req("REQ-003"),
        ])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
            {"source": "REQ-002", "target": "NEED-001", "type": "derives_from"},
            {"source": "REQ-003", "target": "NEED-001", "type": "derives_from"},
        ])
        result = need_sufficiency(workspace)
        assert result["well_covered"] == 1
        assert len(result["under_implemented"]) == 0

    def test_under_implemented(self, workspace):
        """Need with 0 derived reqs is flagged."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [])
        _seed_traceability(workspace, [])
        result = need_sufficiency(workspace)
        assert len(result["under_implemented"]) == 1
        assert result["under_implemented"][0]["derived_count"] == 0

    def test_single_req(self, workspace):
        """Need with 1 derived req is flagged as under-implemented."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [_make_req("REQ-001")])
        _seed_traceability(workspace, [
            {"source": "REQ-001", "target": "NEED-001", "type": "derives_from"},
        ])
        result = need_sufficiency(workspace)
        assert len(result["under_implemented"]) == 1
        assert result["under_implemented"][0]["derived_count"] == 1


# ---------------------------------------------------------------------------
# Block Need Coverage
# ---------------------------------------------------------------------------

class TestBlockNeedCoverage:
    def test_all_blocks_have_needs(self, workspace):
        """No gaps when all blocks have at least one need."""
        _seed_needs(workspace, [
            _make_need("NEED-001", block="auth"),
            _make_need("NEED-002", block="data"),
            _make_need("NEED-003", block="logging"),
        ])
        result = block_need_coverage(workspace)
        assert result["blocks_without_needs"] == []

    def test_blocks_without_needs(self, workspace):
        """Blocks with no approved needs are flagged."""
        _seed_needs(workspace, [_make_need("NEED-001", block="auth")])
        result = block_need_coverage(workspace)
        assert "data" in result["blocks_without_needs"]
        assert "logging" in result["blocks_without_needs"]

    def test_deferred_not_counted(self, workspace):
        """Deferred needs don't count as coverage."""
        _seed_needs(workspace, [_make_need("NEED-001", block="auth", status="deferred")])
        result = block_need_coverage(workspace)
        assert "auth" in result["blocks_without_needs"]


# ---------------------------------------------------------------------------
# Interface Coverage
# ---------------------------------------------------------------------------

class TestInterfaceCoverage:
    def test_covered_relationship(self, workspace):
        """Relationship is covered when at least one side has interface reqs."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", rtype="interface", block="auth"),
        ])
        result = interface_coverage(workspace)
        # auth-data relationship: auth has interface req
        auth_data = [u for u in result.get("uncovered", [])
                     if set([u["block_a"], u["block_b"]]) == {"auth", "data"}]
        assert len(auth_data) == 0
        assert result["relationships_covered"] >= 1

    def test_uncovered_relationship(self, workspace):
        """Relationship without any interface reqs is flagged."""
        _seed_requirements(workspace, [
            _make_req("REQ-001", rtype="functional", block="auth"),
        ])
        result = interface_coverage(workspace)
        # auth-data has relationship but no interface reqs on either side
        uncovered_pairs = {tuple(sorted([u["block_a"], u["block_b"]])) for u in result["uncovered"]}
        assert ("auth", "data") in uncovered_pairs

    def test_no_relationships(self, workspace):
        """Blocks without relationships produce 0 total."""
        # logging has no relationships, so total only includes auth-data pair
        _seed_requirements(workspace, [])
        result = interface_coverage(workspace)
        assert result["relationships_total"] == 1  # only auth-data


# ---------------------------------------------------------------------------
# Analyze (Combined)
# ---------------------------------------------------------------------------

class TestAnalyze:
    def test_produces_all_sections(self, workspace):
        """Combined analysis includes all 8 gap categories."""
        _seed_needs(workspace, [_make_need("NEED-001")])
        _seed_requirements(workspace, [_make_req("REQ-001")])
        _seed_traceability(workspace, [])
        result = analyze(workspace)
        assert "schema_version" in result
        assert "timestamp" in result
        assert "block_type_matrix" in result
        assert "concept_coverage" in result
        assert "block_asymmetry" in result
        assert "vv_coverage" in result
        assert "priority_alignment" in result
        assert "need_sufficiency" in result
        assert "block_need_coverage" in result
        assert "interface_coverage" in result

    def test_saves_report(self, workspace):
        """analyze() persists gap_analysis.json."""
        _seed_needs(workspace, [])
        _seed_requirements(workspace, [])
        _seed_traceability(workspace, [])
        analyze(workspace)
        assert os.path.isfile(f"{workspace}/gap_analysis.json")
        saved = json.loads(open(f"{workspace}/gap_analysis.json").read())
        assert "schema_version" in saved


import os
