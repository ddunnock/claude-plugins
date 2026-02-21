#!/usr/bin/env python3
"""
Fishbone (Ishikawa) Diagram Analysis for Trade Study Analysis

Structured cause categorization across 6 standard dimensions.
Requires source documentation for each identified factor.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class FishboneAnalysis:
    """Fishbone (Ishikawa) cause categorization analysis."""
    
    CATEGORIES = {
        'methods': {
            'name': 'Methods / Processes',
            'description': 'Procedures, workflows, standards, techniques used',
            'examples': [
                'Outdated procedures',
                'Missing process steps',
                'Inadequate standards',
                'Workflow bottlenecks',
                'Lack of documentation'
            ]
        },
        'machines': {
            'name': 'Machines / Technology',
            'description': 'Equipment, hardware, software, tools, infrastructure',
            'examples': [
                'Aging equipment',
                'Software limitations',
                'Inadequate tooling',
                'Infrastructure gaps',
                'Compatibility issues'
            ]
        },
        'materials': {
            'name': 'Materials / Inputs',
            'description': 'Raw materials, data, information, resources consumed',
            'examples': [
                'Poor input quality',
                'Missing data',
                'Resource constraints',
                'Supply issues',
                'Incomplete information'
            ]
        },
        'measurements': {
            'name': 'Measurements / Data',
            'description': 'Metrics, instrumentation, data quality, feedback mechanisms',
            'examples': [
                'Inadequate monitoring',
                'Poor data quality',
                'Missing metrics',
                'Delayed feedback',
                'Inaccurate measurements'
            ]
        },
        'environment': {
            'name': 'Environment',
            'description': 'Operating conditions, organizational culture, external factors',
            'examples': [
                'Harsh conditions',
                'Organizational barriers',
                'External pressures',
                'Regulatory constraints',
                'Cultural issues'
            ]
        },
        'people': {
            'name': 'People / Skills',
            'description': 'Training, expertise, staffing, communication, human factors',
            'examples': [
                'Skill gaps',
                'Understaffing',
                'Communication issues',
                'Training deficiencies',
                'Workload imbalance'
            ]
        }
    }
    
    def __init__(self):
        self.analysis = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'status': 'in_progress'
            },
            'problem': None,
            'categories': {cat: [] for cat in self.CATEGORIES},
            'prioritized_factors': [],
            'root_cause_candidates': [],
            'sources': [],
            'assumptions': []
        }
    
    def set_problem(self, problem: str, source: Optional[str] = None):
        """Set the problem being analyzed."""
        self.analysis['problem'] = {
            'statement': problem,
            'source': source or 'User-provided',
            'timestamp': datetime.now().isoformat()
        }
    
    def add_factor(
        self,
        category: str,
        factor: str,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        impact: str = 'medium',
        is_assumption: bool = False,
        assumption_basis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a contributing factor to a category.
        
        Args:
            category: Category key (methods, machines, etc.)
            factor: Description of the contributing factor
            source: Source document
            source_id: Reference to source registry
            impact: Impact level (high/medium/low)
            is_assumption: Whether this is an assumption
            assumption_basis: Basis for assumption
            
        Returns:
            The created factor entry
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Use: {list(self.CATEGORIES.keys())}")
        
        entry = {
            'factor': factor,
            'source': source or 'User-provided (no document)',
            'source_id': source_id,
            'impact': impact,
            'is_assumption': is_assumption,
            'assumption_basis': assumption_basis,
            'timestamp': datetime.now().isoformat()
        }
        
        self.analysis['categories'][category].append(entry)
        
        # Track sources and assumptions
        if source and source not in self.analysis['sources']:
            self.analysis['sources'].append(source)
        
        if is_assumption:
            self.analysis['assumptions'].append({
                'category': category,
                'factor': factor,
                'basis': assumption_basis
            })
        
        return entry
    
    def prioritize_factors(self):
        """Rank all factors by impact."""
        all_factors = []
        
        impact_order = {'high': 0, 'medium': 1, 'low': 2}
        
        for category, factors in self.analysis['categories'].items():
            for f in factors:
                all_factors.append({
                    'category': category,
                    'category_name': self.CATEGORIES[category]['name'],
                    **f
                })
        
        # Sort by impact
        all_factors.sort(key=lambda x: impact_order.get(x['impact'], 1))
        
        self.analysis['prioritized_factors'] = all_factors
        return all_factors
    
    def identify_root_cause_candidates(self) -> List[Dict[str, Any]]:
        """Identify potential root causes from high-impact factors."""
        candidates = []
        
        for factor in self.analysis['prioritized_factors']:
            if factor['impact'] == 'high':
                candidates.append({
                    'factor': factor['factor'],
                    'category': factor['category'],
                    'category_name': factor['category_name'],
                    'source': factor['source'],
                    'rationale': 'High-impact factor identified through Fishbone analysis',
                    'requires_5whys': not factor['is_assumption']
                })
        
        self.analysis['root_cause_candidates'] = candidates
        return candidates
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        category_counts = {
            cat: len(factors) 
            for cat, factors in self.analysis['categories'].items()
        }
        
        return {
            'problem': self.analysis['problem']['statement'] if self.analysis['problem'] else None,
            'total_factors': sum(category_counts.values()),
            'factors_by_category': category_counts,
            'high_impact_count': len([f for f in self.analysis['prioritized_factors'] if f['impact'] == 'high']),
            'root_cause_candidates': len(self.analysis['root_cause_candidates']),
            'sources_used': len(self.analysis['sources']),
            'assumptions_made': len(self.analysis['assumptions']),
            'status': self.analysis['metadata']['status']
        }
    
    def export(self, path: str):
        """Export analysis to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.analysis, f, indent=2)
    
    def generate_diagram(self, output_path: str):
        """Generate fishbone diagram visualization."""
        if not HAS_MATPLOTLIB:
            print("matplotlib not available. Install with: pip install matplotlib")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Draw main spine
        ax.plot([1, 14], [5, 5], 'k-', linewidth=3)
        
        # Draw problem head
        problem_text = self.analysis['problem']['statement'][:40] + '...' if len(self.analysis['problem']['statement']) > 40 else self.analysis['problem']['statement']
        ax.add_patch(patches.FancyBboxPatch((13.5, 4), 2.3, 2, 
                                            boxstyle="round,pad=0.1",
                                            facecolor='lightcoral',
                                            edgecolor='darkred',
                                            linewidth=2))
        ax.text(14.6, 5, problem_text, ha='center', va='center', fontsize=8, wrap=True)
        
        # Category positions
        top_categories = ['methods', 'machines', 'materials']
        bottom_categories = ['measurements', 'environment', 'people']
        
        x_positions = [3, 7, 11]
        
        # Draw top bones
        for i, (cat, x) in enumerate(zip(top_categories, x_positions)):
            # Draw bone
            ax.plot([x, x + 1.5], [7.5, 5], 'k-', linewidth=2)
            
            # Category label
            ax.text(x, 8, self.CATEGORIES[cat]['name'], ha='center', fontsize=10, fontweight='bold')
            
            # Factors
            factors = self.analysis['categories'][cat]
            for j, f in enumerate(factors[:4]):  # Max 4 factors shown
                y = 7.3 - j * 0.5
                ax.plot([x - 0.5, x + 0.5], [y, y - 0.3], 'k-', linewidth=1)
                factor_text = f['factor'][:25] + '...' if len(f['factor']) > 25 else f['factor']
                ax.text(x - 0.7, y - 0.15, factor_text, ha='right', fontsize=7)
        
        # Draw bottom bones
        for i, (cat, x) in enumerate(zip(bottom_categories, x_positions)):
            # Draw bone
            ax.plot([x, x + 1.5], [2.5, 5], 'k-', linewidth=2)
            
            # Category label
            ax.text(x, 2, self.CATEGORIES[cat]['name'], ha='center', fontsize=10, fontweight='bold')
            
            # Factors
            factors = self.analysis['categories'][cat]
            for j, f in enumerate(factors[:4]):  # Max 4 factors shown
                y = 2.7 + j * 0.5
                ax.plot([x - 0.5, x + 0.5], [y, y + 0.3], 'k-', linewidth=1)
                factor_text = f['factor'][:25] + '...' if len(f['factor']) > 25 else f['factor']
                ax.text(x - 0.7, y + 0.15, factor_text, ha='right', fontsize=7)
        
        # Title
        ax.text(8, 9.5, 'FISHBONE (ISHIKAWA) DIAGRAM', ha='center', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Diagram saved to: {output_path}")
    
    def print_analysis(self):
        """Print formatted analysis results."""
        print("=" * 70)
        print("FISHBONE (ISHIKAWA) ANALYSIS")
        print("=" * 70)
        
        if self.analysis['problem']:
            print(f"\nPROBLEM:")
            print(f"  {self.analysis['problem']['statement']}")
            print(f"  Source: {self.analysis['problem']['source']}")
        
        print("\n" + "-" * 70)
        print("CONTRIBUTING FACTORS BY CATEGORY:")
        print("-" * 70)
        
        for cat_key, cat_info in self.CATEGORIES.items():
            factors = self.analysis['categories'][cat_key]
            print(f"\n{cat_info['name'].upper()}")
            print(f"  ({cat_info['description']})")
            
            if factors:
                for f in factors:
                    impact_icon = '🔴' if f['impact'] == 'high' else ('🟡' if f['impact'] == 'medium' else '🟢')
                    assumption = ' ⚠️ ASSUMPTION' if f['is_assumption'] else ''
                    print(f"  {impact_icon} {f['factor']}{assumption}")
                    print(f"      Source: {f['source']}")
            else:
                print("  (No factors identified)")
        
        # Prioritized factors
        if self.analysis['prioritized_factors']:
            print("\n" + "-" * 70)
            print("PRIORITIZED FACTORS (by impact):")
            print("-" * 70)
            
            for i, f in enumerate(self.analysis['prioritized_factors'][:10], 1):
                print(f"  {i}. [{f['impact'].upper()}] {f['factor']}")
                print(f"     Category: {f['category_name']}")
        
        # Root cause candidates
        if self.analysis['root_cause_candidates']:
            print("\n" + "-" * 70)
            print("ROOT CAUSE CANDIDATES:")
            print("-" * 70)
            
            for i, rc in enumerate(self.analysis['root_cause_candidates'], 1):
                print(f"\n  RC{i}: {rc['factor']}")
                print(f"        Category: {rc['category_name']}")
                print(f"        Source: {rc['source']}")
                if rc['requires_5whys']:
                    print("        → Consider 5 Whys analysis for deeper validation")
        
        # Summary
        summary = self.get_summary()
        print("\n" + "-" * 70)
        print("SUMMARY:")
        print("-" * 70)
        print(f"  Total factors: {summary['total_factors']}")
        print(f"  High-impact factors: {summary['high_impact_count']}")
        print(f"  Sources used: {summary['sources_used']}")
        print(f"  Assumptions made: {summary['assumptions_made']}")
        print("=" * 70)
    
    def run_interactive(self):
        """Run interactive Fishbone analysis session."""
        print("=" * 70)
        print("FISHBONE (ISHIKAWA) ANALYSIS")
        print("=" * 70)
        print("\nThis analysis categorizes contributing factors across 6 dimensions.\n")
        
        # Get problem statement
        print("-" * 70)
        print("STEP 1: Define the problem")
        print("-" * 70)
        problem = input("\nWhat problem are you analyzing?\n> ").strip()
        
        source = input("\nSource for this problem (or 'none'):\n> ").strip()
        if source.lower() == 'none':
            source = None
        
        self.set_problem(problem, source)
        
        # Iterate through categories
        for cat_key, cat_info in self.CATEGORIES.items():
            print("\n" + "=" * 70)
            print(f"CATEGORY: {cat_info['name'].upper()}")
            print("=" * 70)
            print(f"\n{cat_info['description']}")
            print("\nExamples:")
            for ex in cat_info['examples']:
                print(f"  • {ex}")
            
            print("\n" + "-" * 70)
            print("Enter contributing factors for this category.")
            print("Type 'done' when finished, or 'skip' if none apply.")
            print("-" * 70)
            
            factor_num = 1
            while True:
                factor = input(f"\nFactor {factor_num} (or 'done'/'skip'):\n> ").strip()
                
                if factor.lower() == 'done':
                    break
                elif factor.lower() == 'skip':
                    print(f"Skipping {cat_info['name']}")
                    break
                
                # Get impact
                print("\nImpact level?")
                print("  [H] High - Major contributor")
                print("  [M] Medium - Moderate contributor")
                print("  [L] Low - Minor contributor")
                impact_choice = input("> ").strip().upper()
                impact = 'high' if impact_choice == 'H' else ('low' if impact_choice == 'L' else 'medium')
                
                # Get source
                print("\nSource for this factor?")
                print("  [1] Document (specify)")
                print("  [2] User knowledge (no document)")
                print("  [3] Assumption")
                source_choice = input("> ").strip()
                
                source = None
                is_assumption = False
                assumption_basis = None
                
                if source_choice == '1':
                    source = input("Document name: ").strip()
                elif source_choice == '2':
                    source = "User knowledge"
                elif source_choice == '3':
                    is_assumption = True
                    assumption_basis = input("Basis for assumption: ").strip()
                    source = "ASSUMPTION"
                
                self.add_factor(
                    category=cat_key,
                    factor=factor,
                    source=source,
                    impact=impact,
                    is_assumption=is_assumption,
                    assumption_basis=assumption_basis
                )
                
                factor_num += 1
        
        # Analyze
        print("\n" + "=" * 70)
        print("ANALYZING...")
        print("=" * 70)
        
        self.prioritize_factors()
        self.identify_root_cause_candidates()
        self.analysis['metadata']['status'] = 'complete'
        
        # Print results
        print("\n")
        self.print_analysis()
        
        # Offer to save
        save = input("\nSave analysis to file? [Y/N]: ").strip().upper()
        if save == 'Y':
            filename = input("Filename (default: fishbone_analysis.json): ").strip()
            if not filename:
                filename = "fishbone_analysis.json"
            self.export(filename)
            print(f"Saved to: {filename}")
        
        # Offer diagram
        if HAS_MATPLOTLIB:
            diagram = input("\nGenerate diagram? [Y/N]: ").strip().upper()
            if diagram == 'Y':
                diagram_file = input("Filename (default: fishbone_diagram.png): ").strip()
                if not diagram_file:
                    diagram_file = "fishbone_diagram.png"
                self.generate_diagram(diagram_file)



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
        description='Fishbone (Ishikawa) diagram analysis'
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive analysis session')
    parser.add_argument('--load', '-l', help='Load existing analysis from JSON')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--diagram', '-d', help='Generate diagram to file')
    
    args = parser.parse_args()

    args.load = _validate_path(args.load, {'.htm', '.html', '.json', '.md', '.svg', '.txt', '.yaml', '.yml'}, "load")
    
    analysis = FishboneAnalysis()
    
    if args.load:
        with open(args.load) as f:
            analysis.analysis = json.load(f)
        
        # Ensure prioritization
        if not analysis.analysis['prioritized_factors']:
            analysis.prioritize_factors()
            analysis.identify_root_cause_candidates()
        
        analysis.print_analysis()
        
        if args.diagram:
            analysis.generate_diagram(args.diagram)
    
    elif args.interactive:
        analysis.run_interactive()
    
    else:
        # Default to interactive
        analysis.run_interactive()
    
    if args.output:
        analysis.export(args.output)
        print(f"Analysis saved to: {args.output}")


if __name__ == '__main__':
    main()
