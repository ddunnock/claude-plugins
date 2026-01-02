---
description: [TODO: Clear description of what this command does - used for discovery]
handoffs:
  - label: Next Step
    agent: [target-command-name]
    prompt: [Context to pass to target command]
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user input may specify:
- [List expected argument types]
- [Document special flags or modes]

## Purpose

[1-2 paragraphs explaining]:
- What problem this command solves
- When to use it vs alternatives
- Key concepts or terminology

## Workflow

1. **[Step Name]**: [Description]
   - [Sub-step details]
   - **If [condition]**: [action]
   - **Else**: [alternative action]

2. **[Next Step]**: [Description]
   - Run `.claude/scripts/bash/[script].sh --json`
   - Parse response and [action]

3. **[Final Step]**: [Description]
   - Use template `.claude/templates/[template].md`
   - [Generate output]

## Scripts Reference

| Script | Purpose | When Used |
|--------|---------|-----------|
| `[script].sh` | [Purpose] | [When] |

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| "[Error message]" | [Cause] | [Resolution] |

## Completion Criteria

- [ ] [Checkable success condition]
- [ ] [Another success condition]
- [ ] [Final validation passed]
