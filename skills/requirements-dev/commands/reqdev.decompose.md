---
name: reqdev:decompose
description: Decompose baselined blocks into sub-blocks with requirement allocation
---

# /reqdev:decompose - Subsystem Decomposition

Decomposes a baselined system-level block into sub-blocks, allocates parent requirements to sub-blocks, and validates allocation coverage. Sub-blocks then become available for requirements development via `/reqdev:requirements`.

## Prerequisites

- Block requirements must be baselined (run `/reqdev:deliver` first)
- Read `${CLAUDE_PLUGIN_ROOT}/references/decomposition-guide.md` for guidance on decomposition patterns

## Procedure

### Step 1: Select Block to Decompose

Ask the user which block to decompose. Show available blocks from `state.json`:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-baseline --block <block-name>
```

If the block is NOT fully baselined, inform the user:
> Block "{block-name}" has requirements that are not baselined. Run `/reqdev:deliver` to baseline all requirements before decomposing.

### Step 2: Check Decomposition Level

Determine the current level of the block (from `state.json blocks[block-name].level`, default 0) and verify further decomposition is allowed:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev check-level --level <current-level>
```

If NOT allowed (would exceed max_level=3):
> Block "{block-name}" is at level {current-level}. Further decomposition would exceed the maximum depth of 3 levels. You can override this limit in state.json if needed.

If at max_level - 1, warn:
> Note: This will create level {current-level + 1} sub-blocks. One more level of decomposition remains after this.

### Step 3: Identify Sub-Blocks

Guide the user through identifying sub-functions within the block. Reference `decomposition-guide.md` for patterns:

> Looking at the requirements for "{block-name}", let's identify distinct sub-functions.
> Consider: processing stages, data domains, independent failure modes, or API boundaries.

For each sub-block, capture:
- **Name:** Short identifier (e.g., "graph-engine")
- **Description:** What this sub-block is responsible for

Present a summary table for user approval:

```
Proposed Sub-Blocks for "{block-name}":
| # | Name | Description |
|---|------|-------------|
| 1 | graph-engine | Graph data structure and traversal |
| 2 | cycle-detector | Circular dependency detection |
| 3 | critical-path-calc | Critical path computation |

Approve? (yes/edit/add more)
```

### Step 4: Register Sub-Blocks

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev register-sub-blocks \
    --parent <block-name> \
    --sub-blocks '[{"name": "graph-engine", "description": "..."}, ...]' \
    --level <current-level + 1>
```

### Step 5: Allocate Requirements

For each parent requirement in the block, present it and ask which sub-block(s) it allocates to:

> **REQ-001:** "The system shall track dependency graphs"
> Allocate to which sub-block(s)? [graph-engine / cycle-detector / critical-path-calc / multiple]

For each allocation:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev allocate \
    --requirement REQ-001 --sub-block graph-engine \
    --rationale "Graph traversal is the core capability of this sub-block"
```

A requirement can be allocated to multiple sub-blocks if it spans concerns.

### Step 6: Validate Allocation Coverage

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-coverage --block <block-name>
```

If coverage < 100%:
> The following requirements are not allocated to any sub-block:
> - REQ-xxx: "statement"
> - REQ-yyy: "statement"
> Please allocate these requirements before proceeding.

Loop back to Step 5 for unallocated requirements.

### Step 7: Update Decomposition State

After 100% coverage:

```bash
# State is updated by register-sub-blocks and allocation commands
```

### Step 8: Summary

```
Decomposition Complete
----------------------
Parent block:    {block-name} (level {current-level})
Sub-blocks:      {count} created at level {current-level + 1}
  - {sub-block-1}: {description}
  - {sub-block-2}: {description}
  - ...
Allocation:      {count}/{total} requirements allocated (100%)

Sub-blocks are now available as blocks in /reqdev:requirements.
Next: Run /reqdev:requirements to develop requirements for each sub-block.
```

Offer to start requirements development for a sub-block immediately:
> Would you like to start developing requirements for one of the sub-blocks now?
