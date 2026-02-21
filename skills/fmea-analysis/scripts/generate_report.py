#!/usr/bin/env python3
"""
FMEA Report Generator

Generates professional HTML reports from FMEA data with:
- Executive summary
- Risk distribution charts
- Detailed failure mode tables
- Action tracking
- Quality scoring

Usage:
    python generate_report.py --input fmea_data.json --output report.html
    python generate_report.py --input fmea_data.json --output report.html --include-quality
"""

import html
import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


def esc(value) -> str:
    """Escape a value for safe HTML interpolation."""
    return html.escape(str(value)) if value else ""

# Import calculation functions
try:
    from calculate_fmea import (
        calculate_rpn, 
        determine_action_priority, 
        ActionPriority,
        generate_risk_summary
    )
except ImportError:
    # Standalone mode - define minimal functions
    def calculate_rpn(s, o, d):
        return s * o * d
    
    def determine_action_priority(s, o, d, fmea_type="DFMEA"):
        if s >= 9:
            return "H"
        elif s >= 7 and (o >= 5 or d >= 7):
            return "H"
        elif s >= 7 or (o >= 5 and d >= 5):
            return "M"
        else:
            return "L"


def get_ap_color(ap: str) -> str:
    """Get CSS color for Action Priority."""
    colors = {
        "H": "#dc3545",  # Red
        "M": "#ffc107",  # Yellow
        "L": "#28a745",  # Green
    }
    return colors.get(ap, "#6c757d")


def get_severity_color(severity: int) -> str:
    """Get CSS color for severity level."""
    if severity >= 9:
        return "#dc3545"  # Red
    elif severity >= 7:
        return "#fd7e14"  # Orange
    elif severity >= 5:
        return "#ffc107"  # Yellow
    else:
        return "#28a745"  # Green


def generate_html_report(fmea_data: Dict, include_quality: bool = False) -> str:
    """Generate complete HTML report from FMEA data."""
    
    # Extract and escape data for safe HTML output
    title = esc(fmea_data.get("title", "FMEA Report"))
    fmea_type = esc(fmea_data.get("fmea_type", "FMEA"))
    project = esc(fmea_data.get("project", ""))
    prepared_by = esc(fmea_data.get("prepared_by", ""))
    date = esc(fmea_data.get("date", datetime.now().strftime("%Y-%m-%d")))
    revision = esc(fmea_data.get("revision", "1.0"))
    scope = esc(fmea_data.get("scope", ""))
    failure_modes = fmea_data.get("failure_modes", [])
    
    # Calculate statistics
    total_items = len(failure_modes)
    ap_counts = {"H": 0, "M": 0, "L": 0}
    safety_critical = 0
    rpn_values = []
    items_with_actions = 0
    actions_complete = 0
    
    for fm in failure_modes:
        s = fm.get("severity", 1)
        o = fm.get("occurrence", 1)
        d = fm.get("detection", 1)
        
        rpn = calculate_rpn(s, o, d)
        rpn_values.append(rpn)
        
        ap = determine_action_priority(s, o, d, fmea_type)
        if hasattr(ap, 'value'):
            ap = ap.value
        ap_counts[ap] = ap_counts.get(ap, 0) + 1
        
        if s >= 9:
            safety_critical += 1
        
        if fm.get("recommended_action"):
            items_with_actions += 1
            if fm.get("action_taken"):
                actions_complete += 1
    
    avg_rpn = sum(rpn_values) / len(rpn_values) if rpn_values else 0
    max_rpn = max(rpn_values) if rpn_values else 0
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
            font-size: 0.95em;
        }}
        
        .header-meta-item {{
            background: rgba(255,255,255,0.1);
            padding: 10px 15px;
            border-radius: 5px;
        }}
        
        .header-meta-item strong {{
            display: block;
            font-size: 0.8em;
            opacity: 0.8;
            margin-bottom: 3px;
        }}
        
        .section {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #1a1a2e;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        
        .summary-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #0066cc;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        
        .ap-distribution {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        
        .ap-badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px 25px;
            border-radius: 50px;
            font-weight: bold;
            color: white;
        }}
        
        .ap-badge.high {{ background: #dc3545; }}
        .ap-badge.medium {{ background: #ffc107; color: #333; }}
        .ap-badge.low {{ background: #28a745; }}
        
        .ap-badge .count {{
            font-size: 1.8em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }}
        
        th, td {{
            padding: 12px 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background: #1a1a2e;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .rating-cell {{
            text-align: center;
            font-weight: bold;
        }}
        
        .severity-high {{ color: #dc3545; }}
        .severity-med {{ color: #fd7e14; }}
        .severity-low {{ color: #28a745; }}
        
        .ap-indicator {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        
        .ap-H {{ background: #dc3545; color: white; }}
        .ap-M {{ background: #ffc107; color: #333; }}
        .ap-L {{ background: #28a745; color: white; }}
        
        .action-status {{
            font-size: 0.85em;
            padding: 3px 8px;
            border-radius: 4px;
        }}
        
        .status-complete {{ background: #d4edda; color: #155724; }}
        .status-pending {{ background: #fff3cd; color: #856404; }}
        .status-none {{ background: #f8d7da; color: #721c24; }}
        
        .progress-bar {{
            width: 100%;
            height: 25px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-bar-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
            transition: width 0.5s;
        }}
        
        .chart-container {{
            display: flex;
            justify-content: center;
            gap: 50px;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        
        .pie-chart {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            position: relative;
        }}
        
        .chart-legend {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            justify-content: center;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{ background: white; }}
            .section {{ box-shadow: none; border: 1px solid #ddd; }}
            .header {{ background: #1a1a2e; print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>{fmea_type} Analysis Report</p>
            <div class="header-meta">
                <div class="header-meta-item">
                    <strong>Project</strong>
                    {project or "N/A"}
                </div>
                <div class="header-meta-item">
                    <strong>Prepared By</strong>
                    {prepared_by or "N/A"}
                </div>
                <div class="header-meta-item">
                    <strong>Date</strong>
                    {date}
                </div>
                <div class="header-meta-item">
                    <strong>Revision</strong>
                    {revision}
                </div>
            </div>
        </div>
        
        {f'<div class="section"><h2>Scope</h2><p>{scope}</p></div>' if scope else ''}
        
        <div class="section">
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">{total_items}</div>
                    <div class="label">Total Failure Modes</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: #dc3545;">{safety_critical}</div>
                    <div class="label">Safety Critical (S≥9)</div>
                </div>
                <div class="summary-card">
                    <div class="value">{avg_rpn:.0f}</div>
                    <div class="label">Average RPN</div>
                </div>
                <div class="summary-card">
                    <div class="value">{max_rpn}</div>
                    <div class="label">Maximum RPN</div>
                </div>
            </div>
            
            <h3 style="margin-top: 30px; margin-bottom: 15px;">Action Priority Distribution</h3>
            <div class="ap-distribution">
                <div class="ap-badge high">
                    <span>High (H)</span>
                    <span class="count">{ap_counts.get('H', 0)}</span>
                </div>
                <div class="ap-badge medium">
                    <span>Medium (M)</span>
                    <span class="count">{ap_counts.get('M', 0)}</span>
                </div>
                <div class="ap-badge low">
                    <span>Low (L)</span>
                    <span class="count">{ap_counts.get('L', 0)}</span>
                </div>
            </div>
            
            <h3 style="margin-top: 30px; margin-bottom: 15px;">Action Completion Progress</h3>
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: {(actions_complete/items_with_actions*100) if items_with_actions > 0 else 0:.0f}%; background: #28a745;">
                    {actions_complete}/{items_with_actions} Actions Complete ({(actions_complete/items_with_actions*100) if items_with_actions > 0 else 0:.0f}%)
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Failure Mode Analysis</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Function</th>
                            <th>Failure Mode</th>
                            <th>Effect</th>
                            <th>Cause</th>
                            <th>S</th>
                            <th>O</th>
                            <th>D</th>
                            <th>RPN</th>
                            <th>AP</th>
                            <th>Action Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # Add failure mode rows
    for fm in failure_modes:
        fm_id = esc(fm.get("id", ""))
        raw_function = fm.get("function", "")
        raw_failure_mode = fm.get("failure_mode", "")
        raw_effect = fm.get("effect", "")
        raw_cause = fm.get("cause", "")
        function = esc(raw_function[:50] + "..." if len(raw_function) > 50 else raw_function)
        failure_mode = esc(raw_failure_mode[:40] + "..." if len(raw_failure_mode) > 40 else raw_failure_mode)
        effect = esc(raw_effect[:40] + "..." if len(raw_effect) > 40 else raw_effect)
        cause = esc(raw_cause[:40] + "..." if len(raw_cause) > 40 else raw_cause)
        function_full = esc(raw_function)
        failure_mode_full = esc(raw_failure_mode)
        effect_full = esc(raw_effect)
        cause_full = esc(raw_cause)
        
        s = fm.get("severity", 1)
        o = fm.get("occurrence", 1)
        d = fm.get("detection", 1)
        rpn = calculate_rpn(s, o, d)
        
        ap = determine_action_priority(s, o, d, fmea_type)
        if hasattr(ap, 'value'):
            ap = ap.value
        
        # Severity color class
        if s >= 9:
            s_class = "severity-high"
        elif s >= 7:
            s_class = "severity-med"
        else:
            s_class = "severity-low"
        
        # Action status
        if fm.get("action_taken"):
            status_class = "status-complete"
            status_text = "Complete"
        elif fm.get("recommended_action"):
            status_class = "status-pending"
            status_text = "Pending"
        else:
            status_class = "status-none"
            status_text = "No Action"
        
        html += f"""
                        <tr>
                            <td>{fm_id}</td>
                            <td title="{function_full}">{function}</td>
                            <td title="{failure_mode_full}">{failure_mode}</td>
                            <td title="{effect_full}">{effect}</td>
                            <td title="{cause_full}">{cause}</td>
                            <td class="rating-cell {s_class}">{s}</td>
                            <td class="rating-cell">{o}</td>
                            <td class="rating-cell">{d}</td>
                            <td class="rating-cell">{rpn}</td>
                            <td><span class="ap-indicator ap-{ap}">{ap}</span></td>
                            <td><span class="action-status {status_class}">{status_text}</span></td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
"""
    
    # Add actions section if there are any actions
    actions = [fm for fm in failure_modes if fm.get("recommended_action")]
    if actions:
        html += """
        <div class="section">
            <h2>Action Tracking</h2>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Failure Mode</th>
                            <th>AP</th>
                            <th>Recommended Action</th>
                            <th>Owner</th>
                            <th>Target Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for fm in actions:
            fm_id = esc(fm.get("id", ""))
            raw_fm = fm.get("failure_mode", "")
            failure_mode = esc(raw_fm[:30] + "..." if len(raw_fm) > 30 else raw_fm)

            s = fm.get("severity", 1)
            o = fm.get("occurrence", 1)
            d = fm.get("detection", 1)
            ap = determine_action_priority(s, o, d, fmea_type)
            if hasattr(ap, 'value'):
                ap = ap.value

            action = esc(fm.get("recommended_action", ""))
            owner = esc(fm.get("action_owner", "TBD"))
            target = esc(fm.get("target_date", "TBD"))

            if fm.get("action_taken"):
                status_class = "status-complete"
                status_text = "Complete"
            else:
                status_class = "status-pending"
                status_text = "Open"

            html += f"""
                        <tr>
                            <td>{fm_id}</td>
                            <td>{failure_mode}</td>
                            <td><span class="ap-indicator ap-{ap}">{ap}</span></td>
                            <td>{action}</td>
                            <td>{owner}</td>
                            <td>{target}</td>
                            <td><span class="action-status {status_class}">{status_text}</span></td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
"""
    
    # Close HTML
    html += f"""
        <div class="footer">
            <p>Generated by FMEA Analysis Skill | {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            <p>Based on AIAG-VDA FMEA Methodology</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def _validate_path(filepath: str, allowed_extensions: set, label: str) -> None:
    """Validate file path: reject traversal and restrict extensions."""
    if ".." in filepath:
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = Path(filepath).suffix.lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got '{ext}'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="FMEA Report Generator")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with FMEA data")
    parser.add_argument("--output", "-o", required=True, help="Output HTML file")
    parser.add_argument("--include-quality", action="store_true",
                        help="Include quality assessment section")

    args = parser.parse_args()

    _validate_path(args.input, {".json"}, "input file")
    _validate_path(args.output, {".html", ".htm"}, "output file")

    # Load data
    try:
        with open(args.input, 'r') as f:
            fmea_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        sys.exit(1)
    
    # Generate report
    html = generate_html_report(fmea_data, args.include_quality)
    
    # Write output
    with open(args.output, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
