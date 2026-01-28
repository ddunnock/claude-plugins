#!/usr/bin/env python3
"""
5 Whys Analysis Report Generator

Generates professional HTML reports for 5 Whys root cause analyses.

Usage:
    python generate_report.py --json analysis_data.json --output report.html
    python generate_report.py --interactive --output report.html
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
import html


@dataclass
class WhyStep:
    """Single step in the 5 Whys chain."""
    level: int
    question: str
    answer: str
    evidence: str
    evidence_type: str  # "data", "document", "observation", "inference"
    is_branch: bool = False
    branch_id: str = ""


@dataclass
class Countermeasure:
    """Single countermeasure action."""
    action: str
    owner: str
    due_date: str
    success_criteria: str
    status: str = "Planned"  # "Planned", "In Progress", "Complete", "Verified"


@dataclass
class VerificationTest:
    """Root cause verification test result."""
    test_name: str
    passed: bool
    notes: str


@dataclass
class AnalysisData:
    """Complete 5 Whys analysis data structure."""
    # Metadata
    analysis_id: str
    analysis_date: str
    analyst: str
    team_members: List[str]
    
    # Problem Definition
    problem_what: str
    problem_where: str
    problem_when: str
    problem_extent: str
    problem_expected: str
    problem_actual: str
    problem_statement: str
    
    # Analysis
    why_steps: List[WhyStep]
    root_causes: List[str]
    
    # Verification
    verification_tests: List[VerificationTest]
    
    # Countermeasures
    countermeasures: List[Countermeasure]
    
    # Scoring
    scores: Dict[str, int] = field(default_factory=dict)
    overall_score: float = 0.0
    rating: str = ""
    
    # Additional notes
    lessons_learned: str = ""
    related_analyses: List[str] = field(default_factory=list)


def escape_html(text: str) -> str:
    """Safely escape HTML special characters."""
    return html.escape(str(text)) if text else ""


def generate_html_report(data: AnalysisData) -> str:
    """Generate complete HTML report from analysis data."""
    
    # Calculate score color
    if data.overall_score >= 90:
        score_color = "#28a745"  # Green
        score_bg = "#d4edda"
    elif data.overall_score >= 80:
        score_color = "#5cb85c"  # Light green
        score_bg = "#dff0d8"
    elif data.overall_score >= 70:
        score_color = "#f0ad4e"  # Yellow/Orange
        score_bg = "#fcf8e3"
    elif data.overall_score >= 60:
        score_color = "#d9534f"  # Red
        score_bg = "#f2dede"
    else:
        score_color = "#a94442"  # Dark red
        score_bg = "#ebcccc"
    
    # Generate why chain HTML
    why_chain_html = ""
    for step in data.why_steps:
        evidence_badge = {
            "data": '<span class="badge badge-data">Data</span>',
            "document": '<span class="badge badge-doc">Document</span>',
            "observation": '<span class="badge badge-obs">Observation</span>',
            "inference": '<span class="badge badge-inf">Inference</span>',
        }.get(step.evidence_type, "")
        
        branch_class = " branch" if step.is_branch else ""
        why_chain_html += f"""
        <div class="why-step{branch_class}">
            <div class="why-level">Why {step.level}{f" ({step.branch_id})" if step.branch_id else ""}</div>
            <div class="why-question"><strong>Q:</strong> {escape_html(step.question)}</div>
            <div class="why-answer"><strong>A:</strong> {escape_html(step.answer)}</div>
            <div class="why-evidence">{evidence_badge} <em>Evidence:</em> {escape_html(step.evidence)}</div>
        </div>
        """
    
    # Generate verification tests HTML
    verification_html = ""
    for test in data.verification_tests:
        status_class = "pass" if test.passed else "fail"
        status_icon = "✓" if test.passed else "✗"
        verification_html += f"""
        <tr class="{status_class}">
            <td>{escape_html(test.test_name)}</td>
            <td class="status-{status_class}">{status_icon} {"PASS" if test.passed else "FAIL"}</td>
            <td>{escape_html(test.notes)}</td>
        </tr>
        """
    
    # Generate countermeasures HTML
    countermeasures_html = ""
    for cm in data.countermeasures:
        status_class = cm.status.lower().replace(" ", "-")
        countermeasures_html += f"""
        <tr>
            <td>{escape_html(cm.action)}</td>
            <td>{escape_html(cm.owner)}</td>
            <td>{escape_html(cm.due_date)}</td>
            <td>{escape_html(cm.success_criteria)}</td>
            <td class="status-{status_class}">{escape_html(cm.status)}</td>
        </tr>
        """
    
    # Generate score breakdown HTML
    score_breakdown_html = ""
    weight_map = {
        "problem_definition": ("Problem Definition", 15),
        "causal_chain_logic": ("Causal Chain Logic", 25),
        "evidence_basis": ("Evidence Basis", 20),
        "root_cause_depth": ("Root Cause Depth", 20),
        "actionability": ("Actionability", 10),
        "countermeasures": ("Countermeasures", 10),
    }
    for key, (name, weight) in weight_map.items():
        score = data.scores.get(key, 0)
        weighted = score * weight / 100 * 20
        score_breakdown_html += f"""
        <tr>
            <td>{name}</td>
            <td>{score}/5</td>
            <td>{weight}%</td>
            <td>{weighted:.1f}</td>
        </tr>
        """
    
    # Root causes list
    root_causes_html = "\n".join(f"<li>{escape_html(rc)}</li>" for rc in data.root_causes)
    
    # Team members list
    team_html = ", ".join(escape_html(m) for m in data.team_members) if data.team_members else "N/A"
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>5 Whys Analysis Report - {escape_html(data.analysis_id)}</title>
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #28a745;
            --warning-color: #f0ad4e;
            --danger-color: #d9534f;
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
            background-color: #fff;
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
            font-size: 28px;
        }}
        
        .header-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            font-size: 14px;
            opacity: 0.9;
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
            font-size: 20px;
        }}
        
        .score-banner {{
            background: {score_bg};
            border: 2px solid {score_color};
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin-bottom: 25px;
        }}
        
        .score-value {{
            font-size: 48px;
            font-weight: bold;
            color: {score_color};
        }}
        
        .score-rating {{
            font-size: 24px;
            color: {score_color};
            margin-top: 5px;
        }}
        
        .problem-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .problem-item {{
            background: var(--light-bg);
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid var(--secondary-color);
        }}
        
        .problem-item label {{
            font-weight: bold;
            color: var(--primary-color);
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        .problem-statement {{
            background: var(--light-bg);
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
            border-left: 4px solid var(--primary-color);
            font-size: 16px;
        }}
        
        .why-chain {{
            position: relative;
            padding-left: 30px;
        }}
        
        .why-chain::before {{
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, var(--secondary-color), var(--primary-color));
            border-radius: 2px;
        }}
        
        .why-step {{
            position: relative;
            background: var(--light-bg);
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 15px;
            border: 1px solid var(--border-color);
        }}
        
        .why-step::before {{
            content: '';
            position: absolute;
            left: -24px;
            top: 20px;
            width: 12px;
            height: 12px;
            background: var(--secondary-color);
            border-radius: 50%;
            border: 2px solid white;
        }}
        
        .why-step.branch {{
            margin-left: 30px;
            border-left: 3px solid var(--warning-color);
        }}
        
        .why-level {{
            font-weight: bold;
            color: var(--secondary-color);
            margin-bottom: 8px;
        }}
        
        .why-question {{
            margin-bottom: 5px;
        }}
        
        .why-answer {{
            margin-bottom: 8px;
            color: #2c3e50;
        }}
        
        .why-evidence {{
            font-size: 13px;
            color: #666;
            padding-top: 8px;
            border-top: 1px dashed var(--border-color);
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 5px;
        }}
        
        .badge-data {{ background: #d4edda; color: #155724; }}
        .badge-doc {{ background: #cce5ff; color: #004085; }}
        .badge-obs {{ background: #fff3cd; color: #856404; }}
        .badge-inf {{ background: #f8d7da; color: #721c24; }}
        
        .root-cause-box {{
            background: linear-gradient(135deg, #e8f4fd, #d4edda);
            border: 2px solid var(--success-color);
            border-radius: 8px;
            padding: 20px;
        }}
        
        .root-cause-box h3 {{
            color: var(--success-color);
            margin-bottom: 10px;
        }}
        
        .root-cause-box ul {{
            margin-left: 20px;
        }}
        
        .root-cause-box li {{
            margin-bottom: 10px;
            font-size: 16px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
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
        
        tr.pass {{ background: #f0fff0; }}
        tr.fail {{ background: #fff0f0; }}
        
        .status-pass {{ color: var(--success-color); font-weight: bold; }}
        .status-fail {{ color: var(--danger-color); font-weight: bold; }}
        .status-planned {{ color: #6c757d; }}
        .status-in-progress {{ color: var(--warning-color); }}
        .status-complete {{ color: var(--success-color); }}
        .status-verified {{ color: #28a745; font-weight: bold; }}
        
        .score-table td:nth-child(2),
        .score-table td:nth-child(3),
        .score-table td:nth-child(4) {{
            text-align: center;
        }}
        
        .score-table tfoot {{
            font-weight: bold;
            background: var(--light-bg);
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
            body {{
                padding: 0;
                max-width: none;
            }}
            
            .section {{
                break-inside: avoid;
                box-shadow: none;
            }}
            
            .header {{
                background: var(--primary-color) !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>5 Whys Root Cause Analysis Report</h1>
        <div class="header-meta">
            <span><strong>Analysis ID:</strong> {escape_html(data.analysis_id)}</span>
            <span><strong>Date:</strong> {escape_html(data.analysis_date)}</span>
            <span><strong>Analyst:</strong> {escape_html(data.analyst)}</span>
            <span><strong>Team:</strong> {team_html}</span>
        </div>
    </div>
    
    <div class="score-banner">
        <div class="score-value">{data.overall_score:.0f}/100</div>
        <div class="score-rating">{escape_html(data.rating)}</div>
    </div>
    
    <div class="section">
        <h2>Problem Definition</h2>
        <div class="problem-grid">
            <div class="problem-item">
                <label>What</label>
                {escape_html(data.problem_what)}
            </div>
            <div class="problem-item">
                <label>Where</label>
                {escape_html(data.problem_where)}
            </div>
            <div class="problem-item">
                <label>When</label>
                {escape_html(data.problem_when)}
            </div>
            <div class="problem-item">
                <label>Extent</label>
                {escape_html(data.problem_extent)}
            </div>
            <div class="problem-item">
                <label>Expected</label>
                {escape_html(data.problem_expected)}
            </div>
            <div class="problem-item">
                <label>Actual</label>
                {escape_html(data.problem_actual)}
            </div>
        </div>
        <div class="problem-statement">
            <strong>Problem Statement:</strong> {escape_html(data.problem_statement)}
        </div>
    </div>
    
    <div class="section">
        <h2>5 Whys Analysis Chain</h2>
        <div class="why-chain">
            {why_chain_html}
        </div>
    </div>
    
    <div class="section">
        <h2>Root Cause(s) Identified</h2>
        <div class="root-cause-box">
            <h3>Root Cause(s)</h3>
            <ul>
                {root_causes_html}
            </ul>
        </div>
    </div>
    
    <div class="section">
        <h2>Root Cause Verification</h2>
        <table>
            <thead>
                <tr>
                    <th>Test</th>
                    <th>Result</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody>
                {verification_html}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Countermeasures</h2>
        <table>
            <thead>
                <tr>
                    <th>Action</th>
                    <th>Owner</th>
                    <th>Due Date</th>
                    <th>Success Criteria</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {countermeasures_html}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>Quality Score Breakdown</h2>
        <table class="score-table">
            <thead>
                <tr>
                    <th>Dimension</th>
                    <th>Score</th>
                    <th>Weight</th>
                    <th>Points</th>
                </tr>
            </thead>
            <tbody>
                {score_breakdown_html}
            </tbody>
            <tfoot>
                <tr>
                    <td>Overall Score</td>
                    <td colspan="2"></td>
                    <td>{data.overall_score:.1f}/100</td>
                </tr>
            </tfoot>
        </table>
    </div>
    
    {"<div class='section'><h2>Lessons Learned</h2><p>" + escape_html(data.lessons_learned) + "</p></div>" if data.lessons_learned else ""}
    
    <div class="footer">
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 5 Whys Root Cause Analysis</p>
    </div>
</body>
</html>"""
    
    return html_template


def create_sample_data() -> AnalysisData:
    """Create sample analysis data for demonstration."""
    return AnalysisData(
        analysis_id="RCA-2025-001",
        analysis_date="2025-01-15",
        analyst="J. Smith",
        team_members=["M. Johnson", "K. Williams", "T. Brown"],
        problem_what="CNC Machine #3 produced oversized parts",
        problem_where="Machine Shop, CNC Cell A",
        problem_when="January 15, 2025, 6:00 AM shift",
        problem_extent="47 parts affected",
        problem_expected="Diameter 1.500\" ± 0.002\"",
        problem_actual="Diameter 1.515\" to 1.518\"",
        problem_statement="CNC Machine #3 produced 47 parts with diameter 0.015\" oversized during first shift on January 15, 2025.",
        why_steps=[
            WhyStep(1, "Why were the parts oversized?", "Tool offset was set incorrectly (+0.015\" instead of 0.000\")", "Tool offset register reading", "data"),
            WhyStep(2, "Why was the tool offset set incorrectly?", "Offset wasn't reset after previous job", "Previous job setup sheet shows +0.015\" offset", "document"),
            WhyStep(3, "Why wasn't the offset reset before the new job?", "Setup procedure doesn't include offset verification step", "Procedure document review", "document"),
            WhyStep(4, "Why doesn't the procedure include offset verification?", "Procedure written when only one part ran; offsets never changed", "Procedure dated 2019; 2nd part added 2023", "document"),
            WhyStep(5, "Why wasn't procedure updated when 2nd part added?", "No process triggers procedure review on machine capability changes", "Engineering change shows no procedure review routing", "document"),
        ],
        root_causes=["No Management of Change (MOC) process triggers procedure review when machine capability or part mix changes."],
        verification_tests=[
            VerificationTest("Reversal Test", True, "Chain passes 'therefore' test in both directions"),
            VerificationTest("Prevention Test", True, "MOC process would have triggered procedure update with offset verification"),
            VerificationTest("Control Test", True, "MOC process is within engineering's authority to implement"),
            VerificationTest("Evidence Test", True, "All answers verified with documentation"),
            VerificationTest("Recurrence Test", True, "No similar incidents found; first occurrence of this failure mode"),
        ],
        countermeasures=[
            Countermeasure("Add offset verification step to current procedure", "J. Smith", "2025-01-20", "Procedure updated and approved", "In Progress"),
            Countermeasure("Implement MOC process for machine capability changes", "M. Johnson", "2025-02-28", "MOC process documented and trained", "Planned"),
            Countermeasure("Audit first 3 MOC triggers for procedure updates", "Quality", "2025-03-31", "100% compliance on audited changes", "Planned"),
            Countermeasure("Add MOC compliance to monthly operations review", "Plant Manager", "Ongoing", "Monthly review includes MOC metrics", "Planned"),
        ],
        scores={
            "problem_definition": 5,
            "causal_chain_logic": 4,
            "evidence_basis": 5,
            "root_cause_depth": 4,
            "actionability": 5,
            "countermeasures": 4,
        },
        overall_score=88.0,
        rating="Good",
        lessons_learned="Machine capability changes require systematic review of all associated procedures, not just the engineering change itself.",
    )


def interactive_input() -> AnalysisData:
    """Collect analysis data interactively."""
    print("\n5 WHYS ANALYSIS REPORT GENERATOR")
    print("=" * 50)
    print("Enter analysis data (press Enter for defaults where shown)\n")
    
    # This is a simplified interactive mode - in practice, would be more comprehensive
    analysis_id = input("Analysis ID [RCA-2025-001]: ") or "RCA-2025-001"
    analyst = input("Analyst name: ")
    
    print("\nFor full data entry, please provide a JSON file using --json or --file option.")
    print("Generating sample report for demonstration...")
    
    return create_sample_data()


def main():
    parser = argparse.ArgumentParser(
        description="Generate 5 Whys Analysis HTML Report"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="JSON string with analysis data",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with analysis data",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="five_whys_report.html",
        help="Output HTML file path (default: five_whys_report.html)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate report with sample data",
    )
    
    args = parser.parse_args()
    
    # Get analysis data
    if args.sample:
        data = create_sample_data()
    elif args.json:
        try:
            raw_data = json.loads(args.json)
            # Convert nested dicts to dataclasses
            raw_data["why_steps"] = [WhyStep(**s) for s in raw_data.get("why_steps", [])]
            raw_data["verification_tests"] = [VerificationTest(**t) for t in raw_data.get("verification_tests", [])]
            raw_data["countermeasures"] = [Countermeasure(**c) for c in raw_data.get("countermeasures", [])]
            data = AnalysisData(**raw_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, "r") as f:
                raw_data = json.load(f)
            raw_data["why_steps"] = [WhyStep(**s) for s in raw_data.get("why_steps", [])]
            raw_data["verification_tests"] = [VerificationTest(**t) for t in raw_data.get("verification_tests", [])]
            raw_data["countermeasures"] = [Countermeasure(**c) for c in raw_data.get("countermeasures", [])]
            data = AnalysisData(**raw_data)
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        data = interactive_input()
    
    # Generate report
    html_content = generate_html_report(data)
    
    # Write output
    output_path = Path(args.output)
    output_path.write_text(html_content, encoding="utf-8")
    
    print(f"\n✓ Report generated: {output_path.absolute()}")
    print(f"  Analysis ID: {data.analysis_id}")
    print(f"  Overall Score: {data.overall_score}/100 ({data.rating})")


if __name__ == "__main__":
    main()
