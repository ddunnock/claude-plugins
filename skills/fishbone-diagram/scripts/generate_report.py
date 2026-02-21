#!/usr/bin/env python3
"""
Fishbone Diagram HTML Report Generator

Creates comprehensive HTML reports with embedded SVG diagrams.

Usage:
  python generate_report.py --file analysis.json --output report.html
  python generate_report.py --sample --output sample_report.html
"""

import os
import argparse
import json
import sys
from datetime import datetime

# Import diagram generator
from generate_diagram import generate_svg, generate_sample_data as generate_sample_diagram_data
from pathlib import Path


def generate_sample_data():
    """Generate complete sample data for report."""
    diagram_data = generate_sample_diagram_data()
    
    return {
        **diagram_data,
        "analysis_id": f"FB-{datetime.now().strftime('%Y-%m%d')}-001",
        "scores": {
            "problem_clarity": 4,
            "category_coverage": 4,
            "cause_depth": 4,
            "cause_quality": 5,
            "prioritization": 4,
            "documentation": 5
        },
        "prioritized_causes": [
            {
                "rank": 1,
                "cause": "CNC spindle wear",
                "category": "Machine",
                "votes": 8,
                "verification_method": "Vibration analysis and hour log review",
                "owner": "Maintenance",
                "status": "In Progress"
            },
            {
                "rank": 2,
                "cause": "Operator training incomplete",
                "category": "Man",
                "votes": 6,
                "verification_method": "Training records audit",
                "owner": "HR/Training",
                "status": "Pending"
            },
            {
                "rank": 3,
                "cause": "Tool offset verification skipped",
                "category": "Method",
                "votes": 5,
                "verification_method": "Process observation and checklist review",
                "owner": "Quality",
                "status": "Pending"
            }
        ],
        "next_steps": [
            "Schedule spindle rebuild within 2 weeks",
            "Complete operator training modules (2 of 4 remaining)",
            "Reinstate mandatory tool offset verification",
            "Conduct 5 Whys on top prioritized cause"
        ],
        "participants": ["John Smith (Quality)", "Jane Doe (Engineering)", "Bob Wilson (Maintenance)", "Alice Chen (Operations)"],
        "session_date": datetime.now().strftime("%Y-%m-%d"),
        "facilitator": "Quality Engineering Team"
    }


def calculate_score(scores):
    """Calculate weighted quality score."""
    weights = {
        "problem_clarity": 0.15,
        "category_coverage": 0.20,
        "cause_depth": 0.25,
        "cause_quality": 0.20,
        "prioritization": 0.10,
        "documentation": 0.10
    }
    
    weighted_sum = sum(scores.get(k, 3) * w for k, w in weights.items())
    return round(weighted_sum * 20, 1)


def get_rating(score):
    """Convert score to rating."""
    if score >= 85:
        return ("Excellent", "#27ae60")
    elif score >= 70:
        return ("Good", "#3498db")
    elif score >= 50:
        return ("Fair", "#f39c12")
    else:
        return ("Poor", "#e74c3c")


def escape_html(text):
    """Escape HTML special characters."""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def generate_html_report(data):
    """Generate complete HTML report."""
    
    # Calculate scores
    scores = data.get("scores", {
        "problem_clarity": 3,
        "category_coverage": 3,
        "cause_depth": 3,
        "cause_quality": 3,
        "prioritization": 3,
        "documentation": 3
    })
    final_score = calculate_score(scores)
    rating, rating_color = get_rating(final_score)
    
    # Generate SVG diagram
    svg_diagram = generate_svg(data, width=1100, height=700)
    # Remove XML declaration for embedding
    svg_diagram = svg_diagram.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')
    
    # Metadata
    metadata = data.get("metadata", {})
    analysis_id = data.get("analysis_id", f"FB-{datetime.now().strftime('%Y%m%d')}")
    problem = data.get("problem", "Problem statement not provided")
    session_date = data.get("session_date", datetime.now().strftime("%Y-%m-%d"))
    facilitator = data.get("facilitator", "Not specified")
    participants = data.get("participants", [])
    
    # Categories summary
    categories = data.get("categories", [])
    total_causes = sum(len(c.get("causes", [])) for c in categories)
    total_subcauses = sum(
        sum(len(cause.get("subcauses", [])) for cause in c.get("causes", []))
        for c in categories
    )
    
    # Prioritized causes
    prioritized = data.get("prioritized_causes", [])
    
    # Next steps
    next_steps = data.get("next_steps", [])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fishbone Analysis Report - {escape_html(analysis_id)}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .report {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px 40px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header-meta {{
            display: flex;
            gap: 30px;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .score-banner {{
            background: {rating_color};
            color: white;
            padding: 15px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .score-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        
        .score-rating {{
            font-size: 18px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
        
        .problem-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 0 4px 4px 0;
            font-size: 16px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        
        .diagram-container {{
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .diagram-container svg {{
            max-width: 100%;
            height: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .status-pending {{
            background: #ffeaa7;
            color: #6c5ce7;
        }}
        
        .status-in-progress {{
            background: #81ecec;
            color: #00b894;
        }}
        
        .status-complete {{
            background: #55efc4;
            color: #00b894;
        }}
        
        .score-breakdown {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .score-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        
        .score-bar {{
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .score-fill {{
            height: 100%;
            background: #3498db;
            border-radius: 4px;
        }}
        
        .next-steps {{
            list-style: none;
        }}
        
        .next-steps li {{
            padding: 12px 15px;
            background: #f8f9fa;
            margin-bottom: 8px;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }}
        
        .participants {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .participant {{
            background: #e8f4fd;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 13px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .report {{
                box-shadow: none;
            }}
            .diagram-container {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="report">
        <div class="header">
            <h1>Fishbone (Ishikawa) Analysis Report</h1>
            <div class="header-meta">
                <span><strong>ID:</strong> {escape_html(analysis_id)}</span>
                <span><strong>Date:</strong> {escape_html(session_date)}</span>
                <span><strong>Facilitator:</strong> {escape_html(facilitator)}</span>
            </div>
        </div>
        
        <div class="score-banner">
            <div>
                <div class="score-rating">{rating}</div>
                <div>Quality Score</div>
            </div>
            <div class="score-value">{final_score}/100</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Problem Statement</h2>
                <div class="problem-box">
                    {escape_html(problem)}
                </div>
            </div>
            
            <div class="section">
                <h2>Analysis Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(categories)}</div>
                        <div class="stat-label">Categories</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_causes}</div>
                        <div class="stat-label">Causes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_subcauses}</div>
                        <div class="stat-label">Sub-causes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(prioritized)}</div>
                        <div class="stat-label">Prioritized</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Fishbone Diagram</h2>
                <div class="diagram-container">
                    {svg_diagram}
                </div>
            </div>
'''
    
    # Categories breakdown
    html += '''
            <div class="section">
                <h2>Categories Breakdown</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Causes</th>
                            <th>Sub-causes</th>
                            <th>Key Causes</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    for cat in categories:
        causes = cat.get("causes", [])
        subcause_count = sum(len(c.get("subcauses", [])) for c in causes)
        key_causes = ", ".join([c.get("text", "")[:30] for c in causes[:3]])
        if len(causes) > 3:
            key_causes += f" (+{len(causes)-3} more)"
        
        html += f'''
                        <tr>
                            <td><strong>{escape_html(cat.get("name", ""))}</strong></td>
                            <td>{len(causes)}</td>
                            <td>{subcause_count}</td>
                            <td>{escape_html(key_causes)}</td>
                        </tr>
'''
    
    html += '''
                    </tbody>
                </table>
            </div>
'''
    
    # Prioritized causes
    if prioritized:
        html += '''
            <div class="section">
                <h2>Prioritized Causes</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Cause</th>
                            <th>Category</th>
                            <th>Votes</th>
                            <th>Owner</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
'''
        
        for cause in prioritized:
            status = cause.get("status", "Pending")
            status_class = "status-" + status.lower().replace(" ", "-")
            
            html += f'''
                        <tr>
                            <td><strong>#{cause.get("rank", "")}</strong></td>
                            <td>{escape_html(cause.get("cause", ""))}</td>
                            <td>{escape_html(cause.get("category", ""))}</td>
                            <td>{cause.get("votes", "")}</td>
                            <td>{escape_html(cause.get("owner", ""))}</td>
                            <td><span class="status-badge {status_class}">{escape_html(status)}</span></td>
                        </tr>
'''
        
        html += '''
                    </tbody>
                </table>
            </div>
'''
    
    # Quality scores
    html += '''
            <div class="section">
                <h2>Quality Score Breakdown</h2>
                <div class="score-breakdown">
'''
    
    dimension_names = {
        "problem_clarity": "Problem Clarity (15%)",
        "category_coverage": "Category Coverage (20%)",
        "cause_depth": "Cause Depth (25%)",
        "cause_quality": "Cause Quality (20%)",
        "prioritization": "Prioritization (10%)",
        "documentation": "Documentation (10%)"
    }
    
    for key, name in dimension_names.items():
        score = scores.get(key, 3)
        pct = score * 20
        html += f'''
                    <div class="score-item">
                        <div style="flex: 1;">
                            <div>{name}</div>
                            <div class="score-bar">
                                <div class="score-fill" style="width: {pct}%;"></div>
                            </div>
                        </div>
                        <div style="margin-left: 15px; font-weight: bold;">{score}/5</div>
                    </div>
'''
    
    html += '''
                </div>
            </div>
'''
    
    # Next steps
    if next_steps:
        html += '''
            <div class="section">
                <h2>Next Steps</h2>
                <ul class="next-steps">
'''
        for step in next_steps:
            html += f'                    <li>{escape_html(step)}</li>\n'
        
        html += '''
                </ul>
            </div>
'''
    
    # Participants
    if participants:
        html += '''
            <div class="section">
                <h2>Session Participants</h2>
                <div class="participants">
'''
        for p in participants:
            html += f'                    <span class="participant">{escape_html(p)}</span>\n'
        
        html += '''
                </div>
            </div>
'''
    
    # Footer
    html += f'''
        </div>
        
        <div class="footer">
            Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")} | Fishbone Diagram Analysis Skill
        </div>
    </div>
</body>
</html>
'''
    
    return html




def _validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    resolved = os.path.realpath(filepath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)
    return resolved


def main():
    parser = argparse.ArgumentParser(
        description="Generate Fishbone Diagram HTML Report"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with analysis data"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="JSON string with analysis data"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate report with sample data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="fishbone_report.html",
        help="Output HTML file path (default: fishbone_report.html)"
    )
    
    args = parser.parse_args()

    if args.file:
        args.file = _validate_path(args.file, {'.json'}, "input file")
    args.output = _validate_path(args.output, {'.htm', '.html'}, "output file")
    
    # Get data from appropriate source
    if args.sample:
        data = generate_sample_data()
    elif args.json:
        try:
            data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Must provide --file, --json, or --sample", file=sys.stderr)
        sys.exit(1)
    
    # Generate HTML report
    html_content = generate_html_report(data)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Calculate score for output
    scores = data.get("scores", {})
    final_score = calculate_score(scores) if scores else "N/A"
    
    print(f"✓ Fishbone report generated: {args.output}")
    print(f"  Analysis ID: {data.get('analysis_id', 'N/A')}")
    print(f"  Score: {final_score}/100")


if __name__ == "__main__":
    main()
