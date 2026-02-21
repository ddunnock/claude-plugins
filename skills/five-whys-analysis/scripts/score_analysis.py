#!/usr/bin/env python3
"""
5 Whys Analysis Quality Scoring Calculator

Calculates quality scores for 5 Whys root cause analyses based on six weighted dimensions.
Can be used interactively or with JSON input.

Usage:
    Interactive: python score_analysis.py
    JSON input:  python score_analysis.py --json '{"problem_definition": 4, ...}'
    From file:   python score_analysis.py --file analysis_scores.json
"""

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Scoring weights
WEIGHTS = {
    "problem_definition": 0.15,
    "causal_chain_logic": 0.25,
    "evidence_basis": 0.20,
    "root_cause_depth": 0.20,
    "actionability": 0.10,
    "countermeasures": 0.10,
}

# Dimension descriptions
DIMENSIONS = {
    "problem_definition": {
        "name": "Problem Definition",
        "description": "Clarity, specificity, and measurability of the problem statement",
        "criteria": {
            5: "Specific, measurable, time-bound; complete 5W2H; no embedded causes",
            4: "Mostly specific with minor gaps; clear deviation statement",
            3: "Identifies problem but lacks 1-2 dimensions; somewhat vague",
            2: "Vague statement; missing key dimensions; may contain assumptions",
            1: "Too broad, unclear, or contains assumed causes/solutions",
        },
    },
    "causal_chain_logic": {
        "name": "Causal Chain Logic",
        "description": "Logical consistency and verification of each link in the chain",
        "criteria": {
            5: "Every link logical, specific, verified; 'therefore' test passes",
            4: "Mostly logical with minor gaps; most links verified",
            3: "Generally follows but 1-2 links weak or assumed",
            2: "Multiple logical gaps; several unverified assumptions",
            1: "Illogical, jumps to conclusions, or contradictory",
        },
    },
    "evidence_basis": {
        "name": "Evidence Basis",
        "description": "Factual support for each answer in the chain",
        "criteria": {
            5: "All answers supported by documented evidence; sources cited",
            4: "Most evidence-based; 1-2 reasonable inferences marked",
            3: "Mix of evidence and inference; assumptions identified",
            2: "Primarily assumption-based; limited factual support",
            1: "No evidence; entirely speculative or opinion-based",
        },
    },
    "root_cause_depth": {
        "name": "Root Cause Depth",
        "description": "Whether analysis reached process/system level vs symptoms",
        "criteria": {
            5: "Systemic/process level; prevents recurrence; controllable",
            4: "Actionable process cause; may have deeper factors but addressable",
            3: "Contributing cause; would reduce but not eliminate recurrence",
            2: "Symptom level; only temporary relief",
            1: "Person-blame, external factor, or unactionable",
        },
    },
    "actionability": {
        "name": "Actionability",
        "description": "Whether the root cause is within control to address",
        "criteria": {
            5: "100% within control; clear ownership; resources available",
            4: "Largely controllable; may need coordination",
            3: "Partial control; requires escalation or approval",
            2: "Limited control; significant external dependencies",
            1: "External, uncontrollable, or 'acts of God'",
        },
    },
    "countermeasures": {
        "name": "Countermeasures",
        "description": "Quality of corrective actions developed",
        "criteria": {
            5: "Specific actions with owners, dates, criteria; verification & sustainability",
            4: "Clear actions assigned; may lack some verification detail",
            3: "General actions; ownership unclear; limited verification",
            2: "Vague actions; no ownership or timeline",
            1: "No countermeasures or addresses symptoms only",
        },
    },
}


@dataclass
class AnalysisScores:
    """Container for analysis dimension scores."""
    problem_definition: int
    causal_chain_logic: int
    evidence_basis: int
    root_cause_depth: int
    actionability: int
    countermeasures: int
    
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
            "problem_definition": self.problem_definition,
            "causal_chain_logic": self.causal_chain_logic,
            "evidence_basis": self.evidence_basis,
            "root_cause_depth": self.root_cause_depth,
            "actionability": self.actionability,
            "countermeasures": self.countermeasures,
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
        interpretation = "Analysis is thorough, evidence-based, and actionable. Proceed with confidence."
    elif overall_score >= 80:
        rating = "Good"
        interpretation = "Analysis is solid with minor improvement opportunities. Acceptable for most applications."
    elif overall_score >= 70:
        rating = "Acceptable"
        interpretation = "Meets minimum standards. Consider strengthening weak areas before major decisions."
    elif overall_score >= 60:
        rating = "Marginal"
        interpretation = "Significant gaps exist. Revisit weak dimensions before proceeding."
    else:
        rating = "Inadequate"
        interpretation = "Insufficient for decision-making. Rework required."
    
    # Identify weakest dimensions for improvement recommendations
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1]["score"])
    weakest = [d for d in sorted_dims if d[1]["score"] <= 3][:3]
    
    recommendations = []
    for dim_key, dim_data in weakest:
        dim_info = DIMENSIONS[dim_key]
        recommendations.append({
            "dimension": dim_info["name"],
            "current_score": dim_data["score"],
            "improvement_target": dim_info["criteria"].get(dim_data["score"] + 1, dim_info["criteria"][5]),
        })
    
    return {
        "dimension_scores": dimension_scores,
        "weighted_sum": round(weighted_sum, 3),
        "overall_score": overall_score,
        "rating": rating,
        "interpretation": interpretation,
        "passing": overall_score >= 70,
        "recommendations": recommendations,
    }


def print_score_report(result: dict) -> None:
    """Print formatted score report to console."""
    print("\n" + "=" * 60)
    print("5 WHYS ANALYSIS QUALITY SCORE REPORT")
    print("=" * 60)
    
    print("\nDIMENSION SCORES:")
    print("-" * 60)
    print(f"{'Dimension':<25} {'Score':>6} {'Weight':>8} {'Weighted':>10}")
    print("-" * 60)
    
    for dim_key, dim_data in result["dimension_scores"].items():
        print(f"{dim_data['name']:<25} {dim_data['score']:>6}/5 {dim_data['weight']*100:>7.0f}% {dim_data['weighted']:>10.3f}")
    
    print("-" * 60)
    print(f"{'Weighted Sum:':<25} {result['weighted_sum']:>35.3f}")
    print(f"{'Overall Score:':<25} {result['overall_score']:>35.1f}/100")
    print("=" * 60)
    
    # Rating with color indication (using simple text markers)
    passing_marker = "✓ PASS" if result["passing"] else "✗ FAIL"
    print(f"\nRATING: {result['rating']} ({passing_marker})")
    print(f"\n{result['interpretation']}")
    
    if result["recommendations"]:
        print("\nIMPROVEMENT RECOMMENDATIONS:")
        print("-" * 60)
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"\n{i}. {rec['dimension']} (current: {rec['current_score']}/5)")
            print(f"   To improve: {rec['improvement_target']}")
    
    print("\n" + "=" * 60)


def interactive_scoring() -> AnalysisScores:
    """Collect scores interactively from user."""
    print("\n5 WHYS ANALYSIS QUALITY SCORING")
    print("=" * 50)
    print("Rate each dimension from 1 (Inadequate) to 5 (Excellent)")
    print()
    
    scores = {}
    
    for dim_key, dim_info in DIMENSIONS.items():
        print(f"\n{dim_info['name']}")
        print(f"  {dim_info['description']}")
        print("\n  Scoring Guide:")
        for score, desc in sorted(dim_info["criteria"].items(), reverse=True):
            print(f"    {score}: {desc}")
        
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


def _validate_path(filepath: str, allowed_extensions: set, label: str) -> None:
    """Validate file path: reject traversal and restrict extensions."""
    if ".." in filepath:
        print(f"Error: Path traversal not allowed in {label}: {filepath}", file=sys.stderr)
        sys.exit(1)
    ext = Path(filepath).suffix.lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got '{ext}'", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate 5 Whys Analysis Quality Score"
    )
    parser.add_argument(
        "--json",
        type=str,
        help="JSON string with scores: {\"problem_definition\": 4, ...}",
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

    if args.file:
        _validate_path(args.file, {".json"}, "input file")
    if args.output:
        _validate_path(args.output, {".json"}, "output file")

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
