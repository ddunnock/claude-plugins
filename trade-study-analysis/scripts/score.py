#!/usr/bin/env python3
"""
Scoring and Aggregation Tools for Trade Study Analysis

Applies scoring functions and aggregates weighted scores.
All operations maintain full audit trail and source traceability.
"""

import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class Scorer:
    """Calculates scores and aggregates results."""
    
    SCORING_FUNCTIONS = ['linear', 'step', 'exponential', 'sigmoid', 'piecewise']
    AGGREGATION_METHODS = ['weighted_sum', 'weighted_product', 'topsis']
    
    def __init__(self):
        self.audit_log = []
    
    def _log_operation(self, operation: str, inputs: Dict, outputs: Dict):
        """Log scoring operation."""
        self.audit_log.append({
            'operation': operation,
            'inputs': inputs,
            'outputs': outputs,
            'timestamp': datetime.now().isoformat()
        })
    
    # Scoring Functions
    def score_linear(self, values: np.ndarray, min_score: float = 0, max_score: float = 1) -> np.ndarray:
        """Linear scoring - direct proportional relationship."""
        return values * (max_score - min_score) + min_score
    
    def score_step(self, values: np.ndarray, thresholds: List[float], scores: List[float]) -> np.ndarray:
        """Step function scoring - discrete levels based on thresholds."""
        result = np.zeros_like(values, dtype=float)
        for i, v in enumerate(values):
            for j, threshold in enumerate(thresholds):
                if v >= threshold:
                    result[i] = scores[j]
        return result
    
    def score_exponential(self, values: np.ndarray, base: float = 2, direction: str = 'increasing') -> np.ndarray:
        """Exponential scoring - increasing/decreasing marginal returns."""
        if direction == 'increasing':
            return (np.power(base, values) - 1) / (base - 1)
        else:
            return 1 - (np.power(base, 1 - values) - 1) / (base - 1)
    
    def score_sigmoid(self, values: np.ndarray, midpoint: float = 0.5, steepness: float = 10) -> np.ndarray:
        """Sigmoid (S-curve) scoring - smooth transition with saturation."""
        return 1 / (1 + np.exp(-steepness * (values - midpoint)))
    
    def score_piecewise(self, values: np.ndarray, breakpoints: List[float], slopes: List[float]) -> np.ndarray:
        """Piecewise linear scoring - different slopes in different regions."""
        result = np.zeros_like(values, dtype=float)
        for i, v in enumerate(values):
            score = 0
            prev_bp = 0
            for j, bp in enumerate(breakpoints):
                if v <= bp:
                    score += slopes[j] * (v - prev_bp)
                    break
                else:
                    score += slopes[j] * (bp - prev_bp)
                prev_bp = bp
            else:
                # Beyond last breakpoint
                if len(slopes) > len(breakpoints):
                    score += slopes[-1] * (v - breakpoints[-1])
            result[i] = score
        return result
    
    def apply_scoring(self, values: np.ndarray, function: str, **params) -> np.ndarray:
        """Apply specified scoring function."""
        if function == 'linear':
            return self.score_linear(values, params.get('min_score', 0), params.get('max_score', 1))
        elif function == 'step':
            return self.score_step(values, params['thresholds'], params['scores'])
        elif function == 'exponential':
            return self.score_exponential(values, params.get('base', 2), params.get('direction', 'increasing'))
        elif function == 'sigmoid':
            return self.score_sigmoid(values, params.get('midpoint', 0.5), params.get('steepness', 10))
        elif function == 'piecewise':
            return self.score_piecewise(values, params['breakpoints'], params['slopes'])
        else:
            raise ValueError(f"Unknown function: {function}")
    
    # Aggregation Methods
    def weighted_sum(self, scores: np.ndarray, weights: np.ndarray) -> float:
        """Weighted sum aggregation."""
        result = float(np.sum(scores * weights))
        self._log_operation('weighted_sum', 
                           {'scores': scores.tolist(), 'weights': weights.tolist()},
                           {'result': result})
        return result
    
    def weighted_product(self, scores: np.ndarray, weights: np.ndarray) -> float:
        """Weighted product aggregation."""
        # Handle zeros by adding small epsilon
        scores_safe = np.maximum(scores, 1e-10)
        result = float(np.prod(np.power(scores_safe, weights)))
        self._log_operation('weighted_product',
                           {'scores': scores.tolist(), 'weights': weights.tolist()},
                           {'result': result})
        return result
    
    def topsis(self, matrix: np.ndarray, weights: np.ndarray, directions: List[str]) -> np.ndarray:
        """
        TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).
        
        Args:
            matrix: Alternatives x Criteria score matrix
            weights: Criterion weights
            directions: List of 'maximize' or 'minimize' per criterion
        
        Returns:
            Relative closeness scores for each alternative
        """
        # Normalize matrix
        norm_matrix = matrix / np.sqrt(np.sum(matrix**2, axis=0))
        
        # Apply weights
        weighted_matrix = norm_matrix * weights
        
        # Determine ideal and anti-ideal solutions
        ideal = np.zeros(len(weights))
        anti_ideal = np.zeros(len(weights))
        
        for j, direction in enumerate(directions):
            if direction == 'maximize':
                ideal[j] = np.max(weighted_matrix[:, j])
                anti_ideal[j] = np.min(weighted_matrix[:, j])
            else:
                ideal[j] = np.min(weighted_matrix[:, j])
                anti_ideal[j] = np.max(weighted_matrix[:, j])
        
        # Calculate distances
        dist_ideal = np.sqrt(np.sum((weighted_matrix - ideal)**2, axis=1))
        dist_anti_ideal = np.sqrt(np.sum((weighted_matrix - anti_ideal)**2, axis=1))
        
        # Relative closeness
        closeness = dist_anti_ideal / (dist_ideal + dist_anti_ideal)
        
        self._log_operation('topsis',
                           {'matrix_shape': matrix.shape, 'weights': weights.tolist()},
                           {'closeness': closeness.tolist(), 'ideal': ideal.tolist()})
        
        return closeness
    
    def aggregate(self, scores: np.ndarray, weights: np.ndarray, method: str = 'weighted_sum', **kwargs) -> float:
        """Aggregate scores using specified method."""
        if method == 'weighted_sum':
            return self.weighted_sum(scores, weights)
        elif method == 'weighted_product':
            return self.weighted_product(scores, weights)
        elif method == 'topsis':
            raise ValueError("Use topsis() method directly with full matrix")
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def calculate_decision_matrix(
        self,
        data: pd.DataFrame,
        weights: Dict[str, float],
        scoring_config: Optional[Dict] = None,
        aggregation: str = 'weighted_sum'
    ) -> pd.DataFrame:
        """
        Calculate complete decision matrix with scores.
        
        Args:
            data: DataFrame with columns [alternative, criterion, normalized_value]
            weights: Dict of {criterion: weight}
            scoring_config: Optional per-criterion scoring function config
            aggregation: Aggregation method
        
        Returns:
            DataFrame with scores and rankings
        """
        alternatives = data['alternative'].unique()
        criteria = list(weights.keys())
        
        # Build score matrix
        results = []
        
        for alt in alternatives:
            alt_data = data[data['alternative'] == alt]
            scores = []
            weighted_scores = []
            
            for criterion in criteria:
                crit_row = alt_data[alt_data['criterion'] == criterion]
                if len(crit_row) == 0:
                    raise ValueError(f"Missing data for {alt}/{criterion}")
                
                norm_value = crit_row['normalized_value'].values[0]
                
                # Apply scoring function if configured
                if scoring_config and criterion in scoring_config:
                    cfg = scoring_config[criterion]
                    score = self.apply_scoring(
                        np.array([norm_value]),
                        cfg['function'],
                        **cfg.get('params', {})
                    )[0]
                else:
                    score = norm_value  # Linear by default
                
                weight = weights[criterion]
                scores.append(score)
                weighted_scores.append(score * weight)
            
            # Aggregate
            total_score = self.aggregate(
                np.array(scores),
                np.array(list(weights.values())),
                method=aggregation
            )
            
            results.append({
                'alternative': alt,
                'total_score': total_score,
                **{f'score_{c}': s for c, s in zip(criteria, scores)},
                **{f'weighted_{c}': ws for c, ws in zip(criteria, weighted_scores)}
            })
        
        result_df = pd.DataFrame(results)
        result_df['rank'] = result_df['total_score'].rank(ascending=False).astype(int)
        result_df = result_df.sort_values('rank')
        
        return result_df
    
    def get_audit_log(self) -> List[Dict]:
        """Return audit log."""
        return self.audit_log
    
    def save_audit_log(self, path: str):
        """Save audit log to file."""
        with open(path, 'w') as f:
            json.dump({
                'audit_log': self.audit_log,
                'exported_at': datetime.now().isoformat()
            }, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Calculate trade study scores')
    
    parser.add_argument('input', help='Input CSV with normalized data')
    parser.add_argument('weights', help='JSON file with criterion weights')
    parser.add_argument('-o', '--output', help='Output CSV file')
    parser.add_argument('--scoring-config', help='JSON config for scoring functions')
    parser.add_argument('--method', choices=Scorer.AGGREGATION_METHODS, default='weighted_sum',
                       help='Aggregation method')
    parser.add_argument('--matrix', help='Save decision matrix to file')
    parser.add_argument('--audit', help='Save audit log to file')
    parser.add_argument('--report', action='store_true', help='Print summary report')
    
    args = parser.parse_args()
    
    # Load data
    df = pd.read_csv(args.input)
    with open(args.weights) as f:
        weights = json.load(f)
    
    scoring_config = None
    if args.scoring_config:
        with open(args.scoring_config) as f:
            scoring_config = json.load(f)
    
    scorer = Scorer()
    
    # Calculate scores
    result = scorer.calculate_decision_matrix(
        df, weights,
        scoring_config=scoring_config,
        aggregation=args.method
    )
    
    # Output
    output_path = args.output or args.input.replace('.csv', '_scored.csv')
    result.to_csv(output_path, index=False)
    print(f"Scores saved to: {output_path}")
    
    if args.matrix:
        # Save as formatted decision matrix
        result.to_csv(args.matrix, index=False)
        print(f"Decision matrix saved to: {args.matrix}")
    
    if args.audit:
        scorer.save_audit_log(args.audit)
        print(f"Audit log saved to: {args.audit}")
    
    if args.report:
        print("\n" + "=" * 60)
        print("SCORING RESULTS")
        print("=" * 60)
        print(f"\nRankings:")
        for _, row in result.iterrows():
            print(f"  {row['rank']}. {row['alternative']}: {row['total_score']:.4f}")
        
        winner = result.iloc[0]
        runner_up = result.iloc[1] if len(result) > 1 else None
        
        print(f"\nWinner: {winner['alternative']}")
        if runner_up is not None:
            gap = winner['total_score'] - runner_up['total_score']
            print(f"Gap to runner-up: {gap:.4f} ({gap/runner_up['total_score']*100:.1f}%)")


if __name__ == '__main__':
    main()
