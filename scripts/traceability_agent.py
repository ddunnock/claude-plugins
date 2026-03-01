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
from collections import defaultdict
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
        forward_adj: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        reverse_adj: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

        for edge in edges:
            forward_adj[edge["from_id"]][edge["to_id"]].append(edge["edge_type"])
            reverse_adj[edge["to_id"]][edge["from_id"]].append(edge["edge_type"])

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
                if max_level_reached == 0 and level == 0:
                    severity = "critical"
                elif target_level <= 2:
                    severity = "critical"
                else:
                    severity = "warning"

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
        forward_adj = defaultdict(lambda: defaultdict(list))
        reverse_adj = defaultdict(lambda: defaultdict(list))
        for edge in persisted.get("edges", []):
            forward_adj[edge["from_id"]][edge["to_id"]].append(edge["edge_type"])
            reverse_adj[edge["to_id"]][edge["from_id"]].append(edge["edge_type"])
        persisted["_forward_adj"] = dict(forward_adj)
        persisted["_reverse_adj"] = dict(reverse_adj)

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
