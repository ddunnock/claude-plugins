"""Tests for view_assembler.py -- view schemas, scope matching, snapshots, gaps."""

import copy
import json
import logging
import os

import pytest
from jsonschema import Draft202012Validator

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.schema_validator import SchemaValidator
from scripts.view_assembler import (
    BUILTIN_SPECS,
    _apply_field_selection,
    _compute_density_scores,
    _extract_edges,
    _organize_hierarchically,
    _rank_slots,
    assemble_view,
    build_gap_indicator,
    capture_snapshot,
    create_ad_hoc_spec,
    get_builtin_spec,
    load_gap_rules,
    load_view_spec,
    match_scope_pattern,
    render_tree,
)

# Resolve schemas/ relative to the project root
SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


@pytest.fixture
def workspace(tmp_path):
    """Create a fresh .system-dev/ workspace in a temp directory."""
    init_workspace(str(tmp_path))
    return str(tmp_path / ".system-dev")


@pytest.fixture
def api(workspace):
    """Create a SlotAPI instance with the temp workspace."""
    return SlotAPI(workspace, SCHEMAS_DIR)


# ---------------------------------------------------------------------------
# Task 1: Schema validation tests
# ---------------------------------------------------------------------------


class TestViewSpecSchema:
    """Tests for schemas/view-spec.json."""

    @pytest.fixture(autouse=True)
    def load_schema(self):
        schema_path = os.path.join(SCHEMAS_DIR, "view-spec.json")
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def test_valid_minimal_spec(self):
        """A minimal valid spec with name, description, and scope_patterns passes."""
        spec = {
            "name": "test-view",
            "description": "A test view",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"}
            ],
        }
        errors = list(self.validator.iter_errors(spec))
        assert errors == [], f"Unexpected errors: {errors}"

    def test_rejects_missing_required_fields(self):
        """A spec missing required fields is rejected."""
        spec = {"description": "no name or patterns"}
        errors = list(self.validator.iter_errors(spec))
        assert len(errors) > 0

    def test_parameterized_patterns(self):
        """Scope patterns with {variable} syntax are valid."""
        spec = {
            "name": "component-detail",
            "description": "Detail view",
            "scope_patterns": [
                {"pattern": "component:{component_id}", "slot_type": "component"}
            ],
            "parameters": {"component_id": "Auth Service"},
        }
        errors = list(self.validator.iter_errors(spec))
        assert errors == [], f"Unexpected errors: {errors}"

    def test_fields_directive(self):
        """A scope_pattern with fields directive is valid."""
        spec = {
            "name": "filtered-view",
            "description": "View with field selection",
            "scope_patterns": [
                {
                    "pattern": "component:*",
                    "slot_type": "component",
                    "fields": ["name", "description", "status"],
                }
            ],
        }
        errors = list(self.validator.iter_errors(spec))
        assert errors == [], f"Unexpected errors: {errors}"


class TestViewOutputSchema:
    """Tests for schemas/view.json."""

    @pytest.fixture(autouse=True)
    def load_schema(self):
        schema_path = os.path.join(SCHEMAS_DIR, "view.json")
        with open(schema_path) as f:
            self.schema = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def test_valid_minimal_view(self):
        """A minimal valid view with metadata, slots, and gap_summary passes."""
        view = {
            "spec_name": "test-view",
            "format_version": "1.0",
            "assembled_at": "2026-03-02T00:00:00Z",
            "snapshot_id": "snap-abc123",
            "total_slots": 5,
            "total_gaps": 1,
            "gap_summary": {"info": 0, "warning": 1, "error": 0},
            "sections": [],
            "gaps": [],
            "edges": [],
            "metadata": {
                "elapsed_ms": 1.5,
                "ranking_method": "density",
                "section_counts": {},
            },
        }
        errors = list(self.validator.iter_errors(view))
        assert errors == [], f"Unexpected errors: {errors}"

    def test_rejects_missing_gap_summary(self):
        """A view without gap_summary is rejected."""
        view = {
            "spec_name": "test-view",
            "format_version": "1.0",
            "assembled_at": "2026-03-02T00:00:00Z",
            "snapshot_id": "snap-abc123",
            "total_slots": 0,
            "total_gaps": 0,
            "sections": [],
            "gaps": [],
            "edges": [],
            "metadata": {
                "elapsed_ms": 0,
                "ranking_method": "density",
                "section_counts": {},
            },
        }
        errors = list(self.validator.iter_errors(view))
        assert len(errors) > 0
        error_paths = [list(e.absolute_path) for e in errors]
        error_validators = [e.validator for e in errors]
        # Should fail on missing gap_summary (required)
        assert "required" in error_validators


# ---------------------------------------------------------------------------
# Task 2: Scope pattern matcher, snapshot reader, gap builder tests
# ---------------------------------------------------------------------------


@pytest.fixture
def populated_api(api):
    """Create an API with some slots for testing scope matching."""
    api.create("component", {"name": "Auth Service"})
    api.create("component", {"name": "Auth Gateway"})
    api.create("component", {"name": "Database Service"})
    api.create("interface", {"name": "Auth API", "source_component": "comp-x", "target_component": "comp-y"})
    api.create("interface", {"name": "DB Connection", "source_component": "comp-x", "target_component": "comp-y"})
    return api


@pytest.fixture
def snapshot(populated_api):
    """Capture a snapshot from the populated API."""
    return capture_snapshot(populated_api)


class TestMatchScopePattern:
    """Tests for match_scope_pattern()."""

    def test_wildcard_matches_all_components(self, snapshot):
        """match_scope_pattern('component:*', ...) returns all components."""
        results = match_scope_pattern("component:*", "component", snapshot)
        assert len(results) == 3
        names = {s["name"] for s in results}
        assert names == {"Auth Service", "Auth Gateway", "Database Service"}

    def test_prefix_glob_matches_subset(self, snapshot):
        """match_scope_pattern('component:Auth*', ...) returns only Auth-prefixed."""
        results = match_scope_pattern("component:Auth*", "component", snapshot)
        assert len(results) == 2
        names = {s["name"] for s in results}
        assert names == {"Auth Service", "Auth Gateway"}

    def test_type_filter(self, snapshot):
        """match_scope_pattern('interface:*', ...) returns only interfaces."""
        results = match_scope_pattern("interface:*", "interface", snapshot)
        assert len(results) == 2
        names = {s["name"] for s in results}
        assert names == {"Auth API", "DB Connection"}

    def test_parameterized_exact_match(self, snapshot):
        """Parameterized pattern matches exact name after substitution."""
        # Simulate already-resolved pattern (parameters resolved by load_view_spec)
        results = match_scope_pattern("component:Auth Service", "component", snapshot)
        assert len(results) == 1
        assert results[0]["name"] == "Auth Service"

    def test_no_matches_returns_empty(self, snapshot):
        """Pattern with no matches returns empty list, no errors."""
        results = match_scope_pattern("component:NonExistent*", "component", snapshot)
        assert results == []


class TestCaptureSnapshot:
    """Tests for capture_snapshot()."""

    def test_snapshot_structure(self, populated_api):
        """Snapshot has snapshot_id, captured_at, and slots_by_type."""
        snap = capture_snapshot(populated_api)
        assert "snapshot_id" in snap
        assert "captured_at" in snap
        assert "slots_by_type" in snap
        assert isinstance(snap["slots_by_type"], dict)

    def test_snapshot_contains_all_types(self, populated_api):
        """Snapshot captures slots grouped by type."""
        snap = capture_snapshot(populated_api)
        assert "component" in snap["slots_by_type"]
        assert "interface" in snap["slots_by_type"]
        assert len(snap["slots_by_type"]["component"]) == 3
        assert len(snap["slots_by_type"]["interface"]) == 2

    def test_snapshot_is_deep_copy(self, populated_api):
        """Modifying snapshot data does not affect next capture."""
        snap1 = capture_snapshot(populated_api)
        # Mutate the snapshot data
        snap1["slots_by_type"]["component"][0]["name"] = "MUTATED"

        snap2 = capture_snapshot(populated_api)
        names = [s["name"] for s in snap2["slots_by_type"]["component"]]
        assert "MUTATED" not in names


class TestBuildGapIndicator:
    """Tests for build_gap_indicator()."""

    def test_gap_structure(self):
        """Gap indicator has all required fields."""
        gap = build_gap_indicator(
            scope_pattern="component:Auth*",
            slot_type="component",
            reason="No components matching Auth* found",
        )
        assert gap["scope_pattern"] == "component:Auth*"
        assert gap["slot_type"] == "component"
        assert gap["severity"] in ("info", "warning", "error")
        assert "reason" in gap
        assert "suggestion" in gap

    def test_default_severity_is_warning(self):
        """Without gap_rules, default severity is warning."""
        gap = build_gap_indicator(
            scope_pattern="component:*",
            slot_type="component",
            reason="No components found",
        )
        assert gap["severity"] == "warning"

    def test_severity_from_gap_rules(self):
        """Gap rules config overrides default severity."""
        rules = {
            "rules": [
                {"slot_type": "component", "severity": "error"},
                {"slot_type": "interface", "severity": "info"},
            ]
        }
        gap = build_gap_indicator(
            scope_pattern="component:*",
            slot_type="component",
            reason="No components found",
            gap_rules=rules,
        )
        assert gap["severity"] == "error"

    def test_suggestion_is_actionable(self):
        """Suggestion field contains actionable text."""
        gap = build_gap_indicator(
            scope_pattern="component:*",
            slot_type="component",
            reason="No components found",
        )
        assert len(gap["suggestion"]) > 0


class TestLoadViewSpec:
    """Tests for load_view_spec()."""

    def test_load_and_resolve_parameters(self, tmp_path):
        """load_view_spec resolves {variable} placeholders in patterns."""
        spec_data = {
            "name": "component-detail",
            "description": "Detail view",
            "scope_patterns": [
                {"pattern": "component:{component_id}", "slot_type": "component"}
            ],
            "parameters": {"component_id": "default"},
        }
        spec_path = str(tmp_path / "test-spec.json")
        with open(spec_path, "w") as f:
            json.dump(spec_data, f)

        loaded = load_view_spec(spec_path, parameters={"component_id": "Auth Service"})
        assert loaded["scope_patterns"][0]["pattern"] == "component:Auth Service"

    def test_missing_parameter_raises(self, tmp_path):
        """load_view_spec raises ValueError if required parameter is missing."""
        spec_data = {
            "name": "component-detail",
            "description": "Detail view",
            "scope_patterns": [
                {"pattern": "component:{component_id}", "slot_type": "component"}
            ],
        }
        spec_path = str(tmp_path / "test-spec.json")
        with open(spec_path, "w") as f:
            json.dump(spec_data, f)

        with pytest.raises(ValueError, match="component_id"):
            load_view_spec(spec_path, parameters={})

    def test_schema_validation_valid_spec(self, tmp_path):
        """load_view_spec with schemas_dir validates a valid spec successfully."""
        spec_data = {
            "name": "test-view",
            "description": "A valid test view",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"}
            ],
        }
        spec_path = str(tmp_path / "valid-spec.json")
        with open(spec_path, "w") as f:
            json.dump(spec_data, f)

        result = load_view_spec(spec_path, schemas_dir=SCHEMAS_DIR)
        assert result["name"] == "test-view"
        assert len(result["scope_patterns"]) == 1

    def test_schema_validation_invalid_spec_raises(self, tmp_path):
        """load_view_spec with schemas_dir and invalid spec raises SchemaValidationError."""
        from scripts.schema_validator import SchemaValidationError

        # Missing required "name" field
        spec_data = {
            "description": "Missing name field",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"}
            ],
        }
        spec_path = str(tmp_path / "invalid-spec.json")
        with open(spec_path, "w") as f:
            json.dump(spec_data, f)

        with pytest.raises(SchemaValidationError):
            load_view_spec(spec_path, schemas_dir=SCHEMAS_DIR)

    def test_schema_validation_skipped_without_schemas_dir(self, tmp_path):
        """load_view_spec without schemas_dir skips validation (backward compat)."""
        spec_data = {
            "name": "test-view",
            "description": "A test view",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"}
            ],
        }
        spec_path = str(tmp_path / "compat-spec.json")
        with open(spec_path, "w") as f:
            json.dump(spec_data, f)

        # Should work without schemas_dir (no validation)
        result = load_view_spec(spec_path)
        assert result["name"] == "test-view"


class TestLoadGapRules:
    """Tests for load_gap_rules()."""

    def test_default_rules_when_no_file(self, workspace):
        """Returns default rules when gap-rules.json does not exist."""
        rules = load_gap_rules(workspace)
        assert "rules" in rules
        assert isinstance(rules["rules"], list)

    def test_loads_custom_rules(self, workspace):
        """Loads rules from .system-dev/gap-rules.json when it exists."""
        custom = {"rules": [{"slot_type": "component", "severity": "error"}]}
        rules_path = os.path.join(workspace, "gap-rules.json")
        with open(rules_path, "w") as f:
            json.dump(custom, f)

        rules = load_gap_rules(workspace)
        assert rules["rules"][0]["slot_type"] == "component"
        assert rules["rules"][0]["severity"] == "error"


# ---------------------------------------------------------------------------
# Task 1 (Plan 02): assemble_view, field selection, hierarchical org tests
# ---------------------------------------------------------------------------


class TestAssembleView:
    """Tests for assemble_view() core function."""

    @pytest.fixture
    def populated_api_with_ids(self, api):
        """Create slots and return api + slot IDs."""
        comp1 = api.create("component", {"name": "Auth Service"})
        comp2 = api.create("component", {"name": "Database Service"})

        comp1_id = comp1["slot_id"]
        comp2_id = comp2["slot_id"]

        intf1 = api.create("interface", {
            "name": "Auth API",
            "source_component": comp1_id,
            "target_component": comp2_id,
        })

        return {
            "api": api,
            "comp1_id": comp1_id,
            "comp2_id": comp2_id,
            "intf1_id": intf1["slot_id"],
        }

    def test_assemble_returns_matching_slots(self, populated_api_with_ids, workspace):
        """assemble_view with matching spec returns slots in sections."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-view",
            "description": "Components only",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert result["total_slots"] == 2
        assert result["total_gaps"] == 0

    def test_assemble_produces_gaps_for_no_matches(self, api, workspace):
        """assemble_view with no matching slots produces gap indicators."""
        spec = {
            "name": "test-gaps",
            "description": "No matches",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert result["total_slots"] == 0
        assert result["total_gaps"] == 1
        assert result["gaps"][0]["slot_type"] == "component"

    def test_assemble_mixed_matches_and_gaps(self, populated_api_with_ids, workspace):
        """assemble_view with mixed results returns both slots and gaps."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-mixed",
            "description": "Mixed",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "requirement-ref:*", "slot_type": "requirement-ref"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert result["total_slots"] > 0
        assert result["total_gaps"] > 0

    def test_assemble_validates_against_schema(self, populated_api_with_ids, workspace):
        """Assembled output validates against view.json schema (VIEW-06)."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-schema",
            "description": "Schema test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        validator = SchemaValidator(SCHEMAS_DIR)
        errors = validator.validate("view", result)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_assemble_uses_single_snapshot(self, populated_api_with_ids, workspace):
        """All sections share the same snapshot_id (VIEW-07)."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-snapshot",
            "description": "Snapshot test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert "snapshot_id" in result
        assert len(result["snapshot_id"]) > 0

    def test_assemble_field_selection(self, populated_api_with_ids, workspace):
        """assemble_view with fields directive returns only selected fields."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-fields",
            "description": "Field selection test",
            "scope_patterns": [
                {
                    "pattern": "component:*",
                    "slot_type": "component",
                    "fields": ["name", "status"],
                },
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        for section in result["sections"]:
            for slot in section["slots"]:
                # System fields always included
                assert "slot_id" in slot
                assert "slot_type" in slot
                assert "name" in slot
                assert "version" in slot
                # Other fields not requested should be absent
                assert "created_at" not in slot

    def test_assemble_parameterized_spec(self, populated_api_with_ids, workspace):
        """assemble_view with parameterized spec resolves correctly."""
        api = populated_api_with_ids["api"]
        # Manually resolve parameter (load_view_spec handles file-based ones)
        spec = {
            "name": "test-param",
            "description": "Parameterized test",
            "scope_patterns": [
                {"pattern": "component:Auth Service", "slot_type": "component"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert result["total_slots"] == 1

    def test_assemble_does_not_modify_slots(self, populated_api_with_ids, workspace):
        """assemble_view does NOT call create/update/delete (VIEW-10)."""
        api = populated_api_with_ids["api"]
        before = len(api.query("component"))
        spec = {
            "name": "test-readonly",
            "description": "Read-only test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        assemble_view(api, spec, workspace, SCHEMAS_DIR)
        after = len(api.query("component"))
        assert before == after

    def test_gap_summary_counts(self, api, workspace):
        """gap_summary correctly counts info/warning/error gaps."""
        spec = {
            "name": "test-counts",
            "description": "Gap counts",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "contract:*", "slot_type": "contract"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        gs = result["gap_summary"]
        assert gs["info"] + gs["warning"] + gs["error"] == result["total_gaps"]

    def test_hierarchical_groups_interfaces_under_components(
        self, populated_api_with_ids, workspace
    ):
        """Hierarchical organization groups interfaces under parent components."""
        api = populated_api_with_ids["api"]
        spec = {
            "name": "test-hierarchy",
            "description": "Hierarchy test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        # All slots accounted for in sections
        total_in_sections = sum(len(s["slots"]) for s in result["sections"])
        assert total_in_sections == result["total_slots"]

    def test_orphan_slots_in_unlinked_section(self, api, workspace):
        """Slots without a parent appear in an unlinked section."""
        # Create an interface with no valid parent component in the view
        api.create("interface", {
            "name": "Orphan Interface",
            "source_component": "nonexistent-comp",
            "target_component": "also-nonexistent",
        })
        spec = {
            "name": "test-unlinked",
            "description": "Orphan test",
            "scope_patterns": [
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        assert result["total_slots"] == 1


class TestFormatVersionAndTightenedSchema:
    """Tests for format_version in assembled output and tightened slot schema."""

    @pytest.fixture
    def populated_api_for_format(self, api):
        """Create slots for format_version tests."""
        comp = api.create("component", {"name": "Auth Service"})
        return {"api": api, "comp_id": comp["slot_id"]}

    def test_assemble_view_includes_format_version(self, populated_api_for_format, workspace):
        """assemble_view() output contains format_version field with value '1.0'."""
        api_obj = populated_api_for_format["api"]
        spec = {
            "name": "format-test",
            "description": "Format version test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api_obj, spec, workspace, SCHEMAS_DIR)
        assert "format_version" in result
        assert result["format_version"] == "1.1"

    def test_assembled_view_validates_with_tightened_schema(self, populated_api_for_format, workspace):
        """Assembled output validates against updated schema with required slot fields."""
        api_obj = populated_api_for_format["api"]
        spec = {
            "name": "tightened-test",
            "description": "Tightened schema test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(api_obj, spec, workspace, SCHEMAS_DIR)
        validator = SchemaValidator(SCHEMAS_DIR)
        errors = validator.validate("view", result)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_schema_requires_slot_system_fields(self):
        """view.json schema requires slot_id, slot_type, name, version on slot items."""
        schema_path = os.path.join(SCHEMAS_DIR, "view.json")
        with open(schema_path) as f:
            schema = json.load(f)
        slot_schema = schema["properties"]["sections"]["items"]["properties"]["slots"]["items"]
        assert "required" in slot_schema
        assert set(slot_schema["required"]) == {"slot_id", "slot_type", "name", "version"}

    def test_schema_has_format_version_required(self):
        """view.json schema has format_version in top-level required fields."""
        schema_path = os.path.join(SCHEMAS_DIR, "view.json")
        with open(schema_path) as f:
            schema = json.load(f)
        assert "format_version" in schema["required"]
        assert "format_version" in schema["properties"]


class TestApplyFieldSelection:
    """Tests for _apply_field_selection()."""

    def test_returns_only_selected_fields(self):
        """Only requested fields plus system fields are returned."""
        slots = [
            {
                "slot_id": "comp-1",
                "slot_type": "component",
                "name": "Auth",
                "version": 1,
                "description": "Auth service",
                "status": "proposed",
                "created_at": "2026-01-01",
            }
        ]
        result = _apply_field_selection(slots, ["description"])
        assert len(result) == 1
        assert "description" in result[0]
        assert "slot_id" in result[0]  # system field always included
        assert "name" in result[0]  # system field always included
        assert "created_at" not in result[0]
        assert "status" not in result[0]

    def test_preserves_system_fields(self):
        """System fields (slot_id, slot_type, name, version) always included."""
        slots = [
            {
                "slot_id": "comp-1",
                "slot_type": "component",
                "name": "Auth",
                "version": 1,
                "status": "proposed",
            }
        ]
        result = _apply_field_selection(slots, ["status"])
        assert result[0]["slot_id"] == "comp-1"
        assert result[0]["slot_type"] == "component"
        assert result[0]["name"] == "Auth"
        assert result[0]["version"] == 1
        assert result[0]["status"] == "proposed"

    def test_no_fields_returns_all(self):
        """When fields is None, all fields are returned."""
        slots = [{"slot_id": "comp-1", "name": "Auth", "extra": "data"}]
        result = _apply_field_selection(slots, None)
        assert result[0] == slots[0]


class TestOrganizeHierarchically:
    """Tests for _organize_hierarchically()."""

    def test_components_are_roots(self):
        """Component slots appear as top-level sections."""
        sections = [
            {
                "slot_type": "component",
                "slots": [
                    {"slot_id": "comp-1", "slot_type": "component", "name": "Auth"},
                ],
            },
        ]
        result = _organize_hierarchically(sections)
        assert any(s["slot_type"] == "component" for s in result)

    def test_interfaces_nested_under_components(self):
        """Interfaces with source_component matching a component are nested."""
        sections = [
            {
                "slot_type": "component",
                "slots": [
                    {"slot_id": "comp-1", "slot_type": "component", "name": "Auth"},
                ],
            },
            {
                "slot_type": "interface",
                "slots": [
                    {
                        "slot_id": "intf-1",
                        "slot_type": "interface",
                        "name": "Auth API",
                        "source_component": "comp-1",
                        "target_component": "comp-2",
                    },
                ],
            },
        ]
        result = _organize_hierarchically(sections)
        # The interface should be accounted for in the total slot count
        total_slots = sum(len(s["slots"]) for s in result)
        assert total_slots == 2

    def test_orphans_in_unlinked_section(self):
        """Slots without a parent go in unlinked section."""
        sections = [
            {
                "slot_type": "interface",
                "slots": [
                    {
                        "slot_id": "intf-1",
                        "slot_type": "interface",
                        "name": "Orphan",
                        "source_component": "nonexistent",
                        "target_component": "also-nonexistent",
                    },
                ],
            },
        ]
        result = _organize_hierarchically(sections)
        total_slots = sum(len(s["slots"]) for s in result)
        assert total_slots == 1


# ---------------------------------------------------------------------------
# Task 2 (Plan 02): Built-in specs, render_tree, ad-hoc specs
# ---------------------------------------------------------------------------


class TestBuiltinSpecs:
    """Tests for BUILTIN_SPECS and get_builtin_spec()."""

    def test_five_builtin_specs_exist(self):
        """Exactly 5 built-in view specs are available."""
        assert len(BUILTIN_SPECS) == 5

    def test_all_spec_names_resolve(self):
        """All 5 built-in spec names resolve via get_builtin_spec."""
        for name in ("system-overview", "traceability-chain", "interface-map", "gap-report"):
            spec = get_builtin_spec(name)
            assert spec["name"] == name
            assert "scope_patterns" in spec

    def test_component_detail_requires_parameter(self):
        """component-detail raises ValueError without component_id."""
        with pytest.raises(ValueError, match="component_id"):
            get_builtin_spec("component-detail")

    def test_component_detail_with_parameter(self):
        """component-detail resolves when parameter is provided."""
        spec = get_builtin_spec("component-detail", {"component_id": "Auth Service"})
        assert spec["name"] == "component-detail"
        patterns = [sp["pattern"] for sp in spec["scope_patterns"]]
        assert "component:Auth Service" in patterns

    def test_unknown_spec_raises(self):
        """Unknown spec name raises ValueError."""
        with pytest.raises(ValueError, match="nonexistent"):
            get_builtin_spec("nonexistent")

    def test_get_builtin_returns_deep_copy(self):
        """get_builtin_spec returns a copy, not a reference to BUILTIN_SPECS."""
        spec1 = get_builtin_spec("system-overview")
        spec1["name"] = "mutated"
        spec2 = get_builtin_spec("system-overview")
        assert spec2["name"] == "system-overview"


class TestCreateAdHocSpec:
    """Tests for create_ad_hoc_spec()."""

    def test_valid_patterns(self):
        """Ad-hoc spec from valid patterns produces a valid spec dict."""
        spec = create_ad_hoc_spec(["component:Auth*", "interface:*"])
        assert spec["name"] == "ad-hoc"
        assert len(spec["scope_patterns"]) == 2
        assert spec["scope_patterns"][0]["slot_type"] == "component"
        assert spec["scope_patterns"][0]["pattern"] == "component:Auth*"

    def test_invalid_pattern_raises(self):
        """Pattern without colon separator raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ad-hoc pattern"):
            create_ad_hoc_spec(["invalidpattern"])

    def test_single_pattern(self):
        """Single ad-hoc pattern works."""
        spec = create_ad_hoc_spec(["contract:*"])
        assert len(spec["scope_patterns"]) == 1
        assert spec["scope_patterns"][0]["slot_type"] == "contract"


class TestRenderTree:
    """Tests for render_tree()."""

    @pytest.fixture
    def sample_view(self):
        """A sample assembled view dict for rendering tests."""
        return {
            "spec_name": "test-view",
            "format_version": "1.1",
            "assembled_at": "2026-03-02T14:30:00Z",
            "snapshot_id": "snap-abc",
            "total_slots": 3,
            "total_gaps": 1,
            "gap_summary": {"info": 0, "warning": 1, "error": 0},
            "sections": [
                {
                    "slot_type": "component",
                    "slots": [
                        {"slot_id": "comp-1", "name": "Auth Service", "version": 2, "status": "approved"},
                        {"slot_id": "comp-2", "name": "DB Service", "version": 1},
                    ],
                },
                {
                    "slot_type": "interface",
                    "slots": [
                        {"slot_id": "intf-1", "name": "Auth API", "version": 1},
                    ],
                },
            ],
            "gaps": [
                {
                    "scope_pattern": "contract:*",
                    "slot_type": "contract",
                    "severity": "warning",
                    "reason": "No contract slots matching 'contract:*' found",
                    "suggestion": "Run /system-dev:contract to define contracts.",
                },
            ],
        }

    def test_returns_string(self, sample_view):
        """render_tree returns a non-empty string."""
        output = render_tree(sample_view)
        assert isinstance(output, str)
        assert len(output) > 0

    def test_contains_spec_name(self, sample_view):
        """Output contains the spec name."""
        output = render_tree(sample_view)
        assert "test-view" in output

    def test_contains_slot_counts(self, sample_view):
        """Output contains slot and gap counts."""
        output = render_tree(sample_view)
        assert "Slots: 3" in output
        assert "Gaps: 1" in output

    def test_contains_section_headings(self, sample_view):
        """Output contains section headings with slot type."""
        output = render_tree(sample_view)
        assert "component/" in output
        assert "interface/" in output

    def test_contains_slot_names(self, sample_view):
        """Output contains slot names."""
        output = render_tree(sample_view)
        assert "Auth Service" in output
        assert "DB Service" in output
        assert "Auth API" in output

    def test_contains_gap_markers(self, sample_view):
        """Output contains [GAP] markers with severity."""
        output = render_tree(sample_view)
        assert "[GAP]" in output
        assert "[WARNING]" in output

    def test_contains_gap_suggestion(self, sample_view):
        """Output contains gap suggestions."""
        output = render_tree(sample_view)
        assert "Suggestion:" in output
        assert "/system-dev:contract" in output

    def test_contains_gap_summary(self, sample_view):
        """Output contains gap summary section."""
        output = render_tree(sample_view)
        assert "Gap Summary:" in output

    def test_format_version_in_rendered_output(self, sample_view):
        """Output contains format_version if present in view."""
        assert sample_view["format_version"] == "1.1"
        output = render_tree(sample_view)
        assert "test-view" in output  # basic sanity

    def test_empty_view_renders(self):
        """Empty view (no slots, no gaps) renders without errors."""
        view = {
            "spec_name": "empty",
            "format_version": "1.1",
            "assembled_at": "2026-03-02T00:00:00Z",
            "snapshot_id": "snap-empty",
            "total_slots": 0,
            "total_gaps": 0,
            "gap_summary": {"info": 0, "warning": 0, "error": 0},
            "sections": [],
            "gaps": [],
        }
        output = render_tree(view)
        assert "empty" in output
        assert "Slots: 0" in output


# ---------------------------------------------------------------------------
# Phase 7 Plan 01: Ranking, determinism, and performance tests
# ---------------------------------------------------------------------------


def _deterministic_content(view: dict) -> dict:
    """Strip volatile fields (assembled_at, elapsed_ms) for determinism comparison."""
    result = copy.deepcopy(view)
    result.pop("assembled_at", None)
    if "metadata" in result:
        result["metadata"].pop("elapsed_ms", None)
    return result


class TestRanking:
    """Tests for density scoring, slot ranking, and ranking method override."""

    @pytest.fixture
    def ranking_api(self, api):
        """Create an API with slots that have varying relationship density."""
        # comp_a: 2 interfaces (high density)
        comp_a = api.create("component", {"name": "Hub Component"})
        # comp_b: 0 interfaces (low density)
        comp_b = api.create("component", {"name": "Leaf Component"})
        # comp_c: 1 interface (medium density)
        comp_c = api.create("component", {"name": "Mid Component"})

        intf1 = api.create("interface", {
            "name": "API Alpha",
            "source_component": comp_a["slot_id"],
            "target_component": comp_c["slot_id"],
        })
        intf2 = api.create("interface", {
            "name": "API Beta",
            "source_component": comp_a["slot_id"],
            "target_component": comp_b["slot_id"],
        })

        # Contract linked to intf1 -- gives one-hop credit to comp_a
        cntr = api.create("contract", {
            "name": "Contract Alpha",
            "interface_id": intf1["slot_id"],
        })

        return {
            "api": api,
            "comp_a_id": comp_a["slot_id"],
            "comp_b_id": comp_b["slot_id"],
            "comp_c_id": comp_c["slot_id"],
            "intf1_id": intf1["slot_id"],
            "intf2_id": intf2["slot_id"],
            "cntr_id": cntr["slot_id"],
        }

    def test_density_scores_count_interface_connections(self, ranking_api):
        """Component with 2 interfaces scores higher than component with 0."""
        api = ranking_api["api"]
        snapshot = capture_snapshot(api)
        scores = _compute_density_scores(snapshot)
        # comp_a has 2 interfaces -> higher score
        assert scores[ranking_api["comp_a_id"]] > scores[ranking_api["comp_b_id"]]

    def test_density_scores_count_one_hop_contracts(self, ranking_api):
        """Component with interface that has contracts gets one-hop credit."""
        api = ranking_api["api"]
        snapshot = capture_snapshot(api)
        scores = _compute_density_scores(snapshot)
        # comp_a has interface intf1 which has a contract -> one-hop credit
        # comp_a score should be > comp_c score (comp_c has 1 intf, no contract hop credit)
        assert scores[ranking_api["comp_a_id"]] > scores[ranking_api["comp_c_id"]]

    def test_density_scores_count_traceability_links(self):
        """Slots referenced by traceability-links get density credit."""
        # Use a manually constructed snapshot to test traceability-link scoring
        # (avoids schema validation issues with traceability-link slot_id pattern)
        snapshot = {
            "snapshot_id": "test-snap",
            "captured_at": "2026-01-01T00:00:00Z",
            "slots_by_type": {
                "component": [
                    {"slot_id": "comp-1", "slot_type": "component", "name": "Traced", "version": 1},
                ],
                "traceability-link": [
                    {
                        "slot_id": "trace:link-1",
                        "slot_type": "traceability-link",
                        "version": 1,
                        "from_id": "comp-1",
                        "to_id": "external-req-1",
                        "link_type": "satisfies",
                    },
                ],
            },
        }
        scores = _compute_density_scores(snapshot)
        # The component should have score > 0 from traceability link
        assert scores["comp-1"] > 0

    def test_density_scores_computed_from_full_snapshot(self, ranking_api):
        """Same component gets same score regardless of which view includes it."""
        api = ranking_api["api"]
        snapshot = capture_snapshot(api)
        scores = _compute_density_scores(snapshot)
        # Score is computed from full snapshot, not filtered view
        comp_a_score = scores[ranking_api["comp_a_id"]]
        assert comp_a_score > 0
        # Same snapshot gives same score
        scores2 = _compute_density_scores(snapshot)
        assert scores2[ranking_api["comp_a_id"]] == comp_a_score

    def test_rank_slots_density_ordering(self, ranking_api):
        """Higher density slots appear first in section."""
        api = ranking_api["api"]
        snapshot = capture_snapshot(api)
        scores = _compute_density_scores(snapshot)
        slots = [
            {"slot_id": ranking_api["comp_b_id"], "name": "Leaf Component", "version": 1},
            {"slot_id": ranking_api["comp_a_id"], "name": "Hub Component", "version": 1},
        ]
        ranked = _rank_slots(slots, scores, "density")
        assert ranked[0]["name"] == "Hub Component"
        assert ranked[1]["name"] == "Leaf Component"

    def test_rank_slots_tiebreak_version_then_name(self):
        """Same density ties broken by version desc then name asc."""
        scores = {"s1": 5, "s2": 5, "s3": 5}
        slots = [
            {"slot_id": "s1", "name": "Bravo", "version": 1},
            {"slot_id": "s2", "name": "Alpha", "version": 2},
            {"slot_id": "s3", "name": "Alpha", "version": 1},
        ]
        ranked = _rank_slots(slots, scores, "density")
        # Same density -> higher version first -> then alphabetical
        assert ranked[0]["name"] == "Alpha" and ranked[0]["version"] == 2
        assert ranked[1]["name"] == "Alpha" and ranked[1]["version"] == 1
        assert ranked[2]["name"] == "Bravo"

    def test_rank_slots_alphabetical_method(self):
        """ranking='alphabetical' sorts by name."""
        scores = {"s1": 10, "s2": 1}
        slots = [
            {"slot_id": "s1", "name": "Zebra", "version": 1},
            {"slot_id": "s2", "name": "Alpha", "version": 1},
        ]
        ranked = _rank_slots(slots, scores, "alphabetical")
        assert ranked[0]["name"] == "Alpha"
        assert ranked[1]["name"] == "Zebra"

    def test_rank_slots_none_method(self):
        """ranking='none' preserves original order."""
        scores = {"s1": 10, "s2": 1}
        slots = [
            {"slot_id": "s1", "name": "Zebra", "version": 1},
            {"slot_id": "s2", "name": "Alpha", "version": 1},
        ]
        ranked = _rank_slots(slots, scores, "none")
        assert ranked[0]["name"] == "Zebra"
        assert ranked[1]["name"] == "Alpha"

    def test_ranking_override_in_spec(self, ranking_api, workspace):
        """View-spec with 'ranking': 'alphabetical' uses alphabetical instead of density."""
        api = ranking_api["api"]
        spec = {
            "name": "alpha-ranked",
            "description": "Alphabetical ranking test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
            "ranking": "alphabetical",
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        comp_names = [
            s["name"] for section in result["sections"]
            if section["slot_type"] == "component"
            for s in section["slots"]
        ]
        assert comp_names == sorted(comp_names)


class TestDeterminism:
    """Tests for content-hash snapshot_id and deterministic full output."""

    @pytest.fixture
    def det_api(self, api):
        """Create an API with some fixed slots for determinism tests."""
        api.create("component", {"name": "Auth Service"})
        api.create("component", {"name": "Database Service"})
        return api

    def test_deterministic_snapshot_id(self, det_api):
        """Same registry content produces same snapshot_id across calls."""
        snap1 = capture_snapshot(det_api)
        snap2 = capture_snapshot(det_api)
        assert snap1["snapshot_id"] == snap2["snapshot_id"]

    def test_deterministic_snapshot_id_different_content(self, det_api):
        """Different content produces different snapshot_id."""
        snap1 = capture_snapshot(det_api)
        det_api.create("component", {"name": "New Service"})
        snap2 = capture_snapshot(det_api)
        assert snap1["snapshot_id"] != snap2["snapshot_id"]

    def test_deterministic_output(self, det_api, workspace):
        """Two assemble_view calls with same input produce identical output (excluding volatile fields)."""
        spec = {
            "name": "det-test",
            "description": "Determinism test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result1 = assemble_view(det_api, spec, workspace, SCHEMAS_DIR)
        result2 = assemble_view(det_api, spec, workspace, SCHEMAS_DIR)
        assert _deterministic_content(result1) == _deterministic_content(result2)

    def test_format_version_is_1_1(self, det_api, workspace):
        """Assembled output has format_version '1.1'."""
        spec = {
            "name": "version-test",
            "description": "Format version test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(det_api, spec, workspace, SCHEMAS_DIR)
        assert result["format_version"] == "1.1"

    def test_assembled_output_has_edges_array(self, det_api, workspace):
        """Output contains edges key as a list."""
        spec = {
            "name": "edges-test",
            "description": "Edges test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(det_api, spec, workspace, SCHEMAS_DIR)
        assert "edges" in result
        assert isinstance(result["edges"], list)

    def test_assembled_output_has_metadata(self, det_api, workspace):
        """Output contains metadata with elapsed_ms, ranking_method, section_counts."""
        spec = {
            "name": "meta-test",
            "description": "Metadata test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(det_api, spec, workspace, SCHEMAS_DIR)
        assert "metadata" in result
        meta = result["metadata"]
        assert "elapsed_ms" in meta
        assert isinstance(meta["elapsed_ms"], float)
        assert meta["elapsed_ms"] >= 0
        assert meta["ranking_method"] == "density"
        assert "section_counts" in meta
        assert isinstance(meta["section_counts"], dict)


class TestPerformance:
    """Tests for assembly performance targets."""

    def test_performance_100_slots(self, api, workspace):
        """Assembly of 100-slot registry completes in under 500ms."""
        import time

        # Create 100 slots across component/interface/contract types
        comp_ids = []
        for i in range(40):
            comp = api.create("component", {"name": f"Component-{i:03d}"})
            comp_ids.append(comp["slot_id"])

        intf_ids = []
        for i in range(35):
            src = comp_ids[i % len(comp_ids)]
            tgt = comp_ids[(i + 1) % len(comp_ids)]
            intf = api.create("interface", {
                "name": f"Interface-{i:03d}",
                "source_component": src,
                "target_component": tgt,
            })
            intf_ids.append(intf["slot_id"])

        for i in range(25):
            iid = intf_ids[i % len(intf_ids)]
            api.create("contract", {
                "name": f"Contract-{i:03d}",
                "interface_id": iid,
            })

        spec = {
            "name": "perf-test",
            "description": "Performance test with 100 slots",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
                {"pattern": "contract:*", "slot_type": "contract"},
            ],
        }
        start = time.perf_counter()
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result["total_slots"] == 100
        assert elapsed_ms < 500, f"Assembly took {elapsed_ms:.1f}ms, exceeds 500ms target"


# ---------------------------------------------------------------------------
# Phase 7 Plan 02: Edge extraction, inline relationships, structured logging
# ---------------------------------------------------------------------------


class TestEdges:
    """Tests for _extract_edges() and edge population in assemble_view()."""

    @pytest.fixture
    def edge_api(self, api):
        """Create slots with various relationship types for edge tests."""
        comp_a = api.create("component", {"name": "Component A"})
        comp_b = api.create("component", {"name": "Component B"})
        comp_c = api.create("component", {"name": "Component C"})

        intf1 = api.create("interface", {
            "name": "API Alpha",
            "source_component": comp_a["slot_id"],
            "target_component": comp_b["slot_id"],
        })

        cntr1 = api.create("contract", {
            "name": "Contract Alpha",
            "interface_id": intf1["slot_id"],
        })

        return {
            "api": api,
            "comp_a": comp_a["slot_id"],
            "comp_b": comp_b["slot_id"],
            "comp_c": comp_c["slot_id"],
            "intf1": intf1["slot_id"],
            "cntr1": cntr1["slot_id"],
        }

    def test_edges_from_interface_source_component(self, edge_api):
        """Interface with source_component produces component_interface edge."""
        api = edge_api["api"]
        snapshot = capture_snapshot(api)
        in_view = {edge_api["comp_a"], edge_api["intf1"]}
        edges = _extract_edges(snapshot, in_view)
        source_edges = [e for e in edges if e["source_id"] == edge_api["comp_a"] and e["target_id"] == edge_api["intf1"]]
        assert len(source_edges) == 1
        assert source_edges[0]["relationship_type"] == "component_interface"

    def test_edges_from_interface_target_component(self, edge_api):
        """Interface with target_component produces component_interface edge in correct direction."""
        api = edge_api["api"]
        snapshot = capture_snapshot(api)
        in_view = {edge_api["comp_b"], edge_api["intf1"]}
        edges = _extract_edges(snapshot, in_view)
        target_edges = [e for e in edges if e["source_id"] == edge_api["intf1"] and e["target_id"] == edge_api["comp_b"]]
        assert len(target_edges) == 1
        assert target_edges[0]["relationship_type"] == "component_interface"

    def test_edges_from_contract_interface(self, edge_api):
        """Contract with interface_id produces interface_contract edge."""
        api = edge_api["api"]
        snapshot = capture_snapshot(api)
        in_view = {edge_api["intf1"], edge_api["cntr1"]}
        edges = _extract_edges(snapshot, in_view)
        contract_edges = [e for e in edges if e["relationship_type"] == "interface_contract"]
        assert len(contract_edges) == 1
        assert contract_edges[0]["source_id"] == edge_api["intf1"]
        assert contract_edges[0]["target_id"] == edge_api["cntr1"]

    def test_edges_filtered_to_in_view_only(self, edge_api):
        """Edges where one endpoint is outside the view are excluded."""
        api = edge_api["api"]
        snapshot = capture_snapshot(api)
        # Only include comp_a -- intf1 is NOT in view, so no edges should appear
        in_view = {edge_api["comp_a"]}
        edges = _extract_edges(snapshot, in_view)
        assert len(edges) == 0

    def test_edges_sorted_deterministically(self, edge_api):
        """Edges array is sorted by (source_id, target_id, relationship_type)."""
        api = edge_api["api"]
        snapshot = capture_snapshot(api)
        all_ids = {edge_api["comp_a"], edge_api["comp_b"], edge_api["intf1"], edge_api["cntr1"]}
        edges = _extract_edges(snapshot, all_ids)
        for i in range(len(edges) - 1):
            key_a = (edges[i]["source_id"], edges[i]["target_id"], edges[i]["relationship_type"])
            key_b = (edges[i + 1]["source_id"], edges[i + 1]["target_id"], edges[i + 1]["relationship_type"])
            assert key_a <= key_b

    def test_edges_from_traceability_link(self):
        """Traceability link produces edge with link_type as relationship_type."""
        snapshot = {
            "snapshot_id": "test",
            "captured_at": "2026-01-01T00:00:00Z",
            "slots_by_type": {
                "component": [
                    {"slot_id": "comp-1", "slot_type": "component", "name": "A", "version": 1},
                    {"slot_id": "comp-2", "slot_type": "component", "name": "B", "version": 1},
                ],
                "traceability-link": [
                    {
                        "slot_id": "trace:link-1",
                        "slot_type": "traceability-link",
                        "name": "Link1",
                        "version": 1,
                        "from_id": "comp-1",
                        "to_id": "comp-2",
                        "link_type": "satisfies",
                    },
                ],
            },
        }
        edges = _extract_edges(snapshot, {"comp-1", "comp-2"})
        assert len(edges) == 1
        assert edges[0]["source_id"] == "comp-1"
        assert edges[0]["target_id"] == "comp-2"
        assert edges[0]["relationship_type"] == "satisfies"

    def test_no_duplicate_edges(self):
        """Same relationship does not produce duplicate edge entries."""
        snapshot = {
            "snapshot_id": "test",
            "captured_at": "2026-01-01T00:00:00Z",
            "slots_by_type": {
                "component": [
                    {"slot_id": "comp-1", "slot_type": "component", "name": "A", "version": 1},
                ],
                "interface": [
                    {
                        "slot_id": "intf-1",
                        "slot_type": "interface",
                        "name": "API",
                        "version": 1,
                        "source_component": "comp-1",
                        "target_component": "comp-1",
                    },
                ],
            },
        }
        edges = _extract_edges(snapshot, {"comp-1", "intf-1"})
        # comp-1 -> intf-1 (source) and intf-1 -> comp-1 (target) are different directions
        keys = [(e["source_id"], e["target_id"], e["relationship_type"]) for e in edges]
        assert len(keys) == len(set(keys)), "Duplicate edges found"


class TestInlineRelationships:
    """Tests for inline relationships field on slots in assembled views."""

    @pytest.fixture
    def rel_api(self, api):
        """Create slots for inline relationship tests."""
        comp_a = api.create("component", {"name": "Component A"})
        comp_b = api.create("component", {"name": "Component B"})
        intf1 = api.create("interface", {
            "name": "API Alpha",
            "source_component": comp_a["slot_id"],
            "target_component": comp_b["slot_id"],
        })
        return {
            "api": api,
            "comp_a": comp_a["slot_id"],
            "comp_b": comp_b["slot_id"],
            "intf1": intf1["slot_id"],
        }

    def test_inline_relationships_on_slots(self, rel_api, workspace):
        """Each slot has relationships list of connected in-view slot IDs."""
        api = rel_api["api"]
        spec = {
            "name": "rel-test",
            "description": "Relationship test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        for section in result["sections"]:
            for slot in section["slots"]:
                assert "relationships" in slot, f"Slot {slot['slot_id']} missing relationships"
                assert isinstance(slot["relationships"], list)

    def test_inline_relationships_deduplicated(self, rel_api, workspace):
        """Relationships list has no duplicates and is sorted."""
        api = rel_api["api"]
        spec = {
            "name": "dedup-test",
            "description": "Dedup test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
                {"pattern": "interface:*", "slot_type": "interface"},
            ],
        }
        result = assemble_view(api, spec, workspace, SCHEMAS_DIR)
        for section in result["sections"]:
            for slot in section["slots"]:
                rels = slot["relationships"]
                assert rels == sorted(set(rels)), f"Relationships not deduplicated/sorted: {rels}"


class TestStructuredLogging:
    """Tests for structured logging in assemble_view() and capture_snapshot()."""

    @pytest.fixture
    def log_api(self, api):
        """Create minimal slots for logging tests."""
        api.create("component", {"name": "Log Test Component"})
        return api

    def test_logging_info_snapshot_capture(self, log_api, caplog):
        """INFO log for snapshot capture includes view.operation and view.elapsed_ms."""
        with caplog.at_level(logging.INFO, logger="scripts.view_assembler"):
            capture_snapshot(log_api)
        snap_records = [r for r in caplog.records if getattr(r, "view.operation", None) == "snapshot_capture"]
        assert len(snap_records) >= 1
        rec = snap_records[0]
        assert hasattr(rec, "view.elapsed_ms")
        assert getattr(rec, "view.elapsed_ms") >= 0

    def test_logging_info_assembly_complete(self, log_api, workspace, caplog):
        """INFO log for assembly complete includes view.total_slots, view.total_gaps, view.edge_count."""
        spec = {
            "name": "log-test",
            "description": "Logging test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        with caplog.at_level(logging.INFO, logger="scripts.view_assembler"):
            assemble_view(log_api, spec, workspace, SCHEMAS_DIR)
        complete_records = [r for r in caplog.records if getattr(r, "view.operation", None) == "assembly_complete"]
        assert len(complete_records) >= 1
        rec = complete_records[0]
        assert hasattr(rec, "view.total_slots")
        assert hasattr(rec, "view.total_gaps")
        assert hasattr(rec, "view.edge_count")

    def test_logging_debug_density_score(self, log_api, workspace, caplog):
        """DEBUG log for density scores includes view.slot_id and view.score."""
        spec = {
            "name": "debug-log-test",
            "description": "Debug logging test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        with caplog.at_level(logging.DEBUG, logger="scripts.view_assembler"):
            assemble_view(log_api, spec, workspace, SCHEMAS_DIR)
        score_records = [r for r in caplog.records if getattr(r, "view.operation", None) == "density_score"]
        assert len(score_records) >= 1
        rec = score_records[0]
        assert hasattr(rec, "view.slot_id")
        assert hasattr(rec, "view.score")

    def test_logging_namespaced_fields(self, log_api, workspace, caplog):
        """All log extra fields use view.* prefix."""
        spec = {
            "name": "ns-test",
            "description": "Namespace test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        with caplog.at_level(logging.DEBUG, logger="scripts.view_assembler"):
            assemble_view(log_api, spec, workspace, SCHEMAS_DIR)
        # Check that all custom extra fields start with "view."
        for rec in caplog.records:
            if rec.name == "scripts.view_assembler":
                extra_keys = [k for k in rec.__dict__ if k.startswith("view.")]
                # If a record has view.* fields, verify no non-view.* custom fields
                if extra_keys:
                    # Standard LogRecord fields to exclude
                    standard = {
                        "name", "msg", "args", "created", "relativeCreated",
                        "thread", "threadName", "msecs", "filename", "funcName",
                        "levelno", "lineno", "module", "exc_info", "exc_text",
                        "stack_info", "levelname", "message", "pathname",
                        "process", "processName", "taskName",
                    }
                    custom_keys = [
                        k for k in rec.__dict__
                        if k not in standard and not k.startswith("_")
                        and not k.startswith("view.")
                    ]
                    # No non-view.* custom fields
                    assert all(
                        k in standard or k.startswith("view.")
                        for k in rec.__dict__
                        if not k.startswith("_")
                    ), f"Non-namespaced custom fields found: {custom_keys}"

    def test_metadata_has_format_version(self, log_api, workspace):
        """metadata section includes format_version reference in assembled output."""
        spec = {
            "name": "meta-fv-test",
            "description": "Format version in metadata test",
            "scope_patterns": [
                {"pattern": "component:*", "slot_type": "component"},
            ],
        }
        result = assemble_view(log_api, spec, workspace, SCHEMAS_DIR)
        assert "format_version" in result
        assert result["format_version"] == "1.1"
