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


# ===========================================================================
# Task 2: Sanitize ID tests
# ===========================================================================

class TestSanitizeId:
    """Test _sanitize_id() replaces special chars with underscores."""

    def test_hyphens_replaced(self):
        from scripts.diagram_generator import _sanitize_id
        assert _sanitize_id("comp-auth-service") == "comp_auth_service"

    def test_dots_replaced(self):
        from scripts.diagram_generator import _sanitize_id
        assert _sanitize_id("comp.auth.1") == "comp_auth_1"

    def test_underscores_preserved(self):
        from scripts.diagram_generator import _sanitize_id
        assert _sanitize_id("comp_auth") == "comp_auth"

    def test_alphanumeric_preserved(self):
        from scripts.diagram_generator import _sanitize_id
        assert _sanitize_id("abc123") == "abc123"


# ===========================================================================
# Task 2: D2 generation tests
# ===========================================================================

class TestGenerateD2:
    """Test generate_d2() produces valid D2 structural diagram source."""

    def test_components_as_containers(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "comp_auth_service:" in d2
        assert '"Auth Service"' in d2
        assert "shape: rectangle" in d2

    def test_edges_as_connections(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "comp_auth_service -> intf_auth_api: component_interface" in d2

    def test_gap_placeholder_dashed_with_prefix(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "[GAP]" in d2
        assert "stroke-dash: 5" in d2

    def test_gap_color_coded_by_severity_warning(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "#e6a117" in d2

    def test_gap_suggestion_as_comment(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "# Suggestion: Run /system-dev:contract to define contracts." in d2

    def test_gap_error_severity_color(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view(gaps=[{
            "scope_pattern": "contract:*",
            "slot_type": "contract",
            "severity": "error",
            "reason": "Missing contracts",
            "suggestion": "Add contracts.",
        }])
        d2 = generate_d2(view)
        assert "#dc3545" in d2

    def test_gap_info_severity_color(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view(gaps=[{
            "scope_pattern": "contract:*",
            "slot_type": "contract",
            "severity": "info",
            "reason": "Info gap",
            "suggestion": "Optional action.",
        }])
        d2 = generate_d2(view)
        assert "#888888" in d2

    def test_empty_view_produces_valid_d2(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view(sections=[], edges=[], gaps=[],
                          total_slots=0, total_gaps=0,
                          gap_summary={"info": 0, "warning": 0, "error": 0})
        d2 = generate_d2(view)
        assert "# Diagram:" in d2
        assert "# Generated from snapshot:" in d2

    def test_comment_header_contains_spec_name(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "# Diagram: system-overview (structural)" in d2
        assert "# Generated from snapshot: abc123def456abcd" in d2

    def test_unlinked_section_in_separate_container(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view(sections=[
            {
                "slot_type": "unlinked",
                "slots": [
                    {
                        "slot_id": "intf-orphan",
                        "slot_type": "interface",
                        "name": "Orphan Interface",
                        "version": 1,
                    },
                ],
            },
        ])
        d2 = generate_d2(view)
        assert "Unlinked:" in d2
        assert '"Unlinked"' in d2

    def test_interface_section_renders_as_labeled_nodes(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        d2 = generate_d2(view)
        assert "intf_auth_api:" in d2
        assert '"Auth API"' in d2

    def test_gap_dashed_connection_to_context(self):
        """Gap nodes with slot_type matching a section get dashed connection."""
        from scripts.diagram_generator import generate_d2
        view = _make_view(
            sections=[
                {
                    "slot_type": "component",
                    "slots": [
                        {"slot_id": "comp-a", "slot_type": "component",
                         "name": "A", "version": 1},
                    ],
                },
                {
                    "slot_type": "contract",
                    "slots": [
                        {"slot_id": "cntr-x", "slot_type": "contract",
                         "name": "X", "version": 1},
                    ],
                },
            ],
            gaps=[{
                "scope_pattern": "contract:*",
                "slot_type": "contract",
                "severity": "warning",
                "reason": "Missing contract",
                "suggestion": "Add contract.",
            }],
        )
        d2 = generate_d2(view)
        # Should have a dashed connection from gap to contract section context
        assert "style.stroke-dash: 5" in d2 or "stroke-dash: 5" in d2


# ===========================================================================
# Task 2: Mermaid generation tests
# ===========================================================================

class TestGenerateMermaid:
    """Test generate_mermaid() produces valid Mermaid flowchart source."""

    def test_nodes_from_slots(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert 'comp_auth_service["Auth Service"]' in mermaid

    def test_edges_with_labels(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert "-->|component_interface|" in mermaid

    def test_gap_classdef_styles(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert "classDef gapWarning" in mermaid
        assert "stroke:#e6a117" in mermaid
        assert "stroke-dasharray: 5 5" in mermaid
        # NO commas in stroke-dasharray value
        assert "stroke-dasharray: 5, 5" not in mermaid
        assert "stroke-dasharray: 5,5" not in mermaid

    def test_gap_node_with_class(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert ":::gapWarning" in mermaid
        assert "[GAP]" in mermaid

    def test_gap_suggestion_as_mermaid_comment(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert "%% Suggestion:" in mermaid

    def test_gap_error_classdef(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view(gaps=[{
            "scope_pattern": "contract:*",
            "slot_type": "contract",
            "severity": "error",
            "reason": "Missing",
            "suggestion": "Fix it.",
        }])
        mermaid = generate_mermaid(view)
        assert "classDef gapError" in mermaid
        assert "stroke:#dc3545" in mermaid

    def test_gap_info_classdef(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view(gaps=[{
            "scope_pattern": "contract:*",
            "slot_type": "contract",
            "severity": "info",
            "reason": "Info",
            "suggestion": "Optional.",
        }])
        mermaid = generate_mermaid(view)
        assert "classDef gapInfo" in mermaid
        assert "stroke:#888888" in mermaid

    def test_empty_view_produces_valid_mermaid(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view(sections=[], edges=[], gaps=[],
                          total_slots=0, total_gaps=0,
                          gap_summary={"info": 0, "warning": 0, "error": 0})
        mermaid = generate_mermaid(view)
        assert "%% Diagram:" in mermaid
        assert "graph TD" in mermaid

    def test_comment_header(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert "%% Diagram: system-overview (behavioral)" in mermaid
        assert "%% Generated from snapshot: abc123def456abcd" in mermaid

    def test_unlinked_slots_standalone_lighter_styling(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view(sections=[
            {
                "slot_type": "unlinked",
                "slots": [
                    {
                        "slot_id": "intf-orphan",
                        "slot_type": "interface",
                        "name": "Orphan Interface",
                        "version": 1,
                    },
                ],
            },
        ])
        mermaid = generate_mermaid(view)
        assert "intf_orphan" in mermaid
        assert "classDef unlinked" in mermaid

    def test_graph_direction_default_td(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        mermaid = generate_mermaid(view)
        assert "graph TD" in mermaid

    def test_graph_direction_lr_when_many_edges(self):
        """When edge count > 2x node count, use LR direction."""
        from scripts.diagram_generator import generate_mermaid
        view = _make_view(
            sections=[{
                "slot_type": "component",
                "slots": [
                    {"slot_id": "comp-a", "slot_type": "component",
                     "name": "A", "version": 1},
                ],
            }],
            edges=[
                {"source_id": "comp-a", "target_id": "comp-b",
                 "relationship_type": "r1"},
                {"source_id": "comp-a", "target_id": "comp-c",
                 "relationship_type": "r2"},
                {"source_id": "comp-a", "target_id": "comp-d",
                 "relationship_type": "r3"},
            ],
        )
        mermaid = generate_mermaid(view)
        assert "graph LR" in mermaid


# ===========================================================================
# Task 2: Compute diagram slot ID tests
# ===========================================================================

class TestComputeDiagramSlotId:
    """Test _compute_diagram_slot_id() content-hash ID generation."""

    def test_returns_diag_prefix(self):
        from scripts.diagram_generator import _compute_diagram_slot_id
        result = _compute_diagram_slot_id("system-overview", "# test")
        assert result.startswith("diag-system-overview-")

    def test_deterministic(self):
        from scripts.diagram_generator import _compute_diagram_slot_id
        a = _compute_diagram_slot_id("spec", "source")
        b = _compute_diagram_slot_id("spec", "source")
        assert a == b

    def test_different_source_different_id(self):
        from scripts.diagram_generator import _compute_diagram_slot_id
        a = _compute_diagram_slot_id("spec", "source1")
        b = _compute_diagram_slot_id("spec", "source2")
        assert a != b

    def test_hash_length_12(self):
        from scripts.diagram_generator import _compute_diagram_slot_id
        result = _compute_diagram_slot_id("spec", "source")
        hash_part = result.split("-", 2)[2]  # diag-spec-HASH
        assert len(hash_part) == 12
