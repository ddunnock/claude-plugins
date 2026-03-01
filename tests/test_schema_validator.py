"""Tests for schema_validator.py -- JSON Schema validation with user-friendly errors."""

import os

import pytest

from scripts.schema_validator import SchemaValidationError, SchemaValidator

# Resolve schemas/ relative to the project root
SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


def _make_valid_component(**overrides) -> dict:
    """Create a valid component slot dict for testing."""
    base = {
        "slot_id": "comp-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "slot_type": "component",
        "name": "Auth Service",
        "version": 1,
        "created_at": "2026-01-15T10:00:00+00:00",
        "updated_at": "2026-01-15T10:00:00+00:00",
    }
    base.update(overrides)
    return base


@pytest.fixture
def validator():
    return SchemaValidator(SCHEMAS_DIR)


class TestSchemaValidator:
    def test_valid_component_passes(self, validator):
        """Full valid component dict produces no errors."""
        content = _make_valid_component(
            description="Handles authentication",
            status="proposed",
        )
        errors = validator.validate("component", content)
        assert errors == []

    def test_missing_required_field(self, validator):
        """Omitting 'name' produces error with path and hint."""
        content = _make_valid_component()
        del content["name"]
        errors = validator.validate("component", content)
        assert len(errors) >= 1
        name_error = next(e for e in errors if "'name'" in e["message"])
        assert name_error["constraint"] == "required"
        assert "Add the 'name' field" in name_error["hint"]

    def test_wrong_type(self, validator):
        """Passing integer for 'name' produces type error with hint."""
        content = _make_valid_component(name=42)
        errors = validator.validate("component", content)
        assert len(errors) >= 1
        type_error = next(e for e in errors if e["path"] == "$.name")
        assert type_error["constraint"] == "type"
        assert "type 'string'" in type_error["hint"]

    def test_invalid_slot_id_pattern(self, validator):
        """Bad slot_id pattern produces pattern error with hint."""
        content = _make_valid_component(slot_id="bad-id")
        errors = validator.validate("component", content)
        assert len(errors) >= 1
        pattern_error = next(
            e for e in errors if e["constraint"] == "pattern"
        )
        assert "pattern" in pattern_error["hint"].lower()

    def test_invalid_enum_value(self, validator):
        """Invalid status enum value produces enum error with hint."""
        content = _make_valid_component(status="invalid")
        errors = validator.validate("component", content)
        assert len(errors) >= 1
        enum_error = next(e for e in errors if e["constraint"] == "enum")
        assert "Use one of:" in enum_error["hint"]

    def test_additional_property_rejected(self, validator):
        """Unknown field produces additionalProperties error with hint."""
        content = _make_valid_component(unknown_field="surprise")
        errors = validator.validate("component", content)
        assert len(errors) >= 1
        ap_error = next(
            e for e in errors if e["constraint"] == "additionalProperties"
        )
        assert "Remove unexpected field" in ap_error["hint"]

    def test_extensions_object_accepted(self, validator):
        """Extensions field with arbitrary object data passes validation."""
        content = _make_valid_component(extensions={"custom": "data", "flag": True})
        errors = validator.validate("component", content)
        assert errors == []

    def test_unknown_slot_type_raises(self, validator):
        """Validating with unknown slot type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown slot type: 'nonexistent'"):
            validator.validate("nonexistent", {})

    def test_all_slot_types_load(self, validator):
        """Validator loads all 14 slot type schemas (4 original + 5 ingestion + 3 proposals + 2 phase-5)."""
        types = validator.supported_types
        assert types == [
            "assumption",
            "component",
            "component-proposal",
            "contract",
            "contract-proposal",
            "impact-analysis",
            "interface",
            "interface-proposal",
            "need",
            "requirement",
            "requirement-ref",
            "source",
            "traceability-graph",
            "traceability-link",
        ]

    def test_validate_or_raise_passes_on_valid(self, validator):
        """validate_or_raise does not raise for valid content."""
        content = _make_valid_component()
        validator.validate_or_raise("component", content)  # should not raise

    def test_validate_or_raise_raises_on_invalid(self, validator):
        """validate_or_raise raises SchemaValidationError with error details."""
        content = _make_valid_component()
        del content["name"]
        with pytest.raises(SchemaValidationError) as exc_info:
            validator.validate_or_raise("component", content)
        assert exc_info.value.slot_type == "component"
        assert len(exc_info.value.errors) >= 1
