"""Structural decomposition agent: data preparation, gap detection, and proposal creation.

Prepares requirement data for Claude to analyze, validates output against the
component-proposal schema, and creates proposals through SlotAPI. The agent does
NOT call Claude or generate prompts -- it handles data preparation and structured
output. The actual AI reasoning happens in the decompose command workflow.

References:
    STRC-01 (structural decomposition), STRC-02 (gap detection),
    STRC-03 (coverage tracking), XCUT-04 (single API entry point)
"""

import logging
from collections import defaultdict

from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)


def detect_requirement_gaps(requirements: list[dict]) -> dict:
    """Analyze requirements for completeness BEFORE decomposition.

    Checks for missing descriptions, missing source_blocks, and existing
    gap_markers. Returns a severity assessment to help decide whether
    decomposition should proceed.

    Args:
        requirements: List of requirement slot dicts.

    Returns:
        Dict with gap analysis results:
            - total_requirements: int
            - missing_descriptions: list of slot_ids with no/empty description
            - missing_source_blocks: list of slot_ids with no source_block
            - incomplete_slots: list of slot_ids that already have gap_markers
            - gap_count: total gaps (missing_descriptions + incomplete_slots)
            - severity: "high" if gap_count > 20% of total, "medium" if > 0, "none" if 0
    """
    total = len(requirements)
    missing_descriptions: list[str] = []
    missing_source_blocks: list[str] = []
    incomplete_slots: list[str] = []

    for req in requirements:
        slot_id = req.get("slot_id", "unknown")

        # Check for missing or empty description
        desc = req.get("description", "")
        if not desc or not desc.strip():
            missing_descriptions.append(slot_id)

        # Check for missing source_block
        if not req.get("source_block"):
            missing_source_blocks.append(slot_id)

        # Check for existing gap_markers
        gap_markers = req.get("gap_markers", [])
        if gap_markers:
            incomplete_slots.append(slot_id)

    gap_count = len(missing_descriptions) + len(incomplete_slots)

    if total == 0:
        severity = "none"
    elif gap_count > total * 0.2:
        severity = "high"
    elif gap_count > 0:
        severity = "medium"
    else:
        severity = "none"

    return {
        "total_requirements": total,
        "missing_descriptions": missing_descriptions,
        "missing_source_blocks": missing_source_blocks,
        "incomplete_slots": incomplete_slots,
        "gap_count": gap_count,
        "severity": severity,
    }


def check_stale_components(api: SlotAPI) -> list[dict]:
    """Detect accepted components whose requirements have changed.

    Proactive flagging: when requirements are updated (new gap_markers,
    status changes, or any content update), accepted components referencing
    those requirements are flagged as stale for potential revision.

    Called at the START of decompose workflow so the user sees which
    existing components may need revision before creating new proposals.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        List of stale component dicts, each with:
            - component_slot_id: str
            - component_name: str
            - stale_reason: str
            - affected_requirement_ids: list[str]
            - component_updated_at: str
            - newest_requirement_updated_at: str
    """
    # Query all accepted components
    components = api.query("component", {"status": "approved"})
    if not components:
        return []

    stale_components: list[dict] = []

    for comp in components:
        comp_id = comp["slot_id"]
        comp_name = comp.get("name", comp_id)
        comp_updated_at = comp.get("updated_at", "")
        parent_reqs = comp.get("parent_requirements", [])

        if not parent_reqs:
            continue

        # Check each referenced requirement for changes
        affected_req_ids: list[str] = []
        stale_reasons: list[str] = []
        newest_req_updated = ""

        for req_id in parent_reqs:
            req = api.read(req_id)
            if req is None:
                continue

            req_updated = req.get("updated_at", "")
            if req_updated > newest_req_updated:
                newest_req_updated = req_updated

            # Check if requirement was updated after the component
            if req_updated > comp_updated_at:
                affected_req_ids.append(req_id)

                # Determine specific stale reason
                gap_markers = req.get("gap_markers", [])
                req_status = req.get("upstream_status", "")

                if gap_markers:
                    stale_reasons.append(
                        f"{req_id} has gap_markers"
                    )
                if req_status in ("deprecated", "modified"):
                    stale_reasons.append(
                        f"{req_id} status changed to {req_status}"
                    )
                if not stale_reasons or (
                    f"{req_id} has gap_markers" not in stale_reasons
                    and f"{req_id} status changed to {req_status}" not in stale_reasons
                ):
                    stale_reasons.append(
                        f"{req_id} updated after component"
                    )

        if affected_req_ids:
            stale_entry = {
                "component_slot_id": comp_id,
                "component_name": comp_name,
                "stale_reason": "; ".join(stale_reasons),
                "affected_requirement_ids": affected_req_ids,
                "component_updated_at": comp_updated_at,
                "newest_requirement_updated_at": newest_req_updated,
            }
            stale_components.append(stale_entry)
            logger.warning(
                "Stale component detected: %s (%s) -- %s",
                comp_name,
                comp_id,
                stale_entry["stale_reason"],
            )

    return stale_components


def prepare_requirement_data(api: SlotAPI) -> dict:
    """Query all requirement and need slots and prepare data for decomposition.

    Extracts the fields needed for Claude's analysis, runs gap detection,
    and groups requirements by source_block for chunked context.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        Dict with:
            - requirements: list of extracted requirement dicts
            - needs: list of extracted need dicts
            - gap_report: result of detect_requirement_gaps
            - by_source_block: dict grouping requirements by source_block
    """
    # Query all requirements
    raw_requirements = api.query("requirement")
    requirements: list[dict] = []
    for req in raw_requirements:
        extracted = {
            "slot_id": req["slot_id"],
            "upstream_id": req.get("upstream_id", ""),
            "description": req.get("description", ""),
            "requirement_type": req.get("requirement_type", ""),
            "source_block": req.get("source_block", ""),
            "parent_need": req.get("parent_need", ""),
            "gap_markers": req.get("gap_markers", []),
            "derives_from": req.get("derives_from", []),
        }
        requirements.append(extracted)

    # Query all needs for context
    raw_needs = api.query("need")
    needs: list[dict] = []
    for need in raw_needs:
        extracted = {
            "slot_id": need["slot_id"],
            "upstream_id": need.get("upstream_id", ""),
            "description": need.get("description", ""),
            "stakeholder": need.get("stakeholder", ""),
            "source_block": need.get("source_block", ""),
        }
        needs.append(extracted)

    # Run gap detection
    gap_report = detect_requirement_gaps(raw_requirements)

    # Group by source_block
    by_source_block: dict[str, list[dict]] = defaultdict(list)
    for req in requirements:
        block = req.get("source_block", "unassigned")
        if not block:
            block = "unassigned"
        by_source_block[block].append(req)

    return {
        "requirements": requirements,
        "needs": needs,
        "gap_report": gap_report,
        "by_source_block": dict(by_source_block),
    }


class DecompositionAgent:
    """Data preparation and proposal creation for structural decomposition.

    This agent prepares requirement data for Claude to analyze and creates
    validated component-proposal slots from Claude's output. It does NOT
    perform the AI reasoning -- that happens in the decompose command workflow
    where Claude reads the prepared data and produces groupings.

    Args:
        api: SlotAPI instance for all persistence operations.
        schemas_dir: Path to the schemas/ directory.
    """

    def __init__(self, api: SlotAPI, schemas_dir: str):
        self._api = api
        self._schemas_dir = schemas_dir

    def prepare(self) -> dict:
        """Prepare requirement data for decomposition analysis.

        Calls prepare_requirement_data to query all requirements and needs,
        run gap detection, and group by source_block.

        Returns:
            Data bundle with requirements, needs, gap_report, and by_source_block.
        """
        return prepare_requirement_data(self._api)

    def create_proposals(
        self,
        components: list[dict],
        session_id: str,
        agent_id: str = "structural-decomposition",
    ) -> list[dict]:
        """Create component-proposal slots from AI-generated component groupings.

        Takes Claude's analysis output and creates validated component-proposal
        slots through SlotAPI. Each proposal gets a status of "proposed" and
        shares the session_id for batch tracking.

        Args:
            components: List of component dicts from Claude's analysis, each with:
                - name: str
                - description: str
                - requirement_ids: list[str]
                - rationale: dict with narrative, grouping_criteria, evidence
                - relationships: list of {target_proposal, type, description}
                - gap_markers: list of gap marker dicts (optional)
            session_id: Unique session identifier for this decomposition run.
            agent_id: Identifier of the creating agent.

        Returns:
            List of created proposal dicts with slot_ids from SlotAPI.
        """
        created_proposals: list[dict] = []

        for component in components:
            # Build the proposal content matching component-proposal schema
            rationale = component.get("rationale", {})
            if isinstance(rationale, str):
                rationale = {"narrative": rationale}

            # Ensure rationale has required structure
            if "narrative" not in rationale:
                rationale["narrative"] = ""

            content = {
                "name": component["name"],
                "description": component.get("description", ""),
                "status": "proposed",
                "requirement_ids": component.get("requirement_ids", []),
                "rationale": rationale,
                "gap_markers": component.get("gap_markers", []),
                "relationships": component.get("relationships", []),
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
                "component-proposal", content, agent_id
            )
            proposal = self._api.read(result["slot_id"])
            created_proposals.append(proposal)

            logger.info(
                "Created proposal: %s (%s) with %d requirements",
                component["name"],
                result["slot_id"],
                len(component.get("requirement_ids", [])),
            )

        return created_proposals

    def format_coverage_summary(
        self, proposals: list[dict], total_requirements: int
    ) -> str:
        """Format a coverage summary showing mapped vs unmapped requirements.

        Args:
            proposals: List of created proposal dicts.
            total_requirements: Total number of requirements in the registry.

        Returns:
            Formatted summary string like "47/52 requirements mapped, 5 unmapped (gap markers)".
        """
        # Collect all unique requirement_ids across proposals
        mapped_ids: set[str] = set()
        for proposal in proposals:
            for req_id in proposal.get("requirement_ids", []):
                mapped_ids.add(req_id)

        mapped_count = len(mapped_ids)
        unmapped_count = total_requirements - mapped_count

        # Count proposals with gap markers
        proposals_with_gaps = sum(
            1 for p in proposals if p.get("gap_markers")
        )

        parts = [f"{mapped_count}/{total_requirements} requirements mapped"]
        if unmapped_count > 0:
            parts.append(f"{unmapped_count} unmapped")
        if proposals_with_gaps > 0:
            parts.append(f"{proposals_with_gaps} proposals with gap markers")

        return ", ".join(parts)

    def format_proposal_narrative(self, proposals: list[dict]) -> str:
        """Format proposals as narrative blocks with summary-first density.

        Each proposal is formatted as:
        - Component name + 1-line purpose + requirement count header
        - Rationale narrative
        - Evidence list

        Args:
            proposals: List of created proposal dicts.

        Returns:
            Formatted narrative string.
        """
        blocks: list[str] = []

        for proposal in proposals:
            name = proposal.get("name", "Unnamed")
            description = proposal.get("description", "")
            req_ids = proposal.get("requirement_ids", [])
            rationale = proposal.get("rationale", {})
            narrative = rationale.get("narrative", "")
            evidence = rationale.get("evidence", [])

            # Header: name + purpose + requirement count
            header = f"## {name}"
            purpose = f"{description}" if description else ""
            req_count = f"Requirements: {len(req_ids)}"

            lines = [header]
            if purpose:
                lines.append(purpose)
            lines.append(req_count)
            lines.append("")

            # Rationale narrative
            if narrative:
                lines.append(narrative)
                lines.append("")

            # Evidence list
            if evidence:
                lines.append("Evidence:")
                for ev in evidence:
                    req_id = ev.get("req_id", "")
                    relevance = ev.get("relevance", "")
                    lines.append(f"  - {req_id}: {relevance}")
                lines.append("")

            blocks.append("\n".join(lines))

        return "\n---\n\n".join(blocks)
