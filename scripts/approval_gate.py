"""Generic approval gate engine for proposal state transitions.

Provides a configuration-driven approval gate that validates state transitions
against declarative JSON rules and executes accept/reject/modify operations
through SlotAPI. The gate is generic -- it knows nothing about component-specific
fields and works with any proposal type.

References:
    APPR-01 (approval gate), APPR-02 (state transitions),
    APPR-03 (atomic persistence), APPR-04 (batch operations)
"""

import json
import logging
from datetime import datetime, timezone

from scripts.registry import SlotAPI

logger = logging.getLogger(__name__)


def load_approval_rules(rules_path: str) -> dict:
    """Load and return the approval rules JSON config.

    Args:
        rules_path: Path to the approval-rules.json file.

    Returns:
        Parsed rules dict with states, transitions, and overrides.

    Raises:
        FileNotFoundError: If the rules file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(rules_path) as f:
        return json.load(f)


def validate_transition(
    rules: dict, current_state: str, action: str, decision_data: dict
) -> tuple[bool, str]:
    """Check if a state transition is valid per the approval rules config.

    Validates that the current state allows the given action, that the
    state is not terminal, and that all required fields are present in
    decision_data.

    Args:
        rules: The loaded approval rules dict.
        current_state: The proposal's current status (e.g., "proposed").
        action: The action to perform (e.g., "accept", "reject", "modify").
        decision_data: Dict with action-specific data fields.

    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty.
    """
    states = rules.get("states", {})

    if current_state not in states:
        return False, f"Unknown state: '{current_state}'"

    state_config = states[current_state]

    if state_config.get("terminal", False):
        return False, f"State '{current_state}' is terminal; no transitions allowed"

    transitions = state_config.get("transitions", {})
    if action not in transitions:
        valid_actions = list(transitions.keys())
        return False, (
            f"Action '{action}' not valid from state '{current_state}'. "
            f"Valid actions: {valid_actions}"
        )

    transition = transitions[action]
    required_fields = transition.get("required_fields", [])
    missing = [f for f in required_fields if f not in decision_data]
    if missing:
        return False, f"Missing required fields for '{action}': {missing}"

    return True, ""


class ApprovalGate:
    """Generic approval gate engine driven by declarative JSON config.

    Processes accept/reject/modify decisions on proposals through SlotAPI.
    The gate is not coupled to any specific proposal type -- it uses the
    proposal_type parameter for queries and derives the committed slot type
    by stripping the "-proposal" suffix.

    Args:
        api: SlotAPI instance for all persistence operations.
        rules_path: Path to the approval-rules.json config file.
        proposal_type: The slot type name for proposals (e.g., "component-proposal").
    """

    def __init__(self, api: SlotAPI, rules_path: str, proposal_type: str):
        self._api = api
        self._rules = load_approval_rules(rules_path)
        self._proposal_type = proposal_type
        # Derive committed slot type: "component-proposal" -> "component"
        if proposal_type.endswith("-proposal"):
            self._committed_type = proposal_type[: -len("-proposal")]
        else:
            self._committed_type = proposal_type

    def decide(
        self,
        proposal_id: str,
        action: str,
        decision_data: dict,
        agent_id: str = "approval-gate",
    ) -> dict:
        """Process a single approval decision on a proposal.

        Loads the proposal, validates the transition, and executes the action.
        For accept: creates the committed slot FIRST, then updates the proposal.
        All SlotAPI writes complete before returning (APPR-03).

        Args:
            proposal_id: The slot_id of the proposal to decide on.
            action: One of "accept", "reject", "modify", "re_propose".
            decision_data: Action-specific data (e.g., rejection_rationale,
                modifications, notes).
            agent_id: Identifier of the deciding agent.

        Returns:
            Dict with proposal_id, action, new_status, and optionally
            committed_slot_id (for accept actions).

        Raises:
            KeyError: If proposal_id does not exist.
            ValueError: If the transition is invalid.
        """
        proposal = self._api.read(proposal_id)
        if proposal is None:
            raise KeyError(f"Proposal not found: '{proposal_id}'")

        current_state = proposal["status"]
        is_valid, error_msg = validate_transition(
            self._rules, current_state, action, decision_data
        )
        if not is_valid:
            raise ValueError(
                f"Invalid transition for proposal '{proposal_id}': {error_msg}"
            )

        now = datetime.now(timezone.utc).isoformat()
        result = {
            "proposal_id": proposal_id,
            "action": action,
        }

        if action == "accept":
            result.update(self._handle_accept(proposal, decision_data, now, agent_id))
        elif action == "reject":
            result.update(self._handle_reject(proposal, decision_data, now, agent_id))
        elif action == "modify":
            result.update(self._handle_modify(proposal, decision_data, now, agent_id))
        elif action == "re_propose":
            result.update(
                self._handle_re_propose(proposal, decision_data, now, agent_id)
            )
        else:
            raise ValueError(f"Unknown action: '{action}'")

        logger.info(
            "Processed decision: proposal=%s action=%s new_status=%s",
            proposal_id,
            action,
            result.get("new_status"),
        )
        return result

    # Fields managed by SlotAPI -- never copy to committed slot
    _SYSTEM_FIELDS = {"slot_id", "slot_type", "version", "created_at", "updated_at"}
    # Fields specific to proposal lifecycle -- not part of committed content
    _PROPOSAL_ONLY_FIELDS = {"decision", "proposal_session_id", "status"}

    def _handle_accept(
        self, proposal: dict, decision_data: dict, now: str, agent_id: str
    ) -> dict:
        """Accept a proposal: create committed slot FIRST, then update proposal.

        The committed slot is created before the proposal is updated to ensure
        atomic ordering -- if the proposal update fails, the committed slot
        still exists (Pitfall 2 prevention).

        Uses generic field-copy: all proposal fields except system fields and
        proposal-only fields are passed through to the committed slot. This
        means interface-proposal fields (direction, data_format_schema, etc.)
        and contract-proposal fields (obligations, vv_assignments, etc.)
        automatically transfer without hardcoded mapping.
        """
        # Build committed slot content via generic field-copy
        excluded = self._SYSTEM_FIELDS | self._PROPOSAL_ONLY_FIELDS
        committed_content = {
            k: v for k, v in proposal.items() if k not in excluded
        }
        committed_content["status"] = "approved"

        # Create committed slot FIRST (atomic ordering)
        create_result = self._api.create(
            self._committed_type, committed_content, agent_id
        )
        committed_slot_id = create_result["slot_id"]

        # Now update the proposal with decision info
        updated_proposal = dict(proposal)
        updated_proposal["status"] = "accepted"
        updated_proposal["decision"] = {
            "action": "accept",
            "decided_by": "developer",
            "decided_at": now,
            "notes": decision_data.get("notes"),
            "rejection_rationale": None,
            "modifications": None,
            "committed_slot_id": committed_slot_id,
        }

        self._api.update(
            proposal["slot_id"],
            updated_proposal,
            expected_version=proposal["version"],
            agent_id=agent_id,
        )

        return {
            "new_status": "accepted",
            "committed_slot_id": committed_slot_id,
        }

    def _handle_reject(
        self, proposal: dict, decision_data: dict, now: str, agent_id: str
    ) -> dict:
        """Reject a proposal: update status and record rejection rationale."""
        updated_proposal = dict(proposal)
        updated_proposal["status"] = "rejected"
        updated_proposal["decision"] = {
            "action": "reject",
            "decided_by": "developer",
            "decided_at": now,
            "notes": decision_data.get("notes"),
            "rejection_rationale": decision_data["rejection_rationale"],
            "modifications": None,
            "committed_slot_id": None,
        }

        self._api.update(
            proposal["slot_id"],
            updated_proposal,
            expected_version=proposal["version"],
            agent_id=agent_id,
        )

        return {"new_status": "rejected"}

    def _handle_modify(
        self, proposal: dict, decision_data: dict, now: str, agent_id: str
    ) -> dict:
        """Modify a proposal: apply modifications and update status."""
        modifications = decision_data["modifications"]
        updated_proposal = dict(proposal)

        # Apply modifications as shallow merge on proposal fields
        for key, value in modifications.items():
            # Do not allow overwriting system fields
            if key not in ("slot_id", "slot_type", "version", "created_at", "updated_at"):
                updated_proposal[key] = value

        updated_proposal["status"] = "modified"
        updated_proposal["decision"] = {
            "action": "modify",
            "decided_by": "developer",
            "decided_at": now,
            "notes": decision_data.get("notes"),
            "rejection_rationale": None,
            "modifications": modifications,
            "committed_slot_id": None,
        }

        self._api.update(
            proposal["slot_id"],
            updated_proposal,
            expected_version=proposal["version"],
            agent_id=agent_id,
        )

        return {"new_status": "modified"}

    def _handle_re_propose(
        self, proposal: dict, decision_data: dict, now: str, agent_id: str
    ) -> dict:
        """Re-propose a rejected proposal: reset status and clear decision."""
        updated_proposal = dict(proposal)
        updated_proposal["status"] = "proposed"
        updated_proposal["decision"] = {
            "action": None,
            "decided_by": None,
            "decided_at": None,
            "notes": None,
            "rejection_rationale": None,
            "modifications": None,
            "committed_slot_id": None,
        }

        self._api.update(
            proposal["slot_id"],
            updated_proposal,
            expected_version=proposal["version"],
            agent_id=agent_id,
        )

        return {"new_status": "proposed"}

    def batch_decide(
        self,
        decisions: list[dict],
        agent_id: str = "approval-gate",
    ) -> list[dict]:
        """Process multiple approval decisions sequentially.

        Each decision is a dict with proposal_id, action, and decision_data.
        If one fails, processing stops and results so far plus the error
        are returned. A batch journal entry is logged via SlotAPI.

        Args:
            decisions: List of decision dicts, each with:
                - proposal_id: str
                - action: str
                - decision_data: dict
            agent_id: Identifier of the deciding agent.

        Returns:
            List of result dicts from each decide() call. If an error
            occurred, the last entry has an "error" key.
        """
        results = []
        for decision in decisions:
            try:
                result = self.decide(
                    proposal_id=decision["proposal_id"],
                    action=decision["action"],
                    decision_data=decision.get("decision_data", {}),
                    agent_id=agent_id,
                )
                results.append(result)
            except (KeyError, ValueError) as e:
                results.append(
                    {
                        "proposal_id": decision.get("proposal_id"),
                        "action": decision.get("action"),
                        "error": str(e),
                    }
                )
                logger.warning(
                    "Batch decide stopped at proposal %s: %s",
                    decision.get("proposal_id"),
                    e,
                )
                break

        logger.info(
            "Batch decide completed: %d/%d processed",
            len(results),
            len(decisions),
        )
        return results

    def get_pending(self) -> list[dict]:
        """Query proposals in actionable states (proposed or modified).

        Returns:
            List of proposal dicts with status "proposed" or "modified".
        """
        proposed = self._api.query(self._proposal_type, {"status": "proposed"})
        modified = self._api.query(self._proposal_type, {"status": "modified"})
        return proposed + modified
