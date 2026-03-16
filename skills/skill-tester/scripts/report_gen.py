#!/usr/bin/env python3
"""
report_gen.py — Generate a unified HTML analysis report from a skill-tester session.

Usage:
  python scripts/report_gen.py --session-dir session/ --output session/report.html
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from schemas import (
    INVENTORY_SCHEMA,
    SCAN_RESULTS_SCHEMA,
    PROMPT_LINT_SCHEMA,
    PROMPT_REVIEW_SCHEMA,
    SECURITY_REPORT_SCHEMA,
    CODE_REVIEW_SCHEMA,
)
from shared_io import _validate_json_schema


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_json(path: Path, schema: dict | None = None) -> Optional[Any]:
    """Load a JSON file, optionally validating against a schema.

    Args:
        path: Path to the JSON file.
        schema: If provided, validate and log warnings on failure (still returns data).

    Returns:
        Parsed JSON data, or None if file doesn't exist.
    """
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if schema is not None and isinstance(data, dict):
                errors = _validate_json_schema(data, schema)
                if errors:
                    logging.warning(
                        "Schema validation warning for %s: %s",
                        path, "; ".join(errors),
                    )
            return data
        except Exception as e:
            return {"_load_error": str(e)}
    return None


def _load_jsonl(path: Path) -> list:
    results = []
    if not path.exists():
        return results
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return results


def load_session(session_dir: str) -> dict:
    """Load all session data files into a single dict for report generation.

    Args:
        session_dir: Path to the session directory.

    Returns:
        Dict with all session data keyed by analysis type.
    """
    base = Path(session_dir)
    return {
        "inventory": _load_json(base / "inventory.json", schema=INVENTORY_SCHEMA),
        "scan_results": _load_json(base / "scan_results.json", schema=SCAN_RESULTS_SCHEMA),
        "prompt_lint": _load_json(base / "prompt_lint.json", schema=PROMPT_LINT_SCHEMA),
        "prompt_review": _load_json(base / "prompt_review.json", schema=PROMPT_REVIEW_SCHEMA),
        "api_calls": _load_jsonl(base / "api_log.jsonl"),
        "script_runs": _load_jsonl(base / "script_runs.jsonl"),
        "security": _load_json(base / "security_report.json", schema=SECURITY_REPORT_SCHEMA),
        "code_review": _load_json(base / "code_review.json", schema=CODE_REVIEW_SCHEMA),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

SEVERITY_COLORS = {
    "CRITICAL": "#dc2626",
    "HIGH": "#ea580c",
    "MEDIUM": "#d97706",
    "LOW": "#65a30d",
    "INFO": "#6b7280",
}

SCORE_COLORS = [
    (9, "#16a34a"),
    (7, "#65a30d"),
    (5, "#d97706"),
    (0, "#dc2626"),
]

PROMPT_SEVERITY_COLORS = {
    "ERROR": "#dc2626",
    "WARN": "#d97706",
    "INFO": "#6b7280",
}


def _score_color(score: float) -> str:
    for threshold, color in SCORE_COLORS:
        if score >= threshold:
            return color
    return "#dc2626"


def _esc(s: Any) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _expandable(text: str, max_chars: int = 120) -> str:
    """Render text with expand/collapse if it exceeds max_chars."""
    if len(text) <= max_chars:
        return _esc(text)
    preview = _esc(text[:max_chars])
    full = _esc(text)
    return (
        f'<details class="expand-cell">'
        f'<summary>{preview}&hellip;</summary>'
        f'<div class="expand-full">{full}</div>'
        f'</details>'
    )


def _badge(text: str, color: str) -> str:
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.78em;font-weight:600">{_esc(text)}</span>'


def _section(title: str, content: str, id: str = "") -> str:
    id_attr = f' id="{id}"' if id else ""
    return f"""
<section{id_attr} style="margin:2rem 0">
  <h2 style="font-size:1.2rem;font-weight:700;border-bottom:2px solid #e5e7eb;padding-bottom:.4rem;margin-bottom:1rem">{title}</h2>
  {content}
</section>"""


def _table(headers: list, rows: list) -> str:
    ths = "".join(f"<th>{_esc(h)}</th>" for h in headers)
    trs = ""
    for row in rows:
        tds = "".join(f"<td>{c}</td>" for c in row)
        trs += f"<tr>{tds}</tr>"
    return f"""<table style="width:100%;border-collapse:collapse;font-size:.875rem">
<thead><tr style="background:#f3f4f6">{ths}</tr></thead>
<tbody>{trs}</tbody>
</table>"""


def _code(text: str, max_lines: int = 30) -> str:
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"… ({len(lines) - max_lines} more lines)"]
    escaped = _esc("\n".join(lines))
    return f'<pre style="background:#1e1e2e;color:#cdd6f4;padding:1rem;border-radius:6px;overflow-x:auto;font-size:.8rem;white-space:pre-wrap">{escaped}</pre>'


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_summary_card(data: dict) -> str:
    inv = data.get("inventory") or {}
    api_calls = data.get("api_calls") or []
    runs = data.get("script_runs") or []
    sec = data.get("security") or {}
    cr = data.get("code_review") or {}

    findings = sec.get("findings") or []
    critical = sum(1 for f in findings if f.get("severity") == "CRITICAL")
    high = sum(1 for f in findings if f.get("severity") == "HIGH")
    score = cr.get("overall_score", "N/A")
    score_color = _score_color(float(score)) if isinstance(score, (int, float)) else "#6b7280"

    skill_name = (inv.get("frontmatter") or {}).get("name", "Unknown Skill")
    total_scripts = (inv.get("summary") or {}).get("total_scripts", 0)
    api_errors = sum(1 for c in api_calls if c.get("error"))

    cards = [
        ("Skill", f"<strong>{_esc(skill_name)}</strong>", "#3b82f6"),
        ("Scripts", str(total_scripts), "#8b5cf6"),
        ("API Calls", f"{len(api_calls)} ({api_errors} errors)", "#0ea5e9"),
        ("Script Runs", str(len(runs)), "#14b8a6"),
        ("Sec Issues", f"{_badge('CRIT', SEVERITY_COLORS['CRITICAL'])} {critical} &nbsp; {_badge('HIGH', SEVERITY_COLORS['HIGH'])} {high}", "#ef4444"),
        ("Code Score", f'<span style="color:{score_color};font-weight:700;font-size:1.2em">{score}/10</span>', score_color),
    ]

    html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem;margin-bottom:2rem">'
    for label, value, accent in cards:
        html += f"""<div style="border:1px solid #e5e7eb;border-radius:8px;padding:1rem;border-top:3px solid {accent}">
  <div style="font-size:.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:.05em">{label}</div>
  <div style="margin-top:.25rem">{value}</div>
</div>"""
    html += "</div>"
    return html


def _build_inventory_section(inv: Optional[dict]) -> str:
    if not inv:
        return "<p><em>No inventory data.</em></p>"
    summary = inv.get("summary") or {}
    scripts = inv.get("scripts") or []

    # Scripts table
    rows = []
    for s in scripts:
        danger = ", ".join(s.get("dangerous_calls") or []) or "—"
        secrets = len(s.get("potential_secrets") or [])
        api = "✓" if s.get("calls_anthropic_api") else "—"
        rows.append([
            f'<code>{_esc(Path(s["path"]).name)}</code>',
            str(s.get("lines", "?")),
            api,
            _badge(danger, "#dc2626") if danger != "—" else "—",
            _badge(str(secrets), SEVERITY_COLORS["HIGH"]) if secrets > 0 else "0",
        ])

    scripts_table = _table(["Script", "Lines", "Calls API", "Dangerous Calls", "Potential Secrets"], rows) if rows else "<p><em>No scripts found.</em></p>"

    # Sidebar lists for commands, agents, references, assets
    def _file_list(items: list, label: str) -> str:
        if not items:
            return ""
        li = "".join(f"<li><code>{_esc(r)}</code></li>" for r in items)
        return f'<strong style="font-size:.85rem">{_esc(label)}</strong><ul style="font-size:.8rem;margin-top:.25rem;margin-bottom:.75rem">{li}</ul>'

    commands = inv.get("commands") or []
    agents = inv.get("agents") or []
    refs = inv.get("references") or []
    assets = inv.get("assets") or []

    sidebar = _file_list(commands, "Commands") + _file_list(agents, "Agents") + _file_list(refs, "References") + _file_list(assets, "Assets")
    if not sidebar:
        sidebar = "<em style='font-size:.8rem'>No additional files.</em>"

    # Summary counts
    counts = []
    counts.append(f"<strong>{len(scripts)}</strong> scripts")
    if commands:
        counts.append(f"<strong>{len(commands)}</strong> commands")
    if agents:
        counts.append(f"<strong>{len(agents)}</strong> agents")
    if refs:
        counts.append(f"<strong>{len(refs)}</strong> references")
    if assets:
        counts.append(f"<strong>{len(assets)}</strong> assets")
    count_line = f'<div style="font-size:.85rem;margin-bottom:.75rem">{" · ".join(counts)}</div>'

    return f"""
{count_line}
<div style="display:grid;grid-template-columns:1fr 220px;gap:1.5rem">
  <div>{scripts_table}</div>
  <div>{sidebar}</div>
</div>"""


def _build_analysis_summary_section(data: dict, session_dir: str) -> str:
    """Build an AI-generated narrative summary from all available session data."""
    scan = data.get("scan_results") or {}
    lint = data.get("prompt_lint") or {}
    review = data.get("prompt_review") or {}
    sec = data.get("security") or {}
    cr = data.get("code_review") or {}
    inv = data.get("inventory") or {}

    # Collect key metrics
    scan_summary = scan.get("summary") or {}
    scan_risk = scan_summary.get("risk_rating", "N/A")
    scan_total = scan_summary.get("total_findings", 0)
    scan_by_sev = scan_summary.get("by_severity") or {}

    lint_summary = lint.get("summary") or {}
    lint_overall = lint_summary.get("overall", "N/A")
    lint_errors = (lint_summary.get("by_severity") or {}).get("ERROR", 0)

    prompt_score = (review.get("prompt_score") or {}).get("overall", "N/A")
    prompt_findings = len(review.get("findings") or [])

    sec_findings = sec.get("findings") or []
    sec_risk = (sec.get("summary") or {}).get("risk_rating", sec.get("risk_rating", "N/A"))

    code_score = cr.get("overall_score", "N/A")
    code_scripts = cr.get("scripts") or []
    code_issues = sum(len(s.get("issues") or []) for s in code_scripts)

    inv_summary = inv.get("summary") or {}
    total_scripts = inv_summary.get("total_scripts", 0)
    total_commands = inv_summary.get("total_commands", 0)
    total_agents = inv_summary.get("total_agents", 0)

    # Build narrative
    parts = []
    skill_name = (inv.get("frontmatter") or {}).get("name", "this skill")
    parts.append(f"Analysis of <strong>{_esc(skill_name)}</strong> covered {total_scripts} scripts")
    extras = []
    if total_commands:
        extras.append(f"{total_commands} commands")
    if total_agents:
        extras.append(f"{total_agents} agents")
    if extras:
        parts[-1] += f", {', '.join(extras)}"
    parts[-1] += "."

    # Scan narrative
    if scan_total > 0:
        crit = scan_by_sev.get("CRITICAL", 0)
        high = scan_by_sev.get("HIGH", 0)
        parts.append(
            f"The deterministic scan found <strong>{scan_total}</strong> findings "
            f"(risk: <strong>{_esc(scan_risk)}</strong>"
            + (f", {crit} critical, {high} high" if crit or high else "")
            + ")."
        )

    # Prompt quality narrative
    if prompt_score != "N/A":
        parts.append(
            f"Prompt quality scored <strong>{prompt_score}/10</strong> with {prompt_findings} findings. "
            f"Lint result: <strong>{_esc(lint_overall)}</strong>"
            + (f" ({lint_errors} errors)" if lint_errors else "")
            + "."
        )

    # Security narrative
    if sec_findings:
        parts.append(
            f"Security audit identified <strong>{len(sec_findings)}</strong> findings "
            f"(risk: <strong>{_esc(str(sec_risk))}</strong>)."
        )

    # Code quality narrative
    if code_score != "N/A":
        parts.append(
            f"Code quality scored <strong>{code_score}/10</strong> across {len(code_scripts)} scripts "
            f"with {code_issues} issues identified."
        )

    narrative = " ".join(parts)

    # Top 3 Recommendations (synthesized from all sources)
    recommendations = []
    # From scan findings (HIGH/CRITICAL)
    for f in (scan.get("findings") or []):
        if f.get("severity") in ("CRITICAL", "HIGH"):
            recommendations.append(f.get("message", ""))
    # From prompt lint errors
    seen_checks = set()
    for f in (lint.get("findings") or []):
        if f.get("severity") == "ERROR":
            check = f.get("check_id", "")
            if check not in seen_checks:
                seen_checks.add(check)
                recommendations.append(f.get("message", ""))
    # From security findings
    for f in sec_findings:
        if f.get("severity") in ("CRITICAL", "HIGH"):
            recommendations.append(f.get("description", ""))
    # From code review
    for s in code_scripts:
        for i in (s.get("issues") or []):
            recommendations.append(i.get("description", ""))
    # Deduplicate and take top 3
    seen = set()
    unique_recs = []
    for r in recommendations:
        r_short = r[:80]
        if r and r_short not in seen:
            seen.add(r_short)
            unique_recs.append(r)
    top_recs = unique_recs[:3]

    # Top 3 Strengths
    strengths = []
    if scan_by_sev.get("CRITICAL", 0) == 0:
        strengths.append("No critical security findings detected in deterministic scan.")
    if inv_summary.get("potential_secret_count", 0) == 0:
        strengths.append("No hardcoded secrets or credentials found in scripts.")
    if inv_summary.get("scripts_calling_api", 0) == 0:
        strengths.append("Skill uses native Claude tool use — no direct API calls to manage.")
    if prompt_score != "N/A" and isinstance(prompt_score, (int, float)) and prompt_score >= 7:
        strengths.append(f"Prompt quality score of {prompt_score}/10 indicates well-structured instructions.")
    if code_score != "N/A" and isinstance(code_score, (int, float)) and code_score >= 7:
        strengths.append(f"Code quality score of {code_score}/10 shows solid implementation.")
    if total_commands > 0:
        strengths.append(f"Well-organized command structure with {total_commands} dedicated commands.")
    if total_agents > 0:
        strengths.append(f"Agent-based architecture with {total_agents} specialized agents.")
    top_strengths = strengths[:3]

    # Build HTML
    rec_html = ""
    if top_recs:
        rec_items = "".join(f"<li style='margin-bottom:.4rem'>{_expandable(r, 200)}</li>" for r in top_recs)
        rec_html = f"""
<div style="margin-top:1.25rem">
  <h3 style="font-size:.95rem;color:#dc2626;margin-bottom:.5rem">Top Recommendations</h3>
  <ol style="font-size:.875rem;padding-left:1.5rem">{rec_items}</ol>
</div>"""

    str_html = ""
    if top_strengths:
        str_items = "".join(f"<li style='margin-bottom:.4rem'>{_esc(s)}</li>" for s in top_strengths)
        str_html = f"""
<div style="margin-top:1.25rem">
  <h3 style="font-size:.95rem;color:#16a34a;margin-bottom:.5rem">Top Strengths</h3>
  <ol style="font-size:.875rem;padding-left:1.5rem">{str_items}</ol>
</div>"""

    # Session report link
    session_report_path = Path(session_dir) / "session_report.html"
    link_html = ""
    if session_report_path.exists():
        link_html = f"""
<div style="margin-top:1.25rem">
  <a href="session_report.html" style="display:inline-block;padding:.5rem 1rem;background:#3b82f6;color:#fff;border-radius:6px;text-decoration:none;font-size:.875rem">
    View Detailed Session Analysis
  </a>
</div>"""

    return f"""
<div style="font-size:.9rem;line-height:1.6">{narrative}</div>
{rec_html}
{str_html}
{link_html}"""


def _build_script_runs_section(runs: list) -> str:
    if not runs:
        return "<p><em>No script runs recorded.</em></p>"

    rows = []
    for r in runs:
        exit_code = r.get("exit_code", "?")
        status = _badge("OK", "#16a34a") if exit_code == 0 else _badge(f"EXIT {exit_code}", SEVERITY_COLORS["CRITICAL"])
        rows.append([
            f'<code>{_esc(Path(r.get("script", "?")).name)}</code>',
            f'<code>{_esc(r.get("run_id", ""))}</code>',
            f'{r.get("duration_ms", "?")}ms',
            status,
            str(len(r.get("files_created") or [])),
        ])

    table = _table(["Script", "Run ID", "Duration", "Exit", "Files Created"], rows)

    details = ""
    for r in runs:
        stdout = r.get("stdout") or ""
        stderr = r.get("stderr") or ""
        details += f"""<details style="margin:.5rem 0;border:1px solid #e5e7eb;border-radius:6px">
<summary style="padding:.5rem .75rem;cursor:pointer;font-size:.85rem">
  <code>{_esc(Path(r.get("script", "?")).name)}</code> — exit {r.get("exit_code", "?")} — {r.get("duration_ms", "?")}ms
</summary>
<div style="padding:.75rem;font-size:.8rem">
  <strong>stdout</strong>{_code(stdout or "(empty)", 20)}
  {"<strong>stderr</strong>" + _code(stderr, 10) if stderr else ""}
  {"<strong>Files created:</strong> " + ", ".join(f"<code>{_esc(f)}</code>" for f in r.get("files_created") or []) if r.get("files_created") else ""}
</div>
</details>"""

    return table + details


def _build_scan_results_section(scan: Optional[dict]) -> str:
    if not scan:
        return "<p><em>No deterministic scan results. validate_skill.py was not run.</em></p>"
    findings = scan.get("findings") or []
    summary = scan.get("summary") or {}
    coverage = scan.get("tool_coverage") or {}

    risk = summary.get("risk_rating", "UNKNOWN")
    risk_color = SEVERITY_COLORS.get(risk, "#6b7280") if risk != "CLEAR" else "#16a34a"

    tool_badges = " ".join(
        _badge(f"{k}: {v}", "#16a34a" if v == "ran" else "#6b7280")
        for k, v in coverage.items()
    )

    header = f"""<div style="display:flex;gap:1.5rem;align-items:center;margin-bottom:1rem">
  <div>Risk Rating: <span style="font-weight:700;color:{risk_color}">{_esc(risk)}</span></div>
  <div style="font-size:.8rem">{tool_badges}</div>
</div>"""

    if not findings:
        return header + '<p style="color:#16a34a">✓ No deterministic findings.</p>'

    rows = []
    for f in findings:
        sev = f.get("severity", "INFO")
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        rows.append([
            _badge(sev, color),
            f'<code>{_esc(Path(f.get("script", "?")).name)}</code>',
            str(f.get("line", "—")),
            _esc(f.get("check_id", "?")),
            _expandable(f.get("message", ""), 120),
        ])

    return header + _table(["Severity", "Script", "Line", "Check", "Message"], rows)


def _build_security_section(sec: Optional[dict]) -> str:
    if not sec:
        return "<p><em>No security report. Run audit mode to generate.</em></p>"

    findings = sec.get("findings") or []
    if not findings:
        return '<p style="color:#16a34a">✓ No security findings.</p>'

    rows = []
    for f in findings:
        sev = f.get("severity", "INFO")
        color = SEVERITY_COLORS.get(sev, "#6b7280")
        rows.append([
            _badge(sev, color),
            _esc(f.get("script", "?")),
            str(f.get("line", "?")),
            _esc(f.get("category", "?")),
            _expandable(f.get("description", ""), 120),
        ])

    return _table(["Severity", "Script", "Line", "Category", "Description"], rows)


def _build_prompt_lint_section(lint: Optional[dict]) -> str:
    if not lint:
        return "<p><em>No prompt lint data. Run full or audit mode to generate.</em></p>"

    findings = lint.get("findings") or []
    summary = lint.get("summary") or {}
    overall = summary.get("overall", "UNKNOWN")
    overall_color = {"PASS": "#16a34a", "WARN": "#d97706", "FAIL": "#dc2626"}.get(overall, "#6b7280")

    by_sev = summary.get("by_severity") or {}
    header = f"""<div style="display:flex;gap:1.5rem;align-items:center;margin-bottom:1rem">
  <div>Overall: <span style="font-weight:700;color:{overall_color}">{_esc(overall)}</span></div>
  <div style="font-size:.8rem">
    {_badge(f"ERROR: {by_sev.get('ERROR', 0)}", '#dc2626')}
    {_badge(f"WARN: {by_sev.get('WARN', 0)}", '#d97706')}
    {_badge(f"INFO: {by_sev.get('INFO', 0)}", '#6b7280')}
  </div>
</div>"""

    if not findings:
        return header + '<p style="color:#16a34a">No prompt lint findings.</p>'

    rows = []
    for f in findings:
        sev = f.get("severity", "INFO")
        color = PROMPT_SEVERITY_COLORS.get(sev, "#6b7280")
        rows.append([
            _badge(sev, color),
            f'<code>{_esc(f.get("file", "?"))}</code>',
            str(f.get("line", "—")),
            _esc(f.get("category", "?")),
            _expandable(f.get("message", ""), 120),
        ])

    return header + _table(["Severity", "File", "Line", "Category", "Message"], rows)


def _build_prompt_review_section(review: Optional[dict]) -> str:
    if not review:
        return "<p><em>No prompt review data. Run full or audit mode to generate.</em></p>"

    score = review.get("prompt_score") or {}
    overall = score.get("overall", "N/A")
    color = _score_color(float(overall)) if isinstance(overall, (int, float)) else "#6b7280"

    header = f'<div style="font-size:2rem;font-weight:700;color:{color};margin-bottom:1rem">{overall}/10</div>'

    dims = ["clarity", "completeness", "consistency", "tool_use_correctness", "agent_design"]
    dim_rows = [[_esc(d.replace("_", " ").title()), str(score.get(d, "?"))] for d in dims if d in score]
    dim_table = _table(["Dimension", "Score (0-10)"], dim_rows) if dim_rows else ""

    findings = review.get("findings") or []
    finding_rows = []
    for f in findings:
        sev = f.get("severity", "INFO")
        color = PROMPT_SEVERITY_COLORS.get(sev, "#6b7280")
        finding_rows.append([
            _badge(sev, color),
            _esc(f.get("category", "?")),
            _expandable(f.get("issue", ""), 150),
        ])
    finding_table = _table(["Severity", "Category", "Issue"], finding_rows) if finding_rows else ""

    summary_text = review.get("summary") or ""
    summary_html = f"<p style='margin-top:1rem;font-size:.875rem'>{_esc(summary_text)}</p>" if summary_text else ""

    return header + dim_table + finding_table + summary_html


def _build_code_review_section(cr: Optional[dict]) -> str:
    if not cr:
        return "<p><em>No code review report. Run audit mode to generate.</em></p>"

    per_script = cr.get("scripts") or []
    score = cr.get("overall_score", "N/A")

    # If no overall score but we have per-script data, compute an average
    if score == "N/A" and per_script:
        scores = [s.get("score") for s in per_script if isinstance(s.get("score"), (int, float))]
        if scores:
            score = round(sum(scores) / len(scores), 1)

    color = _score_color(float(score)) if isinstance(score, (int, float)) else "#6b7280"
    header = f'<div style="font-size:2rem;font-weight:700;color:{color};margin-bottom:1rem">{score}/10</div>'

    # Show summary text if present
    summary_text = cr.get("summary") or ""
    summary_html = f"<p style='margin-bottom:1rem;font-size:.875rem'>{_esc(summary_text)}</p>" if summary_text else ""

    # Show top recommendations if present
    top_recs = cr.get("recommendations") or cr.get("top_recommendations") or []
    recs_html = ""
    if top_recs:
        rec_items = "".join(f"<li>{_esc(r) if isinstance(r, str) else _esc(r.get('description', str(r)))}</li>" for r in top_recs[:5])
        recs_html = f'<div style="margin-bottom:1rem"><strong style="font-size:.85rem">Recommendations</strong><ol style="font-size:.85rem">{rec_items}</ol></div>'

    tables = ""
    for s in per_script:
        issues = s.get("issues") or []
        rows = [[
            _esc(i.get("category", "?")),
            _expandable(i.get("description", ""), 150),
            _expandable(i.get("suggestion", ""), 150),
        ] for i in issues]
        t = _table(["Category", "Issue", "Suggestion"], rows) if rows else "<p><em>No issues.</em></p>"
        tables += f"<h3 style='font-size:.9rem;margin:.75rem 0 .25rem'><code>{_esc(s.get('script', '?'))}</code> — score: <strong>{s.get('score', '?')}</strong>/10</h3>{t}"

    if not per_script and not summary_text:
        return "<p><em>No code review data available. Ensure code review agent completed successfully.</em></p>"

    return header + summary_html + recs_html + tables


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------

def generate_report(session_dir: str, output_path: str) -> str:
    """Generate a unified HTML report from all session data.

    Args:
        session_dir: Path to the session directory containing analysis results.
        output_path: Path where the HTML report will be written.

    Returns:
        The output path where the report was written.
    """
    data = load_session(session_dir)
    inv = data.get("inventory") or {}
    skill_name = (inv.get("frontmatter") or {}).get("name", "Unknown Skill")

    nav_links = " · ".join(
        f'<a href="#{id}" style="color:#3b82f6;text-decoration:none">{label}</a>'
        for label, id in [
            ("Summary", "summary"), ("Inventory", "inventory"),
            ("Scan", "scan-results"), ("Prompt Lint", "prompt-lint"),
            ("Prompt Review", "prompt-review"), ("Analysis", "analysis-summary"),
            ("Script I/O", "script-io"), ("Security", "security"), ("Code Review", "code-review"),
        ]
    )

    body = f"""
{_build_summary_card(data)}
{_section("📦 Skill Inventory", _build_inventory_section(data.get("inventory")), "inventory")}
{_section("🔍 Deterministic Scan", _build_scan_results_section(data.get("scan_results")), "scan-results")}
{_section("📝 Prompt Lint", _build_prompt_lint_section(data.get("prompt_lint")), "prompt-lint")}
{_section("🧠 Prompt Review", _build_prompt_review_section(data.get("prompt_review")), "prompt-review")}
{_section("📊 Analysis Summary", _build_analysis_summary_section(data, session_dir), "analysis-summary")}
{_section("⚙️ Script I/O Capture", _build_script_runs_section(data.get("script_runs") or []), "script-io")}
{_section("🔐 Security Audit", _build_security_section(data.get("security")), "security")}
{_section("📋 Code Review", _build_code_review_section(data.get("code_review")), "code-review")}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skill Tester Report — {_esc(skill_name)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; background: #f9fafb; color: #111827; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
  th {{ font-weight: 600; font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; color: #374151; }}
  details > summary {{ user-select: none; }}
  details.expand-cell > summary {{ cursor: pointer; list-style: none; }}
  details.expand-cell > summary::after {{ content: " [+]"; color: #3b82f6; font-size: .75em; }}
  details.expand-cell[open] > summary {{ display: none; }}
  details.expand-cell > .expand-full {{ white-space: pre-wrap; }}
  a {{ color: #3b82f6; }}
</style>
</head>
<body>
<header style="background:#1e1e2e;color:#cdd6f4;padding:1rem 0">
  <div style="max-width:1100px;margin:0 auto;padding:0 1rem;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:.7rem;color:#a6e3a1;text-transform:uppercase;letter-spacing:.1em">Skill Tester Report</div>
      <div style="font-size:1.3rem;font-weight:700">{_esc(skill_name)}</div>
    </div>
    <div style="font-size:.75rem;color:#6c7086">Generated {_esc(data["generated_at"][:19].replace("T", " "))} UTC</div>
  </div>
</header>
<nav style="background:#fff;border-bottom:1px solid #e5e7eb;padding:.6rem 0;font-size:.85rem;position:sticky;top:0;z-index:10">
  <div style="max-width:1100px;margin:0 auto;padding:0 1rem">{nav_links}</div>
</nav>
<div class="container">
<div id="summary">{body}</div>
</div>
</body>
</html>"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[report_gen] Report written to {output_path}", file=sys.stderr)
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Skill Tester — Report Generator")
    parser.add_argument("--session-dir", default="session", help="Session directory")
    parser.add_argument("--output", "-o", default="session/report.html")
    args = parser.parse_args()
    path = generate_report(args.session_dir, args.output)
    print(path)


if __name__ == "__main__":
    main()
