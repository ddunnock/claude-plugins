#!/usr/bin/env python3
"""
Kepner-Tregoe Analysis Report Generator

Generates professional HTML reports for KT analyses including:
- Situation Appraisal
- Problem Analysis (with IS/IS NOT matrix)
- Decision Analysis (with scoring)
- Potential Problem Analysis

Usage:
    python generate_report.py --input analysis.json --output report.html
    python generate_report.py --input analysis.json --type PA
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import html


def escape_html(text: str) -> str:
    """Safely escape HTML characters."""
    return html.escape(str(text)) if text else ""


def get_risk_color(level: str) -> str:
    """Get color for risk level."""
    colors = {
        'CRITICAL': '#dc2626',  # red-600
        'HIGH': '#ea580c',      # orange-600
        'MEDIUM': '#ca8a04',    # yellow-600
        'LOW': '#16a34a',       # green-600
        'H': '#ea580c',
        'M': '#ca8a04',
        'L': '#16a34a'
    }
    return colors.get(level.upper(), '#6b7280')


def generate_css() -> str:
    """Generate CSS styles for the report."""
    return """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #1f2937; 
            background: #f9fafb;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .report-header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .report-header h1 { font-size: 1.75rem; margin-bottom: 0.5rem; }
        .report-header .subtitle { opacity: 0.9; font-size: 1rem; }
        .report-header .meta { margin-top: 1rem; font-size: 0.875rem; opacity: 0.8; }
        
        .section {
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .section h2 {
            color: #1e40af;
            font-size: 1.25rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #dbeafe;
        }
        .section h3 {
            color: #374151;
            font-size: 1rem;
            margin: 1rem 0 0.5rem 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.875rem;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f3f4f6;
            font-weight: 600;
            color: #374151;
        }
        tr:hover { background: #f9fafb; }
        
        .is-is-not-table th { font-size: 0.75rem; text-transform: uppercase; }
        .is-col { background: #dcfce7 !important; }
        .is-not-col { background: #fef3c7 !important; }
        .distinction-col { background: #dbeafe !important; }
        
        .score-table .score-cell { text-align: center; font-weight: 600; }
        .score-high { color: #16a34a; }
        .score-mid { color: #ca8a04; }
        .score-low { color: #dc2626; }
        
        .ranking-table tr:first-child { background: #dcfce7; }
        .ranking-table .rank-1 { font-weight: bold; }
        
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
        }
        
        .summary-box {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        .summary-box.success { background: #dcfce7; border-color: #16a34a; }
        .summary-box.warning { background: #fef3c7; border-color: #ca8a04; }
        .summary-box.error { background: #fee2e2; border-color: #dc2626; }
        
        .cause-test-table .pass { color: #16a34a; font-weight: bold; }
        .cause-test-table .partial { color: #ca8a04; }
        .cause-test-table .fail { color: #dc2626; font-weight: bold; }
        
        .ppa-table .preventive { background: #dcfce7; }
        .ppa-table .contingent { background: #fef3c7; }
        
        .footer {
            text-align: center;
            padding: 1rem;
            color: #6b7280;
            font-size: 0.75rem;
        }
        
        @media print {
            body { background: white; padding: 0; }
            .section { box-shadow: none; border: 1px solid #e5e7eb; }
            .report-header { background: #1e40af; -webkit-print-color-adjust: exact; }
        }
    </style>
    """


def generate_pa_report(data: dict) -> str:
    """Generate Problem Analysis report section."""
    html_parts = []
    
    # Deviation Statement
    if 'deviation_statement' in data:
        html_parts.append(f"""
        <div class="section">
            <h2>Problem Statement</h2>
            <div class="summary-box">
                <strong>Object:</strong> {escape_html(data.get('object', 'Not specified'))}<br>
                <strong>Deviation:</strong> {escape_html(data.get('deviation', 'Not specified'))}
            </div>
            <p><strong>Full Statement:</strong> {escape_html(data['deviation_statement'])}</p>
        </div>
        """)
    
    # IS/IS NOT Matrix
    if 'specification' in data:
        spec = data['specification']
        html_parts.append("""
        <div class="section">
            <h2>IS / IS NOT Specification Matrix</h2>
            <table class="is-is-not-table">
                <thead>
                    <tr>
                        <th>Dimension</th>
                        <th class="is-col">IS (Observed)</th>
                        <th class="is-not-col">IS NOT (Could be but isn't)</th>
                        <th class="distinction-col">Distinction</th>
                    </tr>
                </thead>
                <tbody>
        """)
        
        for row in spec:
            html_parts.append(f"""
                <tr>
                    <td><strong>{escape_html(row.get('dimension', ''))}</strong></td>
                    <td class="is-col">{escape_html(row.get('is', ''))}</td>
                    <td class="is-not-col">{escape_html(row.get('is_not', ''))}</td>
                    <td class="distinction-col">{escape_html(row.get('distinction', ''))}</td>
                </tr>
            """)
        
        html_parts.append("</tbody></table></div>")
    
    # Possible Causes and Testing
    if 'possible_causes' in data:
        html_parts.append("""
        <div class="section">
            <h2>Possible Causes and Testing</h2>
            <table class="cause-test-table">
                <thead>
                    <tr>
                        <th>Possible Cause</th>
                        <th>Source Distinction</th>
                        <th>Test Score</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
        """)
        
        for cause in data['possible_causes']:
            score = cause.get('score', 0)
            max_score = cause.get('max_score', 8)
            score_class = 'pass' if score >= max_score * 0.8 else ('partial' if score >= max_score * 0.5 else 'fail')
            html_parts.append(f"""
                <tr>
                    <td>{escape_html(cause.get('cause', ''))}</td>
                    <td>{escape_html(cause.get('source_distinction', ''))}</td>
                    <td class="{score_class}">{score}/{max_score}</td>
                    <td>{escape_html(cause.get('notes', ''))}</td>
                </tr>
            """)
        
        html_parts.append("</tbody></table></div>")
    
    # Most Probable Cause
    if 'most_probable_cause' in data:
        html_parts.append(f"""
        <div class="section">
            <h2>Most Probable Cause</h2>
            <div class="summary-box success">
                <strong>{escape_html(data['most_probable_cause'])}</strong>
            </div>
            <h3>Verification Plan</h3>
            <ul>
        """)
        for step in data.get('verification_plan', []):
            html_parts.append(f"<li>{escape_html(step)}</li>")
        html_parts.append("</ul></div>")
    
    return "\n".join(html_parts)


def generate_da_report(data: dict) -> str:
    """Generate Decision Analysis report section."""
    html_parts = []
    
    # Decision Statement
    if 'decision_statement' in data:
        html_parts.append(f"""
        <div class="section">
            <h2>Decision Statement</h2>
            <div class="summary-box">
                {escape_html(data['decision_statement'])}
            </div>
        </div>
        """)
    
    # MUSTS
    if 'musts' in data:
        html_parts.append("""
        <div class="section">
            <h2>MUSTS (Mandatory Requirements)</h2>
            <table>
                <thead>
                    <tr><th>Criterion</th><th>Measurement</th></tr>
                </thead>
                <tbody>
        """)
        for must in data['musts']:
            html_parts.append(f"""
                <tr>
                    <td><strong>{escape_html(must.get('name', ''))}</strong></td>
                    <td>{escape_html(must.get('measurement', ''))}</td>
                </tr>
            """)
        html_parts.append("</tbody></table></div>")
    
    # WANTS
    if 'wants' in data:
        html_parts.append("""
        <div class="section">
            <h2>WANTS (Desired Outcomes)</h2>
            <table>
                <thead>
                    <tr><th>Criterion</th><th>Direction</th><th>Weight</th></tr>
                </thead>
                <tbody>
        """)
        for want in data['wants']:
            direction = "↑ Higher is better" if want.get('direction') == 'higher_better' else "↓ Lower is better"
            html_parts.append(f"""
                <tr>
                    <td><strong>{escape_html(want.get('name', ''))}</strong></td>
                    <td>{direction}</td>
                    <td><strong>{want.get('weight', '')}</strong></td>
                </tr>
            """)
        html_parts.append("</tbody></table></div>")
    
    # Scoring Results
    if 'results' in data:
        html_parts.append("""
        <div class="section">
            <h2>Alternative Scoring Results</h2>
            <table class="ranking-table">
                <thead>
                    <tr><th>Rank</th><th>Alternative</th><th>Total Score</th><th>Percentage</th></tr>
                </thead>
                <tbody>
        """)
        for result in data['results']:
            rank_class = 'rank-1' if result.get('rank') == 1 else ''
            html_parts.append(f"""
                <tr class="{rank_class}">
                    <td>#{result.get('rank', '')}</td>
                    <td><strong>{escape_html(result.get('alternative', ''))}</strong></td>
                    <td>{result.get('total_weighted', '')}</td>
                    <td>{result.get('percentage', '')}%</td>
                </tr>
            """)
        html_parts.append("</tbody></table></div>")
    
    # Recommendation
    if 'summary' in data and data['summary'].get('recommended'):
        summary = data['summary']
        html_parts.append(f"""
        <div class="section">
            <h2>Recommendation</h2>
            <div class="summary-box success">
                <strong>Recommended: {escape_html(summary['recommended'])}</strong><br>
                Score: {summary.get('recommended_score', '')} ({summary.get('recommended_percentage', '')}%)
            </div>
        </div>
        """)
    
    return "\n".join(html_parts)


def generate_ppa_report(data: dict) -> str:
    """Generate Potential Problem Analysis report section."""
    html_parts = []
    
    # Plan Statement
    if 'plan_statement' in data:
        html_parts.append(f"""
        <div class="section">
            <h2>Plan Statement</h2>
            <div class="summary-box">
                {escape_html(data['plan_statement'])}
            </div>
        </div>
        """)
    
    # Potential Problems and Actions
    if 'potential_problems' in data:
        html_parts.append("""
        <div class="section">
            <h2>Risk Assessment and Actions</h2>
            <table class="ppa-table">
                <thead>
                    <tr>
                        <th>Step/Area</th>
                        <th>Potential Problem</th>
                        <th>P</th>
                        <th>S</th>
                        <th>Risk</th>
                        <th>Preventive Action</th>
                        <th>Contingent Action</th>
                        <th>Trigger</th>
                    </tr>
                </thead>
                <tbody>
        """)
        
        for pp in data['potential_problems']:
            risk_color = get_risk_color(pp.get('combined_risk', ''))
            html_parts.append(f"""
                <tr>
                    <td>{escape_html(pp.get('step', ''))}</td>
                    <td>{escape_html(pp.get('problem', ''))}</td>
                    <td style="color: {get_risk_color(pp.get('probability', ''))}">{pp.get('probability', '')}</td>
                    <td style="color: {get_risk_color(pp.get('seriousness', ''))}">{pp.get('seriousness', '')}</td>
                    <td><span class="risk-badge" style="background: {risk_color}">{pp.get('combined_risk', '')}</span></td>
                    <td class="preventive">{escape_html(pp.get('preventive_action', ''))}</td>
                    <td class="contingent">{escape_html(pp.get('contingent_action', ''))}</td>
                    <td>{escape_html(pp.get('trigger', ''))}</td>
                </tr>
            """)
        
        html_parts.append("</tbody></table></div>")
    
    return "\n".join(html_parts)


def generate_report(data: dict, output_file: str, report_type: Optional[str] = None):
    """Generate complete HTML report."""
    
    # Determine report type from data if not specified
    if not report_type:
        if 'specification' in data or 'deviation_statement' in data:
            report_type = 'PA'
        elif 'decision_statement' in data and 'wants' in data:
            report_type = 'DA'
        elif 'potential_problems' in data:
            report_type = 'PPA'
        else:
            report_type = 'FULL'
    
    report_titles = {
        'SA': 'Situation Appraisal',
        'PA': 'Problem Analysis',
        'DA': 'Decision Analysis', 
        'PPA': 'Potential Problem Analysis',
        'FULL': 'Kepner-Tregoe Analysis'
    }
    
    # Build HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KT {report_titles.get(report_type, 'Analysis')} Report</title>
        {generate_css()}
    </head>
    <body>
        <div class="container">
            <div class="report-header">
                <h1>Kepner-Tregoe {report_titles.get(report_type, 'Analysis')}</h1>
                <div class="subtitle">{escape_html(data.get('title', data.get('decision_statement', data.get('deviation_statement', ''))))}</div>
                <div class="meta">
                    Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}<br>
                    Analysis Date: {data.get('created_at', data.get('analysis', {}).get('created_at', 'Not specified'))}
                </div>
            </div>
    """
    
    # Add appropriate sections based on report type
    if report_type == 'PA' or report_type == 'FULL':
        html_content += generate_pa_report(data.get('analysis', data))
    
    if report_type == 'DA' or report_type == 'FULL':
        da_data = data.get('analysis', data)
        da_data['results'] = data.get('results', [])
        da_data['summary'] = data.get('summary', {})
        html_content += generate_da_report(da_data)
    
    if report_type == 'PPA' or report_type == 'FULL':
        html_content += generate_ppa_report(data.get('analysis', data))
    
    # Footer
    html_content += """
            <div class="footer">
                Generated by Kepner-Tregoe Analysis Toolkit<br>
                Methodology: Kepner-Tregoe Problem Solving and Decision Making (PSDM)
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate Kepner-Tregoe Analysis Report')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    parser.add_argument('--output', '-o', default='kt_report.html', help='Output HTML file')
    parser.add_argument('--type', '-t', choices=['SA', 'PA', 'DA', 'PPA', 'FULL'], 
                        help='Report type (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    generate_report(data, args.output, args.type)


if __name__ == '__main__':
    main()
