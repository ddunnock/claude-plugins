---
name: st:init
description: Initialize a skill-tester session — collect target skill, mode, sensitivity, test prompts, and report location
---

<context>
    <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>
</context>

# /st:init -- Initialize Skill Testing Session

This command collects all inputs and creates the session directory (Phase 1).

<step sequence="1.1" name="collect-skill-path">
    <objective>Identify the skill to analyze.</objective>
    <interaction tool="AskUserQuestion">
        <question>What skill would you like to analyze?</question>
        <header>Skill Path or Content</header>
        <options>["I'll paste the SKILL.md", "Provide a directory path", "Use a skill I have open"]</options>
        <multiSelect>false</multiSelect>
    </interaction>
    <branch condition="directory path provided">
        Validate it (no ".." segments, must exist).
        <gate>If path is invalid or not found, report the error and stop.</gate>
    </branch>
</step>

<step sequence="1.2" name="collect-mode">
    <objective>Select analysis mode.</objective>
    <interaction tool="AskUserQuestion">
        <question>Which analysis mode?</question>
        <header>Analysis Mode</header>
        <options>["Full (default)", "Audit only (no test execution)", "Trace only (runtime capture)", "Report only (re-generate from session)"]</options>
        <multiSelect>false</multiSelect>
    </interaction>
</step>

<step sequence="1.3" name="collect-sensitivity">
    <objective>Set security review sensitivity.</objective>
    <interaction tool="AskUserQuestion">
        <question>Security review sensitivity?</question>
        <header>Sensitivity Level</header>
        <options>["Standard (default)", "Strict (flag more)", "Lenient (critical only)"]</options>
        <multiSelect>false</multiSelect>
    </interaction>
</step>

<step sequence="1.4" name="collect-prompts">
    <objective>Collect 1-3 test prompts (required for Full and Trace modes).</objective>
    If the user doesn't provide them, auto-generate 3 reasonable prompts from the skill's
    description and present them for approval before proceeding.
    <gate>Full and Trace modes require at least one test prompt. Stop if none provided or approved.</gate>
</step>

<step sequence="1.5" name="collect-report-location">
    <objective>Choose where session reports are stored.</objective>
    <interaction tool="AskUserQuestion">
        <question>Where should session reports be stored?</question>
        <header>Report Location</header>
        <options>["sessions/ (project-local, default)", "~/.claude/tests/ (global)", ".claude/tests/ (project .claude dir)"]</options>
        <multiSelect>false</multiSelect>
    </interaction>
    Map user selection to report-root value:
    - "sessions/" -> sessions/
    - "~/.claude/tests/" -> ~/.claude/tests/
    - ".claude/tests/" -> .claude/tests/
</step>

<step sequence="1.6" name="create-session">
    <objective>Create namespaced session directory with validation.</objective>
    Determine session directory name: <report_root>/<skill_name>_<YYYYMMDD_HHMMSS>/
    Confirm session path to user before proceeding.

    Run comprehensive validation and sandbox setup:
    <script>python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup_test_env.py --skill-path <skill_path> --session-dir <session_dir> --mode <mode> --report-root <report_root></script>

    This validates the skill path, checks for required files (SKILL.md, plugin.json, SECURITY.md),
    creates the full session directory structure with placeholders, and initializes the sandbox
    environment for isolated script execution. Writes manifest.json to the session directory.
    <gate>setup_test_env.py must succeed before proceeding. If validation fails with
    errors, report them to the user and stop. Warnings are acceptable and should be noted.</gate>
</step>

<step sequence="1.7" name="suggest-next">
    <objective>Guide the user to the next command based on selected mode.</objective>
    | Mode | Next Command |
    |------|-------------|
    | Full | `/st:run` |
    | Audit | `/st:audit` |
    | Trace | `/st:trace` |
    | Report | `/st:report` |
</step>
