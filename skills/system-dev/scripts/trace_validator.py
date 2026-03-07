"""Write-time trace enforcement for design element slots.

Validates that design elements (components, interfaces, contracts) include
required traceability fields and that referenced slot IDs exist. Returns
warnings only -- never blocks writes (TRAC-04 warn-but-allow policy).

Follows the SchemaValidator pattern as a separate validation layer called
by SlotAPI after schema validation passes.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)

# Only design elements are subject to trace enforcement.
# Upstream-ingested types (need, requirement, source, assumption,
# traceability-link) and proposals are exempt.
DESIGN_ELEMENT_TYPES = {"component", "interface", "contract"}

# Maps slot_type to the trace fields that should be present.
TRACE_FIELDS: dict[str, list[str]] = {
    "component": ["requirement_ids"],
    "interface": ["requirement_ids", "source_component", "target_component"],
    "contract": ["component_id", "interface_id", "requirement_ids"],
}

# Fields whose values are single slot ID references (not lists).
_SINGLE_REF_FIELDS = {"source_component", "target_component", "component_id", "interface_id"}

# Fields whose values are lists of slot ID references.
_LIST_REF_FIELDS = {"requirement_ids"}


class TraceValidator:
    """Validates traceability fields on design element writes.

    Returns a list of warning dicts. Never raises exceptions.
    Warnings are used by SlotAPI to auto-inject gap_markers into
    the persisted slot content.
    """

    def validate(
        self, slot_type: str, content: dict, api: SlotAPI
    ) -> list[dict]:
        """Check trace fields and reference existence for a slot.

        Args:
            slot_type: The type of slot being written.
            content: The slot content dict (system fields already set).
            api: SlotAPI instance for reference existence checks.

        Returns:
            List of warning dicts, each with keys: type, field, message,
            and optionally ref_id for broken references. Empty list means
            no trace issues found.
        """
        if slot_type not in DESIGN_ELEMENT_TYPES:
            return []

        warnings: list[dict] = []
        fields = TRACE_FIELDS.get(slot_type, [])

        for field in fields:
            value = content.get(field)

            # Check for missing or empty field
            if value is None or (isinstance(value, list) and len(value) == 0):
                warnings.append({
                    "type": "missing_trace_field",
                    "field": field,
                    "message": (
                        f"Design element '{slot_type}' is missing "
                        f"trace field '{field}'"
                    ),
                })
                continue

            # Check reference existence for non-empty values
            if field in _SINGLE_REF_FIELDS and isinstance(value, str):
                if api.read(value) is None:
                    warnings.append({
                        "type": "broken_reference",
                        "field": field,
                        "ref_id": value,
                        "message": (
                            f"Referenced slot '{value}' in field "
                            f"'{field}' does not exist"
                        ),
                    })
            elif field in _LIST_REF_FIELDS and isinstance(value, list):
                for ref_id in value:
                    if api.read(ref_id) is None:
                        warnings.append({
                            "type": "broken_reference",
                            "field": field,
                            "ref_id": ref_id,
                            "message": (
                                f"Referenced slot '{ref_id}' in field "
                                f"'{field}' does not exist"
                            ),
                        })

        return warnings
