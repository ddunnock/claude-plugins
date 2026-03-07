"""Tests for diagram generation: schema validation, registry, D2 and Mermaid engines."""

import json
import os

import jsonschema
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schema_path() -> str:
    """Return absolute path to schemas/diagram.json."""
    return os.path.join(
        os.path.dirname(__file__), os.pardir, "schemas", "diagram.json"
    )


def _load_schema() -> dict:
    with open(_schema_path()) as f:
        return json.load(f)


def _make_diagram_slot(**overrides) -> dict:
    """Return a minimal valid diagram slot dict."""
    slot = {
        "slot_id": "diag-test-abc123def456",
        "slot_type": "diagram",
        "name": "diagram-system-overview",
        "version": 1,
        "format": "d2",
        "diagram_type": "structural",
        "source": "# empty diagram",
        "source_view_spec": "system-overview",
        "source_snapshot_id": "abc123def456abcd",
        "slot_count": 3,
        "gap_count": 1,
        "created_at": "2026-03-07T00:00:00+00:00",
        "updated_at": "2026-03-07T00:00:00+00:00",
    }
    slot.update(overrides)
    return slot


def _make_view(**overrides) -> dict:
    """Return a minimal valid view handoff dict for testing generators."""
    view = {
        "spec_name": "system-overview",
        "format_version": "1.0",
        "assembled_at": "2026-03-07T00:00:00+00:00",
        "snapshot_id": "abc123def456abcd",
        "total_slots": 3,
        "total_gaps": 1,
        "gap_summary": {"info": 0, "warning": 1, "error": 0},
        "sections": [
            {
                "slot_type": "component",
                "slots": [
                    {
                        "slot_id": "comp-auth-service",
                        "slot_type": "component",
                        "name": "Auth Service",
                        "version": 1,
                    },
                    {
                        "slot_id": "comp-db-service",
                        "slot_type": "component",
                        "name": "Database Service",
                        "version": 1,
                    },
                ],
            },
            {
                "slot_type": "interface",
                "slots": [
                    {
                        "slot_id": "intf-auth-api",
                        "slot_type": "interface",
                        "name": "Auth API",
                        "version": 1,
                    },
                ],
            },
        ],
        "edges": [
            {
                "source_id": "comp-auth-service",
                "target_id": "intf-auth-api",
                "relationship_type": "component_interface",
            },
        ],
        "gaps": [
            {
                "scope_pattern": "contract:*",
                "slot_type": "contract",
                "severity": "warning",
                "reason": "No contract slots found",
                "suggestion": "Run /system-dev:contract to define contracts.",
            },
        ],
        "metadata": {
            "elapsed_ms": 5.0,
            "ranking_method": "density",
            "section_counts": {"component": 2, "interface": 1},
        },
    }
    view.update(overrides)
    return view


# ===========================================================================
# Task 1: Schema validation tests
# ===========================================================================

class TestDiagramSchema:
    """Test schemas/diagram.json validates diagram slot structure."""

    def test_valid_slot_passes_validation(self):
        schema = _load_schema()
        slot = _make_diagram_slot()
        jsonschema.validate(slot, schema)  # should not raise

    def test_missing_source_rejected(self):
        schema = _load_schema()
        slot = _make_diagram_slot()
        del slot["source"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(slot, schema)

    def test_missing_format_rejected(self):
        schema = _load_schema()
        slot = _make_diagram_slot()
        del slot["format"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(slot, schema)

    def test_invalid_format_rejected(self):
        schema = _load_schema()
        slot = _make_diagram_slot(format="svg")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(slot, schema)

    def test_invalid_diagram_type_rejected(self):
        schema = _load_schema()
        slot = _make_diagram_slot(diagram_type="invalid")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(slot, schema)

    def test_additional_properties_rejected(self):
        schema = _load_schema()
        slot = _make_diagram_slot(extra_field="nope")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(slot, schema)


# ===========================================================================
# Task 1: Registry registration tests
# ===========================================================================

class TestRegistryRegistration:
    """Test diagram slot type registration in registry.py."""

    def test_diagram_in_slot_type_dirs(self):
        from scripts.registry import SLOT_TYPE_DIRS
        assert "diagram" in SLOT_TYPE_DIRS
        assert SLOT_TYPE_DIRS["diagram"] == "diagram"

    def test_diagram_in_slot_id_prefixes(self):
        from scripts.registry import SLOT_ID_PREFIXES
        assert "diagram" in SLOT_ID_PREFIXES
        assert SLOT_ID_PREFIXES["diagram"] == "diag"


class TestInitWorkspaceRegistration:
    """Test registry/diagram in init_workspace registry_dirs."""

    def test_diagram_dir_in_registry_dirs(self):
        """Verify registry/diagram appears in init_workspace source."""
        init_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "scripts", "init_workspace.py"
        )
        with open(init_path) as f:
            source = f.read()
        assert '"registry/diagram"' in source
