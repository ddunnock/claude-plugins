#!/usr/bin/env python3
"""
Stream Repair - Fix corrupted or partial sections in streaming files.

Usage:
    python stream_repair.py <filepath> <section-id>
    python stream_repair.py <filepath> <section-id> --strategy remove
    python stream_repair.py <filepath> <section-id> --strategy backup
    python stream_repair.py <filepath> <section-id> --dry-run

Strategies:
    remove (default): Remove partial content, reset section to pending
    complete: Attempt to add missing END marker (use with caution)
    backup: Create backup before repair, then remove

Examples:
    python stream_repair.py report.md analysis
    python stream_repair.py report.md analysis --strategy backup
    python stream_repair.py report.md analysis --dry-run
"""

import os
import argparse
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime


def parse_frontmatter(content: str) -> tuple[dict, str, int]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter dict, body content, frontmatter end position)
    """
    if not content.startswith('---'):
        return {}, content, 0

    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return {}, content, 0

    frontmatter_end = end_match.end() + 3
    frontmatter_str = content[4:end_match.start() + 3]
    remaining = content[frontmatter_end:]

    frontmatter = {}
    sections = []

    for line in frontmatter_str.split('\n'):
        line = line.rstrip()
        if line.startswith('stream_plan:'):
            frontmatter['stream_plan'] = {}
        elif line.strip().startswith('- id:'):
            section_id = line.split(':', 1)[1].strip()
            sections.append({'id': section_id, 'status': 'pending', 'hash': None})
        elif line.strip().startswith('status:') and sections:
            sections[-1]['status'] = line.split(':', 1)[1].strip()
        elif line.strip().startswith('hash:') and sections:
            hash_val = line.split(':', 1)[1].strip()
            sections[-1]['hash'] = None if hash_val == 'null' else hash_val
        elif line.strip().startswith('created:'):
            if 'stream_plan' in frontmatter:
                frontmatter['stream_plan']['created'] = line.split(':', 1)[1].strip()

    if sections and 'stream_plan' in frontmatter:
        frontmatter['stream_plan']['sections'] = sections

    return frontmatter, remaining, frontmatter_end


def find_section_markers(content: str, section_id: str) -> dict:
    """Find section markers and their positions in content.

    Returns:
        Dictionary with marker info: has_start, has_end, start_pos, end_pos, etc.
    """
    # Match both old format and new format with hash
    start_pattern = rf'<!-- SECTION_START: {re.escape(section_id)}(?: \| hash:[a-f0-9]+)? -->'
    end_pattern = rf'<!-- SECTION_END: {re.escape(section_id)}(?: \| hash:[a-f0-9]+)? -->'

    start_match = re.search(start_pattern, content)
    end_match = re.search(end_pattern, content)

    result = {
        'has_start': start_match is not None,
        'has_end': end_match is not None,
        'start_pos': start_match.start() if start_match else None,
        'start_end_pos': start_match.end() if start_match else None,
        'end_pos': end_match.start() if end_match else None,
        'end_end_pos': end_match.end() if end_match else None,
    }

    if start_match and end_match:
        result['content'] = content[start_match.end():end_match.start()]
        result['full_section'] = content[start_match.start():end_match.end()]
    elif start_match:
        # Find where partial content ends (next section start or EOF)
        next_start = re.search(r'<!-- SECTION_START:', content[start_match.end():])
        if next_start:
            result['partial_content'] = content[start_match.end():start_match.end() + next_start.start()]
            result['partial_end_pos'] = start_match.end() + next_start.start()
        else:
            result['partial_content'] = content[start_match.end():]
            result['partial_end_pos'] = len(content)

    return result


def repair_section(filepath: str, section_id: str, strategy: str = 'remove',
                   dry_run: bool = False, preserve_context: bool = True) -> dict:
    """Repair a corrupted section.

    Args:
        filepath: Path to the streaming file
        section_id: ID of the section to repair
        strategy: Repair strategy (remove, complete, backup)
        dry_run: If True, don't make changes, just report what would happen
        preserve_context: If True, save incomplete content to .context file for resume

    Returns:
        Dictionary with repair results
    """
    path = Path(filepath)

    if not path.exists():
        return {'error': f'File not found: {filepath}', 'success': False}

    content = path.read_text()
    frontmatter, body, fm_end_pos = parse_frontmatter(content)

    if 'stream_plan' not in frontmatter:
        return {'error': 'File not initialized with stream plan', 'success': False}

    # Check if section exists in plan
    sections = frontmatter['stream_plan'].get('sections', [])
    section_exists = any(s['id'] == section_id for s in sections)

    if not section_exists:
        return {'error': f'Section "{section_id}" not found in plan', 'success': False}

    # Find markers
    markers = find_section_markers(content, section_id)

    # Determine issue type
    if markers['has_start'] and markers['has_end']:
        issue = 'complete'  # Section appears complete, maybe hash mismatch
    elif markers['has_start'] and not markers['has_end']:
        issue = 'orphaned_start'
    elif not markers['has_start'] and not markers['has_end']:
        issue = 'not_written'
    else:
        issue = 'orphaned_end'  # Unusual case

    result = {
        'success': True,
        'section_id': section_id,
        'issue': issue,
        'strategy': strategy,
        'dry_run': dry_run,
        'changes': []
    }

    if issue == 'not_written':
        result['message'] = f'Section "{section_id}" has not been written yet. No repair needed.'
        result['action'] = 'none'
        return result

    if issue == 'complete' and strategy != 'remove':
        result['message'] = f'Section "{section_id}" appears complete. Use --strategy remove to force reset.'
        result['action'] = 'none'
        return result

    # Perform repair based on strategy
    new_content = content

    if strategy == 'backup' or (strategy == 'remove' and not dry_run):
        # Create backup
        if not dry_run:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_path = path.with_suffix(f'.backup.{timestamp}{path.suffix}')
            shutil.copy2(path, backup_path)
            result['backup_path'] = str(backup_path)
            result['changes'].append(f'Created backup: {backup_path}')

    if strategy in ('remove', 'backup'):
        # Remove the section content
        if issue == 'orphaned_start':
            # Remove from SECTION_START to end of partial content
            start_pos = markers['start_pos']
            end_pos = markers['partial_end_pos']
            removed_content = content[start_pos:end_pos]
            
            # Extract just the content (without the START marker) for context
            partial_content = markers.get('partial_content', '')
            
            # Preserve incomplete content for resume context
            if preserve_context and partial_content and not dry_run:
                context_path = path.with_suffix(f'.{section_id}.context')
                context_path.write_text(partial_content.strip())
                result['context_path'] = str(context_path)
                result['changes'].append(f'Preserved incomplete content to: {context_path}')
            
            new_content = content[:start_pos] + content[end_pos:]

            result['removed_chars'] = len(removed_content)
            result['changes'].append(f'Removed {len(removed_content)} characters of partial content')

        elif issue == 'complete':
            # Remove entire section including markers
            start_pos = markers['start_pos']
            end_pos = markers['end_end_pos']
            removed_content = content[start_pos:end_pos]
            new_content = content[:start_pos] + content[end_pos:]

            result['removed_chars'] = len(removed_content)
            result['changes'].append(f'Removed complete section ({len(removed_content)} characters)')

        # Update frontmatter to set section status to pending
        for section in sections:
            if section['id'] == section_id:
                section['status'] = 'pending'
                section['hash'] = None
                break

        # Rebuild frontmatter
        new_frontmatter = rebuild_frontmatter(frontmatter)

        # Get body content (after frontmatter)
        if fm_end_pos > 0:
            new_body = new_content[fm_end_pos:]
        else:
            new_body = new_content

        new_content = new_frontmatter + new_body
        result['changes'].append(f'Reset section "{section_id}" status to pending')

    elif strategy == 'complete':
        # Try to add missing END marker
        if issue == 'orphaned_start':
            # Add END marker at the end of partial content
            end_marker = f'\n<!-- SECTION_END: {section_id} -->\n'
            insert_pos = markers['partial_end_pos']
            new_content = content[:insert_pos] + end_marker + content[insert_pos:]

            result['changes'].append(f'Added SECTION_END marker for "{section_id}"')
            result['warning'] = 'Content may be incomplete. Review before finalizing.'
        else:
            result['error'] = f'Cannot complete: issue type is "{issue}"'
            result['success'] = False
            return result

    # Write changes
    if not dry_run and result['success']:
        path.write_text(new_content)
        result['changes'].append('Wrote changes to file')

    result['action'] = strategy
    result['message'] = f'Section "{section_id}" repaired successfully'

    return result


def rebuild_frontmatter(frontmatter: dict) -> str:
    """Rebuild YAML frontmatter string from dict."""
    lines = ['---']

    if 'stream_plan' in frontmatter:
        plan = frontmatter['stream_plan']
        lines.append('stream_plan:')

        if 'version' in plan:
            lines.append(f"  version: \"{plan['version']}\"")

        if 'sections' in plan:
            lines.append('  sections:')
            for section in plan['sections']:
                lines.append(f"    - id: {section['id']}")
                lines.append(f"      status: {section['status']}")
                hash_val = section.get('hash')
                lines.append(f"      hash: {hash_val if hash_val else 'null'}")

        if 'created' in plan:
            lines.append(f"  created: {plan['created']}")

        # Add last_modified
        lines.append(f"  last_modified: {datetime.now().isoformat()}")

    lines.append('---\n')
    return '\n'.join(lines)


def print_result(result: dict):
    """Print human-readable repair result."""
    print(f"\nRepair Report: {result.get('section_id', 'unknown')}")
    print("=" * 50)

    if 'error' in result:
        print(f"\nError: {result['error']}")
        return

    print(f"\nSection: {result['section_id']}")
    print(f"Issue: {result['issue']}")
    print(f"Strategy: {result['strategy']}")

    if result.get('dry_run'):
        print("\n[DRY RUN - No changes made]")

    if result.get('changes'):
        print("\nChanges:")
        for change in result['changes']:
            print(f"  - {change}")

    if result.get('backup_path'):
        print(f"\nBackup created: {result['backup_path']}")

    if result.get('warning'):
        print(f"\n⚠️  Warning: {result['warning']}")

    if result.get('message'):
        print(f"\n{result['message']}")

    # Show context file info for resume
    if result.get('context_path'):
        print(f"\n📝 Incomplete content preserved for context:")
        print(f"   {result['context_path']}")
        print(f"\n   To view before resuming:")
        print(f"   cat {result['context_path']}")
        print(f"\n   Continue from where you left off - don't start over!")

    if result['action'] != 'none':
        print(f"\nReady to continue: /stream.write {result['section_id']}")
        if result.get('context_path'):
            print(f"(Review the .context file first to continue coherently)")



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
        description='Fix corrupted or partial sections in streaming files'
    )
    parser.add_argument('filepath', help='Path to streaming file')
    parser.add_argument('section_id', help='ID of section to repair')
    parser.add_argument(
        '--strategy', '-s',
        choices=['remove', 'complete', 'backup'],
        default='remove',
        help='Repair strategy (default: remove)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    args.filepath = _validate_path(args.filepath, {'.md', '.txt', '.html'}, "filepath")

    result = repair_section(
        args.filepath,
        args.section_id,
        strategy=args.strategy,
        dry_run=args.dry_run
    )

    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_result(result)

    # Exit codes
    if not result.get('success', False):
        sys.exit(1)
    elif result.get('action') == 'none':
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
