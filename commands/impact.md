# Impact Command

## Trigger

`/system-dev:impact`

## Purpose

Compute change impact (blast radius) from any design element, showing forward and backward propagation paths through the traceability graph. Displays a hierarchical tree view of all affected elements and persists the analysis as an impact-analysis slot for future reference.

## Prerequisites

- Workspace initialized (`/system-dev:init` completed)
- Requirements ingested (`/system-dev:ingest` completed)
- At least some design elements exist (components, interfaces, or contracts)

## Usage

```
/system-dev:impact <element_id>
```

### Optional Flags

- `--direction forward|backward|both` (default: forward)
- `--depth N` (default: unlimited)
- `--type component,interface,contract` (comma-separated filter, default: all types shown)

## Workflow

### Step 1: Initialize Workspace

```python
from scripts.init_workspace import init_workspace
from scripts.registry import SlotAPI
from scripts.traceability_agent import TraceabilityAgent

import os

project_root = os.getcwd()
workspace_dir = os.path.join(project_root, ".system-dev")
schemas_dir = os.path.join(os.path.dirname(__file__), "..", "schemas")

api = SlotAPI(workspace_dir, schemas_dir)
agent = TraceabilityAgent(api)
```

### Step 2: Parse User Input

Parse the element_id and optional flags from user input:

```python
element_id = args.element_id  # e.g., "requirement:REQ-001" or "comp-abc123"

# Parse optional flags
direction = args.direction or "forward"    # forward | backward | both
depth_limit = int(args.depth) if args.depth else None
type_filter = args.type.split(",") if args.type else None
```

### Step 3: Build or Refresh Traceability Graph

Ensure the graph is fresh before computing impact:

```python
graph_slot = agent.build_or_refresh()
```

### Step 4: Compute Impact

```python
result = agent.compute_impact(
    element_id,
    direction=direction,
    depth_limit=depth_limit,
    type_filter=type_filter,
)
```

If the element is not found, the result will contain gap_markers indicating the element was not in the registry.

### Step 5: Persist Impact Analysis

Save the impact analysis result as a slot for future reference:

```python
persisted = agent.persist_impact(result)
impact_slot_id = persisted["slot_id"]
```

### Step 6: Display Results

```python
output = agent.format_impact_output(result)
print(output)
```

The output shows:
1. **Source element and direction** at the top
2. **Graph coverage percentage** indicating analysis completeness
3. **Hierarchical tree view** from the source element outward
4. **Affected count** summary at the bottom
5. **Uncertainty markers** when graph coverage < 100%
6. **Type filter note** when filtering was applied

### Step 7: Report Slot Reference

```python
print(f"\nImpact analysis saved as: {impact_slot_id}")
print("Use /system-dev:query to retrieve this analysis later.")
```

## Error Handling

- If workspace not initialized: exit with guidance to run `/system-dev:init`
- If element_id not found: report "Element '{element_id}' not found in design registry. Use /system-dev:query to find valid element IDs."
- If no design elements exist: exit with "No design elements found. Run /system-dev:ingest and /system-dev:decompose first."
- If graph build fails: report the error with details

## Example Output

```
# Impact Analysis: requirement:REQ-001

**Direction:** forward
**Graph coverage:** 85.7%

requirement:REQ-001
|-- comp-abc123 (component: Auth Service) [allocated_to]
|   |-- intf-def456 (interface: Auth-Gateway) [boundary_of]
|   |   `-- cntr-ghi789 (contract: Auth Protocol) [constrained_by]
|   |       `-- vv:cntr-ghi789:OBL-01 (vv: Test Auth) [verified_by]
|   `-- cntr-jkl012 (contract: Auth Behavior) [constrained_by]
`-- comp-mno345 (component: Session Service) [allocated_to]

**Total affected elements:** 6

**Uncertainty:** 2 elements not reachable (coverage 85.7%)
```

## Reference Scripts

- `scripts/traceability_agent.py` -- TraceabilityAgent with compute_impact(), persist_impact(), format_impact_output()
- `scripts/registry.py` -- SlotAPI for all slot access
- `scripts/trace_validator.py` -- Write-time trace enforcement
- `scripts/init_workspace.py` -- workspace initialization
