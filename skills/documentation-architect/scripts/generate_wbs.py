#!/usr/bin/env python3
"""
Generate work breakdown structure for documentation project.

Usage:
    python generate_wbs.py --inventory inventory.json --output wbs.md [--target-structure structure.yaml]
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import sys


# Default target structure based on Diátaxis
DEFAULT_STRUCTURE = {
    'docs': {
        'index.md': {'quadrant': 'Overview', 'priority': 1, 'effort': 'Low'},
        'getting-started': {
            'quickstart.md': {'quadrant': 'Tutorial', 'priority': 1, 'effort': 'Medium'},
            'installation.md': {'quadrant': 'How-To', 'priority': 1, 'effort': 'Low'},
            'first-project.md': {'quadrant': 'Tutorial', 'priority': 2, 'effort': 'High'},
        },
        'guides': {
            '_description': 'How-To Guides',
            '_default_quadrant': 'How-To',
            '_default_priority': 2,
            '_default_effort': 'Medium',
        },
        'concepts': {
            '_description': 'Explanation content',
            '_default_quadrant': 'Explanation',
            '_default_priority': 3,
            '_default_effort': 'Medium',
        },
        'reference': {
            '_description': 'Reference documentation',
            '_default_quadrant': 'Reference',
            '_default_priority': 2,
            '_default_effort': 'High',
        },
    }
}


def load_inventory(inventory_path: Path) -> dict:
    """Load documentation inventory."""
    with open(inventory_path) as f:
        return json.load(f)


def generate_wbs_items(inventory: dict, structure: dict) -> list:
    """Generate WBS items based on inventory and target structure."""
    items = []
    wbs_id = 1
    
    # Map existing docs to quadrants
    existing_docs = {}
    for doc in inventory.get('documents', []):
        existing_docs[doc['path']] = doc
    
    # Generate items for target structure
    def process_structure(struct: dict, path_prefix: str = '', parent_id: str = ''):
        nonlocal wbs_id
        
        for name, value in struct.items():
            if name.startswith('_'):
                continue
            
            current_path = f"{path_prefix}/{name}" if path_prefix else name
            current_id = f"WBS-{wbs_id:03d}"
            wbs_id += 1
            
            if isinstance(value, dict) and not value.get('quadrant'):
                # Directory
                description = value.get('_description', f'{name} section')
                items.append({
                    'id': current_id,
                    'type': 'section',
                    'path': current_path,
                    'name': name,
                    'description': description,
                    'priority': value.get('_default_priority', 2),
                    'effort': 'N/A',
                    'status': 'Pending',
                    'dependencies': [],
                })
                process_structure(value, current_path, current_id)
            else:
                # File
                if isinstance(value, dict):
                    quadrant = value.get('quadrant', 'Unknown')
                    priority = value.get('priority', 2)
                    effort = value.get('effort', 'Medium')
                else:
                    quadrant = 'Unknown'
                    priority = 2
                    effort = 'Medium'
                
                items.append({
                    'id': current_id,
                    'type': 'document',
                    'path': current_path,
                    'name': name,
                    'quadrant': quadrant,
                    'priority': priority,
                    'effort': effort,
                    'status': 'Pending',
                    'dependencies': [parent_id] if parent_id else [],
                    'sources': [],
                })
    
    process_structure(structure)
    
    # Map existing docs as sources
    quadrant_map = {
        'Tutorial': ['getting-started', 'tutorial'],
        'How-To': ['guides', 'how-to'],
        'Reference': ['reference', 'api'],
        'Explanation': ['concepts', 'explanation'],
    }
    
    for doc in inventory.get('documents', []):
        doc_quadrant = doc.get('diataxis_quadrant', 'Unknown')
        
        # Find best matching WBS item
        for item in items:
            if item['type'] == 'document':
                if item.get('quadrant') == doc_quadrant:
                    item['sources'].append({
                        'id': f"SRC-{len(item['sources']) + 1:02d}",
                        'path': doc['path'],
                        'title': doc.get('title', doc['name']),
                        'tokens': doc.get('token_estimate', 0),
                    })
                    break
    
    return items


def estimate_total_effort(items: list) -> dict:
    """Estimate total project effort."""
    effort_hours = {
        'Low': 2,
        'Medium': 4,
        'High': 8,
    }
    
    total_hours = 0
    by_quadrant = {}
    by_priority = {1: 0, 2: 0, 3: 0}
    
    for item in items:
        if item['type'] == 'document':
            hours = effort_hours.get(item['effort'], 4)
            total_hours += hours
            
            quadrant = item.get('quadrant', 'Unknown')
            by_quadrant[quadrant] = by_quadrant.get(quadrant, 0) + hours
            
            priority = item.get('priority', 2)
            by_priority[priority] = by_priority.get(priority, 0) + hours
    
    return {
        'total_hours': total_hours,
        'by_quadrant': by_quadrant,
        'by_priority': by_priority,
        'estimated_days': total_hours / 6,  # 6 productive hours per day
    }


def generate_markdown(items: list, effort: dict, output_path: Path):
    """Generate WBS as Markdown."""
    lines = [
        '# Work Breakdown Structure',
        '',
        f'Generated: {datetime.now().isoformat()}',
        '',
        '## Project Summary',
        '',
        f'- **Total Items**: {len([i for i in items if i["type"] == "document"])} documents',
        f'- **Estimated Hours**: {effort["total_hours"]}',
        f'- **Estimated Days**: {effort["estimated_days"]:.1f}',
        '',
        '### Effort by Priority',
        '',
        '| Priority | Hours | Description |',
        '|----------|-------|-------------|',
        f'| P1 (Critical) | {effort["by_priority"].get(1, 0)} | Must have for launch |',
        f'| P2 (Important) | {effort["by_priority"].get(2, 0)} | Should have |',
        f'| P3 (Nice to Have) | {effort["by_priority"].get(3, 0)} | Can defer |',
        '',
        '### Effort by Quadrant',
        '',
        '| Quadrant | Hours |',
        '|----------|-------|',
    ]
    
    for quadrant, hours in sorted(effort['by_quadrant'].items()):
        lines.append(f'| {quadrant} | {hours} |')
    
    lines.extend([
        '',
        '## Work Items',
        '',
        '### Priority 1 (Critical)',
        '',
    ])
    
    # Group by priority
    for priority in [1, 2, 3]:
        if priority > 1:
            priority_names = {2: 'Important', 3: 'Nice to Have'}
            lines.extend([
                '',
                f'### Priority {priority} ({priority_names.get(priority, "")})',
                '',
            ])
        
        priority_items = [i for i in items if i.get('priority') == priority and i['type'] == 'document']
        
        if not priority_items:
            lines.append('*No items at this priority*')
            continue
        
        for item in priority_items:
            lines.extend([
                f'#### {item["id"]}: {item["path"]}',
                '',
                f'**Quadrant**: {item.get("quadrant", "Unknown")}',
                f'**Effort**: {item["effort"]}',
                f'**Status**: {item["status"]}',
                '',
            ])
            
            if item.get('dependencies'):
                lines.append(f'**Dependencies**: {", ".join(item["dependencies"])}')
                lines.append('')
            
            if item.get('sources'):
                lines.append('**Source References**:')
                for src in item['sources']:
                    lines.append(f'- [{src["id"]}]: {src["title"]} (~{src["tokens"]:,} tokens)')
                lines.append('')
            
            lines.extend([
                '**Content Requirements**:',
                '- [ ] [Requirement 1]',
                '- [ ] [Requirement 2]',
                '',
                '---',
                '',
            ])
    
    # Progress tracker
    lines.extend([
        '',
        '## Progress Tracker',
        '',
        '| ID | Document | Priority | Effort | Status |',
        '|-----|----------|----------|--------|--------|',
    ])
    
    for item in items:
        if item['type'] == 'document':
            lines.append(
                f'| {item["id"]} | {item["path"]} | P{item.get("priority", 2)} | {item["effort"]} | ⬜ Pending |'
            )
    
    lines.extend([
        '',
        '## Chunk Processing Order',
        '',
        'Process in this order to manage dependencies:',
        '',
    ])
    
    # Suggest processing order
    chunk_num = 1
    for priority in [1, 2, 3]:
        priority_items = [i for i in items if i.get('priority') == priority and i['type'] == 'document']
        if priority_items:
            lines.append(f'### Chunk {chunk_num}: Priority {priority} Items')
            lines.append('')
            for item in priority_items:
                lines.append(f'- [ ] {item["id"]}: {item["path"]}')
            lines.append('')
            chunk_num += 1
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"WBS written to {output_path}")




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
    parser = argparse.ArgumentParser(description='Generate work breakdown structure')
    parser.add_argument('--inventory', '-i', type=Path, required=True,
                        help='Path to inventory.json from analyze_docs.py')
    parser.add_argument('--output', '-o', type=Path, default=Path('wbs.md'),
                        help='Output WBS file')
    parser.add_argument('--target-structure', '-t', type=Path,
                        help='Optional YAML file defining target structure')
    
    args = parser.parse_args()

    _validate_path(str(args.output), {'.md', '.json'}, "output file")
    
    if not args.inventory.exists():
        print(f"Error: Inventory file {args.inventory} not found")
        return 1
    
    print(f"Loading inventory from {args.inventory}...")
    inventory = load_inventory(args.inventory)
    
    structure = DEFAULT_STRUCTURE
    if args.target_structure and args.target_structure.exists():
        import yaml
        with open(args.target_structure) as f:
            structure = yaml.safe_load(f)
    
    print("Generating WBS items...")
    items = generate_wbs_items(inventory, structure)
    
    effort = estimate_total_effort(items)
    
    print(f"Generated {len(items)} WBS items")
    print(f"Estimated effort: {effort['total_hours']} hours ({effort['estimated_days']:.1f} days)")
    
    generate_markdown(items, effort, args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
