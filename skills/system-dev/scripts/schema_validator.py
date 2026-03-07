"""JSON Schema validation with user-friendly error formatting.

Validates slot content against Draft 2020-12 JSON Schema definitions,
producing detailed error messages with field paths and fix hints.
"""

import json
import os

from jsonschema import Draft202012Validator


class SchemaValidationError(Exception):
    """Raised when slot content fails schema validation.

    Attributes:
        slot_type: The slot type that failed validation.
        errors: List of error dicts with path, constraint, message, hint, actual_value.
    """

    def __init__(self, slot_type: str, errors: list[dict]):
        self.slot_type = slot_type
        self.errors = errors
        msg = f"Schema validation failed for '{slot_type}': {len(errors)} error(s)\n"
        for e in errors:
            msg += f"  - {e['path']}: {e['message']}. Hint: {e['hint']}\n"
        super().__init__(msg)


def _generate_hint(error) -> str:
    """Generate a user-friendly fix hint from a jsonschema ValidationError.

    Maps common constraint types to actionable suggestions.

    Args:
        error: A jsonschema.ValidationError instance.

    Returns:
        A human-readable hint string suggesting how to fix the error.
    """
    validator = error.validator

    if validator == "required":
        # error.message is like "'name' is a required property"
        field = error.message.split("'")[1] if "'" in error.message else "unknown"
        return f"Add the '{field}' field to this object."

    if validator == "type":
        expected = error.schema.get("type", "unknown")
        return f"Change the value to type '{expected}'."

    if validator == "enum":
        values = error.schema.get("enum", [])
        return f"Use one of: {values}."

    if validator == "pattern":
        pattern = error.schema.get("pattern", "")
        return f"Value must match pattern: {pattern}"

    if validator == "minLength":
        min_len = error.schema.get("minLength", 0)
        return f"Value must be at least {min_len} characters."

    if validator == "const":
        value = error.schema.get("const", "")
        return f"Value must be exactly '{value}'."

    if validator == "additionalProperties":
        # Extract the unexpected field name from the error message
        # message is like "Additional properties are not allowed ('foo' was unexpected)"
        msg = error.message
        field = "unknown"
        if "'" in msg:
            parts = msg.split("'")
            if len(parts) >= 2:
                field = parts[1]
        allowed = sorted(error.schema.get("properties", {}).keys())
        return f"Remove unexpected field '{field}'. Allowed fields: {allowed}."

    return "Check the schema definition for valid values."


class SchemaValidator:
    """Validates slot content against JSON Schema definitions.

    Loads all JSON Schema files from a directory and validates slot content
    against the appropriate schema based on slot_type.

    Attributes:
        _schemas: Dict mapping slot_type name to parsed schema dict.
    """

    def __init__(self, schemas_dir: str):
        """Load all JSON Schema files from schemas/ directory.

        Args:
            schemas_dir: Path to directory containing .json schema files.
                Each file is named after its slot type (e.g., component.json).

        Raises:
            FileNotFoundError: If schemas_dir does not exist.
        """
        self._schemas: dict[str, dict] = {}
        if not os.path.isdir(schemas_dir):
            raise FileNotFoundError(f"Schemas directory not found: {schemas_dir}")

        for filename in os.listdir(schemas_dir):
            if filename.endswith(".json"):
                slot_type = filename[:-5]  # e.g., "component" from "component.json"
                filepath = os.path.join(schemas_dir, filename)
                with open(filepath) as f:
                    self._schemas[slot_type] = json.load(f)

    def validate(self, slot_type: str, content: dict) -> list[dict]:
        """Validate content against schema for the given slot_type.

        Args:
            slot_type: The type of slot (e.g., "component", "interface").
            content: The slot content dictionary to validate.

        Returns:
            Empty list if valid. List of error dicts if invalid, each with:
                - path: JSON path to the failing field (e.g., "$.name")
                - constraint: The schema constraint that failed (e.g., "required")
                - message: The jsonschema error message
                - hint: A user-friendly fix suggestion
                - actual_value: The actual value that failed validation

        Raises:
            ValueError: If slot_type is not a recognized schema type.
        """
        if slot_type not in self._schemas:
            raise ValueError(
                f"Unknown slot type: '{slot_type}'. "
                f"Supported types: {sorted(self._schemas.keys())}"
            )

        schema = self._schemas[slot_type]
        validator = Draft202012Validator(schema)
        errors_out = []

        sorted_errors = sorted(
            validator.iter_errors(content),
            key=lambda e: list(e.absolute_path),
        )

        for error in sorted_errors:
            path_parts = list(error.absolute_path)
            path = "$." + ".".join(str(p) for p in path_parts) if path_parts else "$"

            actual = error.instance
            if error.validator == "required":
                actual = None

            errors_out.append(
                {
                    "path": path,
                    "constraint": error.validator,
                    "message": error.message,
                    "hint": _generate_hint(error),
                    "actual_value": actual,
                }
            )

        return errors_out

    def validate_or_raise(self, slot_type: str, content: dict) -> None:
        """Validate and raise SchemaValidationError if invalid.

        Args:
            slot_type: The type of slot to validate against.
            content: The slot content dictionary to validate.

        Raises:
            SchemaValidationError: If content does not match the schema.
            ValueError: If slot_type is not recognized.
        """
        errors = self.validate(slot_type, content)
        if errors:
            raise SchemaValidationError(slot_type, errors)

    @property
    def supported_types(self) -> list[str]:
        """Return sorted list of supported slot types."""
        return sorted(self._schemas.keys())
