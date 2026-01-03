#!/usr/bin/env python3
"""
Validate documentation quality and completeness.

Usage:
    python validate_docs.py <docs-dir> [--output report.md] [--strict]
"""

import argparse
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ValidationIssue:
    """A single validation issue."""
    path: str
    severity: str  # error, warning, info
    category: str
    message: str
    line: Optional[int] = None


@dataclass  
class DocumentValidation:
    """Validation results for a single document."""
    path: str
    title: Optional[str]
    quadrant: str
    issues: list
    quality_score: int
    passed: bool


def check_frontmatter(content: str, filepath: Path) -> list:
    """Check frontmatter validity."""
    issues = []
    
    if not content.strip().startswith('---'):
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='frontmatter',
            message='Missing YAML frontmatter'
        ))
        return issues
    
    # Check for closing frontmatter
    fm_end = content.find('---', 3)
    if fm_end == -1:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='error',
            category='frontmatter',
            message='Unclosed frontmatter (missing closing ---)'
        ))
    
    return issues


def check_headings(content: str, filepath: Path) -> list:
    """Check heading structure."""
    issues = []
    headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
    
    if not headings:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='structure',
            message='No headings found'
        ))
        return issues
    
    # Check for H1
    h1_count = sum(1 for h, _ in headings if len(h) == 1)
    if h1_count == 0:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='structure',
            message='No H1 heading (document title)'
        ))
    elif h1_count > 1:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='structure',
            message=f'Multiple H1 headings ({h1_count}) - should have only one'
        ))
    
    # Check heading hierarchy
    prev_level = 0
    for i, (hashes, text) in enumerate(headings):
        level = len(hashes)
        if level > prev_level + 1 and prev_level > 0:
            issues.append(ValidationIssue(
                path=str(filepath),
                severity='warning',
                category='structure',
                message=f'Heading level skip: H{prev_level} to H{level} ("{text}")'
            ))
        prev_level = level
    
    return issues


def check_links(content: str, filepath: Path, docs_root: Path) -> list:
    """Check for broken links."""
    issues = []
    
    # Find all markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    
    for link_text, url in links:
        # Skip external links and anchors
        if url.startswith(('http://', 'https://', '//', '#', 'mailto:')):
            continue
        
        # Remove anchor from internal links
        url_path = url.split('#')[0]
        if not url_path:
            continue
        
        # Resolve relative path
        if url_path.startswith('/'):
            target = docs_root / url_path.lstrip('/')
        else:
            target = filepath.parent / url_path
        
        # Check if target exists
        if not target.exists():
            # Try with .md extension
            if not target.with_suffix('.md').exists():
                issues.append(ValidationIssue(
                    path=str(filepath),
                    severity='error',
                    category='links',
                    message=f'Broken link: [{link_text}]({url})'
                ))
    
    return issues


def check_code_blocks(content: str, filepath: Path) -> list:
    """Check code block formatting."""
    issues = []
    
    # Check for unclosed code blocks
    fence_count = content.count('```')
    if fence_count % 2 != 0:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='error',
            category='formatting',
            message='Unclosed code block (odd number of ``` markers)'
        ))
    
    # Check for language specification
    code_blocks = re.findall(r'```(\w*)\n', content)
    unnamed = sum(1 for lang in code_blocks if not lang)
    if unnamed > 0:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='info',
            category='formatting',
            message=f'{unnamed} code block(s) without language specification'
        ))
    
    return issues


def check_content_quality(content: str, filepath: Path) -> list:
    """Check content quality indicators."""
    issues = []
    
    # Check for TODO/FIXME markers
    todos = re.findall(r'\b(TODO|FIXME|XXX|HACK)\b', content, re.IGNORECASE)
    if todos:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='content',
            message=f'Contains {len(todos)} TODO/FIXME markers'
        ))
    
    # Check for placeholder text
    placeholders = re.findall(r'\[(?:TBD|TBW|PLACEHOLDER|INSERT|DESCRIBE)\]', content, re.IGNORECASE)
    if placeholders:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='warning',
            category='content',
            message=f'Contains {len(placeholders)} placeholder markers'
        ))
    
    # Check for very short documents
    words = len(content.split())
    if words < 50:
        issues.append(ValidationIssue(
            path=str(filepath),
            severity='info',
            category='content',
            message=f'Very short document ({words} words)'
        ))
    
    return issues


def detect_quadrant(content: str, filename: str) -> str:
    """Detect Diátaxis quadrant."""
    content_lower = content.lower()
    filename_lower = filename.lower()
    
    patterns = {
        'Tutorial': ['tutorial', 'lesson', 'learn', 'quickstart', 'getting-started'],
        'How-To': ['how-to', 'howto', 'guide', 'cookbook'],
        'Reference': ['reference', 'api', 'spec', 'schema', 'config'],
        'Explanation': ['explanation', 'concept', 'architecture', 'why', 'about'],
    }
    
    for quadrant, keywords in patterns.items():
        if any(kw in filename_lower for kw in keywords):
            return quadrant
    
    return 'Unknown'


def calculate_quality_score(issues: list) -> int:
    """Calculate quality score out of 100."""
    score = 100
    
    for issue in issues:
        if issue.severity == 'error':
            score -= 15
        elif issue.severity == 'warning':
            score -= 5
        elif issue.severity == 'info':
            score -= 1
    
    return max(0, score)


def validate_document(filepath: Path, docs_root: Path) -> DocumentValidation:
    """Validate a single document."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return DocumentValidation(
            path=str(filepath),
            title=None,
            quadrant='Unknown',
            issues=[ValidationIssue(
                path=str(filepath),
                severity='error',
                category='read',
                message=f'Could not read file: {e}'
            )],
            quality_score=0,
            passed=False
        )
    
    issues = []
    issues.extend(check_frontmatter(content, filepath))
    issues.extend(check_headings(content, filepath))
    issues.extend(check_links(content, filepath, docs_root))
    issues.extend(check_code_blocks(content, filepath))
    issues.extend(check_content_quality(content, filepath))
    
    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else None
    
    quadrant = detect_quadrant(content, filepath.name)
    quality_score = calculate_quality_score(issues)
    
    error_count = sum(1 for i in issues if i.severity == 'error')
    passed = error_count == 0
    
    return DocumentValidation(
        path=str(filepath),
        title=title,
        quadrant=quadrant,
        issues=issues,
        quality_score=quality_score,
        passed=passed
    )


def validate_directory(docs_dir: Path) -> list:
    """Validate all documents in a directory."""
    results = []
    extensions = ['.md', '.mdx']
    
    for ext in extensions:
        for filepath in docs_dir.rglob(f'*{ext}'):
            if any(x in str(filepath) for x in ['node_modules', '.git', '__pycache__']):
                continue
            results.append(validate_document(filepath, docs_dir))
    
    return results


def check_orphans(results: list, docs_dir: Path) -> list:
    """Check for orphan pages (no incoming links)."""
    issues = []
    
    # Build set of all doc paths
    all_docs = {Path(r.path).relative_to(docs_dir) for r in results}
    
    # Build set of linked docs
    linked_docs = set()
    for result in results:
        try:
            content = Path(result.path).read_text()
            links = re.findall(r'\]\(([^)]+)\)', content)
            for link in links:
                if not link.startswith(('http://', 'https://', '#')):
                    link_path = link.split('#')[0]
                    if link_path:
                        linked_docs.add(Path(link_path).with_suffix('.md'))
        except:
            pass
    
    # Find orphans (excluding index files)
    for doc in all_docs:
        if doc.stem not in ['index', 'README', '_index']:
            if doc not in linked_docs:
                issues.append(ValidationIssue(
                    path=str(doc),
                    severity='info',
                    category='structure',
                    message='Orphan page (no incoming links)'
                ))
    
    return issues


def generate_report(results: list, orphan_issues: list, output_path: Path, strict: bool):
    """Generate validation report."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    
    all_issues = []
    for r in results:
        all_issues.extend(r.issues)
    all_issues.extend(orphan_issues)
    
    errors = sum(1 for i in all_issues if i.severity == 'error')
    warnings = sum(1 for i in all_issues if i.severity == 'warning')
    infos = sum(1 for i in all_issues if i.severity == 'info')
    
    avg_quality = sum(r.quality_score for r in results) / total if total > 0 else 0
    
    lines = [
        '# Documentation Validation Report',
        '',
        f'Generated: {datetime.now().isoformat()}',
        '',
        '## Summary',
        '',
        f'- **Documents Validated**: {total}',
        f'- **Passed**: {passed}',
        f'- **Failed**: {failed}',
        f'- **Average Quality Score**: {avg_quality:.1f}/100',
        '',
        '### Issues by Severity',
        '',
        f'- 🔴 Errors: {errors}',
        f'- 🟡 Warnings: {warnings}',
        f'- 🔵 Info: {infos}',
        '',
        '## Results by Document',
        '',
        '| Document | Quadrant | Score | Status | Issues |',
        '|----------|----------|-------|--------|--------|',
    ]
    
    for r in sorted(results, key=lambda x: x.quality_score):
        status = '✅ Pass' if r.passed else '❌ Fail'
        issue_count = len(r.issues)
        title = r.title[:30] + '...' if r.title and len(r.title) > 30 else (r.title or Path(r.path).name)
        lines.append(f'| {title} | {r.quadrant} | {r.quality_score} | {status} | {issue_count} |')
    
    if all_issues:
        lines.extend([
            '',
            '## All Issues',
            '',
        ])
        
        # Group by severity
        for severity, emoji in [('error', '🔴'), ('warning', '🟡'), ('info', '🔵')]:
            severity_issues = [i for i in all_issues if i.severity == severity]
            if severity_issues:
                lines.append(f'### {emoji} {severity.title()}s ({len(severity_issues)})')
                lines.append('')
                for issue in severity_issues:
                    lines.append(f'- **{Path(issue.path).name}**: {issue.message}')
                lines.append('')
    
    # Quadrant distribution
    quadrant_counts = {}
    for r in results:
        quadrant_counts[r.quadrant] = quadrant_counts.get(r.quadrant, 0) + 1
    
    lines.extend([
        '## Diátaxis Distribution',
        '',
        '| Quadrant | Count | Percentage |',
        '|----------|-------|------------|',
    ])
    
    for quadrant, count in sorted(quadrant_counts.items()):
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f'| {quadrant} | {count} | {pct:.1f}% |')
    
    # Overall status
    overall_pass = errors == 0 if strict else failed == 0
    
    lines.extend([
        '',
        '## Validation Result',
        '',
        f'**Status**: {"✅ PASSED" if overall_pass else "❌ FAILED"}',
        '',
    ])
    
    if not overall_pass:
        lines.extend([
            '### Required Actions',
            '',
        ])
        if errors > 0:
            lines.append(f'- Fix {errors} error(s) before deployment')
        if warnings > 0:
            lines.append(f'- Consider addressing {warnings} warning(s)')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Report written to {output_path}")
    return overall_pass


def main():
    parser = argparse.ArgumentParser(description='Validate documentation quality')
    parser.add_argument('docs_dir', type=Path, help='Documentation directory')
    parser.add_argument('--output', '-o', type=Path, default=Path('validation-report.md'),
                        help='Output report path')
    parser.add_argument('--strict', action='store_true',
                        help='Strict mode: fail on any warning or error')
    parser.add_argument('--json', action='store_true',
                        help='Also output JSON results')
    
    args = parser.parse_args()
    
    if not args.docs_dir.exists():
        print(f"Error: Directory {args.docs_dir} does not exist")
        return 1
    
    print(f"Validating documentation in {args.docs_dir}...")
    results = validate_directory(args.docs_dir)
    
    if not results:
        print("No documentation files found.")
        return 1
    
    print(f"Validated {len(results)} documents")
    
    orphan_issues = check_orphans(results, args.docs_dir)
    
    passed = generate_report(results, orphan_issues, args.output, args.strict)
    
    if args.json:
        json_output = {
            'results': [
                {
                    'path': r.path,
                    'title': r.title,
                    'quadrant': r.quadrant,
                    'quality_score': r.quality_score,
                    'passed': r.passed,
                    'issues': [
                        {
                            'severity': i.severity,
                            'category': i.category,
                            'message': i.message
                        }
                        for i in r.issues
                    ]
                }
                for r in results
            ]
        }
        json_path = args.output.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(json_output, f, indent=2)
        print(f"JSON output written to {json_path}")
    
    return 0 if passed else 1


if __name__ == '__main__':
    exit(main())
