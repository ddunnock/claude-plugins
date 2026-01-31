#!/usr/bin/env python3
"""
Problem Statement Validator

Checks problem statements for common anti-patterns:
- Embedded causes
- Embedded solutions
- Vague language
- Missing dimensions

Usage:
    python validate_statement.py "Your problem statement here"
    python validate_statement.py --file definition.json
    python validate_statement.py --interactive
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from typing import List, Tuple


# Anti-pattern indicators for embedded causes
CAUSE_INDICATORS = [
    (r'\bbecause\b', "Contains 'because' - may embed cause"),
    (r'\bdue to\b', "Contains 'due to' - may embed cause"),
    (r'\bcaused by\b', "Contains 'caused by' - explicitly embeds cause"),
    (r'\bresulting from\b', "Contains 'resulting from' - may embed cause"),
    (r'\bsince\b(?!\s+\d)', "Contains 'since' - may embed cause (not temporal)"),
    (r'\bas a result of\b', "Contains 'as a result of' - embeds cause"),
    (r'\bfrom\b.*\b(failure|error|mistake|issue)\b', "Contains 'from [failure]' - may embed cause"),
    (r'\boperator\b.*\b(error|mistake|forgot)\b', "Contains operator error - person-blame"),
    (r'\buser\b.*\b(error|mistake|forgot)\b', "Contains user error - person-blame"),
    (r'\bhuman error\b', "Contains 'human error' - person-blame"),
    (r'\black of\b', "Contains 'lack of' - may embed cause"),
    (r'\bfailure to\b', "Contains 'failure to' - may embed cause"),
    (r'\binadequate\b', "Contains 'inadequate' - may embed cause"),
    (r'\binsufficient\b', "Contains 'insufficient' - may embed cause"),
]

# Anti-pattern indicators for embedded solutions
SOLUTION_INDICATORS = [
    (r'\bshould\b', "Contains 'should' - may embed solution"),
    (r'\bmust\b', "Contains 'must' - may embed solution"),
    (r'\bneed(?:s)? to\b', "Contains 'need(s) to' - may embed solution"),
    (r'\brequires?\b', "Contains 'require(s)' - may embed solution"),
    (r'\bfix\b', "Contains 'fix' - embeds solution"),
    (r'\bimprove\b', "Contains 'improve' - embeds solution"),
    (r'\bimplement\b', "Contains 'implement' - embeds solution"),
    (r'\binstall\b', "Contains 'install' - embeds solution"),
    (r'\breplace\b', "Contains 'replace' - embeds solution"),
    (r'\bupgrade\b', "Contains 'upgrade' - embeds solution"),
    (r'\btrain(?:ing)?\b', "Contains 'train/training' - embeds solution"),
    (r'\badd\b', "Contains 'add' - may embed solution"),
    (r'\bremove\b', "Contains 'remove' - may embed solution"),
    (r'\bchange\b', "Contains 'change' - may embed solution"),
]

# Vague language indicators
VAGUE_INDICATORS = [
    (r'\bissue(?:s)?\b', "Contains vague 'issue(s)' - be more specific"),
    (r'\bproblem(?:s)?\b', "Contains vague 'problem(s)' - be more specific"),
    (r'\bthing(?:s)?\b', "Contains vague 'thing(s)' - be more specific"),
    (r'\bsome\b', "Contains vague 'some' - quantify if possible"),
    (r'\bseveral\b', "Contains vague 'several' - quantify if possible"),
    (r'\bmany\b', "Contains vague 'many' - quantify if possible"),
    (r'\bfew\b', "Contains vague 'few' - quantify if possible"),
    (r'\boften\b', "Contains vague 'often' - specify frequency"),
    (r'\bsometimes\b', "Contains vague 'sometimes' - specify frequency"),
    (r'\busually\b', "Contains vague 'usually' - specify frequency"),
    (r'\boccasionally\b', "Contains vague 'occasionally' - specify frequency"),
    (r'\betc\.?\b', "Contains 'etc.' - list all relevant items"),
    (r'\band so on\b', "Contains 'and so on' - be complete"),
    (r'\band others?\b', "Contains 'and other(s)' - be complete"),
]

# Required dimensions (simplified check)
DIMENSION_PATTERNS = [
    ("what", r'\b(what|which|type|model|part|product|component)\b'),
    ("where", r'\b(where|location|site|line|station|area|region)\b'),
    ("when", r'\b(when|date|time|since|during|after|before|\d{4}|\d{1,2}/\d{1,2})\b'),
    ("magnitude", r'\b(\d+%?|\d+\s*(units?|pcs|pieces|parts|failures?|defects?))\b'),
]


@dataclass
class ValidationResult:
    """Container for validation results."""
    statement: str
    is_valid: bool
    cause_issues: List[str]
    solution_issues: List[str]
    vague_issues: List[str]
    missing_dimensions: List[str]
    score: float
    rating: str
    recommendations: List[str]


def validate_statement(statement: str) -> ValidationResult:
    """
    Validate a problem statement for anti-patterns.

    Returns ValidationResult with issues found and recommendations.
    """
    statement_lower = statement.lower()
    cause_issues = []
    solution_issues = []
    vague_issues = []

    # Check for embedded causes
    for pattern, message in CAUSE_INDICATORS:
        if re.search(pattern, statement_lower):
            cause_issues.append(message)

    # Check for embedded solutions
    for pattern, message in SOLUTION_INDICATORS:
        if re.search(pattern, statement_lower):
            solution_issues.append(message)

    # Check for vague language
    for pattern, message in VAGUE_INDICATORS:
        if re.search(pattern, statement_lower):
            vague_issues.append(message)

    # Check for missing dimensions
    missing_dimensions = []
    for dim_name, pattern in DIMENSION_PATTERNS:
        if not re.search(pattern, statement_lower):
            missing_dimensions.append(dim_name)

    # Calculate score
    # Start with 100, deduct for issues
    score = 100.0
    score -= len(cause_issues) * 15  # Causes are serious
    score -= len(solution_issues) * 15  # Solutions are serious
    score -= len(vague_issues) * 5  # Vagueness is less serious
    score -= len(missing_dimensions) * 10  # Missing dimensions matter
    score = max(0, score)

    # Determine rating
    if score >= 90:
        rating = "Excellent"
    elif score >= 80:
        rating = "Good"
    elif score >= 70:
        rating = "Acceptable"
    elif score >= 60:
        rating = "Marginal"
    else:
        rating = "Inadequate"

    # Generate recommendations
    recommendations = []
    if cause_issues:
        recommendations.append(
            "Remove embedded causes - describe WHAT is wrong, not WHY. "
            "Save cause analysis for root cause investigation."
        )
    if solution_issues:
        recommendations.append(
            "Remove embedded solutions - describe the gap/deviation, not HOW to fix it. "
            "Solutions come after root cause analysis."
        )
    if vague_issues:
        recommendations.append(
            "Replace vague terms with specific, measurable descriptions. "
            "Use numbers, dates, and precise terminology."
        )
    if missing_dimensions:
        recommendations.append(
            f"Consider adding: {', '.join(missing_dimensions).upper()}. "
            "A complete statement typically includes what, where, when, and magnitude."
        )

    # Overall validity
    is_valid = (
        len(cause_issues) == 0 and
        len(solution_issues) == 0 and
        score >= 70
    )

    return ValidationResult(
        statement=statement,
        is_valid=is_valid,
        cause_issues=cause_issues,
        solution_issues=solution_issues,
        vague_issues=vague_issues,
        missing_dimensions=missing_dimensions,
        score=score,
        rating=rating,
        recommendations=recommendations,
    )


def print_validation_report(result: ValidationResult) -> None:
    """Print formatted validation report."""
    print("\n" + "=" * 70)
    print("PROBLEM STATEMENT VALIDATION REPORT")
    print("=" * 70)

    print(f"\nStatement: {result.statement[:100]}{'...' if len(result.statement) > 100 else ''}")

    validity_marker = "✓ VALID" if result.is_valid else "✗ INVALID"
    print(f"\nResult: {validity_marker} | Score: {result.score:.0f}/100 | Rating: {result.rating}")

    if result.cause_issues:
        print("\n" + "-" * 70)
        print("EMBEDDED CAUSES DETECTED (Critical):")
        for issue in result.cause_issues:
            print(f"  ✗ {issue}")

    if result.solution_issues:
        print("\n" + "-" * 70)
        print("EMBEDDED SOLUTIONS DETECTED (Critical):")
        for issue in result.solution_issues:
            print(f"  ✗ {issue}")

    if result.vague_issues:
        print("\n" + "-" * 70)
        print("VAGUE LANGUAGE DETECTED (Warning):")
        for issue in result.vague_issues:
            print(f"  ⚠ {issue}")

    if result.missing_dimensions:
        print("\n" + "-" * 70)
        print("POSSIBLY MISSING DIMENSIONS:")
        print(f"  Consider adding: {', '.join(result.missing_dimensions).upper()}")

    if result.recommendations:
        print("\n" + "-" * 70)
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"\n  {i}. {rec}")

    print("\n" + "=" * 70)

    if result.is_valid:
        print("\n✓ Statement is suitable for root cause investigation.")
    else:
        print("\n✗ Statement needs revision before proceeding with root cause analysis.")

    print()


def interactive_mode():
    """Run in interactive mode."""
    print("\nPROBLEM STATEMENT VALIDATOR")
    print("=" * 50)
    print("Enter problem statements to validate (type 'quit' to exit)\n")

    while True:
        statement = input("\nProblem statement: ").strip()
        if statement.lower() in ('quit', 'exit', 'q'):
            break
        if not statement:
            print("Please enter a statement to validate.")
            continue

        result = validate_statement(statement)
        print_validation_report(result)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Problem Statement for Anti-patterns"
    )
    parser.add_argument(
        "statement",
        nargs="?",
        type=str,
        help="Problem statement to validate",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="JSON file containing problem_statement field",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for JSON results",
    )
    parser.add_argument(
        "--quiet",
        "-q",
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

    # Get statement from input source
    if args.interactive:
        interactive_mode()
        return

    statement = None
    if args.statement:
        statement = args.statement
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
            statement = data.get('problem_statement', '')
            if not statement:
                print("Error: No problem_statement found in JSON file", file=sys.stderr)
                sys.exit(1)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Please provide a statement, --file, or use --interactive", file=sys.stderr)
        sys.exit(1)

    # Validate
    result = validate_statement(statement)

    # Output
    if not args.quiet:
        print_validation_report(result)

    if args.output:
        output_data = {
            "statement": result.statement,
            "is_valid": result.is_valid,
            "score": result.score,
            "rating": result.rating,
            "cause_issues": result.cause_issues,
            "solution_issues": result.solution_issues,
            "vague_issues": result.vague_issues,
            "missing_dimensions": result.missing_dimensions,
            "recommendations": result.recommendations,
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}")
    elif args.quiet:
        output_data = {
            "is_valid": result.is_valid,
            "score": result.score,
            "rating": result.rating,
            "issues_count": len(result.cause_issues) + len(result.solution_issues) + len(result.vague_issues),
        }
        print(json.dumps(output_data, indent=2))

    # Exit code based on validity
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
