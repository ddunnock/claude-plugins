# Trace Command

## Trigger

`/system-dev:trace`

## Purpose

Build and display end-to-end traceability chains from stakeholder needs through V&V assignments. This command constructs a traversable graph from all design registry slots, validates chain completeness, detects broken segments and orphan elements, and reports divergences between traceability-link slots and embedded fields.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Requirements ingested (`/system-dev:ingest` completed)
- At least some design elements exist (components, interfaces, or contracts)

## Workflow

### Step 1: Initialize Workspace

```python
import os
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.traceability_agent import TraceabilityAgent

project_root = os.getcwd()
init_workspace(project_root)  # idempotent: creates if missing, cleans orphaned temps

workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")

api = SlotAPI(workspace_dir, schemas_dir)
agent = TraceabilityAgent(api)
```

### Step 2: Build or Refresh Traceability Graph

The agent checks for an existing graph (singleton ID `tgraph-current`), rebuilds it if stale, or creates a new one if none exists. Staleness is determined by comparing the graph's `built_at` timestamp against the most recent `updated_at` across all traceable slot types.

```python
# Check if any design elements exist
has_elements = any(
    api.query(t) for t in ["component", "interface", "contract"]
)

if not has_elements and not api.query("need"):
    print("No design elements found. Run /system-dev:ingest and /system-dev:decompose first.")
    return

graph_slot = agent.build_or_refresh()
```

If no design elements or needs exist, exit with guidance.

### Step 3: Format and Display Trace Output

```python
output = agent.format_trace_output(graph_slot)
print(output)
```

The output shows:
1. **Completeness percentage** at the top
2. **Chain-per-need summary** with inline break indicators
3. **Gap report** with severity classification (critical/warning/info)
4. **Divergences** in a separate section (not mixed with gaps)
5. **Orphan elements** listed at bottom as info severity

### Step 4: Display Gap Report (if gaps detected)

If the chain report contains gaps:
- Show each gap with its severity level and the specific chain break point
- Critical gaps indicate chains fully broken at early levels (need to requirement or requirement to component)
- Warning gaps indicate partial chains that stop before reaching V&V
- Info gaps indicate orphan elements not connected to any chain

### Step 5: Display Divergences (if detected)

Divergences occur when the same pair of elements has different relationship types from different sources (traceability-link slot vs embedded field). These are shown in a separate section per the project's design decision.

### Step 6: Single-Need Filtering (optional)

If invoked with `--need NEED-001`:

```python
# Filter output to show only the chain for the specified need
need_id = f"need:{args.need}"
# The agent's format_trace_output handles the full graph;
# for single-need filtering, extract the relevant chain and re-format
```

Show only the chain for the specified need, with full detail including all downstream elements.

## Error Handling

- If workspace not initialized: exit with guidance to run `/system-dev:init`
- If no design elements exist: exit with "No design elements found. Run /system-dev:ingest and /system-dev:decompose first."
- If graph build fails: report the error with details
- If all chains are complete: celebrate with 100% completeness message

## Reference Scripts

- `scripts/traceability_agent.py` -- TraceabilityAgent for graph building, chain validation, staleness, formatting
- `scripts/registry.py` -- SlotAPI for all slot access
- `scripts/trace_validator.py` -- Write-time trace enforcement (complementary, runs on individual writes)
- `scripts/init_workspace.py` -- workspace initialization
