#!/usr/bin/env python3
"""
Stream Status - Show progress and detect resume point for streaming files.

Usage:
    python stream_status.py <filepath>
    python stream_status.py <filepath> --resume
    python stream_status.py <filepath> --json

Examples:
    python stream_status.py report.md
    python stream_status.py report.md --resume  # Just output next section ID
"""

import argparse
import sys
import re
import json
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content

    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return {}, content

    frontmatter_str = content[4:end_match.start() + 3]
    remaining = content[end_match.end() + 3:]

    frontmatter = {}
    sections = []

    for line in frontmatter_str.split('\n'):
        line = line.rstrip()
        if line.startswith('stream_plan:'):
            frontmatter['stream_plan'] = {}
        elif line.strip().startswith('- id:'):
            section_id = line.split(':', 1)[1].strip()
            sections.append({'id': section_id, 'status': 'pending'})
        elif line.strip().startswith('status:') and sections:
            sections[-1]['status'] = line.split(':', 1)[1].strip()
        elif line.strip().startswith('created:'):
            if 'stream_plan' in frontmatter:
                frontmatter['stream_plan']['created'] = line.split(':', 1)[1].strip()

    if sections and 'stream_plan' in frontmatter:
        frontmatter['stream_plan']['sections'] = sections

    return frontmatter, remaining


def check_markers(content: str, sections: list[dict]) -> list[dict]:
    """Check actual markers in file content and update section status.

    This handles cases where frontmatter may be out of sync with actual content.
    """
    result = []

    for section in sections:
        section_id = section['id']
        start_marker = f'<!-- SECTION_START: {section_id} -->'
        end_marker = f'<!-- SECTION_END: {section_id} -->'

        has_start = start_marker in content
        has_end = end_marker in content

        if has_start and has_end:
            status = 'completed'
        elif has_start and not has_end:
            status = 'incomplete'  # Partial write, needs recovery
        else:
            status = 'pending'

        result.append({
            'id': section_id,
            'status': status,
            'frontmatter_status': section.get('status', 'pending')
        })

    return result


def find_context_files(filepath: str, sections: list[dict]) -> dict:
    """Find any .context files for sections.
    
    Returns:
        Dictionary mapping section_id to context file path
    """
    path = Path(filepath)
    context_files = {}
    
    for section in sections:
        section_id = section['id']
        context_path = path.with_suffix(f'.{section_id}.context')
        if context_path.exists():
            context_files[section_id] = {
                'path': str(context_path),
                'size': context_path.stat().st_size,
                'preview': context_path.read_text()[-500:] if context_path.stat().st_size > 0 else ''
            }
    
    return context_files


def get_status(filepath: str) -> dict:
    """Get comprehensive status of a streaming file.

    Returns:
        Dictionary with status information
    """
    path = Path(filepath)

    if not path.exists():
        return {
            'error': f'File not found: {filepath}',
            'exists': False
        }

    content = path.read_text()
    frontmatter, body = parse_frontmatter(content)

    if 'stream_plan' not in frontmatter:
        return {
            'error': 'File not initialized with stream plan',
            'exists': True,
            'initialized': False
        }

    sections = frontmatter['stream_plan'].get('sections', [])
    sections_with_markers = check_markers(content, sections)
    
    # Check for context files (preserved incomplete content)
    context_files = find_context_files(filepath, sections)

    # Calculate stats
    completed = sum(1 for s in sections_with_markers if s['status'] == 'completed')
    incomplete = sum(1 for s in sections_with_markers if s['status'] == 'incomplete')
    pending = sum(1 for s in sections_with_markers if s['status'] == 'pending')
    total = len(sections_with_markers)

    # Find resume point
    resume_section = None
    for section in sections_with_markers:
        if section['status'] == 'incomplete':
            resume_section = section['id']
            break
        elif section['status'] == 'pending':
            resume_section = section['id']
            break

    return {
        'exists': True,
        'initialized': True,
        'filepath': str(path.absolute()),
        'sections': sections_with_markers,
        'stats': {
            'completed': completed,
            'incomplete': incomplete,
            'pending': pending,
            'total': total,
            'progress_percent': round(completed / total * 100) if total > 0 else 0
        },
        'resume_section': resume_section,
        'has_incomplete': incomplete > 0,
        'is_complete': pending == 0 and incomplete == 0,
        'created': frontmatter['stream_plan'].get('created'),
        'context_files': context_files
    }


def print_status(status: dict):
    """Print human-readable status."""
    if 'error' in status:
        print(f"Error: {status['error']}")
        return

    print(f"\nStream Status: {status['filepath']}")
    print("=" * 50)

    print("\nSections:")
    for section in status['sections']:
        if section['status'] == 'completed':
            marker = '[x]'
        elif section['status'] == 'incomplete':
            marker = '[!]'  # Needs attention
        else:
            marker = '[ ]'

        suffix = ''
        if section['id'] == status['resume_section']:
            suffix = ' <- RESUME HERE'
        if section['status'] == 'incomplete':
            suffix = ' <- INCOMPLETE (needs recovery)'

        print(f"  {marker} {section['id']}{suffix}")

    stats = status['stats']
    print(f"\nProgress: {stats['completed']}/{stats['total']} sections ({stats['progress_percent']}%)")

    if status['has_incomplete']:
        print("\n!! Found incomplete section (partial write).")
        print("   Delete the partial content, then resume.")

    # Show context files if they exist
    context_files = status.get('context_files', {})
    if context_files:
        print("\n📝 Context files (from previous incomplete writes):")
        for section_id, info in context_files.items():
            print(f"   {section_id}: {info['path']} ({info['size']} bytes)")
            if info.get('preview'):
                print(f"\n   Preview (last 500 chars):")
                for line in info['preview'].splitlines()[-10:]:
                    print(f"   | {line[:80]}")
        print("\n   ⚠️  Review context before writing - continue where you left off!")

    if status['is_complete']:
        print("\nAll sections complete! Run 'stream.finalize' to finish.")
    elif status['resume_section']:
        print(f"\nNext section: {status['resume_section']}")
        if status['resume_section'] in context_files:
            print(f"   (Has context file - continue from where interrupted, don't restart)")


def main():
    parser = argparse.ArgumentParser(
        description='Show status and resume point for streaming files'
    )
    parser.add_argument('filepath', help='Path to streaming file')
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Only output the next section ID to resume'
    )
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    status = get_status(args.filepath)

    if args.resume:
        if 'error' in status:
            print(f"Error: {status['error']}", file=sys.stderr)
            sys.exit(1)

        if status['resume_section']:
            print(status['resume_section'])
        else:
            print("COMPLETE")
        sys.exit(0)

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print_status(status)

    # Exit codes
    if 'error' in status:
        sys.exit(1)
    elif status.get('has_incomplete'):
        sys.exit(2)  # Needs recovery
    elif status.get('is_complete'):
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
