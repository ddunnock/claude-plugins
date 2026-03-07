# Contract Command

## Trigger

`/system-dev:contract`

## Purpose

Derive behavioral contracts with INCOSE-style obligations and V&V assignments for approved components. This command checks for stale contracts, prepares component/interface/requirement data, invokes Claude for obligation derivation, and creates contract-proposal slots through the Design Registry.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Requirements ingested (`/system-dev:ingest` completed)
- Components decomposed and approved (`/system-dev:decompose` + `/system-dev:approve` completed)
- Interfaces resolved and approved (`/system-dev:resolve` + `/system-dev:approve` completed)

## Workflow

### Step 1: Initialize Workspace

```python
import os
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.contract_agent import ContractAgent, check_stale_contracts

project_root = os.getcwd()
init_workspace(project_root)  # idempotent: creates if missing, cleans orphaned temps

workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")
vv_rules_path = os.path.join(os.path.dirname(__file__), "..", "data", "vv-rules.json")

api = SlotAPI(workspace_dir, schemas_dir)
agent = ContractAgent(api, schemas_dir, vv_rules_path)
```

### Step 2: Check for Stale Contracts

Before creating new proposals, check if any approved contracts have interfaces that changed since the contract was accepted.

```python
stale = check_stale_contracts(api)
```

If stale contracts are found:
- Display each stale contract with its name, reason, and affected interface ID
- Log the stale contracts for inclusion in the re-proposal batch
- Ask the user whether to proceed with contract derivation or address stale contracts first
- If user chooses not to proceed, exit with guidance

### Step 3: Prepare Obligation Data

```python
data = agent.prepare()
summary = agent.format_preparation_summary(data)
print(summary)
```

This returns approved components with their interfaces and requirements, organized for obligation derivation. The summary shows component counts, interface pairings, and requirement groupings.

### Step 4: Check Data Completeness

If `data["gaps"]` is non-empty:
- Show the gap list: components with missing requirements or no interfaces
- Ask the user whether to proceed despite gaps
- If proceeding, gap markers will be included in the contract proposals

If no approved components exist, exit with guidance to run decompose and approve first.

### Step 5: Derive Behavioral Obligations

Using the instructions from `agents/behavioral-contract.md`:
- Read the prepared obligation data
- For each component-interface pair, derive INCOSE-style behavioral obligations
- Classify each obligation by type (data_processing, state_management, error_handling, etc.)
- Assign error_category for error-related obligations
- Provide vv_overrides for any obligations where the default V&V method is inappropriate
- Write rationale with narrative explaining the derivation logic

### Step 6: Create Contract Proposals

```python
import uuid

session_id = f"contract-{uuid.uuid4()}"
proposals = agent.create_proposals(contracts, session_id)
```

Where `contracts` is the JSON array produced in Step 5. The agent automatically:
- Assigns default V&V methods from vv-rules.json per obligation type
- Merges Claude's vv_overrides over defaults (is_override=True)
- Creates contract-proposal slots through SlotAPI

### Step 7: Report Results

```python
total_obligations = sum(len(p.get("obligations", [])) for p in proposals)
total_overrides = sum(
    sum(1 for a in p.get("vv_assignments", []) if a.get("is_override"))
    for p in proposals
)
stale_count = len(stale)

print(f"Created {len(proposals)} contract proposals")
print(f"Total obligations: {total_obligations}")
print(f"V&V overrides: {total_overrides}")
if stale_count:
    print(f"Stale contracts flagged: {stale_count}")
```

Output format: Structured summary with proposal count, obligation count, override count, and stale alerts.

### Step 8: Next Steps

Inform the user:
- Contract proposals have been created in the Design Registry with status "proposed"
- Each proposal bundles obligations and V&V assignments together
- Run `/system-dev:approve` to review and accept/reject/modify proposals
- Accepted proposals become committed contract slots with finalized V&V assignments

## Error Handling

- If no approved components exist: exit with guidance to run decompose workflow first
- If no approved interfaces exist: exit with guidance to run resolve workflow first
- If some components lack sufficient data: create partial proposals with gap markers
- If stale contracts found: log and include in report, but do not block new derivation

## Reference Scripts

- `scripts/contract_agent.py` -- ContractAgent, assign_vv_methods, check_stale_contracts, load_vv_rules
- `scripts/registry.py` -- SlotAPI for all persistence
- `scripts/approval_gate.py` -- ApprovalGate for contract-proposal acceptance
- `scripts/init_workspace.py` -- workspace initialization
- `agents/behavioral-contract.md` -- Claude obligation derivation instructions
- `data/vv-rules.json` -- V&V method defaults per obligation type
