---
name: reqdev:decompose
description: Decompose baselined blocks into sub-blocks with requirement allocation
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/references/type-guide.md</read>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/references/decomposition-guide.md</read>
</context>

# /reqdev:decompose - Subsystem Decomposition

Decomposes a baselined system-level block into sub-blocks, allocates parent requirements to sub-blocks, and validates allocation coverage. Sub-blocks then become available for requirements development via `/reqdev:requirements`.

<prerequisite>
    <condition>Block requirements must be baselined (run /reqdev:deliver first).</condition>
    <reference>${CLAUDE_PLUGIN_ROOT}/references/decomposition-guide.md</reference>
</prerequisite>

<step sequence="1" name="select-block">
    <objective>Ask the user which block to decompose and validate it is baselined.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-baseline --block BLOCK_NAME</script>
    <branch condition="block NOT fully baselined">
        <presentation>Block "{block-name}" has requirements that are not baselined. Run /reqdev:deliver to baseline all requirements before decomposing.</presentation>
    </branch>
</step>

<step sequence="2" name="check-decomposition-level">
    <objective>Verify further decomposition is allowed (max 3 levels).</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev check-level --level CURRENT_LEVEL</script>
    <branch condition="would exceed max_level=3">
        <presentation>Block "{block-name}" is at level {current-level}. Further decomposition would exceed the maximum depth of 3 levels. You can override this limit in state.json if needed.</presentation>
        <then>Stop.</then>
    </branch>
    <branch condition="at max_level - 1">
        <presentation>Note: This will create level {current-level + 1} sub-blocks. One more level of decomposition remains after this.</presentation>
    </branch>
</step>

<step sequence="3" name="identify-sub-blocks">
    <objective>Guide the user through identifying sub-functions within the block.</objective>
    <presentation>
Looking at the requirements for "{block-name}", let's identify distinct sub-functions.
Consider: processing stages, data domains, independent failure modes, or API boundaries.
    </presentation>
    <collect>
        <per-sub-block>
            - Name: short identifier (e.g., "graph-engine")
            - Description: what this sub-block is responsible for
        </per-sub-block>
    </collect>
    <presentation>
Proposed Sub-Blocks for "{block-name}":
| # | Name | Description |
|---|------|-------------|
| 1 | graph-engine | Graph data structure and traversal |
| 2 | cycle-detector | Circular dependency detection |
| 3 | critical-path-calc | Critical path computation |

Approve? (yes/edit/add more)
    </presentation>
    <gate type="user-confirm">User approves sub-block definitions.</gate>
</step>

<step sequence="4" name="register-sub-blocks">
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev register-sub-blocks --parent BLOCK_NAME --sub-blocks '[SUB_BLOCKS_JSON]' --level NEXT_LEVEL</script>
</step>

<step sequence="5" name="allocate-requirements">
    <objective>For each parent requirement, ask which sub-block(s) it allocates to.</objective>
    <loop over="each parent requirement in the block">
        <presentation>
**REQ-xxx:** "The system shall track dependency graphs"
Allocate to which sub-block(s)? [graph-engine / cycle-detector / critical-path-calc / multiple]
        </presentation>
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev allocate --requirement REQ-xxx --sub-block SUB_BLOCK --rationale "RATIONALE"</script>
        <note>A requirement can be allocated to multiple sub-blocks if it spans concerns.</note>
    </loop>
</step>

<step sequence="6" name="validate-allocation-coverage">
    <objective>Ensure 100% of parent requirements are allocated.</objective>
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/decompose.py --workspace .requirements-dev validate-coverage --block BLOCK_NAME</script>
    <loop until="coverage = 100%">
        <branch condition="coverage less than 100%">
            <presentation>
The following requirements are not allocated to any sub-block:
  - REQ-xxx: "statement"
  - REQ-yyy: "statement"
Please allocate these requirements before proceeding.
            </presentation>
            <then>Return to step 5 for unallocated requirements.</then>
        </branch>
    </loop>
</step>

<step sequence="7" name="summary">
    <presentation>
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
    </presentation>
    <collect>
        <question>Would you like to start developing requirements for one of the sub-blocks now?</question>
    </collect>
</step>
