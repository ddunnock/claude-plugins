"""D2 and Mermaid diagram generation engines.

Template-driven diagram generation using Jinja2 templates loaded from a
manifest-driven registry. Supports two-tier template resolution: user
overrides in .system-dev/templates/ take precedence over built-in templates.

Gap markers render as visually distinct dashed, color-coded placeholders.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import re
import time
from collections import defaultdict

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


def _apply_abstraction_level(view: dict, level: str) -> dict:
    """Apply abstraction-level pre-processing to a view before rendering.

    At ``"component"`` level (or when *level* is ``None``), the view is
    returned as-is (deep-copied for safety).

    At ``"system"`` level the view is collapsed:

    * Only top-level component slots are kept.  A component is
      *top-level* if its ``slot_id`` is never referenced as a
      ``parent_id`` target by another component **and** it is not
      itself a child (has no ``parent_id`` field, or ``parent_id`` is
      empty).  Children are counted and a badge is appended to the
      parent name: ``"Name (N sub-components, M interfaces)"``.
    * Edges between child slots are aggregated to their parents.
      Multiple edges between the same parent pair are collapsed into a
      single edge whose ``relationship_type`` carries a count label,
      e.g. ``"implements (3)"``.

    Args:
        view: Assembled view dict (output of ``assemble_view()``).
        level: ``"system"`` or ``"component"`` (default pass-through).

    Returns:
        A **new** view dict — the original is never mutated.
    """
    if level is None or level == "component":
        return copy.deepcopy(view)

    # --- system-level abstraction ---
    view = copy.deepcopy(view)

    # 1. Build component index: slot_id -> slot dict, and parent mapping
    all_component_slots: list[dict] = []
    component_section_idx: int | None = None
    for idx, section in enumerate(view.get("sections", [])):
        if section["slot_type"] == "component":
            all_component_slots.extend(section["slots"])
            component_section_idx = idx

    if not all_component_slots:
        return view

    comp_by_id = {s["slot_id"]: s for s in all_component_slots}

    # Determine parent-child relationships via parent_id field
    child_ids: set[str] = set()
    children_of: dict[str, list[str]] = defaultdict(list)
    for slot in all_component_slots:
        pid = slot.get("parent_id", "")
        if pid and pid in comp_by_id:
            child_ids.add(slot["slot_id"])
            children_of[pid].append(slot["slot_id"])

    # If no explicit parent_id hierarchy exists, treat all components as
    # top-level (no collapsing needed, but still aggregate edges).
    top_level_ids = [
        s["slot_id"] for s in all_component_slots
        if s["slot_id"] not in child_ids
    ]

    # 2. Count interfaces per top-level component (from interface sections)
    intf_count: dict[str, int] = defaultdict(int)
    for section in view.get("sections", []):
        if section["slot_type"] == "interface":
            for intf in section["slots"]:
                src = intf.get("source_component", "")
                tgt = intf.get("target_component", "")
                for cid in (src, tgt):
                    if cid in comp_by_id:
                        # Walk up to top-level parent
                        resolved = _resolve_parent(cid, comp_by_id, child_ids)
                        intf_count[resolved] += 1

    # 3. Badge top-level component names
    top_level_slots: list[dict] = []
    for tid in top_level_ids:
        slot = comp_by_id[tid]
        n_children = len(children_of.get(tid, []))
        n_interfaces = intf_count.get(tid, 0)
        if n_children > 0 or n_interfaces > 0:
            parts = []
            if n_children > 0:
                parts.append(f"{n_children} sub-component{'s' if n_children != 1 else ''}")
            if n_interfaces > 0:
                parts.append(f"{n_interfaces} interface{'s' if n_interfaces != 1 else ''}")
            slot["name"] = f"{slot['name']} ({', '.join(parts)})"
        top_level_slots.append(slot)

    # Replace component section with collapsed top-level only
    if component_section_idx is not None:
        view["sections"][component_section_idx]["slots"] = top_level_slots

    # 4. Build child -> top-level parent mapping for edge aggregation
    child_to_parent: dict[str, str] = {}
    for slot in all_component_slots:
        resolved = _resolve_parent(slot["slot_id"], comp_by_id, child_ids)
        if resolved != slot["slot_id"]:
            child_to_parent[slot["slot_id"]] = resolved

    # 5. Aggregate edges
    agg: dict[tuple[str, str, str], int] = defaultdict(int)
    for edge in view.get("edges", []):
        src = child_to_parent.get(edge["source_id"], edge["source_id"])
        tgt = child_to_parent.get(edge["target_id"], edge["target_id"])
        rel = edge["relationship_type"]
        agg[(src, tgt, rel)] += 1

    new_edges: list[dict] = []
    for (src, tgt, rel), count in sorted(agg.items()):
        label = f"{rel} ({count})" if count > 1 else rel
        new_edges.append({
            "source_id": src,
            "target_id": tgt,
            "relationship_type": label,
        })
    view["edges"] = new_edges

    return view


def _resolve_parent(
    slot_id: str,
    comp_by_id: dict[str, dict],
    child_ids: set[str],
) -> str:
    """Walk up parent_id chain to find the top-level ancestor."""
    visited: set[str] = set()
    current = slot_id
    while current in child_ids and current not in visited:
        visited.add(current)
        pid = comp_by_id[current].get("parent_id", "")
        if pid and pid in comp_by_id:
            current = pid
        else:
            break
    return current


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
    # Apply abstraction level pre-processing before sorting
    view = _apply_abstraction_level(view, abstraction_level)

    spec_name = view.get("spec_name", "unknown")
    snapshot_id = view.get("snapshot_id", "unknown")

    # Sort sections by slot_type for determinism
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

    # DEBUG: per-section rendering info
    if logger.isEnabledFor(logging.DEBUG):
        for section in sections:
            logger.debug(
                "Rendering section: %s (%d slots)",
                section["slot_type"],
                len(section.get("slots", [])),
                extra={
                    "diagram.operation": "section_rendered",
                    "diagram.slot_type": section["slot_type"],
                    "diagram.slot_count": len(section.get("slots", [])),
                },
            )
        logger.debug(
            "Rendering %d edges",
            len(edges),
            extra={
                "diagram.operation": "edges_rendered",
                "diagram.edge_count": len(edges),
            },
        )
        logger.debug(
            "Rendering %d gaps",
            len(gaps),
            extra={
                "diagram.operation": "gaps_rendered",
                "diagram.gap_count": len(gaps),
            },
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

    # Verify the resolved file actually exists somewhere
    builtin_path = os.path.join(_BUILTIN_TEMPLATES_DIR, template_file)
    user_path = (
        os.path.join(workspace_root, "templates", template_file)
        if workspace_root
        else None
    )
    if not os.path.isfile(builtin_path) and (
        user_path is None or not os.path.isfile(user_path)
    ):
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
    logger.info(
        "Format resolved: %s (%s)",
        fmt,
        diagram_type,
        extra={
            "diagram.operation": "format_resolved",
            "diagram.format": fmt,
            "diagram.diagram_type": diagram_type,
        },
    )

    # Use template_name from spec if not explicitly provided
    if template_name is None:
        template_name = spec.get("diagram_template")

    # 3. Generate diagram source via template
    resolved_template_name = template_name or "auto"
    context = _build_template_context(
        view, abstraction_level=spec.get("abstraction_level", "component")
    )
    template = _load_template(template_name, fmt, diagram_type, workspace_root)
    logger.info(
        "Template loaded: %s",
        resolved_template_name,
        extra={
            "diagram.operation": "template_loaded",
            "diagram.template": resolved_template_name,
        },
    )
    source = template.render(**context)

    elapsed_ms = (time.perf_counter() - t0) * 1000
    line_count = source.count("\n") + 1
    logger.info(
        "Generation complete: %d lines",
        line_count,
        extra={
            "diagram.operation": "generation_complete",
            "diagram.elapsed_ms": round(elapsed_ms, 2),
            "diagram.line_count": line_count,
            "diagram.format": fmt,
        },
    )

    # 4. Compute content-hash slot ID
    slot_id = _compute_diagram_slot_id(spec["name"], source)

    # 5. Check if identical slot already exists (no-op optimization)
    existing = api.read(slot_id)
    if existing is not None:
        logger.info(
            "Slot written: %s (%s)",
            slot_id,
            "unchanged",
            extra={
                "diagram.operation": "slot_written",
                "diagram.slot_id": slot_id,
                "diagram.status": "unchanged",
            },
        )
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

    logger.info(
        "Slot written: %s (%s)",
        slot_id,
        result["status"],
        extra={
            "diagram.operation": "slot_written",
            "diagram.slot_id": slot_id,
            "diagram.status": result["status"],
        },
    )

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
