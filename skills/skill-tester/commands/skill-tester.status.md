---
name: skill-tester:status
description: Display session state — skill path, mode, session dir, phase completion, and next action
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /skill-tester:status -- Session Status

Display the current state of a skill-tester session.

## Procedure

### Step 1: Locate Session

If `$ARGUMENTS` provides a session directory path, use it.
Otherwise, find the most recent session directory by scanning for manifest.json files
under the report roots (sessions/, ~/.claude/tests/, .claude/tests/).

If no session found: "No active session. Run `/skill-tester:init` to start."

### Step 2: Read Manifest

Read manifest.json from the session directory. Extract:
- skill_path
- session_dir
- mode (from manifest or infer from which files exist)
- report_root (if present)
- validation results

### Step 3: Check Phase Completion

Determine which phases have completed by checking file existence and non-empty content:

| Phase | File | Check |
|-------|------|-------|
| 1. Init | manifest.json | exists and valid |
| 2. Inventory | inventory.json | exists and not "{}" |
| 3. Scan | scan_results.json | exists and not "{}" |
| 4. Prompt Lint | prompt_lint.json | exists and not "{}" |
| 4. Prompt Review | prompt_review.json | exists and not "{}" |
| 5. Test Execution | script_runs.jsonl | exists and not empty |
| 6. Security Audit | security_report.json | exists and not "{}" |
| 7. Code Review | code_review.json | exists and not "{}" |
| 8. Session Trace | session_report.html | exists |
| 9. Report | report.html | exists and not placeholder |

### Step 4: Display Dashboard

```
===================================================================
SKILL TESTER STATUS
===================================================================

Skill:       <skill_path>
Session:     <session_dir>
Report Root: <report_root or "sessions/ (default)">

-------------------------------------------------------------------
PHASE COMPLETION
-------------------------------------------------------------------

  [X/  ] 1. Init             manifest.json
  [X/  ] 2. Inventory        inventory.json
  [X/  ] 3. Scan             scan_results.json
  [X/  ] 4. Prompt Lint      prompt_lint.json + prompt_review.json
  [X/  ] 5. Test Execution   script_runs.jsonl
  [X/  ] 6. Security Audit   security_report.json
  [X/  ] 7. Code Review      code_review.json
  [X/  ] 8. Session Trace    session_report.html
  [X/  ] 9. Report           report.html

===================================================================
```

### Step 5: Suggest Next Action

Based on completion state:

| State | Suggestion |
|-------|-----------|
| No phases complete after init | Run the appropriate mode command |
| Some phases complete | `/skill-tester:resume` to continue |
| All phases complete | "Analysis complete. View report.html" |
| Report missing but data exists | `/skill-tester:report` to regenerate |
