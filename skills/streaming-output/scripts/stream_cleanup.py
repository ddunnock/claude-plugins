#!/usr/bin/env python3
"""
Stream Cleanup - Finalize streaming files by removing markers.

Usage:
    python stream_cleanup.py <filepath>
    python stream_cleanup.py <filepath> --output <output_filepath>
    python stream_cleanup.py <filepath> --in-place
    python stream_cleanup.py <filepath> --check

Examples:
    python stream_cleanup.py report.md                    # Output to stdout
    python stream_cleanup.py report.md -o final.md        # Output to file
    python stream_cleanup.py report.md --in-place         # Modify original
    python stream_cleanup.py report.md --check            # Validate only
"""

import os
import argparse
import sys
import re
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

    if sections and 'stream_plan' in frontmatter:
        frontmatter['stream_plan']['sections'] = sections

    return frontmatter, remaining


def check_completion(content: str, sections: list[dict]) -> tuple[bool, list[str]]:
    """Check if all sections are complete.

    Returns:
        (is_complete, list of issues)
    """
    issues = []

    for section in sections:
        section_id = section['id']
        start_marker = f'<!-- SECTION_START: {section_id} -->'
        end_marker = f'<!-- SECTION_END: {section_id} -->'

        has_start = start_marker in content
        has_end = end_marker in content

        if not has_start and not has_end:
            issues.append(f"Section '{section_id}' not written")
        elif has_start and not has_end:
            issues.append(f"Section '{section_id}' incomplete (no end marker)")

    return len(issues) == 0, issues


def cleanup_content(content: str) -> str:
    """Remove stream markers and frontmatter from content.

    Removes:
    - YAML frontmatter with stream_plan
    - SECTION_START markers
    - SECTION_END markers
    - Extra whitespace from marker removal
    """
    # Remove frontmatter if it contains stream_plan
    frontmatter, body = parse_frontmatter(content)

    if 'stream_plan' in frontmatter:
        content = body

    # Remove section markers
    content = re.sub(r'<!-- SECTION_START: [^>]+ -->\n?', '', content)
    content = re.sub(r'\n?<!-- SECTION_END: [^>]+ -->', '', content)

    # Clean up excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    # Remove leading/trailing whitespace but keep structure
    content = content.strip() + '\n'

    return content


def finalize(filepath: str, output_path: str = None, in_place: bool = False, check_only: bool = False) -> bool:
    """Finalize a streaming file.

    Args:
        filepath: Path to input file
        output_path: Path to output file (None for stdout)
        in_place: Modify original file
        check_only: Only validate, don't produce output

    Returns:
        True if successful, False otherwise
    """
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return False

    content = path.read_text()
    frontmatter, _ = parse_frontmatter(content)

    if 'stream_plan' not in frontmatter:
        print(f"Error: File not initialized with stream plan: {filepath}", file=sys.stderr)
        return False

    sections = frontmatter['stream_plan'].get('sections', [])

    # Check completion
    is_complete, issues = check_completion(content, sections)

    if not is_complete:
        print("Error: Cannot finalize - incomplete sections:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return False

    if check_only:
        print("Validation passed: All sections complete")
        print(f"Sections: {', '.join(s['id'] for s in sections)}")
        return True

    # Clean up content
    cleaned = cleanup_content(content)

    # Output
    if in_place:
        path.write_text(cleaned)
        print(f"Finalized (in-place): {filepath}")
    elif output_path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(cleaned)
        print(f"Finalized: {output_path}")
    else:
        # Output to stdout
        print(cleaned)

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
        description='Finalize streaming files by removing markers'
    )
    parser.add_argument('filepath', help='Path to streaming file')
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--in-place', '-i',
        action='store_true',
        help='Modify the original file'
    )
    parser.add_argument(
        '--check', '-c',
        action='store_true',
        help='Only check completion, do not produce output'
    )

    args = parser.parse_args()

    args.filepath = _validate_path(args.filepath, {'.md', '.txt', '.html'}, "filepath")
    if args.output:
        args.output = _validate_path(args.output, {'.md', '.txt', '.html'}, "output file")

    if args.in_place and args.output:
        print("Error: Cannot use both --in-place and --output", file=sys.stderr)
        sys.exit(1)

    success = finalize(
        args.filepath,
        output_path=args.output,
        in_place=args.in_place,
        check_only=args.check
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
