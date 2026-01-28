#!/usr/bin/env python3
"""
FMEA Quality Scoring Script

Evaluates FMEA quality based on six dimensions:
1. Structure Analysis (15%)
2. Function Definition (15%)
3. Failure Chain Logic (20%)
4. Control Identification (15%)
5. Rating Consistency (20%)
6. Action Effectiveness (15%)

Usage:
    python score_analysis.py --input fmea_data.json
    python score_analysis.py --interactive
"""

import json
import argparse
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension."""
    name: str
    score: int  # 1-5
    weight: float
    rationale: str
    issues: List[str]


@dataclass
class QualityAssessment:
    """Complete quality assessment for an FMEA."""
    dimensions: List[DimensionScore]
    overall_score: float
    rating: str
    pass_fail: str
    recommendations: List[str]


# Dimension definitions with weights
DIMENSIONS = {
    "structure_analysis": {
        "name": "Structure Analysis",
        "weight": 0.15,
        "description": "Completeness of system/process breakdown",
        "criteria": {
            5: "Complete breakdown, all interfaces, clear hierarchy, diagrams provided",
            4: "Most elements with minor gaps, key interfaces captured",
            3: "Basic structure, some interfaces missing",
            2: "Incomplete breakdown, many interfaces missing",
            1: "No meaningful structure analysis"
        }
    },
    "function_definition": {
        "name": "Function Definition",
        "weight": 0.15,
        "description": "Clarity, measurability of functions",
        "criteria": {
            5: "All functions in verb+noun, linked to measurable requirements",
            4: "Most functions properly formatted with requirements",
            3: "Basic function statements, partial specification linkage",
            2: "Vague statements, weak requirement linkage",
            1: "No clear function statements"
        }
    },
    "failure_chain_logic": {
        "name": "Failure Chain Logic",
        "weight": 0.20,
        "description": "Correct Mode→Effect→Cause relationships",
        "criteria": {
            5: "All modes relate to function, effects/causes at correct levels",
            4: "Most properly linked, minor confusion",
            3: "Basic modes identified, some logic gaps",
            2: "Incomplete identification, logic chain broken",
            1: "Missing/nonsensical modes, no logical chain"
        }
    },
    "control_identification": {
        "name": "Control Identification",
        "weight": 0.15,
        "description": "Completeness of prevention/detection controls",
        "criteria": {
            5: "Prevention/detection distinguished, all controls documented, gaps identified",
            4: "Mostly distinguished, most controls documented",
            3: "Some confusion, basic controls documented",
            2: "Prevention/detection confused, many controls missing",
            1: "No distinction, controls not documented"
        }
    },
    "rating_consistency": {
        "name": "Rating Consistency",
        "weight": 0.20,
        "description": "Appropriate, justified S/O/D ratings",
        "criteria": {
            5: "Consistently applied, rationale documented, similar items match",
            4: "Mostly consistent, most rationale documented",
            3: "Some inconsistencies, limited rationale",
            2: "Significant inconsistencies, no rationale",
            1: "Random/arbitrary ratings"
        }
    },
    "action_effectiveness": {
        "name": "Action Effectiveness",
        "weight": 0.15,
        "description": "Specific, assigned, measurable actions",
        "criteria": {
            5: "All High AP have specific actions with owners, dates, re-evaluation done",
            4: "Most High AP have actions with ownership",
            3: "Some High AP lack actions, actions sometimes generic",
            2: "Many High AP without actions, vague actions",
            1: "No actions despite High AP items"
        }
    }
}


def get_rating_label(score: float) -> str:
    """Convert numeric score to rating label."""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Acceptable"
    elif score >= 60:
        return "Needs Improvement"
    else:
        return "Unacceptable"


def get_pass_fail(score: float) -> str:
    """Determine pass/fail status."""
    return "PASS" if score >= 70 else "FAIL"


def calculate_overall_score(dimensions: List[DimensionScore]) -> float:
    """Calculate weighted overall score."""
    weighted_sum = sum(d.score * d.weight for d in dimensions)
    return round(weighted_sum * 20, 1)  # Convert to 0-100 scale


def automated_checks(fmea_data: Dict) -> Dict[str, List[str]]:
    """
    Perform automated quality checks on FMEA data.
    Returns issues found by dimension.
    """
    issues = {dim: [] for dim in DIMENSIONS.keys()}
    
    failure_modes = fmea_data.get("failure_modes", [])
    
    if not failure_modes:
        issues["structure_analysis"].append("No failure modes found in data")
        return issues
    
    # Check for structure analysis issues
    if not fmea_data.get("structure_tree"):
        issues["structure_analysis"].append("No structure tree/block diagram provided")
    
    # Check each failure mode
    functions_seen = set()
    rating_pairs = []  # For consistency checks
    
    for fm in failure_modes:
        fm_id = fm.get("id", "Unknown")
        
        # Function checks
        func = fm.get("function", "")
        if not func:
            issues["function_definition"].append(f"{fm_id}: Missing function")
        elif not any(word in func.lower() for word in ["to ", "provide", "maintain", "ensure", "prevent", "enable"]):
            issues["function_definition"].append(f"{fm_id}: Function may not be in verb+noun format")
        functions_seen.add(func)
        
        # Failure chain checks
        mode = fm.get("failure_mode", "")
        effect = fm.get("effect", "")
        cause = fm.get("cause", "")
        
        if not mode:
            issues["failure_chain_logic"].append(f"{fm_id}: Missing failure mode")
        elif len(mode) < 10:
            issues["failure_chain_logic"].append(f"{fm_id}: Failure mode may be too vague")
        
        if not effect:
            issues["failure_chain_logic"].append(f"{fm_id}: Missing effect")
        if not cause:
            issues["failure_chain_logic"].append(f"{fm_id}: Missing cause")
        
        # Check for mode/cause confusion (common mistake: cause in mode column)
        if mode and any(word in mode.lower() for word in ["due to", "because", "caused by"]):
            issues["failure_chain_logic"].append(f"{fm_id}: Failure mode may contain cause language")
        
        # Control checks
        prev_ctrl = fm.get("prevention_controls", "")
        det_ctrl = fm.get("detection_controls", "")
        
        if not prev_ctrl and not det_ctrl:
            issues["control_identification"].append(f"{fm_id}: No controls documented")
        elif not prev_ctrl:
            issues["control_identification"].append(f"{fm_id}: No prevention controls documented")
        elif not det_ctrl:
            issues["control_identification"].append(f"{fm_id}: No detection controls documented")
        
        # Rating checks
        severity = fm.get("severity")
        occurrence = fm.get("occurrence")
        detection = fm.get("detection")
        
        if not all([severity, occurrence, detection]):
            issues["rating_consistency"].append(f"{fm_id}: Missing S/O/D ratings")
        else:
            # Check for suspicious ratings
            if detection <= 2 and not det_ctrl:
                issues["rating_consistency"].append(f"{fm_id}: D={detection} but no detection controls documented")
            if occurrence <= 2 and not prev_ctrl:
                issues["rating_consistency"].append(f"{fm_id}: O={occurrence} but no prevention controls documented")
            
            rating_pairs.append((fm_id, severity, occurrence, detection, mode))
        
        # Action checks
        # Calculate AP to determine if action needed
        if severity and occurrence and detection:
            needs_action = severity >= 9 or (severity >= 7 and occurrence >= 5) or (occurrence >= 7 and detection >= 5)
            action = fm.get("recommended_action", "")
            
            if needs_action and not action:
                issues["action_effectiveness"].append(f"{fm_id}: High/Medium AP but no action documented")
            elif action:
                owner = fm.get("action_owner", "")
                date = fm.get("target_date", "")
                if not owner:
                    issues["action_effectiveness"].append(f"{fm_id}: Action documented but no owner assigned")
                if not date:
                    issues["action_effectiveness"].append(f"{fm_id}: Action documented but no target date")
    
    # Rating consistency across similar items
    # Group by similar failure modes and check for inconsistent severity
    from collections import defaultdict
    mode_severities = defaultdict(list)
    for fm_id, s, o, d, mode in rating_pairs:
        # Simplified grouping by keywords
        key_words = set(mode.lower().split())
        for other_id, other_s, _, _, other_mode in rating_pairs:
            other_words = set(other_mode.lower().split())
            if len(key_words & other_words) >= 2 and abs(s - other_s) > 2:
                issues["rating_consistency"].append(
                    f"{fm_id} and {other_id}: Similar modes with severity difference >2"
                )
                break
    
    return issues


def interactive_scoring() -> QualityAssessment:
    """Conduct interactive FMEA quality scoring."""
    print("\n=== FMEA Quality Assessment (Interactive Mode) ===\n")
    print("Rate each dimension from 1 (Inadequate) to 5 (Excellent)\n")
    
    dimensions = []
    
    for dim_key, dim_info in DIMENSIONS.items():
        print(f"\n--- {dim_info['name']} ---")
        print(f"Description: {dim_info['description']}")
        print(f"Weight: {dim_info['weight']*100:.0f}%")
        print("\nCriteria:")
        for score, criteria in dim_info['criteria'].items():
            print(f"  {score}: {criteria}")
        
        while True:
            try:
                score = int(input(f"\nScore for {dim_info['name']} (1-5): "))
                if 1 <= score <= 5:
                    break
                print("Please enter a value between 1 and 5")
            except ValueError:
                print("Please enter a valid integer")
        
        rationale = input("Rationale (optional): ")
        
        issues_input = input("Issues found (comma-separated, optional): ")
        issues = [i.strip() for i in issues_input.split(",")] if issues_input else []
        
        dimensions.append(DimensionScore(
            name=dim_info['name'],
            score=score,
            weight=dim_info['weight'],
            rationale=rationale,
            issues=issues
        ))
    
    return create_assessment(dimensions)


def create_assessment(dimensions: List[DimensionScore]) -> QualityAssessment:
    """Create quality assessment from dimension scores."""
    overall_score = calculate_overall_score(dimensions)
    rating = get_rating_label(overall_score)
    pass_fail = get_pass_fail(overall_score)
    
    # Generate recommendations based on scores
    recommendations = []
    for d in dimensions:
        if d.score <= 2:
            recommendations.append(f"CRITICAL: Improve {d.name} - current score indicates major deficiencies")
        elif d.score == 3:
            recommendations.append(f"IMPROVE: {d.name} meets minimum but should be strengthened")
    
    # Critical dimension checks
    chain_logic = next((d for d in dimensions if d.name == "Failure Chain Logic"), None)
    rating_cons = next((d for d in dimensions if d.name == "Rating Consistency"), None)
    
    if chain_logic and chain_logic.score <= 2:
        recommendations.insert(0, "⚠️ PRIORITY: Failure Chain Logic is critically deficient - FMEA may be unreliable")
    
    if rating_cons and rating_cons.score <= 2:
        recommendations.insert(0, "⚠️ PRIORITY: Rating Consistency is critically deficient - risk prioritization unreliable")
    
    if overall_score < 70:
        recommendations.insert(0, "❌ FMEA does not meet minimum quality threshold - rework required")
    
    return QualityAssessment(
        dimensions=dimensions,
        overall_score=overall_score,
        rating=rating,
        pass_fail=pass_fail,
        recommendations=recommendations
    )


def score_from_data(fmea_data: Dict) -> QualityAssessment:
    """
    Automatically score FMEA based on data quality checks.
    Returns assessment with automated scoring.
    """
    issues = automated_checks(fmea_data)
    
    # Convert issues to scores (rough heuristic)
    dimensions = []
    for dim_key, dim_info in DIMENSIONS.items():
        dim_issues = issues[dim_key]
        
        # Score based on number of issues (heuristic)
        num_items = len(fmea_data.get("failure_modes", []))
        if num_items == 0:
            score = 1
        else:
            issue_rate = len(dim_issues) / num_items if num_items > 0 else 0
            if issue_rate == 0:
                score = 5
            elif issue_rate < 0.1:
                score = 4
            elif issue_rate < 0.25:
                score = 3
            elif issue_rate < 0.5:
                score = 2
            else:
                score = 1
        
        dimensions.append(DimensionScore(
            name=dim_info['name'],
            score=score,
            weight=dim_info['weight'],
            rationale=f"Automated check: {len(dim_issues)} issues found",
            issues=dim_issues[:5]  # Limit to first 5 issues
        ))
    
    return create_assessment(dimensions)


def format_assessment_report(assessment: QualityAssessment) -> str:
    """Format assessment as readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("FMEA QUALITY ASSESSMENT REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Score: {assessment.overall_score}/100")
    lines.append(f"Rating: {assessment.rating}")
    lines.append(f"Status: {assessment.pass_fail}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("DIMENSION SCORES")
    lines.append("-" * 60)
    
    for d in assessment.dimensions:
        lines.append(f"\n{d.name} (Weight: {d.weight*100:.0f}%)")
        lines.append(f"  Score: {d.score}/5")
        if d.rationale:
            lines.append(f"  Rationale: {d.rationale}")
        if d.issues:
            lines.append("  Issues:")
            for issue in d.issues[:3]:  # Show up to 3 issues
                lines.append(f"    • {issue}")
            if len(d.issues) > 3:
                lines.append(f"    ... and {len(d.issues)-3} more issues")
    
    lines.append("")
    lines.append("-" * 60)
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 60)
    
    if assessment.recommendations:
        for rec in assessment.recommendations:
            lines.append(f"  • {rec}")
    else:
        lines.append("  No critical recommendations - FMEA meets quality standards")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="FMEA Quality Scorer")
    parser.add_argument("--input", "-i", help="Input JSON file with FMEA data")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--interactive", action="store_true", 
                        help="Run interactive scoring")
    parser.add_argument("--format", "-f", choices=["json", "text"], 
                        default="text", help="Output format")
    
    args = parser.parse_args()
    
    if args.interactive:
        assessment = interactive_scoring()
    elif args.input:
        try:
            with open(args.input, 'r') as f:
                fmea_data = json.load(f)
            assessment = score_from_data(fmea_data)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            sys.exit(1)
    else:
        print("Error: Either --input or --interactive required")
        sys.exit(1)
    
    # Format output
    if args.format == "json":
        output = json.dumps({
            "overall_score": assessment.overall_score,
            "rating": assessment.rating,
            "pass_fail": assessment.pass_fail,
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "weight": d.weight,
                    "rationale": d.rationale,
                    "issues": d.issues
                }
                for d in assessment.dimensions
            ],
            "recommendations": assessment.recommendations
        }, indent=2)
    else:
        output = format_assessment_report(assessment)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
