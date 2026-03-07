"""Traceability graph builder and chain validator.

Constructs a traversable graph from all design registry slots (both
traceability-link slots and embedded fields on committed slots),
validates end-to-end chains from stakeholder needs through V&V
assignments, and materializes the result as a singleton traceability-graph
slot with staleness tracking.

Follows the established agent pattern: data prep only, no AI calls.
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)

# Slot types that produce graph nodes
TRACEABLE_TYPES = ["need", "requirement", "component", "interface", "contract"]

# Expected chain level order for validation
CHAIN_LEVELS = {
    "need": 0,
    "requirement": 1,
    "component": 2,
    "interface": 3,
    "contract": 4,
    "vv": 5,
}

# Edge types that connect adjacent chain levels (forward direction)
_LEVEL_FORWARD_EDGES = {
    (0, 1): {"satisfies", "allocated_to", "derives_from"},
    (1, 2): {"allocated_to"},
    (2, 3): {"boundary_of"},
    (3, 4): {"constrained_by"},
    (4, 5): {"verified_by"},
}

# Well-known singleton ID for the materialized traceability graph
GRAPH_SLOT_ID = "tgraph-current"


def _build_adjacency(edges: list[dict]) -> tuple[dict, dict]:
    """Build forward and reverse adjacency dicts from edge list."""
    forward: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    reverse: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for edge in edges:
        forward[edge["from_id"]][edge["to_id"]].append(edge["edge_type"])
        reverse[edge["to_id"]][edge["from_id"]].append(edge["edge_type"])
    return dict(forward), dict(reverse)


class TraceabilityAgent:
    """Builds and validates traceability graphs from registry slots.

    Args:
        api: SlotAPI instance for reading/writing slots.
    """

    def __init__(self, api: SlotAPI):
        self._api = api

    def build_graph(self) -> dict:
        """Build a traceability graph from all registry slots.

        Collects edges from both traceability-link slots and embedded
        fields on committed design elements. Deduplicates edges and
        detects divergences.

        Returns:
            Graph dict matching traceability-graph schema structure,
            plus internal _forward_adj and _reverse_adj dicts.
        """
        nodes: dict[str, dict] = {}
        raw_edges: list[dict] = []

        # 1. Collect all traceable slots as nodes
        for slot_type in TRACEABLE_TYPES:
            for slot in self._api.query(slot_type):
                slot_id = slot["slot_id"]
                nodes[slot_id] = {
                    "type": slot_type,
                    "name": slot.get("name", slot.get("description", slot_id)[:80]),
                }

        # 2. Collect edges from traceability-link slots
        for link in self._api.query("traceability-link"):
            raw_edges.append({
                "from_id": link["from_id"],
                "to_id": link["to_id"],
                "edge_type": link["link_type"],
                "source": "traceability-link",
            })

        # 3. Collect edges from embedded fields
        self._collect_component_edges(raw_edges)
        self._collect_interface_edges(raw_edges)
        self._collect_contract_edges(raw_edges, nodes)

        # 4. Deduplicate and detect divergences
        edges, divergences = self._deduplicate_edges(raw_edges)

        # 5. Build adjacency dicts
        forward_adj, reverse_adj = _build_adjacency(edges)

        now = datetime.now(timezone.utc).isoformat()

        return {
            "nodes": nodes,
            "edges": edges,
            "chain_report": {
                "chains": [],
                "gaps": [],
                "divergences": divergences,
            },
            "completeness": {
                "total_chains": 0,
                "complete_chains": 0,
                "percentage": 0.0,
                "broken_chains": 0,
                "orphan_count": 0,
            },
            "built_at": now,
            "staleness_marker": now,
            "_forward_adj": dict(forward_adj),
            "_reverse_adj": dict(reverse_adj),
        }

    def _collect_component_edges(self, raw_edges: list[dict]) -> None:
        """Extract edges from component embedded fields."""
        for comp in self._api.query("component"):
            comp_id = comp["slot_id"]

            # requirement_ids -> allocated_to edges (requirement -> component)
            for req_id in comp.get("requirement_ids", []) or []:
                raw_edges.append({
                    "from_id": req_id,
                    "to_id": comp_id,
                    "edge_type": "allocated_to",
                    "source": "embedded_field",
                })

            # relationships -> communicates_with edges
            for rel in comp.get("relationships", []) or []:
                target = rel.get("target_id") or rel.get("component_id", "")
                if target:
                    raw_edges.append({
                        "from_id": comp_id,
                        "to_id": target,
                        "edge_type": "communicates_with",
                        "source": "embedded_field",
                    })

    def _collect_interface_edges(self, raw_edges: list[dict]) -> None:
        """Extract edges from interface embedded fields."""
        for intf in self._api.query("interface"):
            intf_id = intf["slot_id"]

            # source_component/target_component -> boundary_of edges
            for field in ("source_component", "target_component"):
                comp_id = intf.get(field, "")
                if comp_id:
                    raw_edges.append({
                        "from_id": comp_id,
                        "to_id": intf_id,
                        "edge_type": "boundary_of",
                        "source": "embedded_field",
                    })

            # requirement_ids -> allocated_to edges
            for req_id in intf.get("requirement_ids", []) or []:
                raw_edges.append({
                    "from_id": req_id,
                    "to_id": intf_id,
                    "edge_type": "allocated_to",
                    "source": "embedded_field",
                })

    def _collect_contract_edges(self, raw_edges: list[dict], nodes: dict) -> None:
        """Extract edges from contract embedded fields and create synthetic V&V nodes."""
        for cntr in self._api.query("contract"):
            cntr_id = cntr["slot_id"]

            # component_id -> constrained_by edge (component -> contract)
            comp_id = cntr.get("component_id", "")
            if comp_id:
                raw_edges.append({
                    "from_id": comp_id,
                    "to_id": cntr_id,
                    "edge_type": "constrained_by",
                    "source": "embedded_field",
                })

            # interface_id -> constrained_by edge (interface -> contract)
            intf_id = cntr.get("interface_id", "")
            if intf_id:
                raw_edges.append({
                    "from_id": intf_id,
                    "to_id": cntr_id,
                    "edge_type": "constrained_by",
                    "source": "embedded_field",
                })

            # obligations[].source_requirement_ids -> derives_from edges
            for obl in cntr.get("obligations", []) or []:
                for req_id in obl.get("source_requirement_ids", []) or []:
                    raw_edges.append({
                        "from_id": req_id,
                        "to_id": cntr_id,
                        "edge_type": "derives_from",
                        "source": "embedded_field",
                    })

            # vv_assignments -> synthetic vv: nodes + verified_by edges
            for vv in cntr.get("vv_assignments", []) or []:
                obl_id = vv.get("obligation_id", "")
                if obl_id:
                    vv_node_id = f"vv:{cntr_id}:{obl_id}"
                    nodes[vv_node_id] = {
                        "type": "vv",
                        "name": f"V&V {vv.get('method', 'unknown')} for {obl_id}",
                    }
                    raw_edges.append({
                        "from_id": cntr_id,
                        "to_id": vv_node_id,
                        "edge_type": "verified_by",
                        "source": "embedded_field",
                    })

    def _deduplicate_edges(
        self, raw_edges: list[dict]
    ) -> tuple[list[dict], list[dict]]:
        """Deduplicate edges and detect divergences.

        Edges with same (from_id, to_id, edge_type) are deduplicated,
        preferring traceability-link source. Edges with same (from_id, to_id)
        but different edge_type from different sources are flagged as divergences.

        Returns:
            Tuple of (deduplicated edges, divergences).
        """
        # Group by (from_id, to_id, edge_type) for dedup
        edge_map: dict[tuple[str, str, str], dict] = {}
        for edge in raw_edges:
            key = (edge["from_id"], edge["to_id"], edge["edge_type"])
            existing = edge_map.get(key)
            if existing is None:
                edge_map[key] = edge
            elif edge["source"] == "traceability-link":
                # Prefer traceability-link source
                edge_map[key] = edge

        # Detect divergences: same (from, to) but different edge_type from different sources
        pair_map: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for edge in edge_map.values():
            pair_map[(edge["from_id"], edge["to_id"])].append(edge)

        divergences = []
        for (from_id, to_id), edges_for_pair in pair_map.items():
            if len(edges_for_pair) > 1:
                sources = {e["source"] for e in edges_for_pair}
                if len(sources) > 1:
                    divergences.append({
                        "from_id": from_id,
                        "to_id": to_id,
                        "edges": [
                            {"edge_type": e["edge_type"], "source": e["source"]}
                            for e in edges_for_pair
                        ],
                    })

        return list(edge_map.values()), divergences

    def validate_chains(self, graph: dict) -> dict:
        """Validate end-to-end traceability chains from needs through V&V.

        Walks forward from each need node through the expected chain levels.
        Reports complete chains, gaps with severity, and orphan elements.

        Args:
            graph: Graph dict from build_graph().

        Returns:
            Report dict with chains, gaps, divergences, and completeness.
        """
        nodes = graph["nodes"]
        forward_adj = graph.get("_forward_adj", {})

        need_nodes = [nid for nid, n in nodes.items() if n["type"] == "need"]
        visited: set[str] = set()

        chains: list[dict] = []
        gaps: list[dict] = []

        for need_id in need_nodes:
            chain_result = self._walk_chain(need_id, nodes, forward_adj, visited)
            chains.append(chain_result["chain"])
            gaps.extend(chain_result["gaps"])

        # Orphan detection: nodes not visited from any chain walk
        all_node_ids = set(nodes.keys())
        orphans = all_node_ids - visited
        orphan_gaps = []
        for orphan_id in orphans:
            node = nodes[orphan_id]
            if node["type"] != "need":  # Disconnected needs are already caught as empty chains
                orphan_gaps.append({
                    "need_id": "",
                    "type": "orphan",
                    "severity": "info",
                    "node_id": orphan_id,
                    "node_type": node["type"],
                    "message": f"Orphan {node['type']} '{node['name']}' not connected to any chain",
                })
        gaps.extend(orphan_gaps)

        total_chains = len(need_nodes)
        complete_chains = sum(1 for c in chains if c["status"] == "complete")
        broken_chains = total_chains - complete_chains
        percentage = (complete_chains / total_chains * 100) if total_chains > 0 else 0.0

        report = {
            "chains": chains,
            "gaps": gaps,
            "divergences": graph.get("chain_report", {}).get("divergences", []),
            "completeness": {
                "total_chains": total_chains,
                "complete_chains": complete_chains,
                "percentage": percentage,
                "broken_chains": broken_chains,
                "orphan_count": len(orphan_gaps),
            },
        }
        return report

    def _walk_chain(
        self, need_id: str, nodes: dict, forward_adj: dict, visited: set
    ) -> dict:
        """Walk a single chain from a need node forward through levels.

        Returns dict with chain summary and any gaps found.
        """
        visited.add(need_id)
        chain_path: list[dict] = [{"level": 0, "type": "need", "id": need_id}]
        chain_gaps: list[dict] = []

        # BFS-style walk through chain levels
        current_level_ids = {need_id}
        max_level_reached = 0

        for level in range(5):  # levels 0-4, looking for connections to level+1
            next_level_ids: set[str] = set()
            target_level = level + 1
            target_type = [t for t, l in CHAIN_LEVELS.items() if l == target_level][0]

            for node_id in current_level_ids:
                neighbors = forward_adj.get(node_id, {})
                for neighbor_id in neighbors:
                    neighbor_node = nodes.get(neighbor_id)
                    if neighbor_node and neighbor_node["type"] == target_type:
                        next_level_ids.add(neighbor_id)
                        visited.add(neighbor_id)

            if next_level_ids:
                max_level_reached = target_level
                for nid in next_level_ids:
                    chain_path.append({
                        "level": target_level,
                        "type": target_type,
                        "id": nid,
                    })
                current_level_ids = next_level_ids
            else:
                # Gap at this level -- record and stop walking
                severity = "critical" if target_level <= 2 else "warning"

                chain_gaps.append({
                    "need_id": need_id,
                    "type": "chain_break",
                    "severity": severity,
                    "break_at_level": target_level,
                    "break_at_type": target_type,
                    "message": f"Chain from {need_id} breaks at {target_type} level",
                })
                break

        is_complete = max_level_reached == 5  # reached vv level
        status = "complete" if is_complete else "incomplete"

        return {
            "chain": {
                "need_id": need_id,
                "status": status,
                "max_level": max_level_reached,
                "path": chain_path,
            },
            "gaps": chain_gaps,
        }

    def check_staleness(self, graph_slot: dict) -> bool:
        """Check if the traceability graph is stale.

        Compares graph built_at against the most recent updated_at
        across all traceable slot types.

        Args:
            graph_slot: The traceability-graph slot dict.

        Returns:
            True if any source slot is newer than built_at.
        """
        built_at = graph_slot.get("built_at", "")
        if not built_at:
            return True

        for slot_type in TRACEABLE_TYPES + ["traceability-link"]:
            for slot in self._api.query(slot_type):
                if slot.get("updated_at", "") > built_at:
                    return True

        return False

    def build_or_refresh(self) -> dict:
        """Get or rebuild the traceability graph.

        Uses well-known singleton ID tgraph-current. Creates new graph
        if none exists, rebuilds if stale, returns existing if fresh.

        Returns:
            The traceability-graph slot dict.
        """
        existing = self._api.read(GRAPH_SLOT_ID)

        if existing is not None and not self.check_staleness(existing):
            return existing

        # Build fresh graph
        graph = self.build_graph()
        report = self.validate_chains(graph)

        # Prepare slot content (remove internal adjacency dicts)
        slot_content = {
            "nodes": graph["nodes"],
            "edges": graph["edges"],
            "built_at": graph["built_at"],
            "staleness_marker": graph["staleness_marker"],
            "chain_report": {
                "chains": report["chains"],
                "gaps": report["gaps"],
                "divergences": report["divergences"],
            },
            "completeness": report["completeness"],
        }

        if existing is not None:
            # Update existing graph
            result = self._api.update(
                GRAPH_SLOT_ID,
                slot_content,
                expected_version=existing["version"],
                agent_id="traceability-agent",
            )
            logger.info("Rebuilt stale traceability graph: v%s", result["version"])
        else:
            # Create new graph with deterministic ID
            result = self._api.ingest(
                GRAPH_SLOT_ID,
                "traceability-graph",
                slot_content,
                agent_id="traceability-agent",
            )
            logger.info("Created traceability graph: %s", result["slot_id"])

        # Re-read to get the full persisted slot
        persisted = self._api.read(GRAPH_SLOT_ID)
        if persisted is None:
            raise RuntimeError(f"Failed to read back graph slot '{GRAPH_SLOT_ID}' after write")

        # Attach internal adjacency for callers that need it
        fwd, rev = _build_adjacency(persisted.get("edges", []))
        persisted["_forward_adj"] = fwd
        persisted["_reverse_adj"] = rev

        return persisted

    def format_trace_output(self, graph_slot: dict) -> str:
        """Format the traceability graph as human-readable output.

        Shows completeness percentage at top, chain-per-need summary,
        divergences in separate section, orphans at bottom.

        Args:
            graph_slot: The traceability-graph slot dict.

        Returns:
            Markdown-formatted trace report string.
        """
        completeness = graph_slot.get("completeness", {})
        chain_report = graph_slot.get("chain_report", {})
        nodes = graph_slot.get("nodes", {})

        lines: list[str] = []

        # Header with completeness
        pct = completeness.get("percentage", 0)
        total = completeness.get("total_chains", 0)
        complete = completeness.get("complete_chains", 0)
        broken = completeness.get("broken_chains", 0)

        lines.append(f"# Traceability Report -- {pct:.0f}% Complete")
        lines.append("")
        lines.append(f"**Chains:** {complete}/{total} complete, {broken} broken")
        lines.append(f"**Orphans:** {completeness.get('orphan_count', 0)}")
        lines.append("")

        # Chain-per-need summary
        chains = chain_report.get("chains", [])
        gaps = chain_report.get("gaps", [])

        if chains:
            lines.append("## Chain Summary")
            lines.append("")
            for chain in chains:
                need_id = chain["need_id"]
                need_name = nodes.get(need_id, {}).get("name", need_id)
                status_icon = "OK" if chain["status"] == "complete" else "BREAK"

                lines.append(f"### [{status_icon}] {need_name}")
                lines.append("")

                # Show chain path
                for step in chain.get("path", []):
                    level_name = step["type"]
                    step_name = nodes.get(step["id"], {}).get("name", step["id"])
                    lines.append(f"  {level_name} -> {step_name}")

                # Show gaps for this need
                need_gaps = [g for g in gaps if g.get("need_id") == need_id]
                for gap in need_gaps:
                    severity = gap["severity"].upper()
                    lines.append(f"  [{severity}] {gap['message']}")

                lines.append("")

        # Divergences section (separate per CONTEXT.md)
        divergences = chain_report.get("divergences", [])
        if divergences:
            lines.append("## Divergences")
            lines.append("")
            for div in divergences:
                lines.append(f"- {div['from_id']} -> {div['to_id']}:")
                for edge_info in div.get("edges", []):
                    lines.append(f"  - {edge_info['edge_type']} (from {edge_info['source']})")
            lines.append("")

        # Orphans at bottom
        orphan_gaps = [g for g in gaps if g.get("type") == "orphan"]
        if orphan_gaps:
            lines.append("## Orphan Elements (info)")
            lines.append("")
            for og in orphan_gaps:
                lines.append(f"- {og['node_type']}: {og.get('node_id', 'unknown')}")
            lines.append("")

        return "\n".join(lines)

    # ============================================================
    # Impact analysis methods
    # ============================================================

    def compute_impact(
        self,
        start_id: str,
        direction: str = "forward",
        depth_limit: int | None = None,
        type_filter: list[str] | None = None,
    ) -> dict:
        """Compute change impact (blast radius) from a design element.

        Uses BFS with a visited set for cycle safety. Traverses all node
        types internally even when type_filter restricts output paths.

        Args:
            start_id: Slot ID to analyze impact from.
            direction: "forward", "backward", or "both".
            depth_limit: Max BFS depth (None = unlimited).
            type_filter: If set, only include these types in output paths.

        Returns:
            Dict matching impact-analysis schema structure.
        """
        graph_slot = self.build_or_refresh()
        nodes = graph_slot.get("nodes", {})
        total_nodes = len(nodes)

        # Handle nonexistent start_id
        if start_id not in nodes:
            return {
                "source_element": start_id,
                "direction": direction,
                "depth_limit": depth_limit,
                "type_filter": type_filter,
                "paths": [],
                "affected_count": 0,
                "uncertainty_markers": [],
                "graph_coverage_percent": 0.0,
                "gap_markers": [
                    {
                        "type": "missing_data",
                        "finding_ref": f"IMPACT-{start_id}",
                        "severity": "high",
                        "description": f"Element '{start_id}' not found in design registry",
                    }
                ],
            }

        forward_adj = graph_slot.get("_forward_adj", {})
        reverse_adj = graph_slot.get("_reverse_adj", {})

        if direction == "both":
            fwd_visited, fwd_parent = self._bfs(start_id, forward_adj, depth_limit)
            bwd_visited, bwd_parent = self._bfs(start_id, reverse_adj, depth_limit)
            all_visited = fwd_visited | bwd_visited
            fwd_tree = self._build_tree(start_id, fwd_parent, nodes, forward_adj, type_filter)
            bwd_tree = self._build_tree(start_id, bwd_parent, nodes, reverse_adj, type_filter)
            paths = fwd_tree + bwd_tree
        elif direction == "backward":
            all_visited, parent_map = self._bfs(start_id, reverse_adj, depth_limit)
            paths = self._build_tree(start_id, parent_map, nodes, reverse_adj, type_filter)
        else:  # forward
            all_visited, parent_map = self._bfs(start_id, forward_adj, depth_limit)
            paths = self._build_tree(start_id, parent_map, nodes, forward_adj, type_filter)

        # affected_count = all reachable nodes (excluding start), regardless of type_filter
        affected_count = len(all_visited) - 1  # exclude start_id itself

        # Coverage and uncertainty
        coverage = (len(all_visited) / total_nodes * 100) if total_nodes > 0 else 0.0
        uncertainty_markers = []
        if coverage < 100:
            unreachable = set(nodes.keys()) - all_visited
            for uid in unreachable:
                uncertainty_markers.append({
                    "element_id": uid,
                    "reason": f"Not reachable from '{start_id}' via {direction} traversal",
                })

        return {
            "source_element": start_id,
            "direction": direction,
            "depth_limit": depth_limit,
            "type_filter": type_filter,
            "paths": paths,
            "affected_count": affected_count,
            "uncertainty_markers": uncertainty_markers,
            "graph_coverage_percent": round(coverage, 2),
            "gap_markers": [],
        }

    def _bfs(
        self,
        start_id: str,
        adj: dict[str, dict[str, list[str]]],
        depth_limit: int | None,
    ) -> tuple[set[str], dict[str, str]]:
        """BFS traversal with cycle-safe visited set.

        Returns:
            Tuple of (visited set, parent_map {child_id: parent_id}).
        """
        visited: set[str] = {start_id}
        parent_map: dict[str, str] = {}
        queue: deque[tuple[str, int]] = deque([(start_id, 0)])

        while queue:
            node_id, depth = queue.popleft()
            if depth_limit is not None and depth >= depth_limit:
                continue

            neighbors = adj.get(node_id, {})
            for neighbor_id in neighbors:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    parent_map[neighbor_id] = node_id
                    queue.append((neighbor_id, depth + 1))

        return visited, parent_map

    def _build_tree(
        self,
        start_id: str,
        parent_map: dict[str, str],
        nodes: dict[str, dict],
        adj: dict[str, dict[str, list[str]]],
        type_filter: list[str] | None,
    ) -> list[dict]:
        """Build tree-structured paths from BFS parent map.

        Returns list of root-level tree nodes (direct children of start_id).
        """
        # Build children map from parent_map
        children_map: dict[str, list[str]] = defaultdict(list)
        for child, parent in parent_map.items():
            children_map[parent].append(child)

        def build_node(node_id: str, depth: int, rel_from_parent: str) -> dict | None:
            node_info = nodes.get(node_id, {})
            node_type = node_info.get("type", "unknown")
            node_name = node_info.get("name", node_id)

            child_nodes = []
            for child_id in children_map.get(node_id, []):
                # Get relationship type
                edge_types = adj.get(node_id, {}).get(child_id, [])
                rel = edge_types[0] if edge_types else "related_to"
                child_node = build_node(child_id, depth + 1, rel)
                if child_node is not None:
                    child_nodes.append(child_node)

            # Apply type filter: include node if it matches filter OR has matching descendants
            if type_filter is not None:
                if node_type not in type_filter and not child_nodes:
                    return None
                if node_type not in type_filter and child_nodes:
                    # Skip this node but promote its children
                    return None  # Will be handled by parent

            return {
                "element_id": node_id,
                "element_type": node_type,
                "element_name": node_name,
                "depth": depth,
                "relationship": rel_from_parent,
                "children": child_nodes,
            }

        # Build from start_id's direct children
        result = []
        for child_id in children_map.get(start_id, []):
            edge_types = adj.get(start_id, {}).get(child_id, [])
            rel = edge_types[0] if edge_types else "related_to"
            node = build_node(child_id, 1, rel)
            if node is not None:
                result.append(node)
            elif type_filter is not None:
                # Node filtered out but might have descendants that match
                # Promote matching descendants
                for desc in self._find_filtered_descendants(
                    child_id, children_map, nodes, adj, type_filter, 1
                ):
                    result.append(desc)

        return result

    def _find_filtered_descendants(
        self,
        node_id: str,
        children_map: dict[str, list[str]],
        nodes: dict[str, dict],
        adj: dict[str, dict[str, list[str]]],
        type_filter: list[str],
        depth: int,
    ) -> list[dict]:
        """Find descendants matching type_filter when intermediate nodes are filtered out."""
        result = []
        for child_id in children_map.get(node_id, []):
            node_info = nodes.get(child_id, {})
            node_type = node_info.get("type", "unknown")
            if node_type in type_filter:
                edge_types = adj.get(node_id, {}).get(child_id, [])
                rel = edge_types[0] if edge_types else "related_to"
                result.append({
                    "element_id": child_id,
                    "element_type": node_type,
                    "element_name": node_info.get("name", child_id),
                    "depth": depth + 1,
                    "relationship": rel,
                    "children": [],
                })
            else:
                result.extend(self._find_filtered_descendants(
                    child_id, children_map, nodes, adj, type_filter, depth + 1
                ))
        return result

    def persist_impact(self, impact_result: dict) -> dict:
        """Persist an impact analysis result as an impact-analysis slot.

        Args:
            impact_result: Dict from compute_impact().

        Returns:
            The created slot dict with slot_id.
        """
        content = {
            "source_element": impact_result["source_element"],
            "direction": impact_result["direction"],
            "depth_limit": impact_result.get("depth_limit"),
            "type_filter": impact_result.get("type_filter"),
            "paths": impact_result["paths"],
            "affected_count": impact_result["affected_count"],
            "uncertainty_markers": impact_result.get("uncertainty_markers", []),
            "graph_coverage_percent": impact_result.get("graph_coverage_percent", 0.0),
            "gap_markers": impact_result.get("gap_markers", []),
        }
        result = self._api.create("impact-analysis", content)
        slot_id = result["slot_id"]
        # Read back the full persisted slot
        persisted = self._api.read(slot_id)
        if persisted is None:
            raise RuntimeError(f"Failed to read back impact-analysis slot '{slot_id}' after create")
        return persisted

    def format_impact_output(self, impact_result: dict) -> str:
        """Format impact analysis result as a hierarchical tree view.

        Args:
            impact_result: Dict from compute_impact().

        Returns:
            Human-readable tree view string.
        """
        lines: list[str] = []
        source = impact_result["source_element"]
        direction = impact_result["direction"]
        affected = impact_result["affected_count"]
        coverage = impact_result.get("graph_coverage_percent", 0.0)
        type_filter = impact_result.get("type_filter")

        lines.append(f"# Impact Analysis: {source}")
        lines.append("")
        lines.append(f"**Direction:** {direction}")
        depth_limit = impact_result.get("depth_limit")
        if depth_limit is not None:
            lines.append(f"**Depth limit:** {depth_limit}")
        if type_filter:
            lines.append(f"**Type filter:** {', '.join(type_filter)}")
        lines.append(f"**Graph coverage:** {coverage:.1f}%")
        lines.append("")

        # Tree view
        paths = impact_result.get("paths", [])
        if paths:
            lines.append(f"{source}")
            for i, child in enumerate(paths):
                is_last = i == len(paths) - 1
                self._format_tree_node(child, lines, "", is_last)
        else:
            lines.append("No impact paths found.")

        lines.append("")
        lines.append(f"**Total affected elements:** {affected}")

        # Uncertainty markers
        markers = impact_result.get("uncertainty_markers", [])
        if markers:
            lines.append("")
            lines.append(f"**Uncertainty:** {len(markers)} elements not reachable (coverage {coverage:.1f}%)")

        # Gap markers
        gaps = impact_result.get("gap_markers", [])
        if gaps:
            lines.append("")
            lines.append("**Gaps:**")
            for gap in gaps:
                lines.append(f"  - [{gap['severity']}] {gap['description']}")

        return "\n".join(lines)

    def _format_tree_node(
        self, node: dict, lines: list[str], prefix: str, is_last: bool
    ) -> None:
        """Recursively format a tree node for display."""
        connector = "`-- " if is_last else "|-- "
        el_id = node["element_id"]
        el_type = node["element_type"]
        el_name = node["element_name"]
        rel = node.get("relationship", "")

        lines.append(f"{prefix}{connector}{el_id} ({el_type}: {el_name}) [{rel}]")

        child_prefix = prefix + ("    " if is_last else "|   ")
        children = node.get("children", [])
        for i, child in enumerate(children):
            child_is_last = i == len(children) - 1
            self._format_tree_node(child, lines, child_prefix, child_is_last)
