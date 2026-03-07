---
name: skill-tester:audit
description: Static analysis only — run inventory, deterministic scan, prompt lint, security audit, code review, and report (no test execution)
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /skill-tester:audit -- Audit Mode (Phases 2-4, 6-7, 9)

Static analysis only. Skips test execution (phase 5) and session trace (phase 8).

<gate>Read manifest.json from the session directory. If it does not exist or is invalid, stop and instruct the user to run `/skill-tester:init` first.</gate>

<phase name="inventory" sequence="2">
    <objective>Scan the skill directory and produce structured inventory.json.</objective>
    <step sequence="2.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/api_logger.py inventory <skill_path> --output <session_dir>/inventory.json</script>
    </step>
    <step sequence="2.2">
        Report inventory summary to user.
    </step>
    <gate>inventory.json must be written before proceeding.</gate>
</phase>

<phase name="deterministic-scan" sequence="3" depends-on="inventory">
    <objective>Run deterministic tools against skill scripts BEFORE any AI analysis (Rule B9).</objective>
    <step sequence="3.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_skill.py --skill-path <skill_path> --session-dir <session_dir> --sensitivity <sensitivity></script>
    </step>
    <step sequence="3.2">
        Report scan summary. Handle CRITICAL findings gate (same as /skill-tester:run phase 3).
    </step>
    <gate>scan_results.json must be written before proceeding.</gate>
</phase>

<phase name="prompt-lint" sequence="4" depends-on="inventory">
    <objective>Deterministic prompt quality checks + AI deep review.</objective>
    <step sequence="4.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prompt_linter.py --skill-path <skill_path> --session-dir <session_dir></script>
    </step>
    <step sequence="4.2">
        Report lint summary. Handle ERROR findings gate (same as /skill-tester:run phase 4).
    </step>
    <step sequence="4.3">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/prompt_reviewer.md</read>
        </context>
        Invoke the prompt-reviewer agent (same as /skill-tester:run step 4.3).
    </step>
    <gate>prompt_lint.json must be written before invoking the prompt-reviewer agent.</gate>
</phase>

<phase name="security-audit" sequence="6" depends-on="deterministic-scan">
    <objective>AI security analysis with scan_results.json as grounding.</objective>
    <step sequence="6.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/security_review.md</read>
        </context>
        Invoke the security-review agent (same as /skill-tester:run step 6.1).
    </step>
</phase>

<phase name="code-review" sequence="7" depends-on="deterministic-scan">
    <objective>AI code quality review.</objective>
    <step sequence="7.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/code_review.md</read>
        </context>
        Invoke the code-review agent (same as /skill-tester:run step 7.1).
    </step>
</phase>

<phase name="report" sequence="9">
    <objective>Generate unified interactive HTML report.</objective>
    <step sequence="9.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report_gen.py --session-dir <session_dir> --output <session_dir>/report.html</script>
    </step>
    <step sequence="9.2">
        Present report.html and plain-language summary (same as /skill-tester:run step 9.2).
    </step>
</phase>
