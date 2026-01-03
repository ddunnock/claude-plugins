#!/usr/bin/env python3
"""
Sensitivity Analysis Tools for Trade Study Analysis

Performs weight zeroing, tornado, Monte Carlo, and breakeven analyses.
All analyses require user-specified parameters - no auto-selection.
"""

import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats


class SensitivityAnalyzer:
    """Performs sensitivity analyses on trade study results."""
    
    METHODS = ['weight_zeroing', 'tornado', 'monte_carlo', 'breakeven']
    
    def __init__(self, scores_df: pd.DataFrame, weights: Dict[str, float]):
        self.scores_df = scores_df
        self.weights = weights
        self.criteria = list(weights.keys())
        self.alternatives = scores_df['alternative'].tolist()
        self.baseline_winner = scores_df.iloc[0]['alternative']
        self.baseline_scores = {row['alternative']: row['total_score'] 
                               for _, row in scores_df.iterrows()}
        self.results = {}
        self.audit_log = []
    
    def _recalculate_scores(self, new_weights: Dict[str, float]) -> Dict[str, float]:
        """Recalculate total scores with new weights."""
        # Normalize weights to sum to 1
        total = sum(new_weights.values())
        norm_weights = {k: v/total for k, v in new_weights.items()}
        
        scores = {}
        for alt in self.alternatives:
            row = self.scores_df[self.scores_df['alternative'] == alt].iloc[0]
            total_score = sum(
                row[f'score_{c}'] * norm_weights[c]
                for c in self.criteria
            )
            scores[alt] = total_score
        
        return scores
    
    def _get_winner(self, scores: Dict[str, float]) -> str:
        """Get winner from scores dict."""
        return max(scores, key=scores.get)
    
    def weight_zeroing(self) -> Dict[str, Any]:
        """
        DAU weight zeroing analysis.
        Sets each criterion weight to zero and redistributes.
        """
        results = {
            'method': 'weight_zeroing',
            'baseline_winner': self.baseline_winner,
            'zeroing_results': []
        }
        
        for criterion in self.criteria:
            # Zero this criterion, redistribute others
            new_weights = {c: w for c, w in self.weights.items() if c != criterion}
            
            new_scores = self._recalculate_scores(new_weights)
            new_winner = self._get_winner(new_scores)
            
            results['zeroing_results'].append({
                'criterion_zeroed': criterion,
                'original_weight': self.weights[criterion],
                'new_scores': new_scores,
                'new_winner': new_winner,
                'ranking_changed': new_winner != self.baseline_winner
            })
        
        # Identify decision drivers
        results['decision_drivers'] = [
            r['criterion_zeroed'] for r in results['zeroing_results']
            if r['ranking_changed']
        ]
        
        self.results['weight_zeroing'] = results
        self._log('weight_zeroing', results)
        return results
    
    def tornado(self, variation_pct: float = 0.2) -> Dict[str, Any]:
        """
        Tornado analysis - varies each weight by specified percentage.
        
        Args:
            variation_pct: Variation percentage (e.g., 0.2 = ±20%)
        """
        results = {
            'method': 'tornado',
            'variation_pct': variation_pct,
            'baseline_winner': self.baseline_winner,
            'baseline_score': self.baseline_scores[self.baseline_winner],
            'sensitivity_by_criterion': []
        }
        
        for criterion in self.criteria:
            base_weight = self.weights[criterion]
            
            # Low variation
            low_weights = self.weights.copy()
            low_weights[criterion] = base_weight * (1 - variation_pct)
            low_scores = self._recalculate_scores(low_weights)
            low_winner_score = low_scores[self.baseline_winner]
            
            # High variation
            high_weights = self.weights.copy()
            high_weights[criterion] = base_weight * (1 + variation_pct)
            high_scores = self._recalculate_scores(high_weights)
            high_winner_score = high_scores[self.baseline_winner]
            
            # Check if ranking flips
            low_winner = self._get_winner(low_scores)
            high_winner = self._get_winner(high_scores)
            
            results['sensitivity_by_criterion'].append({
                'criterion': criterion,
                'base_weight': base_weight,
                'low_weight': base_weight * (1 - variation_pct),
                'high_weight': base_weight * (1 + variation_pct),
                'low_score': low_winner_score,
                'high_score': high_winner_score,
                'range': abs(high_winner_score - low_winner_score),
                'flips_at_low': low_winner != self.baseline_winner,
                'flips_at_high': high_winner != self.baseline_winner
            })
        
        # Sort by range (most sensitive first)
        results['sensitivity_by_criterion'].sort(
            key=lambda x: x['range'], reverse=True
        )
        
        # Add ranking
        for i, item in enumerate(results['sensitivity_by_criterion']):
            item['sensitivity_rank'] = i + 1
        
        self.results['tornado'] = results
        self._log('tornado', results)
        return results
    
    def monte_carlo(
        self,
        n_iterations: int = 10000,
        distribution: str = 'normal',
        params: Optional[Dict[str, Dict]] = None
    ) -> Dict[str, Any]:
        """
        Monte Carlo simulation.
        
        Args:
            n_iterations: Number of simulation iterations
            distribution: 'normal', 'uniform', or 'triangular'
            params: Per-criterion distribution parameters
                    For normal: {'criterion': {'std': 0.05}}
                    For uniform: {'criterion': {'min': 0.1, 'max': 0.3}}
                    For triangular: {'criterion': {'min': 0.1, 'mode': 0.2, 'max': 0.3}}
        """
        results = {
            'method': 'monte_carlo',
            'n_iterations': n_iterations,
            'distribution': distribution,
            'params': params,
            'baseline_winner': self.baseline_winner
        }
        
        win_counts = {alt: 0 for alt in self.alternatives}
        score_samples = {alt: [] for alt in self.alternatives}
        
        for _ in range(n_iterations):
            # Sample weights
            sampled_weights = {}
            for criterion in self.criteria:
                base = self.weights[criterion]
                
                if params and criterion in params:
                    p = params[criterion]
                    if distribution == 'normal':
                        std = p.get('std', base * 0.1)
                        sampled = np.random.normal(base, std)
                    elif distribution == 'uniform':
                        low = p.get('min', base * 0.8)
                        high = p.get('max', base * 1.2)
                        sampled = np.random.uniform(low, high)
                    elif distribution == 'triangular':
                        low = p.get('min', base * 0.8)
                        mode = p.get('mode', base)
                        high = p.get('max', base * 1.2)
                        sampled = np.random.triangular(low, mode, high)
                else:
                    # Default: normal with 10% std
                    sampled = np.random.normal(base, base * 0.1)
                
                sampled_weights[criterion] = max(0, sampled)  # Ensure non-negative
            
            # Calculate scores
            scores = self._recalculate_scores(sampled_weights)
            winner = self._get_winner(scores)
            win_counts[winner] += 1
            
            for alt, score in scores.items():
                score_samples[alt].append(score)
        
        # Calculate statistics
        results['win_frequencies'] = {
            alt: {
                'wins': count,
                'win_pct': count / n_iterations * 100
            }
            for alt, count in win_counts.items()
        }
        
        results['score_statistics'] = {}
        for alt in self.alternatives:
            samples = score_samples[alt]
            results['score_statistics'][alt] = {
                'mean': float(np.mean(samples)),
                'std': float(np.std(samples)),
                'ci_95_low': float(np.percentile(samples, 2.5)),
                'ci_95_high': float(np.percentile(samples, 97.5)),
                'min': float(np.min(samples)),
                'max': float(np.max(samples))
            }
        
        # Sort by win percentage
        sorted_alts = sorted(
            results['win_frequencies'].items(),
            key=lambda x: x[1]['win_pct'],
            reverse=True
        )
        results['ranking'] = [alt for alt, _ in sorted_alts]
        results['most_likely_winner'] = results['ranking'][0]
        results['confidence'] = results['win_frequencies'][results['ranking'][0]]['win_pct']
        
        self.results['monte_carlo'] = results
        self._log('monte_carlo', {k: v for k, v in results.items() if k != 'score_samples'})
        return results
    
    def breakeven(self) -> Dict[str, Any]:
        """
        Breakeven analysis - calculates exact weight change to flip winner.
        """
        results = {
            'method': 'breakeven',
            'baseline_winner': self.baseline_winner,
            'breakeven_points': []
        }
        
        # Get runner-up
        sorted_alts = sorted(
            self.baseline_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        if len(sorted_alts) < 2:
            results['error'] = 'Need at least 2 alternatives'
            return results
        
        runner_up = sorted_alts[1][0]
        score_gap = sorted_alts[0][1] - sorted_alts[1][1]
        
        results['runner_up'] = runner_up
        results['score_gap'] = score_gap
        
        winner_row = self.scores_df[self.scores_df['alternative'] == self.baseline_winner].iloc[0]
        runner_row = self.scores_df[self.scores_df['alternative'] == runner_up].iloc[0]
        
        for criterion in self.criteria:
            # Calculate breakeven weight
            winner_score = winner_row[f'score_{criterion}']
            runner_score = runner_row[f'score_{criterion}']
            score_diff = runner_score - winner_score
            
            if score_diff == 0:
                # Same score on this criterion - can't flip with this one
                results['breakeven_points'].append({
                    'criterion': criterion,
                    'current_weight': self.weights[criterion],
                    'breakeven_weight': None,
                    'change_required': None,
                    'can_flip': False,
                    'reason': 'Equal scores on this criterion'
                })
            else:
                # Calculate weight needed for runner-up to win
                # This is approximate - full calculation depends on redistribution
                base_weight = self.weights[criterion]
                
                # Binary search for breakeven
                low, high = 0.0, 1.0
                breakeven_weight = None
                
                for _ in range(50):  # Max iterations
                    mid = (low + high) / 2
                    test_weights = self.weights.copy()
                    test_weights[criterion] = mid
                    test_scores = self._recalculate_scores(test_weights)
                    
                    if self._get_winner(test_scores) != self.baseline_winner:
                        if score_diff > 0:
                            high = mid
                        else:
                            low = mid
                        breakeven_weight = mid
                    else:
                        if score_diff > 0:
                            low = mid
                        else:
                            high = mid
                    
                    if high - low < 0.001:
                        break
                
                results['breakeven_points'].append({
                    'criterion': criterion,
                    'current_weight': base_weight,
                    'breakeven_weight': breakeven_weight,
                    'change_required': breakeven_weight - base_weight if breakeven_weight else None,
                    'can_flip': breakeven_weight is not None,
                    'change_pct': ((breakeven_weight - base_weight) / base_weight * 100) if breakeven_weight else None
                })
        
        # Find easiest flip
        flippable = [bp for bp in results['breakeven_points'] if bp['can_flip'] and bp['change_required']]
        if flippable:
            easiest = min(flippable, key=lambda x: abs(x['change_required']))
            results['easiest_flip'] = easiest
        
        self.results['breakeven'] = results
        self._log('breakeven', results)
        return results
    
    def _log(self, method: str, results: Dict):
        """Log analysis to audit trail."""
        self.audit_log.append({
            'method': method,
            'results_summary': {k: v for k, v in results.items() 
                              if k not in ['score_samples']},
            'timestamp': datetime.now().isoformat()
        })
    
    def get_robustness_assessment(self) -> Dict[str, Any]:
        """Assess overall decision robustness based on analyses performed."""
        assessment = {
            'baseline_winner': self.baseline_winner,
            'analyses_performed': list(self.results.keys()),
            'factors': []
        }
        
        # Weight zeroing assessment
        if 'weight_zeroing' in self.results:
            wz = self.results['weight_zeroing']
            n_drivers = len(wz['decision_drivers'])
            n_criteria = len(self.criteria)
            assessment['factors'].append({
                'factor': 'Decision drivers',
                'value': f"{n_drivers}/{n_criteria} criteria flip decision when zeroed",
                'robustness': 'high' if n_drivers <= 1 else 'medium' if n_drivers <= 2 else 'low'
            })
        
        # Monte Carlo assessment
        if 'monte_carlo' in self.results:
            mc = self.results['monte_carlo']
            win_pct = mc['confidence']
            assessment['factors'].append({
                'factor': 'Win probability',
                'value': f"{win_pct:.1f}% win rate for leader",
                'robustness': 'high' if win_pct >= 80 else 'medium' if win_pct >= 60 else 'low'
            })
        
        # Breakeven assessment
        if 'breakeven' in self.results:
            be = self.results['breakeven']
            if 'easiest_flip' in be:
                change = abs(be['easiest_flip']['change_required'])
                assessment['factors'].append({
                    'factor': 'Minimum weight change to flip',
                    'value': f"{change:.3f} weight units",
                    'robustness': 'high' if change >= 0.15 else 'medium' if change >= 0.05 else 'low'
                })
        
        # Overall assessment
        if assessment['factors']:
            robustness_scores = {'high': 3, 'medium': 2, 'low': 1}
            avg_score = np.mean([robustness_scores[f['robustness']] for f in assessment['factors']])
            assessment['overall_robustness'] = 'high' if avg_score >= 2.5 else 'medium' if avg_score >= 1.5 else 'low'
        
        return assessment
    
    def save_results(self, path: str):
        """Save all results to JSON."""
        output = {
            'baseline_winner': self.baseline_winner,
            'baseline_scores': self.baseline_scores,
            'weights': self.weights,
            'results': self.results,
            'robustness': self.get_robustness_assessment(),
            'audit_log': self.audit_log,
            'exported_at': datetime.now().isoformat()
        }
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Perform sensitivity analysis')
    
    parser.add_argument('scores', help='Scores CSV from score.py')
    parser.add_argument('weights', help='Weights JSON file')
    parser.add_argument('-o', '--output', default='sensitivity_results.json',
                       help='Output JSON file')
    parser.add_argument('--method', choices=['all'] + SensitivityAnalyzer.METHODS,
                       default='all', help='Analysis method(s)')
    parser.add_argument('--variation', type=float, default=0.2,
                       help='Tornado variation percentage (default: 0.2 = ±20%%)')
    parser.add_argument('--iterations', type=int, default=10000,
                       help='Monte Carlo iterations (default: 10000)')
    parser.add_argument('--distribution', choices=['normal', 'uniform', 'triangular'],
                       default='normal', help='Monte Carlo distribution')
    parser.add_argument('--mc-params', help='JSON file with Monte Carlo distribution parameters')
    parser.add_argument('--report', action='store_true', help='Print summary report')
    
    args = parser.parse_args()
    
    # Load data
    scores_df = pd.read_csv(args.scores)
    with open(args.weights) as f:
        weights = json.load(f)
    
    mc_params = None
    if args.mc_params:
        with open(args.mc_params) as f:
            mc_params = json.load(f)
    
    analyzer = SensitivityAnalyzer(scores_df, weights)
    
    # Run analyses
    methods = SensitivityAnalyzer.METHODS if args.method == 'all' else [args.method]
    
    for method in methods:
        if method == 'weight_zeroing':
            analyzer.weight_zeroing()
        elif method == 'tornado':
            analyzer.tornado(args.variation)
        elif method == 'monte_carlo':
            analyzer.monte_carlo(args.iterations, args.distribution, mc_params)
        elif method == 'breakeven':
            analyzer.breakeven()
    
    # Save results
    analyzer.save_results(args.output)
    print(f"Results saved to: {args.output}")
    
    if args.report:
        print("\n" + "=" * 60)
        print("SENSITIVITY ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"\nBaseline winner: {analyzer.baseline_winner}")
        
        robustness = analyzer.get_robustness_assessment()
        print(f"\nOverall robustness: {robustness.get('overall_robustness', 'N/A').upper()}")
        
        for factor in robustness.get('factors', []):
            print(f"  • {factor['factor']}: {factor['value']} ({factor['robustness']})")
        
        if 'monte_carlo' in analyzer.results:
            mc = analyzer.results['monte_carlo']
            print(f"\nMonte Carlo win probabilities:")
            for alt in mc['ranking']:
                pct = mc['win_frequencies'][alt]['win_pct']
                print(f"  {alt}: {pct:.1f}%")


if __name__ == '__main__':
    main()
