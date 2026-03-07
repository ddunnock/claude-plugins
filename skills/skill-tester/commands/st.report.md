---
name: st:report
description: Regenerate HTML report from existing session data
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /st:report -- Regenerate Report (Phase 9)

Regenerates report.html from existing session data without re-running analysis.

## Procedure

### Step 1: Locate Session

If `$ARGUMENTS` provides a session directory path, use it.
Otherwise, find the most recent session directory by scanning for manifest.json files
under the report roots (sessions/, ~/.claude/tests/, .claude/tests/).

<gate>A valid session directory with manifest.json must exist. If not found, instruct the user to run `/st:init` first.</gate>

### Step 2: Generate Report

<script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report_gen.py --session-dir <session_dir> --output <session_dir>/report.html</script>

### Step 3: Present Report

Present report.html to the user with a plain-language summary of findings.
If session_report.html exists, mention it as a companion report.
