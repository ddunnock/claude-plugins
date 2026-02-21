#!/usr/bin/env python3
"""
Pareto Chart Generator

Generates SVG Pareto charts with bar graph and cumulative line.

Usage:
    python3 generate_chart.py --input data.json --output pareto_chart.svg
    python3 generate_chart.py --input data.json --output chart.svg --title "Defect Analysis"

Input JSON format (output from calculate_pareto.py):
{
    "results": [...],
    "vital_few": {...},
    "total": ...,
    ...
}
"""

import json
import argparse
import sys
from typing import List, Dict, Any
from pathlib import Path


def generate_pareto_svg(
    results: List[Dict],
    total: float,
    title: str = "Pareto Chart",
    threshold: float = 80.0,
    vital_few_count: int = 0,
    width: int = 900,
    height: int = 500
) -> str:
    """
    Generate SVG Pareto chart.
    
    Args:
        results: List of category results with value, percentage, cumulative_percentage
        total: Total value for scaling
        title: Chart title
        threshold: Cumulative percentage threshold line
        vital_few_count: Number of vital few categories to highlight
        width: SVG width in pixels
        height: SVG height in pixels
    
    Returns:
        SVG string
    """
    # Chart dimensions
    margin_top = 60
    margin_bottom = 120
    margin_left = 80
    margin_right = 80
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    
    # Calculate bar dimensions
    n_bars = len(results)
    bar_gap = 8
    bar_width = max(20, (chart_width - (n_bars - 1) * bar_gap) / n_bars)
    
    # Colors
    bar_color = "#3498db"  # Blue
    vital_bar_color = "#e74c3c"  # Red for vital few
    line_color = "#2c3e50"  # Dark blue/gray
    threshold_color = "#e67e22"  # Orange
    grid_color = "#ecf0f1"  # Light gray
    
    # Find max value for scaling
    max_value = max(r['value'] for r in results)
    
    # Start SVG
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        '  .title { font: bold 18px sans-serif; fill: #2c3e50; }',
        '  .axis-label { font: 12px sans-serif; fill: #7f8c8d; }',
        '  .axis-title { font: bold 12px sans-serif; fill: #2c3e50; }',
        '  .category-label { font: 11px sans-serif; fill: #2c3e50; }',
        '  .value-label { font: 10px sans-serif; fill: #2c3e50; }',
        '  .legend-text { font: 11px sans-serif; fill: #2c3e50; }',
        '</style>',
        
        # Background
        f'<rect width="{width}" height="{height}" fill="white"/>',
        
        # Title
        f'<text x="{width/2}" y="30" text-anchor="middle" class="title">{title}</text>',
    ]
    
    # Grid lines (horizontal)
    for i in range(5):
        y = margin_top + chart_height - (i * chart_height / 4)
        svg_parts.append(
            f'<line x1="{margin_left}" y1="{y}" x2="{margin_left + chart_width}" y2="{y}" '
            f'stroke="{grid_color}" stroke-width="1"/>'
        )
    
    # Left Y-axis labels (Value)
    for i in range(5):
        y = margin_top + chart_height - (i * chart_height / 4)
        value = (i / 4) * max_value
        svg_parts.append(
            f'<text x="{margin_left - 10}" y="{y + 4}" text-anchor="end" class="axis-label">'
            f'{value:.0f}</text>'
        )
    
    # Right Y-axis labels (Percentage)
    for i in range(5):
        y = margin_top + chart_height - (i * chart_height / 4)
        pct = i * 25
        svg_parts.append(
            f'<text x="{margin_left + chart_width + 10}" y="{y + 4}" text-anchor="start" class="axis-label">'
            f'{pct}%</text>'
        )
    
    # Y-axis titles
    svg_parts.append(
        f'<text x="20" y="{margin_top + chart_height/2}" text-anchor="middle" '
        f'transform="rotate(-90, 20, {margin_top + chart_height/2})" class="axis-title">Value</text>'
    )
    svg_parts.append(
        f'<text x="{width - 20}" y="{margin_top + chart_height/2}" text-anchor="middle" '
        f'transform="rotate(90, {width - 20}, {margin_top + chart_height/2})" class="axis-title">Cumulative %</text>'
    )
    
    # Bars and cumulative line points
    line_points = []
    
    for i, r in enumerate(results):
        x = margin_left + i * (bar_width + bar_gap) + bar_width / 2
        
        # Bar
        bar_height = (r['value'] / max_value) * chart_height if max_value > 0 else 0
        bar_x = margin_left + i * (bar_width + bar_gap)
        bar_y = margin_top + chart_height - bar_height
        
        # Highlight vital few
        color = vital_bar_color if i < vital_few_count else bar_color
        
        svg_parts.append(
            f'<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" '
            f'fill="{color}" opacity="0.8"/>'
        )
        
        # Value label on bar
        if bar_height > 20:
            svg_parts.append(
                f'<text x="{x}" y="{bar_y + 15}" text-anchor="middle" class="value-label">'
                f'{r["value"]}</text>'
            )
        
        # Category label (rotated)
        label_y = margin_top + chart_height + 10
        # Truncate long labels
        label = r['category'][:15] + '...' if len(r['category']) > 15 else r['category']
        svg_parts.append(
            f'<text x="{x}" y="{label_y}" text-anchor="start" '
            f'transform="rotate(45, {x}, {label_y})" class="category-label">{label}</text>'
        )
        
        # Cumulative line point
        line_y = margin_top + chart_height - (r['cumulative_percentage'] / 100) * chart_height
        line_points.append(f'{x},{line_y}')
    
    # Draw cumulative line
    if line_points:
        svg_parts.append(
            f'<polyline points="{" ".join(line_points)}" '
            f'fill="none" stroke="{line_color}" stroke-width="2"/>'
        )
        
        # Draw points on line
        for i, point in enumerate(line_points):
            x, y = point.split(',')
            svg_parts.append(
                f'<circle cx="{x}" cy="{y}" r="4" fill="{line_color}"/>'
            )
    
    # 80% threshold line
    threshold_y = margin_top + chart_height - (threshold / 100) * chart_height
    svg_parts.append(
        f'<line x1="{margin_left}" y1="{threshold_y}" x2="{margin_left + chart_width}" y2="{threshold_y}" '
        f'stroke="{threshold_color}" stroke-width="2" stroke-dasharray="8,4"/>'
    )
    svg_parts.append(
        f'<text x="{margin_left + chart_width + 5}" y="{threshold_y - 5}" '
        f'text-anchor="start" fill="{threshold_color}" class="axis-label">{threshold}%</text>'
    )
    
    # Legend
    legend_y = height - 25
    svg_parts.extend([
        f'<rect x="{margin_left}" y="{legend_y - 10}" width="15" height="15" fill="{vital_bar_color}" opacity="0.8"/>',
        f'<text x="{margin_left + 20}" y="{legend_y}" class="legend-text">Vital Few</text>',
        f'<rect x="{margin_left + 100}" y="{legend_y - 10}" width="15" height="15" fill="{bar_color}" opacity="0.8"/>',
        f'<text x="{margin_left + 120}" y="{legend_y}" class="legend-text">Useful Many</text>',
        f'<line x1="{margin_left + 220}" y1="{legend_y - 3}" x2="{margin_left + 250}" y2="{legend_y - 3}" stroke="{line_color}" stroke-width="2"/>',
        f'<text x="{margin_left + 255}" y="{legend_y}" class="legend-text">Cumulative %</text>',
        f'<line x1="{margin_left + 370}" y1="{legend_y - 3}" x2="{margin_left + 400}" y2="{legend_y - 3}" stroke="{threshold_color}" stroke-width="2" stroke-dasharray="8,4"/>',
        f'<text x="{margin_left + 405}" y="{legend_y}" class="legend-text">{threshold}% Threshold</text>',
    ])
    
    # Close SVG
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)




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
    parser = argparse.ArgumentParser(description="Pareto Chart Generator")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file (from calculate_pareto.py)")
    parser.add_argument("--output", "-o", required=True, help="Output SVG file")
    parser.add_argument("--title", "-t", default="Pareto Chart", help="Chart title")
    parser.add_argument("--width", type=int, default=900, help="Chart width (default: 900)")
    parser.add_argument("--height", type=int, default=500, help="Chart height (default: 500)")
    
    args = parser.parse_args()

    _validate_path(args.input, {'.json'}, "input file")
    _validate_path(args.output, {'.png', '.svg'}, "output file")
    
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
    
    # Extract required data
    results = data.get('results', [])
    total = data.get('total', 0)
    threshold = data.get('threshold', 80)
    vital_few_count = data.get('vital_few', {}).get('count', 0)
    
    if not results:
        print("Error: No results data in input file")
        sys.exit(1)
    
    # Generate title
    title = args.title
    if data.get('input', {}).get('problem_statement'):
        title = data['input']['problem_statement'][:50]
        if len(data['input']['problem_statement']) > 50:
            title += "..."
    
    # Generate SVG
    svg = generate_pareto_svg(
        results=results,
        total=total,
        title=title,
        threshold=threshold,
        vital_few_count=vital_few_count,
        width=args.width,
        height=args.height
    )
    
    # Write output
    with open(args.output, 'w') as f:
        f.write(svg)
    
    print(f"Pareto chart saved to {args.output}")


if __name__ == "__main__":
    main()
