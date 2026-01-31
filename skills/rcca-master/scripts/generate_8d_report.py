#!/usr/bin/env python3
"""
8D Report Generator

Compiles final 8D report from session data in professional HTML format.

Usage:
    python generate_8d_report.py --input session.json --output report.html
    python generate_8d_report.py --sample --output sample_report.html
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import html


def escape_html(text: str) -> str:
    """Safely escape HTML special characters."""
    return html.escape(str(text)) if text else ""


def status_badge(status: str) -> str:
    """Generate HTML badge for status."""
    status_classes = {
        'Complete': 'badge-complete',
        'Verified': 'badge-verified',
        'In Progress': 'badge-progress',
        'Planned': 'badge-planned',
        'Open': 'badge-open',
    }
    cls = status_classes.get(status, 'badge-default')
    return f'<span class="badge {cls}">{escape_html(status)}</span>'


def generate_team_section(team_members: List[Dict]) -> str:
    """Generate team section HTML."""
    if not team_members:
        return "<p><em>No team members documented</em></p>"

    rows = ""
    for member in team_members:
        rows += f"""
        <tr>
            <td>{escape_html(member.get('name', ''))}</td>
            <td>{escape_html(member.get('role', ''))}</td>
            <td>{escape_html(member.get('function', ''))}</td>
        </tr>
        """
    return f"""
    <table>
        <thead>
            <tr><th>Name</th><th>Role</th><th>Function</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


def generate_containment_section(containment: List[Dict]) -> str:
    """Generate containment section HTML."""
    if not containment:
        return "<p><em>No containment actions documented</em></p>"

    rows = ""
    for action in containment:
        rows += f"""
        <tr>
            <td>{escape_html(action.get('id', ''))}</td>
            <td>{escape_html(action.get('description', ''))}</td>
            <td>{escape_html(action.get('owner', ''))}</td>
            <td>{escape_html(action.get('due_date', ''))}</td>
            <td>{status_badge(action.get('status', 'Planned'))}</td>
        </tr>
        """
    return f"""
    <table>
        <thead>
            <tr><th>#</th><th>Action</th><th>Owner</th><th>Due</th><th>Status</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


def generate_actions_section(actions: List[Dict], title: str) -> str:
    """Generate corrective/preventive actions section HTML."""
    if not actions:
        return f"<p><em>No {title.lower()} documented</em></p>"

    rows = ""
    for action in actions:
        rows += f"""
        <tr>
            <td>{escape_html(action.get('id', ''))}</td>
            <td>{escape_html(action.get('description', ''))}</td>
            <td>{escape_html(action.get('type', ''))}</td>
            <td>{escape_html(action.get('owner', ''))}</td>
            <td>{escape_html(action.get('due_date', ''))}</td>
            <td>{status_badge(action.get('status', 'Planned'))}</td>
        </tr>
        """
    return f"""
    <table>
        <thead>
            <tr><th>#</th><th>Action</th><th>Type</th><th>Owner</th><th>Due</th><th>Status</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


def generate_html_report(data: Dict) -> str:
    """Generate complete HTML report from 8D session data."""

    # Determine overall status color
    status = data.get('status', 'Open')
    if 'D8' in status or 'Closed' in status:
        status_color = "#28a745"
        status_bg = "#d4edda"
    elif 'D7' in status or 'D6' in status or 'D5' in status:
        status_color = "#17a2b8"
        status_bg = "#d1ecf1"
    elif 'D4' in status or 'D3' in status:
        status_color = "#ffc107"
        status_bg = "#fff3cd"
    else:
        status_color = "#dc3545"
        status_bg = "#f8d7da"

    # Build problem definition grid
    problem_items = [
        ("What (Object)", data.get('problem_what_object', '')),
        ("What (Defect)", data.get('problem_what_defect', '')),
        ("Where (Location)", data.get('problem_where_geographic', '')),
        ("Where (On Object)", data.get('problem_where_on_object', '')),
        ("When (Calendar)", data.get('problem_when_calendar', '')),
        ("When (Lifecycle)", data.get('problem_when_lifecycle', '')),
        ("Who (Detected by)", data.get('problem_who', '')),
        ("How (Detection)", data.get('problem_how_detected', '')),
        ("How Much (Extent)", data.get('problem_how_much', '')),
    ]

    problem_grid = ""
    for label, value in problem_items:
        if value:
            problem_grid += f"""
            <div class="problem-item">
                <label>{escape_html(label)}</label>
                <span>{escape_html(value)}</span>
            </div>
            """

    # IS/IS NOT section
    is_not_items = [
        ("What IS NOT affected", data.get('is_not_what', '')),
        ("Where IS NOT observed", data.get('is_not_where', '')),
        ("When IS NOT occurring", data.get('is_not_when', '')),
    ]
    is_not_html = ""
    for label, value in is_not_items:
        if value:
            is_not_html += f"<li><strong>{escape_html(label)}:</strong> {escape_html(value)}</li>"

    # Root causes
    root_causes = data.get('root_causes', [])
    root_causes_html = "".join(f"<li>{escape_html(rc)}</li>" for rc in root_causes) if root_causes else "<li><em>Not yet identified</em></li>"

    # Score section
    score = data.get('overall_score', 0)
    rating = data.get('rating', 'Not Scored')
    scores = data.get('scores', {})

    score_rows = ""
    for dim, val in scores.items():
        dim_name = dim.replace('_', ' ').title()
        score_rows += f"<tr><td>{dim_name}</td><td>{val}/5</td></tr>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>8D Report - {escape_html(data.get('session_id', 'Unknown'))}</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #8e44ad;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --info-color: #17a2b8;
            --light-bg: #f8f9fa;
            --border-color: #dee2e6;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            margin-bottom: 10px;
            font-size: 24px;
        }}

        .header-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            font-size: 14px;
            opacity: 0.9;
        }}

        .status-banner {{
            background: {status_bg};
            border: 2px solid {status_color};
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .status-text {{
            font-size: 18px;
            font-weight: bold;
            color: {status_color};
        }}

        .section {{
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .section h2 {{
            color: var(--primary-color);
            border-bottom: 2px solid var(--secondary-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 18px;
        }}

        .section h3 {{
            color: var(--primary-color);
            margin: 20px 0 10px 0;
            font-size: 16px;
        }}

        .d-phase {{
            display: inline-block;
            background: var(--secondary-color);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 8px;
        }}

        .problem-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .problem-item {{
            background: var(--light-bg);
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid var(--secondary-color);
        }}

        .problem-item label {{
            display: block;
            font-weight: bold;
            color: var(--primary-color);
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}

        .problem-statement {{
            background: linear-gradient(135deg, #e8f4fd, #f0e6f6);
            border: 2px solid var(--secondary-color);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            font-size: 16px;
        }}

        .problem-statement strong {{
            display: block;
            margin-bottom: 8px;
            color: var(--primary-color);
        }}

        .root-cause-box {{
            background: linear-gradient(135deg, #d4edda, #e8f4fd);
            border: 2px solid var(--success-color);
            border-radius: 8px;
            padding: 20px;
        }}

        .root-cause-box h3 {{
            color: var(--success-color);
            margin: 0 0 10px 0;
        }}

        .root-cause-box ul {{
            margin-left: 20px;
        }}

        .root-cause-box li {{
            margin-bottom: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background: var(--light-bg);
            font-weight: 600;
            color: var(--primary-color);
        }}

        tr:hover {{
            background: #f5f5f5;
        }}

        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}

        .badge-complete {{ background: #d4edda; color: #155724; }}
        .badge-verified {{ background: #28a745; color: white; }}
        .badge-progress {{ background: #fff3cd; color: #856404; }}
        .badge-planned {{ background: #e2e3e5; color: #383d41; }}
        .badge-open {{ background: #f8d7da; color: #721c24; }}
        .badge-default {{ background: #e9ecef; color: #495057; }}

        .score-box {{
            text-align: center;
            padding: 20px;
            background: var(--light-bg);
            border-radius: 8px;
        }}

        .score-value {{
            font-size: 48px;
            font-weight: bold;
            color: var(--secondary-color);
        }}

        .score-rating {{
            font-size: 20px;
            color: var(--primary-color);
        }}

        .is-not-list {{
            background: #fff3cd;
            border-radius: 6px;
            padding: 15px;
            margin-top: 15px;
        }}

        .is-not-list h4 {{
            margin: 0 0 10px 0;
            color: #856404;
        }}

        .is-not-list ul {{
            margin: 0 0 0 20px;
        }}

        .verification-result {{
            background: #d4edda;
            border: 2px solid var(--success-color);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}

        .verification-result.failed {{
            background: #f8d7da;
            border-color: var(--danger-color);
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            border-top: 1px solid var(--border-color);
            margin-top: 30px;
        }}

        @media print {{
            body {{ max-width: none; padding: 0; }}
            .section {{ break-inside: avoid; box-shadow: none; }}
            .header {{ background: var(--primary-color) !important; print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>8D Investigation Report</h1>
        <div class="header-meta">
            <span><strong>ID:</strong> {escape_html(data.get('session_id', 'N/A'))}</span>
            <span><strong>Title:</strong> {escape_html(data.get('title', 'N/A'))}</span>
            <span><strong>Created:</strong> {escape_html(data.get('created_date', 'N/A'))}</span>
            <span><strong>By:</strong> {escape_html(data.get('created_by', 'N/A'))}</span>
        </div>
    </div>

    <div class="status-banner">
        <div class="status-text">Status: {escape_html(status)}</div>
        <div>
            <strong>Domain:</strong> {escape_html(data.get('domain', 'N/A'))} |
            <strong>Severity:</strong> {escape_html(data.get('severity', 'N/A'))} |
            <strong>Complexity:</strong> {escape_html(data.get('complexity', 'N/A'))}
        </div>
    </div>

    <div class="section">
        <h2><span class="d-phase">D1</span> Team Formation</h2>
        {generate_team_section(data.get('team_members', []))}
    </div>

    <div class="section">
        <h2><span class="d-phase">D2</span> Problem Definition</h2>
        <h3>5W2H Analysis</h3>
        <div class="problem-grid">
            {problem_grid}
        </div>

        {f'''<div class="is-not-list">
            <h4>IS NOT (Investigation Boundaries)</h4>
            <ul>{is_not_html}</ul>
        </div>''' if is_not_html else ''}

        <div class="problem-statement">
            <strong>Problem Statement:</strong>
            {escape_html(data.get('problem_statement', 'Not yet defined'))}
        </div>
    </div>

    <div class="section">
        <h2><span class="d-phase">D3</span> Containment Actions</h2>
        {generate_containment_section(data.get('containment_actions', []))}
    </div>

    <div class="section">
        <h2><span class="d-phase">D4</span> Root Cause Analysis</h2>
        <p><strong>Tool Used:</strong> {escape_html(data.get('tool_selected', 'Not selected'))}</p>
        <p><strong>Verification Method:</strong> {escape_html(data.get('verification_method', 'N/A'))}</p>

        <div class="root-cause-box">
            <h3>Verified Root Cause(s)</h3>
            <ul>
                {root_causes_html}
            </ul>
        </div>
    </div>

    <div class="section">
        <h2><span class="d-phase">D5/D6</span> Corrective Actions</h2>
        {generate_actions_section(data.get('corrective_actions', []), 'Corrective Actions')}
    </div>

    <div class="section">
        <h2><span class="d-phase">D7</span> Prevention & Systemic Actions</h2>
        {generate_actions_section(data.get('systemic_actions', []), 'Systemic Actions')}

        <h3>Documents Updated</h3>
        <ul>
            {"".join(f"<li>{escape_html(doc)}</li>" for doc in data.get('documents_updated', [])) or "<li><em>None documented</em></li>"}
        </ul>

        <h3>Horizontal Deployment</h3>
        <ul>
            {"".join(f"<li>{escape_html(item)}</li>" for item in data.get('horizontal_deployment', [])) or "<li><em>None documented</em></li>"}
        </ul>
    </div>

    <div class="section">
        <h2><span class="d-phase">D8</span> Closure & Verification</h2>

        <p><strong>Verification Period:</strong>
            {escape_html(data.get('verification_period_start', ''))} to {escape_html(data.get('verification_period_end', ''))}
        </p>

        <div class="verification-result {'failed' if data.get('verification_result') == 'FAILED' else ''}">
            <h3>Verification Result</h3>
            <p style="font-size: 24px; font-weight: bold;">
                {escape_html(data.get('verification_result', 'Pending'))}
            </p>
        </div>

        <h3>Lessons Learned</h3>
        <p>{escape_html(data.get('lessons_learned', '')) or '<em>Not documented</em>'}</p>

        <p><strong>Closure Approved By:</strong> {escape_html(data.get('closure_approved_by', 'N/A'))}</p>
        <p><strong>Closure Date:</strong> {escape_html(data.get('closure_date', 'N/A'))}</p>
    </div>

    {f'''<div class="section">
        <h2>Quality Score</h2>
        <div class="score-box">
            <div class="score-value">{score:.0f}/100</div>
            <div class="score-rating">{escape_html(rating)}</div>
        </div>
        <table>
            <thead><tr><th>Dimension</th><th>Score</th></tr></thead>
            <tbody>{score_rows}</tbody>
        </table>
    </div>''' if score > 0 else ''}

    <div class="footer">
        <p>8D Report generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>RCCA Master Skill | Root Cause and Corrective Action</p>
    </div>
</body>
</html>"""

    return html_content


def create_sample_data() -> Dict:
    """Create sample 8D data for demonstration."""
    return {
        "session_id": "8D-2025-001",
        "title": "Cracked Connector Housing",
        "created_date": "2025-03-15",
        "created_by": "J. Smith",
        "status": "D8 - Closed",
        "domain": "Manufacturing/Production",
        "severity": "High",
        "urgency": "Days",
        "complexity": "Moderate",
        "team_members": [
            {"name": "J. Smith", "role": "Team Leader", "function": "Quality Engineering"},
            {"name": "M. Johnson", "role": "Facilitator", "function": "Continuous Improvement"},
            {"name": "K. Williams", "role": "SME", "function": "Production"},
            {"name": "T. Brown", "role": "SME", "function": "Process Engineering"},
        ],
        "problem_what_object": "Connector housing P/N 12345-A, Rev C",
        "problem_what_defect": "Crack at locking tab base, 2-4mm length",
        "problem_where_geographic": "Final assembly, Station 3",
        "problem_where_on_object": "Locking tab connection to housing body",
        "problem_when_calendar": "Production weeks 12-13, 2025",
        "problem_when_lifecycle": "Discovered during torque verification",
        "problem_who": "QC Inspector",
        "problem_how_detected": "Visual inspection, confirmed by microscope",
        "problem_how_much": "47 of 1,580 units (3.0%)",
        "is_not_what": "Other connector types (12345-B, C) not affected",
        "is_not_where": "Stations 1, 2 not affected",
        "is_not_when": "Weeks 1-11 not affected",
        "problem_statement": "Connector housing P/N 12345-A exhibited cracking at locking tab base (2-4mm) at final assembly Station 3 during production weeks 12-13, affecting 47 of 1,580 units (3.0%), detected by visual inspection.",
        "containment_actions": [
            {"id": "C1", "description": "Quarantine all Station 3 output from weeks 12-13", "owner": "K. Williams", "due_date": "2025-03-15", "status": "Complete"},
            {"id": "C2", "description": "100% inspection of quarantined inventory", "owner": "QC Team", "due_date": "2025-03-16", "status": "Complete"},
            {"id": "C3", "description": "Add 100% visual inspection at Station 3", "owner": "K. Williams", "due_date": "2025-03-15", "status": "Complete"},
        ],
        "tool_selected": "Fishbone → 5 Whys",
        "verification_method": "Reversal test, Prevention test, Evidence test",
        "root_causes": [
            "Work instruction change (torque sequence) was implemented without validation testing because the Management of Change (MOC) procedure did not require review for work instruction updates."
        ],
        "root_cause_verified": True,
        "corrective_actions": [
            {"id": "CA1", "description": "Revise work instruction to original torque sequence", "type": "Prevention", "owner": "T. Brown", "due_date": "2025-03-20", "status": "Complete"},
            {"id": "CA2", "description": "Update MOC procedure to include work instructions", "type": "Systemic", "owner": "M. Johnson", "due_date": "2025-04-01", "status": "Complete"},
        ],
        "systemic_actions": [
            {"id": "PA1", "description": "Audit all WI changes from past 12 months for validation gaps", "type": "Systemic", "owner": "Quality", "due_date": "2025-04-30", "status": "Complete"},
            {"id": "PA2", "description": "Add 'process validation required' flag to WI template", "type": "Systemic", "owner": "Engineering", "due_date": "2025-04-15", "status": "Complete"},
        ],
        "documents_updated": ["WI-1234 Assembly Procedure", "MOC-001 Management of Change Procedure", "FMEA-Assembly"],
        "horizontal_deployment": ["Applied MOC expansion to all production lines", "Shared lesson learned in monthly quality review"],
        "verification_period_start": "2025-03-22",
        "verification_period_end": "2025-04-22",
        "verification_result": "PASSED - 0 defects in 4,200 units produced",
        "lessons_learned": "Machine capability changes require systematic review of all associated procedures, not just the engineering change itself.",
        "closure_approved_by": "R. Davis, Plant Manager",
        "closure_date": "2025-04-25",
        "scores": {
            "problem_definition": 5,
            "team_composition": 4,
            "containment": 5,
            "root_cause_depth": 4,
            "corrective_actions": 5,
            "prevention": 4,
            "verification": 5,
        },
        "overall_score": 88,
        "rating": "Good",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate 8D HTML Report from session data"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input JSON file with 8D session data",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="8d_report.html",
        help="Output HTML file path (default: 8d_report.html)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate report with sample data",
    )

    args = parser.parse_args()

    # Get data
    if args.sample:
        data = create_sample_data()
    elif args.input:
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Provide --input file or use --sample for demo", file=sys.stderr)
        sys.exit(1)

    # Generate report
    html_content = generate_html_report(data)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(html_content, encoding='utf-8')

    print(f"\n✓ Report generated: {output_path.absolute()}")
    print(f"  Session ID: {data.get('session_id', 'N/A')}")
    print(f"  Status: {data.get('status', 'N/A')}")


if __name__ == "__main__":
    main()
