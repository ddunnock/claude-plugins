"""D2 and Mermaid diagram generation engines.

Pure functions that transform view handoff data (output of assemble_view())
into valid D2 structural and Mermaid behavioral diagram source code.
Gap markers render as visually distinct dashed, color-coded placeholders.
"""

from __future__ import annotations

import hashlib
import re

# Severity -> color mapping for gap placeholders
_GAP_COLORS: dict[str, str] = {
    "error": "#dc3545",
    "warning": "#e6a117",
    "info": "#888888",
}


def _sanitize_id(slot_id: str) -> str:
    """Convert slot_id to a safe diagram identifier.

    Replaces hyphens and other non-alphanumeric characters with
    underscores. Works for both D2 and Mermaid identifiers.

    Args:
        slot_id: Original slot ID (e.g., "comp-abc-123").

    Returns:
        Sanitized identifier (e.g., "comp_abc_123").
    """
    return re.sub(r"[^a-zA-Z0-9_]", "_", slot_id)


def _compute_diagram_slot_id(spec_name: str, source: str) -> str:
    """Compute a deterministic diagram slot ID from content hash.

    Args:
        spec_name: The view spec name (e.g., "system-overview").
        source: The diagram source code string.

    Returns:
        Slot ID in format ``diag-{spec_name}-{sha256(source)[:12]}``.
    """
    content_hash = hashlib.sha256(source.encode()).hexdigest()[:12]
    return f"diag-{spec_name}-{content_hash}"


def generate_d2(view: dict) -> str:
    """Generate D2 structural diagram source from assembled view.

    Pure function with no side effects. Produces D2 source with:
    - Components as nested containers (rectangle shapes)
    - Non-component slots as labeled nodes
    - Edges as labeled connections
    - Gap placeholders as dashed, color-coded shapes with [GAP] prefix

    Args:
        view: Assembled view dict (output of assemble_view()).

    Returns:
        D2 source code string.
    """
    spec_name = view.get("spec_name", "unknown")
    snapshot_id = view.get("snapshot_id", "unknown")

    lines: list[str] = [
        f"# Diagram: {spec_name} (structural)",
        f"# Generated from snapshot: {snapshot_id}",
    ]

    sections = view.get("sections", [])
    edges = view.get("edges", [])
    gaps = view.get("gaps", [])

    # Track which section slot_types exist (for gap context connections)
    section_types: set[str] = set()
    # Track first slot_id per section type (for gap connections)
    section_first_slot: dict[str, str] = {}

    # Emit slots by section
    for section in sections:
        slot_type = section["slot_type"]
        section_types.add(slot_type)
        section_slots = section.get("slots", [])

        if slot_type == "unlinked":
            # Wrap unlinked slots in a container
            if section_slots:
                lines.append("")
                lines.append('Unlinked: "Unlinked" {')
                for slot in section_slots:
                    safe_id = _sanitize_id(slot["slot_id"])
                    name = slot.get("name", slot["slot_id"])
                    lines.append(f'  {safe_id}: "{name}"')
                lines.append("}")
        elif slot_type == "component":
            # Components as nested containers
            lines.append("")
            lines.append("# Components")
            for slot in section_slots:
                safe_id = _sanitize_id(slot["slot_id"])
                name = slot.get("name", slot["slot_id"])
                if safe_id not in section_first_slot.get("component", safe_id + "_"):
                    section_first_slot.setdefault("component", safe_id)
                lines.append(f'{safe_id}: "{name}" {{')
                lines.append("  shape: rectangle")
                lines.append("}")
        else:
            # Non-component slot types as labeled nodes
            if section_slots:
                lines.append("")
                lines.append(f"# {slot_type.title()}s")
                for slot in section_slots:
                    safe_id = _sanitize_id(slot["slot_id"])
                    name = slot.get("name", slot["slot_id"])
                    section_first_slot.setdefault(slot_type, safe_id)
                    lines.append(f'{safe_id}: "{name}"')

    # Emit edges as connections
    if edges:
        lines.append("")
        lines.append("# Connections")
        for edge in edges:
            src = _sanitize_id(edge["source_id"])
            tgt = _sanitize_id(edge["target_id"])
            rel = edge["relationship_type"]
            lines.append(f"{src} -> {tgt}: {rel}")

    # Emit gap placeholders
    if gaps:
        lines.append("")
        lines.append("# Gap placeholders")
        for i, gap in enumerate(gaps):
            gap_id = _sanitize_id(f"gap_{gap['slot_type']}_{i}")
            color = _GAP_COLORS.get(gap["severity"], _GAP_COLORS["info"])
            reason = gap.get("reason", "Missing")
            suggestion = gap.get("suggestion", "")

            lines.append(f'{gap_id}: "[GAP] {gap["slot_type"]}: {reason}" {{')
            lines.append("  shape: rectangle")
            lines.append("  style: {")
            lines.append(f'    stroke: "{color}"')
            lines.append("    stroke-dash: 5")
            lines.append(f'    font-color: "{color}"')
            lines.append("  }")
            lines.append("}")
            if suggestion:
                lines.append(f"# Suggestion: {suggestion}")

            # Add dashed connection to context if gap slot_type matches a section
            if gap["slot_type"] in section_types:
                context_id = section_first_slot.get(gap["slot_type"])
                if context_id:
                    lines.append(
                        f"{gap_id} -> {context_id}: missing {{"
                    )
                    lines.append("  style.stroke-dash: 5")
                    lines.append("}")

    return "\n".join(lines)


def generate_mermaid(view: dict) -> str:
    """Generate Mermaid behavioral diagram source from assembled view.

    Pure function with no side effects. Produces Mermaid flowchart with:
    - Nodes for each slot (``safe_id["Label"]``)
    - Labeled arrows for edges (``-->|relationship_type|``)
    - classDef gap styles with stroke-dasharray (NO commas in value)
    - Gap nodes with ``:::className``

    Args:
        view: Assembled view dict (output of assemble_view()).

    Returns:
        Mermaid source code string.
    """
    spec_name = view.get("spec_name", "unknown")
    snapshot_id = view.get("snapshot_id", "unknown")

    sections = view.get("sections", [])
    edges = view.get("edges", [])
    gaps = view.get("gaps", [])

    # Count total nodes to determine direction
    node_count = sum(len(s.get("slots", [])) for s in sections)
    edge_count = len(edges)

    # Use LR when edges >> nodes (wide graph)
    direction = "LR" if node_count > 0 and edge_count > 2 * node_count else "TD"

    lines: list[str] = [
        f"%% Diagram: {spec_name} (behavioral)",
        f"%% Generated from snapshot: {snapshot_id}",
        "",
        f"graph {direction}",
    ]

    has_unlinked = False

    # Emit nodes
    if any(s.get("slots") for s in sections):
        lines.append("")
        lines.append("%% Nodes")
        for section in sections:
            slot_type = section["slot_type"]
            for slot in section.get("slots", []):
                safe_id = _sanitize_id(slot["slot_id"])
                name = slot.get("name", slot["slot_id"])
                if slot_type == "unlinked":
                    has_unlinked = True
                    lines.append(f'{safe_id}["{name}"]:::unlinked')
                else:
                    lines.append(f'{safe_id}["{name}"]')

    # Emit edges
    if edges:
        lines.append("")
        lines.append("%% Edges")
        for edge in edges:
            src = _sanitize_id(edge["source_id"])
            tgt = _sanitize_id(edge["target_id"])
            rel = edge["relationship_type"]
            lines.append(f"{src} -->|{rel}| {tgt}")

    # Collect needed gap severity levels
    gap_severities: set[str] = set()
    for gap in gaps:
        gap_severities.add(gap.get("severity", "warning"))

    # Emit gap styles and nodes
    if gaps:
        lines.append("")
        lines.append("%% Gap placeholders")

        # Emit classDef for each severity level used
        for severity in sorted(gap_severities):
            color = _GAP_COLORS.get(severity, _GAP_COLORS["info"])
            class_name = f"gap{severity.title()}"
            lines.append(
                f"classDef {class_name} "
                f"stroke:{color},stroke-width:2px,"
                f"stroke-dasharray: 5 5,color:{color}"
            )

        lines.append("")
        for i, gap in enumerate(gaps):
            gap_id = _sanitize_id(f"gap_{gap['slot_type']}_{i}")
            severity = gap.get("severity", "warning")
            class_name = f"gap{severity.title()}"
            reason = gap.get("reason", "Missing")
            suggestion = gap.get("suggestion", "")

            lines.append(
                f'{gap_id}["[GAP] {gap["slot_type"]}: {reason}"]'
                f":::{class_name}"
            )
            if suggestion:
                lines.append(f"%% Suggestion: {suggestion}")

    # Emit unlinked classDef if needed
    if has_unlinked:
        lines.append("")
        lines.append(
            "classDef unlinked fill:#f8f8f8,stroke:#cccccc,"
            "stroke-width:1px,color:#999999"
        )

    return "\n".join(lines)
