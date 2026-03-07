---
name: st:run
description: Execute full analysis — all phases (2-9) including inventory, scan, prompt lint, test execution, security audit, code review, session trace, and report
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /st:run -- Full Analysis (Phases 2-9)

Prerequisite: manifest.json must exist from `/st:init`.

<gate>Read manifest.json from the session directory. If it does not exist or is invalid, stop and instruct the user to run `/st:init` first.</gate>

<phase name="inventory" sequence="2">
    <objective>Scan the skill directory and produce structured inventory.json.</objective>
    <step sequence="2.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/api_logger.py inventory <skill_path> --output <session_dir>/inventory.json</script>
    </step>
    <step sequence="2.2">
        Report inventory summary to user: script count, reference count, any hardcoded URLs
        or potential secrets flagged by the scanner.
    </step>
    <step sequence="2.3">
        <branch condition="skill has no scripts">
            Note "No scripts -- SKILL.md-only skill" in session. Skip phase 5 (test execution).
        </branch>
    </step>
    <gate>inventory.json must be written before proceeding.</gate>
</phase>

<phase name="deterministic-scan" sequence="3" depends-on="inventory">
    <objective>Run deterministic tools against skill scripts BEFORE any AI analysis (Rule B9).</objective>
    <step sequence="3.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_skill.py --skill-path <skill_path> --session-dir <session_dir> --sensitivity <sensitivity></script>
    </step>
    <step sequence="3.2">
        Report scan summary to user: total findings by severity.
        <branch condition="CRITICAL findings found">
            Display CRITICAL findings immediately.
            <interaction tool="AskUserQuestion">
                <question>CRITICAL security findings detected. Continue analysis?</question>
                <header>Critical Findings Gate</header>
                <options>["Yes, continue", "No, stop here"]</options>
                <multiSelect>false</multiSelect>
            </interaction>
        </branch>
    </step>
    <gate>scan_results.json must be written before proceeding.</gate>
</phase>

<phase name="prompt-lint" sequence="4" depends-on="inventory">
    <objective>Run deterministic prompt quality checks, then AI deep review.</objective>
    <step sequence="4.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/prompt_linter.py --skill-path <skill_path> --session-dir <session_dir></script>
    </step>
    <step sequence="4.2">
        Report lint summary: ERROR and WARN counts by category.
        <branch condition="ERROR findings found">
            Display all ERROR findings with recommendations.
            <interaction tool="AskUserQuestion">
                <question>Prompt lint found ERROR-level issues. Continue to AI prompt review?</question>
                <header>Prompt Lint Gate</header>
                <options>["Yes, continue", "No, stop here"]</options>
                <multiSelect>false</multiSelect>
            </interaction>
        </branch>
    </step>
    <step sequence="4.3">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/prompt_reviewer.md</read>
        </context>
        Invoke the prompt-reviewer agent, providing in the prompt:
        - --output-path: the absolute path to <session_dir>/prompt_review.json
        - prompt_lint.json (deterministic findings -- primary grounding)
        - Full SKILL.md content
        - Content of all agent .md files found in agents/
        - Content of all command .md files found in commands/ (if present)
        The agent will attempt to Write the file directly. If the agent's response
        contains a ```json block instead (Write was denied), extract the JSON and
        write it to <session_dir>/prompt_review.json from the orchestrator.
    </step>
    <gate>prompt_lint.json must be written before invoking the prompt-reviewer agent.</gate>
</phase>

<phase name="test-execution" sequence="5" depends-on="deterministic-scan">
    <objective>Execute skill scripts with full I/O capture.</objective>
    <gate>If inventory noted "no scripts", skip this phase entirely.</gate>
    <step sequence="5.1">
        For each test prompt, execute the skill and capture all observable behavior:
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/script_runner.py skill <skill_path> --prompt "<test_prompt>" --session-dir <session_dir> --capture-api</script>
    </step>
    <step sequence="5.2">
        If the skill's scripts make no direct anthropic API calls, note "API trace: N/A --
        skill uses native Claude tool use" in the report.
    </step>
</phase>

<phase name="security-audit" sequence="6" depends-on="deterministic-scan">
    <objective>AI security analysis with scan_results.json as grounding input.</objective>
    <step sequence="6.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/security_review.md</read>
        </context>
        Invoke the security-review agent, providing in the prompt:
        - --output-path: the absolute path to <session_dir>/security_report.json
        - scan_results.json (deterministic findings -- primary grounding)
        - inventory.json (script paths and flags)
        - Raw script content for each script flagged in scan_results
        - Sensitivity level from intake
        The agent will attempt to Write the file directly. If the agent's response
        contains a ```json block instead (Write was denied), extract the JSON and
        write it to <session_dir>/security_report.json from the orchestrator.
    </step>
</phase>

<phase name="code-review" sequence="7" depends-on="deterministic-scan">
    <objective>AI code quality review.</objective>
    <step sequence="7.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/code_review.md</read>
        </context>
        Invoke the code-review agent, providing in the prompt:
        - --output-path: the absolute path to <session_dir>/code_review.json
        - inventory.json
        - SKILL.md content
        - Raw script content for all discovered scripts
        - anti_patterns.md reference
        The agent will attempt to Write the file directly. If the agent's response
        contains a ```json block instead (Write was denied), extract the JSON and
        write it to <session_dir>/code_review.json from the orchestrator.
    </step>
</phase>

<phase name="session-trace" sequence="8" depends-on="test-execution">
    <objective>Capture Claude Code session trace from JSONL logs.</objective>
    <step sequence="8.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/session_analyzer.py --output <session_dir>/session_report.html --format both</script>
        The script auto-detects the project directory and latest session from ~/.claude/projects/.
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
        Present report.html to the user. If session_report.html was also generated (phase 8),
        mention it as a companion report.
        Provide a plain-language summary covering:
        - Mode run and skill name
        - Script count and API-calling scripts
        - Deterministic scan findings (CRITICAL/HIGH counts)
        - Prompt lint result (PASS/WARN/FAIL + top ERRORs)
        - Prompt quality score
        - Security risk rating
        - Code quality score
        - Session trace summary (if available)
        - Top 3 recommendations across all analysis layers
    </step>
</phase>
