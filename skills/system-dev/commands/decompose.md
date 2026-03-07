# Decompose Command

## Trigger

`/system-dev:decompose`

## Purpose

Analyze ingested requirements and propose component groupings for the system architecture. This command prepares requirement data, runs gap detection, invokes Claude for structural analysis, and creates component-proposal slots through the Design Registry.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Requirements ingested (`/system-dev:ingest` completed)

## Workflow

### Step 1: Initialize Workspace

```python
import os
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.decomposition_agent import DecompositionAgent, check_stale_components

project_root = os.getcwd()
init_workspace(project_root)  # idempotent: creates if missing, cleans orphaned temps

workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")

api = SlotAPI(workspace_dir, schemas_dir)
agent = DecompositionAgent(api, schemas_dir)
```

### Step 2: Check for Stale Components

Before creating new proposals, check if any accepted components have requirements that changed since acceptance.

```python
stale = check_stale_components(api)
```

If stale components are found:
- Display each stale component with its name, stale reason, and affected requirement IDs
- Ask the user whether to proceed with decomposition or address stale components first
- If user chooses not to proceed, exit with guidance

### Step 3: Prepare Requirement Data

```python
data = agent.prepare()
```

This returns requirements, needs, gap_report, and by_source_block.

### Step 4: Check Gap Severity

If `data["gap_report"]["severity"] == "high"`:
- Show the gap summary: total requirements, missing descriptions, incomplete slots
- Ask the user whether to proceed despite significant gaps
- If user chooses not to proceed, exit with guidance to address gaps first

If severity is "medium", note the gaps but proceed.

### Step 5: Analyze Requirements

Using the instructions from `agents/structural-decomposition.md`:
- Read the prepared requirement data
- Group requirements by functional coherence and data affinity
- Determine component count from natural clustering
- Produce component groupings with rationale and evidence

### Step 6: Create Proposals

```python
import uuid

session_id = f"decompose-{uuid.uuid4()}"
proposals = agent.create_proposals(components, session_id)
```

Where `components` is the JSON array produced in Step 5.

### Step 7: Show Coverage Summary

```python
total_reqs = data["gap_report"]["total_requirements"]
summary = agent.format_coverage_summary(proposals, total_reqs)
print(summary)
```

### Step 8: Show Proposals

```python
narrative = agent.format_proposal_narrative(proposals)
print(narrative)
```

### Step 9: Next Steps

Inform the user:
- Proposals have been created in the Design Registry with status "proposed"
- Run `/system-dev:approve` to review and accept/reject/modify proposals
- Accepted proposals become committed component slots

## Reference Scripts

- `scripts/decomposition_agent.py` -- DecompositionAgent, detect_requirement_gaps, check_stale_components
- `scripts/registry.py` -- SlotAPI for all persistence
- `scripts/init_workspace.py` -- workspace initialization
- `agents/structural-decomposition.md` -- Claude analysis instructions
