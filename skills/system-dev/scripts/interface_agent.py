"""Interface resolution agent: boundary discovery, proposal creation, and stale detection.

Discovers interface boundaries between approved components using relationship
data from accepted component-proposals and requirement cross-references. Creates
interface-proposal slots through SlotAPI for Claude to enrich with direction,
protocol, data_format_schema, and error_categories. Detects stale interfaces
when source components have newer timestamps.

The agent does NOT call Claude -- it handles data preparation and structured
output. The actual AI reasoning happens in the interface command workflow.

References:
    INTF-01 (interface discovery), INTF-02 (protocol/data-format contracts),
    INTF-03 (approval gate routing), INTF-04 (stale detection)
"""

import logging
from collections import defaultdict

from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)


def discover_interface_candidates(api: SlotAPI) -> list[dict]:
    """Discover interface candidates between approved components.

    Uses two discovery methods:
    1. Relationships from accepted component-proposals: each relationship
       in an accepted proposal indicates a boundary between components.
    2. Requirement cross-references: two components sharing requirement_ids
       indicate a boundary (filtering out cross-cutting requirements that
       appear in 3+ components).

    Deduplicates by sorted component pair (frozenset) so each pair produces
    at most one candidate regardless of discovery method or direction.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        List of candidate dicts with source_component, target_component,
        relationship_type, description, discovery_method, shared_requirement_ids.
    """
    # Query approved components and accepted proposals
    approved_components = api.query("component", {"status": "approved"})
    accepted_proposals = api.query("component-proposal", {"status": "accepted"})

    # Build mapping: proposal name -> committed component slot_id
    proposal_to_component: dict[str, str] = {}
    # Build mapping: component slot_id -> component name
    component_names: dict[str, str] = {}

    for comp in approved_components:
        component_names[comp["slot_id"]] = comp.get("name", comp["slot_id"])

    for proposal in accepted_proposals:
        committed_id = (
            proposal.get("decision", {}).get("committed_slot_id")
        )
        if committed_id and committed_id in component_names:
            proposal_to_component[proposal.get("name", "")] = committed_id

    # Track seen pairs for deduplication
    seen_pairs: dict[frozenset, dict] = {}

    # Method 1: Discover from relationships in accepted proposals
    for proposal in accepted_proposals:
        committed_id = (
            proposal.get("decision", {}).get("committed_slot_id")
        )
        if not committed_id or committed_id not in component_names:
            continue

        relationships = proposal.get("relationships", [])
        for rel in relationships:
            target_name = rel.get("target_proposal", "")
            target_id = proposal_to_component.get(target_name)
            if not target_id or target_id == committed_id:
                continue

            pair = frozenset([committed_id, target_id])
            if pair not in seen_pairs:
                seen_pairs[pair] = {
                    "source_component": committed_id,
                    "target_component": target_id,
                    "relationship_type": rel.get("type", "unknown"),
                    "description": rel.get("description", ""),
                    "discovery_method": "relationship",
                    "shared_requirement_ids": [],
                }

    # Method 2: Discover from requirement cross-references
    # Count how many components reference each requirement
    req_to_components: dict[str, list[str]] = defaultdict(list)
    for comp in approved_components:
        req_ids = comp.get("requirement_ids", comp.get("parent_requirements", []))
        for req_id in req_ids:
            req_to_components[req_id].append(comp["slot_id"])

    # Filter out cross-cutting requirements (3+ components)
    shared_reqs: dict[str, list[str]] = {
        req_id: comp_ids
        for req_id, comp_ids in req_to_components.items()
        if len(comp_ids) == 2
    }

    # Build pairs from shared requirements
    pair_shared_reqs: dict[frozenset, list[str]] = defaultdict(list)
    for req_id, comp_ids in shared_reqs.items():
        pair = frozenset(comp_ids)
        pair_shared_reqs[pair].append(req_id)

    for pair, req_ids in pair_shared_reqs.items():
        if pair not in seen_pairs:
            comp_list = sorted(pair)
            seen_pairs[pair] = {
                "source_component": comp_list[0],
                "target_component": comp_list[1],
                "relationship_type": "requirement_crossref",
                "description": f"Shared requirements: {', '.join(req_ids)}",
                "discovery_method": "requirement_crossref",
                "shared_requirement_ids": req_ids,
            }
        else:
            # Augment existing candidate with shared requirement info
            seen_pairs[pair]["shared_requirement_ids"] = req_ids

    return list(seen_pairs.values())


def detect_orphan_components(
    api: SlotAPI, candidates: list[dict]
) -> list[str]:
    """Find approved components that appear in zero interface candidates.

    Args:
        api: SlotAPI instance for querying slots.
        candidates: List of interface candidates from discover_interface_candidates.

    Returns:
        List of component slot_ids that have no interface candidates.
    """
    approved_components = api.query("component", {"status": "approved"})
    all_comp_ids = {comp["slot_id"] for comp in approved_components}

    # Collect all component IDs that appear in candidates
    connected_ids: set[str] = set()
    for candidate in candidates:
        connected_ids.add(candidate["source_component"])
        connected_ids.add(candidate["target_component"])

    orphans = sorted(all_comp_ids - connected_ids)
    if orphans:
        logger.warning(
            "Orphan components detected (no interface candidates): %s",
            orphans,
        )
    return orphans


def check_stale_interfaces(api: SlotAPI) -> list[dict]:
    """Detect approved interfaces whose source or target component has changed.

    Compares each approved interface's updated_at timestamp against its
    source_component and target_component updated_at timestamps. If either
    component is newer, the interface is flagged as stale.

    During normal command runs, stale interfaces trigger automatic re-proposal.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        List of stale interface dicts with slot_id, name, reason.
    """
    approved_interfaces = api.query("interface", {"status": "approved"})
    if not approved_interfaces:
        return []

    stale: list[dict] = []

    for intf in approved_interfaces:
        intf_id = intf["slot_id"]
        intf_name = intf.get("name", intf_id)
        intf_updated = intf.get("updated_at", "")

        reasons: list[str] = []

        # Check source component
        source_id = intf.get("source_component", "")
        if source_id:
            source = api.read(source_id)
            if source and source.get("updated_at", "") > intf_updated:
                reasons.append(
                    f"source component '{source.get('name', source_id)}' updated"
                )

        # Check target component
        target_id = intf.get("target_component", "")
        if target_id:
            target = api.read(target_id)
            if target and target.get("updated_at", "") > intf_updated:
                reasons.append(
                    f"target component '{target.get('name', target_id)}' updated"
                )

        if reasons:
            stale_entry = {
                "slot_id": intf_id,
                "name": intf_name,
                "reason": "; ".join(reasons),
            }
            stale.append(stale_entry)
            logger.warning(
                "Stale interface detected: %s (%s) -- %s",
                intf_name,
                intf_id,
                stale_entry["reason"],
            )

    return stale


class InterfaceAgent:
    """Data preparation and proposal creation for interface resolution.

    Discovers interface boundaries between approved components, prepares
    structured data for Claude to enrich with protocol/data-format details,
    and creates validated interface-proposal slots through SlotAPI.

    The agent does NOT perform AI reasoning -- that happens in the interface
    command workflow where Claude reads the prepared data and produces
    enriched interface definitions.

    Args:
        api: SlotAPI instance for all persistence operations.
        schemas_dir: Path to the schemas/ directory.
    """

    def __init__(self, api: SlotAPI, schemas_dir: str):
        self._api = api
        self._schemas_dir = schemas_dir

    def prepare(self) -> dict:
        """Discover interface candidates and detect orphan components.

        Calls discover_interface_candidates and detect_orphan_components
        to build a structured data bundle for Claude to enrich with
        direction, protocol, data_format_schema, and error_categories.

        Returns:
            Dict with:
                - candidates: list of interface candidate dicts
                - orphan_components: list of component slot_ids with no interfaces
                - component_count: total approved components
                - candidate_count: number of interface candidates
        """
        candidates = discover_interface_candidates(self._api)
        orphans = detect_orphan_components(self._api, candidates)

        approved = self._api.query("component", {"status": "approved"})

        return {
            "candidates": candidates,
            "orphan_components": orphans,
            "component_count": len(approved),
            "candidate_count": len(candidates),
        }

    def create_proposals(
        self,
        interfaces: list[dict],
        session_id: str,
        agent_id: str = "interface-resolution",
    ) -> list[dict]:
        """Create interface-proposal slots from enriched interface definitions.

        Takes Claude's enriched output and creates validated interface-proposal
        slots through SlotAPI. Each proposal gets status "proposed" and shares
        the session_id for batch tracking.

        Args:
            interfaces: List of enriched interface dicts from Claude, each with:
                - name: str (convention "{source}-to-{target}: {purpose}")
                - description: str
                - source_component: str (component slot_id)
                - target_component: str (component slot_id)
                - direction: "unidirectional" or "bidirectional"
                - protocol: str (e.g., "function_call", "event")
                - data_format_schema: dict (concrete JSON snippets)
                - error_categories: list of {name, description, expected_behavior}
                - rationale: dict with narrative and discovery_method
                - requirement_ids: list of str
                - gap_markers: list of gap marker dicts (optional)
            session_id: Unique session identifier for this interface run.
            agent_id: Identifier of the creating agent.

        Returns:
            List of created proposal dicts with slot_ids from SlotAPI.
        """
        created_proposals: list[dict] = []

        for interface in interfaces:
            rationale = interface.get("rationale", {})
            if isinstance(rationale, str):
                rationale = {"narrative": rationale}
            if "narrative" not in rationale:
                rationale["narrative"] = ""

            content = {
                "name": interface["name"],
                "description": interface.get("description", ""),
                "status": "proposed",
                "source_component": interface["source_component"],
                "target_component": interface["target_component"],
                "direction": interface.get("direction", "unidirectional"),
                "protocol": interface.get("protocol", ""),
                "data_format_schema": interface.get("data_format_schema", {}),
                "error_categories": interface.get("error_categories", []),
                "rationale": rationale,
                "requirement_ids": interface.get("requirement_ids", []),
                "gap_markers": interface.get("gap_markers", []),
                "decision": {
                    "action": None,
                    "decided_by": None,
                    "decided_at": None,
                    "notes": None,
                    "rejection_rationale": None,
                    "modifications": None,
                    "committed_slot_id": None,
                },
                "proposal_session_id": session_id,
            }

            result = self._api.create(
                "interface-proposal", content, agent_id
            )
            proposal = self._api.read(result["slot_id"])
            if proposal is not None:
                created_proposals.append(proposal)

            logger.info(
                "Created interface proposal: %s (%s) between %s and %s",
                interface["name"],
                result["slot_id"],
                interface["source_component"],
                interface["target_component"],
            )

        return created_proposals

    def format_preparation_summary(self, data: dict) -> str:
        """Format a human-readable summary of discovered candidates and orphans.

        Args:
            data: Data bundle from prepare().

        Returns:
            Formatted summary string.
        """
        lines: list[str] = []
        lines.append(
            f"Interface Discovery: {data['candidate_count']} candidates "
            f"found across {data['component_count']} approved components"
        )
        lines.append("")

        if data["candidates"]:
            lines.append("Candidates:")
            for i, c in enumerate(data["candidates"], 1):
                lines.append(
                    f"  {i}. {c['source_component']} <-> {c['target_component']} "
                    f"(via {c['discovery_method']})"
                )
                if c.get("description"):
                    lines.append(f"     {c['description']}")
            lines.append("")

        if data["orphan_components"]:
            lines.append(
                f"Orphan Components ({len(data['orphan_components'])} with no interfaces):"
            )
            for orphan_id in data["orphan_components"]:
                lines.append(f"  - {orphan_id}")
            lines.append("")

        return "\n".join(lines)
