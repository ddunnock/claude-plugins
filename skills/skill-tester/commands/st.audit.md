---
name: st:audit
description: Static analysis only — run inventory, deterministic scan, prompt lint, security audit, code review, and report (no test execution)
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /st:audit -- Audit Mode (Phases 2-4, 6-7, 9)

Static analysis only. Skips test execution (phase 5) and session trace (phase 8).

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
            Note "No scripts -- SKILL.md-only skill" in session. Security and code review
            will analyze SKILL.md structure only.
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
    <objective>Deterministic prompt quality checks + AI deep review.</objective>
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
        - prompt_lint.json (deterministic findings -- primary grounding)
        - Full SKILL.md content
        - Content of all agent .md files found in agents/
        - Content of all command .md files found in commands/ (if present)
        Extract the ```json block from the agent response and write it to
        <session_dir>/prompt_review.json.
    </step>
    <gate>prompt_lint.json must be written before invoking the prompt-reviewer agent.</gate>
</phase>

<phase name="security-audit" sequence="6" depends-on="deterministic-scan">
    <objective>AI security analysis with scan_results.json as grounding input.</objective>
    <step sequence="6.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/security_review.md</read>
        </context>
        Invoke the security-review agent, providing in the prompt:
        - scan_results.json (deterministic findings -- primary grounding)
        - inventory.json (script paths and flags)
        - Raw script content for each script flagged in scan_results
        - Sensitivity level from intake
        Extract the ```json block from the agent response and write it to
        <session_dir>/security_report.json.
    </step>
</phase>

<phase name="code-review" sequence="7" depends-on="deterministic-scan">
    <objective>AI code quality review.</objective>
    <step sequence="7.1">
        <context>
            <read required="true">${CLAUDE_PLUGIN_ROOT}/agents/code_review.md</read>
        </context>
        Invoke the code-review agent, providing in the prompt:
        - inventory.json
        - SKILL.md content
        - Raw script content for all discovered scripts
        - anti_patterns.md reference
        Extract the ```json block from the agent response and write it to
        <session_dir>/code_review.json.
    </step>
</phase>

<phase name="report" sequence="9">
    <objective>Generate unified interactive HTML report.</objective>
    <step sequence="9.1">
        <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/report_gen.py --session-dir <session_dir> --output <session_dir>/report.html</script>
    </step>
    <step sequence="9.2">
        Present report.html to the user. Provide a plain-language summary covering:
        - Mode run and skill name
        - Script count and API-calling scripts
        - Deterministic scan findings (CRITICAL/HIGH counts)
        - Prompt lint result (PASS/WARN/FAIL + top ERRORs)
        - Prompt quality score
        - Security risk rating
        - Code quality score
        - Top 3 recommendations across all analysis layers
    </step>
</phase>
