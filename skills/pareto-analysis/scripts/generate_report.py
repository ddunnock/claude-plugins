#!/usr/bin/env python3
"""
Pareto Analysis Report Generator

Generates professional HTML reports with embedded Pareto chart.

Usage:
    python3 generate_report.py --input data.json --output report.html
    python3 generate_report.py --input data.json --output report.html --analyst "John Doe"

Input JSON format (output from calculate_pareto.py):
{
    "input": {"problem_statement": "...", "measurement_type": "..."},
    "results": [...],
    "vital_few": {...},
    "pareto_effect": "...",
    "pareto_description": "...",
    ...
}
"""

import os
import html as html_mod
import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


def esc(val):
    """HTML-escape a value for safe interpolation into HTML."""
    return html_mod.escape(str(val)) if val else ''


def generate_svg_inline(results, total, threshold, vital_few_count, title="Pareto Chart"):
    """Generate inline SVG for the report."""
    # Simplified inline version - import from generate_chart.py in production
    width, height = 800, 400
    margin_top, margin_bottom, margin_left, margin_right = 50, 100, 70, 70
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    
    n_bars = len(results)
    bar_gap = 6
    bar_width = max(15, (chart_width - (n_bars - 1) * bar_gap) / n_bars)
    max_value = max(r['value'] for r in results) if results else 1
    
    svg = [f'<svg viewBox="0 0 {width} {height}" style="max-width:100%;height:auto;">']
    
    # Bars and line
    line_points = []
    for i, r in enumerate(results):
        x = margin_left + i * (bar_width + bar_gap) + bar_width / 2
        bar_height = (r['value'] / max_value) * chart_height
        bar_x = margin_left + i * (bar_width + bar_gap)
        bar_y = margin_top + chart_height - bar_height
        color = "#e74c3c" if i < vital_few_count else "#3498db"
        
        svg.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="{color}" opacity="0.8"/>')
        
        line_y = margin_top + chart_height - (r['cumulative_percentage'] / 100) * chart_height
        line_points.append(f'{x},{line_y}')
    
    if line_points:
        svg.append(f'<polyline points="{" ".join(line_points)}" fill="none" stroke="#2c3e50" stroke-width="2"/>')
    
    # Threshold line
    threshold_y = margin_top + chart_height - (threshold / 100) * chart_height
    svg.append(f'<line x1="{margin_left}" y1="{threshold_y}" x2="{margin_left + chart_width}" y2="{threshold_y}" stroke="#e67e22" stroke-width="2" stroke-dasharray="5,3"/>')
    
    # Axes
    svg.append(f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#333" stroke-width="1"/>')
    svg.append(f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#333" stroke-width="1"/>')
    
    svg.append('</svg>')
    return '\n'.join(svg)


def generate_html_report(
    data: Dict[str, Any],
    analyst: str = "",
    notes: str = ""
) -> str:
    """
    Generate HTML report from Pareto analysis data.
    
    Args:
        data: Complete Pareto analysis data from calculate_pareto.py
        analyst: Analyst name (optional)
        notes: Additional notes (optional)
    
    Returns:
        HTML string
    """
    # Extract data
    results = data.get('results', [])
    vital_few = data.get('vital_few', {})
    total = data.get('total', 0)
    threshold = data.get('threshold', 80)
    pareto_effect = data.get('pareto_effect', 'unknown')
    pareto_description = data.get('pareto_description', '')
    summary = data.get('summary', {})
    
    input_data = data.get('input', {})
    problem_statement = input_data.get('problem_statement', 'Not specified')
    measurement_type = input_data.get('measurement_type', 'frequency')
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Effect styling
    effect_colors = {
        'strong': ('#27ae60', 'Strong Pareto Effect'),
        'moderate': ('#f39c12', 'Moderate Pareto Effect'),
        'weak': ('#e74c3c', 'Weak/No Pareto Effect')
    }
    effect_color, effect_label = effect_colors.get(pareto_effect, ('#7f8c8d', 'Unknown'))
    
    # Generate data table rows
    table_rows = []
    for r in results:
        vital_marker = '✓' if r.get('is_vital_few') else ''
        row_class = 'vital-row' if r.get('is_vital_few') else ''
        table_rows.append(f'''
            <tr class="{row_class}">
                <td>{r['rank']}</td>
                <td>{esc(r['category'])}</td>
                <td class="number">{r['value']:,.0f}</td>
                <td class="number">{r['percentage']:.1f}%</td>
                <td class="number">{r['cumulative_percentage']:.1f}%</td>
                <td class="center">{vital_marker}</td>
            </tr>
        ''')
    
    # Generate vital few list
    vital_list = '\n'.join([f'<li>{esc(cat)}</li>' for cat in vital_few.get('categories', [])])
    
    # Generate SVG
    svg_chart = generate_svg_inline(
        results, total, threshold,
        vital_few.get('count', 0),
        problem_statement
    )
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pareto Analysis Report</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            max-width: 1100px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .report-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .meta-info {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 12px;
            opacity: 0.8;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 18px;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-bottom: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
        }}
        .summary-card .label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .effect-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
            background: {effect_color};
        }}
        .chart-container {{
            background: #f8f9fa;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        th {{
            background: #3498db;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .vital-row {{
            background: #ffeaea;
        }}
        .vital-row:hover {{
            background: #ffdddd;
        }}
        .number {{
            text-align: right;
            font-family: 'SF Mono', Monaco, monospace;
        }}
        .center {{
            text-align: center;
        }}
        .vital-few-list {{
            background: #fff5f5;
            border-left: 4px solid #e74c3c;
            padding: 15px 15px 15px 25px;
            border-radius: 0 6px 6px 0;
        }}
        .vital-few-list h3 {{
            color: #e74c3c;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        .vital-few-list ul {{
            list-style: none;
        }}
        .vital-few-list li {{
            padding: 5px 0;
            border-bottom: 1px dashed #f5c6cb;
        }}
        .vital-few-list li:last-child {{
            border-bottom: none;
        }}
        .recommendations {{
            background: #e8f6ff;
            border-radius: 6px;
            padding: 20px;
        }}
        .recommendations h3 {{
            color: #2980b9;
            margin-bottom: 10px;
        }}
        .recommendations ol {{
            margin-left: 20px;
        }}
        .recommendations li {{
            margin-bottom: 8px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            font-size: 12px;
            color: #7f8c8d;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .report-container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>Pareto Analysis Report</h1>
            <div class="subtitle">{esc(problem_statement)}</div>
            <div class="meta-info">
                <span>Generated: {esc(timestamp)}</span>
                {f'<span>Analyst: {esc(analyst)}</span>' if analyst else ''}
                <span>Measurement: {esc(measurement_type.title())}</span>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="label">Total</div>
                        <div class="value">{total:,.0f}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Categories</div>
                        <div class="value">{len(results)}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Vital Few</div>
                        <div class="value">{vital_few.get('count', 0)}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Vital Few Impact</div>
                        <div class="value">{vital_few.get('cumulative_percentage', 0):.0f}%</div>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 15px;">
                    <span class="effect-badge">{effect_label}</span>
                </p>
                <p style="text-align: center; margin-top: 10px; color: #7f8c8d;">
                    {esc(pareto_description)}
                </p>
            </div>
            
            <div class="section">
                <h2>Pareto Chart</h2>
                <div class="chart-container">
                    {svg_chart}
                </div>
                <p style="text-align: center; font-size: 12px; color: #7f8c8d;">
                    Red bars indicate vital few categories. Orange dashed line shows {threshold}% threshold.
                </p>
            </div>
            
            <div class="section">
                <h2>Vital Few Categories</h2>
                <div class="vital-few-list">
                    <h3>Focus improvement efforts on these {vital_few.get('count', 0)} categories ({vital_few.get('cumulative_percentage', 0):.0f}% of total impact):</h3>
                    <ul>
                        {vital_list}
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>Detailed Data</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Category</th>
                            <th class="number">Value</th>
                            <th class="number">%</th>
                            <th class="number">Cumulative %</th>
                            <th class="center">Vital Few</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(table_rows)}
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>Recommended Next Steps</h2>
                <div class="recommendations">
                    <h3>Based on this Pareto Analysis:</h3>
                    <ol>
                        <li><strong>Investigate Root Causes:</strong> Conduct Fishbone (Ishikawa) analysis on the top vital few categories to brainstorm potential causes.</li>
                        <li><strong>Deep Dive:</strong> Apply 5 Whys technique to each major cause identified to find root causes.</li>
                        <li><strong>Verify Findings:</strong> Validate that the vital few categories align with operational experience and business priorities.</li>
                        <li><strong>Develop Action Plan:</strong> Create corrective action plans for each root cause with owners and timelines.</li>
                        <li><strong>Monitor Progress:</strong> Re-run Pareto analysis after improvements to verify impact.</li>
                    </ol>
                </div>
            </div>
            
            {f'<div class="section"><h2>Additional Notes</h2><p>{esc(notes)}</p></div>' if notes else ''}
        </div>
        
        <div class="footer">
            Pareto Analysis Report | Generated by RCCA Skill Suite
        </div>
    </div>
</body>
</html>'''
    
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
    parser = argparse.ArgumentParser(description="Pareto Report Generator")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file (from calculate_pareto.py)")
    parser.add_argument("--output", "-o", required=True, help="Output HTML file")
    parser.add_argument("--analyst", "-a", default="", help="Analyst name")
    parser.add_argument("--notes", "-n", default="", help="Additional notes")
    
    args = parser.parse_args()

    args.input = _validate_path(args.input, {'.json'}, "input file")
    args.output = _validate_path(args.output, {'.htm', '.html'}, "output file")
    
    # Load input data
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{args.input}'")
        sys.exit(1)
    
    # Generate report
    html = generate_html_report(
        data=data,
        analyst=args.analyst,
        notes=args.notes
    )
    
    # Write output
    with open(args.output, 'w') as f:
        f.write(html)
    
    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
