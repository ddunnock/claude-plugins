#!/usr/bin/env python3
"""
Source Tracker for Trade Study Analysis

Manages the source registry for grounding all claims and data points.
Every piece of data in the trade study must be traceable to a registered source.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib


class SourceTracker:
    """Manages source registration and tracking for trade studies."""
    
    SOURCE_TYPES = {
        'datasheet': 'Product Datasheet',
        'test_report': 'Test Report',
        'requirements': 'Requirements Document',
        'cost_estimate': 'Cost Estimate',
        'prior_study': 'Prior Trade Study',
        'standard': 'Standard/Specification',
        'expert_input': 'Expert Input',
        'user_provided': 'User-Provided (Verbal)',
        'other': 'Other'
    }
    
    CONFIDENCE_LEVELS = {
        'high': 'Verified test data or certified specification',
        'medium': 'Vendor datasheet or credible estimate',
        'low': 'Expert opinion or extrapolation',
        'ungrounded': 'No source available'
    }
    
    def __init__(self, registry_path: str = 'sources/source_registry.json'):
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
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry['metadata']['last_modified'] = datetime.now().isoformat()
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _generate_id(self, prefix: str = 'SRC') -> str:
        """Generate unique source ID."""
        existing_ids = [s['id'] for s in self.registry['sources']]
        counter = 1
        while f"{prefix}-{counter:03d}" in existing_ids:
            counter += 1
        return f"{prefix}-{counter:03d}"
    
    def add_source(
        self,
        name: str,
        source_type: str,
        version: Optional[str] = None,
        date: Optional[str] = None,
        file_path: Optional[str] = None,
        relevant_sections: Optional[List[str]] = None,
        confidence: str = 'medium',
        notes: Optional[str] = None
    ) -> str:
        """
        Register a new source document.
        
        Args:
            name: Document name
            source_type: Type from SOURCE_TYPES
            version: Document version
            date: Document date
            file_path: Path to document file
            relevant_sections: List of relevant sections
            confidence: Confidence level
            notes: Additional notes
            
        Returns:
            Source ID
        """
        if source_type not in self.SOURCE_TYPES:
            raise ValueError(f"Invalid source type. Must be one of: {list(self.SOURCE_TYPES.keys())}")
        
        if confidence not in self.CONFIDENCE_LEVELS:
            raise ValueError(f"Invalid confidence. Must be one of: {list(self.CONFIDENCE_LEVELS.keys())}")
        
        source_id = self._generate_id('SRC')
        
        source = {
            'id': source_id,
            'name': name,
            'type': source_type,
            'type_description': self.SOURCE_TYPES[source_type],
            'version': version,
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'file_path': file_path,
            'relevant_sections': relevant_sections or [],
            'confidence': confidence,
            'confidence_description': self.CONFIDENCE_LEVELS[confidence],
            'notes': notes,
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
        requested_source_type: str
    ) -> str:
        """
        Register a data gap requiring a source.
        
        Args:
            description: Description of missing data
            required_for: List of criteria/sections needing this data
            requested_source_type: Type of source needed
            
        Returns:
            Gap ID
        """
        gap_id = f"GAP-{len(self.registry['gaps']) + 1:03d}"
        
        gap = {
            'id': gap_id,
            'description': description,
            'required_for': required_for,
            'requested_source_type': requested_source_type,
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
                break
        self._save_registry()
    
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
            location: Where in the trade study this citation appears
            page_section: Specific page/section in source
            
        Returns:
            Citation ID
        """
        # Verify source exists
        source = self.get_source(source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
        
        citation_id = f"CIT-{len(self.registry['citations']) + 1:03d}"
        
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
    
    def list_sources(self) -> List[Dict[str, Any]]:
        """List all registered sources."""
        return self.registry['sources']
    
    def list_gaps(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List data gaps, optionally filtered by status."""
        gaps = self.registry['gaps']
        if status:
            gaps = [g for g in gaps if g['status'] == status]
        return gaps
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of source coverage."""
        sources = self.registry['sources']
        citations = self.registry['citations']
        gaps = self.registry['gaps']
        
        confidence_counts = {'high': 0, 'medium': 0, 'low': 0, 'ungrounded': 0}
        for source in sources:
            confidence_counts[source['confidence']] += 1
        
        type_counts = {}
        for source in sources:
            t = source['type']
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            'total_sources': len(sources),
            'total_citations': len(citations),
            'open_gaps': len([g for g in gaps if g['status'] == 'open']),
            'resolved_gaps': len([g for g in gaps if g['status'] == 'resolved']),
            'confidence_distribution': confidence_counts,
            'type_distribution': type_counts,
            'sources_with_citations': len([s for s in sources if s.get('citation_count', 0) > 0]),
            'sources_without_citations': len([s for s in sources if s.get('citation_count', 0) == 0])
        }
    
    def format_citation(self, source_id: str, page_section: Optional[str] = None) -> str:
        """Format a source citation string."""
        source = self.get_source(source_id)
        if not source:
            return f"[Source {source_id} not found]"
        
        parts = [source['name']]
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
            print(f"  Version/Date: {source.get('version', 'N/A')} / {source.get('date', 'N/A')}")
            print(f"  Confidence: {source['confidence'].upper()}")
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
                f.write(f"- Version: {source.get('version', 'N/A')}\n")
                f.write(f"- Date: {source.get('date', 'N/A')}\n")
                f.write(f"- Confidence: {source['confidence'].capitalize()}\n")
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


def main():
    parser = argparse.ArgumentParser(
        description='Manage source registry for trade study analysis'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add source
    add_parser = subparsers.add_parser('add', help='Add a new source')
    add_parser.add_argument('name', help='Source document name')
    add_parser.add_argument('--type', required=True, choices=SourceTracker.SOURCE_TYPES.keys(),
                          help='Source type')
    add_parser.add_argument('--version', help='Document version')
    add_parser.add_argument('--date', help='Document date (YYYY-MM-DD)')
    add_parser.add_argument('--file', help='Path to document file')
    add_parser.add_argument('--sections', nargs='+', help='Relevant sections')
    add_parser.add_argument('--confidence', choices=['high', 'medium', 'low'],
                          default='medium', help='Confidence level')
    add_parser.add_argument('--notes', help='Additional notes')
    
    # Add gap
    gap_parser = subparsers.add_parser('gap', help='Register a data gap')
    gap_parser.add_argument('description', help='Description of missing data')
    gap_parser.add_argument('--required-for', nargs='+', required=True,
                           help='Criteria/sections needing this data')
    gap_parser.add_argument('--source-type', required=True,
                           choices=SourceTracker.SOURCE_TYPES.keys(),
                           help='Type of source needed')
    
    # List sources
    list_parser = subparsers.add_parser('list', help='List registered sources')
    list_parser.add_argument('--gaps-only', action='store_true',
                            help='Show only data gaps')
    
    # Show summary
    subparsers.add_parser('summary', help='Show coverage summary')
    
    # Export bibliography
    export_parser = subparsers.add_parser('export', help='Export bibliography')
    export_parser.add_argument('-o', '--output', default='bibliography.md',
                              help='Output file path')
    
    # Common arguments
    parser.add_argument('--registry', default='sources/source_registry.json',
                       help='Path to source registry file')
    
    args = parser.parse_args()
    
    tracker = SourceTracker(args.registry)
    
    if args.command == 'add':
        source_id = tracker.add_source(
            name=args.name,
            source_type=args.type,
            version=args.version,
            date=args.date,
            file_path=args.file,
            relevant_sections=args.sections,
            confidence=args.confidence,
            notes=args.notes
        )
        print(f"Added source: {source_id}")
    
    elif args.command == 'gap':
        gap_id = tracker.add_gap(
            description=args.description,
            required_for=args.required_for,
            requested_source_type=args.source_type
        )
        print(f"Registered data gap: {gap_id}")
    
    elif args.command == 'list':
        if args.gaps_only:
            gaps = tracker.list_gaps(status='open')
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
