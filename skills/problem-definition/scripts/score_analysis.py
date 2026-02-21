#!/usr/bin/env python3
"""
Problem Definition Quality Scoring Calculator

Calculates quality scores for problem definition analyses based on four weighted dimensions.
Can be used interactively or with JSON input.

Usage:
    Interactive: python score_analysis.py
    JSON input:  python score_analysis.py --json '{"completeness": 4, ...}'
    From file:   python score_analysis.py --file definition_scores.json
"""

import os
import argparse
import json
import sys
from dataclasses import dataclass
from typing import Optional


# Scoring weights (sum to 1.0)
WEIGHTS = {
    "completeness": 0.25,
    "specificity": 0.30,
    "measurability": 0.25,
    "neutrality": 0.20,
}

# Dimension descriptions and criteria
DIMENSIONS = {
    "completeness": {
        "name": "Completeness",
        "description": "Coverage of 5W2H and IS/IS NOT dimensions",
        "criteria": {
            5: "All 5W2H dimensions addressed; complete IS/IS NOT analysis; deviation clearly stated",
            4: "Most dimensions covered; 1-2 minor gaps; IS/IS NOT mostly complete",
            3: "Key dimensions present; 2-3 gaps; partial IS/IS NOT analysis",
            2: "Several dimensions missing; incomplete analysis; significant gaps",
            1: "Minimal information; most dimensions missing; no IS/IS NOT",
        },
    },
    "specificity": {
        "name": "Specificity",
        "description": "Precision and detail level of the problem description",
        "criteria": {
            5: "Highly specific: exact part numbers, locations, dates, counts; no ambiguity",
            4: "Mostly specific with minor generalizations; clear focus area",
            3: "Moderately specific; some vague terms; generally understandable",
            2: "Vague language; general descriptions; multiple interpretations possible",
            1: "Very general; could apply to many problems; lacks focus",
        },
    },
    "measurability": {
        "name": "Measurability",
        "description": "Presence of quantifiable metrics and verification criteria",
        "criteria": {
            5: "Quantified magnitude, frequency, trend; clear success criteria; baseline established",
            4: "Good metrics present; minor gaps in quantification",
            3: "Some metrics; mixed qualitative/quantitative; baseline unclear",
            2: "Mostly qualitative; few numbers; hard to measure improvement",
            1: "No metrics; entirely qualitative; cannot verify resolution",
        },
    },
    "neutrality": {
        "name": "Neutrality",
        "description": "Freedom from embedded causes, solutions, and blame",
        "criteria": {
            5: "Pure description of deviation; no cause speculation; no solution hints; no blame",
            4: "Mostly neutral with minor cause/solution hints that can be edited out",
            3: "Some cause language present but not dominant; minor blame",
            2: "Significant cause or solution language; person-blame evident",
            1: "Problem statement IS a cause or solution; heavy blame assignment",
        },
    },
}


@dataclass
class AnalysisScores:
    """Container for problem definition dimension scores."""
    completeness: int
    specificity: int
    measurability: int
    neutrality: int

    def validate(self) -> bool:
        """Validate all scores are between 1 and 5."""
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if not isinstance(value, int) or value < 1 or value > 5:
                return False
        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "completeness": self.completeness,
            "specificity": self.specificity,
            "measurability": self.measurability,
            "neutrality": self.neutrality,
        }


def calculate_score(scores: AnalysisScores) -> dict:
    """
    Calculate overall quality score from dimension scores.

    Returns dict with:
        - dimension_scores: Individual scores with weights
        - weighted_sum: Sum of (score * weight)
        - overall_score: Final score out of 100
        - rating: Text rating
        - passing: Whether meets 70-point threshold
        - critical_failure: Whether neutrality is critically low
    """
    scores_dict = scores.to_dict()

    # Calculate weighted contributions
    dimension_scores = {}
    weighted_sum = 0.0

    for dimension, weight in WEIGHTS.items():
        score = scores_dict[dimension]
        weighted_contribution = score * weight
        weighted_sum += weighted_contribution
        dimension_scores[dimension] = {
            "score": score,
            "weight": weight,
            "weighted": round(weighted_contribution, 3),
            "name": DIMENSIONS[dimension]["name"],
        }

    # Convert to 100-point scale
    overall_score = round(weighted_sum * 20, 1)

    # Determine rating
    if overall_score >= 90:
        rating = "Excellent"
        interpretation = "Problem definition is thorough and ready for root cause analysis."
    elif overall_score >= 80:
        rating = "Good"
        interpretation = "Problem definition is solid with minor improvement opportunities."
    elif overall_score >= 70:
        rating = "Acceptable"
        interpretation = "Meets minimum standards. Consider strengthening weak areas."
    elif overall_score >= 60:
        rating = "Marginal"
        interpretation = "Significant gaps exist. Revisit weak dimensions before proceeding."
    else:
        rating = "Inadequate"
        interpretation = "Problem definition insufficient. Rework required before analysis."

    # Check for critical neutrality failure
    critical_failure = scores_dict["neutrality"] <= 2
    if critical_failure:
        interpretation += " CRITICAL: Neutrality score indicates embedded causes/solutions that must be removed."

    # Identify weakest dimensions for improvement recommendations
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1]["score"])
    weakest = [d for d in sorted_dims if d[1]["score"] <= 3][:3]

    recommendations = []
    for dim_key, dim_data in weakest:
        dim_info = DIMENSIONS[dim_key]
        recommendations.append({
            "dimension": dim_info["name"],
            "current_score": dim_data["score"],
            "improvement_target": dim_info["criteria"].get(
                dim_data["score"] + 1, dim_info["criteria"][5]
            ),
        })

    return {
        "dimension_scores": dimension_scores,
        "weighted_sum": round(weighted_sum, 3),
        "overall_score": overall_score,
        "rating": rating,
        "interpretation": interpretation,
        "passing": overall_score >= 70 and not critical_failure,
        "critical_failure": critical_failure,
        "recommendations": recommendations,
    }


def print_score_report(result: dict) -> None:
    """Print formatted score report to console."""
    print("\n" + "=" * 60)
    print("PROBLEM DEFINITION QUALITY SCORE REPORT")
    print("=" * 60)

    print("\nDIMENSION SCORES:")
    print("-" * 60)
    print(f"{'Dimension':<20} {'Score':>6} {'Weight':>8} {'Weighted':>10}")
    print("-" * 60)

    for dim_key, dim_data in result["dimension_scores"].items():
        print(
            f"{dim_data['name']:<20} "
            f"{dim_data['score']:>6}/5 "
            f"{dim_data['weight']*100:>7.0f}% "
            f"{dim_data['weighted']:>10.3f}"
        )

    print("-" * 60)
    print(f"{'Weighted Sum:':<20} {result['weighted_sum']:>30.3f}")
    print(f"{'Overall Score:':<20} {result['overall_score']:>30.1f}/100")
    print("=" * 60)

    # Rating with pass/fail
    passing_marker = "✓ PASS" if result["passing"] else "✗ FAIL"
    print(f"\nRATING: {result['rating']} ({passing_marker})")
    print(f"\n{result['interpretation']}")

    # Critical warning
    if result["critical_failure"]:
        print("\n" + "!" * 60)
        print("CRITICAL: Neutrality score indicates embedded causes or solutions.")
        print("The problem statement must be revised before proceeding.")
        print("!" * 60)

    # Improvement recommendations
    if result["recommendations"]:
        print("\nIMPROVEMENT RECOMMENDATIONS:")
        print("-" * 60)
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"\n{i}. {rec['dimension']} (current: {rec['current_score']}/5)")
            print(f"   To improve: {rec['improvement_target']}")

    print("\n" + "=" * 60)


def interactive_scoring() -> AnalysisScores:
    """Collect scores interactively from user."""
    print("\nPROBLEM DEFINITION QUALITY SCORING")
    print("=" * 50)
    print("Rate each dimension from 1 (Inadequate) to 5 (Excellent)")
    print()

    scores = {}

    for dim_key, dim_info in DIMENSIONS.items():
        print(f"\n{dim_info['name']}")
        print(f"  {dim_info['description']}")
        print("\n  Scoring Guide:")
        for score, desc in sorted(dim_info["criteria"].items(), reverse=True):
            # Truncate long descriptions for display
            display_desc = desc[:65] + "..." if len(desc) > 65 else desc
            print(f"    {score}: {display_desc}")

        while True:
            try:
                value = int(input(f"\n  Enter score (1-5): "))
                if 1 <= value <= 5:
                    scores[dim_key] = value
                    break
                else:
                    print("  Please enter a number between 1 and 5.")
            except ValueError:
                print("  Please enter a valid number.")

    return AnalysisScores(**scores)



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
        description="Calculate Problem Definition Quality Score"
    )
    parser.add_argument(
        "--json",
        type=str,
        help='JSON string with scores: {"completeness": 4, ...}',
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file with scores",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for JSON results",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output JSON, no formatted report",
    )

    args = parser.parse_args()

    args.file = _validate_path(args.file, {'.json'}, "file")
    args.output = _validate_path(args.output, {'.htm', '.html', '.json', '.md', '.svg', '.txt'}, "output")

    # Get scores from input source
    if args.json:
        try:
            data = json.loads(args.json)
            scores = AnalysisScores(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        try:
            with open(args.file, "r") as f:
                data = json.load(f)
            scores = AnalysisScores(**data)
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        scores = interactive_scoring()

    # Validate scores
    if not scores.validate():
        print("Error: All scores must be integers between 1 and 5.", file=sys.stderr)
        sys.exit(1)

    # Calculate results
    result = calculate_score(scores)
    result["input_scores"] = scores.to_dict()

    # Output results
    if not args.quiet:
        print_score_report(result)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    elif args.quiet:
        print(json.dumps(result, indent=2))

    # Return exit code based on passing
    sys.exit(0 if result["passing"] else 1)


if __name__ == "__main__":
    main()
