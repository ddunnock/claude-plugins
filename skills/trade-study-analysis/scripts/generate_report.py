#!/usr/bin/env python3
"""
Report Generator for Trade Study Analysis

Generates final trade study report with:
- Mandatory assumption review
- Source citations for all claims
- Only user-selected diagrams
- Complete audit trail

WILL NOT generate report until all gates pass.
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys


class ReportGenerator:
    """Generates trade study reports with mandatory verification gates."""
    
    def __init__(
        self,
        study_data: Dict[str, Any],
        sources: Dict[str, Any],
        assumptions: Dict[str, Any],
        diagrams: Dict[str, Any]
    ):
        self.study_data = study_data
        self.sources = sources
        self.assumptions = assumptions
        self.diagrams = diagrams
        self.gates_status = {}
    
    def check_gate(self, gate_name: str, condition: bool, message: str) -> bool:
        """Check a gate condition."""
        self.gates_status[gate_name] = {
            'passed': condition,
            'message': message,
            'checked_at': datetime.now().isoformat()
        }
        return condition
    
    def verify_all_gates(self) -> Dict[str, Any]:
        """Verify all mandatory gates before report generation."""
        gates = {}
        
        # Gate 1: Assumptions resolved
        pending = [a for a in self.assumptions.get('assumptions', [])
                  if a.get('status') == 'pending']
        gates['assumptions_resolved'] = self.check_gate(
            'assumptions_resolved',
            len(pending) == 0,
            f"{len(pending)} pending assumptions" if pending else "All assumptions resolved"
        )
        
        # Gate 2: Diagrams selected
        selected = self.diagrams.get('selected_diagrams', [])
        gates['diagrams_selected'] = self.check_gate(
            'diagrams_selected',
            len(selected) > 0,
            f"{len(selected)} diagrams selected" if selected else "No diagrams selected"
        )
        
        # Gate 3: Sources registered
        sources_list = self.sources.get('sources', [])
        gates['sources_registered'] = self.check_gate(
            'sources_registered',
            len(sources_list) > 0,
            f"{len(sources_list)} sources registered" if sources_list else "No sources registered"
        )
        
        # Gate 4: Study data complete
        has_results = 'scores' in self.study_data or 'results' in self.study_data
        gates['data_complete'] = self.check_gate(
            'data_complete',
            has_results,
            "Study data present" if has_results else "Missing study data"
        )
        
        # Overall status
        all_passed = all(g['passed'] for g in gates.values())
        
        return {
            'gates': gates,
            'all_passed': all_passed,
            'blocking_gates': [k for k, v in gates.items() if not v['passed']]
        }
    
    def format_source_citation(self, source_id: str) -> str:
        """Format a source citation."""
        for source in self.sources.get('sources', []):
            if source['id'] == source_id:
                parts = [source['name']]
                if source.get('version'):
                    parts.append(f"v{source['version']}")
                if source.get('date'):
                    parts.append(source['date'])
                confidence = source.get('confidence', 'medium')
                return f"{', '.join(parts)}; Confidence: {confidence.capitalize()}"
        return f"[Source {source_id} not found]"
    
    def generate_markdown(self, sections: List[str]) -> str:
        """Generate markdown report."""
        lines = []
        
        # Title
        title = self.study_data.get('study_name', 'Trade Study Report')
        lines.append(f"# {title}\n")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        # Executive Summary
        if 'A' in sections:
            lines.extend(self._section_executive_summary())
        
        # Introduction
        if 'B' in sections:
            lines.extend(self._section_introduction())
        
        # Problem Statement
        if 'C' in sections:
            lines.extend(self._section_problem_statement())
        
        # Alternatives
        if 'D' in sections:
            lines.extend(self._section_alternatives())
        
        # Methodology
        if 'E' in sections:
            lines.extend(self._section_methodology())
        
        # Data Collection
        if 'F' in sections:
            lines.extend(self._section_data_collection())
        
        # Results
        if 'G' in sections:
            lines.extend(self._section_results())
        
        # Sensitivity
        if 'H' in sections:
            lines.extend(self._section_sensitivity())
        
        # Findings
        if 'I' in sections:
            lines.extend(self._section_findings())
        
        # Assumptions
        if 'J' in sections:
            lines.extend(self._section_assumptions())
        
        # Sources
        if 'K' in sections:
            lines.extend(self._section_sources())
        
        # Appendices
        if 'L' in sections:
            lines.extend(self._section_appendices())
        
        return '\n'.join(lines)
    
    def _section_executive_summary(self) -> List[str]:
        """Generate executive summary section."""
        lines = ["\n## Executive Summary\n"]
        
        # Winner
        if 'winner' in self.study_data:
            winner = self.study_data['winner']
            score = self.study_data.get('winner_score', 'N/A')
            lines.append(f"**Recommendation:** {winner} (Score: {score})\n")
        
        # Confidence
        if 'robustness' in self.study_data:
            rob = self.study_data['robustness']
            lines.append(f"**Decision Confidence:** {rob.get('overall_robustness', 'N/A').upper()}\n")
        
        # Key findings
        lines.append("\n**Key Findings:**\n")
        if 'findings' in self.study_data:
            for finding in self.study_data['findings']:
                lines.append(f"- {finding}\n")
        
        return lines
    
    def _section_introduction(self) -> List[str]:
        """Generate introduction section."""
        lines = ["\n## Introduction\n"]
        
        lines.append("### Purpose\n")
        if 'purpose' in self.study_data:
            lines.append(f"{self.study_data['purpose']}\n")
        
        lines.append("\n### Scope\n")
        if 'scope' in self.study_data:
            lines.append(f"{self.study_data['scope']}\n")
        
        lines.append("\n### Methodology\n")
        lines.append("This trade study follows the DAU 9-Step Trade Study Process.\n")
        
        return lines
    
    def _section_problem_statement(self) -> List[str]:
        """Generate problem statement section."""
        lines = ["\n## Problem Statement\n"]
        
        if 'problem_statement' in self.study_data:
            ps = self.study_data['problem_statement']
            lines.append(f"> {ps}\n")
        
        # Root cause
        if 'root_cause' in self.study_data:
            lines.append("\n### Root Cause Analysis\n")
            lines.append(f"{self.study_data['root_cause']}\n")
        
        return lines
    
    def _section_alternatives(self) -> List[str]:
        """Generate alternatives section."""
        lines = ["\n## Alternatives Evaluated\n"]
        
        alternatives = self.study_data.get('alternatives', [])
        for alt in alternatives:
            name = alt.get('name', alt.get('id', 'Unknown'))
            lines.append(f"\n### {name}\n")
            if 'description' in alt:
                lines.append(f"{alt['description']}\n")
        
        return lines
    
    def _section_methodology(self) -> List[str]:
        """Generate methodology section."""
        lines = ["\n## Evaluation Methodology\n"]
        
        # Criteria
        lines.append("### Evaluation Criteria\n")
        criteria = self.study_data.get('criteria', [])
        if criteria:
            lines.append("| Criterion | Weight | Direction | Source |\n")
            lines.append("|-----------|--------|-----------|--------|\n")
            for crit in criteria:
                name = crit.get('name', crit.get('id', 'N/A'))
                weight = crit.get('weight', 'N/A')
                direction = crit.get('direction', 'N/A')
                source = crit.get('source', 'User-defined')
                lines.append(f"| {name} | {weight} | {direction} | {source} |\n")
        
        # Weighting method
        if 'weighting_method' in self.study_data:
            lines.append(f"\n**Weighting Method:** {self.study_data['weighting_method']}\n")
        
        # Normalization
        if 'normalization_method' in self.study_data:
            lines.append(f"**Normalization:** {self.study_data['normalization_method']}\n")
        
        # Aggregation
        if 'aggregation_method' in self.study_data:
            lines.append(f"**Aggregation:** {self.study_data['aggregation_method']}\n")
        
        return lines
    
    def _section_data_collection(self) -> List[str]:
        """Generate data collection section."""
        lines = ["\n## Data Collection Summary\n"]
        
        # Sources used
        sources = self.sources.get('sources', [])
        lines.append(f"\n**Sources Registered:** {len(sources)}\n")
        
        # Source coverage
        coverage = self.sources.get('coverage', {})
        if coverage:
            lines.append(f"- Documented sources: {coverage.get('documented', 0)}%\n")
            lines.append(f"- User-provided: {coverage.get('user_provided', 0)}%\n")
            lines.append(f"- Data gaps: {coverage.get('gaps', 0)}%\n")
        
        # Confidence distribution
        confidence = self.sources.get('confidence_distribution', {})
        if confidence:
            lines.append("\n**Data Confidence:**\n")
            for level, count in confidence.items():
                if count > 0:
                    lines.append(f"- {level.capitalize()}: {count} data points\n")
        
        return lines
    
    def _section_results(self) -> List[str]:
        """Generate results section."""
        lines = ["\n## Analysis Results\n"]
        
        # Decision matrix
        lines.append("### Decision Matrix\n")
        
        scores = self.study_data.get('scores', [])
        if scores:
            # Build header
            criteria = self.study_data.get('criteria', [])
            header = "| Alternative | " + " | ".join([c.get('name', c.get('id', '')) for c in criteria]) + " | Total | Rank |\n"
            lines.append(header)
            lines.append("|" + "---|" * (len(criteria) + 3) + "\n")
            
            for score in scores:
                row = f"| {score.get('alternative', 'N/A')} |"
                for crit in criteria:
                    val = score.get(f"score_{crit.get('id', crit.get('name', ''))}", 'N/A')
                    if isinstance(val, float):
                        val = f"{val:.3f}"
                    row += f" {val} |"
                row += f" {score.get('total_score', 'N/A'):.3f} | {score.get('rank', 'N/A')} |\n"
                lines.append(row)
        
        # Include selected diagrams
        lines.append("\n### Visualizations\n")
        selected = self.diagrams.get('selected_diagrams', [])
        for diag_id in selected:
            diag_info = self.diagrams.get('diagrams', {}).get(str(diag_id), {})
            if diag_info.get('selected'):
                lines.append(f"- {diag_info.get('description', f'Diagram {diag_id}')}\n")
        
        return lines
    
    def _section_sensitivity(self) -> List[str]:
        """Generate sensitivity analysis section."""
        lines = ["\n## Sensitivity Analysis\n"]
        
        sensitivity = self.study_data.get('sensitivity', {})
        
        # Robustness assessment
        robustness = sensitivity.get('robustness', {})
        if robustness:
            overall = robustness.get('overall_robustness', 'N/A')
            lines.append(f"**Overall Robustness:** {overall.upper()}\n")
            
            factors = robustness.get('factors', [])
            if factors:
                lines.append("\n| Factor | Value | Assessment |\n")
                lines.append("|--------|-------|------------|\n")
                for f in factors:
                    lines.append(f"| {f['factor']} | {f['value']} | {f['robustness'].upper()} |\n")
        
        # Monte Carlo results
        mc = sensitivity.get('monte_carlo', {})
        if mc:
            lines.append("\n### Monte Carlo Simulation\n")
            lines.append(f"Iterations: {mc.get('n_iterations', 'N/A')}\n")
            
            win_freq = mc.get('win_frequencies', {})
            if win_freq:
                lines.append("\n| Alternative | Win Probability |\n")
                lines.append("|-------------|----------------|\n")
                for alt, data in win_freq.items():
                    lines.append(f"| {alt} | {data['win_pct']:.1f}% |\n")
        
        return lines
    
    def _section_findings(self) -> List[str]:
        """Generate findings and recommendation section."""
        lines = ["\n## Findings and Recommendation\n"]
        
        # Recommendation
        if 'winner' in self.study_data:
            winner = self.study_data['winner']
            lines.append(f"### Recommendation\n")
            lines.append(f"Based on the analysis, **{winner}** is recommended.\n")
            
            # Supporting rationale
            if 'recommendation_rationale' in self.study_data:
                lines.append(f"\n**Rationale:**\n")
                for point in self.study_data['recommendation_rationale']:
                    lines.append(f"- {point}\n")
        
        return lines
    
    def _section_assumptions(self) -> List[str]:
        """Generate assumptions and limitations section."""
        lines = ["\n## Assumptions and Limitations\n"]
        
        assumptions = self.assumptions.get('assumptions', [])
        
        # Summary
        summary = self.assumptions.get('summary', {})
        lines.append(f"**Total Assumptions:** {summary.get('total', len(assumptions))}\n")
        lines.append(f"- Approved: {summary.get('approved', 0)}\n")
        lines.append(f"- Pending: {summary.get('pending', 0)}\n")
        
        # List by category
        categories = {}
        for a in assumptions:
            cat = a.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(a)
        
        for cat, cat_assumptions in categories.items():
            lines.append(f"\n### {cat.replace('_', ' ').title()} Assumptions\n")
            for a in cat_assumptions:
                status = "✓" if a['status'] in ['approved', 'modified'] else "⚠️"
                lines.append(f"\n**[{a['id']}]** {a['description']} {status}\n")
                lines.append(f"- Basis: {a.get('basis', 'N/A')}\n")
                lines.append(f"- Impact if incorrect: {a.get('impact_level', 'N/A').upper()}\n")
                lines.append(f"- Status: {a['status'].capitalize()}\n")
        
        return lines
    
    def _section_sources(self) -> List[str]:
        """Generate source references section."""
        lines = ["\n## Source References\n"]
        
        sources = self.sources.get('sources', [])
        
        for source in sorted(sources, key=lambda x: x['id']):
            lines.append(f"\n**[{source['id']}]** {source['name']}\n")
            lines.append(f"- Type: {source.get('type_description', source.get('type', 'N/A'))}\n")
            lines.append(f"- Version: {source.get('version', 'N/A')}\n")
            lines.append(f"- Date: {source.get('date', 'N/A')}\n")
            lines.append(f"- Confidence: {source.get('confidence', 'N/A').capitalize()}\n")
            if source.get('notes'):
                lines.append(f"- Notes: {source['notes']}\n")
        
        # Data gaps
        gaps = self.sources.get('gaps', [])
        open_gaps = [g for g in gaps if g.get('status') == 'open']
        if open_gaps:
            lines.append("\n### Unresolved Data Gaps\n")
            for gap in open_gaps:
                lines.append(f"- {gap['description']} (needs: {gap['requested_source_type']})\n")
        
        return lines
    
    def _section_appendices(self) -> List[str]:
        """Generate appendices section."""
        lines = ["\n## Appendices\n"]
        lines.append("\n### A. Detailed Calculations\n")
        lines.append("See accompanying data files for full calculation audit trail.\n")
        
        lines.append("\n### B. Diagram Selection Record\n")
        selected = self.diagrams.get('selected_diagrams', [])
        lines.append(f"User selected {len(selected)} diagrams for inclusion.\n")
        
        return lines
    
    def generate(self, sections: List[str], output_path: str, format: str = 'markdown'):
        """Generate report if all gates pass."""
        # Verify gates
        gate_results = self.verify_all_gates()
        
        if not gate_results['all_passed']:
            blocking = gate_results['blocking_gates']
            raise RuntimeError(
                f"Cannot generate report. Blocking gates: {blocking}\n"
                f"Please resolve these issues first."
            )
        
        # Generate report
        if format == 'markdown':
            content = self.generate_markdown(sections)
            
            with open(output_path, 'w') as f:
                f.write(content)
            
            return output_path
        else:
            raise ValueError(f"Unsupported format: {format}")




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
        description='Generate trade study report (requires all gates to pass)'
    )
    
    parser.add_argument('study_data', help='Study data JSON file')
    parser.add_argument('-o', '--output', default='trade_study_report.md',
                       help='Output file path')
    parser.add_argument('--sources', required=True, help='Source registry JSON')
    parser.add_argument('--assumptions', required=True, help='Assumption registry JSON')
    parser.add_argument('--diagrams', required=True, help='Diagram selection JSON')
    parser.add_argument('--sections', default='ABCDEFGHIJK',
                       help='Sections to include (e.g., "ACGI" for Executive/Problem/Results/Findings)')
    parser.add_argument('--format', choices=['markdown'], default='markdown',
                       help='Output format')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check gates, do not generate')
    
    args = parser.parse_args()

    args.study_data = _validate_path(args.study_data, {'.json'}, "study data file")
    args.output = _validate_path(args.output, {'.md', '.html'}, "output file")
    args.sources = _validate_path(args.sources, {'.json'}, "sources file")
    args.assumptions = _validate_path(args.assumptions, {'.json'}, "assumptions file")
    args.diagrams = _validate_path(args.diagrams, {'.json'}, "diagrams file")
    
    # Load data
    with open(args.study_data) as f:
        study_data = json.load(f)
    
    with open(args.sources) as f:
        sources = json.load(f)
    
    with open(args.assumptions) as f:
        assumptions = json.load(f)
    
    with open(args.diagrams) as f:
        diagrams = json.load(f)
    
    generator = ReportGenerator(study_data, sources, assumptions, diagrams)
    
    # Check gates
    gate_results = generator.verify_all_gates()
    
    print("=" * 60)
    print("GATE VERIFICATION")
    print("=" * 60)
    
    for gate, result in gate_results['gates'].items():
        status = "✓ PASS" if result['passed'] else "✗ FAIL"
        print(f"  {gate}: {status} - {result['message']}")
    
    print("-" * 60)
    
    if not gate_results['all_passed']:
        print(f"⛔ BLOCKED: {gate_results['blocking_gates']}")
        print("\nResolve blocking issues before generating report.")
        return 1
    
    if args.check_only:
        print("✅ All gates pass. Ready for report generation.")
        return 0
    
    # Generate report
    print("✅ All gates pass. Generating report...")
    
    sections = list(args.sections.upper())
    output_path = generator.generate(sections, args.output, args.format)
    
    print(f"\nReport generated: {output_path}")
    return 0


if __name__ == '__main__':
    exit(main())
