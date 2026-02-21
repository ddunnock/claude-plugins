#!/usr/bin/env python3
"""
Fishbone Analysis Data Export

Exports fishbone analysis data to JSON format for integration with other tools.

Usage:
  python export_data.py --template > template.json
  python export_data.py --sample > sample_data.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def generate_template():
    """Generate empty template structure."""
    return {
        "analysis_id": "FB-YYYY-MMDD-NNN",
        "problem": "Clear, specific, measurable problem statement",
        "categories": [
            {
                "name": "Category Name (e.g., Man, Machine, Method)",
                "causes": [
                    {
                        "text": "Cause description",
                        "evidence": "Optional: Evidence or data supporting this cause",
                        "subcauses": [
                            {
                                "text": "Sub-cause description",
                                "subcauses": []
                            }
                        ]
                    }
                ]
            }
        ],
        "prioritized_causes": [
            {
                "rank": 1,
                "cause": "Top prioritized cause",
                "category": "Category it belongs to",
                "votes": 0,
                "verification_method": "How this cause will be verified",
                "owner": "Person/team responsible",
                "status": "Pending|In Progress|Complete",
                "due_date": "YYYY-MM-DD"
            }
        ],
        "scores": {
            "problem_clarity": 3,
            "category_coverage": 3,
            "cause_depth": 3,
            "cause_quality": 3,
            "prioritization": 3,
            "documentation": 3
        },
        "next_steps": [
            "Action item 1",
            "Action item 2"
        ],
        "metadata": {
            "title": "Analysis Title",
            "date": "YYYY-MM-DD",
            "team": "Team Name",
            "facilitator": "Facilitator Name",
            "participants": ["Participant 1", "Participant 2"],
            "framework": "6Ms|8Ps|4Ss|Custom",
            "related_analyses": ["Related analysis IDs"]
        },
        "notes": "Additional notes or context"
    }


def generate_sample():
    """Generate sample data with realistic values."""
    return {
        "analysis_id": f"FB-{datetime.now().strftime('%Y-%m%d')}-001",
        "problem": "Widget A dimensional variance exceeds ±0.05mm on 15% of units from CNC Machine #3, occurring since January 15th",
        "categories": [
            {
                "name": "Man",
                "causes": [
                    {
                        "text": "Operator inexperience",
                        "evidence": "New operator assigned Dec 28",
                        "subcauses": [
                            {"text": "Training incomplete (2 of 4 modules)", "subcauses": []},
                            {"text": "No mentorship assigned", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Measurement technique variation",
                        "evidence": "Observed during quality audit",
                        "subcauses": [
                            {"text": "No standardized measurement procedure", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Night shift fatigue",
                        "evidence": "Overtime increased 30% in January",
                        "subcauses": []
                    }
                ]
            },
            {
                "name": "Machine",
                "causes": [
                    {
                        "text": "CNC spindle wear",
                        "evidence": "Vibration readings elevated",
                        "subcauses": [
                            {"text": "2,500 hours since last rebuild (spec: 2,000)", "subcauses": []},
                            {"text": "Bearing clearance out of spec", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Coolant system degradation",
                        "evidence": "Filter overdue by 2 weeks",
                        "subcauses": [
                            {"text": "Coolant concentration low", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Fixture wear",
                        "evidence": "Visual inspection findings",
                        "subcauses": [
                            {"text": "Locating pins worn", "subcauses": []},
                            {"text": "Clamps not holding firmly", "subcauses": []}
                        ]
                    }
                ]
            },
            {
                "name": "Method",
                "causes": [
                    {
                        "text": "Tool offset not verified",
                        "evidence": "Checklist not completed on 3 shifts",
                        "subcauses": [
                            {"text": "Procedure skipped under time pressure", "subcauses": []},
                            {"text": "No automated verification", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Warm-up cycle inadequate",
                        "evidence": "Reduced from 15 to 5 min",
                        "subcauses": [
                            {"text": "Thermal expansion not stabilized", "subcauses": []}
                        ]
                    },
                    {
                        "text": "In-process inspection reduced",
                        "evidence": "Changed from 100% to sampling",
                        "subcauses": []
                    }
                ]
            },
            {
                "name": "Material",
                "causes": [
                    {
                        "text": "New material lot",
                        "evidence": "Lot arrived January 10",
                        "subcauses": [
                            {"text": "Hardness variation at edge of spec", "subcauses": []},
                            {"text": "Different supplier", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Bar stock diameter variation",
                        "evidence": "At upper limit of tolerance",
                        "subcauses": []
                    }
                ]
            },
            {
                "name": "Measurement",
                "causes": [
                    {
                        "text": "Calibration overdue",
                        "evidence": "Caliper last calibrated December 1",
                        "subcauses": [
                            {"text": "CMM drift not verified", "subcauses": []}
                        ]
                    },
                    {
                        "text": "SPC chart not reviewed",
                        "evidence": "Upward trend visible since Nov 15",
                        "subcauses": []
                    },
                    {
                        "text": "Sampling plan inadequate",
                        "evidence": "Missing early shifts",
                        "subcauses": []
                    }
                ]
            },
            {
                "name": "Mother Nature",
                "causes": [
                    {
                        "text": "Temperature fluctuation",
                        "evidence": "HVAC records show variance",
                        "subcauses": [
                            {"text": "HVAC issues in January cold snap", "subcauses": []},
                            {"text": "Door opened frequently for deliveries", "subcauses": []}
                        ]
                    },
                    {
                        "text": "Humidity variation",
                        "evidence": "New humidifier not working properly",
                        "subcauses": []
                    }
                ]
            }
        ],
        "prioritized_causes": [
            {
                "rank": 1,
                "cause": "CNC spindle wear",
                "category": "Machine",
                "votes": 8,
                "verification_method": "Vibration analysis and hour log review",
                "owner": "Maintenance - Bob Wilson",
                "status": "In Progress",
                "due_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "rank": 2,
                "cause": "Operator training incomplete",
                "category": "Man",
                "votes": 6,
                "verification_method": "Training records audit",
                "owner": "HR/Training - Alice Chen",
                "status": "Pending",
                "due_date": datetime.now().strftime("%Y-%m-%d")
            },
            {
                "rank": 3,
                "cause": "Tool offset verification skipped",
                "category": "Method",
                "votes": 5,
                "verification_method": "Process observation and checklist review",
                "owner": "Quality - John Smith",
                "status": "Pending",
                "due_date": datetime.now().strftime("%Y-%m-%d")
            }
        ],
        "scores": {
            "problem_clarity": 5,
            "category_coverage": 5,
            "cause_depth": 4,
            "cause_quality": 4,
            "prioritization": 4,
            "documentation": 5
        },
        "next_steps": [
            "Schedule spindle rebuild within 2 weeks",
            "Complete operator training modules (2 of 4 remaining)",
            "Reinstate mandatory tool offset verification",
            "Conduct 5 Whys on CNC spindle wear cause",
            "Review and update PM schedule for Machine #3"
        ],
        "metadata": {
            "title": "CNC Dimensional Variance Analysis",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "team": "Quality Engineering",
            "facilitator": "Jane Doe",
            "participants": [
                "John Smith (Quality)",
                "Jane Doe (Engineering)",
                "Bob Wilson (Maintenance)",
                "Alice Chen (Operations)"
            ],
            "framework": "6Ms",
            "related_analyses": []
        },
        "notes": "Analysis triggered by Q1 quality review identifying increased reject rate. Spindle rebuild appears to be primary driver based on timing correlation."
    }




def _validate_path(filepath: str, allowed_extensions: set, label: str) -> None:
    """Validate file path: reject traversal and restrict extensions."""
    if ".." in filepath:
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = Path(filepath).suffix.lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Export Fishbone Analysis Data"
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Output empty template structure"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Output sample data with realistic values"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()

    if args.output:
        _validate_path(args.output, {'.md', '.json'}, "output file")
    
    if args.template:
        data = generate_template()
    elif args.sample:
        data = generate_sample()
    else:
        print("Error: Must specify --template or --sample", file=sys.stderr)
        sys.exit(1)
    
    json_output = json.dumps(data, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"✓ Data exported to: {args.output}", file=sys.stderr)
    else:
        print(json_output)


if __name__ == "__main__":
    main()
