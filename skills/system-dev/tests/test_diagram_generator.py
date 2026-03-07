"""Tests for diagram generation: schema validation, registry, D2 and Mermaid engines."""

import json
import os
import random
import tempfile

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


# ===========================================================================
# Task 1 (08-02g): diagram_hint on view-spec schema and BUILTIN_SPECS
# ===========================================================================

class TestDiagramHint:
    """Test diagram_hint field on view-spec.json schema and BUILTIN_SPECS."""

    def _load_view_spec_schema(self) -> dict:
        schema_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "schemas", "view-spec.json"
        )
        with open(schema_path) as f:
            return json.load(f)

    def test_schema_accepts_structural_hint(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
            "diagram_hint": "structural",
        }
        jsonschema.validate(spec, schema)

    def test_schema_accepts_behavioral_hint(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
            "diagram_hint": "behavioral",
        }
        jsonschema.validate(spec, schema)

    def test_schema_accepts_no_hint_backward_compatible(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        jsonschema.validate(spec, schema)

    def test_schema_rejects_invalid_hint(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
            "diagram_hint": "invalid",
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(spec, schema)

    def test_system_overview_has_structural_hint(self):
        from scripts.view_assembler import BUILTIN_SPECS
        assert BUILTIN_SPECS["system-overview"].get("diagram_hint") == "structural"

    def test_traceability_chain_has_behavioral_hint(self):
        from scripts.view_assembler import BUILTIN_SPECS
        assert BUILTIN_SPECS["traceability-chain"].get("diagram_hint") == "behavioral"

    def test_component_detail_has_structural_hint(self):
        from scripts.view_assembler import BUILTIN_SPECS
        assert BUILTIN_SPECS["component-detail"].get("diagram_hint") == "structural"

    def test_interface_map_has_structural_hint(self):
        from scripts.view_assembler import BUILTIN_SPECS
        assert BUILTIN_SPECS["interface-map"].get("diagram_hint") == "structural"

    def test_gap_report_has_no_hint(self):
        from scripts.view_assembler import BUILTIN_SPECS
        assert "diagram_hint" not in BUILTIN_SPECS["gap-report"]


# ===========================================================================
# Task 2 (08-02g): generate_diagram() orchestration integration tests
# ===========================================================================

def _setup_workspace(tmp_path):
    """Create a minimal workspace with registry dirs, schemas, and component slots."""
    workspace = tmp_path / ".system-dev"
    workspace.mkdir()
    registry = workspace / "registry"
    registry.mkdir()

    # Create all required registry subdirectories
    for subdir in [
        "components", "interfaces", "contracts", "diagram",
        "requirement-refs", "needs", "requirements", "sources",
        "assumptions", "traceability-links", "component-proposals",
        "interface-proposals", "contract-proposals",
        "traceability-graphs", "impact-analyses",
    ]:
        (registry / subdir).mkdir()

    # Copy schemas dir
    schemas_src = os.path.join(os.path.dirname(__file__), os.pardir, "schemas")
    schemas_dir = str(tmp_path / "schemas")
    import shutil
    shutil.copytree(schemas_src, schemas_dir)

    # Write an empty index
    index_path = workspace / "index.json"
    index_path.write_text(json.dumps({
        "schema_version": "1.0.0",
        "updated_at": "",
        "slots": {},
    }))

    return str(workspace), schemas_dir


def _create_component_slot(api, name="Auth Service", slot_id="comp-a0b1c2d3e4f5"):
    """Ingest a minimal component slot."""
    return api.ingest(
        slot_id, "component",
        {"name": name, "description": f"{name} component"},
        agent_id="test",
    )


class TestGenerateDiagramOrchestration:
    """Integration tests for generate_diagram() orchestration."""

    def test_calls_assemble_view_and_returns_result(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert "source" in result
        assert "slot_id" in result
        assert "status" in result
        assert len(result["source"]) > 0

    def test_format_override_d2(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "behavioral",  # hint says mermaid
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir, format_override="d2")
        assert result["format"] == "d2"
        assert "# Diagram:" in result["source"]  # D2 comment style

    def test_format_override_mermaid(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "structural",  # hint says d2
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir, format_override="mermaid")
        assert result["format"] == "mermaid"
        assert "%% Diagram:" in result["source"]  # Mermaid comment style

    def test_structural_hint_resolves_to_d2(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["format"] == "d2"
        assert result["diagram_type"] == "structural"

    def test_behavioral_hint_resolves_to_mermaid(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "behavioral",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["format"] == "mermaid"
        assert result["diagram_type"] == "behavioral"

    def test_no_hint_no_override_raises_valueerror(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "gap-report",
            "description": "Test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        with pytest.raises(ValueError, match="No diagram_hint"):
            generate_diagram(api, spec, workspace, schemas_dir)

    def test_writes_diagram_slot_via_ingest(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["status"] in ("created", "updated")

        # Verify slot was actually written
        slot = api.read(result["slot_id"])
        assert slot is not None
        assert slot["slot_type"] == "diagram"

    def test_content_hash_slot_id(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["slot_id"].startswith("diag-system-overview-")

    def test_unchanged_when_slot_already_exists(self, tmp_path):
        """When slot with same content-hash ID already exists, return unchanged.

        Uses unittest.mock to patch api.read to return a non-None value
        for the computed slot_id, triggering the early-return path.
        """
        from unittest.mock import patch
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }

        # First call creates the slot normally
        result1 = generate_diagram(api, spec, workspace, schemas_dir)
        assert result1["status"] == "created"

        # Patch api.read to always return a fake slot (simulating existing slot)
        original_read = api.read
        def patched_read(slot_id):
            return {"slot_id": slot_id, "exists": True}
        api.read = patched_read

        try:
            result2 = generate_diagram(api, spec, workspace, schemas_dir)
            assert result2["status"] == "unchanged"
        finally:
            api.read = original_read

    def test_only_diagram_type_slots_written_diag09(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        # Record pre-existing component slots
        pre_components = api.query("component")
        pre_comp_versions = {s["slot_id"]: s["version"] for s in pre_components}

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        generate_diagram(api, spec, workspace, schemas_dir)

        # Verify component slots unchanged (DIAG-09)
        post_components = api.query("component")
        post_comp_versions = {s["slot_id"]: s["version"] for s in post_components}
        assert pre_comp_versions == post_comp_versions

    def test_populates_all_diagram_schema_fields(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        slot = api.read(result["slot_id"])
        assert slot is not None
        for field in [
            "format", "diagram_type", "source", "source_view_spec",
            "source_snapshot_id", "slot_count", "gap_count",
        ]:
            assert field in slot, f"Missing field: {field}"

    def test_literal_d2_hint_produces_d2(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "d2",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["format"] == "d2"

    def test_literal_mermaid_hint_produces_mermaid(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "test-spec",
            "description": "Test",
            "diagram_hint": "mermaid",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["format"] == "mermaid"

    def test_returns_dict_with_required_keys(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert "source" in result
        assert "slot_id" in result
        assert "status" in result

    def test_empty_view_produces_valid_diagram(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        # No slots created - view will have gaps only

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["status"] in ("created", "updated")
        assert len(result["source"]) > 0

    def test_no_slots_still_produces_valid_diagram(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)

        spec = {
            "name": "minimal",
            "description": "Test",
            "diagram_hint": "behavioral",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        assert result["status"] in ("created", "updated")

    def test_schema_validation_before_write(self, tmp_path):
        from scripts.diagram_generator import generate_diagram
        from scripts.registry import SlotAPI
        workspace, schemas_dir = _setup_workspace(tmp_path)
        api = SlotAPI(workspace, schemas_dir)
        _create_component_slot(api)

        spec = {
            "name": "system-overview",
            "description": "Test",
            "diagram_hint": "structural",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
        }
        result = generate_diagram(api, spec, workspace, schemas_dir)
        # If we got here without error, schema validation passed
        # Verify the stored slot passes diagram schema
        slot = api.read(result["slot_id"])
        schema_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "schemas", "diagram.json"
        )
        with open(schema_path) as f:
            diagram_schema = json.load(f)
        jsonschema.validate(slot, diagram_schema)


# ===========================================================================
# Phase 09-01: Template loading tests
# ===========================================================================

class TestTemplateLoading:
    """Test _load_template() template resolution from manifest."""

    def test_load_template_d2_structural(self):
        from scripts.diagram_generator import _load_template
        template = _load_template(None, "d2", "structural")
        assert template is not None

    def test_load_template_mermaid_behavioral(self):
        from scripts.diagram_generator import _load_template
        template = _load_template(None, "mermaid", "behavioral")
        assert template is not None

    def test_load_template_explicit_name(self):
        from scripts.diagram_generator import _load_template
        template = _load_template("d2-structural", "d2", "structural")
        assert template is not None

    def test_load_template_user_override(self):
        from scripts.diagram_generator import _load_template
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create user override template
            tpl_dir = os.path.join(tmpdir, "templates")
            os.makedirs(tpl_dir)
            override_content = "# OVERRIDE {{ spec_name }}"
            with open(os.path.join(tpl_dir, "d2-structural.j2"), "w") as f:
                f.write(override_content)

            template = _load_template(None, "d2", "structural", workspace_root=tmpdir)
            rendered = template.render(spec_name="test")
            assert "OVERRIDE" in rendered

    def test_load_template_missing_raises(self):
        from scripts.diagram_generator import _load_template
        with pytest.raises(ValueError, match="No template found"):
            _load_template("nonexistent-template", "svg", "unknown")


# ===========================================================================
# Phase 09-01: Determinism tests (DIAG-08)
# ===========================================================================

class TestDeterminism:
    """Test deterministic output from diagram generators."""

    def test_determinism_d2(self):
        from scripts.diagram_generator import generate_d2
        view = _make_view()
        out1 = generate_d2(view)
        out2 = generate_d2(view)
        assert out1 == out2

    def test_determinism_mermaid(self):
        from scripts.diagram_generator import generate_mermaid
        view = _make_view()
        out1 = generate_mermaid(view)
        out2 = generate_mermaid(view)
        assert out1 == out2

    def test_determinism_with_shuffled_input(self):
        """Build view with edges/slots in random order, verify identical output."""
        from scripts.diagram_generator import generate_d2, generate_mermaid

        slots = [
            {"slot_id": f"comp-{c}", "slot_type": "component",
             "name": f"Component {c}", "version": 1}
            for c in ["charlie", "alpha", "bravo"]
        ]
        edges = [
            {"source_id": "comp-charlie", "target_id": "comp-alpha",
             "relationship_type": "uses"},
            {"source_id": "comp-alpha", "target_id": "comp-bravo",
             "relationship_type": "calls"},
            {"source_id": "comp-bravo", "target_id": "comp-charlie",
             "relationship_type": "depends"},
        ]

        # Shuffle multiple times and verify identical output
        outputs_d2 = set()
        outputs_mermaid = set()
        for _ in range(5):
            shuffled_slots = list(slots)
            shuffled_edges = list(edges)
            random.shuffle(shuffled_slots)
            random.shuffle(shuffled_edges)
            view = _make_view(
                sections=[{"slot_type": "component", "slots": shuffled_slots}],
                edges=shuffled_edges,
            )
            outputs_d2.add(generate_d2(view))
            outputs_mermaid.add(generate_mermaid(view))

        assert len(outputs_d2) == 1, "D2 output should be identical regardless of input order"
        assert len(outputs_mermaid) == 1, "Mermaid output should be identical regardless of input order"


# ===========================================================================
# Phase 09-01: Template context tests
# ===========================================================================

class TestBuildTemplateContext:
    """Test _build_template_context() sorting and convenience vars."""

    def test_sorts_sections_by_slot_type(self):
        from scripts.diagram_generator import _build_template_context
        view = _make_view(sections=[
            {"slot_type": "interface", "slots": [
                {"slot_id": "intf-a", "name": "A", "version": 1}
            ]},
            {"slot_type": "component", "slots": [
                {"slot_id": "comp-a", "name": "A", "version": 1}
            ]},
        ])
        ctx = _build_template_context(view)
        types = [s["slot_type"] for s in ctx["sections"]]
        assert types == sorted(types)

    def test_sorts_edges(self):
        from scripts.diagram_generator import _build_template_context
        view = _make_view(edges=[
            {"source_id": "z", "target_id": "a", "relationship_type": "r1"},
            {"source_id": "a", "target_id": "b", "relationship_type": "r2"},
        ])
        ctx = _build_template_context(view)
        assert ctx["edges"][0]["source_id"] == "a"
        assert ctx["edges"][1]["source_id"] == "z"

    def test_sorts_gaps(self):
        from scripts.diagram_generator import _build_template_context
        view = _make_view(gaps=[
            {"scope_pattern": "*", "slot_type": "interface", "severity": "warning",
             "reason": "gap1"},
            {"scope_pattern": "*", "slot_type": "component", "severity": "error",
             "reason": "gap2"},
        ])
        ctx = _build_template_context(view)
        assert ctx["gaps"][0]["slot_type"] == "component"
        assert ctx["gaps"][1]["slot_type"] == "interface"


# ===========================================================================
# Phase 09-01: Schema tests for new fields
# ===========================================================================

class TestSchemaNewFields:
    """Test schema updates for new fields added in 09-01."""

    def _load_view_spec_schema(self) -> dict:
        schema_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "schemas", "view-spec.json"
        )
        with open(schema_path) as f:
            return json.load(f)

    def test_diagram_schema_accepts_elapsed_ms(self):
        schema = _load_schema()
        slot = _make_diagram_slot(generation_elapsed_ms=42.5)
        jsonschema.validate(slot, schema)  # should not raise

    def test_view_spec_schema_accepts_abstraction_level(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
            "abstraction_level": "system",
        }
        jsonschema.validate(spec, schema)

    def test_view_spec_schema_accepts_diagram_template(self):
        schema = self._load_view_spec_schema()
        spec = {
            "name": "test",
            "description": "test",
            "scope_patterns": [{"pattern": "component:*", "slot_type": "component"}],
            "diagram_template": "d2-structural",
        }
        jsonschema.validate(spec, schema)


# ===========================================================================
# Phase 09-01: Migration parity test
# ===========================================================================

class TestMigrationParity:
    """Verify template output structurally matches expectations."""

    def test_template_output_matches_legacy(self):
        """Build representative view and verify template output structure."""
        from scripts.diagram_generator import generate_d2, generate_mermaid

        view = _make_view(
            sections=[
                {
                    "slot_type": "component",
                    "slots": [
                        {"slot_id": "comp-auth", "slot_type": "component",
                         "name": "Auth Service", "version": 1},
                        {"slot_id": "comp-db", "slot_type": "component",
                         "name": "Database", "version": 1},
                    ],
                },
                {
                    "slot_type": "interface",
                    "slots": [
                        {"slot_id": "intf-api", "slot_type": "interface",
                         "name": "REST API", "version": 1},
                    ],
                },
                {
                    "slot_type": "unlinked",
                    "slots": [
                        {"slot_id": "intf-orphan", "slot_type": "interface",
                         "name": "Orphan", "version": 1},
                    ],
                },
            ],
            edges=[
                {"source_id": "comp-auth", "target_id": "intf-api",
                 "relationship_type": "component_interface"},
                {"source_id": "comp-db", "target_id": "comp-auth",
                 "relationship_type": "dependency"},
            ],
            gaps=[
                {"scope_pattern": "contract:*", "slot_type": "contract",
                 "severity": "warning", "reason": "No contracts",
                 "suggestion": "Add contracts."},
                {"scope_pattern": "requirement:*", "slot_type": "requirement",
                 "severity": "error", "reason": "Missing reqs",
                 "suggestion": "Define requirements."},
            ],
        )

        # D2 structural checks
        d2 = generate_d2(view)
        assert "# Diagram: system-overview (structural)" in d2
        assert "# Components" in d2
        assert 'comp_auth: "Auth Service"' in d2
        assert 'comp_db: "Database"' in d2
        assert "shape: rectangle" in d2
        assert "# Interfaces" in d2
        assert 'intf_api: "REST API"' in d2
        assert 'Unlinked: "Unlinked"' in d2
        assert "# Connections" in d2
        assert "comp_auth -> intf_api: component_interface" in d2
        assert "# Gap placeholders" in d2
        assert "[GAP] contract: No contracts" in d2
        assert "[GAP] requirement: Missing reqs" in d2
        assert "stroke-dash: 5" in d2
        assert "#e6a117" in d2  # warning color
        assert "#dc3545" in d2  # error color

        # Mermaid behavioral checks
        mermaid = generate_mermaid(view)
        assert "%% Diagram: system-overview (behavioral)" in mermaid
        assert "graph" in mermaid
        assert "%% Nodes" in mermaid
        assert 'comp_auth["Auth Service"]' in mermaid
        assert 'comp_db["Database"]' in mermaid
        assert 'intf_api["REST API"]' in mermaid
        assert ':::unlinked' in mermaid
        assert "%% Edges" in mermaid
        assert "-->|component_interface|" in mermaid
        assert "%% Gap placeholders" in mermaid
        assert "classDef gapWarning" in mermaid
        assert "classDef gapError" in mermaid
        assert "stroke-dasharray: 5 5" in mermaid
        assert "classDef unlinked" in mermaid
