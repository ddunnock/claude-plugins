#!/usr/bin/env python3
"""
Research documentation patterns and competitors.

Usage:
    python doc_research.py "<domain>" [--output research-notes.md] [--format markdown|json]

This script provides a structured framework for documentation research.
Actual web searches should be performed by Claude using web_search tool.
This script generates research templates and organizes findings.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
import sys


@dataclass
class ResearchQuery:
    """A single research query."""
    query: str
    category: str
    priority: int
    purpose: str


@dataclass
class CompetitorDoc:
    """Information about competitor documentation."""
    name: str
    url: str
    strengths: list
    patterns: list
    quadrant_coverage: dict
    notes: str


def get_research_queries(domain: str) -> list:
    """Generate research queries for a domain."""
    return [
        ResearchQuery(
            query=f'"{domain}" documentation best practices',
            category='Best Practices',
            priority=1,
            purpose='Identify established patterns in the domain'
        ),
        ResearchQuery(
            query=f'"{domain}" getting started guide',
            category='Tutorials',
            priority=1,
            purpose='Find exemplar quickstart/tutorial patterns'
        ),
        ResearchQuery(
            query=f'"{domain}" API documentation',
            category='Reference',
            priority=2,
            purpose='Find reference documentation patterns'
        ),
        ResearchQuery(
            query=f'"{domain}" how to guide',
            category='How-To',
            priority=2,
            purpose='Find task-oriented documentation patterns'
        ),
        ResearchQuery(
            query=f'site:github.com "{domain}" awesome',
            category='Resources',
            priority=3,
            purpose='Find curated resource lists'
        ),
        ResearchQuery(
            query=f'"{domain}" documentation framework',
            category='Structure',
            priority=2,
            purpose='Find structural approaches used in the domain'
        ),
        ResearchQuery(
            query=f'"{domain}" vs alternatives comparison',
            category='Explanation',
            priority=3,
            purpose='Find comparison/explanation patterns'
        ),
    ]


def generate_research_template(domain: str) -> str:
    """Generate a research template for manual completion."""
    queries = get_research_queries(domain)
    
    template = f"""# Documentation Research: {domain}

Generated: {datetime.now().isoformat()}

## Research Objective

Identify documentation patterns, best practices, and exemplar sites in the **{domain}** domain to inform the documentation architecture.

---

## Research Queries

Execute these searches and record findings:

"""
    
    for i, q in enumerate(queries, 1):
        template += f"""### Query {i}: {q.category} (Priority {q.priority})

**Search**: `{q.query}`
**Purpose**: {q.purpose}

**Findings**:
- [ ] Search executed
- Results:
  1. [Title](URL) - [Notes]
  2. [Title](URL) - [Notes]
  3. [Title](URL) - [Notes]

**Patterns Identified**:
- [Pattern 1]
- [Pattern 2]

---

"""

    template += """## Competitor Analysis

### Competitor 1: [Name]

**URL**: [URL]
**Type**: [Official docs / Community / Blog / etc.]

**Diátaxis Coverage**:
| Quadrant | Present | Quality (1-5) | Notes |
|----------|---------|---------------|-------|
| Tutorial | [yes/no] | | |
| How-To | [yes/no] | | |
| Reference | [yes/no] | | |
| Explanation | [yes/no] | | |

**Strengths**:
- [Strength 1]
- [Strength 2]

**Patterns to Adopt**:
- [Pattern 1]
- [Pattern 2]

**Patterns to Avoid**:
- [Anti-pattern 1]

---

### Competitor 2: [Name]

[Repeat structure above]

---

## Summary Findings

### Best Practices Identified

| Practice | Source | Applicability |
|----------|--------|---------------|
| [Practice] | [Source URL] | [High/Medium/Low] |

### Recommended Patterns

#### Navigation
- [Pattern from research]

#### Structure  
- [Pattern from research]

#### Content Types
- [Pattern from research]

### Anti-Patterns to Avoid

| Anti-Pattern | Why to Avoid | Source |
|--------------|--------------|--------|
| [Anti-pattern] | [Reason] | [Where observed] |

---

## Evidence Grounding

All findings must be marked:
- `[VERIFIED: URL]` - Directly observed in source
- `[INFERRED: URL]` - Reasonable inference from source
- `[ASSUMPTION]` - Needs stakeholder validation

---

## Next Steps

Based on this research:
1. [ ] Review findings with stakeholder
2. [ ] Prioritize patterns for adoption
3. [ ] Update documentation architecture plan
4. [ ] Create WBS incorporating research insights
"""

    return template


def generate_json_template(domain: str) -> dict:
    """Generate a JSON research template."""
    return {
        'domain': domain,
        'generated_at': datetime.now().isoformat(),
        'queries': [asdict(q) for q in get_research_queries(domain)],
        'competitors': [],
        'patterns': {
            'navigation': [],
            'structure': [],
            'content_types': [],
            'anti_patterns': []
        },
        'best_practices': [],
        'recommendations': [],
        'evidence': {
            'verified': [],
            'inferred': [],
            'assumptions': []
        }
    }




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
    parser = argparse.ArgumentParser(
        description='Generate documentation research template',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python doc_research.py "API documentation"
    python doc_research.py "developer tools" --output research.md
    python doc_research.py "kubernetes" --format json --output research.json

Note: This script generates research templates. Actual web searches
should be performed by Claude using the web_search tool.
        """
    )
    parser.add_argument('domain', help='Domain or topic to research')
    parser.add_argument('--output', '-o', type=Path, 
                        default=Path('research-notes.md'),
                        help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'],
                        default='markdown', help='Output format')
    
    args = parser.parse_args()

    _validate_path(str(args.output), {'.md', '.json'}, "output file")
    
    print(f"Generating research template for domain: {args.domain}")
    
    if args.format == 'json':
        output = generate_json_template(args.domain)
        output_path = args.output.with_suffix('.json')
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
    else:
        output = generate_research_template(args.domain)
        output_path = args.output
        with open(output_path, 'w') as f:
            f.write(output)
    
    print(f"Research template written to: {output_path}")
    print(f"\nGenerated {len(get_research_queries(args.domain))} research queries.")
    print("\nNext steps:")
    print("1. Execute the research queries using web search")
    print("2. Fill in the competitor analysis sections")
    print("3. Document patterns and best practices found")
    print("4. Mark all findings with evidence grounding")
    
    return 0


if __name__ == '__main__':
    exit(main())
