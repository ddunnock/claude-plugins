---
description: "[One-line description of what this command produces]"
agent:
  model: sonnet
---

# [Command Name]

## Purpose

[Clear statement of the deliverable this command produces]

**Deliverable Type**: [Generator | Analyzer | Orchestrator | Decision]

## Prerequisites

- [ ] [Required input 1] - Available at: [location/source]
- [ ] [Required input 2] - Available at: [location/source]
- [ ] [Prior command] completed (if dependent)

## Workflow

### Phase 1: Preparation

1. Verify all prerequisites are met
2. Load required resources:
   - Template: `.claude/templates/[template-name].md`
   - State: `.claude/memory/[state-file].md`
3. Initialize output structure

### Phase 2: [Primary Action Name]

1. [Action step 1]
   - [Sub-step if needed]
   - [Sub-step if needed]

2. [Action step 2]

3. [Action step 3]

**Script Support** (if applicable):
```bash
python scripts/python/[script-name].py <input> --json
```

**Decision Point** (if applicable):
- If [condition]: [action]
- If [condition]: [action]

### Phase 3: Quality Validation

1. Run validation checks:

```bash
python scripts/python/validate-output.py <output-path> --json
```

2. Verify against completion criteria (below)

3. Document any issues or TBDs:
   - Update `.claude/memory/[relevant-status].md`
   - Log assumptions to `.claude/memory/assumptions-log.md`

### Phase 4: Output Finalization

1. Save output to designated location
2. Update status in `.claude/memory/[status-file].md`
3. Prepare handoff context for next command

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Primary Deliverable | `[PATH]` | [FORMAT] |
| Status Update | `.claude/memory/[file].md` | Markdown |
| [Other Output] | `[PATH]` | [FORMAT] |

## Completion Criteria

- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]
- [ ] Validation script passes without errors
- [ ] All TBD items documented
- [ ] Assumptions logged

## Error Handling

| Error Condition | Resolution |
|-----------------|------------|
| [Error 1] | [How to resolve] |
| [Error 2] | [How to resolve] |

## Handoffs

### Proceed to [Next Command Name]

**Context**: 
[Summary of what was accomplished in this command]

**Inputs Ready**:
- [Input 1]: `[location]`
- [Input 2]: `[location]`

**Objective**:
[What the next command should accomplish]

**Constraints**:
- [Any constraints to carry forward]

Use: `/[next-command]`

---

### Alternative Handoff: [Alternative Path]

**Context**:
[When to use this alternative path]

Use: `/[alternative-command]`

---

## Notes

<!-- 
GROUNDING: Document evidence sources and assumptions

[VERIFIED: source-url] - Any verified facts used
[ASSUMPTION: rationale] - Any assumptions made

Update assumptions-log.md with any new assumptions.
-->
