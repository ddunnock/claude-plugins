"""Tests for view_assembler.py -- view schemas, scope matching, snapshots, gaps."""

import json
import os

import pytest
from jsonschema import Draft202012Validator

from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.schema_validator import SchemaValidator

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
