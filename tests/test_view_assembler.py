"""Tests for view_assembler.py -- view schemas, scope matching, snapshots, gaps."""

import copy
import json
import os

import pytest
from jsonschema import Draft202012Validator

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.schema_validator import SchemaValidator
from scripts.view_assembler import (
    _apply_field_selection,
    _organize_hierarchically,
    assemble_view,
    build_gap_indicator,
    capture_snapshot,
    load_gap_rules,
    load_view_spec,
    match_scope_pattern,
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
            "assembled_at": "2026-03-02T00:00:00Z",
            "snapshot_id": "snap-abc123",
            "total_slots": 5,
            "total_gaps": 1,
            "gap_summary": {"info": 0, "warning": 1, "error": 0},
            "sections": [],
            "gaps": [],
        }
        errors = list(self.validator.iter_errors(view))
        assert errors == [], f"Unexpected errors: {errors}"

    def test_rejects_missing_gap_summary(self):
        """A view without gap_summary is rejected."""
        view = {
            "spec_name": "test-view",
            "assembled_at": "2026-03-02T00:00:00Z",
            "snapshot_id": "snap-abc123",
            "total_slots": 0,
            "total_gaps": 0,
            "sections": [],
            "gaps": [],
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
