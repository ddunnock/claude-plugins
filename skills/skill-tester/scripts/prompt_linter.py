#!/usr/bin/env python3
"""prompt_linter.py — Deterministic prompt and instruction quality linter for Claude skills.

Analyzes SKILL.md and all agent/command .md files for structural and behavioral
anti-patterns in the prompt instructions themselves — independent of the Python scripts.

Check categories (run in order):
  1. INTERACTION  — AskUserQuestion usage and field completeness
  2. DEAD_COLLECT — inputs collected but never used downstream
  3. AGENT_USAGE  — agent definition / invocation consistency
  4. WORKFLOW     — phase sequencing, gates, branches, depends-on integrity
  5. REFERENCE    — file paths referenced in prompts that don't exist on disk
  6. CONTEXT_READ — agent files missing mandatory <context><read> blocks

Writes findings to <session_dir>/prompt_lint.json.

Usage:
  python3 scripts/prompt_linter.py \\
    --skill-path /path/to/skill \\
    --session-dir sessions/my-skill_20260101_120000
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from schemas import PROMPT_LINT_SCHEMA
from shared_io import _save_json

# ---------------------------------------------------------------------------
# Finding builder
# ---------------------------------------------------------------------------

_counter = 0


def _finding(
    check_id: str,
    severity: str,
    category: str,
    file: str,
    message: str,
    line: Optional[int] = None,
    snippet: Optional[str] = None,
    recommendation: Optional[str] = None,
) -> dict:
    """Build a standardized prompt-lint finding dict.

    Args:
        check_id: Short identifier like PL-001.
        severity: ERROR, WARN, or INFO.
        category: One of INTERACTION, DEAD_COLLECT, AGENT_USAGE,
            WORKFLOW, REFERENCE, CONTEXT_READ.
        file: Relative path to the file containing the issue.
        message: Human-readable description of the problem.
        line: Approximate line number in the file, or None.
        snippet: Relevant text excerpt, or None.
        recommendation: Specific fix guidance, or None.

    Returns:
        Finding dict matching the prompt_lint.json schema.
    """
    global _counter
    _counter += 1
    return {
        "finding_id": f"PL-{_counter:03d}",
        "check_id": check_id,
        "severity": severity,
        "category": category,
        "file": file,
        "line": line,
        "snippet": snippet[:120] if snippet else None,
        "message": message,
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    """Read a file to string, returning empty string on failure.

    Args:
        path: File to read.

    Returns:
        File content as string, or empty string if unreadable.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _line_of(text: str, char_offset: int) -> int:
    """Return 1-based line number for a character offset in text.

    Args:
        text: Full file content.
        char_offset: Character offset within text.

    Returns:
        1-based line number.
    """
    return text[:char_offset].count("\n") + 1


def _find_md_files(skill_root: Path) -> list[Path]:
    """Collect all .md files in agents/ and commands/ subdirectories.

    Args:
        skill_root: Root of the skill directory.

    Returns:
        Sorted list of Path objects for agent/command .md files.
    """
    result = []
    for sub in ("agents", "commands"):
        subdir = skill_root / sub
        if subdir.is_dir():
            result.extend(sorted(subdir.glob("*.md")))
    return result


# ---------------------------------------------------------------------------
# Check 1: INTERACTION — AskUserQuestion usage
# ---------------------------------------------------------------------------

# Phrases that strongly indicate user input collection without a tool block
_ASK_PROSE_PATTERN = re.compile(
    r"(?i)\b(ask\s+the\s+user|collect\s+(from\s+the\s+user|user\s+input)|"
    r"prompt\s+the\s+user|request\s+(from|the)\s+user|get\s+(from|the)\s+user|"
    r"wait\s+for\s+(the\s+)?user|have\s+the\s+user\s+(choose|select|provide|enter|input))"
)

_INTERACTION_TAG = re.compile(r"<interaction\b([^>]*)>", re.DOTALL)
_AUQ_FIELD = re.compile(
    r"<(?P<tag>question|header|options|multiSelect)\s*>(?P<content>[^<]*)</(?P=tag)>",
    re.DOTALL,
)
_OPTIONS_LIST = re.compile(r"\[([^\]]*)\]")

REQUIRED_AUQ_FIELDS = {"question", "header", "options", "multiSelect"}


def check_interaction(skill_root: Path, skill_md_content: str) -> list:
    """Check AskUserQuestion usage in SKILL.md for completeness and correctness.

    Args:
        skill_root: Root of the skill directory.
        skill_md_content: Full text of SKILL.md.

    Returns:
        List of finding dicts.
    """
    findings = []
    rel = "SKILL.md"
    text = skill_md_content

    # PL-ask-prose: prose that collects input without <interaction> block
    # Find all <step> blocks and check each one
    step_blocks = list(re.finditer(r"<step\b[^>]*>(.*?)</step>", text, re.DOTALL))
    for step_match in step_blocks:
        step_text = step_match.group(1)
        line_num = _line_of(text, step_match.start())
        has_interaction = "<interaction" in step_text
        prose_ask = _ASK_PROSE_PATTERN.search(step_text)
        if prose_ask and not has_interaction:
            findings.append(
                _finding(
                    check_id="PL-ask-no-tool",
                    severity="ERROR",
                    category="INTERACTION",
                    file=rel,
                    line=line_num,
                    snippet=step_text.strip()[:120],
                    message=(
                        f"Step at line {line_num} collects user input using prose "
                        f'("{prose_ask.group(0).strip()}") but has no '
                        '<interaction tool="AskUserQuestion"> block. This will cause '
                        "Claude to hang waiting for user input with no structured widget."
                    ),
                    recommendation=(
                        "Replace the prose instruction with an explicit "
                        '<interaction tool="AskUserQuestion"> block containing '
                        "<question>, <header>, <options>, and <multiSelect> fields."
                    ),
                )
            )

    # PL-auq-missing-tool: <interaction> tag without tool="AskUserQuestion"
    for m in _INTERACTION_TAG.finditer(text):
        attrs = m.group(1)
        line_num = _line_of(text, m.start())
        if (
            'tool="AskUserQuestion"' not in attrs
            and "tool='AskUserQuestion'" not in attrs
        ):
            findings.append(
                _finding(
                    check_id="PL-interaction-no-tool",
                    severity="ERROR",
                    category="INTERACTION",
                    file=rel,
                    line=line_num,
                    snippet=m.group(0)[:80],
                    message=(
                        f"<interaction> tag at line {line_num} is missing "
                        'tool="AskUserQuestion" attribute. Claude won\'t know which '
                        "widget to render."
                    ),
                    recommendation='Add tool="AskUserQuestion" to the <interaction> tag.',
                )
            )

    # PL-auq-missing-field: AskUserQuestion block missing required fields
    auq_blocks = list(
        re.finditer(
            r'<interaction[^>]*tool=["\']AskUserQuestion["\'][^>]*>(.*?)</interaction>',
            text,
            re.DOTALL,
        )
    )
    for m in auq_blocks:
        block_text = m.group(1)
        line_num = _line_of(text, m.start())
        found_fields = {fm.group("tag") for fm in _AUQ_FIELD.finditer(block_text)}
        missing = REQUIRED_AUQ_FIELDS - found_fields
        if missing:
            findings.append(
                _finding(
                    check_id="PL-auq-missing-field",
                    severity="ERROR",
                    category="INTERACTION",
                    file=rel,
                    line=line_num,
                    snippet=block_text.strip()[:120],
                    message=(
                        f"AskUserQuestion block at line {line_num} is missing required "
                        f"field(s): {', '.join(sorted(missing))}. Incomplete blocks "
                        "produce broken or unusable question widgets."
                    ),
                    recommendation=(
                        f"Add the missing field(s): "
                        + ", ".join(f"<{f}></{f}>" for f in sorted(missing))
                    ),
                )
            )

    # PL-auq-too-few-options: options list with fewer than 2 items
    for m in auq_blocks:
        block_text = m.group(1)
        line_num = _line_of(text, m.start())
        options_match = re.search(
            r"<options\s*>\s*(\[.*?\])\s*</options>", block_text, re.DOTALL
        )
        if options_match:
            raw_list = options_match.group(1)
            # Count non-empty quoted items
            items = re.findall(r'"[^"]+"|\'[^\']+\'', raw_list)
            if len(items) < 2:
                findings.append(
                    _finding(
                        check_id="PL-auq-few-options",
                        severity="WARN",
                        category="INTERACTION",
                        file=rel,
                        line=line_num,
                        snippet=raw_list[:80],
                        message=(
                            f"AskUserQuestion at line {line_num} has fewer than 2 options "
                            f"({len(items)} found). A single option gives the user no real choice."
                        ),
                        recommendation="Provide at least 2 meaningful option strings.",
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Check 2: DEAD_COLLECT — inputs collected but never used
# ---------------------------------------------------------------------------


def _extract_collected_labels(text: str) -> list[tuple[str, int]]:
    """Extract what an AskUserQuestion collects, based on <header> or <question> text.

    Args:
        text: SKILL.md full content.

    Returns:
        List of (label, line_number) tuples for each AskUserQuestion block found.
    """
    collected = []
    for m in re.finditer(
        r'<interaction[^>]*tool=["\']AskUserQuestion["\'][^>]*>(.*?)</interaction>',
        text,
        re.DOTALL,
    ):
        block = m.group(1)
        line_num = _line_of(text, m.start())
        # Try header first, then question
        header_m = re.search(r"<header\s*>(.*?)</header>", block, re.DOTALL)
        question_m = re.search(r"<question\s*>(.*?)</question>", block, re.DOTALL)
        label = None
        if header_m:
            label = header_m.group(1).strip()
        elif question_m:
            label = question_m.group(1).strip()
        if label:
            collected.append((label, line_num))
    return collected


def check_dead_collect(skill_md_content: str) -> list:
    """Detect inputs collected in intake that are never referenced downstream.

    Args:
        skill_md_content: Full text of SKILL.md.

    Returns:
        List of finding dicts.
    """
    findings = []
    text = skill_md_content

    # Extract workflow phases and their content, tagged by name
    phases: dict[str, str] = {}
    for m in re.finditer(
        r'<phase\s+name=["\']([^"\']+)["\'][^>]*>(.*?)</phase>', text, re.DOTALL
    ):
        phases[m.group(1)] = m.group(2)

    intake_text = phases.get("intake", "")
    non_intake = {k: v for k, v in phases.items() if k != "intake"}
    downstream_text = "\n".join(non_intake.values())

    # Labels collected in intake
    collected = _extract_collected_labels(intake_text)
    for label, line_num in collected:
        # Build keyword set from label words (e.g. "Analysis Mode" → ["analysis", "mode"])
        keywords = [w.lower() for w in re.split(r"\W+", label) if len(w) > 3]
        if not keywords:
            continue
        referenced = any(kw in downstream_text.lower() for kw in keywords)
        if not referenced:
            findings.append(
                _finding(
                    check_id="PL-dead-collect",
                    severity="WARN",
                    category="DEAD_COLLECT",
                    file="SKILL.md",
                    line=line_num,
                    snippet=label,
                    message=(
                        f'Input collected in intake ("{label}") at line {line_num} '
                        f"does not appear to be used in any downstream phase. "
                        "Collecting input that goes nowhere wastes user interaction."
                    ),
                    recommendation=(
                        f"Either reference the collected value downstream (e.g., in a "
                        f'<branch condition="..."> or step prose), or remove the question.'
                    ),
                )
            )

    # Check if mode is collected but never branched on
    mode_collected = any("mode" in label.lower() for label, _ in collected)
    if mode_collected:
        branch_on_mode = bool(
            re.search(
                r'<branch\s+condition=["\'][^"\']*mode\s+is',
                downstream_text,
                re.IGNORECASE,
            )
        )
        if not branch_on_mode:
            findings.append(
                _finding(
                    check_id="PL-mode-no-branch",
                    severity="WARN",
                    category="DEAD_COLLECT",
                    file="SKILL.md",
                    message=(
                        "Analysis mode is collected in intake but no downstream phase "
                        'contains a <branch condition="mode is ..."> element. The mode '
                        "selection has no effect on workflow execution."
                    ),
                    recommendation=(
                        'Add <branch condition="mode is X"> elements in affected phases '
                        "to conditionally skip or modify behavior based on the selected mode."
                    ),
                )
            )

    return findings


# ---------------------------------------------------------------------------
# Check 3: AGENT_USAGE — definition / invocation consistency
# ---------------------------------------------------------------------------


def _extract_defined_agents(text: str) -> dict[str, int]:
    """Extract agent names from the <agents> XML block in SKILL.md.

    Args:
        text: SKILL.md full content.

    Returns:
        Dict mapping agent name → approximate line number.
    """
    agents = {}
    agents_block_m = re.search(r"<agents>(.*?)</agents>", text, re.DOTALL)
    if not agents_block_m:
        return agents
    block = agents_block_m.group(1)
    block_start = agents_block_m.start()
    for m in re.finditer(r'<agent\s+name=["\']([^"\']+)["\']', block):
        line_num = _line_of(text, block_start + m.start())
        agents[m.group(1)] = line_num
    return agents


def _extract_workflow_agent_refs(text: str) -> list[tuple[str, int]]:
    """Find agent name references in workflow phase content.

    Args:
        text: SKILL.md full content.

    Returns:
        List of (agent_name, line_number) tuples for each reference found.
    """
    refs = []
    # Match patterns like "Invoke the X agent" or "invoke X-agent" or agent name in <context><read> agents/
    patterns = [
        re.compile(r"(?i)invoke\s+the\s+([a-z][a-z0-9\-]+)\s+agent"),
        re.compile(r"(?i)invoke\s+([a-z][a-z0-9\-]+)\s+agent"),
        re.compile(r"agents/([a-z][a-z0-9_\-]+)\.md"),
    ]
    workflow_m = re.search(r"<workflow>(.*?)</workflow>", text, re.DOTALL)
    if not workflow_m:
        return refs
    wf_text = workflow_m.group(1)
    wf_start = workflow_m.start()
    for pattern in patterns:
        for m in pattern.finditer(wf_text):
            name = m.group(1).replace("_", "-").rstrip(".md")
            line_num = _line_of(text, wf_start + m.start())
            refs.append((name, line_num))
    return refs


def check_agent_usage(skill_root: Path, skill_md_content: str) -> list:
    """Check agent definition/invocation consistency and file existence.

    Args:
        skill_root: Root of the skill directory.
        skill_md_content: Full text of SKILL.md.

    Returns:
        List of finding dicts.
    """
    findings = []
    text = skill_md_content

    defined = _extract_defined_agents(text)
    workflow_refs = _extract_workflow_agent_refs(text)
    invoked_names = {name for name, _ in workflow_refs}

    # PL-agent-defined-not-invoked: defined but never referenced in workflow
    for agent_name, line_num in defined.items():
        # Normalize: check both exact name and name without prefix
        normalized_refs = {r.replace("_", "-") for r in invoked_names}
        if (
            agent_name not in normalized_refs
            and agent_name.replace("-", "_") not in normalized_refs
        ):
            findings.append(
                _finding(
                    check_id="PL-agent-dead",
                    severity="WARN",
                    category="AGENT_USAGE",
                    file="SKILL.md",
                    line=line_num,
                    snippet=agent_name,
                    message=(
                        f'Agent "{agent_name}" is defined in the <agents> block '
                        f"(line {line_num}) but is never invoked in any workflow phase. "
                        "Dead agent definitions add confusion without adding capability."
                    ),
                    recommendation=(
                        f"Either add an invocation step in the appropriate workflow phase, "
                        f"or remove the agent definition if it is no longer needed."
                    ),
                )
            )

    # PL-agent-invoked-not-defined: invoked in workflow but not in <agents>
    defined_normalized = {k.replace("-", "_"): v for k, v in defined.items()}
    defined_normalized.update(defined)
    for agent_name, line_num in workflow_refs:
        norm = agent_name.replace("-", "_")
        if agent_name not in defined and norm not in defined_normalized:
            findings.append(
                _finding(
                    check_id="PL-agent-undefined",
                    severity="ERROR",
                    category="AGENT_USAGE",
                    file="SKILL.md",
                    line=line_num,
                    snippet=agent_name,
                    message=(
                        f'Workflow at line {line_num} invokes agent "{agent_name}" '
                        "but this agent is not defined in the <agents> block. "
                        "Claude will have no model or I/O contract to follow."
                    ),
                    recommendation=(
                        f'Add an <agent name="{agent_name}"> entry to the <agents> '
                        "block with ref, model, purpose, invoked-by, inputs, and outputs."
                    ),
                )
            )

    # PL-agent-file-missing: ref path in <agents> block doesn't exist on disk
    agents_block_m = re.search(r"<agents>(.*?)</agents>", text, re.DOTALL)
    if agents_block_m:
        for m in re.finditer(r'ref=["\']([^"\']+)["\']', agents_block_m.group(1)):
            ref_path = m.group(1).replace("${CLAUDE_PLUGIN_ROOT}/", "")
            abs_path = skill_root / ref_path
            if not abs_path.exists():
                line_num = _line_of(text, agents_block_m.start() + m.start())
                findings.append(
                    _finding(
                        check_id="PL-agent-file-missing",
                        severity="ERROR",
                        category="AGENT_USAGE",
                        file="SKILL.md",
                        line=line_num,
                        snippet=ref_path,
                        message=(
                            f'Agent ref path "{ref_path}" does not exist on disk. '
                            "Claude cannot read agent instructions that aren't present."
                        ),
                        recommendation=f"Create the file at {ref_path} or fix the ref path.",
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Check 4: WORKFLOW — sequencing, gates, branches, depends-on
# ---------------------------------------------------------------------------


def _extract_phases(text: str) -> dict[str, dict]:
    """Extract all phases from the <workflow> block with metadata.

    Args:
        text: SKILL.md full content.

    Returns:
        Dict mapping phase name → {sequence, depends_on, content, line}.
    """
    phases = {}
    workflow_m = re.search(r"<workflow>(.*?)</workflow>", text, re.DOTALL)
    if not workflow_m:
        return phases
    wf_text = workflow_m.group(1)
    wf_start = workflow_m.start()
    for m in re.finditer(r"<phase\s+([^>]*)>(.*?)</phase>", wf_text, re.DOTALL):
        attrs_text = m.group(1)
        content = m.group(2)
        line_num = _line_of(text, wf_start + m.start())
        name_m = re.search(r'name=["\']([^"\']+)["\']', attrs_text)
        seq_m = re.search(r'sequence=["\']([^"\']+)["\']', attrs_text)
        dep_m = re.search(r'depends-on=["\']([^"\']+)["\']', attrs_text)
        name = name_m.group(1) if name_m else f"unnamed-{line_num}"
        phases[name] = {
            "sequence": int(seq_m.group(1)) if seq_m else 999,
            "depends_on": dep_m.group(1) if dep_m else None,
            "content": content,
            "line": line_num,
        }
    return phases


def check_workflow(skill_md_content: str) -> list:
    """Check workflow phase integrity: depends-on, gates, branches, orphans.

    Args:
        skill_md_content: Full text of SKILL.md.

    Returns:
        List of finding dicts.
    """
    findings = []
    text = skill_md_content
    phases = _extract_phases(text)
    phase_names = set(phases.keys())

    for name, meta in phases.items():
        content = meta["content"]
        line_num = meta["line"]

        # PL-depends-on-missing: depends-on references a phase that doesn't exist
        dep = meta.get("depends_on")
        if dep and dep not in phase_names:
            findings.append(
                _finding(
                    check_id="PL-depends-missing",
                    severity="ERROR",
                    category="WORKFLOW",
                    file="SKILL.md",
                    line=line_num,
                    snippet=f'depends-on="{dep}"',
                    message=(
                        f'Phase "{name}" declares depends-on="{dep}" but no phase '
                        f'named "{dep}" exists in the workflow. This breaks execution ordering.'
                    ),
                    recommendation=(
                        f"Fix the depends-on value to match an existing phase name: "
                        f"{', '.join(sorted(phase_names))}."
                    ),
                )
            )

        # PL-gate-empty: <gate> element with no content
        for gm in re.finditer(r"<gate\s*>([\s]*)</gate>", content):
            gate_content = gm.group(1).strip()
            if not gate_content:
                g_line = _line_of(text, phases[name]["line"])
                findings.append(
                    _finding(
                        check_id="PL-gate-empty",
                        severity="WARN",
                        category="WORKFLOW",
                        file="SKILL.md",
                        line=g_line,
                        snippet="<gate></gate>",
                        message=(
                            f'Empty <gate> element found in phase "{name}". '
                            "A gate with no condition is never enforced."
                        ),
                        recommendation="Add a specific gate condition, e.g. <gate>If X is missing, stop and report.</gate>",
                    )
                )

        # PL-branch-no-condition: <branch> with missing or empty condition
        for bm in re.finditer(r"<branch\b([^>]*)>", content):
            attrs = bm.group(1)
            cond_m = re.search(r'condition=["\']([^"\']*)["\']', attrs)
            b_line = _line_of(text, meta["line"])
            if not cond_m:
                findings.append(
                    _finding(
                        check_id="PL-branch-no-condition",
                        severity="ERROR",
                        category="WORKFLOW",
                        file="SKILL.md",
                        line=b_line,
                        snippet=bm.group(0),
                        message=(
                            f'<branch> in phase "{name}" has no condition attribute. '
                            "Claude cannot determine when to take this branch."
                        ),
                        recommendation='Add a condition attribute: <branch condition="mode is Audit">',
                    )
                )
            elif not cond_m.group(1).strip():
                findings.append(
                    _finding(
                        check_id="PL-branch-empty-condition",
                        severity="ERROR",
                        category="WORKFLOW",
                        file="SKILL.md",
                        line=b_line,
                        snippet=bm.group(0),
                        message=(
                            f'<branch> in phase "{name}" has an empty condition. '
                            "An empty condition is always false and the branch is dead."
                        ),
                        recommendation='Fill in the condition: condition="mode is X" or condition="no scripts found"',
                    )
                )

    # PL-no-workflow: no <workflow> block at all
    if not phases:
        workflow_present = "<workflow>" in text or "<workflow " in text
        if not workflow_present:
            findings.append(
                _finding(
                    check_id="PL-no-workflow",
                    severity="ERROR",
                    category="WORKFLOW",
                    file="SKILL.md",
                    message=(
                        "SKILL.md has no <workflow> block. Without a workflow, Claude has "
                        "no structured execution path to follow."
                    ),
                    recommendation="Add a <workflow> block with at least one <phase> element.",
                )
            )

    return findings


# ---------------------------------------------------------------------------
# Check 5: REFERENCE — file paths referenced but not on disk
# ---------------------------------------------------------------------------


def check_references(skill_root: Path, skill_md_content: str) -> list:
    """Check that all referenced files (scripts, references, agents) exist on disk.

    Args:
        skill_root: Root of the skill directory.
        skill_md_content: Full text of SKILL.md.

    Returns:
        List of finding dicts.
    """
    findings = []
    text = skill_md_content

    # Script tags in workflow
    for m in re.finditer(
        r"<script>\s*\$\{CLAUDE_PLUGIN_ROOT\}/([^<\s]+)\s*</script>", text
    ):
        rel = m.group(1).strip()
        # Strip arguments (everything after first space)
        script_file = rel.split()[0] if " " in rel else rel
        abs_path = skill_root / script_file
        line_num = _line_of(text, m.start())
        if not abs_path.exists():
            findings.append(
                _finding(
                    check_id="PL-script-missing",
                    severity="ERROR",
                    category="REFERENCE",
                    file="SKILL.md",
                    line=line_num,
                    snippet=script_file,
                    message=(
                        f"Workflow step at line {line_num} references script "
                        f'"{script_file}" but the file does not exist. '
                        "Claude will fail trying to run this step."
                    ),
                    recommendation=f"Create the script at {script_file} or fix the path.",
                )
            )

    # References block
    refs_block_m = re.search(r"<references>(.*?)</references>", text, re.DOTALL)
    if refs_block_m:
        for m in re.finditer(r'path=["\']([^"\']+)["\']', refs_block_m.group(1)):
            ref_path = m.group(1).replace("${CLAUDE_PLUGIN_ROOT}/", "")
            abs_path = skill_root / ref_path
            if not abs_path.exists():
                line_num = _line_of(text, refs_block_m.start() + m.start())
                findings.append(
                    _finding(
                        check_id="PL-ref-missing",
                        severity="WARN",
                        category="REFERENCE",
                        file="SKILL.md",
                        line=line_num,
                        snippet=ref_path,
                        message=(
                            f'References block points to "{ref_path}" which does not '
                            "exist on disk. Claude will silently skip this reference."
                        ),
                        recommendation=f"Create the file at {ref_path} or remove the stale reference.",
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Check 6: CONTEXT_READ — agent files must read SKILL.md
# ---------------------------------------------------------------------------


def check_context_reads(skill_root: Path) -> list:
    """Verify agent files have proper <context><read> blocks.

    Args:
        skill_root: Root of the skill directory.

    Returns:
        List of finding dicts.
    """
    findings = []
    for agent_path in _find_md_files(skill_root):
        rel = str(agent_path.relative_to(skill_root))
        content = _read(agent_path)

        # PL-no-context: no <context> block at all
        has_context = bool(re.search(r"<context\b", content))
        if not has_context:
            findings.append(
                _finding(
                    check_id="PL-no-context",
                    severity="ERROR",
                    category="CONTEXT_READ",
                    file=rel,
                    message=(
                        f'Agent file "{rel}" has no <context> block. Per B5, every '
                        "agent must begin with a <context><read> block referencing SKILL.md."
                    ),
                    recommendation=(
                        "Add immediately after YAML frontmatter:\n"
                        "<context>\n"
                        '  <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>\n'
                        "</context>"
                    ),
                )
            )
            continue

        # PL-no-skill-read: <context> block doesn't read SKILL.md
        reads_skill_md = bool(re.search(r"SKILL\.md", content))
        if not reads_skill_md:
            findings.append(
                _finding(
                    check_id="PL-context-no-skillmd",
                    severity="ERROR",
                    category="CONTEXT_READ",
                    file=rel,
                    message=(
                        f'Agent file "{rel}" has a <context> block but does not '
                        "read SKILL.md. The agent will lack access to security rules, "
                        "paths, and behavior definitions from the parent skill."
                    ),
                    recommendation=(
                        'Add <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read> '
                        "as the first item in the <context> block."
                    ),
                )
            )

        # PL-context-not-first: <context> block not immediately after frontmatter
        # Frontmatter ends at second '---'
        fm_end = text_after_frontmatter_start(content)
        if fm_end is not None:
            content_after_fm = content[fm_end:]
            first_non_whitespace = content_after_fm.lstrip()
            if not first_non_whitespace.startswith("<context"):
                findings.append(
                    _finding(
                        check_id="PL-context-not-first",
                        severity="WARN",
                        category="CONTEXT_READ",
                        file=rel,
                        message=(
                            f'Agent file "{rel}" has a <context> block but it does not '
                            "appear immediately after the YAML frontmatter. By convention "
                            "the context block is always first so the agent loads SKILL.md "
                            "before reading any other instructions."
                        ),
                        recommendation="Move the <context> block to be the first element after the YAML frontmatter.",
                    )
                )

    return findings


def text_after_frontmatter_start(content: str) -> Optional[int]:
    """Return character offset after the closing '---' of YAML frontmatter.

    Args:
        content: Full file text.

    Returns:
        Character offset after frontmatter, or None if no frontmatter found.
    """
    if not content.startswith("---"):
        return None
    second = content.find("\n---", 3)
    if second == -1:
        return None
    return second + 4  # skip past \n---


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


def run_lint(skill_path: str, session_dir: str) -> dict:
    """Run all prompt lint checks and write prompt_lint.json.

    Args:
        skill_path: Path to the skill directory.
        session_dir: Session directory where prompt_lint.json will be written.

    Returns:
        The prompt lint results dict that was written to disk.

    Raises:
        FileNotFoundError: If skill_path does not exist.
        ValueError: If skill_path contains '..' segments.
    """
    if ".." in Path(skill_path).parts:
        raise ValueError(f"Path traversal rejected: {skill_path}")
    skill_root = Path(skill_path).resolve()
    if not skill_root.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_root}")

    session = Path(session_dir)
    session.mkdir(parents=True, exist_ok=True)

    skill_md_path = skill_root / "SKILL.md"
    skill_md_content = _read(skill_md_path) if skill_md_path.exists() else ""

    all_findings = []

    if not skill_md_content:
        all_findings.append(
            _finding(
                check_id="PL-no-skill-md",
                severity="ERROR",
                category="WORKFLOW",
                file="SKILL.md",
                message="SKILL.md not found or empty — cannot run prompt lint checks.",
                recommendation="Ensure SKILL.md exists and contains workflow instructions.",
            )
        )
    else:
        print(
            "[prompt_linter] Check 1/6: Interaction / AskUserQuestion...",
            file=sys.stderr,
        )
        f = check_interaction(skill_root, skill_md_content)
        all_findings.extend(f)
        print(f"  {len(f)} finding(s)", file=sys.stderr)

        print("[prompt_linter] Check 2/6: Dead collection...", file=sys.stderr)
        f = check_dead_collect(skill_md_content)
        all_findings.extend(f)
        print(f"  {len(f)} finding(s)", file=sys.stderr)

        print("[prompt_linter] Check 3/6: Agent usage...", file=sys.stderr)
        f = check_agent_usage(skill_root, skill_md_content)
        all_findings.extend(f)
        print(f"  {len(f)} finding(s)", file=sys.stderr)

        print("[prompt_linter] Check 4/6: Workflow integrity...", file=sys.stderr)
        f = check_workflow(skill_md_content)
        all_findings.extend(f)
        print(f"  {len(f)} finding(s)", file=sys.stderr)

        print("[prompt_linter] Check 5/6: Reference integrity...", file=sys.stderr)
        f = check_references(skill_root, skill_md_content)
        all_findings.extend(f)
        print(f"  {len(f)} finding(s)", file=sys.stderr)

    print("[prompt_linter] Check 6/6: Context reads in agent files...", file=sys.stderr)
    f = check_context_reads(skill_root)
    all_findings.extend(f)
    print(f"  {len(f)} finding(s)", file=sys.stderr)

    # Build summary
    by_severity = {"ERROR": 0, "WARN": 0, "INFO": 0}
    by_category: dict[str, int] = {}
    for finding in all_findings:
        sev = finding.get("severity", "INFO")
        if sev in by_severity:
            by_severity[sev] += 1
        cat = finding.get("category", "OTHER")
        by_category[cat] = by_category.get(cat, 0) + 1

    overall = "PASS"
    if by_severity["ERROR"] > 0:
        overall = "FAIL"
    elif by_severity["WARN"] > 0:
        overall = "WARN"

    result = {
        "skill_path": str(skill_root),
        "linted_at": datetime.now(timezone.utc).isoformat(),
        "files_analyzed": [
            "SKILL.md",
            *[str(p.relative_to(skill_root)) for p in _find_md_files(skill_root)],
        ],
        "findings": all_findings,
        "summary": {
            "total_findings": len(all_findings),
            "by_severity": by_severity,
            "by_category": by_category,
            "overall": overall,
        },
    }

    output_path = session / "prompt_lint.json"
    _save_json(str(output_path), result, schema=PROMPT_LINT_SCHEMA)
    print(
        f"[prompt_linter] prompt_lint.json written to {output_path} — overall: {overall}",
        file=sys.stderr,
    )
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for CLI usage."""
    parser = argparse.ArgumentParser(
        description="Skill Tester — Prompt & Instruction Quality Linter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Checks AskUserQuestion completeness, dead collection, agent usage,\n"
            "workflow integrity, reference integrity, and context reads.\n"
            "Output: <session_dir>/prompt_lint.json"
        ),
    )
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument(
        "--session-dir", required=True, help="Session directory for output"
    )

    args = parser.parse_args()

    try:
        result = run_lint(args.skill_path, args.session_dir)
        print(json.dumps(result["summary"], indent=2))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
