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
    api.create("interface", {"name": "Auth API", "provided_by": "comp-x", "consumed_by": ["comp-y"]})
    api.create("interface", {"name": "DB Connection", "provided_by": "comp-x", "consumed_by": ["comp-y"]})
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
