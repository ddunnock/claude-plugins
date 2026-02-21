#!/usr/bin/env python3
"""
Stream Write - Initialize and write sections to markdown files with markers.

Usage:
    python stream_write.py init <filepath> --sections "section1,section2,..."
    python stream_write.py write <filepath> <section_id> <content>
    python stream_write.py write <filepath> <section_id> --file <content_file>

Examples:
    python stream_write.py init report.md --sections "intro,body,conclusion"
    python stream_write.py write report.md intro "# Introduction\n\nContent here..."
"""

import os
import argparse
import sys
import re
from datetime import datetime
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content.

    Returns (frontmatter_dict, remaining_content).
    """
    if not content.startswith('---'):
        return {}, content

    # Find closing ---
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return {}, content

    frontmatter_str = content[4:end_match.start() + 3]
    remaining = content[end_match.end() + 3:]

    # Simple YAML parsing for our specific format
    frontmatter = {}
    current_key = None
    sections = []

    for line in frontmatter_str.split('\n'):
        line = line.rstrip()
        if line.startswith('stream_plan:'):
            frontmatter['stream_plan'] = {}
        elif line.strip().startswith('sections:'):
            current_key = 'sections'
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


def generate_frontmatter(sections: list[str], created: str = None) -> str:
    """Generate YAML frontmatter for stream plan."""
    if created is None:
        created = datetime.now().isoformat()

    lines = [
        '---',
        'stream_plan:',
        '  sections:'
    ]

    for section_id in sections:
        lines.append(f'    - id: {section_id}')
        lines.append('      status: pending')

    lines.append(f'  created: {created}')
    lines.append('---')

    return '\n'.join(lines)


def update_frontmatter(content: str, section_id: str, new_status: str) -> str:
    """Update a section's status in the frontmatter."""
    lines = content.split('\n')
    in_target_section = False

    for i, line in enumerate(lines):
        if f'- id: {section_id}' in line:
            in_target_section = True
        elif in_target_section and 'status:' in line:
            # Update status
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'status: {new_status}'
            break
        elif in_target_section and line.strip().startswith('- id:'):
            # Moved to next section without finding status
            break

    return '\n'.join(lines)


def init_file(filepath: str, sections: list[str]) -> bool:
    """Initialize a new streaming output file.

    Args:
        filepath: Path to the output file
        sections: List of section IDs

    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)

    # Check if file exists
    if path.exists():
        content = path.read_text()
        frontmatter, _ = parse_frontmatter(content)

        if 'stream_plan' in frontmatter:
            print(f"File already initialized with stream plan: {filepath}")
            print("Use --force to reinitialize (will lose existing content)")
            return False

    # Generate content
    frontmatter = generate_frontmatter(sections)

    # Create initial content
    content = f"""{frontmatter}

# Document

<!-- Streamed content below. Do not edit markers manually. -->

"""

    # Write file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

    print(f"Initialized: {filepath}")
    print(f"Sections planned: {', '.join(sections)}")
    print(f"\nNext: Run 'stream.write {sections[0]}' to write the first section")

    return True


def write_section(filepath: str, section_id: str, content: str) -> bool:
    """Write a section to the file with markers.

    Args:
        filepath: Path to the output file
        section_id: ID of the section to write
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File not found: {filepath}")
        print("Run 'stream.init' first to create the file.")
        return False

    file_content = path.read_text()
    frontmatter, body = parse_frontmatter(file_content)

    if 'stream_plan' not in frontmatter:
        print(f"Error: File not initialized with stream plan: {filepath}")
        return False

    # Check section exists in plan
    sections = frontmatter['stream_plan'].get('sections', [])
    section = next((s for s in sections if s['id'] == section_id), None)

    if not section:
        print(f"Error: Section '{section_id}' not in plan.")
        print(f"Available sections: {', '.join(s['id'] for s in sections)}")
        return False

    if section['status'] == 'completed':
        print(f"Warning: Section '{section_id}' already completed.")
        print("To rewrite, manually delete the section markers first.")
        return False

    # Check for incomplete marker (partial write from previous attempt)
    start_marker = f'<!-- SECTION_START: {section_id} -->'
    end_marker = f'<!-- SECTION_END: {section_id} -->'

    if start_marker in file_content and end_marker not in file_content:
        print(f"Error: Found incomplete section '{section_id}' (no end marker).")
        print("Delete the partial content first, then retry.")
        return False

    # Build section content with markers
    section_content = f"""
{start_marker}
{content.strip()}
{end_marker}
"""

    # Append to file
    new_content = file_content.rstrip() + '\n' + section_content

    # Update frontmatter status
    new_content = update_frontmatter(new_content, section_id, 'completed')

    # Write file
    path.write_text(new_content)

    print(f"Written: {section_id}")

    # Find next section
    current_idx = next(i for i, s in enumerate(sections) if s['id'] == section_id)
    if current_idx + 1 < len(sections):
        next_section = sections[current_idx + 1]['id']
        print(f"Next: Run 'stream.write {next_section}'")
    else:
        print("All sections written! Run 'stream.finalize' to complete.")

    return True



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
        description='Stream content to markdown files with section markers'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new streaming file')
    init_parser.add_argument('filepath', help='Path to output file')
    init_parser.add_argument(
        '--sections', '-s',
        required=True,
        help='Comma-separated list of section IDs'
    )
    init_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force reinitialization'
    )

    # Write command
    write_parser = subparsers.add_parser('write', help='Write a section')
    write_parser.add_argument('filepath', help='Path to output file')
    write_parser.add_argument('section_id', help='Section ID to write')
    write_parser.add_argument('content', nargs='?', help='Content to write')
    write_parser.add_argument(
        '--file', '-f',
        help='Read content from file instead of argument'
    )

    args = parser.parse_args()

    args.file = _validate_path(args.file, {'.json'}, "file")

    if args.command == 'init':
        sections = [s.strip() for s in args.sections.split(',')]
        success = init_file(args.filepath, sections)
        sys.exit(0 if success else 1)

    elif args.command == 'write':
        # Get content
        if args.file:
            content = Path(args.file).read_text()
        elif args.content:
            content = args.content
        else:
            # Read from stdin
            print("Reading content from stdin (Ctrl+D to end):")
            content = sys.stdin.read()

        success = write_section(args.filepath, args.section_id, content)
        sys.exit(0 if success else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
