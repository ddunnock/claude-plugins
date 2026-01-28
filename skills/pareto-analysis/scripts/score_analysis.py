#!/usr/bin/env python3
"""
Pareto Analysis Quality Scoring Calculator

Calculates quality scores for Pareto Analysis based on the 6-dimension rubric.

Usage:
    python3 score_analysis.py --interactive
    python3 score_analysis.py --input scores.json --output results.json

Dimensions:
1. Problem Clarity (15%)
2. Data Quality (25%)
3. Category Design (20%)
4. Calculation Accuracy (15%)
5. Pattern Interpretation (15%)
6. Actionability (10%)
"""

import json
import argparse
import sys
from typing import Dict, Any, List, Tuple


DIMENSIONS = {
    "problem_clarity": {
        "name": "Problem Clarity",
        "weight": 0.15,
        "description": "Clear scope, measurement type, business relevance",
        "criteria": {
            5: "Specific outcome; clear measurement type; direct business relevance; appropriately bounded",
            4: "Clear statement; measurement specified; business context understood",
            3: "Problem identified but lacks specificity in scope or measurement",
            2: "Vague statement; unclear measurement or business relevance",
            1: "No clear definition; measurement type undefined"
        }
    },
    "data_quality": {
        "name": "Data Quality",
        "weight": 0.25,
        "description": "Representative, sufficient, consistent data",
        "criteria": {
            5: "Representative period; ≥50 data points; verified accuracy; documented sources",
            4: "Adequate period; 30-50 points; source documented; minor gaps",
            3: "Minimum viable data (20-30); some documentation; gaps acknowledged",
            2: "Insufficient data (<20); undocumented; questionable accuracy",
            1: "Too little data; no documentation"
        }
    },
    "category_design": {
        "name": "Category Design",
        "weight": 0.20,
        "description": "MECE, actionable, appropriate granularity",
        "criteria": {
            5: "MECE categories; 5-8 actionable; 'Other' ≤5%; clear definitions",
            4: "Mostly MECE; 7-10 categories; 'Other' ≤10%; definitions provided",
            3: "Minor overlap/gaps; 10-12 categories; 'Other' ≤15%",
            2: "Significant overlap; too many/few categories; large 'Other'",
            1: "Categories overlap heavily; non-actionable; 'Other' dominant"
        }
    },
    "calculation_accuracy": {
        "name": "Calculation Accuracy",
        "weight": 0.15,
        "description": "Correct sorting, percentages, cumulative line",
        "criteria": {
            5: "Correct sort; accurate percentages; correct cumulative; proper threshold",
            4: "All calculations correct; minor formatting issues",
            3: "Mostly correct; small rounding errors",
            2: "Errors in cumulative or threshold identification",
            1: "Fundamental errors; incorrect sorting"
        }
    },
    "pattern_interpretation": {
        "name": "Pattern Interpretation",
        "weight": 0.15,
        "description": "Valid conclusions from cumulative curve",
        "criteria": {
            5: "Correct effect identification; validates with domain knowledge; acknowledges limitations; considers weighting",
            4: "Correct pattern; reasonable conclusions; limitations noted",
            3: "Basic recognition; conclusions reasonable but superficial",
            2: "Misinterprets pattern; overconfident conclusions",
            1: "No analysis; incorrect conclusions"
        }
    },
    "actionability": {
        "name": "Actionability",
        "weight": 0.10,
        "description": "Clear next steps, linked to improvement actions",
        "criteria": {
            5: "Clear next steps; vital few linked to root cause investigation; cost/effort considered; timeline",
            4: "Next steps identified; logical connection to improvements",
            3: "Some recommendations; general direction",
            2: "Vague recommendations; no clear path",
            1: "No recommendations; analysis ends at chart"
        }
    }
}


def calculate_score(scores: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate weighted quality score from dimension scores.
    
    Args:
        scores: Dict mapping dimension keys to scores (1-5)
    
    Returns:
        Dict with total score, breakdown, and interpretation
    """
    results = {
        "dimensions": {},
        "weighted_contributions": {},
        "total_score": 0,
        "rating": "",
        "improvements": []
    }
    
    total = 0
    
    for dim_key, dim_info in DIMENSIONS.items():
        score = scores.get(dim_key, 3)  # Default to 3 if missing
        
        # Validate score range
        if score < 1:
            score = 1
        elif score > 5:
            score = 5
        
        # Calculate weighted contribution (scale to 100-point system)
        contribution = score * dim_info['weight'] * 20
        
        results["dimensions"][dim_key] = {
            "name": dim_info['name'],
            "score": score,
            "max_score": 5,
            "weight": dim_info['weight'],
            "weighted_contribution": round(contribution, 1)
        }
        
        results["weighted_contributions"][dim_info['name']] = round(contribution, 1)
        total += contribution
        
        # Add improvement recommendations for low scores
        if score <= 3:
            results["improvements"].append({
                "dimension": dim_info['name'],
                "current_score": score,
                "recommendation": get_improvement_recommendation(dim_key, score)
            })
    
    results["total_score"] = round(total, 1)
    results["rating"] = get_rating(total)
    results["passing"] = total >= 70
    
    return results


def get_rating(score: float) -> str:
    """Get rating label from score."""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Adequate"
    elif score >= 60:
        return "Marginal"
    else:
        return "Inadequate"


def get_improvement_recommendation(dimension: str, score: int) -> str:
    """Get improvement recommendation for a dimension."""
    recommendations = {
        "problem_clarity": {
            1: "Completely rewrite problem statement with specific outcome, measurement type, and business relevance",
            2: "Clarify measurement type and add business context",
            3: "Add more specificity to scope boundaries"
        },
        "data_quality": {
            1: "Restart data collection with proper planning; need minimum 30+ data points",
            2: "Extend collection period; document sources; verify accuracy",
            3: "Consider extending time period; improve documentation"
        },
        "category_design": {
            1: "Redesign categories following MECE principle; break down 'Other'",
            2: "Review categories for overlap; reduce 'Other' below 10%",
            3: "Document category definitions; check for edge case clarity"
        },
        "calculation_accuracy": {
            1: "Recalculate all values; use provided calculation script",
            2: "Verify cumulative percentage calculation and threshold identification",
            3: "Check rounding and formatting consistency"
        },
        "pattern_interpretation": {
            1: "Analyze cumulative curve objectively; avoid forcing 80/20 pattern",
            2: "Consider weighting; validate against domain knowledge",
            3: "Add limitations and assumptions to analysis"
        },
        "actionability": {
            1: "Define specific next steps for each vital few category",
            2: "Link priorities to root cause investigation methods",
            3: "Add cost/effort considerations and timeline"
        }
    }
    
    return recommendations.get(dimension, {}).get(score, "Review rubric for improvement guidance")


def interactive_scoring() -> Dict[str, int]:
    """Interactive scoring session."""
    print("\n" + "=" * 60)
    print("PARETO ANALYSIS QUALITY SCORING")
    print("=" * 60)
    print("\nRate each dimension from 1-5:")
    print("  1 = Inadequate")
    print("  2 = Marginal")
    print("  3 = Adequate")
    print("  4 = Good")
    print("  5 = Excellent")
    print()
    
    scores = {}
    
    for dim_key, dim_info in DIMENSIONS.items():
        print(f"\n--- {dim_info['name']} ({int(dim_info['weight']*100)}% weight) ---")
        print(f"Focus: {dim_info['description']}")
        print("\nCriteria:")
        for score_val, criteria in dim_info['criteria'].items():
            print(f"  {score_val}: {criteria}")
        
        while True:
            try:
                score = int(input(f"\nScore for {dim_info['name']} (1-5): ").strip())
                if 1 <= score <= 5:
                    scores[dim_key] = score
                    break
                else:
                    print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
    
    return scores


def format_results(results: Dict[str, Any]) -> str:
    """Format results as readable text."""
    lines = [
        "\n" + "=" * 60,
        "PARETO ANALYSIS QUALITY SCORE RESULTS",
        "=" * 60,
        "",
        f"TOTAL SCORE: {results['total_score']}/100",
        f"RATING: {results['rating']}",
        f"PASSING: {'Yes ✓' if results['passing'] else 'No ✗'}",
        "",
        "DIMENSION BREAKDOWN:",
        "-" * 40
    ]
    
    for dim_key, dim_data in results['dimensions'].items():
        lines.append(
            f"  {dim_data['name']}: {dim_data['score']}/5 "
            f"(contributes {dim_data['weighted_contribution']} points)"
        )
    
    if results['improvements']:
        lines.extend([
            "",
            "IMPROVEMENT RECOMMENDATIONS:",
            "-" * 40
        ])
        for imp in results['improvements']:
            lines.append(f"  [{imp['dimension']} - Score {imp['current_score']}]")
            lines.append(f"    → {imp['recommendation']}")
    
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pareto Analysis Quality Scoring")
    parser.add_argument("--input", "-i", help="Input JSON file with scores")
    parser.add_argument("--output", "-o", help="Output JSON file for results")
    parser.add_argument("--interactive", action="store_true", help="Interactive scoring mode")
    parser.add_argument("--format", "-f", choices=["json", "text", "both"], default="both",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Get scores
    if args.interactive:
        scores = interactive_scoring()
    elif args.input:
        try:
            with open(args.input, 'r') as f:
                input_data = json.load(f)
            scores = input_data.get('scores', input_data)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{args.input}'")
            sys.exit(1)
    else:
        print("Error: Provide --input file or use --interactive mode")
        sys.exit(1)
    
    # Calculate results
    results = calculate_score(scores)
    
    # Output
    if args.format in ["text", "both"]:
        print(format_results(results))
    
    if args.format in ["json", "both"]:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        elif args.format == "json":
            print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
