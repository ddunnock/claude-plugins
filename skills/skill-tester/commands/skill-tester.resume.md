---
name: skill-tester:resume
description: Resume an interrupted skill-tester session from the last completed phase
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /skill-tester:resume -- Resume Interrupted Session

Resume a skill-tester session from the last completed phase.

## Procedure

### Step 1: Locate Session

If `$ARGUMENTS` provides a session directory path, use it.
Otherwise, find the most recent session directory by scanning for manifest.json files
under the report roots (sessions/, ~/.claude/tests/, .claude/tests/).

If no session found: "No active session. Run `/skill-tester:init` to start."

### Step 2: Load Manifest and Detect Mode

Read manifest.json. Determine the analysis mode from either:
- Explicit `report_root` or mode field in manifest
- Infer from which files exist (e.g., if security_report.json exists but script_runs.jsonl is empty, likely Audit mode)

### Step 3: Detect Completed Phases

Check each phase's output file for existence and non-empty content (same checks as `/skill-tester:status` Step 3).

### Step 4: Present Resume Point

```
===================================================================
RESUMING SESSION
===================================================================

Skill:       <skill_path>
Session:     <session_dir>
Mode:        <detected_mode>

Completed:   <list of completed phases>
Next Phase:  <next incomplete phase>

===================================================================
```

Ask the user:
- [A] Continue from the next incomplete phase
- [B] Re-run from a specific phase
- [C] Show full status (`/skill-tester:status`)

### Step 5: Resume Execution

Based on the detected mode and next incomplete phase, execute the remaining phases
using the logic from the appropriate mode command:

| Mode | Command Logic |
|------|--------------|
| Full | Follow `/skill-tester:run` phases from resume point |
| Audit | Follow `/skill-tester:audit` phases from resume point |
| Trace | Follow `/skill-tester:trace` phases from resume point |

Skip any phases that have already completed (files exist with valid content).
Resume from the first incomplete phase.
