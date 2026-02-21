#!/usr/bin/env python3
"""
Fishbone Diagram Analysis Scoring Calculator

Calculates quality score based on 6 dimensions:
- Problem Clarity (15%)
- Category Coverage (20%)
- Cause Depth (25%)
- Cause Quality (20%)
- Prioritization (10%)
- Documentation (10%)

Usage:
  Interactive: python score_analysis.py
  JSON input:  python score_analysis.py --json '{"problem_clarity": 4, ...}'
  File input:  python score_analysis.py --file scores.json
  Quiet mode:  python score_analysis.py --json '...' --quiet
"""

import os
import argparse
import json
import sys

# Scoring dimensions with weights
DIMENSIONS = {
    "problem_clarity": {
        "weight": 0.15,
        "name": "Problem Clarity",
        "description": "Specific, measurable, non-blaming problem statement",
        "criteria": {
            5: "Specific, measurable, time-bounded. Observable effect. Includes what/where/when/extent.",
            4: "Specific and measurable. Minor gaps in context.",
            3: "Moderately specific. Some vagueness in what/where/when.",
            2: "Vague or broad. Missing critical specifics.",
            1: "Very vague, abstract, or unclear. May embed cause or solution."
        }
    },
    "category_coverage": {
        "weight": 0.20,
        "name": "Category Coverage",
        "description": "All relevant categories explored with adequate causes",
        "criteria": {
            5: "All categories explored with 3+ causes each. No blind spots.",
            4: "All categories have 2+ causes. Minor gaps in 1-2 categories.",
            3: "Most categories explored. 1-2 categories thin or missing.",
            2: "Several categories thin or missing. Uneven coverage.",
            1: "Many categories empty. Major blind spots evident."
        }
    },
    "cause_depth": {
        "weight": 0.25,
        "name": "Cause Depth",
        "description": "2-3 levels of sub-causes for major causes",
        "criteria": {
            5: "Major causes have 3+ levels. Clear causal chains to actionable root causes.",
            4: "Most major causes have 2-3 levels. Good drilling into key causes.",
            3: "Some sub-causes but inconsistent. Mix of deep and shallow.",
            2: "Mostly Level 1 causes only. Limited sub-cause drilling.",
            1: "No sub-causes. Only top-level causes listed."
        }
    },
    "cause_quality": {
        "weight": 0.20,
        "name": "Cause Quality",
        "description": "Specific, distinct, process-focused, evidence-based causes",
        "criteria": {
            5: "Causes specific, distinct, process/system focused. Evidence-based.",
            4: "Most causes specific and distinct. Generally process-focused.",
            3: "Adequate specificity. Some vagueness or overlap.",
            2: "Many vague causes. Person-blame present. Some restate problem.",
            1: "Causes vague, generic, or mostly person-blame."
        }
    },
    "prioritization": {
        "weight": 0.10,
        "name": "Prioritization",
        "description": "Clear method applied, top causes identified with rationale",
        "criteria": {
            5: "Clear method (multi-voting, impact-effort). Top 3-5 identified with verification plan.",
            4: "Method used. Top causes identified. Rationale documented.",
            3: "Some prioritization. Top causes identified informally.",
            2: "Minimal prioritization. No clear method.",
            1: "No prioritization. All causes treated equally."
        }
    },
    "documentation": {
        "weight": 0.10,
        "name": "Documentation",
        "description": "Complete visual diagram, clear labeling, shareable output",
        "criteria": {
            5: "Complete visual diagram. Clear labeling. Professional. Action items assigned.",
            4: "Good diagram. Minor labeling gaps. Presentable output.",
            3: "Basic diagram. Adequate labeling. Needs cleanup for sharing.",
            2: "Rough diagram. Poor labeling. Not shareable as-is.",
            1: "No diagram or very incomplete. Not usable."
        }
    }
}


def get_rating(score):
    """Convert numeric score to rating."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Poor"


def calculate_score(scores):
    """Calculate weighted score from dimension scores."""
    weighted_sum = 0
    for dim_key, dim_score in scores.items():
        if dim_key in DIMENSIONS:
            weighted_sum += dim_score * DIMENSIONS[dim_key]["weight"]
    
    # Convert from 1-5 scale to 0-100
    final_score = weighted_sum * 20
    return round(final_score, 1)


def get_improvement_recommendations(scores):
    """Identify weakest dimensions and provide recommendations."""
    recommendations = []
    
    # Sort dimensions by score (lowest first)
    sorted_dims = sorted(scores.items(), key=lambda x: x[1])
    
    # Get bottom 2 dimensions
    weak_dims = sorted_dims[:2]
    
    recommendations_map = {
        "problem_clarity": "Apply 5W2H framework to sharpen the problem statement. Focus on observable effects, not assumed causes.",
        "category_coverage": "Use prompting questions for each category. Challenge 'this doesn't apply' assumptions.",
        "cause_depth": "For each major cause, ask 'Why might this happen?' 2-3 more times. Target Level 3 depth.",
        "cause_quality": "Review causes for person-blame and convert to system focus. Add specificity with 'What exactly?'",
        "prioritization": "Conduct multi-voting exercise (3 votes per participant) or create impact-effort matrix.",
        "documentation": "Generate formal diagram using generate_diagram.py. Ensure clear labeling and action items."
    }
    
    for dim_key, score in weak_dims:
        if score < 4:  # Only recommend for dimensions scoring below 4
            recommendations.append({
                "dimension": DIMENSIONS[dim_key]["name"],
                "score": score,
                "recommendation": recommendations_map.get(dim_key, "Review quality rubric for improvement guidance.")
            })
    
    return recommendations


def interactive_scoring():
    """Run interactive scoring session."""
    print("\n" + "="*60)
    print("FISHBONE DIAGRAM QUALITY ASSESSMENT")
    print("="*60)
    print("\nRate each dimension from 1-5:")
    print("  1 = Poor    2 = Below Average    3 = Average")
    print("  4 = Good    5 = Excellent")
    print()
    
    scores = {}
    
    for dim_key, dim_info in DIMENSIONS.items():
        print(f"\n--- {dim_info['name']} ({int(dim_info['weight']*100)}%) ---")
        print(f"    {dim_info['description']}")
        print()
        for score_val, criteria in dim_info["criteria"].items():
            print(f"    {score_val}: {criteria}")
        
        while True:
            try:
                score = int(input(f"\n    Enter score for {dim_info['name']} (1-5): "))
                if 1 <= score <= 5:
                    scores[dim_key] = score
                    break
                else:
                    print("    Please enter a value between 1 and 5.")
            except ValueError:
                print("    Please enter a valid integer.")
    
    return scores


def print_results(scores, final_score, quiet=False):
    """Print scoring results."""
    if quiet:
        # JSON output only
        result = {
            "scores": scores,
            "final_score": final_score,
            "rating": get_rating(final_score),
            "passed": final_score >= 70,
            "recommendations": get_improvement_recommendations(scores)
        }
        print(json.dumps(result, indent=2))
        return
    
    print("\n" + "="*60)
    print("SCORING RESULTS")
    print("="*60)
    
    print("\nDimension Scores:")
    print("-" * 50)
    for dim_key, score in scores.items():
        dim = DIMENSIONS[dim_key]
        weighted = score * dim["weight"] * 20
        print(f"  {dim['name']:<20} {score}/5  (weighted: {weighted:.1f})")
    
    print("-" * 50)
    print(f"  {'TOTAL SCORE':<20} {final_score}/100")
    print(f"  {'Rating':<20} {get_rating(final_score)}")
    print(f"  {'Status':<20} {'PASS ✓' if final_score >= 70 else 'NEEDS IMPROVEMENT'}")
    
    # Recommendations
    recommendations = get_improvement_recommendations(scores)
    if recommendations:
        print("\n" + "="*60)
        print("IMPROVEMENT RECOMMENDATIONS")
        print("="*60)
        for rec in recommendations:
            print(f"\n  [{rec['dimension']} - Score: {rec['score']}/5]")
            print(f"  → {rec['recommendation']}")
    
    print()



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
        description="Fishbone Diagram Analysis Quality Scoring Calculator"
    )
    parser.add_argument(
        "--json",
        type=str,
        help='JSON string with scores, e.g., \'{"problem_clarity": 4, "category_coverage": 3, ...}\''
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with scores"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Output only JSON result (no interactive prompts)"
    )
    
    args = parser.parse_args()

    args.file = _validate_path(args.file, {'.json'}, "file")
    
    # Get scores from appropriate source
    if args.json:
        try:
            scores = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.quiet:
            print("Error: --quiet requires --json or --file input", file=sys.stderr)
            sys.exit(1)
        scores = interactive_scoring()
    
    # Validate scores
    required_dims = set(DIMENSIONS.keys())
    provided_dims = set(scores.keys())
    
    if not required_dims.issubset(provided_dims):
        missing = required_dims - provided_dims
        print(f"Error: Missing dimensions: {missing}", file=sys.stderr)
        sys.exit(1)
    
    for dim_key, score in scores.items():
        if dim_key in DIMENSIONS:
            if not isinstance(score, (int, float)) or not 1 <= score <= 5:
                print(f"Error: Invalid score for {dim_key}: {score} (must be 1-5)", file=sys.stderr)
                sys.exit(1)
    
    # Calculate and display results
    final_score = calculate_score(scores)
    print_results(scores, final_score, quiet=args.quiet)
    
    # Exit code based on pass/fail
    sys.exit(0 if final_score >= 70 else 1)


if __name__ == "__main__":
    main()
