#!/usr/bin/env python3
"""
Kepner-Tregoe Decision Analysis Scoring Calculator

Calculates weighted scores for alternatives against WANTS criteria.
Supports both interactive mode and JSON file input.

Usage:
    python calculate_scores.py                    # Interactive mode
    python calculate_scores.py --input data.json  # From JSON file
    python calculate_scores.py --output results.json  # Save results
"""

import json
import argparse
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class WantCriterion:
    """A WANT criterion with name, direction, and weight."""
    name: str
    direction: str  # "higher_better" or "lower_better"
    weight: int  # 1-10


@dataclass
class MustCriterion:
    """A MUST criterion with name and measurement."""
    name: str
    measurement: str


@dataclass 
class Alternative:
    """An alternative being evaluated."""
    name: str
    must_results: Dict[str, bool]  # {must_name: pass/fail}
    want_scores: Dict[str, int]  # {want_name: score 1-10}


@dataclass
class RiskAssessment:
    """Risk assessment for an alternative."""
    consequence: str
    probability: str  # H/M/L
    seriousness: str  # H/M/L
    combined: str  # Calculated


@dataclass
class DecisionAnalysis:
    """Complete Decision Analysis data structure."""
    decision_statement: str
    musts: List[MustCriterion]
    wants: List[WantCriterion]
    alternatives: List[Alternative]
    risks: Dict[str, List[RiskAssessment]]  # {alternative_name: [risks]}
    created_at: str
    notes: str = ""


def calculate_combined_risk(probability: str, seriousness: str) -> str:
    """Calculate combined risk from probability and seriousness."""
    risk_matrix = {
        ('H', 'H'): 'CRITICAL',
        ('H', 'M'): 'HIGH',
        ('M', 'H'): 'HIGH',
        ('H', 'L'): 'MEDIUM',
        ('M', 'M'): 'MEDIUM',
        ('L', 'H'): 'MEDIUM',
        ('M', 'L'): 'LOW',
        ('L', 'M'): 'LOW',
        ('L', 'L'): 'LOW'
    }
    return risk_matrix.get((probability.upper(), seriousness.upper()), 'UNKNOWN')


def screen_musts(alternative: Alternative, musts: List[MustCriterion]) -> tuple:
    """Screen alternative against MUSTS. Returns (passed, failed_musts)."""
    failed = []
    for must in musts:
        if not alternative.must_results.get(must.name, False):
            failed.append(must.name)
    return (len(failed) == 0, failed)


def calculate_weighted_score(alternative: Alternative, wants: List[WantCriterion]) -> dict:
    """Calculate weighted score for an alternative."""
    scores = []
    total = 0
    max_possible = 0
    
    for want in wants:
        raw_score = alternative.want_scores.get(want.name, 0)
        weighted = raw_score * want.weight
        scores.append({
            'want': want.name,
            'weight': want.weight,
            'raw_score': raw_score,
            'weighted_score': weighted
        })
        total += weighted
        max_possible += 10 * want.weight
    
    return {
        'alternative': alternative.name,
        'scores': scores,
        'total_weighted': total,
        'max_possible': max_possible,
        'percentage': round(total / max_possible * 100, 1) if max_possible > 0 else 0
    }


def rank_alternatives(results: List[dict]) -> List[dict]:
    """Rank alternatives by total weighted score."""
    sorted_results = sorted(results, key=lambda x: x['total_weighted'], reverse=True)
    for i, result in enumerate(sorted_results, 1):
        result['rank'] = i
    return sorted_results


def generate_summary(analysis: DecisionAnalysis, scored_results: List[dict]) -> dict:
    """Generate analysis summary."""
    # Find alternatives that passed MUSTS
    passed_alternatives = []
    failed_alternatives = []
    
    for alt in analysis.alternatives:
        passed, failed_musts = screen_musts(alt, analysis.musts)
        if passed:
            passed_alternatives.append(alt.name)
        else:
            failed_alternatives.append({'name': alt.name, 'failed_musts': failed_musts})
    
    # Get top alternative
    top_alt = scored_results[0] if scored_results else None
    
    # Summarize risks for top alternatives
    risk_summary = {}
    for result in scored_results[:3]:  # Top 3
        alt_name = result['alternative']
        if alt_name in analysis.risks:
            risks = analysis.risks[alt_name]
            critical_high = sum(1 for r in risks if r.combined in ['CRITICAL', 'HIGH'])
            medium = sum(1 for r in risks if r.combined == 'MEDIUM')
            low = sum(1 for r in risks if r.combined == 'LOW')
            risk_summary[alt_name] = {
                'critical_high': critical_high,
                'medium': medium,
                'low': low,
                'total': len(risks)
            }
    
    return {
        'decision_statement': analysis.decision_statement,
        'total_alternatives': len(analysis.alternatives),
        'passed_must_screening': len(passed_alternatives),
        'failed_must_screening': len(failed_alternatives),
        'failed_details': failed_alternatives,
        'recommended': top_alt['alternative'] if top_alt else None,
        'recommended_score': top_alt['total_weighted'] if top_alt else None,
        'recommended_percentage': top_alt['percentage'] if top_alt else None,
        'risk_summary': risk_summary,
        'rankings': [{'rank': r['rank'], 'alternative': r['alternative'], 
                      'score': r['total_weighted'], 'percentage': r['percentage']} 
                     for r in scored_results]
    }


def interactive_mode():
    """Run interactive Decision Analysis scoring."""
    print("\n" + "="*60)
    print("KEPNER-TREGOE DECISION ANALYSIS SCORING")
    print("="*60)
    
    # Decision Statement
    print("\n--- DECISION STATEMENT ---")
    decision_statement = input("Enter decision statement: ").strip()
    
    # MUSTS
    print("\n--- MUSTS (Mandatory Requirements) ---")
    print("Enter MUST criteria (empty name to finish):")
    musts = []
    while True:
        name = input("  MUST name: ").strip()
        if not name:
            break
        measurement = input("  Measurement/test: ").strip()
        musts.append(MustCriterion(name=name, measurement=measurement))
    
    # WANTS
    print("\n--- WANTS (Desired Outcomes) ---")
    print("Enter WANT criteria (empty name to finish):")
    wants = []
    while True:
        name = input("  WANT name: ").strip()
        if not name:
            break
        direction = input("  Direction (h=higher better, l=lower better) [h]: ").strip().lower()
        direction = "lower_better" if direction == 'l' else "higher_better"
        while True:
            try:
                weight = int(input("  Weight (1-10): ").strip())
                if 1 <= weight <= 10:
                    break
                print("    Weight must be 1-10")
            except ValueError:
                print("    Enter a number 1-10")
        wants.append(WantCriterion(name=name, direction=direction, weight=weight))
    
    # Alternatives
    print("\n--- ALTERNATIVES ---")
    print("Enter alternatives (empty name to finish):")
    alternatives = []
    while True:
        name = input("  Alternative name: ").strip()
        if not name:
            break
        
        # MUST screening
        must_results = {}
        if musts:
            print(f"  --- MUST screening for {name} ---")
            for must in musts:
                result = input(f"    Does '{name}' meet '{must.name}'? (y/n): ").strip().lower()
                must_results[must.name] = result in ['y', 'yes', '1', 'true']
        
        # WANT scoring
        want_scores = {}
        passed, failed = screen_musts(Alternative(name=name, must_results=must_results, want_scores={}), musts)
        
        if passed:
            print(f"  --- WANT scoring for {name} (1-10 scale) ---")
            for want in wants:
                while True:
                    try:
                        score = int(input(f"    {want.name}: ").strip())
                        if 1 <= score <= 10:
                            want_scores[want.name] = score
                            break
                        print("      Score must be 1-10")
                    except ValueError:
                        print("      Enter a number 1-10")
        else:
            print(f"  '{name}' FAILED MUST screening on: {', '.join(failed)}")
            print("  Skipping WANT scoring for this alternative.")
        
        alternatives.append(Alternative(name=name, must_results=must_results, want_scores=want_scores))
    
    # Build analysis object
    analysis = DecisionAnalysis(
        decision_statement=decision_statement,
        musts=musts,
        wants=wants,
        alternatives=alternatives,
        risks={},
        created_at=datetime.now().isoformat()
    )
    
    # Calculate scores
    results = []
    for alt in alternatives:
        passed, _ = screen_musts(alt, musts)
        if passed:
            result = calculate_weighted_score(alt, wants)
            results.append(result)
    
    ranked = rank_alternatives(results)
    summary = generate_summary(analysis, ranked)
    
    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    print(f"\nDecision: {summary['decision_statement']}")
    print(f"\nAlternatives evaluated: {summary['total_alternatives']}")
    print(f"Passed MUST screening: {summary['passed_must_screening']}")
    print(f"Failed MUST screening: {summary['failed_must_screening']}")
    
    if summary['failed_details']:
        print("\nFailed alternatives:")
        for fail in summary['failed_details']:
            print(f"  - {fail['name']}: Failed {', '.join(fail['failed_musts'])}")
    
    print("\n--- RANKINGS ---")
    print(f"{'Rank':<6}{'Alternative':<30}{'Score':<10}{'%':<10}")
    print("-" * 56)
    for r in summary['rankings']:
        print(f"{r['rank']:<6}{r['alternative']:<30}{r['score']:<10}{r['percentage']:.1f}%")
    
    print(f"\n*** RECOMMENDED: {summary['recommended']} ***")
    print(f"    Score: {summary['recommended_score']} ({summary['recommended_percentage']:.1f}%)")
    
    # Offer to save
    save = input("\nSave results to JSON? (y/n): ").strip().lower()
    if save in ['y', 'yes']:
        filename = input("Filename [da_results.json]: ").strip() or "da_results.json"
        output = {
            'analysis': asdict(analysis),
            'results': ranked,
            'summary': summary
        }
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {filename}")


def process_json_input(input_file: str, output_file: Optional[str] = None):
    """Process Decision Analysis from JSON input."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Parse input
    musts = [MustCriterion(**m) for m in data.get('musts', [])]
    wants = [WantCriterion(**w) for w in data['wants']]
    alternatives = [Alternative(**a) for a in data['alternatives']]
    
    # Parse risks if present
    risks = {}
    for alt_name, risk_list in data.get('risks', {}).items():
        risks[alt_name] = []
        for r in risk_list:
            r['combined'] = calculate_combined_risk(r['probability'], r['seriousness'])
            risks[alt_name].append(RiskAssessment(**r))
    
    analysis = DecisionAnalysis(
        decision_statement=data.get('decision_statement', ''),
        musts=musts,
        wants=wants,
        alternatives=alternatives,
        risks=risks,
        created_at=data.get('created_at', datetime.now().isoformat()),
        notes=data.get('notes', '')
    )
    
    # Calculate scores for alternatives that passed MUSTS
    results = []
    for alt in alternatives:
        passed, _ = screen_musts(alt, musts)
        if passed:
            result = calculate_weighted_score(alt, wants)
            results.append(result)
    
    ranked = rank_alternatives(results)
    summary = generate_summary(analysis, ranked)
    
    output = {
        'analysis': asdict(analysis),
        'results': ranked,
        'summary': summary
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {output_file}")
    else:
        print(json.dumps(output, indent=2))
    
    return output


def main():
    parser = argparse.ArgumentParser(description='Kepner-Tregoe Decision Analysis Scoring Calculator')
    parser.add_argument('--input', '-i', help='Input JSON file')
    parser.add_argument('--output', '-o', help='Output JSON file')
    
    args = parser.parse_args()
    
    if args.input:
        process_json_input(args.input, args.output)
    else:
        interactive_mode()


if __name__ == '__main__':
    main()
