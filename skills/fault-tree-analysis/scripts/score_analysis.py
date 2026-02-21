#!/usr/bin/env python3
"""
Fault Tree Analysis Quality Scorer

Evaluates FTA quality against the 6-dimension rubric.
Supports interactive or JSON-based scoring.

Usage:
    python score_analysis.py [scores.json]
    
Interactive mode if no file provided.
"""

import os
import json
import sys
import argparse
from typing import Dict, List, Optional, Tuple


# Rubric dimensions with weights
DIMENSIONS = {
    "system_definition": {
        "name": "System Definition",
        "weight": 0.15,
        "description": "Clear boundaries, assumptions, operating conditions",
        "criteria": {
            5: "Boundaries explicit, all conditions specified, comprehensive assumptions, docs available",
            4: "Boundaries defined with minor gaps, key conditions specified, main assumptions listed",
            3: "Boundaries loosely defined, some conditions missing, basic assumptions",
            2: "Boundaries unclear, conditions incomplete, assumptions vague",
            1: "No boundaries defined, conditions unspecified, no assumptions"
        }
    },
    "top_event_clarity": {
        "name": "Top Event Clarity",
        "weight": 0.15,
        "description": "Specific, unambiguous, appropriate level",
        "criteria": {
            5: "Single specific event, precise failure criteria, measurable, appropriate level",
            4: "Clear event with minor ambiguity, well-defined, appropriate level",
            3: "Generally clear but some interpretation needed, acceptable level",
            2: "Vague or too broad, poorly defined, wrong level",
            1: "Multiple events conflated, no clear definition, inappropriate level"
        }
    },
    "tree_completeness": {
        "name": "Tree Completeness",
        "weight": 0.25,
        "description": "All pathways developed, consistent logic, no gaps",
        "criteria": {
            5: "All pathways to basic events, correct gates, CCF considered, human factors included",
            4: "Most pathways developed, gate logic generally correct, key factors considered",
            3: "Primary pathways developed, some gate issues, limited CCF/human factors",
            2: "Significant gaps, multiple gate errors, missing key pathways",
            1: "Barely developed, fundamental errors, critical pathways missing"
        }
    },
    "minimal_cut_sets": {
        "name": "Minimal Cut Sets",
        "weight": 0.20,
        "description": "Correctly identified, SPOFs flagged, analyzed",
        "criteria": {
            5: "All MCS correct, organized by order, SPOFs flagged, CCF combinations noted",
            4: "Most MCS correct, organized, SPOFs noted, some CCF consideration",
            3: "Primary MCS identified, partially organized, SPOFs incomplete",
            2: "MCS identification incomplete, unorganized, SPOFs missed",
            1: "MCS not identified, no understanding demonstrated"
        }
    },
    "quantification": {
        "name": "Quantification",
        "weight": 0.15,
        "description": "Accurate calculations, appropriate data sources",
        "criteria": {
            5: "All probabilities documented, sources traced, calculations verified, uncertainty stated",
            4: "Most probabilities documented, sources identified, calculations correct",
            3: "Qualitative only (acceptable if justified) OR partial quantification with gaps",
            2: "Incomplete probabilities, questionable sources, calculation errors",
            1: "No quantification when required, fabricated values, fundamental errors"
        }
    },
    "actionability": {
        "name": "Actionability",
        "weight": 0.10,
        "description": "Clear recommendations linked to findings",
        "criteria": {
            5: "Clear prioritized recommendations, cost/benefit considered, validation criteria",
            4: "Recommendations provided, some prioritization, feasible implementation",
            3: "General recommendations, limited prioritization, loose link to findings",
            2: "Vague recommendations, no prioritization, disconnected from analysis",
            1: "No recommendations, analysis ends without conclusions"
        }
    }
}


def display_rubric():
    """Display the full scoring rubric."""
    print("\n" + "="*70)
    print("FAULT TREE ANALYSIS QUALITY RUBRIC")
    print("="*70)
    
    for dim_id, dim in DIMENSIONS.items():
        print(f"\n{dim['name']} (Weight: {dim['weight']*100:.0f}%)")
        print("-" * 50)
        print(f"Focus: {dim['description']}")
        print("\nScoring Criteria:")
        for score, criteria in dim['criteria'].items():
            print(f"  {score}: {criteria}")


def get_score_interactive(dim_id: str, dim: Dict) -> int:
    """Get score for a dimension interactively."""
    print(f"\n{'='*60}")
    print(f"{dim['name']} (Weight: {dim['weight']*100:.0f}%)")
    print(f"{'='*60}")
    print(f"Focus: {dim['description']}\n")
    
    print("Scoring Criteria:")
    for score, criteria in sorted(dim['criteria'].items(), reverse=True):
        print(f"  {score}: {criteria}")
    
    while True:
        try:
            score = int(input(f"\nScore for {dim['name']} (1-5): "))
            if 1 <= score <= 5:
                return score
            print("Please enter a score between 1 and 5.")
        except ValueError:
            print("Please enter a valid integer.")


def calculate_overall_score(scores: Dict[str, int]) -> Tuple[float, str]:
    """Calculate weighted overall score and rating."""
    weighted_sum = 0.0
    total_weight = 0.0
    
    for dim_id, score in scores.items():
        if dim_id in DIMENSIONS:
            weight = DIMENSIONS[dim_id]["weight"]
            weighted_sum += score * weight
            total_weight += weight
    
    # Normalize and scale to 100
    if total_weight > 0:
        avg = weighted_sum / total_weight
        overall = avg * 20  # Scale 1-5 to 0-100
    else:
        overall = 0
    
    # Determine rating
    if overall >= 90:
        rating = "Excellent"
    elif overall >= 80:
        rating = "Good"
    elif overall >= 70:
        rating = "Adequate"
    elif overall >= 60:
        rating = "Marginal"
    else:
        rating = "Inadequate"
    
    return overall, rating


def get_improvement_recommendations(scores: Dict[str, int]) -> List[str]:
    """Generate improvement recommendations based on low scores."""
    recommendations = []
    
    for dim_id, score in scores.items():
        if score <= 3 and dim_id in DIMENSIONS:
            dim = DIMENSIONS[dim_id]
            if dim_id == "system_definition":
                recommendations.append(
                    f"System Definition ({score}/5): Clarify system boundaries, document "
                    "all operating conditions and assumptions."
                )
            elif dim_id == "top_event_clarity":
                recommendations.append(
                    f"Top Event Clarity ({score}/5): Refine top event to be single, specific, "
                    "and measurable with clear failure criteria."
                )
            elif dim_id == "tree_completeness":
                recommendations.append(
                    f"Tree Completeness ({score}/5): Continue developing branches to basic events, "
                    "review gate logic, consider human factors and CCF."
                )
            elif dim_id == "minimal_cut_sets":
                recommendations.append(
                    f"Minimal Cut Sets ({score}/5): Identify and organize all MCS, "
                    "flag single points of failure, analyze CCF potential."
                )
            elif dim_id == "quantification":
                recommendations.append(
                    f"Quantification ({score}/5): Document probability data sources, "
                    "verify calculations, state uncertainty bounds."
                )
            elif dim_id == "actionability":
                recommendations.append(
                    f"Actionability ({score}/5): Develop prioritized recommendations "
                    "linked to specific cut sets and vulnerabilities."
                )
    
    return recommendations


def score_from_json(filepath: str) -> Dict:
    """Load scores from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    scores = {}
    for dim_id in DIMENSIONS.keys():
        if dim_id in data:
            scores[dim_id] = data[dim_id]
        elif "scores" in data and dim_id in data["scores"]:
            scores[dim_id] = data["scores"][dim_id]
    
    return scores


def interactive_scoring() -> Dict[str, int]:
    """Conduct interactive scoring session."""
    print("\n" + "="*70)
    print("FAULT TREE ANALYSIS QUALITY SCORING")
    print("="*70)
    print("\nYou will score the analysis on 6 dimensions.")
    print("Each dimension is rated 1-5 (Inadequate to Excellent).")
    
    view_rubric = input("\nView full rubric before scoring? (y/n): ").lower()
    if view_rubric == 'y':
        display_rubric()
    
    scores = {}
    for dim_id, dim in DIMENSIONS.items():
        scores[dim_id] = get_score_interactive(dim_id, dim)
    
    return scores



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
    parser = argparse.ArgumentParser(description="Score FTA Quality")
    parser.add_argument("input_file", nargs="?", help="JSON file with scores")
    parser.add_argument("--output", "-o", help="Output JSON file for results")
    parser.add_argument("--rubric", "-r", action="store_true", help="Display rubric and exit")
    
    args = parser.parse_args()

    if args.input_file:
        args.input_file = _validate_path(args.input_file, {'.json'}, "input file")
    if args.output:
        args.output = _validate_path(args.output, {'.json', '.txt'}, "output file")
    
    if args.rubric:
        display_rubric()
        return
    
    # Get scores
    if args.input_file:
        scores = score_from_json(args.input_file)
    else:
        scores = interactive_scoring()
    
    # Calculate overall score
    overall, rating = calculate_overall_score(scores)
    
    # Get recommendations
    recommendations = get_improvement_recommendations(scores)
    
    # Display results
    print("\n" + "="*70)
    print("SCORING RESULTS")
    print("="*70)
    
    print("\nDimension Scores:")
    print("-" * 50)
    for dim_id, score in scores.items():
        if dim_id in DIMENSIONS:
            dim = DIMENSIONS[dim_id]
            print(f"  {dim['name']:25s} {score}/5  (Weight: {dim['weight']*100:.0f}%)")
    
    print("\n" + "-"*50)
    print(f"Overall Score: {overall:.1f}/100 ({rating})")
    
    if overall >= 70:
        print("✓ PASSES minimum threshold (70 points)")
    else:
        print("✗ BELOW minimum threshold (70 points)")
    
    if recommendations:
        print("\nImprovement Recommendations:")
        print("-" * 50)
        for rec in recommendations:
            print(f"• {rec}")
    
    # Prepare output
    results = {
        "scores": scores,
        "overall_score": overall,
        "rating": rating,
        "passes_threshold": overall >= 70,
        "recommendations": recommendations
    }
    
    # Save output
    output_file = args.output or "fta_score.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
