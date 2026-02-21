#!/usr/bin/env python3
"""
Normalization Tools for Trade Study Analysis

Converts raw measurements to comparable scales with full source traceability.
All normalization operations require source-grounded input data.
"""

import sys
import os
import json
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class Normalizer:
    """Normalizes trade study data with audit trail."""
    
    METHODS = ['min-max', 'z-score', 'log', 'percentile']
    
    def __init__(self):
        self.audit_log = []
    
    def _log_operation(self, operation: str, inputs: Dict, outputs: Dict, method: str):
        """Log normalization operation for audit."""
        self.audit_log.append({
            'operation': operation,
            'method': method,
            'inputs': inputs,
            'outputs': outputs,
            'timestamp': datetime.now().isoformat()
        })
    
    def min_max(
        self,
        values: np.ndarray,
        direction: str = 'maximize',
        output_range: Tuple[float, float] = (0.0, 1.0)
    ) -> np.ndarray:
        """
        Min-max normalization.
        
        Formula: (x - min) / (max - min) * (range_max - range_min) + range_min
        """
        v_min, v_max = np.min(values), np.max(values)
        
        if v_max == v_min:
            # All values equal - return midpoint of range
            return np.full_like(values, (output_range[0] + output_range[1]) / 2, dtype=float)
        
        normalized = (values - v_min) / (v_max - v_min)
        
        # Scale to output range
        range_min, range_max = output_range
        normalized = normalized * (range_max - range_min) + range_min
        
        # Flip if minimize (lower is better)
        if direction == 'minimize':
            normalized = range_max - normalized + range_min
        
        self._log_operation(
            'min_max_normalization',
            {'values': values.tolist(), 'direction': direction, 'range': output_range},
            {'normalized': normalized.tolist(), 'min': v_min, 'max': v_max},
            'min-max'
        )
        
        return normalized
    
    def z_score(self, values: np.ndarray, direction: str = 'maximize') -> np.ndarray:
        """
        Z-score normalization.
        
        Formula: (x - mean) / std_dev
        """
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return np.zeros_like(values, dtype=float)
        
        normalized = (values - mean) / std
        
        if direction == 'minimize':
            normalized = -normalized
        
        self._log_operation(
            'z_score_normalization',
            {'values': values.tolist(), 'direction': direction},
            {'normalized': normalized.tolist(), 'mean': mean, 'std': std},
            'z-score'
        )
        
        return normalized
    
    def logarithmic(
        self,
        values: np.ndarray,
        direction: str = 'maximize',
        base: float = 10,
        offset: float = 1
    ) -> np.ndarray:
        """
        Logarithmic normalization for multi-order magnitude data.
        
        Formula: log(x + offset) / log(max + offset)
        """
        # Add offset to handle zeros
        adjusted = values + offset
        v_max = np.max(adjusted)
        
        normalized = np.log(adjusted) / np.log(v_max) if v_max > 1 else adjusted / v_max
        
        if direction == 'minimize':
            normalized = 1 - normalized
        
        self._log_operation(
            'logarithmic_normalization',
            {'values': values.tolist(), 'direction': direction, 'base': base, 'offset': offset},
            {'normalized': normalized.tolist(), 'max_adjusted': v_max},
            'log'
        )
        
        return normalized
    
    def percentile_rank(self, values: np.ndarray, direction: str = 'maximize') -> np.ndarray:
        """
        Percentile rank normalization.
        
        Formula: rank / n
        """
        n = len(values)
        ranks = np.zeros(n)
        
        for i, v in enumerate(values):
            ranks[i] = np.sum(values <= v) / n
        
        if direction == 'minimize':
            ranks = 1 - ranks
        
        self._log_operation(
            'percentile_rank_normalization',
            {'values': values.tolist(), 'direction': direction},
            {'normalized': ranks.tolist()},
            'percentile'
        )
        
        return ranks
    
    def normalize(
        self,
        values: np.ndarray,
        method: str,
        direction: str = 'maximize',
        **kwargs
    ) -> np.ndarray:
        """Normalize using specified method."""
        if method == 'min-max':
            return self.min_max(values, direction, kwargs.get('output_range', (0, 1)))
        elif method == 'z-score':
            return self.z_score(values, direction)
        elif method == 'log':
            return self.logarithmic(
                values, direction,
                kwargs.get('base', 10),
                kwargs.get('offset', 1)
            )
        elif method == 'percentile':
            return self.percentile_rank(values, direction)
        else:
            raise ValueError(f"Unknown method: {method}. Use one of: {self.METHODS}")
    
    def normalize_dataframe(
        self,
        df: pd.DataFrame,
        config: Dict[str, Dict],
        value_column: str = 'raw_value',
        criterion_column: str = 'criterion'
    ) -> pd.DataFrame:
        """
        Normalize a dataframe with per-criterion configuration.
        
        Config format:
        {
            "criterion_name": {
                "method": "min-max",
                "direction": "maximize",
                "params": {...}
            }
        }
        """
        result = df.copy()
        result['normalized_value'] = 0.0
        result['normalization_method'] = ''
        result['normalization_direction'] = ''
        
        for criterion, settings in config.items():
            mask = result[criterion_column] == criterion
            if not mask.any():
                continue
            
            values = result.loc[mask, value_column].values.astype(float)
            method = settings.get('method', 'min-max')
            direction = settings.get('direction', 'maximize')
            params = settings.get('params', {})
            
            normalized = self.normalize(values, method, direction, **params)
            
            result.loc[mask, 'normalized_value'] = normalized
            result.loc[mask, 'normalization_method'] = method
            result.loc[mask, 'normalization_direction'] = direction
        
        return result
    
    def get_audit_log(self) -> List[Dict]:
        """Return audit log of all operations."""
        return self.audit_log
    
    def save_audit_log(self, path: str):
        """Save audit log to file."""
        with open(path, 'w') as f:
            json.dump({
                'audit_log': self.audit_log,
                'exported_at': datetime.now().isoformat()
            }, f, indent=2)



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
        description='Normalize trade study data'
    )
    
    parser.add_argument('input', help='Input CSV file with raw data')
    parser.add_argument('-o', '--output', help='Output CSV file')
    parser.add_argument('--method', choices=Normalizer.METHODS, default='min-max',
                       help='Normalization method')
    parser.add_argument('--direction', choices=['maximize', 'minimize'], default='maximize',
                       help='Optimization direction')
    parser.add_argument('--config', help='JSON config file for per-criterion settings')
    parser.add_argument('--value-col', default='raw_value', help='Value column name')
    parser.add_argument('--criterion-col', default='criterion', help='Criterion column name')
    parser.add_argument('--range', type=float, nargs=2, default=[0, 1],
                       help='Output range for min-max (default: 0 1)')
    parser.add_argument('--base', type=float, default=10, help='Log base')
    parser.add_argument('--offset', type=float, default=1, help='Log offset')
    parser.add_argument('--audit', help='Save audit log to file')
    parser.add_argument('--report', action='store_true', help='Print summary report')
    
    args = parser.parse_args()

    args.config = _validate_path(args.config, {'.json', '.yaml', '.yml'}, "config")
    
    # Load data
    df = pd.read_csv(args.input)
    normalizer = Normalizer()
    
    if args.config:
        # Use per-criterion config
        with open(args.config) as f:
            config = json.load(f)
        result = normalizer.normalize_dataframe(
            df, config,
            value_column=args.value_col,
            criterion_column=args.criterion_col
        )
    else:
        # Apply single method to all
        values = df[args.value_col].values.astype(float)
        normalized = normalizer.normalize(
            values,
            method=args.method,
            direction=args.direction,
            output_range=tuple(args.range),
            base=args.base,
            offset=args.offset
        )
        result = df.copy()
        result['normalized_value'] = normalized
        result['normalization_method'] = args.method
        result['normalization_direction'] = args.direction
    
    # Output
    output_path = args.output or args.input.replace('.csv', '_normalized.csv')
    result.to_csv(output_path, index=False)
    print(f"Normalized data saved to: {output_path}")
    
    # Audit log
    if args.audit:
        normalizer.save_audit_log(args.audit)
        print(f"Audit log saved to: {args.audit}")
    
    # Report
    if args.report:
        print("\n" + "=" * 60)
        print("NORMALIZATION SUMMARY")
        print("=" * 60)
        print(f"Input records: {len(df)}")
        print(f"Output records: {len(result)}")
        print(f"\nNormalized value statistics:")
        print(f"  Min: {result['normalized_value'].min():.4f}")
        print(f"  Max: {result['normalized_value'].max():.4f}")
        print(f"  Mean: {result['normalized_value'].mean():.4f}")
        print(f"  Std: {result['normalized_value'].std():.4f}")


if __name__ == '__main__':
    main()
