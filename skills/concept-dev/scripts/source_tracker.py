#!/usr/bin/env python3
"""
Source Tracker for Concept Development

Manages the source registry for grounding all claims and research findings.
Adapted from trade-study-analysis source_tracker.py with concept-dev-specific
source types and confidence levels.
"""

import os
import json
import argparse
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys


class SourceTracker:
    """Manages source registration and tracking for concept development."""

    SOURCE_TYPES = {
        'web_research': 'Web Research (article, blog, documentation)',
        'paper': 'Academic Paper or Technical Report',
        'domain_expert': 'Domain Expert Input',
        'existing_system': 'Existing System Documentation',
        'standards_document': 'Standard or Specification',
        'patent': 'Patent or Patent Application',
        'conference': 'Conference Proceedings or Presentation',
        'vendor_doc': 'Vendor Documentation or Datasheet',
        'user_provided': 'User-Provided Knowledge (Verbal)',
        'prior_study': 'Prior Study or Analysis',
        'other': 'Other'
    }

    CONFIDENCE_LEVELS = {
        'high': 'Verified via authoritative source with citation',
        'medium': 'Credible source, not independently verified',
        'low': 'Single source or expert opinion',
        'ungrounded': 'No external source — training data or inference'
    }

    def __init__(self, registry_path: str = '.concept-dev/source_registry.json'):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load existing registry or create new one."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            },
            'sources': [],
            'gaps': [],
            'citations': []
        }

    def _save_registry(self):
        """Save registry to file atomically."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry['metadata']['last_modified'] = datetime.now().isoformat()
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.registry_path.parent), suffix='.tmp'
        )
        try:
            with open(fd, 'w') as f:
                json.dump(self.registry, f, indent=2)
            Path(tmp_path).replace(self.registry_path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def _generate_id(self, prefix: str, collection: str = 'sources') -> str:
        """Generate unique ID within the given registry collection."""
        existing_ids = {item['id'] for item in self.registry[collection]}
        counter = 1
        while f"{prefix}-{counter:03d}" in existing_ids:
            counter += 1
        return f"{prefix}-{counter:03d}"

    def add_source(
        self,
        name: str,
        source_type: str,
        url: Optional[str] = None,
        version: Optional[str] = None,
        date: Optional[str] = None,
        file_path: Optional[str] = None,
        relevant_sections: Optional[List[str]] = None,
        confidence: str = 'medium',
        notes: Optional[str] = None,
        phase: Optional[str] = None
    ) -> str:
        """
        Register a new source document.

        Args:
            name: Source name or title
            source_type: Type from SOURCE_TYPES
            url: URL if web-based source
            version: Document version
            date: Publication/access date
            file_path: Local file path if applicable
            relevant_sections: List of relevant sections
            confidence: Confidence level
            notes: Additional notes
            phase: Which concept-dev phase this source is for

        Returns:
            Source ID
        """
        if source_type not in self.SOURCE_TYPES:
            raise ValueError(f"Invalid source type. Must be one of: {list(self.SOURCE_TYPES.keys())}")

        if confidence not in self.CONFIDENCE_LEVELS:
            raise ValueError(f"Invalid confidence. Must be one of: {list(self.CONFIDENCE_LEVELS.keys())}")

        source_id = self._generate_id('SRC', 'sources')

        source = {
            'id': source_id,
            'name': name,
            'type': source_type,
            'type_description': self.SOURCE_TYPES[source_type],
            'url': url,
            'version': version,
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'file_path': file_path,
            'relevant_sections': relevant_sections or [],
            'confidence': confidence,
            'confidence_description': self.CONFIDENCE_LEVELS[confidence],
            'notes': notes,
            'phase': phase,
            'registered_at': datetime.now().isoformat(),
            'citation_count': 0
        }

        self.registry['sources'].append(source)
        self._save_registry()

        return source_id

    def add_gap(
        self,
        description: str,
        required_for: List[str],
        requested_source_type: str,
        phase: Optional[str] = None
    ) -> str:
        """
        Register a data gap requiring a source.

        Args:
            description: Description of missing data
            required_for: List of blocks/sections needing this data
            requested_source_type: Type of source needed
            phase: Which concept-dev phase this gap is for

        Returns:
            Gap ID
        """
        gap_id = self._generate_id('GAP', 'gaps')

        gap = {
            'id': gap_id,
            'description': description,
            'required_for': required_for,
            'requested_source_type': requested_source_type,
            'phase': phase,
            'status': 'open',
            'resolution': None,
            'created_at': datetime.now().isoformat()
        }

        self.registry['gaps'].append(gap)
        self._save_registry()

        return gap_id

    def resolve_gap(self, gap_id: str, resolution: str, source_id: Optional[str] = None):
        """Mark a gap as resolved."""
        for gap in self.registry['gaps']:
            if gap['id'] == gap_id:
                gap['status'] = 'resolved'
                gap['resolution'] = resolution
                gap['resolved_source_id'] = source_id
                gap['resolved_at'] = datetime.now().isoformat()
                self._save_registry()
                return
        raise ValueError(f"Gap {gap_id} not found")

    def add_citation(
        self,
        source_id: str,
        claim: str,
        location: str,
        page_section: Optional[str] = None
    ) -> str:
        """
        Record a citation of a source.

        Args:
            source_id: ID of source being cited
            claim: The claim being supported
            location: Where in the concept artifacts this citation appears
            page_section: Specific page/section in source

        Returns:
            Citation ID
        """
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")

        citation_id = self._generate_id('CIT', 'citations')

        citation = {
            'id': citation_id,
            'source_id': source_id,
            'source_name': source['name'],
            'claim': claim,
            'location': location,
            'page_section': page_section,
            'created_at': datetime.now().isoformat()
        }

        self.registry['citations'].append(citation)

        # Update citation count
        for s in self.registry['sources']:
            if s['id'] == source_id:
                s['citation_count'] = s.get('citation_count', 0) + 1
                break

        self._save_registry()
        return citation_id

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get source by ID."""
        for source in self.registry['sources']:
            if source['id'] == source_id:
                return source
        return None

    def list_sources(self, phase: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sources, optionally filtered by phase."""
        sources = self.registry['sources']
        if phase:
            sources = [s for s in sources if s.get('phase') == phase]
        return sources

    def list_gaps(self, status: Optional[str] = None, phase: Optional[str] = None) -> List[Dict[str, Any]]:
        """List data gaps, optionally filtered by status and phase."""
        gaps = self.registry['gaps']
        if status:
            gaps = [g for g in gaps if g['status'] == status]
        if phase:
            gaps = [g for g in gaps if g.get('phase') == phase]
        return gaps

    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of source coverage."""
        sources = self.registry['sources']
        citations = self.registry['citations']
        gaps = self.registry['gaps']

        confidence_counts = {'high': 0, 'medium': 0, 'low': 0, 'ungrounded': 0}
        type_counts = {}
        phase_counts = {}
        for source in sources:
            confidence_counts[source['confidence']] += 1
            t = source['type']
            type_counts[t] = type_counts.get(t, 0) + 1
            p = source.get('phase', 'unassigned')
            phase_counts[p] = phase_counts.get(p, 0) + 1

        return {
            'total_sources': len(sources),
            'total_citations': len(citations),
            'open_gaps': len([g for g in gaps if g['status'] == 'open']),
            'resolved_gaps': len([g for g in gaps if g['status'] == 'resolved']),
            'confidence_distribution': confidence_counts,
            'type_distribution': type_counts,
            'phase_distribution': phase_counts,
            'sources_with_citations': len([s for s in sources if s.get('citation_count', 0) > 0]),
            'sources_without_citations': len([s for s in sources if s.get('citation_count', 0) == 0])
        }

    def format_citation(self, source_id: str, page_section: Optional[str] = None) -> str:
        """Format a source citation string."""
        source = self.get_source(source_id)
        if not source:
            return f"[Source {source_id} not found]"

        parts = [source['name']]
        if source.get('url'):
            parts.append(source['url'])
        if source.get('version'):
            parts.append(f"v{source['version']}")
        if page_section:
            parts.append(page_section)
        if source.get('date'):
            parts.append(source['date'])

        confidence = source.get('confidence', 'medium')

        return f"{', '.join(parts)}; Confidence: {confidence.capitalize()}"

    def print_registry(self):
        """Print formatted registry summary."""
        print("=" * 80)
        print("SOURCE REGISTRY")
        print("=" * 80)

        print("\nREGISTERED SOURCES:")
        print("-" * 80)

        for source in self.registry['sources']:
            print(f"\n[{source['id']}] {source['name']}")
            print(f"  Type: {source['type_description']}")
            if source.get('url'):
                print(f"  URL: {source['url']}")
            print(f"  Date: {source.get('date', 'N/A')}")
            print(f"  Confidence: {source['confidence'].upper()}")
            print(f"  Phase: {source.get('phase', 'N/A')}")
            print(f"  Citations: {source.get('citation_count', 0)}")
            if source.get('relevant_sections'):
                print(f"  Sections: {', '.join(source['relevant_sections'])}")
            if source.get('notes'):
                print(f"  Notes: {source['notes']}")

        print("\n" + "-" * 80)
        print("DATA GAPS:")
        print("-" * 80)

        open_gaps = [g for g in self.registry['gaps'] if g['status'] == 'open']
        if open_gaps:
            for gap in open_gaps:
                print(f"\n[{gap['id']}] {gap['description']}")
                print(f"  Required for: {', '.join(gap['required_for'])}")
                print(f"  Needs: {gap['requested_source_type']}")
                print(f"  Phase: {gap.get('phase', 'N/A')}")
        else:
            print("\nNo open data gaps.")

        print("\n" + "-" * 80)
        print("COVERAGE SUMMARY:")
        print("-" * 80)

        summary = self.get_coverage_summary()
        print(f"\n  Total sources: {summary['total_sources']}")
        print(f"  Total citations: {summary['total_citations']}")
        print(f"  Open gaps: {summary['open_gaps']}")
        print(f"\n  Confidence distribution:")
        for level, count in summary['confidence_distribution'].items():
            if count > 0:
                print(f"    {level.capitalize()}: {count}")

        print("\n" + "=" * 80)

    def export_bibliography(self, output_path: str):
        """Export sources as formatted bibliography."""
        with open(output_path, 'w') as f:
            f.write("# Source Bibliography\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

            f.write("## Registered Sources\n\n")

            for source in sorted(self.registry['sources'], key=lambda x: x['id']):
                f.write(f"**[{source['id']}]** {source['name']}\n")
                f.write(f"- Type: {source['type_description']}\n")
                if source.get('url'):
                    f.write(f"- URL: {source['url']}\n")
                f.write(f"- Date: {source.get('date', 'N/A')}\n")
                f.write(f"- Confidence: {source['confidence'].capitalize()}\n")
                f.write(f"- Phase: {source.get('phase', 'N/A')}\n")
                if source.get('notes'):
                    f.write(f"- Notes: {source['notes']}\n")
                f.write("\n")

            f.write("## Data Gaps\n\n")

            open_gaps = [g for g in self.registry['gaps'] if g['status'] == 'open']
            if open_gaps:
                for gap in open_gaps:
                    f.write(f"**[{gap['id']}]** {gap['description']}\n")
                    f.write(f"- Required for: {', '.join(gap['required_for'])}\n")
                    f.write(f"- Needs: {gap['requested_source_type']}\n\n")
            else:
                f.write("No open data gaps.\n")


def _sync_to_state(registry_path: str, state_path: str):
    """Sync source counts from registry to state.json."""
    state_file = Path(state_path)
    if not state_file.exists():
        return
    reg_file = Path(registry_path)
    if not reg_file.exists():
        return
    with open(reg_file, 'r') as f:
        reg = json.load(f)
    sources = reg.get('sources', [])
    by_conf = {'high': 0, 'medium': 0, 'low': 0, 'ungrounded': 0}
    for s in sources:
        conf = s.get('confidence', 'medium')
        if conf in by_conf:
            by_conf[conf] += 1

    with open(state_file, 'r') as f:
        state = json.load(f)
    state['sources']['total'] = len(sources)
    state['sources']['by_confidence'] = by_conf
    state['session']['last_updated'] = datetime.now().isoformat()
    tmp = state_file.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    tmp.rename(state_file)




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
        description='Manage source registry for concept development'
    )
    parser.add_argument('--state', default='.concept-dev/state.json',
                       help='Path to state.json for auto-sync')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add source
    add_parser = subparsers.add_parser('add', help='Add a new source')
    add_parser.add_argument('name', help='Source name')
    add_parser.add_argument('--type', required=True, choices=SourceTracker.SOURCE_TYPES.keys(),
                           help='Source type')
    add_parser.add_argument('--url', help='Source URL')
    add_parser.add_argument('--version', help='Document version')
    add_parser.add_argument('--date', help='Document date (YYYY-MM-DD)')
    add_parser.add_argument('--file', help='Path to document file')
    add_parser.add_argument('--sections', nargs='+', help='Relevant sections')
    add_parser.add_argument('--confidence', choices=['high', 'medium', 'low', 'ungrounded'],
                           default='medium', help='Confidence level')
    add_parser.add_argument('--notes', help='Additional notes')
    add_parser.add_argument('--phase', help='Concept-dev phase')

    # Add gap
    gap_parser = subparsers.add_parser('gap', help='Register a data gap')
    gap_parser.add_argument('description', help='Description of missing data')
    gap_parser.add_argument('--required-for', nargs='+', required=True,
                           help='Blocks/sections needing this data')
    gap_parser.add_argument('--needed-source-type', '--source-type', required=True,
                           choices=list(SourceTracker.SOURCE_TYPES.keys()),
                           dest='needed_source_type',
                           help='Type of source needed')
    gap_parser.add_argument('--phase', help='Concept-dev phase')

    # List sources
    list_parser = subparsers.add_parser('list', help='List registered sources')
    list_parser.add_argument('--gaps-only', action='store_true', help='Show only data gaps')
    list_parser.add_argument('--phase', help='Filter by phase')

    # Show summary
    subparsers.add_parser('summary', help='Show coverage summary')

    # Export bibliography
    export_parser = subparsers.add_parser('export', help='Export bibliography')
    export_parser.add_argument('-o', '--output', default='bibliography.md',
                              help='Output file path')

    # Common arguments
    parser.add_argument('--registry', default='.concept-dev/source_registry.json',
                       help='Path to source registry file')

    args = parser.parse_args()

    args.registry = _validate_path(args.registry, {'.json'}, "registry file")
    args.state = _validate_path(args.state, {'.json'}, "state file")
    if args.command == "export" and hasattr(args, "output") and args.output:
        args.output = _validate_path(args.output, {'.md', '.json'}, "output file")

    tracker = SourceTracker(args.registry)

    if args.command == 'add':
        source_id = tracker.add_source(
            name=args.name,
            source_type=args.type,
            url=args.url,
            version=args.version,
            date=args.date,
            file_path=args.file,
            relevant_sections=args.sections,
            confidence=args.confidence,
            notes=args.notes,
            phase=args.phase
        )
        print(f"Added source: {source_id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'gap':
        gap_id = tracker.add_gap(
            description=args.description,
            required_for=args.required_for,
            requested_source_type=args.needed_source_type,
            phase=args.phase
        )
        print(f"Registered data gap: {gap_id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'list':
        if args.gaps_only:
            gaps = tracker.list_gaps(status='open', phase=args.phase)
            print(f"Open data gaps: {len(gaps)}")
            for gap in gaps:
                print(f"  [{gap['id']}] {gap['description']}")
        else:
            tracker.print_registry()

    elif args.command == 'summary':
        summary = tracker.get_coverage_summary()
        print(json.dumps(summary, indent=2))

    elif args.command == 'export':
        tracker.export_bibliography(args.output)
        print(f"Exported bibliography to: {args.output}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
