---
name: skill-tester:trace
description: Runtime capture only — run inventory, test execution, session trace, and report (no security/code/prompt review)
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /skill-tester:trace -- Trace Mode (Phases 2, 5, 8, 9)

Runtime capture only. Skips deterministic scan (phase 3), prompt lint (phase 4),
security audit (phase 6), and code review (phase 7).

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

<phase name="test-execution" sequence="5" depends-on="inventory">
    <objective>Execute skill scripts with full I/O capture.</objective>
    <step sequence="5.1">
        For each test prompt, execute the skill and capture all observable behavior:
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/script_runner.py skill <skill_path> --prompt "<test_prompt>" --session-dir <session_dir> --capture-api</script>
    </step>
    <step sequence="5.2">
        If the skill's scripts make no direct anthropic API calls, note "API trace: N/A --
        skill uses native Claude tool use" in the report.
    </step>
</phase>

<phase name="session-trace" sequence="8" depends-on="test-execution">
    <objective>Capture Claude Code session trace from JSONL logs.</objective>
    <step sequence="8.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_analyzer.py --output <session_dir>/session_report.html --format both</script>
    </step>
    <step sequence="8.2">
        If session_analyzer.py fails, note "Session trace: unavailable" in the report.
        This is non-blocking.
    </step>
</phase>

<phase name="report" sequence="9" depends-on="session-trace">
    <objective>Generate unified interactive HTML report.</objective>
    <step sequence="9.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report_gen.py --session-dir <session_dir> --output <session_dir>/report.html</script>
    </step>
    <step sequence="9.2">
        Present report.html and plain-language summary focusing on runtime data:
        - Script execution results
        - API call trace (SDK or session trace)
        - Session trace summary (if available)
    </step>
</phase>
