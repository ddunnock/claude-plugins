#!/usr/bin/env python3
"""
report_gen.py — Generate a unified HTML analysis report from a skill-tester session.

Usage:
  python scripts/report_gen.py --session-dir session/ --output session/report.html
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> Optional[Any]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
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
    base = Path(session_dir)
    return {
        "inventory": _load_json(base / "inventory.json"),
        "scan_results": _load_json(base / "scan_results.json"),
        "api_calls": _load_jsonl(base / "api_log.jsonl"),
        "script_runs": _load_jsonl(base / "script_runs.jsonl"),
        "security": _load_json(base / "security_report.json"),
        "code_review": _load_json(base / "code_review.json"),
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

    table = _table(["Script", "Lines", "Calls API", "Dangerous Calls", "Potential Secrets"], rows) if rows else "<p><em>No scripts found.</em></p>"

    refs = inv.get("references") or []
    ref_list = "".join(f"<li><code>{_esc(r)}</code></li>" for r in refs) or "<li><em>None</em></li>"

    return f"""
<div style="display:grid;grid-template-columns:1fr 200px;gap:1.5rem">
  <div>{table}</div>
  <div>
    <strong style="font-size:.85rem">References</strong>
    <ul style="font-size:.8rem;margin-top:.5rem">{ref_list}</ul>
  </div>
</div>"""


def _build_api_trace_section(api_calls: list) -> str:
    if not api_calls:
        return "<p><em>No API calls recorded. Either no scripts call the Anthropic API, or capture was not enabled.</em></p>"

    total_in = sum((c.get("response") or {}).get("usage", {}).get("input_tokens", 0) or 0 for c in api_calls)
    total_out = sum((c.get("response") or {}).get("usage", {}).get("output_tokens", 0) or 0 for c in api_calls)
    avg_latency = int(sum(c.get("latency_ms", 0) for c in api_calls) / len(api_calls))

    meta = f"""<div style="display:flex;gap:2rem;margin-bottom:1rem;font-size:.875rem">
  <span>📨 <strong>{len(api_calls)}</strong> calls</span>
  <span>⬆ <strong>{total_in:,}</strong> input tokens</span>
  <span>⬇ <strong>{total_out:,}</strong> output tokens</span>
  <span>⏱ avg <strong>{avg_latency}ms</strong></span>
</div>"""

    rows = []
    for c in api_calls:
        req = c.get("request") or {}
        resp = c.get("response") or {}
        usage = resp.get("usage") or {}
        err = c.get("error")
        status = _badge("ERROR", SEVERITY_COLORS["CRITICAL"]) if err else _badge("OK", "#16a34a")
        rows.append([
            f'<code>{_esc(c.get("call_id", "?"))}</code>',
            _esc(req.get("model", "?")),
            str(usage.get("input_tokens", "?")),
            str(usage.get("output_tokens", "?")),
            f'{c.get("latency_ms", "?")}ms',
            status,
        ])

    table = _table(["Call ID", "Model", "In Tokens", "Out Tokens", "Latency", "Status"], rows)

    # Detail accordion-style (simplified as collapsible details)
    details = ""
    for c in api_calls[:10]:  # cap at 10 for readability
        req = c.get("request") or {}
        resp = c.get("response") or {}
        details += f"""<details style="margin:.5rem 0;border:1px solid #e5e7eb;border-radius:6px">
<summary style="padding:.5rem .75rem;cursor:pointer;font-size:.85rem">
  <code>{_esc(c.get("call_id", "?"))}</code> — {_esc(req.get("model", "?"))} — {c.get("latency_ms", "?")}ms
</summary>
<div style="padding:.75rem;display:grid;grid-template-columns:1fr 1fr;gap:1rem;font-size:.8rem">
  <div><strong>Request (system)</strong>{_code((req.get("system") or "")[:500], 15)}</div>
  <div><strong>Response</strong>{_code(json.dumps(resp, indent=2)[:800], 20)}</div>
</div>
</details>"""

    return meta + table + "<h3 style='font-size:.9rem;margin-top:1.5rem;margin-bottom:.5rem'>Call Details (first 10)</h3>" + details


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
            _esc(f.get("message", "")[:120]),
        ])

    return header + _table(["Severity", "Script", "Line", "Check", "Message"], rows)


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
            _esc(f.get("description", "")[:120]),
        ])

    return _table(["Severity", "Script", "Line", "Category", "Description"], rows)


def _build_code_review_section(cr: Optional[dict]) -> str:
    if not cr:
        return "<p><em>No code review report. Run audit mode to generate.</em></p>"

    score = cr.get("overall_score", "N/A")
    color = _score_color(float(score)) if isinstance(score, (int, float)) else "#6b7280"

    header = f'<div style="font-size:2rem;font-weight:700;color:{color};margin-bottom:1rem">{score}/10</div>'

    per_script = cr.get("scripts") or []
    tables = ""
    for s in per_script:
        issues = s.get("issues") or []
        rows = [[
            _esc(i.get("category", "?")),
            _esc(i.get("description", "")[:150]),
            _esc(i.get("suggestion", "")[:150]),
        ] for i in issues]
        t = _table(["Category", "Issue", "Suggestion"], rows) if rows else "<p><em>No issues.</em></p>"
        tables += f"<h3 style='font-size:.9rem;margin:.75rem 0 .25rem'><code>{_esc(s.get('script', '?'))}</code> — score: <strong>{s.get('score', '?')}</strong>/10</h3>{t}"

    return header + tables


# ---------------------------------------------------------------------------
# Main report builder
# ---------------------------------------------------------------------------

def generate_report(session_dir: str, output_path: str):
    data = load_session(session_dir)
    inv = data.get("inventory") or {}
    skill_name = (inv.get("frontmatter") or {}).get("name", "Unknown Skill")

    nav_links = " · ".join(
        f'<a href="#{id}" style="color:#3b82f6;text-decoration:none">{label}</a>'
        for label, id in [
            ("Summary", "summary"), ("Inventory", "inventory"),
            ("Scan", "scan-results"), ("API Trace", "api-trace"),
            ("Script I/O", "script-io"), ("Security", "security"), ("Code Review", "code-review"),
        ]
    )

    body = f"""
{_build_summary_card(data)}
{_section("📦 Skill Inventory", _build_inventory_section(data.get("inventory")), "inventory")}
{_section("🔍 Deterministic Scan", _build_scan_results_section(data.get("scan_results")), "scan-results")}
{_section("🔌 API Call Trace", _build_api_trace_section(data.get("api_calls") or []), "api-trace")}
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
