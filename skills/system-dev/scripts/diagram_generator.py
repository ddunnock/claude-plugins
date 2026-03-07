"""D2 and Mermaid diagram generation engines.

Template-driven diagram generation using Jinja2 templates loaded from a
manifest-driven registry. Supports two-tier template resolution: user
overrides in .system-dev/templates/ take precedence over built-in templates.

Gap markers render as visually distinct dashed, color-coded placeholders.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time

import jinja2

from scripts.registry import SlotAPI
from scripts.view_assembler import assemble_view

logger = logging.getLogger(__name__)

# Severity -> color mapping for gap placeholders
_GAP_COLORS: dict[str, str] = {
    "error": "#dc3545",
    "warning": "#e6a117",
    "info": "#888888",
}

# Path to built-in templates directory (sibling of scripts/)
_BUILTIN_TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
)


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


def _build_template_context(
    view: dict, abstraction_level: str = "component"
) -> dict:
    """Build a flat context dict for template rendering.

    Pre-sorts all data for deterministic output (DIAG-08): sections by
    slot_type, slots within sections by name, edges by (source_id,
    target_id, relationship_type), gaps by (slot_type, index).

    Args:
        view: Assembled view dict (output of assemble_view()).
        abstraction_level: Abstraction level ("system" or "component").

    Returns:
        Context dict with keys: spec_name, snapshot_id, sections, edges,
        gaps, abstraction_level, node_count, edge_count, direction,
        has_unlinked, has_nodes, gap_severities, section_types,
        section_first_slot.
    """
    spec_name = view.get("spec_name", "unknown")
    snapshot_id = view.get("snapshot_id", "unknown")

    # Deep-copy and sort sections by slot_type for determinism
    sections = sorted(
        view.get("sections", []), key=lambda s: s["slot_type"]
    )
    # Sort slots within each section by name
    for section in sections:
        section["slots"] = sorted(
            section.get("slots", []),
            key=lambda s: s.get("name", s.get("slot_id", "")),
        )

    # Sort edges by (source_id, target_id, relationship_type)
    edges = sorted(
        view.get("edges", []),
        key=lambda e: (
            e["source_id"],
            e["target_id"],
            e["relationship_type"],
        ),
    )

    # Sort gaps by (slot_type, original index preserved via enumerate)
    gaps_raw = view.get("gaps", [])
    gaps = sorted(
        gaps_raw,
        key=lambda g: g["slot_type"],
    )

    # Compute convenience vars
    node_count = sum(len(s.get("slots", [])) for s in sections)
    edge_count = len(edges)
    direction = "LR" if node_count > 0 and edge_count > 2 * node_count else "TD"

    has_unlinked = any(
        s["slot_type"] == "unlinked" and s.get("slots")
        for s in sections
    )
    has_nodes = any(s.get("slots") for s in sections)

    gap_severities = sorted({g.get("severity", "warning") for g in gaps})

    # Track section types and first slot per type (for gap connections)
    section_types: set[str] = set()
    section_first_slot: dict[str, str] = {}
    for section in sections:
        slot_type = section["slot_type"]
        section_types.add(slot_type)
        for slot in section.get("slots", []):
            if slot_type not in section_first_slot:
                section_first_slot[slot_type] = _sanitize_id(slot["slot_id"])

    return {
        "spec_name": spec_name,
        "snapshot_id": snapshot_id,
        "sections": sections,
        "edges": edges,
        "gaps": gaps,
        "abstraction_level": abstraction_level,
        "node_count": node_count,
        "edge_count": edge_count,
        "direction": direction,
        "has_unlinked": has_unlinked,
        "has_nodes": has_nodes,
        "gap_severities": gap_severities,
        "section_types": section_types,
        "section_first_slot": section_first_slot,
    }


def _load_template(
    template_name: str | None,
    fmt: str,
    diagram_type: str,
    workspace_root: str | None = None,
) -> jinja2.Template:
    """Load a Jinja2 template from the manifest-driven registry.

    Resolution order:
    1. If template_name is provided, look for that exact .j2 file.
    2. Otherwise auto-select from manifest using fmt + diagram_type match.
    3. Check user override dir first, then fall back to built-in templates.

    Custom Jinja2 filters registered: sanitize_id, gap_color, truncate_label.

    Args:
        template_name: Explicit template name (e.g., "d2-structural"),
            or None for auto-selection.
        fmt: Diagram format ("d2" or "mermaid").
        diagram_type: Diagram type ("structural" or "behavioral").
        workspace_root: Path to .system-dev/ dir for user override resolution.

    Returns:
        Loaded and configured jinja2.Template.

    Raises:
        ValueError: If no matching template found in manifest.
    """
    # Load manifest
    manifest_path = os.path.join(_BUILTIN_TEMPLATES_DIR, "manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    # Find matching template entry
    template_file = None
    if template_name is not None:
        # Look for exact name match
        for entry in manifest["templates"]:
            if entry["name"] == template_name:
                template_file = entry["file"]
                break
        if template_file is None:
            # Try as a direct filename
            template_file = (
                template_name
                if template_name.endswith(".j2")
                else f"{template_name}.j2"
            )
    else:
        # Auto-select by fmt + diagram_type
        for entry in manifest["templates"]:
            if entry["format"] == fmt and entry["diagram_type"] == diagram_type:
                template_file = entry["file"]
                break

    if template_file is None:
        raise ValueError(
            f"No template found for format={fmt}, "
            f"diagram_type={diagram_type}, name={template_name}"
        )

    # Resolve template path: user override first, then built-in
    template_dir = _BUILTIN_TEMPLATES_DIR
    if workspace_root is not None:
        user_template_path = os.path.join(
            workspace_root, "templates", template_file
        )
        if os.path.isfile(user_template_path):
            template_dir = os.path.join(workspace_root, "templates")
            logger.info("Using user override template: %s", user_template_path)

    # Create Jinja2 environment with custom filters
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        keep_trailing_newline=False,
        undefined=jinja2.StrictUndefined,
    )

    # Register custom filters
    env.filters["sanitize_id"] = _sanitize_id
    env.filters["gap_color"] = lambda severity: _GAP_COLORS.get(
        severity, _GAP_COLORS["info"]
    )
    env.filters["truncate_label"] = lambda s, length=50: (
        s[:length] + "..." if len(s) > length else s
    )

    return env.get_template(template_file)


def generate_d2(view: dict) -> str:
    """Generate D2 structural diagram source from assembled view.

    Uses the d2-structural Jinja2 template internally.

    Args:
        view: Assembled view dict (output of assemble_view()).

    Returns:
        D2 source code string.
    """
    context = _build_template_context(view)
    template = _load_template(None, "d2", "structural")
    return template.render(**context)


def _resolve_format(
    format_override: str | None, spec: dict
) -> tuple[str, str]:
    """Resolve diagram output format from override or spec hint.

    Args:
        format_override: Explicit format ("d2" or "mermaid"), or None.
        spec: View spec dict, may contain "diagram_hint" field.

    Returns:
        Tuple of (format_str, diagram_type_str) where format_str is
        "d2" or "mermaid" and diagram_type_str is "structural" or
        "behavioral".

    Raises:
        ValueError: If no hint on spec and no format_override provided.
    """
    if format_override is not None:
        fmt = format_override.lower()
        if fmt in ("d2", "structural"):
            return ("d2", "structural")
        return ("mermaid", "behavioral")

    hint = spec.get("diagram_hint")
    if hint in ("structural", "d2"):
        return ("d2", "structural")
    if hint in ("behavioral", "mermaid"):
        return ("mermaid", "behavioral")

    raise ValueError(
        f"No diagram_hint on spec '{spec.get('name', 'unknown')}' "
        "and no --format override provided"
    )


def generate_diagram(
    api: SlotAPI,
    spec: dict,
    workspace_root: str,
    schemas_dir: str,
    format_override: str | None = None,
    template_name: str | None = None,
) -> dict:
    """Orchestrate diagram generation from a view spec.

    Assembles a view, resolves the output format, generates D2 or Mermaid
    source via Jinja2 template rendering, and writes the result as a
    diagram slot via SlotAPI.ingest().

    Only writes slots with slot_type="diagram" (DIAG-09 preservation).

    Args:
        api: A SlotAPI instance for registry access and diagram slot writes.
        spec: A view spec dict (must have name, description, scope_patterns).
        workspace_root: Path to the .system-dev/ directory.
        schemas_dir: Path to the schemas/ directory with JSON Schema files.
        format_override: Optional explicit format ("d2" or "mermaid").
            When provided, overrides the spec's diagram_hint.
        template_name: Optional explicit template name from
            spec.get("diagram_template"), overriding auto-selection.

    Returns:
        Dict with keys: status, slot_id, source, format, diagram_type,
        generation_elapsed_ms.
        Status is "created", "updated", or "unchanged".

    Raises:
        ValueError: If no diagram_hint on spec and no format_override.
    """
    t0 = time.perf_counter()

    # 1. Assemble view from spec
    view = assemble_view(api, spec, workspace_root, schemas_dir)

    # 2. Resolve format
    fmt, diagram_type = _resolve_format(format_override, spec)

    # Use template_name from spec if not explicitly provided
    if template_name is None:
        template_name = spec.get("diagram_template")

    # 3. Generate diagram source via template
    context = _build_template_context(
        view, abstraction_level=spec.get("abstraction_level", "component")
    )
    template = _load_template(template_name, fmt, diagram_type, workspace_root)
    source = template.render(**context)

    elapsed_ms = (time.perf_counter() - t0) * 1000

    # 4. Compute content-hash slot ID
    slot_id = _compute_diagram_slot_id(spec["name"], source)

    # 5. Check if identical slot already exists (no-op optimization)
    existing = api.read(slot_id)
    if existing is not None:
        return {
            "status": "unchanged",
            "slot_id": slot_id,
            "source": source,
            "format": fmt,
            "diagram_type": diagram_type,
            "generation_elapsed_ms": round(elapsed_ms, 3),
        }

    # 6. Build diagram slot content
    content = {
        "name": f"diagram-{spec['name']}",
        "format": fmt,
        "diagram_type": diagram_type,
        "source": source,
        "source_view_spec": spec["name"],
        "source_snapshot_id": view["snapshot_id"],
        "slot_count": view["total_slots"],
        "gap_count": view["total_gaps"],
        "generation_elapsed_ms": round(elapsed_ms, 3),
    }

    # 7. Write via SlotAPI.ingest() -- only "diagram" type (DIAG-09)
    result = api.ingest(slot_id, "diagram", content, agent_id="diagram-generator")

    return {
        "status": result["status"],
        "slot_id": slot_id,
        "source": source,
        "format": fmt,
        "diagram_type": diagram_type,
        "generation_elapsed_ms": round(elapsed_ms, 3),
    }


def generate_mermaid(view: dict) -> str:
    """Generate Mermaid behavioral diagram source from assembled view.

    Uses the mermaid-behavioral Jinja2 template internally.

    Args:
        view: Assembled view dict (output of assemble_view()).

    Returns:
        Mermaid source code string.
    """
    context = _build_template_context(view)
    template = _load_template(None, "mermaid", "behavioral")
    return template.render(**context)
