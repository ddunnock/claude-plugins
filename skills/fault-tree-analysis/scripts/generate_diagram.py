#!/usr/bin/env python3
"""
Fault Tree Diagram Generator

Generates SVG fault tree diagrams from JSON input.
Uses standard FTA symbols: rectangles for intermediate events,
circles for basic events, AND/OR gate symbols.

Usage:
    python generate_diagram.py input.json [output.svg]
"""

import json
import sys
import argparse
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import math


@dataclass
class NodeLayout:
    """Position and size information for a node."""
    x: float
    y: float
    width: float
    height: float
    node_type: str  # "gate", "basic", "undeveloped"
    gate_type: Optional[str] = None  # "AND", "OR"


def calculate_tree_layout(
    tree_data: Dict,
    x_spacing: float = 120,
    y_spacing: float = 150,
    node_width: float = 100,
    node_height: float = 60
) -> Tuple[Dict[str, NodeLayout], float, float]:
    """
    Calculate positions for all nodes in the tree.
    Returns layout dict and total width/height.
    """
    
    # Build parent-child relationships
    children = {}  # node_id -> list of child ids
    node_types = {}  # node_id -> "gate" or "basic"
    gate_types = {}  # gate_id -> "AND" or "OR"
    
    # Process gates
    for gate in tree_data.get("gates", []):
        gid = gate["id"]
        children[gid] = gate.get("inputs", [])
        node_types[gid] = "gate"
        gate_types[gid] = gate.get("gate_type", "OR")
    
    # Process basic events
    for event in tree_data.get("basic_events", []):
        eid = event["id"]
        children[eid] = []
        node_types[eid] = "basic"
    
    top_id = tree_data["top_event"]["id"]
    
    # Calculate subtree widths (bottom-up)
    subtree_widths = {}
    
    def calc_width(node_id: str) -> float:
        if node_id in subtree_widths:
            return subtree_widths[node_id]
        
        child_ids = children.get(node_id, [])
        if not child_ids:
            subtree_widths[node_id] = node_width + x_spacing
            return subtree_widths[node_id]
        
        total = sum(calc_width(cid) for cid in child_ids)
        subtree_widths[node_id] = max(total, node_width + x_spacing)
        return subtree_widths[node_id]
    
    calc_width(top_id)
    
    # Position nodes (top-down)
    layouts = {}
    
    def position_node(node_id: str, x: float, y: float):
        child_ids = children.get(node_id, [])
        ntype = node_types.get(node_id, "basic")
        gtype = gate_types.get(node_id) if ntype == "gate" else None
        
        # Center this node in its allocated space
        node_x = x + subtree_widths[node_id] / 2 - node_width / 2
        
        layouts[node_id] = NodeLayout(
            x=node_x,
            y=y,
            width=node_width,
            height=node_height,
            node_type=ntype,
            gate_type=gtype
        )
        
        # Position children
        if child_ids:
            child_x = x
            child_y = y + y_spacing
            for cid in child_ids:
                position_node(cid, child_x, child_y)
                child_x += subtree_widths.get(cid, node_width + x_spacing)
    
    # Start positioning from top
    total_width = subtree_widths[top_id]
    position_node(top_id, 0, 50)
    
    # Calculate total height
    max_y = max(layout.y for layout in layouts.values())
    total_height = max_y + node_height + 100
    
    return layouts, total_width, total_height


def generate_svg(
    tree_data: Dict,
    layouts: Dict[str, NodeLayout],
    width: float,
    height: float
) -> str:
    """Generate SVG string for the fault tree."""
    
    # Build lookup for names
    names = {}
    names[tree_data["top_event"]["id"]] = tree_data["top_event"]["name"]
    for gate in tree_data.get("gates", []):
        names[gate["id"]] = gate["name"]
    for event in tree_data.get("basic_events", []):
        names[event["id"]] = event["name"]
    
    # Build child relationships
    children = {}
    for gate in tree_data.get("gates", []):
        children[gate["id"]] = gate.get("inputs", [])
    
    svg_parts = []
    
    # SVG header
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 {width + 100} {height + 50}" 
     width="{width + 100}" height="{height + 50}">
  <defs>
    <style>
      .event-box {{ fill: #f0f0f0; stroke: #333; stroke-width: 2; }}
      .basic-event {{ fill: #e8f4e8; stroke: #2e7d32; stroke-width: 2; }}
      .gate-symbol {{ fill: none; stroke: #333; stroke-width: 2; }}
      .gate-fill {{ fill: #fff; }}
      .event-text {{ font-family: Arial, sans-serif; font-size: 11px; text-anchor: middle; }}
      .gate-text {{ font-family: Arial, sans-serif; font-size: 10px; text-anchor: middle; font-weight: bold; }}
      .connector {{ stroke: #666; stroke-width: 1.5; fill: none; }}
    </style>
  </defs>
  <rect width="100%" height="100%" fill="white"/>
  <g transform="translate(50, 0)">
''')
    
    # Draw connectors first (so they're behind nodes)
    for node_id, layout in layouts.items():
        child_ids = children.get(node_id, [])
        if child_ids:
            # Draw vertical line down from this node
            start_x = layout.x + layout.width / 2
            start_y = layout.y + layout.height
            
            # Gate symbol position (below event box)
            gate_y = start_y + 25
            
            # Horizontal line across children
            child_layouts = [layouts[cid] for cid in child_ids if cid in layouts]
            if len(child_layouts) > 1:
                min_x = min(cl.x + cl.width/2 for cl in child_layouts)
                max_x = max(cl.x + cl.width/2 for cl in child_layouts)
                svg_parts.append(f'    <line class="connector" x1="{min_x}" y1="{gate_y + 20}" x2="{max_x}" y2="{gate_y + 20}"/>')
            
            # Vertical lines to each child
            for cid in child_ids:
                if cid in layouts:
                    cl = layouts[cid]
                    child_x = cl.x + cl.width / 2
                    child_y = cl.y
                    svg_parts.append(f'    <line class="connector" x1="{child_x}" y1="{gate_y + 20}" x2="{child_x}" y2="{child_y}"/>')
    
    # Draw nodes
    for node_id, layout in layouts.items():
        cx = layout.x + layout.width / 2
        cy = layout.y + layout.height / 2
        name = names.get(node_id, node_id)
        
        # Wrap long names
        words = name.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line + " " + word) > 15:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = (current_line + " " + word).strip()
        if current_line:
            lines.append(current_line)
        
        if layout.node_type == "basic":
            # Circle for basic event
            radius = min(layout.width, layout.height) / 2 - 5
            svg_parts.append(f'    <circle class="basic-event" cx="{cx}" cy="{cy}" r="{radius}"/>')
            
            # Text
            text_y = cy - (len(lines) - 1) * 6
            for i, line in enumerate(lines):
                svg_parts.append(f'    <text class="event-text" x="{cx}" y="{text_y + i * 12}">{line}</text>')
        
        else:
            # Rectangle for intermediate/top event
            svg_parts.append(f'    <rect class="event-box" x="{layout.x}" y="{layout.y}" width="{layout.width}" height="{layout.height}" rx="3"/>')
            
            # Text
            text_y = cy - (len(lines) - 1) * 6
            for i, line in enumerate(lines):
                svg_parts.append(f'    <text class="event-text" x="{cx}" y="{text_y + i * 12}">{line}</text>')
            
            # Draw gate symbol if this has children
            child_ids = children.get(node_id, [])
            if child_ids:
                gate_y = layout.y + layout.height + 25
                gate_type = layout.gate_type or "OR"
                
                if gate_type == "AND":
                    # AND gate: flat bottom, curved top
                    svg_parts.append(f'''    <path class="gate-symbol gate-fill" d="
                        M {cx - 20} {gate_y + 15}
                        L {cx - 20} {gate_y}
                        L {cx + 20} {gate_y}
                        L {cx + 20} {gate_y + 15}
                        A 20 15 0 0 1 {cx - 20} {gate_y + 15}
                        Z"/>''')
                    svg_parts.append(f'    <text class="gate-text" x="{cx}" y="{gate_y + 10}">AND</text>')
                else:
                    # OR gate: pointed bottom, curved top
                    svg_parts.append(f'''    <path class="gate-symbol gate-fill" d="
                        M {cx - 20} {gate_y + 15}
                        Q {cx - 10} {gate_y} {cx} {gate_y}
                        Q {cx + 10} {gate_y} {cx + 20} {gate_y + 15}
                        Q {cx + 10} {gate_y + 20} {cx} {gate_y + 20}
                        Q {cx - 10} {gate_y + 20} {cx - 20} {gate_y + 15}
                        Z"/>''')
                    svg_parts.append(f'    <text class="gate-text" x="{cx}" y="{gate_y + 12}">OR</text>')
                
                # Line from event box to gate
                svg_parts.append(f'    <line class="connector" x1="{cx}" y1="{layout.y + layout.height}" x2="{cx}" y2="{gate_y}"/>')
    
    # Add legend
    legend_y = height - 30
    svg_parts.append(f'''
    <!-- Legend -->
    <g transform="translate(10, {legend_y})">
      <rect class="event-box" x="0" y="0" width="30" height="20" rx="2"/>
      <text class="event-text" x="50" y="14" style="text-anchor: start">Intermediate Event</text>
      
      <circle class="basic-event" cx="125" cy="10" r="10"/>
      <text class="event-text" x="145" y="14" style="text-anchor: start">Basic Event</text>
      
      <path class="gate-symbol gate-fill" d="M 230 20 L 230 5 L 250 5 L 250 20 A 10 8 0 0 1 230 20 Z"/>
      <text class="gate-text" x="240" y="15">AND</text>
      <text class="event-text" x="265" y="14" style="text-anchor: start">AND Gate</text>
      
      <path class="gate-symbol gate-fill" d="M 330 20 Q 335 5 345 5 Q 355 5 360 20 Q 350 25 345 25 Q 340 25 330 20 Z"/>
      <text class="gate-text" x="345" y="17">OR</text>
      <text class="event-text" x="375" y="14" style="text-anchor: start">OR Gate</text>
    </g>
''')
    
    # Close SVG
    svg_parts.append('  </g>\n</svg>')
    
    return '\n'.join(svg_parts)


def main():
    parser = argparse.ArgumentParser(description="Generate Fault Tree Diagram")
    parser.add_argument("input_file", help="JSON input file with fault tree structure")
    parser.add_argument("output_file", nargs="?", default="fault_tree.svg",
                       help="Output SVG file (default: fault_tree.svg)")
    parser.add_argument("--width", "-w", type=int, default=100,
                       help="Node width in pixels (default: 100)")
    parser.add_argument("--x-spacing", type=int, default=120,
                       help="Horizontal spacing between nodes (default: 120)")
    parser.add_argument("--y-spacing", type=int, default=150,
                       help="Vertical spacing between levels (default: 150)")
    
    args = parser.parse_args()
    
    # Load tree data
    with open(args.input_file, 'r') as f:
        tree_data = json.load(f)
    
    # Calculate layout
    layouts, width, height = calculate_tree_layout(
        tree_data,
        x_spacing=args.x_spacing,
        y_spacing=args.y_spacing,
        node_width=args.width
    )
    
    # Generate SVG
    svg = generate_svg(tree_data, layouts, width, height)
    
    # Write output
    with open(args.output_file, 'w') as f:
        f.write(svg)
    
    print(f"Fault tree diagram saved to: {args.output_file}")
    print(f"Dimensions: {width + 100}x{height + 50} pixels")
    print(f"Nodes: {len(layouts)}")


if __name__ == "__main__":
    main()
