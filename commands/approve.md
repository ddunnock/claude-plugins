# Approve Command

## Trigger

`/system-dev:approve`

## Purpose

Review pending component proposals through the approval gate. Supports accept, reject, and modify operations with batch review. Rejected proposals can be automatically re-proposed with rejection rationale as additional context.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Proposals created (`/system-dev:decompose` completed)

## Workflow

### Step 1: Initialize Workspace

```python
from scripts.registry import SlotAPI
from scripts.approval_gate import ApprovalGate
from scripts.decomposition_agent import DecompositionAgent

import os

project_root = os.getcwd()
workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")
rules_path = os.path.join(os.path.dirname(__file__), "..", "data", "approval-rules.json")

api = SlotAPI(workspace_dir, schemas_dir)
gate = ApprovalGate(api, rules_path, "component-proposal")
```

### Step 2: Get Pending Proposals

```python
pending = gate.get_pending()
```

If no pending proposals:
- Inform the user there are no proposals awaiting review
- Suggest running `/system-dev:decompose` first if no proposals exist at all
- Exit

### Step 3: Batch Review

Present all pending proposals for batch review. Show each proposal with:
- Name and description
- Requirement count and IDs
- Rationale narrative
- Gap markers (if any)
- Relationships to other proposals
- Current status (proposed or modified)

### Step 4: Collect Decisions

For each proposal, the user chooses one action:

**Accept** -- Proposal becomes a committed component slot.
- No additional input required
- Optional: notes for the decision record

**Reject** -- Proposal is rejected with rationale.
- Required: rejection_rationale explaining why
- Optional: notes

**Modify** -- Proposal is updated before final decision.
Supported modifications:
- **Rename**: Change the component name
- **Scope change**: Add or remove requirement_ids
- **Split**: Divide one proposal into two (creates new proposals, rejects original)
- **Merge**: Combine two proposals into one (creates new merged proposal, rejects originals)
- **Edit description**: Update the component description
- **Edit rationale**: Update the rationale narrative

For modifications, provide a `modifications` dict with the changed fields.

### Step 5: Process Decisions

For individual decisions:
```python
result = gate.decide(proposal_id, action, decision_data)
```

For batch processing:
```python
decisions = [
    {"proposal_id": pid, "action": action, "decision_data": data}
    for pid, action, data in collected_decisions
]
results = gate.batch_decide(decisions)
```

### Step 6: Show Results

Display results for each decision:
- **Accepted**: Show the new component slot ID (committed_slot_id)
- **Rejected**: Show the rejection rationale recorded
- **Modified**: Show the modifications applied

### Step 7: Handle Rejections (Conversational Loop)

For rejected proposals, offer to re-propose:
- Use the rejection rationale as additional context for the decomposition agent
- Run a targeted re-decomposition with the rejection feedback
- Create new proposals that address the rejection concerns

```python
# Re-propose rejected proposals
for result in results:
    if result.get("new_status") == "rejected":
        # Re-propose: reset proposal to proposed state
        gate.decide(result["proposal_id"], "re_propose", {})
        # The user can then re-run decompose or manually adjust
```

### Step 8: Check for Remaining Proposals

If modified proposals remain (status "modified"), loop back to Step 3 to present them for final accept/reject.

### Step 9: Summary

Show final summary:
- Number of proposals accepted (with component slot IDs)
- Number rejected
- Number modified and pending further review
- Total requirements covered by accepted components

## Reference Scripts

- `scripts/approval_gate.py` -- ApprovalGate with decide/batch_decide/get_pending
- `scripts/decomposition_agent.py` -- DecompositionAgent for re-proposal support
- `scripts/registry.py` -- SlotAPI for all persistence
