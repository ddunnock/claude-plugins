"""Tests for traceability.py."""
import json

import pytest

from traceability import coverage_report, link, orphan_check, query


def _seed_registries(ws, needs=None, reqs=None):
    """Seed needs and requirements registries."""
    if needs is None:
        needs = [
            {"id": "NEED-001", "statement": "Need 1", "stakeholder": "Op", "status": "approved"},
            {"id": "NEED-002", "statement": "Need 2", "stakeholder": "Op", "status": "approved"},
        ]
    if reqs is None:
        reqs = [
            {"id": "REQ-001", "statement": "Req 1", "type": "functional", "status": "registered",
             "parent_need": "NEED-001", "source_block": "blk"},
            {"id": "REQ-002", "statement": "Req 2", "type": "functional", "status": "registered",
             "parent_need": "NEED-002", "source_block": "blk"},
        ]
    (ws / "needs_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "needs": needs}))
    (ws / "requirements_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "requirements": reqs}))
    # Ensure traceability registry exists
    if not (ws / "traceability_registry.json").exists():
        (ws / "traceability_registry.json").write_text(json.dumps({"schema_version": "1.0.0", "links": []}))


# --- Link creation ---

def test_link_creates_valid_link(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
    assert len(reg["links"]) == 1
    assert reg["links"][0]["source"] == "REQ-001"
    assert reg["links"][0]["target"] == "NEED-001"
    assert reg["links"][0]["type"] == "derives_from"


def test_link_validates_source_exists(tmp_workspace):
    _seed_registries(tmp_workspace)
    with pytest.raises(ValueError, match="not found"):
        link(str(tmp_workspace), "REQ-999", "NEED-001", "derives_from", "requirement")


def test_link_validates_target_exists(tmp_workspace):
    _seed_registries(tmp_workspace)
    with pytest.raises(ValueError, match="not found"):
        link(str(tmp_workspace), "REQ-001", "NEED-999", "derives_from", "requirement")


def test_link_conflicts_with_has_resolution(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "REQ-002", "conflicts_with", "conflict")
    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
    lnk = reg["links"][0]
    assert lnk["type"] == "conflicts_with"
    assert lnk["resolution_status"] == "open"


# --- Query ---

def test_query_forward(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    result = query(str(tmp_workspace), "REQ-001", "forward")
    assert len(result) == 1
    assert result[0]["target"] == "NEED-001"


def test_query_backward(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    result = query(str(tmp_workspace), "NEED-001", "backward")
    assert len(result) == 1
    assert result[0]["source"] == "REQ-001"


def test_query_both(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    link(str(tmp_workspace), "REQ-002", "REQ-001", "parent_of", "hierarchy")
    result = query(str(tmp_workspace), "REQ-001", "both")
    assert len(result) == 2


def test_query_no_links(tmp_workspace):
    _seed_registries(tmp_workspace)
    result = query(str(tmp_workspace), "REQ-001", "both")
    assert result == []


# --- Coverage ---

def test_coverage_full(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    link(str(tmp_workspace), "REQ-002", "NEED-002", "derives_from", "requirement")
    report = coverage_report(str(tmp_workspace))
    assert report["coverage_pct"] == 100.0
    assert report["needs_covered"] == 2


def test_coverage_partial(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    report = coverage_report(str(tmp_workspace))
    assert report["coverage_pct"] == 50.0
    assert report["needs_covered"] == 1
    assert report["needs_total"] == 2


def test_coverage_excludes_withdrawn(tmp_workspace):
    reqs = [
        {"id": "REQ-001", "statement": "Req 1", "type": "functional", "status": "withdrawn",
         "parent_need": "NEED-001", "source_block": "blk"},
    ]
    _seed_registries(tmp_workspace, reqs=reqs)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    report = coverage_report(str(tmp_workspace))
    # Withdrawn requirement doesn't count for coverage
    assert report["needs_covered"] == 0


# --- Orphan detection ---

def test_orphan_finds_uncovered_needs(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    # NEED-002 has no requirement
    result = orphan_check(str(tmp_workspace))
    assert "NEED-002" in result["orphan_needs"]


def test_orphan_finds_unlinked_requirements(tmp_workspace):
    _seed_registries(tmp_workspace)
    # REQ-001 has no derives_from link
    result = orphan_check(str(tmp_workspace))
    assert "REQ-001" in result["orphan_requirements"]
    assert "REQ-002" in result["orphan_requirements"]


def test_orphan_empty_when_all_linked(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    link(str(tmp_workspace), "REQ-002", "NEED-002", "derives_from", "requirement")
    result = orphan_check(str(tmp_workspace))
    assert result["orphan_needs"] == []
    assert result["orphan_requirements"] == []


# --- Schema ---

def test_schema_version_present(tmp_workspace):
    _seed_registries(tmp_workspace)
    link(str(tmp_workspace), "REQ-001", "NEED-001", "derives_from", "requirement")
    reg = json.loads((tmp_workspace / "traceability_registry.json").read_text())
    assert reg["schema_version"] == "1.0.0"
