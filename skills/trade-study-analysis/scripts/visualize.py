#!/usr/bin/env python3
"""
Visualization Tools for Trade Study Analysis

Generates ONLY user-selected diagrams. No auto-generation.
All diagrams include source attribution where applicable.
"""

import sys
import os
import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


# Available diagram types
DIAGRAM_TYPES = {
    1: {'name': 'decision_matrix_heatmap', 'description': 'Decision Matrix Heatmap'},
    2: {'name': 'score_bar_chart', 'description': 'Score Comparison Bar Chart'},
    3: {'name': 'radar_chart', 'description': 'Radar/Spider Chart'},
    4: {'name': 'weight_pie_chart', 'description': 'Criteria Weight Pie Chart'},
    5: {'name': 'weight_bar_chart', 'description': 'Weight Comparison Bar Chart'},
    6: {'name': 'tornado_diagram', 'description': 'Tornado Sensitivity Diagram'},
    7: {'name': 'monte_carlo_chart', 'description': 'Monte Carlo Win Frequency'},
    8: {'name': 'breakeven_chart', 'description': 'Breakeven Analysis Chart'},
    9: {'name': 'fishbone_diagram', 'description': 'Fishbone (Ishikawa) Diagram'},
    10: {'name': 'five_whys_chain', 'description': '5 Whys Chain Diagram'},
    11: {'name': 'source_coverage_matrix', 'description': 'Source Coverage Matrix'},
    12: {'name': 'confidence_heatmap', 'description': 'Confidence Level Heatmap'}
}


class TradeStudyVisualizer:
    """Generates trade study visualizations."""
    
    def __init__(self, output_dir: str = 'visualizations'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated = []
        
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        self.colors = sns.color_palette("husl", 10)
    
    def decision_matrix_heatmap(
        self,
        scores_df: pd.DataFrame,
        criteria: List[str],
        title: str = "Decision Matrix"
    ) -> str:
        """Generate decision matrix heatmap."""
        # Pivot data for heatmap
        matrix_data = []
        alternatives = scores_df['alternative'].tolist()
        
        for alt in alternatives:
            row = scores_df[scores_df['alternative'] == alt].iloc[0]
            matrix_data.append([row[f'score_{c}'] for c in criteria])
        
        matrix = np.array(matrix_data)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        sns.heatmap(
            matrix,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            xticklabels=criteria,
            yticklabels=alternatives,
            ax=ax,
            vmin=0,
            vmax=1
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Criteria', fontsize=12)
        ax.set_ylabel('Alternatives', fontsize=12)
        
        plt.tight_layout()
        
        path = self.output_dir / 'decision_matrix_heatmap.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'decision_matrix_heatmap', 'path': str(path)})
        return str(path)
    
    def score_bar_chart(
        self,
        scores_df: pd.DataFrame,
        title: str = "Alternative Scores"
    ) -> str:
        """Generate horizontal bar chart of total scores."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        alternatives = scores_df['alternative'].tolist()
        scores = scores_df['total_score'].tolist()
        
        colors = ['#2ecc71' if i == 0 else '#3498db' for i in range(len(alternatives))]
        
        bars = ax.barh(alternatives, scores, color=colors)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(score + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{score:.3f}', va='center', fontsize=10)
        
        ax.set_xlabel('Total Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(0, max(scores) * 1.15)
        
        # Add legend for winner
        winner_patch = mpatches.Patch(color='#2ecc71', label='Winner')
        ax.legend(handles=[winner_patch], loc='lower right')
        
        plt.tight_layout()
        
        path = self.output_dir / 'score_bar_chart.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'score_bar_chart', 'path': str(path)})
        return str(path)
    
    def radar_chart(
        self,
        scores_df: pd.DataFrame,
        criteria: List[str],
        title: str = "Multi-Criteria Comparison"
    ) -> str:
        """Generate radar/spider chart."""
        alternatives = scores_df['alternative'].tolist()
        n_criteria = len(criteria)
        
        # Calculate angles
        angles = [n / float(n_criteria) * 2 * np.pi for n in range(n_criteria)]
        angles += angles[:1]  # Complete the loop
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        for idx, alt in enumerate(alternatives):
            row = scores_df[scores_df['alternative'] == alt].iloc[0]
            values = [row[f'score_{c}'] for c in criteria]
            values += values[:1]  # Complete the loop
            
            ax.plot(angles, values, 'o-', linewidth=2, label=alt, color=self.colors[idx])
            ax.fill(angles, values, alpha=0.1, color=self.colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(criteria, size=10)
        ax.set_ylim(0, 1)
        ax.set_title(title, fontsize=14, fontweight='bold', y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        
        path = self.output_dir / 'radar_chart.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'radar_chart', 'path': str(path)})
        return str(path)
    
    def weight_pie_chart(
        self,
        weights: Dict[str, float],
        title: str = "Criteria Weights"
    ) -> str:
        """Generate pie chart of criterion weights."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        criteria = list(weights.keys())
        values = list(weights.values())
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=criteria,
            autopct='%1.1f%%',
            colors=self.colors[:len(criteria)],
            explode=[0.02] * len(criteria),
            shadow=True
        )
        
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        path = self.output_dir / 'weight_pie_chart.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'weight_pie_chart', 'path': str(path)})
        return str(path)
    
    def weight_bar_chart(
        self,
        weights: Dict[str, float],
        title: str = "Criteria Weight Distribution"
    ) -> str:
        """Generate bar chart of weights."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        criteria = list(weights.keys())
        values = list(weights.values())
        
        bars = ax.bar(criteria, values, color=self.colors[:len(criteria)])
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=10)
        
        ax.set_ylabel('Weight', fontsize=12)
        ax.set_xlabel('Criterion', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(values) * 1.2)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path = self.output_dir / 'weight_bar_chart.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'weight_bar_chart', 'path': str(path)})
        return str(path)
    
    def tornado_diagram(
        self,
        sensitivity_data: List[Dict],
        baseline_score: float,
        title: str = "Sensitivity Analysis (Tornado)"
    ) -> str:
        """Generate tornado diagram from sensitivity analysis."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by range
        sorted_data = sorted(sensitivity_data, key=lambda x: x['range'])
        
        criteria = [d['criterion'] for d in sorted_data]
        lows = [d['low_score'] - baseline_score for d in sorted_data]
        highs = [d['high_score'] - baseline_score for d in sorted_data]
        
        y_pos = np.arange(len(criteria))
        
        # Plot bars
        ax.barh(y_pos, lows, align='center', color='#e74c3c', alpha=0.7, label='Low')
        ax.barh(y_pos, highs, align='center', color='#2ecc71', alpha=0.7, label='High')
        
        ax.axvline(x=0, color='black', linewidth=1)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(criteria)
        ax.set_xlabel('Change in Winner Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        
        path = self.output_dir / 'tornado_diagram.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'tornado_diagram', 'path': str(path)})
        return str(path)
    
    def monte_carlo_chart(
        self,
        win_frequencies: Dict[str, Dict],
        title: str = "Monte Carlo Win Frequencies"
    ) -> str:
        """Generate Monte Carlo win frequency chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        alternatives = list(win_frequencies.keys())
        win_pcts = [win_frequencies[alt]['win_pct'] for alt in alternatives]
        
        # Sort by win percentage
        sorted_indices = np.argsort(win_pcts)[::-1]
        alternatives = [alternatives[i] for i in sorted_indices]
        win_pcts = [win_pcts[i] for i in sorted_indices]
        
        colors = ['#2ecc71' if i == 0 else '#3498db' for i in range(len(alternatives))]
        
        bars = ax.bar(alternatives, win_pcts, color=colors)
        
        for bar, pct in zip(bars, win_pcts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{pct:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel('Win Probability (%)', fontsize=12)
        ax.set_xlabel('Alternative', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        
        path = self.output_dir / 'monte_carlo_chart.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'monte_carlo_chart', 'path': str(path)})
        return str(path)
    
    def source_coverage_matrix(
        self,
        coverage_data: pd.DataFrame,
        title: str = "Source Coverage Matrix"
    ) -> str:
        """Generate source coverage matrix showing data grounding."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create coverage matrix (1 = documented, 0.5 = user-provided, 0 = gap)
        coverage_map = {'documented': 1.0, 'user_provided': 0.5, 'gap': 0.0}
        
        if 'coverage' in coverage_data.columns:
            matrix = coverage_data.pivot(
                index='alternative',
                columns='criterion',
                values='coverage'
            ).map(lambda x: coverage_map.get(x, 0))
        else:
            # Assume binary coverage
            matrix = coverage_data.pivot(
                index='alternative',
                columns='criterion',
                values='has_source'
            ).astype(float)
        
        cmap = sns.color_palette(['#e74c3c', '#f39c12', '#2ecc71'], as_cmap=True)
        
        sns.heatmap(
            matrix,
            annot=True,
            cmap=cmap,
            vmin=0,
            vmax=1,
            ax=ax,
            cbar_kws={'label': 'Source Coverage'}
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Criteria', fontsize=12)
        ax.set_ylabel('Alternatives', fontsize=12)
        
        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor='#2ecc71', label='Documented Source'),
            mpatches.Patch(facecolor='#f39c12', label='User-Provided'),
            mpatches.Patch(facecolor='#e74c3c', label='Gap/Missing')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.15, 1))
        
        plt.tight_layout()
        
        path = self.output_dir / 'source_coverage_matrix.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'source_coverage_matrix', 'path': str(path)})
        return str(path)
    
    def confidence_heatmap(
        self,
        confidence_data: pd.DataFrame,
        title: str = "Data Confidence Levels"
    ) -> str:
        """Generate confidence level heatmap."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        confidence_map = {'high': 1.0, 'medium': 0.5, 'low': 0.25, 'ungrounded': 0.0}
        
        matrix = confidence_data.pivot(
            index='alternative',
            columns='criterion',
            values='confidence'
        ).map(lambda x: confidence_map.get(x, 0))
        
        cmap = sns.color_palette(['#e74c3c', '#f39c12', '#3498db', '#2ecc71'], as_cmap=True)
        
        sns.heatmap(
            matrix,
            annot=confidence_data.pivot(
                index='alternative',
                columns='criterion',
                values='confidence'
            ),
            fmt='',
            cmap=cmap,
            vmin=0,
            vmax=1,
            ax=ax
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Criteria', fontsize=12)
        ax.set_ylabel('Alternatives', fontsize=12)
        
        plt.tight_layout()
        
        path = self.output_dir / 'confidence_heatmap.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.generated.append({'type': 'confidence_heatmap', 'path': str(path)})
        return str(path)
    
    def get_generated(self) -> List[Dict]:
        """Return list of generated diagrams."""
        return self.generated
    
    def save_selection_record(self, selected_ids: List[int], path: str = None):
        """Save record of diagram selection."""
        record = {
            'selected_diagrams': selected_ids,
            'selection_timestamp': datetime.now().isoformat(),
            'diagrams': {
                str(k): {
                    'name': v['name'],
                    'description': v['description'],
                    'selected': k in selected_ids
                }
                for k, v in DIAGRAM_TYPES.items()
            },
            'generated': self.generated
        }
        
        path = path or self.output_dir / 'diagram_selection.json'
        with open(path, 'w') as f:
            json.dump(record, f, indent=2)


def print_diagram_menu():
    """Print available diagrams for selection."""
    print("=" * 70)
    print("📊 AVAILABLE DIAGRAMS")
    print("=" * 70)
    
    print("\nDECISION ANALYSIS:")
    print(f"  [1] {DIAGRAM_TYPES[1]['description']}")
    print(f"  [2] {DIAGRAM_TYPES[2]['description']}")
    print(f"  [3] {DIAGRAM_TYPES[3]['description']}")
    
    print("\nWEIGHT ANALYSIS:")
    print(f"  [4] {DIAGRAM_TYPES[4]['description']}")
    print(f"  [5] {DIAGRAM_TYPES[5]['description']}")
    
    print("\nSENSITIVITY ANALYSIS:")
    print(f"  [6] {DIAGRAM_TYPES[6]['description']}")
    print(f"  [7] {DIAGRAM_TYPES[7]['description']}")
    print(f"  [8] {DIAGRAM_TYPES[8]['description']}")
    
    print("\nROOT CAUSE ANALYSIS:")
    print(f"  [9] {DIAGRAM_TYPES[9]['description']}")
    print(f"  [10] {DIAGRAM_TYPES[10]['description']}")
    
    print("\nDATA QUALITY:")
    print(f"  [11] {DIAGRAM_TYPES[11]['description']}")
    print(f"  [12] {DIAGRAM_TYPES[12]['description']}")
    
    print("\n" + "=" * 70)



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
        description='Generate trade study visualizations (ONLY selected diagrams)'
    )
    
    parser.add_argument('data', help='Input JSON or CSV file with trade study data')
    parser.add_argument('-o', '--output-dir', default='visualizations',
                       help='Output directory for diagrams')
    parser.add_argument('--diagrams', type=str, required=True,
                       help='Comma-separated list of diagram numbers to generate (e.g., "1,2,4,6")')
    parser.add_argument('--weights', help='Weights JSON file')
    parser.add_argument('--sensitivity', help='Sensitivity results JSON file')
    parser.add_argument('--sources', help='Source registry JSON file')
    parser.add_argument('--list', action='store_true', help='List available diagrams')
    parser.add_argument('--format', choices=['png', 'svg', 'both'], default='png',
                       help='Output format')
    
    args = parser.parse_args()

    args.data = _validate_path(args.data, {'.json'}, "data")
    args.sensitivity = _validate_path(args.sensitivity, {'.htm', '.html', '.json', '.md', '.svg', '.txt', '.yaml', '.yml'}, "sensitivity")
    args.weights = _validate_path(args.weights, {'.htm', '.html', '.json', '.md', '.svg', '.txt', '.yaml', '.yml'}, "weights")
    
    if args.list:
        print_diagram_menu()
        return
    
    # Parse diagram selection
    selected_ids = [int(x.strip()) for x in args.diagrams.split(',')]
    
    # Validate selection
    invalid = [x for x in selected_ids if x not in DIAGRAM_TYPES]
    if invalid:
        print(f"Error: Invalid diagram numbers: {invalid}")
        print_diagram_menu()
        return
    
    print(f"Generating {len(selected_ids)} selected diagrams...")
    
    # Load data
    if args.data.endswith('.json'):
        with open(args.data) as f:
            data = json.load(f)
        scores_df = pd.DataFrame(data.get('scores', []))
        weights = data.get('weights', {})
        criteria = data.get('criteria', list(weights.keys()))
    else:
        scores_df = pd.read_csv(args.data)
        criteria = [c.replace('score_', '') for c in scores_df.columns if c.startswith('score_')]
        weights = {}
    
    if args.weights:
        with open(args.weights) as f:
            weights = json.load(f)
    
    sensitivity_data = None
    if args.sensitivity:
        with open(args.sensitivity) as f:
            sensitivity_data = json.load(f)
    
    viz = TradeStudyVisualizer(args.output_dir)
    
    # Generate ONLY selected diagrams
    for diagram_id in selected_ids:
        diagram_name = DIAGRAM_TYPES[diagram_id]['name']
        print(f"  Generating: {DIAGRAM_TYPES[diagram_id]['description']}")
        
        try:
            if diagram_id == 1:
                viz.decision_matrix_heatmap(scores_df, criteria)
            elif diagram_id == 2:
                viz.score_bar_chart(scores_df)
            elif diagram_id == 3:
                viz.radar_chart(scores_df, criteria)
            elif diagram_id == 4 and weights:
                viz.weight_pie_chart(weights)
            elif diagram_id == 5 and weights:
                viz.weight_bar_chart(weights)
            elif diagram_id == 6 and sensitivity_data:
                tornado_data = sensitivity_data.get('results', {}).get('tornado', {})
                if tornado_data:
                    viz.tornado_diagram(
                        tornado_data['sensitivity_by_criterion'],
                        tornado_data['baseline_score']
                    )
            elif diagram_id == 7 and sensitivity_data:
                mc_data = sensitivity_data.get('results', {}).get('monte_carlo', {})
                if mc_data:
                    viz.monte_carlo_chart(mc_data['win_frequencies'])
            else:
                print(f"    Skipped: Missing required data")
        except Exception as e:
            print(f"    Error: {e}")
    
    # Save selection record
    viz.save_selection_record(selected_ids)
    
    print(f"\nGenerated {len(viz.generated)} diagrams in: {args.output_dir}")
    for item in viz.generated:
        print(f"  - {item['path']}")


if __name__ == '__main__':
    main()
