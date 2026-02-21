"""Tests for ReqIF XML export functionality."""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import reqif_export


def _make_registries(tmp_path, requirements=None, needs=None, links=None):
    """Helper to create registry files and return paths."""
    ws = tmp_path / ".requirements-dev"
    ws.mkdir(exist_ok=True)

    reqs = {"schema_version": "1.0.0", "requirements": requirements or []}
    needs_reg = {"schema_version": "1.0.0", "needs": needs or []}
    trace = {"schema_version": "1.0.0", "links": links or []}

    req_path = ws / "requirements_registry.json"
    needs_path = ws / "needs_registry.json"
    trace_path = ws / "traceability_registry.json"

    req_path.write_text(json.dumps(reqs, indent=2))
    needs_path.write_text(json.dumps(needs_reg, indent=2))
    trace_path.write_text(json.dumps(trace, indent=2))

    output_path = ws / "exports" / "requirements.reqif"
    return str(req_path), str(needs_path), str(trace_path), str(output_path)


def _sample_requirements():
    return [
        {
            "id": "REQ-001",
            "statement": "The system shall authenticate users via credentials",
            "type": "functional",
            "priority": "high",
            "status": "registered",
            "parent_need": "NEED-001",
            "source_block": "auth",
            "level": 0,
            "attributes": {},
            "quality_checks": {},
            "tbd_tbr": None,
            "rationale": None,
            "registered_at": "2025-01-01T00:00:00+00:00",
        },
        {
            "id": "REQ-002",
            "statement": "The system shall respond within 500ms",
            "type": "performance",
            "priority": "high",
            "status": "registered",
            "parent_need": "NEED-001",
            "source_block": "auth",
            "level": 0,
            "attributes": {},
            "quality_checks": {},
            "tbd_tbr": None,
            "rationale": None,
            "registered_at": "2025-01-01T00:00:00+00:00",
        },
    ]


def _sample_links():
    return [
        {
            "source": "REQ-001",
            "target": "NEED-001",
            "type": "derives_from",
            "role": "requirement",
            "created_at": "2025-01-01T00:00:00+00:00",
        },
        {
            "source": "REQ-002",
            "target": "NEED-001",
            "type": "derives_from",
            "role": "requirement",
            "created_at": "2025-01-01T00:00:00+00:00",
        },
    ]


class TestReqIFExport:
    """Tests for ReqIF XML export."""

    def test_export_generates_valid_xml(self, tmp_path):
        """Export with sample registries produces well-formed XML with REQ-IF root element."""
        req_p, needs_p, trace_p, out_p = _make_registries(
            tmp_path, requirements=_sample_requirements(), links=_sample_links(),
        )
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        assert os.path.isfile(out_p)
        tree = ElementTree.parse(out_p)
        root = tree.getroot()
        # Root should be REQ-IF (possibly with namespace)
        assert "REQ-IF" in root.tag

    def test_export_maps_requirements_to_spec_objects(self, tmp_path):
        """Each requirement in registry becomes a SPEC-OBJECT in ReqIF output."""
        reqs = _sample_requirements()
        req_p, needs_p, trace_p, out_p = _make_registries(
            tmp_path, requirements=reqs, links=_sample_links(),
        )
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        content = Path(out_p).read_text()
        for req in reqs:
            assert req["id"] in content, f"Missing requirement {req['id']} in output"

    def test_export_maps_links_to_spec_relations(self, tmp_path):
        """Each traceability link becomes a SPEC-RELATION in ReqIF output."""
        links = _sample_links()
        req_p, needs_p, trace_p, out_p = _make_registries(
            tmp_path, requirements=_sample_requirements(), links=links,
        )
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        content = Path(out_p).read_text()
        assert "SPEC-RELATION" in content

    def test_export_maps_types_to_spec_types(self, tmp_path):
        """Each requirement type (functional, performance, etc.) maps to a SPEC-TYPE."""
        req_p, needs_p, trace_p, out_p = _make_registries(
            tmp_path, requirements=_sample_requirements(), links=_sample_links(),
        )
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        content = Path(out_p).read_text()
        assert "SPEC-TYPE" in content

    def test_export_empty_registry(self, tmp_path):
        """Empty registries produce a minimal but valid ReqIF document."""
        req_p, needs_p, trace_p, out_p = _make_registries(tmp_path)
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        assert os.path.isfile(out_p)
        tree = ElementTree.parse(out_p)
        root = tree.getroot()
        assert "REQ-IF" in root.tag

    def test_export_missing_reqif_package(self, tmp_path, capsys):
        """When reqif package is not installed, prints install instructions and exits 0."""
        req_p, needs_p, trace_p, out_p = _make_registries(
            tmp_path, requirements=_sample_requirements(),
        )

        # Patch all reqif submodules to simulate missing package
        reqif_modules = {k: None for k in list(sys.modules) if k == "reqif" or k.startswith("reqif.")}
        reqif_modules["reqif"] = None

        with patch.dict("sys.modules", reqif_modules):
            reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        captured = capsys.readouterr()
        assert "install" in captured.out.lower() or "pip" in captured.out.lower()
        # Output file should NOT be created
        assert not os.path.isfile(out_p)

    def test_export_escapes_xml_special_chars(self, tmp_path):
        """Requirement text containing <, >, &, quotes is properly escaped in XML output."""
        reqs = [
            {
                "id": "REQ-001",
                "statement": 'The system shall handle <input> & "output" values > 0',
                "type": "functional",
                "priority": "high",
                "status": "registered",
                "parent_need": "NEED-001",
                "source_block": "auth",
                "level": 0,
                "attributes": {},
                "quality_checks": {},
                "tbd_tbr": None,
                "rationale": None,
                "registered_at": "2025-01-01T00:00:00+00:00",
            },
        ]
        req_p, needs_p, trace_p, out_p = _make_registries(tmp_path, requirements=reqs)
        reqif_export.export_reqif(req_p, needs_p, trace_p, out_p)

        assert os.path.isfile(out_p)
        # Must be parseable (special chars properly escaped)
        tree = ElementTree.parse(out_p)
        content = Path(out_p).read_text()
        # The original special chars should be escaped
        assert "&amp;" in content or "&lt;" in content
