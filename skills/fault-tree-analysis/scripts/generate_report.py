#!/usr/bin/env python3
"""
Fault Tree Analysis Report Generator

Generates comprehensive HTML reports from FTA analysis results.
Includes embedded diagram, cut set analysis, and recommendations.

Usage:
    python generate_report.py tree.json results.json [output.html]
    python generate_report.py tree.json results.json --svg diagram.svg
"""

import html
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64
from pathlib import Path


def esc(val):
    """HTML-escape a value for safe interpolation into HTML."""
    return html.escape(str(val)) if val else ''


def generate_report_html(
    tree_data: Dict,
    results: Dict,
    svg_content: Optional[str] = None,
    analyst_name: str = "FTA Analyst"
) -> str:
    """Generate comprehensive HTML report."""
    
    top_event = tree_data["top_event"]["name"]
    analysis_type = results.get("analysis_type", "qualitative")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Count events
    num_basic = len(tree_data.get("basic_events", []))
    num_gates = len(tree_data.get("gates", []))
    
    # Build HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fault Tree Analysis Report - {esc(top_event)}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        
        header {{
            background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
            color: white;
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        header h1 {{ font-size: 1.8rem; margin-bottom: 10px; }}
        header .subtitle {{ opacity: 0.9; font-size: 1rem; }}
        header .meta {{ 
            margin-top: 15px; 
            font-size: 0.85rem; 
            opacity: 0.8;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        section h2 {{
            color: #1a237e;
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e8eaf6;
        }}
        section h3 {{
            color: #3949ab;
            font-size: 1.1rem;
            margin: 20px 0 10px 0;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #3949ab;
        }}
        .summary-card .value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #1a237e;
        }}
        .summary-card .label {{
            font-size: 0.85rem;
            color: #666;
            margin-top: 5px;
        }}
        .summary-card.warning {{
            border-left-color: #ff9800;
            background: #fff8e1;
        }}
        .summary-card.warning .value {{
            color: #e65100;
        }}
        .summary-card.danger {{
            border-left-color: #f44336;
            background: #ffebee;
        }}
        .summary-card.danger .value {{
            color: #c62828;
        }}
        .summary-card.success {{
            border-left-color: #4caf50;
            background: #e8f5e9;
        }}
        .summary-card.success .value {{
            color: #2e7d32;
        }}
        
        .diagram-container {{
            overflow-x: auto;
            padding: 20px;
            background: #fafafa;
            border-radius: 6px;
            text-align: center;
        }}
        .diagram-container svg {{
            max-width: 100%;
            height: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #e8eaf6;
            font-weight: 600;
            color: #1a237e;
        }}
        tr:hover {{ background: #f5f5f5; }}
        
        .spof-item {{
            background: #ffebee;
            border: 1px solid #ef9a9a;
            border-radius: 6px;
            padding: 12px 15px;
            margin: 8px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .spof-icon {{
            color: #c62828;
            font-size: 1.2rem;
        }}
        
        .cut-set {{
            background: #f5f5f5;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px 0;
            display: inline-block;
            font-family: monospace;
        }}
        .cut-set.order-1 {{ background: #ffebee; border: 1px solid #ef9a9a; }}
        .cut-set.order-2 {{ background: #fff8e1; border: 1px solid #ffcc80; }}
        
        .importance-bar {{
            display: flex;
            align-items: center;
            margin: 8px 0;
        }}
        .importance-bar .name {{
            width: 200px;
            flex-shrink: 0;
        }}
        .importance-bar .bar-container {{
            flex-grow: 1;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 0 10px;
        }}
        .importance-bar .bar {{
            height: 100%;
            background: linear-gradient(90deg, #3949ab, #7986cb);
            border-radius: 10px;
        }}
        .importance-bar .value {{
            width: 60px;
            text-align: right;
            font-weight: 600;
        }}
        
        .recommendation {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin: 10px 0;
            border-radius: 0 6px 6px 0;
        }}
        .recommendation h4 {{
            color: #2e7d32;
            margin-bottom: 8px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.85rem;
        }}
        
        @media print {{
            body {{ background: white; }}
            section {{ box-shadow: none; border: 1px solid #ddd; }}
            header {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚙️ Fault Tree Analysis Report</h1>
            <div class="subtitle">{esc(top_event)}</div>
            <div class="meta">
                <span>📅 {esc(timestamp)}</span>
                <span>👤 {esc(analyst_name)}</span>
                <span>📊 {esc(analysis_type.capitalize())} Analysis</span>
            </div>
        </header>
'''

    # Executive Summary Section
    spof_count = results.get("spof_count", 0)
    total_cs = results.get("total_cut_sets", 0)
    top_prob = results.get("top_event_probability")
    
    spof_class = "danger" if spof_count > 0 else "success"
    
    html += f'''
        <section>
            <h2>📋 Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">{num_basic}</div>
                    <div class="label">Basic Events</div>
                </div>
                <div class="summary-card">
                    <div class="value">{num_gates}</div>
                    <div class="label">Logic Gates</div>
                </div>
                <div class="summary-card">
                    <div class="value">{total_cs}</div>
                    <div class="label">Minimal Cut Sets</div>
                </div>
                <div class="summary-card {spof_class}">
                    <div class="value">{spof_count}</div>
                    <div class="label">Single Points of Failure</div>
                </div>
'''
    
    if top_prob is not None:
        html += f'''
                <div class="summary-card">
                    <div class="value">{top_prob:.2e}</div>
                    <div class="label">Top Event Probability</div>
                </div>
'''
    
    html += '''
            </div>
        </section>
'''

    # Diagram Section
    if svg_content:
        html += f'''
        <section>
            <h2>🌳 Fault Tree Diagram</h2>
            <div class="diagram-container">
                {svg_content}
            </div>
        </section>
'''

    # Single Points of Failure Section
    spofs = results.get("single_points_of_failure", [])
    if spofs:
        html += '''
        <section>
            <h2>⚠️ Single Points of Failure</h2>
            <p style="margin-bottom: 15px; color: #c62828;">
                <strong>Critical:</strong> These events alone can cause the top event to occur.
                Priority attention required for design improvement.
            </p>
'''
        for spof in spofs:
            html += f'''
            <div class="spof-item">
                <span class="spof-icon">⚠️</span>
                <strong>{esc(spof['name'])}</strong>
                <span style="color: #666;">({esc(spof['id'])})</span>
            </div>
'''
        html += '''
        </section>
'''

    # Minimal Cut Sets Section
    cut_sets = results.get("minimal_cut_sets", [])
    if cut_sets:
        html += '''
        <section>
            <h2>🔗 Minimal Cut Sets</h2>
            <p style="margin-bottom: 15px;">
                Minimal combinations of basic events that cause the top event.
                Lower order cut sets are more critical.
            </p>
'''
        
        # Group by order
        by_order = {}
        for cs in cut_sets:
            order = cs.get("order", len(cs.get("events", [])))
            if order not in by_order:
                by_order[order] = []
            by_order[order].append(cs)
        
        for order in sorted(by_order.keys()):
            cs_list = by_order[order]
            html += f'''
            <h3>Order {order} ({len(cs_list)} cut sets)</h3>
'''
            for cs in cs_list[:10]:  # Limit to first 10 per order
                event_names = [esc(e['name']) for e in cs.get('events', [])]
                prob = cs.get('probability')
                prob_str = f" — P = {prob:.2e}" if prob else ""
                order_class = f"order-{order}" if order <= 2 else ""
                html += f'''
            <div class="cut-set {order_class}">{{{", ".join(event_names)}}}{prob_str}</div>
'''
            if len(cs_list) > 10:
                html += f'''
            <p style="color: #666; margin-top: 10px;">... and {len(cs_list) - 10} more order-{order} cut sets</p>
'''
        
        html += '''
        </section>
'''

    # Importance Measures Section
    importance = results.get("importance_measures", {})
    if importance:
        html += '''
        <section>
            <h2>📊 Importance Analysis (Fussell-Vesely)</h2>
            <p style="margin-bottom: 15px;">
                Contribution of each basic event to the top event probability.
                Higher values indicate more critical components.
            </p>
'''
        # Sort and take top 10
        sorted_imp = sorted(importance.items(), 
                          key=lambda x: x[1].get('fussell_vesely', 0), 
                          reverse=True)[:10]
        
        for event_id, data in sorted_imp:
            fv = data.get('fussell_vesely', 0)
            name = data.get('name', event_id)
            bar_width = min(fv * 100, 100)
            html += f'''
            <div class="importance-bar">
                <span class="name">{esc(name)}</span>
                <div class="bar-container">
                    <div class="bar" style="width: {bar_width}%"></div>
                </div>
                <span class="value">{fv:.1%}</span>
            </div>
'''
        html += '''
        </section>
'''

    # Recommendations Section
    html += '''
        <section>
            <h2>💡 Recommendations</h2>
'''
    
    if spof_count > 0:
        html += '''
            <div class="recommendation">
                <h4>Address Single Points of Failure</h4>
                <p>Add redundancy or additional protective barriers for identified SPOFs.
                Consider diverse redundancy to reduce common cause failure potential.</p>
            </div>
'''
    
    # Check for dominant contributors
    if importance:
        top_contributor = sorted_imp[0] if sorted_imp else None
        if top_contributor and top_contributor[1].get('fussell_vesely', 0) > 0.5:
            html += f'''
            <div class="recommendation">
                <h4>Focus on Dominant Contributor</h4>
                <p><strong>{esc(top_contributor[1].get('name'))}</strong> contributes 
                {top_contributor[1].get('fussell_vesely', 0):.0%} to the top event probability.
                Improving reliability of this component will have the greatest impact.</p>
            </div>
'''
    
    html += '''
            <div class="recommendation">
                <h4>Consider Common Cause Failures</h4>
                <p>Review all AND gates for potential common cause failures. 
                Redundant components may share environmental, maintenance, or design vulnerabilities.</p>
            </div>
            
            <div class="recommendation">
                <h4>Validate with Subject Matter Experts</h4>
                <p>Review cut sets and tree structure with system experts to ensure 
                completeness and accuracy of the failure logic model.</p>
            </div>
        </section>
'''

    # Basic Events Table
    basic_events = tree_data.get("basic_events", [])
    if basic_events:
        html += '''
        <section>
            <h2>📝 Basic Events Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Event Name</th>
                        <th>Probability</th>
                        <th>Data Source</th>
                    </tr>
                </thead>
                <tbody>
'''
        for event in basic_events:
            prob = event.get('probability')
            if not prob and event.get('failure_rate') and event.get('mission_time'):
                prob = event['failure_rate'] * event['mission_time']
            prob_str = f"{prob:.2e}" if prob else "N/A"
            source = event.get('data_source', 'Not specified')
            html += f'''
                    <tr>
                        <td>{esc(event['id'])}</td>
                        <td>{esc(event['name'])}</td>
                        <td>{esc(prob_str)}</td>
                        <td>{esc(source)}</td>
                    </tr>
'''
        html += '''
                </tbody>
            </table>
        </section>
'''

    # Footer
    html += '''
        <footer>
            <p>Generated by Fault Tree Analysis Skill</p>
            <p>This analysis should be reviewed by qualified personnel before making safety-critical decisions.</p>
        </footer>
    </div>
</body>
</html>
'''
    
    return html




def _validate_path(filepath: str, allowed_extensions: set, label: str) -> None:
    """Validate file path: reject traversal and restrict extensions."""
    if ".." in filepath:
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = Path(filepath).suffix.lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate FTA Report")
    parser.add_argument("tree_file", help="JSON file with fault tree structure")
    parser.add_argument("results_file", help="JSON file with analysis results")
    parser.add_argument("output_file", nargs="?", default="fta_report.html",
                       help="Output HTML file (default: fta_report.html)")
    parser.add_argument("--svg", help="SVG diagram file to embed")
    parser.add_argument("--analyst", default="FTA Analyst", help="Analyst name for report")
    
    args = parser.parse_args()

    _validate_path(args.tree_file, {'.json'}, "tree file")
    _validate_path(args.results_file, {'.json'}, "results file")
    _validate_path(args.output_file, {'.htm', '.html'}, "output file")
    if args.svg:
        _validate_path(args.svg, {'.svg'}, "SVG file")
    
    # Load input files
    with open(args.tree_file, 'r') as f:
        tree_data = json.load(f)
    
    with open(args.results_file, 'r') as f:
        results = json.load(f)
    
    # Load SVG if provided
    svg_content = None
    if args.svg:
        with open(args.svg, 'r') as f:
            svg_content = f.read()
    
    # Generate report
    html = generate_report_html(tree_data, results, svg_content, args.analyst)
    
    # Write output
    with open(args.output_file, 'w') as f:
        f.write(html)
    
    print(f"Report generated: {args.output_file}")


if __name__ == "__main__":
    main()
