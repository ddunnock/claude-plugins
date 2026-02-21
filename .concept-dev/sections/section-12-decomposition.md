Now I have all the context needed. Let me generate the section content for section-12-decomposition.

# Section 12: Subsystem Decomposition

## Overview

This section implements the Phase 3 Subsystem Decomposer feature for the requirements-dev plugin. It adds the `/reqdev:decompose` command, decomposition state tracking in `state.json`, parent-to-child requirement allocation with coverage validation, and the `decomposition-guide.md` reference document.

The decomposer enables users to break down baselined system-level blocks into sub-blocks, allocate parent requirements to sub-blocks, validate allocation coverage, and then re-enter the requirements pipeline at the subsystem level.

## Dependencies

- **Section 01 (Plugin Scaffolding):** Plugin directory exists, `decomposition-guide.md` stub in `references/`
- **Section 02 (State Management):** `update_state.py` and `state.json` template with `decomposition` field already present
- **Section 06 (Requirements Engine):** `requirement_tracker.py` with baseline status support and `traceability.py` with `parent_of` and `allocated_to` link types
- **Section 10 (Validation Sweep):** Set validation logic used for re-entrant pipeline validation at subsystem level

## Tests First

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_decomposition.py`**

```python
"""Tests for subsystem decomposition logic.

Validates that the decomposition feature correctly enforces prerequisites
(baselined blocks), creates proper allocation traces, validates coverage,
manages decomposition levels, and enforces max_level limits.
"""

# Test: decompose requires block status "baselined"
# - Set up a block with all requirements at status "baselined"
# - Call decompose on that block
# - Verify it succeeds without error

# Test: decompose on non-baselined block raises error
# - Set up a block with requirements at status "registered" (not baselined)
# - Call decompose on that block
# - Verify it raises an error with a clear message about baseline requirement

# Test: allocation creates parent_of traces for each parent requirement
# - Set up a baselined block with 3 requirements (REQ-001, REQ-002, REQ-003)
# - Define 2 sub-blocks
# - Allocate REQ-001 to sub-block-a, REQ-002 to sub-block-b, REQ-003 to both
# - Verify traceability registry contains parent_of links:
#   REQ-001 -> sub-block-a, REQ-002 -> sub-block-b, REQ-003 -> sub-block-a, REQ-003 -> sub-block-b
# - Verify allocated_to links are also created

# Test: allocation coverage validation: flags requirements not allocated to any sub-block
# - Set up 3 baselined requirements
# - Allocate only 2 of them
# - Run coverage validation
# - Verify it returns a list containing the unallocated requirement ID
# - Verify it reports coverage < 100%

# Test: allocation coverage validation: passes when all requirements allocated
# - Set up 3 baselined requirements
# - Allocate all 3
# - Run coverage validation
# - Verify it returns empty list of unallocated requirements
# - Verify it reports coverage = 100% (1.0)

# Test: sub-blocks registered with level=1 in state.json
# - Decompose a level-0 block into 3 sub-blocks
# - Read state.json
# - Verify each sub-block entry has level: 1
# - Verify sub-blocks appear in state.json blocks dict

# Test: max_level=3 prevents decomposition beyond level 3
# - Set up a block at level 3 (already deeply decomposed)
# - Attempt to decompose it further
# - Verify it raises an error about exceeding max_level
# - Verify error message mentions that user override is available

# Test: decomposition state tracks parent_block and sub_blocks correctly
# - Decompose block "block-dependency-tracker" into ["graph-engine", "cycle-detector", "critical-path-calc"]
# - Read state.json decomposition.levels
# - Verify level "1" entry has:
#   parent_block: "block-dependency-tracker"
#   sub_blocks: ["graph-engine", "cycle-detector", "critical-path-calc"]
#   allocation_coverage: correct float value
```

## Implementation Details

### 1. Decomposition Logic Module

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/decompose.py`**

This script implements the core decomposition operations. It is a standalone Python script (stdlib only) that manages decomposition state, allocation, and coverage validation.

**Key functions (signatures and docstrings only):**

```python
"""Subsystem decomposition logic for requirements-dev plugin.

Manages block decomposition into sub-blocks, requirement allocation
to sub-blocks, coverage validation, and decomposition state tracking.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

def validate_baseline(workspace_path: str, block_name: str) -> bool:
    """Check that all requirements for the given block have status 'baselined'.

    Reads requirements_registry.json filtered by source_block == block_name.
    Returns True if all are baselined, False otherwise.
    Raises ValueError if block has no requirements.
    """

def check_max_level(workspace_path: str, current_level: int) -> bool:
    """Check whether decomposition at current_level + 1 would exceed max_level.

    Reads state.json decomposition.max_level (default 3).
    Returns True if allowed, False if would exceed.
    """

def register_sub_blocks(workspace_path: str, parent_block: str,
                        sub_blocks: list[dict], level: int) -> None:
    """Register sub-blocks in state.json.

    Each sub_block dict has: name, description, parent_block.
    Updates state.json:
    - Adds each sub-block to blocks dict with level field
    - Updates decomposition.levels with new level entry
    Uses atomic write (temp-file-then-rename).
    """

def allocate_requirement(workspace_path: str, requirement_id: str,
                         sub_block_name: str, rationale: str) -> None:
    """Allocate a parent requirement to a sub-block.

    Creates two traceability links via traceability.py:
    - allocated_to: requirement_id -> sub_block_name
    - parent_of: requirement_id -> (future child requirement placeholder)

    Stores rationale in the link metadata.
    Validates requirement_id exists and is baselined.
    """

def validate_allocation_coverage(workspace_path: str,
                                 parent_block: str) -> dict:
    """Check that every baselined requirement of parent_block is allocated.

    Returns dict with:
    - coverage: float (0.0 to 1.0)
    - allocated: list of requirement IDs that are allocated
    - unallocated: list of requirement IDs missing allocation
    - total: int count of parent requirements
    """

def update_decomposition_state(workspace_path: str, level: int,
                               parent_block: str, sub_blocks: list[str],
                               coverage: float) -> None:
    """Update the decomposition section in state.json.

    Sets decomposition.levels[str(level)] to:
    {
        "parent_block": parent_block,
        "sub_blocks": sub_blocks,
        "allocation_coverage": coverage
    }
    Uses atomic write.
    """
```

**CLI interface:**

```bash
# Validate that a block is ready for decomposition
python3 decompose.py validate-baseline --workspace .requirements-dev --block block-name

# Register sub-blocks
python3 decompose.py register-sub-blocks --workspace .requirements-dev \
    --parent block-name --sub-blocks '["graph-engine", "cycle-detector"]' --level 1

# Allocate a requirement to a sub-block
python3 decompose.py allocate --workspace .requirements-dev \
    --requirement REQ-001 --sub-block graph-engine --rationale "Graph traversal is core to this sub-block"

# Validate allocation coverage
python3 decompose.py validate-coverage --workspace .requirements-dev --block block-name

# Check if further decomposition is allowed
python3 decompose.py check-level --workspace .requirements-dev --level 2
```

### 2. Path Validation and Security

Follow the established codebase pattern. All CLI file path arguments go through `_validate_path()` which rejects `..` traversal and restricts extensions. The workspace path argument uses `_validate_dir_path()` for directory-only validation.

```python
def _validate_dir_path(path_str: str) -> str:
    """Validate directory path: reject traversal, return resolved path."""
    resolved = os.path.realpath(path_str)
    if ".." in os.path.normpath(path_str):
        print("Error: path traversal not allowed", file=sys.stderr)
        sys.exit(1)
    return resolved
```

### 3. Decomposition State in `state.json`

The `state.json` template (from Section 02) already includes the decomposition field:

```json
"decomposition": {
    "levels": {},
    "max_level": 3
}
```

After decomposing a block, this becomes:

```json
"decomposition": {
    "levels": {
        "0": { "blocks_baselined": true },
        "1": {
            "parent_block": "block-dependency-tracker",
            "sub_blocks": ["graph-engine", "cycle-detector", "critical-path-calc"],
            "allocation_coverage": 1.0
        }
    },
    "max_level": 3
}
```

When sub-blocks are registered, they are added to the top-level `blocks` dict in `state.json` with their `level` field set appropriately. This makes them visible to the Block Requirements Engine (`/reqdev:requirements`), which treats them as new blocks to process through the standard type-guided passes.

### 4. Integration with Traceability Engine

The decomposition module calls `traceability.py` (from Section 06) to create links. It uses two link types:

- **`allocated_to`**: `REQ-xxx` -> sub-block name. Records which sub-block a parent requirement is allocated to.
- **`parent_of`**: `REQ-xxx` -> `REQ-yyy`. Created later when sub-block requirements are written, linking parent requirements to their child derivations (INCOSE attribute A2).

The `allocated_to` links are created during the `/reqdev:decompose` workflow. The `parent_of` links are created during `/reqdev:requirements` when the user writes sub-block requirements and traces them back to parent requirements.

### 5. Re-entrant Pipeline Validation

After sub-blocks are registered, the user runs `/reqdev:requirements` on each sub-block. The Block Requirements Engine, Quality Checker, V&V Planner, and Traceability Engine operate identically at any level. The differences are:

- The `level` field in new requirement records is set to 1 (or deeper) instead of 0
- Parent-to-child traces (`parent_of` links) connect the sub-block requirements to their parent requirements
- Sub-block requirements inherit the parent block's source traceability (concept-dev references carry forward)

No special code changes are needed in the requirements engine scripts. The `level` field is already part of the Requirement dataclass (Section 06), and the traceability engine already supports `parent_of` links.

The set validator (Section 10) should also work at the sub-block level to check interface coverage between sub-blocks, duplicate detection, and terminology consistency within the decomposed block.

### 6. The `/reqdev:decompose` Command

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.decompose.md`**

This command prompt orchestrates the decomposition workflow. It instructs Claude to:

1. Ask the user which block to decompose
2. Verify the block's requirements are all baselined (call `decompose.py validate-baseline`)
3. Check that decomposition level is within `max_level` (call `decompose.py check-level`)
4. Guide the user through identifying sub-functions/sub-blocks:
   - For each sub-block: name, description, parent block reference
   - Present summary table for approval
5. Register sub-blocks (call `decompose.py register-sub-blocks`)
6. For each parent requirement in the block:
   - Present the requirement statement
   - Ask user which sub-block(s) it allocates to, with rationale
   - Create allocation (call `decompose.py allocate`)
7. Validate allocation coverage (call `decompose.py validate-coverage`)
   - If coverage < 100%: show unallocated requirements, prompt user to allocate them
   - If coverage = 100%: confirm and proceed
8. Inform user that sub-blocks are now available as blocks in `/reqdev:requirements`
9. Offer to start requirements development for a sub-block immediately

**Key prompt elements:**

- The command reads `references/decomposition-guide.md` for guidance on decomposition patterns
- It enforces the prerequisite check (baselined block) before proceeding
- It warns at max_level - 1 that the user is approaching the depth limit
- It requires explicit user override to exceed max_level (the command asks "Are you sure you want to decompose beyond level 3?")

### 7. Decomposition Guide Reference

**File: `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/references/decomposition-guide.md`**

This reference document provides guidance consumed by the `/reqdev:decompose` command. Content should cover:

- **When to decompose:** A block is a candidate for decomposition when it has more than 15-20 requirements, when requirements span clearly distinct sub-functions, or when the block's scope is too broad for a single implementation unit.
- **How to identify sub-functions:** Look for distinct processing stages, separate data domains, independent failure modes, different performance profiles, or natural API boundaries within the block.
- **Allocation rationale templates:** Provide structured templates for explaining why a requirement maps to a specific sub-block. Example: "REQ-xxx allocates to [sub-block] because [sub-block] is responsible for [capability] which directly implements [requirement's core function]."
- **Stopping conditions:** Do not decompose further when sub-blocks have fewer than 5 requirements each, when sub-functions are atomic (cannot be meaningfully subdivided), or when the max_level limit is reached.
- **Common decomposition patterns:** Pipeline decomposition (sequential processing stages), layer decomposition (abstraction layers), feature decomposition (independent feature modules), data decomposition (by data domain).

### 8. Atomic Write Pattern

All state mutations in `decompose.py` follow the atomic write pattern established across the codebase:

```python
import tempfile

def _atomic_write(filepath: str, data: dict) -> None:
    """Write JSON data atomically using temp-file-then-rename."""
    dir_path = os.path.dirname(filepath)
    with tempfile.NamedTemporaryFile(mode='w', dir=dir_path,
                                      suffix='.tmp', delete=False) as f:
        json.dump(data, f, indent=2)
        tmp_path = f.name
    os.replace(tmp_path, filepath)
```

## File Summary

| File | Action | Description |
|------|--------|-------------|
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/tests/test_decomposition.py` | Create | Test suite for decomposition logic (8 test stubs) |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/scripts/decompose.py` | Create | Core decomposition logic: validation, allocation, coverage, state tracking |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/commands/reqdev.decompose.md` | Create | Command prompt for the `/reqdev:decompose` workflow |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/references/decomposition-guide.md` | Create/Update | Reference content on decomposition patterns, stopping conditions, rationale templates |
| `/Users/dunnock/projects/claude-plugins/skills/requirements-dev/templates/state.json` | No change | Already contains `decomposition` field from Section 02 |

## Implementation Checklist

1. Write `tests/test_decomposition.py` with all 8 test stubs fleshed out using pytest fixtures
2. Create `conftest.py` fixtures for test workspace setup (state.json, requirements_registry.json, traceability_registry.json with sample baselined requirements)
3. Implement `scripts/decompose.py` with all functions and CLI subcommands
4. Write `commands/reqdev.decompose.md` command prompt
5. Write `references/decomposition-guide.md` reference content
6. Run tests to verify all 8 pass
7. Integration test: manually run the decompose workflow end-to-end with a sample block to verify the command prompt and scripts work together

## Implementation Notes (Post-Build)

### Deviations from Plan

1. **conftest.py not modified** - Fixtures are inlined in `test_decomposition.py`. The `decomposition_workspace` fixture is specific to decomposition tests.

2. **decomposition-guide.md not modified** - Already has comprehensive content from section-01 scaffolding covering when to decompose, sub-function identification, allocation rationale templates, stopping conditions, and max level rationale.

3. **parent_of links not created during allocation** - Per plan line 240: "Created later when sub-block requirements are written, linking parent requirements to their child derivations." Only `allocated_to` links are created during the allocation step.

4. **9 tests instead of 8** - Added an extra `test_within_max_level_allowed` test for completeness.

### Code Review Fixes

1. **Added requirement validation** - `allocate_requirement()` now validates that the requirement exists and is baselined before creating allocation links.

### Actual Files Created

| File | Action | Notes |
|------|--------|-------|
| `skills/requirements-dev/scripts/decompose.py` | Created | 6 functions + CLI with 5 subcommands |
| `skills/requirements-dev/tests/test_decomposition.py` | Created | 9 tests covering all decomposition functions |
| `skills/requirements-dev/commands/reqdev.decompose.md` | Created | 8-step decomposition workflow |

### Test Results

- 172 total tests passing (up from 163)
- 9 new decomposition tests