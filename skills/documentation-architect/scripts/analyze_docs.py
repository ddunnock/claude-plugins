#!/usr/bin/env python3
"""
Analyze documentation structure and content.

Usage:
    python analyze_docs.py <source-dir> [--output inventory.json] [--format json|markdown]
"""

import argparse
import json
import os
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
import sys


@dataclass
class DocumentInfo:
    """Information about a single document."""
    path: str
    name: str
    extension: str
    size_bytes: int
    line_count: int
    word_count: int
    token_estimate: int
    has_frontmatter: bool
    title: Optional[str]
    headings: list
    links_internal: int
    links_external: int
    code_blocks: int
    diataxis_quadrant: str  # Tutorial, How-To, Reference, Explanation, Mixed, Unknown
    last_modified: str


def estimate_tokens(text: str) -> int:
    """Rough token estimate (words * 1.3)."""
    words = len(text.split())
    return int(words * 1.3)


def detect_quadrant(content: str, filename: str) -> str:
    """Attempt to detect Diátaxis quadrant from content patterns."""
    content_lower = content.lower()
    filename_lower = filename.lower()
    
    # Check filename patterns
    if any(x in filename_lower for x in ['tutorial', 'lesson', 'learn', 'quickstart', 'getting-started']):
        return 'Tutorial'
    if any(x in filename_lower for x in ['how-to', 'howto', 'guide', 'cookbook']):
        return 'How-To'
    if any(x in filename_lower for x in ['reference', 'api', 'spec', 'schema', 'config']):
        return 'Reference'
    if any(x in filename_lower for x in ['explanation', 'concept', 'architecture', 'why', 'about']):
        return 'Explanation'
    
    # Check content patterns
    tutorial_signals = ['you will learn', 'in this tutorial', 'step 1', 'let\'s start', 'by the end']
    howto_signals = ['how to', 'this guide shows', 'to accomplish', 'steps:', 'prerequisites:']
    reference_signals = ['parameters:', 'returns:', 'type:', 'default:', 'required:']
    explanation_signals = ['why', 'because', 'the reason', 'this means', 'in other words']
    
    scores = {
        'Tutorial': sum(1 for s in tutorial_signals if s in content_lower),
        'How-To': sum(1 for s in howto_signals if s in content_lower),
        'Reference': sum(1 for s in reference_signals if s in content_lower),
        'Explanation': sum(1 for s in explanation_signals if s in content_lower),
    }
    
    max_score = max(scores.values())
    if max_score == 0:
        return 'Unknown'
    
    top_quadrants = [q for q, s in scores.items() if s == max_score]
    if len(top_quadrants) > 1:
        return 'Mixed'
    
    return top_quadrants[0]


def extract_title(content: str) -> Optional[str]:
    """Extract title from first heading or frontmatter."""
    # Check for frontmatter title
    fm_match = re.search(r'^---\s*\n.*?title:\s*["\']?([^"\'\n]+)', content, re.DOTALL)
    if fm_match:
        return fm_match.group(1).strip()
    
    # Check for first heading
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    
    return None


def extract_headings(content: str) -> list:
    """Extract all headings with their levels."""
    headings = []
    for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append({'level': level, 'text': text})
    return headings


def has_frontmatter(content: str) -> bool:
    """Check if document has YAML frontmatter."""
    return content.strip().startswith('---')


def count_links(content: str) -> tuple:
    """Count internal and external links."""
    # Markdown links
    all_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    
    internal = 0
    external = 0
    
    for _, url in all_links:
        if url.startswith(('http://', 'https://', '//')):
            external += 1
        else:
            internal += 1
    
    return internal, external


def count_code_blocks(content: str) -> int:
    """Count fenced code blocks."""
    return len(re.findall(r'```', content)) // 2


def analyze_document(filepath: Path) -> Optional[DocumentInfo]:
    """Analyze a single document."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None
    
    lines = content.split('\n')
    words = content.split()
    internal_links, external_links = count_links(content)
    
    stat = filepath.stat()
    
    return DocumentInfo(
        path=str(filepath),
        name=filepath.name,
        extension=filepath.suffix,
        size_bytes=stat.st_size,
        line_count=len(lines),
        word_count=len(words),
        token_estimate=estimate_tokens(content),
        has_frontmatter=has_frontmatter(content),
        title=extract_title(content),
        headings=extract_headings(content),
        links_internal=internal_links,
        links_external=external_links,
        code_blocks=count_code_blocks(content),
        diataxis_quadrant=detect_quadrant(content, filepath.name),
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


def analyze_directory(source_dir: Path, extensions: list = None) -> list:
    """Analyze all documents in a directory."""
    if extensions is None:
        extensions = ['.md', '.mdx', '.rst', '.txt', '.html']
    
    documents = []
    
    for ext in extensions:
        for filepath in source_dir.rglob(f'*{ext}'):
            # Skip common non-doc directories
            if any(x in str(filepath) for x in ['node_modules', '.git', '__pycache__', 'venv']):
                continue
            
            doc_info = analyze_document(filepath)
            if doc_info:
                documents.append(doc_info)
    
    return documents


def generate_summary(documents: list) -> dict:
    """Generate summary statistics."""
    if not documents:
        return {'error': 'No documents found'}
    
    quadrant_counts = {}
    total_tokens = 0
    total_words = 0
    
    for doc in documents:
        quadrant = doc.diataxis_quadrant
        quadrant_counts[quadrant] = quadrant_counts.get(quadrant, 0) + 1
        total_tokens += doc.token_estimate
        total_words += doc.word_count
    
    return {
        'total_documents': len(documents),
        'total_words': total_words,
        'total_tokens_estimate': total_tokens,
        'quadrant_distribution': quadrant_counts,
        'extensions': list(set(d.extension for d in documents)),
        'documents_with_frontmatter': sum(1 for d in documents if d.has_frontmatter),
    }


def output_json(documents: list, summary: dict, output_path: Path):
    """Output results as JSON."""
    result = {
        'generated_at': datetime.now().isoformat(),
        'summary': summary,
        'documents': [asdict(d) for d in documents],
    }
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"JSON output written to {output_path}")


def output_markdown(documents: list, summary: dict, output_path: Path):
    """Output results as Markdown."""
    lines = [
        '# Documentation Inventory',
        '',
        f'Generated: {datetime.now().isoformat()}',
        '',
        '## Summary',
        '',
        f'- **Total Documents**: {summary["total_documents"]}',
        f'- **Total Words**: {summary["total_words"]:,}',
        f'- **Estimated Tokens**: {summary["total_tokens_estimate"]:,}',
        f'- **Documents with Frontmatter**: {summary["documents_with_frontmatter"]}',
        '',
        '### Diátaxis Distribution',
        '',
        '| Quadrant | Count |',
        '|----------|-------|',
    ]
    
    for quadrant, count in sorted(summary.get('quadrant_distribution', {}).items()):
        lines.append(f'| {quadrant} | {count} |')
    
    lines.extend([
        '',
        '## Documents',
        '',
        '| Path | Title | Quadrant | Tokens | Status |',
        '|------|-------|----------|--------|--------|',
    ])
    
    for doc in sorted(documents, key=lambda d: d.path):
        title = doc.title or doc.name
        if len(title) > 40:
            title = title[:37] + '...'
        lines.append(
            f'| {doc.path} | {title} | {doc.diataxis_quadrant} | ~{doc.token_estimate:,} | Pending |'
        )
    
    lines.extend([
        '',
        '## Next Steps',
        '',
        '- [ ] Review quadrant classifications',
        '- [ ] Identify mixed-content documents for splitting',
        '- [ ] Plan processing order based on dependencies',
        '- [ ] Begin chunk-by-chunk processing',
    ])
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Markdown output written to {output_path}")




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
    parser = argparse.ArgumentParser(description='Analyze documentation structure')
    parser.add_argument('source_dir', type=Path, help='Directory containing documentation')
    parser.add_argument('--output', '-o', type=Path, default=Path('inventory.json'),
                        help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='json',
                        help='Output format')
    
    args = parser.parse_args()

    _validate_path(str(args.output), {'.md', '.json'}, "output file")
    
    if not args.source_dir.exists():
        print(f"Error: Directory {args.source_dir} does not exist")
        return 1
    
    print(f"Analyzing documentation in {args.source_dir}...")
    documents = analyze_directory(args.source_dir)
    
    if not documents:
        print("No documentation files found.")
        return 1
    
    print(f"Found {len(documents)} documents")
    summary = generate_summary(documents)
    
    if args.format == 'json':
        output_json(documents, summary, args.output)
    else:
        if not args.output.suffix == '.md':
            args.output = args.output.with_suffix('.md')
        output_markdown(documents, summary, args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())
