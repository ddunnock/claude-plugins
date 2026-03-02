"""Behavioral contract agent: obligation derivation, V&V assignment, and stale detection.

Prepares component/interface/requirement data for Claude to derive INCOSE-style
behavioral obligations, assigns default V&V methods from vv-rules.json with AI
override capability, and detects stale contracts when interfaces change.

The agent does NOT call Claude -- it handles data preparation and structured output.
The actual AI reasoning happens in the contract command workflow.

References:
    BHVR-01 (behavioral obligations), BHVR-02 (V&V assignment),
    BHVR-03 (approval routing), BHVR-04 (stale contract detection)
"""

import json
import logging
from collections import defaultdict

from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)


def load_vv_rules(rules_path: str) -> dict:
    """Load and return the V&V rules JSON config.

    Args:
        rules_path: Path to the vv-rules.json file.

    Returns:
        Parsed rules dict with default_methods, override_policy, valid_methods.

    Raises:
        FileNotFoundError: If the rules file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(rules_path) as f:
        return json.load(f)


def assign_vv_methods(obligations: list[dict], vv_rules: dict) -> list[dict]:
    """Assign default V&V methods to obligations using vv-rules.json.

    For each obligation, looks up obligation_type in default_methods.
    If found, assigns that method. If not found, defaults to "test".
    These are DEFAULT assignments -- Claude can override any of them
    with a different method and rationale (is_override=True).

    Args:
        obligations: List of obligation dicts, each with at least
            id and obligation_type fields.
        vv_rules: Loaded vv-rules.json config dict.

    Returns:
        List of V&V assignment dicts, each with:
            - obligation_id: str
            - method: str (test|analysis|inspection|demonstration)
            - rationale: str
            - is_override: bool (always False for defaults)
    """
    default_methods = vv_rules.get("default_methods", {})
    assignments: list[dict] = []

    for obligation in obligations:
        ob_id = obligation["id"]
        ob_type = obligation.get("obligation_type", "")

        if ob_type in default_methods:
            method = default_methods[ob_type]
            rationale = f"Default for {ob_type} obligations per vv-rules.json"
        else:
            method = "test"
            rationale = f"No default rule for {ob_type}; defaulting to test"

        assignments.append({
            "obligation_id": ob_id,
            "method": method,
            "rationale": rationale,
            "is_override": False,
        })

    return assignments


def prepare_obligation_data(api: SlotAPI) -> dict:
    """Query approved components, interfaces, and requirements for obligation derivation.

    For each approved component, groups its requirements by type/category and
    pairs with its interfaces. Returns structured data for Claude to derive
    INCOSE-style behavioral obligations.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        Dict with:
            - components: list of component dicts with their interfaces and requirements
            - total_components: int
            - total_interfaces: int
            - total_requirements: int
            - gaps: list of gap descriptions for components with incomplete data
    """
    # Query approved components and interfaces
    components = api.query("component", {"status": "approved"})
    interfaces = api.query("interface", {"status": "approved"})

    if not components:
        return {
            "components": [],
            "total_components": 0,
            "total_interfaces": 0,
            "total_requirements": 0,
            "gaps": [],
        }

    # Build interface lookup by component (source or target)
    intf_by_component: dict[str, list[dict]] = defaultdict(list)
    for intf in interfaces:
        source = intf.get("source_component", "")
        target = intf.get("target_component", "")
        if source:
            intf_by_component[source].append(intf)
        if target and target != source:
            intf_by_component[target].append(intf)

    result_components: list[dict] = []
    gaps: list[str] = []
    total_reqs = 0

    for comp in components:
        comp_id = comp["slot_id"]
        comp_name = comp.get("name", comp_id)
        req_ids = comp.get("requirement_ids", comp.get("parent_requirements", []))

        # Fetch requirements for this component
        comp_requirements: list[dict] = []
        for req_id in req_ids:
            req = api.read(req_id)
            if req is not None:
                comp_requirements.append({
                    "slot_id": req["slot_id"],
                    "description": req.get("description", ""),
                    "requirement_type": req.get("requirement_type", ""),
                    "source_block": req.get("source_block", ""),
                    "gap_markers": req.get("gap_markers", []),
                })
            else:
                gaps.append(
                    f"Component '{comp_name}' references missing requirement '{req_id}'"
                )

        total_reqs += len(comp_requirements)

        # Get interfaces for this component
        comp_interfaces = intf_by_component.get(comp_id, [])
        extracted_interfaces: list[dict] = [
            {
                "slot_id": intf["slot_id"],
                "name": intf.get("name", ""),
                "description": intf.get("description", ""),
                "source_component": intf.get("source_component", ""),
                "target_component": intf.get("target_component", ""),
                "direction": intf.get("direction", ""),
                "data_format_schema": intf.get("data_format_schema", {}),
                "error_categories": intf.get("error_categories", []),
            }
            for intf in comp_interfaces
        ]

        # Group requirements by type for easier analysis
        reqs_by_type: dict[str, list[dict]] = defaultdict(list)
        for req in comp_requirements:
            req_type = req.get("requirement_type", "unclassified")
            if not req_type:
                req_type = "unclassified"
            reqs_by_type[req_type].append(req)

        # Check for incomplete data
        if not comp_requirements:
            gaps.append(
                f"Component '{comp_name}' ({comp_id}) has no mapped requirements"
            )
        if not comp_interfaces:
            gaps.append(
                f"Component '{comp_name}' ({comp_id}) has no approved interfaces"
            )

        result_components.append({
            "component_id": comp_id,
            "component_name": comp_name,
            "description": comp.get("description", ""),
            "interfaces": extracted_interfaces,
            "requirements": comp_requirements,
            "requirements_by_type": dict(reqs_by_type),
            "requirement_ids": req_ids,
            "has_gaps": bool(gaps) or any(
                r.get("gap_markers") for r in comp_requirements
            ),
        })

    return {
        "components": result_components,
        "total_components": len(result_components),
        "total_interfaces": len(interfaces),
        "total_requirements": total_reqs,
        "gaps": gaps,
    }


def check_stale_contracts(api: SlotAPI) -> list[dict]:
    """Detect approved contracts whose interfaces have changed.

    One-level cascade only: interface -> contract. If an interface has
    updated_at newer than a contract referencing it, the contract is
    flagged as stale. Contract changes do NOT cascade back to interfaces.

    Args:
        api: SlotAPI instance for querying slots.

    Returns:
        List of stale contract dicts, each with:
            - slot_id: str
            - name: str
            - reason: str
            - interface_id: str
            - contract_updated_at: str
            - interface_updated_at: str
    """
    contracts = api.query("contract", {"status": "approved"})
    if not contracts:
        return []

    stale_contracts: list[dict] = []

    for contract in contracts:
        contract_id = contract["slot_id"]
        contract_name = contract.get("name", contract_id)
        contract_updated = contract.get("updated_at", "")
        interface_id = contract.get("interface_id", "")

        if not interface_id:
            continue

        interface = api.read(interface_id)
        if interface is None:
            continue

        interface_updated = interface.get("updated_at", "")

        if interface_updated > contract_updated:
            stale_entry = {
                "slot_id": contract_id,
                "name": contract_name,
                "reason": (
                    f"Interface '{interface.get('name', interface_id)}' "
                    f"updated after contract"
                ),
                "interface_id": interface_id,
                "contract_updated_at": contract_updated,
                "interface_updated_at": interface_updated,
            }
            stale_contracts.append(stale_entry)
            logger.warning(
                "Stale contract detected: %s (%s) -- %s",
                contract_name,
                contract_id,
                stale_entry["reason"],
            )

    return stale_contracts


class ContractAgent:
    """Data preparation and proposal creation for behavioral contracts.

    Prepares component/interface/requirement data for Claude to derive
    INCOSE-style obligations, assigns default V&V methods, merges Claude's
    overrides, and creates contract-proposal slots through SlotAPI.

    Args:
        api: SlotAPI instance for all persistence operations.
        schemas_dir: Path to the schemas/ directory.
        vv_rules_path: Path to the vv-rules.json config file.
    """

    def __init__(self, api: SlotAPI, schemas_dir: str, vv_rules_path: str):
        self._api = api
        self._schemas_dir = schemas_dir
        self._vv_rules = load_vv_rules(vv_rules_path)

    def prepare(self) -> dict:
        """Prepare obligation data for behavioral contract derivation.

        Calls prepare_obligation_data to query approved components, interfaces,
        and requirements, organized for Claude to derive obligations.

        Returns:
            Data bundle with components, interfaces, requirements, and gaps.
        """
        return prepare_obligation_data(self._api)

    def create_proposals(
        self,
        contracts: list[dict],
        session_id: str,
        agent_id: str = "behavioral-contract",
    ) -> list[dict]:
        """Create contract-proposal slots from AI-generated contract definitions.

        Takes Claude's obligation analysis and creates validated contract-proposal
        slots through SlotAPI. Each proposal gets default V&V assignments, with
        Claude's overrides merged in.

        Args:
            contracts: List of contract dicts from Claude, each with:
                - component_id: str
                - interface_id: str
                - name: str
                - description: str
                - obligations: list of {id, statement, obligation_type,
                    source_requirement_ids, error_category?}
                - rationale: str or dict with narrative
                - vv_overrides: optional list of {obligation_id, method,
                    rationale} to override defaults
            session_id: Unique session identifier for this contract run.
            agent_id: Identifier of the creating agent.

        Returns:
            List of created proposal dicts with slot_ids from SlotAPI.
        """
        created_proposals: list[dict] = []

        for contract in contracts:
            obligations = contract.get("obligations", [])

            # Assign default V&V methods
            vv_assignments = assign_vv_methods(obligations, self._vv_rules)

            # Merge Claude's overrides over defaults
            vv_overrides = contract.get("vv_overrides", [])
            if vv_overrides:
                override_map = {
                    ov["obligation_id"]: ov for ov in vv_overrides
                }
                for i, assignment in enumerate(vv_assignments):
                    ob_id = assignment["obligation_id"]
                    if ob_id in override_map:
                        override = override_map[ob_id]
                        vv_assignments[i] = {
                            "obligation_id": ob_id,
                            "method": override["method"],
                            "rationale": override["rationale"],
                            "is_override": True,
                        }

            # Normalize rationale
            rationale = contract.get("rationale", {})
            if isinstance(rationale, str):
                rationale = {"narrative": rationale}
            if "narrative" not in rationale:
                rationale["narrative"] = ""

            # Collect deduplicated source requirement IDs from obligations (preserving order)
            requirement_ids: list[str] = list(dict.fromkeys(
                req_id
                for ob in obligations
                for req_id in ob.get("source_requirement_ids", [])
            ))

            content = {
                "name": contract["name"],
                "description": contract.get("description", ""),
                "status": "proposed",
                "component_id": contract["component_id"],
                "interface_id": contract["interface_id"],
                "obligations": obligations,
                "vv_assignments": vv_assignments,
                "rationale": rationale,
                "requirement_ids": requirement_ids,
                "gap_markers": contract.get("gap_markers", []),
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
                "contract-proposal", content, agent_id
            )
            proposal = self._api.read(result["slot_id"])
            if proposal is not None:
                created_proposals.append(proposal)

            override_count = sum(
                1 for a in vv_assignments if a.get("is_override")
            )
            logger.info(
                "Created contract proposal: %s (%s) with %d obligations, %d V&V overrides",
                contract["name"],
                result["slot_id"],
                len(obligations),
                override_count,
            )

        return created_proposals

    def format_preparation_summary(self, data: dict) -> str:
        """Format a human-readable summary of the prepared obligation data.

        Args:
            data: Output from prepare() containing components, interfaces,
                requirements, and gaps.

        Returns:
            Formatted summary string.
        """
        lines: list[str] = []
        lines.append("# Contract Derivation Data Summary")
        lines.append("")
        lines.append(
            f"- **Components:** {data['total_components']} approved"
        )
        lines.append(
            f"- **Interfaces:** {data['total_interfaces']} approved"
        )
        lines.append(
            f"- **Requirements:** {data['total_requirements']} mapped to components"
        )
        lines.append("")

        # Per-component details
        for comp in data.get("components", []):
            name = comp["component_name"]
            n_intf = len(comp["interfaces"])
            n_reqs = len(comp["requirements"])
            lines.append(f"## {name}")
            lines.append(f"Interfaces: {n_intf}, Requirements: {n_reqs}")

            if comp["interfaces"]:
                lines.append("Interfaces:")
                for intf in comp["interfaces"]:
                    intf_name = intf.get("name", intf["slot_id"])
                    direction = intf.get("direction", "unspecified")
                    lines.append(f"  - {intf_name} ({direction})")

            if comp["requirements_by_type"]:
                lines.append("Requirements by type:")
                for rtype, reqs in comp["requirements_by_type"].items():
                    lines.append(f"  - {rtype}: {len(reqs)}")

            if comp.get("has_gaps"):
                lines.append("  [!] Has gaps or incomplete data")

            lines.append("")

        # Gaps
        if data.get("gaps"):
            lines.append("## Gaps")
            for gap in data["gaps"]:
                lines.append(f"- {gap}")
            lines.append("")

        return "\n".join(lines)
