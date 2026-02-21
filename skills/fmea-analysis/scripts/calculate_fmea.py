#!/usr/bin/env python3
"""
FMEA Calculation Script

Calculates Risk Priority Numbers (RPN) and Action Priority (AP) for FMEA data.
Provides risk summaries and prioritization analysis.

Usage:
    python calculate_fmea.py --input fmea_data.json --mode [rpn|ap|summary|all]
    python calculate_fmea.py --interactive
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ActionPriority(Enum):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


@dataclass
class FailureMode:
    """Represents a single failure mode in the FMEA."""
    id: str
    function: str
    failure_mode: str
    effect: str
    cause: str
    severity: int
    occurrence: int
    detection: int
    prevention_controls: str = ""
    detection_controls: str = ""
    recommended_action: str = ""
    action_owner: str = ""
    target_date: str = ""
    action_taken: str = ""
    revised_severity: Optional[int] = None
    revised_occurrence: Optional[int] = None
    revised_detection: Optional[int] = None


def validate_rating(value: int, name: str) -> bool:
    """Validate that a rating is within 1-10 range."""
    if not isinstance(value, int) or value < 1 or value > 10:
        print(f"Warning: {name} rating {value} is outside valid range 1-10")
        return False
    return True


def calculate_rpn(severity: int, occurrence: int, detection: int) -> int:
    """Calculate Risk Priority Number (S × O × D)."""
    return severity * occurrence * detection


def get_ap_rating_group(rating: int) -> str:
    """Convert a 1-10 rating to AP rating group."""
    if rating >= 9:
        return "9-10"
    elif rating >= 7:
        return "7-8"
    elif rating >= 5:
        return "5-6"
    elif rating >= 3:
        return "3-4"
    else:
        return "1-2"


def determine_action_priority(severity: int, occurrence: int, detection: int, 
                               fmea_type: str = "DFMEA") -> ActionPriority:
    """
    Determine Action Priority (AP) based on AIAG-VDA methodology.
    
    Severity is prioritized first, then Occurrence, then Detection.
    """
    # Safety-critical items (S >= 9) are always HIGH priority unless O and D are very low
    if severity >= 9:
        if occurrence >= 5 or detection >= 5:
            return ActionPriority.HIGH
        elif occurrence >= 3 or detection >= 7:
            return ActionPriority.HIGH
        elif occurrence <= 2 and detection <= 4:
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.HIGH
    
    # High severity (7-8)
    elif severity >= 7:
        if occurrence >= 7:
            return ActionPriority.HIGH
        elif occurrence >= 5 and detection >= 5:
            return ActionPriority.HIGH
        elif occurrence >= 5:
            return ActionPriority.MEDIUM
        elif occurrence >= 3 and detection >= 7:
            return ActionPriority.HIGH
        elif occurrence >= 3 and detection >= 5:
            return ActionPriority.MEDIUM
        elif detection >= 9:
            return ActionPriority.HIGH
        elif detection >= 7:
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.LOW
    
    # Moderate severity (5-6)
    elif severity >= 5:
        if occurrence >= 9:
            return ActionPriority.HIGH if detection >= 3 else ActionPriority.MEDIUM
        elif occurrence >= 7:
            return ActionPriority.HIGH if detection >= 5 else ActionPriority.MEDIUM
        elif occurrence >= 5:
            return ActionPriority.HIGH if detection >= 7 else ActionPriority.MEDIUM
        elif occurrence >= 3:
            return ActionPriority.HIGH if detection >= 9 else ActionPriority.MEDIUM if detection >= 5 else ActionPriority.LOW
        else:
            return ActionPriority.MEDIUM if detection >= 9 else ActionPriority.LOW
    
    # Low severity (3-4)
    elif severity >= 3:
        if occurrence >= 9:
            return ActionPriority.HIGH if detection >= 7 else ActionPriority.MEDIUM
        elif occurrence >= 7:
            return ActionPriority.HIGH if detection >= 9 else ActionPriority.MEDIUM if detection >= 5 else ActionPriority.LOW
        elif occurrence >= 5:
            return ActionPriority.HIGH if detection >= 10 else ActionPriority.MEDIUM if detection >= 7 else ActionPriority.LOW
        elif occurrence >= 3:
            return ActionPriority.MEDIUM if detection >= 9 else ActionPriority.LOW
        else:
            return ActionPriority.MEDIUM if detection >= 10 else ActionPriority.LOW
    
    # Very low severity (1-2)
    else:
        return ActionPriority.LOW


def analyze_failure_mode(fm: FailureMode, fmea_type: str = "DFMEA") -> Dict:
    """Analyze a single failure mode and return risk metrics."""
    # Validate ratings
    validate_rating(fm.severity, "Severity")
    validate_rating(fm.occurrence, "Occurrence")
    validate_rating(fm.detection, "Detection")
    
    rpn = calculate_rpn(fm.severity, fm.occurrence, fm.detection)
    ap = determine_action_priority(fm.severity, fm.occurrence, fm.detection, fmea_type)
    
    # Calculate revised metrics if available
    revised_rpn = None
    revised_ap = None
    rpn_reduction = None
    
    if all([fm.revised_severity, fm.revised_occurrence, fm.revised_detection]):
        revised_rpn = calculate_rpn(fm.revised_severity, fm.revised_occurrence, fm.revised_detection)
        revised_ap = determine_action_priority(fm.revised_severity, fm.revised_occurrence, 
                                                fm.revised_detection, fmea_type)
        rpn_reduction = rpn - revised_rpn
    
    return {
        "id": fm.id,
        "failure_mode": fm.failure_mode,
        "severity": fm.severity,
        "occurrence": fm.occurrence,
        "detection": fm.detection,
        "rpn": rpn,
        "action_priority": ap.value,
        "ap_description": get_ap_description(ap),
        "is_safety_critical": fm.severity >= 9,
        "revised_rpn": revised_rpn,
        "revised_ap": revised_ap.value if revised_ap else None,
        "rpn_reduction": rpn_reduction,
        "requires_action": ap in [ActionPriority.HIGH, ActionPriority.MEDIUM] or fm.severity >= 9,
        "has_action": bool(fm.recommended_action),
    }


def get_ap_description(ap: ActionPriority) -> str:
    """Get description of action priority level."""
    descriptions = {
        ActionPriority.HIGH: "MUST identify action to improve controls",
        ActionPriority.MEDIUM: "SHOULD identify action or justify current controls",
        ActionPriority.LOW: "COULD improve controls at discretion",
    }
    return descriptions[ap]


def generate_risk_summary(failure_modes: List[FailureMode], fmea_type: str = "DFMEA") -> Dict:
    """Generate overall risk summary for the FMEA."""
    analyses = [analyze_failure_mode(fm, fmea_type) for fm in failure_modes]
    
    # Count by AP
    ap_counts = {"H": 0, "M": 0, "L": 0}
    for a in analyses:
        ap_counts[a["action_priority"]] += 1
    
    # RPN statistics
    rpns = [a["rpn"] for a in analyses]
    
    # Identify items needing attention
    needs_action = [a for a in analyses if a["requires_action"]]
    safety_critical = [a for a in analyses if a["is_safety_critical"]]
    high_rpn = [a for a in analyses if a["rpn"] >= 200]
    
    # Action coverage
    items_with_actions = [a for a in needs_action if a["has_action"]]
    action_coverage = len(items_with_actions) / len(needs_action) * 100 if needs_action else 100
    
    return {
        "total_failure_modes": len(failure_modes),
        "action_priority_distribution": ap_counts,
        "rpn_statistics": {
            "minimum": min(rpns) if rpns else 0,
            "maximum": max(rpns) if rpns else 0,
            "average": sum(rpns) / len(rpns) if rpns else 0,
        },
        "safety_critical_count": len(safety_critical),
        "high_rpn_count": len(high_rpn),
        "items_requiring_action": len(needs_action),
        "items_with_actions": len(items_with_actions),
        "action_coverage_percent": round(action_coverage, 1),
        "top_risks": sorted(analyses, key=lambda x: (-x["severity"], -x["rpn"]))[:10],
    }


def load_fmea_data(filepath: str) -> Tuple[List[FailureMode], str]:
    """Load FMEA data from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    fmea_type = data.get("fmea_type", "DFMEA")
    failure_modes = []
    
    for item in data.get("failure_modes", []):
        fm = FailureMode(
            id=item.get("id", ""),
            function=item.get("function", ""),
            failure_mode=item.get("failure_mode", ""),
            effect=item.get("effect", ""),
            cause=item.get("cause", ""),
            severity=item.get("severity", 1),
            occurrence=item.get("occurrence", 1),
            detection=item.get("detection", 1),
            prevention_controls=item.get("prevention_controls", ""),
            detection_controls=item.get("detection_controls", ""),
            recommended_action=item.get("recommended_action", ""),
            action_owner=item.get("action_owner", ""),
            target_date=item.get("target_date", ""),
            action_taken=item.get("action_taken", ""),
            revised_severity=item.get("revised_severity"),
            revised_occurrence=item.get("revised_occurrence"),
            revised_detection=item.get("revised_detection"),
        )
        failure_modes.append(fm)
    
    return failure_modes, fmea_type


def interactive_mode():
    """Run in interactive mode for single calculations."""
    print("\n=== FMEA Risk Calculator (Interactive Mode) ===\n")
    
    while True:
        print("\nEnter ratings (or 'quit' to exit):")
        
        try:
            s_input = input("Severity (1-10): ")
            if s_input.lower() == 'quit':
                break
            severity = int(s_input)
            
            occurrence = int(input("Occurrence (1-10): "))
            detection = int(input("Detection (1-10): "))
            
            # Validate
            if not all([1 <= r <= 10 for r in [severity, occurrence, detection]]):
                print("Error: All ratings must be between 1 and 10")
                continue
            
            # Calculate
            rpn = calculate_rpn(severity, occurrence, detection)
            ap = determine_action_priority(severity, occurrence, detection)
            
            print(f"\n--- Results ---")
            print(f"RPN: {rpn}")
            print(f"Action Priority: {ap.value} ({get_ap_description(ap)})")
            print(f"Safety Critical: {'Yes' if severity >= 9 else 'No'}")
            
            if ap == ActionPriority.HIGH or severity >= 9:
                print("\n⚠️  ACTION REQUIRED: This item requires risk mitigation action.")
            elif ap == ActionPriority.MEDIUM:
                print("\n⚡ ACTION RECOMMENDED: Consider risk mitigation or justify current controls.")
            
        except ValueError:
            print("Error: Please enter valid integer values")
        except KeyboardInterrupt:
            break
    
    print("\nExiting calculator.")


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
    parser = argparse.ArgumentParser(description="FMEA Risk Calculator")
    parser.add_argument("--input", "-i", help="Input JSON file with FMEA data")
    parser.add_argument("--output", "-o", help="Output JSON file for results")
    parser.add_argument("--mode", "-m", choices=["rpn", "ap", "summary", "all"],
                        default="all", help="Calculation mode")
    parser.add_argument("--interactive", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("--type", "-t", choices=["DFMEA", "PFMEA"],
                        default="DFMEA", help="FMEA type")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.input:
        print("Error: --input file required (or use --interactive mode)")
        sys.exit(1)

    args.input = _validate_path(args.input, {".json"}, "input file")
    if args.output:
        args.output = _validate_path(args.output, {".json"}, "output file")

    # Load data
    try:
        failure_modes, fmea_type = load_fmea_data(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}")
        sys.exit(1)
    
    # Override FMEA type if specified
    if args.type:
        fmea_type = args.type
    
    # Perform analysis
    results = {
        "fmea_type": fmea_type,
        "total_items": len(failure_modes),
    }
    
    if args.mode in ["rpn", "all"]:
        results["item_analysis"] = [analyze_failure_mode(fm, fmea_type) for fm in failure_modes]
    
    if args.mode in ["summary", "all"]:
        results["summary"] = generate_risk_summary(failure_modes, fmea_type)
    
    # Output
    output_json = json.dumps(results, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
