# Interface Command

## Trigger

`/system-dev:interface`

## Purpose

Discover and propose interfaces between approved components. This command checks for stale interfaces, discovers boundary candidates from component relationships and requirement cross-references, invokes Claude for enrichment with protocol/data-format details, and creates interface-proposal slots through the Design Registry.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Requirements ingested (`/system-dev:ingest` completed)
- Components decomposed and approved (`/system-dev:decompose` + `/system-dev:approve` completed)

## Workflow

### Step 1: Initialize Workspace

```python
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.interface_agent import InterfaceAgent, check_stale_interfaces

import os

project_root = os.getcwd()
workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")

api = SlotAPI(workspace_dir, schemas_dir)
agent = InterfaceAgent(api, schemas_dir)
```

### Step 2: Check for Stale Interfaces

Before discovering new candidates, check if any approved interfaces have components that changed since the interface was last updated.

```python
stale = check_stale_interfaces(api)
```

If stale interfaces are found:
- Display each stale interface with its name, reason, and which component changed
- Log them for inclusion in the re-proposal batch alongside new candidates
- Stale interfaces are automatically included in re-proposal (no separate --refresh flag)

### Step 3: Discover Interface Candidates

```python
data = agent.prepare()
```

This returns candidates, orphan_components, component_count, and candidate_count.

### Step 4: Display Preparation Summary

```python
summary = agent.format_preparation_summary(data)
print(summary)
```

Shows discovered candidates with their discovery method (relationship or requirement_crossref) and any orphan components that have no interface boundaries.

### Step 5: Enrich Candidates with Claude

Using the instructions from `agents/interface-resolution.md`:
- Read the prepared candidate data including source/target components, relationship types, shared requirements
- For each candidate, determine direction (unidirectional or bidirectional)
- Assign protocol (function_call, event, shared_state, message_passing)
- Create data_format_schema with concrete JSON snippets showing expected data shapes
- Define error_categories with named categories and expected_behavior per category
- Name each interface using "{source}-to-{target}: {purpose}" convention
- Write rationale with narrative and discovery_method

### Step 6: Validate and Create Proposals

```python
import uuid

session_id = f"interface-{uuid.uuid4()}"
proposals = agent.create_proposals(enriched_interfaces, session_id)
```

Where `enriched_interfaces` is the JSON array produced in Step 5.

If some candidates fail validation, create proposals for valid ones and attach gap markers to failures for partial output.

### Step 7: Report Results

Display a structured summary:
- N interface proposals created
- M orphan components detected (components with no interface boundaries)
- K stale interfaces flagged for re-proposal

```
Interface Resolution Complete:
  Proposals created: {len(proposals)}
  Orphan components: {len(data['orphan_components'])}
  Stale interfaces: {len(stale)}
```

### Step 8: Next Steps

Inform the user:
- Interface proposals have been created in the Design Registry with status "proposed"
- Run `/system-dev:approve` to review and accept/reject/modify interface proposals
- Accepted proposals become committed interface slots
- Orphan components may need manual interface definition or may be standalone

## Error Handling

- If no approved components exist, exit with guidance to run `/system-dev:decompose` first
- If no candidates are discovered, report zero candidates and list all components as orphans
- Partial output with gap markers if some candidates fail validation during proposal creation

## Reference Scripts

- `scripts/interface_agent.py` -- InterfaceAgent, discover_interface_candidates, check_stale_interfaces, detect_orphan_components
- `scripts/registry.py` -- SlotAPI for all persistence
- `scripts/approval_gate.py` -- ApprovalGate for interface-proposal decisions
- `agents/interface-resolution.md` -- Claude analysis instructions for interface enrichment
