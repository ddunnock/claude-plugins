#!/usr/bin/env python3
"""
Fishbone Diagram SVG Generator

Creates visual fishbone (Ishikawa) diagrams from structured data.

Usage:
  python generate_diagram.py --file analysis.json --output diagram.svg
  python generate_diagram.py --sample --output sample_diagram.svg

Input JSON structure:
{
  "problem": "Problem statement text",
  "categories": [
    {
      "name": "Category Name",
      "causes": [
        {
          "text": "Cause text",
          "subcauses": [
            {"text": "Subcause text", "subcauses": [...]}
          ]
        }
      ]
    }
  ],
  "metadata": {
    "title": "Analysis Title",
    "date": "2025-01-27",
    "team": "Team Name"
  }
}
"""

import os
import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path


def escape_xml(text):
    """Escape special XML characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def wrap_text(text, max_chars=25):
    """Wrap text into multiple lines."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_chars:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines if lines else [text[:max_chars]]


def generate_sample_data():
    """Generate sample fishbone data for testing."""
    return {
        "problem": "Widget A dimensional variance exceeds ±0.05mm on 15% of units",
        "categories": [
            {
                "name": "Man",
                "causes": [
                    {
                        "text": "Operator inexperience",
                        "subcauses": [
                            {"text": "New operator assigned", "subcauses": []},
                            {"text": "Training incomplete", "subcauses": []}
                        ]
                    },
                    {"text": "Measurement technique variation", "subcauses": []},
                    {"text": "Night shift fatigue", "subcauses": []}
                ]
            },
            {
                "name": "Machine",
                "causes": [
                    {
                        "text": "CNC spindle wear",
                        "subcauses": [
                            {"text": "2500 hrs since rebuild", "subcauses": []},
                            {"text": "Vibration elevated", "subcauses": []}
                        ]
                    },
                    {"text": "Coolant degradation", "subcauses": []},
                    {"text": "Fixture wear", "subcauses": []}
                ]
            },
            {
                "name": "Method",
                "causes": [
                    {
                        "text": "Tool offset not verified",
                        "subcauses": [
                            {"text": "Procedure skipped", "subcauses": []}
                        ]
                    },
                    {"text": "Warm-up cycle inadequate", "subcauses": []},
                    {"text": "Inspection reduced", "subcauses": []}
                ]
            },
            {
                "name": "Material",
                "causes": [
                    {
                        "text": "New material lot",
                        "subcauses": [
                            {"text": "Hardness variation", "subcauses": []},
                            {"text": "Different supplier", "subcauses": []}
                        ]
                    },
                    {"text": "Bar stock variation", "subcauses": []}
                ]
            },
            {
                "name": "Measurement",
                "causes": [
                    {"text": "Calibration overdue", "subcauses": []},
                    {"text": "SPC not reviewed", "subcauses": []},
                    {"text": "Sampling inadequate", "subcauses": []}
                ]
            },
            {
                "name": "Mother Nature",
                "causes": [
                    {
                        "text": "Temperature fluctuation",
                        "subcauses": [
                            {"text": "HVAC issues", "subcauses": []}
                        ]
                    },
                    {"text": "Humidity variation", "subcauses": []}
                ]
            }
        ],
        "metadata": {
            "title": "CNC Dimensional Variance Analysis",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "team": "Quality Engineering"
        }
    }


def generate_svg(data, width=1200, height=800):
    """Generate SVG fishbone diagram from data."""
    
    # Colors
    colors = {
        "spine": "#2c3e50",
        "bone": "#34495e",
        "category": "#3498db",
        "cause": "#2c3e50",
        "subcause": "#7f8c8d",
        "head_fill": "#e74c3c",
        "head_text": "#ffffff",
        "background": "#ffffff",
        "title": "#2c3e50"
    }
    
    # Layout parameters
    margin = 60
    head_width = 200
    head_height = 80
    spine_y = height / 2
    spine_start_x = margin
    spine_end_x = width - margin - head_width
    
    # Calculate category spacing
    categories = data.get("categories", [])
    num_categories = len(categories)
    
    # Alternate categories above and below spine
    top_categories = categories[::2]  # Even indices (0, 2, 4, ...)
    bottom_categories = categories[1::2]  # Odd indices (1, 3, 5, ...)
    
    # Calculate horizontal positions
    category_spacing = (spine_end_x - spine_start_x - 100) / max(num_categories, 1)
    
    svg_parts = []
    
    # SVG header
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .title {{ font-family: Arial, sans-serif; font-size: 20px; font-weight: bold; fill: {colors["title"]}; }}
      .subtitle {{ font-family: Arial, sans-serif; font-size: 12px; fill: {colors["subcause"]}; }}
      .category {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: {colors["category"]}; }}
      .cause {{ font-family: Arial, sans-serif; font-size: 11px; fill: {colors["cause"]}; }}
      .subcause {{ font-family: Arial, sans-serif; font-size: 10px; fill: {colors["subcause"]}; }}
      .head-text {{ font-family: Arial, sans-serif; font-size: 12px; fill: {colors["head_text"]}; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="{colors["spine"]}" />
    </marker>
  </defs>
  
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="{colors["background"]}" />
''')
    
    # Title
    metadata = data.get("metadata", {})
    title = metadata.get("title", "Fishbone Diagram")
    date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
    team = metadata.get("team", "")
    
    svg_parts.append(f'''
  <!-- Title -->
  <text x="{margin}" y="30" class="title">{escape_xml(title)}</text>
  <text x="{margin}" y="48" class="subtitle">Date: {escape_xml(date)}{f"  |  Team: {escape_xml(team)}" if team else ""}</text>
''')
    
    # Main spine (horizontal line with arrow)
    svg_parts.append(f'''
  <!-- Spine -->
  <line x1="{spine_start_x}" y1="{spine_y}" x2="{spine_end_x}" y2="{spine_y}" 
        stroke="{colors["spine"]}" stroke-width="3" marker-end="url(#arrowhead)" />
''')
    
    # Fish head (problem statement)
    problem = data.get("problem", "Problem Statement")
    problem_lines = wrap_text(problem, 22)
    
    head_x = spine_end_x
    head_y = spine_y - head_height / 2
    
    svg_parts.append(f'''
  <!-- Fish Head (Problem) -->
  <rect x="{head_x}" y="{head_y}" width="{head_width}" height="{head_height}" 
        rx="10" ry="10" fill="{colors["head_fill"]}" />
''')
    
    # Problem text (centered in head)
    text_start_y = head_y + (head_height - len(problem_lines) * 14) / 2 + 12
    for i, line in enumerate(problem_lines):
        svg_parts.append(f'''  <text x="{head_x + head_width/2}" y="{text_start_y + i*14}" 
        text-anchor="middle" class="head-text">{escape_xml(line)}</text>
''')
    
    # Draw categories and causes
    def draw_category(cat, x_pos, is_top):
        """Draw a category bone with its causes."""
        parts = []
        
        # Bone angle
        angle = 50 if is_top else -50
        bone_length = 150
        
        # Calculate bone endpoint
        end_x = x_pos - bone_length * math.cos(math.radians(angle))
        end_y = spine_y - bone_length * math.sin(math.radians(angle))
        
        # Main bone line
        parts.append(f'''
  <!-- Category: {escape_xml(cat["name"])} -->
  <line x1="{x_pos}" y1="{spine_y}" x2="{end_x}" y2="{end_y}" 
        stroke="{colors["bone"]}" stroke-width="2" />
''')
        
        # Category label
        label_y = end_y - 15 if is_top else end_y + 20
        parts.append(f'''  <text x="{end_x}" y="{label_y}" text-anchor="middle" class="category">{escape_xml(cat["name"])}</text>
''')
        
        # Draw causes along the bone
        causes = cat.get("causes", [])
        if causes:
            cause_spacing = bone_length / (len(causes) + 1)
            
            for i, cause in enumerate(causes):
                # Position along the bone
                t = (i + 1) / (len(causes) + 1)
                cause_x = x_pos - t * (x_pos - end_x)
                cause_y = spine_y - t * (spine_y - end_y)
                
                # Cause branch (perpendicular to bone)
                branch_length = 60
                if is_top:
                    branch_end_x = cause_x - branch_length * 0.7
                    branch_end_y = cause_y - branch_length * 0.3
                else:
                    branch_end_x = cause_x - branch_length * 0.7
                    branch_end_y = cause_y + branch_length * 0.3
                
                parts.append(f'''  <line x1="{cause_x}" y1="{cause_y}" x2="{branch_end_x}" y2="{branch_end_y}" 
        stroke="{colors["bone"]}" stroke-width="1.5" />
''')
                
                # Cause text
                cause_text = cause.get("text", "")
                cause_lines = wrap_text(cause_text, 18)
                text_x = branch_end_x - 5
                text_y = branch_end_y - 5 if is_top else branch_end_y + 12
                
                for j, line in enumerate(cause_lines[:2]):  # Max 2 lines
                    offset = j * 12 if not is_top else -j * 12
                    parts.append(f'''  <text x="{text_x}" y="{text_y + offset}" text-anchor="end" class="cause">{escape_xml(line)}</text>
''')
                
                # Draw subcauses
                subcauses = cause.get("subcauses", [])
                if subcauses:
                    for k, subcause in enumerate(subcauses[:3]):  # Max 3 subcauses
                        sub_t = (k + 1) / (len(subcauses[:3]) + 1)
                        sub_x = cause_x - sub_t * (cause_x - branch_end_x)
                        sub_y = cause_y - sub_t * (cause_y - branch_end_y)
                        
                        # Small branch for subcause
                        sub_length = 35
                        if is_top:
                            sub_end_x = sub_x - sub_length * 0.5
                            sub_end_y = sub_y - sub_length * 0.5
                        else:
                            sub_end_x = sub_x - sub_length * 0.5
                            sub_end_y = sub_y + sub_length * 0.5
                        
                        parts.append(f'''  <line x1="{sub_x}" y1="{sub_y}" x2="{sub_end_x}" y2="{sub_end_y}" 
        stroke="{colors["subcause"]}" stroke-width="1" />
''')
                        
                        # Subcause text
                        sub_text = subcause.get("text", "")[:25]
                        sub_text_y = sub_end_y - 3 if is_top else sub_end_y + 10
                        parts.append(f'''  <text x="{sub_end_x - 3}" y="{sub_text_y}" text-anchor="end" class="subcause">{escape_xml(sub_text)}</text>
''')
        
        return "".join(parts)
    
    # Draw top categories
    for i, cat in enumerate(top_categories):
        x_pos = spine_start_x + 100 + (i * 2) * category_spacing
        svg_parts.append(draw_category(cat, x_pos, True))
    
    # Draw bottom categories
    for i, cat in enumerate(bottom_categories):
        x_pos = spine_start_x + 100 + (i * 2 + 1) * category_spacing
        svg_parts.append(draw_category(cat, x_pos, False))
    
    # Close SVG
    svg_parts.append("</svg>")
    
    return "".join(svg_parts)




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
        description="Generate SVG Fishbone (Ishikawa) Diagram"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with fishbone data"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="JSON string with fishbone data"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate diagram with sample data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="fishbone_diagram.svg",
        help="Output SVG file path (default: fishbone_diagram.svg)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1200,
        help="Diagram width in pixels (default: 1200)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=800,
        help="Diagram height in pixels (default: 800)"
    )
    
    args = parser.parse_args()

    if args.file:
        args.file = _validate_path(args.file, {'.json'}, "input file")
    args.output = _validate_path(args.output, {'.svg'}, "output file")
    
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
    
    # Generate SVG
    svg_content = generate_svg(data, args.width, args.height)
    
    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✓ Fishbone diagram generated: {args.output}")
    print(f"  Problem: {data.get('problem', 'N/A')[:50]}...")
    print(f"  Categories: {len(data.get('categories', []))}")
    total_causes = sum(len(c.get('causes', [])) for c in data.get('categories', []))
    print(f"  Total causes: {total_causes}")


if __name__ == "__main__":
    main()
