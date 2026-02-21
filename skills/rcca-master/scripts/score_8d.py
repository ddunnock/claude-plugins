#!/usr/bin/env python3
"""
8D Quality Scoring Calculator

Calculates quality scores for 8D investigations based on phase completion and rigor.
Supports scoring individual phases or complete investigations.

Usage:
    python score_8d.py --file session.json
    python score_8d.py --interactive
    python score_8d.py --json '{"d0": 4, "d1": 3, ...}'
"""

import os
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_ALLOWED_INPUT_EXTENSIONS = {'.json'}
_ALLOWED_OUTPUT_EXTENSIONS = {'.json'}


def _validate_path(filepath: str, allowed_extensions: set, label: str) -> Path:
    """Validate a file path: check extension, reject traversal."""
    path = Path(filepath).resolve()
    if '..' in Path(filepath).parts:
        print(f"Error: Path traversal not allowed in {label}: {filepath}", file=sys.stderr)
        sys.exit(1)
    if path.suffix.lower() not in allowed_extensions:
        print(f"Error: {label} file must be one of {allowed_extensions}, got '{path.suffix}'", file=sys.stderr)
        sys.exit(1)
    return path


# Phase weights (sum to 1.0)
PHASE_WEIGHTS = {
    "d0": 0.05,   # Initial Assessment
    "d1": 0.05,   # Team Formation
    "d2": 0.15,   # Problem Definition
    "d3": 0.10,   # Containment
    "d4": 0.25,   # Root Cause Analysis
    "d5": 0.15,   # Corrective Action Selection
    "d6": 0.10,   # Implementation
    "d7": 0.10,   # Prevention
    "d8": 0.05,   # Closure
}

# Phase definitions with scoring criteria
PHASES = {
    "d0": {
        "name": "D0 - Initial Assessment",
        "description": "Severity, urgency, scope, and complexity evaluation",
        "criteria": {
            5: "Complete assessment with severity matrix; clear complexity rating; documented decision to proceed with 8D",
            4: "All key dimensions assessed; minor gaps in documentation",
            3: "Basic assessment complete; some dimensions missing",
            2: "Partial assessment; insufficient basis for planning",
            1: "No meaningful assessment; jumped directly to investigation",
        },
    },
    "d1": {
        "name": "D1 - Team Formation",
        "description": "Cross-functional team assembly with clear roles",
        "criteria": {
            5: "Cross-functional team with champion, all roles assigned, subject matter experts included",
            4: "Adequate team coverage; minor role gaps",
            3: "Basic team formed; missing some key functions",
            2: "Incomplete team; champion unclear",
            1: "No team formed; single person investigation",
        },
    },
    "d2": {
        "name": "D2 - Problem Definition",
        "description": "5W2H and IS/IS NOT analysis quality",
        "criteria": {
            5: "Complete 5W2H, thorough IS/IS NOT, specific measurable statement, no embedded cause",
            4: "Good definition with minor gaps; clear statement",
            3: "Basic definition; some dimensions weak or missing",
            2: "Vague statement; significant gaps; may contain assumptions",
            1: "No meaningful definition; jumped to cause speculation",
        },
    },
    "d3": {
        "name": "D3 - Containment",
        "description": "Interim containment action effectiveness",
        "criteria": {
            5: "All affected product/scope contained; verified effective; customer protected",
            4: "Good containment; verification complete; minor gaps",
            3: "Basic containment in place; verification incomplete",
            2: "Partial containment; customer exposure continues",
            1: "No containment; problem continues to occur",
        },
    },
    "d4": {
        "name": "D4 - Root Cause Analysis",
        "description": "Root cause identification and verification",
        "criteria": {
            5: "Verified root cause at system/process level; appropriate tool used; evidence-based",
            4: "Strong root cause with good evidence; minor verification gaps",
            3: "Plausible root cause; limited verification; may be contributing factor",
            2: "Symptom-level cause; poor evidence; unverified",
            1: "Person-blame, speculation, or no analysis performed",
        },
    },
    "d5": {
        "name": "D5 - Corrective Action Selection",
        "description": "Permanent corrective action quality",
        "criteria": {
            5: "Actions address root cause directly; prevention and detection controls; clear success criteria",
            4: "Good actions with ownership; minor criteria gaps",
            3: "Actions defined but may not fully address root cause",
            2: "Weak actions; address symptoms more than cause",
            1: "No meaningful corrective actions; repeat of containment",
        },
    },
    "d6": {
        "name": "D6 - Implementation",
        "description": "Execution and verification of corrective actions",
        "criteria": {
            5: "All actions implemented on time; effectiveness verified; evidence documented",
            4: "Most actions complete; verification adequate",
            3: "Implementation in progress; some delays; partial verification",
            2: "Significant delays; limited verification",
            1: "Actions not implemented or abandoned",
        },
    },
    "d7": {
        "name": "D7 - Prevention",
        "description": "Systemic improvements and horizontal deployment",
        "criteria": {
            5: "Root cause eliminated systemically; similar products/processes addressed; standards updated",
            4: "Good systemic actions; some horizontal deployment",
            3: "Local fix only; limited systemic improvement",
            2: "No systemic action; problem may recur elsewhere",
            1: "No prevention actions; learning not captured",
        },
    },
    "d8": {
        "name": "D8 - Closure",
        "description": "Verification period and closure rigor",
        "criteria": {
            5: "Adequate verification period; metrics confirm effectiveness; containment removed; lessons learned captured",
            4: "Good closure with minor documentation gaps",
            3: "Basic closure; verification period short; lessons learned incomplete",
            2: "Premature closure; effectiveness unconfirmed",
            1: "No formal closure; problem unresolved",
        },
    },
}


@dataclass
class PhaseScores:
    """Container for 8D phase scores."""
    d0: int
    d1: int
    d2: int
    d3: int
    d4: int
    d5: int
    d6: int
    d7: int
    d8: int

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
            "d0": self.d0,
            "d1": self.d1,
            "d2": self.d2,
            "d3": self.d3,
            "d4": self.d4,
            "d5": self.d5,
            "d6": self.d6,
            "d7": self.d7,
            "d8": self.d8,
        }


def calculate_score(scores: PhaseScores) -> dict:
    """
    Calculate overall 8D quality score from phase scores.

    Returns dict with:
        - phase_scores: Individual scores with weights
        - weighted_sum: Sum of (score * weight)
        - overall_score: Final score out of 100
        - rating: Text rating
        - passing: Whether meets 70-point threshold
        - critical_phase_warnings: Phases below minimum threshold
    """
    scores_dict = scores.to_dict()

    # Calculate weighted contributions
    phase_scores = {}
    weighted_sum = 0.0

    for phase, weight in PHASE_WEIGHTS.items():
        score = scores_dict[phase]
        weighted_contribution = score * weight
        weighted_sum += weighted_contribution
        phase_scores[phase] = {
            "score": score,
            "weight": weight,
            "weighted": round(weighted_contribution, 3),
            "name": PHASES[phase]["name"],
        }

    # Convert to 100-point scale
    overall_score = round(weighted_sum * 20, 1)

    # Determine rating
    if overall_score >= 90:
        rating = "Excellent"
        interpretation = "Investigation is thorough and rigorous. High confidence in effectiveness."
    elif overall_score >= 80:
        rating = "Good"
        interpretation = "Investigation is solid with minor gaps. Acceptable for most applications."
    elif overall_score >= 70:
        rating = "Acceptable"
        interpretation = "Meets minimum standards. Consider strengthening weak phases."
    elif overall_score >= 60:
        rating = "Marginal"
        interpretation = "Significant gaps exist. Rework weak phases before closure."
    else:
        rating = "Inadequate"
        interpretation = "Investigation quality insufficient. Major rework required."

    # Check for critical phase failures (D2, D4, D5 are critical)
    critical_phases = ["d2", "d4", "d5"]
    critical_warnings = []
    for phase in critical_phases:
        if scores_dict[phase] <= 2:
            critical_warnings.append({
                "phase": PHASES[phase]["name"],
                "score": scores_dict[phase],
                "warning": f"Critical phase {phase.upper()} scored {scores_dict[phase]}/5 - investigation validity at risk",
            })

    # Identify weakest phases for improvement
    sorted_phases = sorted(phase_scores.items(), key=lambda x: x[1]["score"])
    weakest = [p for p in sorted_phases if p[1]["score"] <= 3][:3]

    recommendations = []
    for phase_key, phase_data in weakest:
        phase_info = PHASES[phase_key]
        current_score = phase_data["score"]
        target_desc = phase_info["criteria"].get(
            current_score + 1, phase_info["criteria"][5]
        )
        recommendations.append({
            "phase": phase_info["name"],
            "current_score": current_score,
            "improvement_target": target_desc,
        })

    return {
        "phase_scores": phase_scores,
        "weighted_sum": round(weighted_sum, 3),
        "overall_score": overall_score,
        "rating": rating,
        "interpretation": interpretation,
        "passing": overall_score >= 70 and len(critical_warnings) == 0,
        "critical_warnings": critical_warnings,
        "recommendations": recommendations,
    }


def print_score_report(result: dict) -> None:
    """Print formatted score report to console."""
    print("\n" + "=" * 70)
    print("8D INVESTIGATION QUALITY SCORE REPORT")
    print("=" * 70)

    print("\nPHASE SCORES:")
    print("-" * 70)
    print(f"{'Phase':<35} {'Score':>6} {'Weight':>8} {'Weighted':>10}")
    print("-" * 70)

    for phase_key in PHASE_WEIGHTS.keys():
        phase_data = result["phase_scores"][phase_key]
        print(
            f"{phase_data['name']:<35} "
            f"{phase_data['score']:>6}/5 "
            f"{phase_data['weight']*100:>7.0f}% "
            f"{phase_data['weighted']:>10.3f}"
        )

    print("-" * 70)
    print(f"{'Weighted Sum:':<35} {result['weighted_sum']:>25.3f}")
    print(f"{'Overall Score:':<35} {result['overall_score']:>25.1f}/100")
    print("=" * 70)

    # Rating
    passing_marker = "✓ PASS" if result["passing"] else "✗ FAIL"
    print(f"\nRATING: {result['rating']} ({passing_marker})")
    print(f"\n{result['interpretation']}")

    # Critical warnings
    if result["critical_warnings"]:
        print("\n" + "!" * 70)
        print("CRITICAL WARNINGS:")
        print("!" * 70)
        for warning in result["critical_warnings"]:
            print(f"\n⚠  {warning['warning']}")
        print("\n" + "!" * 70)

    # Improvement recommendations
    if result["recommendations"]:
        print("\nIMPROVEMENT RECOMMENDATIONS:")
        print("-" * 70)
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"\n{i}. {rec['phase']} (current: {rec['current_score']}/5)")
            print(f"   To improve: {rec['improvement_target']}")

    print("\n" + "=" * 70)


def interactive_scoring() -> PhaseScores:
    """Collect scores interactively from user."""
    print("\n8D INVESTIGATION QUALITY SCORING")
    print("=" * 60)
    print("Rate each phase from 1 (Inadequate) to 5 (Excellent)")
    print()

    scores = {}

    for phase_key, phase_info in PHASES.items():
        print(f"\n{phase_info['name']}")
        print(f"  {phase_info['description']}")
        print("\n  Scoring Guide:")
        for score, desc in sorted(phase_info["criteria"].items(), reverse=True):
            print(f"    {score}: {desc[:70]}...")

        while True:
            try:
                value = int(input(f"\n  Enter score (1-5): "))
                if 1 <= value <= 5:
                    scores[phase_key] = value
                    break
                else:
                    print("  Please enter a number between 1 and 5.")
            except ValueError:
                print("  Please enter a valid number.")

    return PhaseScores(**scores)


def extract_scores_from_session(session_data: dict) -> PhaseScores:
    """Extract phase scores from a session JSON file."""
    # If scores are directly provided
    if "scores" in session_data and isinstance(session_data["scores"], dict):
        scores = session_data["scores"]
        if all(f"d{i}" in scores for i in range(9)):
            return PhaseScores(**{f"d{i}": scores[f"d{i}"] for i in range(9)})

    # If phase scores need to be derived from session content
    # This is a heuristic based on session completeness
    scores = {}

    # D0 - Check initial assessment fields
    d0_fields = ["domain", "severity", "urgency", "complexity"]
    d0_filled = sum(1 for f in d0_fields if session_data.get(f))
    scores["d0"] = min(5, max(1, d0_filled + 1))

    # D1 - Check team formation
    team = session_data.get("team_members", [])
    scores["d1"] = min(5, max(1, len(team) if isinstance(team, list) else 1))

    # D2 - Check problem definition
    d2_fields = [
        "problem_what_object", "problem_what_defect", "problem_where_geographic",
        "problem_when_calendar", "problem_how_detected", "problem_statement"
    ]
    d2_filled = sum(1 for f in d2_fields if session_data.get(f))
    scores["d2"] = min(5, max(1, d2_filled))

    # D3 - Check containment
    containment = session_data.get("containment_actions", [])
    scores["d3"] = min(5, max(1, len(containment) * 2 if isinstance(containment, list) else 1))

    # D4 - Check root cause analysis
    root_causes = session_data.get("root_causes", [])
    verified = session_data.get("root_cause_verified", False)
    scores["d4"] = 4 if root_causes and verified else (3 if root_causes else 1)

    # D5 - Check corrective actions
    actions = session_data.get("corrective_actions", [])
    scores["d5"] = min(5, max(1, len(actions) * 2 if isinstance(actions, list) else 1))

    # D6 - Check implementation
    impl = session_data.get("implementation_plan", [])
    scores["d6"] = min(5, max(1, len(impl) if isinstance(impl, list) else 1))

    # D7 - Check prevention
    systemic = session_data.get("systemic_actions", [])
    scores["d7"] = min(5, max(1, len(systemic) * 2 if isinstance(systemic, list) else 1))

    # D8 - Check closure
    closure_fields = ["verification_result", "lessons_learned", "closure_date"]
    d8_filled = sum(1 for f in closure_fields if session_data.get(f))
    scores["d8"] = min(5, max(1, d8_filled + 1))

    return PhaseScores(**scores)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate 8D Investigation Quality Score"
    )
    parser.add_argument(
        "--json",
        type=str,
        help='JSON string with scores: {"d0": 4, "d1": 3, ...}',
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to 8D session JSON file",
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
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode",
    )

    args = parser.parse_args()

    # Get scores from input source
    if args.json:
        try:
            data = json.loads(args.json)
            scores = PhaseScores(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        file_path = _validate_path(args.file, _ALLOWED_INPUT_EXTENSIONS, 'input')
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            scores = extract_scores_from_session(data)
        except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.interactive:
        scores = interactive_scoring()
    else:
        # Default to interactive
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
        output_path = _validate_path(args.output, _ALLOWED_OUTPUT_EXTENSIONS, 'output')
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to: {output_path}")
    elif args.quiet:
        print(json.dumps(result, indent=2))

    # Return exit code based on passing
    sys.exit(0 if result["passing"] else 1)


if __name__ == "__main__":
    main()
