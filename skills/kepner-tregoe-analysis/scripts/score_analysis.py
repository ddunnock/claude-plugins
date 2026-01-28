#!/usr/bin/env python3
"""
Kepner-Tregoe Analysis Quality Scorer

Evaluates the quality of a KT analysis against the rubric dimensions.
Supports both interactive scoring and JSON input.

Usage:
    python score_analysis.py                      # Interactive mode
    python score_analysis.py --input analysis.json # From JSON file
"""

import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DimensionScore:
    """Score for a single rubric dimension."""
    dimension: str
    weight: float
    rating: int  # 1-5
    percentage: float  # Rating converted to %
    weighted_score: float
    notes: str = ""


@dataclass
class QualityAssessment:
    """Complete quality assessment result."""
    analysis_type: str
    dimension_scores: List[DimensionScore]
    total_score: float
    rating: str
    recommendations: List[str]
    scored_at: str


# Rubric dimensions with weights
DIMENSIONS = {
    'PA': {
        'problem_specification': {
            'name': 'Problem Specification',
            'weight': 0.20,
            'description': 'Quality of deviation statement and IS/IS NOT matrix'
        },
        'distinction_quality': {
            'name': 'Distinction Quality', 
            'weight': 0.20,
            'description': 'Specificity and change-orientation of distinctions'
        },
        'cause_specification_fit': {
            'name': 'Cause-Specification Fit',
            'weight': 0.20,
            'description': 'How well cause explains all specification data'
        },
        'documentation': {
            'name': 'Documentation Quality',
            'weight': 0.10,
            'description': 'Completeness and traceability of analysis'
        }
    },
    'DA': {
        'decision_criteria_rigor': {
            'name': 'Decision Criteria Rigor',
            'weight': 0.25,
            'description': 'Quality of MUSTS/WANTS and scoring process'
        },
        'risk_analysis': {
            'name': 'Risk Analysis Depth',
            'weight': 0.20,
            'description': 'Thoroughness of adverse consequence assessment'
        },
        'documentation': {
            'name': 'Documentation Quality',
            'weight': 0.10,
            'description': 'Completeness and traceability of analysis'
        }
    },
    'PPA': {
        'risk_identification': {
            'name': 'Risk Identification',
            'weight': 0.25,
            'description': 'Comprehensiveness of potential problem identification'
        },
        'action_quality': {
            'name': 'Action Quality',
            'weight': 0.25,
            'description': 'Quality of preventive and contingent actions'
        },
        'documentation': {
            'name': 'Documentation Quality',
            'weight': 0.10,
            'description': 'Completeness and traceability of analysis'
        }
    },
    'FULL': {
        'problem_specification': {
            'name': 'Problem Specification',
            'weight': 0.20,
            'description': 'Quality of deviation statement and IS/IS NOT matrix'
        },
        'distinction_quality': {
            'name': 'Distinction Quality',
            'weight': 0.20,
            'description': 'Specificity and change-orientation of distinctions'
        },
        'cause_specification_fit': {
            'name': 'Cause-Specification Fit',
            'weight': 0.20,
            'description': 'How well cause explains all specification data'
        },
        'decision_criteria_rigor': {
            'name': 'Decision Criteria Rigor',
            'weight': 0.15,
            'description': 'Quality of MUSTS/WANTS and scoring process'
        },
        'risk_analysis': {
            'name': 'Risk Analysis Depth',
            'weight': 0.15,
            'description': 'Thoroughness of PPA or DA risk assessment'
        },
        'documentation': {
            'name': 'Documentation Quality',
            'weight': 0.10,
            'description': 'Completeness and traceability of analysis'
        }
    }
}

# Rating level descriptions
RATING_LEVELS = {
    5: ('Excellent', 100, 'Rigorous, complete, well-documented'),
    4: ('Good', 80, 'Sound with minor gaps'),
    3: ('Adequate', 60, 'Acceptable but improvements needed'),
    2: ('Needs Work', 40, 'Significant gaps present'),
    1: ('Inadequate', 20, 'Fundamental flaws, restart needed')
}

# Recommendations by dimension and rating
RECOMMENDATIONS = {
    'problem_specification': {
        1: "Restart problem specification. Define specific object and observable deviation.",
        2: "Improve specificity. Complete all 4 dimensions of IS/IS NOT matrix.",
        3: "Strengthen IS NOT column with meaningful comparisons. Remove assumed causes.",
        4: "Minor refinements. Verify data sources are documented."
    },
    'distinction_quality': {
        1: "Distinctions missing or meaningless. For each IS/IS NOT pair, identify what's different.",
        2: "Distinctions too vague. Focus on specific changes, differences, or unique factors.",
        3: "Good start. Ensure all distinctions are change-oriented and factual.",
        4: "Strong distinctions. Verify all are used in cause generation."
    },
    'cause_specification_fit': {
        1: "Causes not tested against specification. Systematically evaluate each cause.",
        2: "Cause testing incomplete. Ensure cause explains BOTH IS and IS NOT data.",
        3: "Most probable cause identified but verification incomplete.",
        4: "Good fit. Confirm verification plan is executed."
    },
    'decision_criteria_rigor': {
        1: "No clear criteria structure. Define MUSTS (mandatory) and WANTS (weighted).",
        2: "Criteria present but confused. MUSTS must be pass/fail. WANTS must be weighted.",
        3: "Structure good but weights may need review. Ensure scoring consistency.",
        4: "Minor refinements to weight rationale or scoring documentation."
    },
    'risk_analysis': {
        1: "No risk assessment performed. Identify adverse consequences for top alternatives.",
        2: "Risks identified but not systematically evaluated. Add probability and seriousness.",
        3: "Assessment present. Add preventive and contingent actions for HIGH/MEDIUM risks.",
        4: "Good coverage. Verify trigger conditions are specific and monitorable."
    },
    'documentation': {
        1: "Insufficient documentation. Cannot trace how conclusions were reached.",
        2: "Partial documentation. Add data sources, participants, assumptions.",
        3: "Adequate but gaps in traceability. Ensure logic flow is clear.",
        4: "Good documentation. Minor formatting or detail improvements."
    },
    'risk_identification': {
        1: "Potential problems not identified. Review all critical plan steps.",
        2: "Some risks identified. Ensure coverage of all critical steps and dependencies.",
        3: "Good coverage. Verify ratings (P/S) have documented rationale.",
        4: "Comprehensive identification. Minor gaps in edge cases."
    },
    'action_quality': {
        1: "Actions missing or too generic. Add specific, assigned actions with deadlines.",
        2: "Actions present but vague. Ensure preventive actions address likelihood.",
        3: "Good actions. Verify triggers are specific and responsibility is assigned.",
        4: "Strong actions. Minor refinements to monitoring approach."
    }
}


def get_rating_label(score: float) -> str:
    """Get rating label from total score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Acceptable"
    elif score >= 55:
        return "Needs Revision"
    else:
        return "Inadequate"


def get_recommendations(dimension_scores: List[DimensionScore]) -> List[str]:
    """Generate recommendations based on dimension scores."""
    recommendations = []
    
    for ds in dimension_scores:
        if ds.rating < 5:
            dim_key = ds.dimension.lower().replace(' ', '_').replace('-', '_')
            # Normalize dimension key
            key_map = {
                'problem_specification': 'problem_specification',
                'distinction_quality': 'distinction_quality',
                'cause_specification_fit': 'cause_specification_fit',
                'decision_criteria_rigor': 'decision_criteria_rigor',
                'risk_analysis_depth': 'risk_analysis',
                'risk_analysis': 'risk_analysis',
                'documentation_quality': 'documentation',
                'documentation': 'documentation',
                'risk_identification': 'risk_identification',
                'action_quality': 'action_quality'
            }
            normalized_key = key_map.get(dim_key, dim_key)
            
            if normalized_key in RECOMMENDATIONS and ds.rating in RECOMMENDATIONS[normalized_key]:
                rec = RECOMMENDATIONS[normalized_key][ds.rating]
                recommendations.append(f"**{ds.dimension}** (Rating: {ds.rating}/5): {rec}")
    
    return recommendations


def calculate_assessment(analysis_type: str, ratings: Dict[str, int], notes: Dict[str, str] = None) -> QualityAssessment:
    """Calculate quality assessment from ratings."""
    if notes is None:
        notes = {}
    
    dimensions = DIMENSIONS.get(analysis_type, DIMENSIONS['FULL'])
    dimension_scores = []
    
    for dim_key, dim_info in dimensions.items():
        rating = ratings.get(dim_key, 3)  # Default to 3 if not provided
        percentage = RATING_LEVELS[rating][1]
        weighted = percentage * dim_info['weight']
        
        dimension_scores.append(DimensionScore(
            dimension=dim_info['name'],
            weight=dim_info['weight'],
            rating=rating,
            percentage=percentage,
            weighted_score=weighted,
            notes=notes.get(dim_key, '')
        ))
    
    total_score = sum(ds.weighted_score for ds in dimension_scores)
    rating_label = get_rating_label(total_score)
    recommendations = get_recommendations(dimension_scores)
    
    return QualityAssessment(
        analysis_type=analysis_type,
        dimension_scores=dimension_scores,
        total_score=round(total_score, 1),
        rating=rating_label,
        recommendations=recommendations,
        scored_at=datetime.now().isoformat()
    )


def interactive_scoring():
    """Run interactive quality scoring."""
    print("\n" + "="*60)
    print("KEPNER-TREGOE QUALITY ASSESSMENT")
    print("="*60)
    
    # Select analysis type
    print("\nAnalysis Type:")
    print("  1. PA  - Problem Analysis")
    print("  2. DA  - Decision Analysis")
    print("  3. PPA - Potential Problem Analysis")
    print("  4. FULL - Complete KT Analysis")
    
    type_map = {'1': 'PA', '2': 'DA', '3': 'PPA', '4': 'FULL'}
    choice = input("\nSelect type (1-4): ").strip()
    analysis_type = type_map.get(choice, 'FULL')
    
    dimensions = DIMENSIONS[analysis_type]
    ratings = {}
    notes = {}
    
    print(f"\n--- Scoring {analysis_type} Analysis ---")
    print("Rate each dimension 1-5:")
    print("  5 = Excellent (100%)")
    print("  4 = Good (80%)")
    print("  3 = Adequate (60%)")
    print("  2 = Needs Work (40%)")
    print("  1 = Inadequate (20%)")
    
    for dim_key, dim_info in dimensions.items():
        print(f"\n{dim_info['name']} (Weight: {dim_info['weight']*100:.0f}%)")
        print(f"  {dim_info['description']}")
        
        while True:
            try:
                rating = int(input("  Rating (1-5): ").strip())
                if 1 <= rating <= 5:
                    ratings[dim_key] = rating
                    break
                print("  Rating must be 1-5")
            except ValueError:
                print("  Enter a number 1-5")
        
        note = input("  Notes (optional): ").strip()
        if note:
            notes[dim_key] = note
    
    # Calculate assessment
    assessment = calculate_assessment(analysis_type, ratings, notes)
    
    # Display results
    print("\n" + "="*60)
    print("ASSESSMENT RESULTS")
    print("="*60)
    
    print(f"\nAnalysis Type: {assessment.analysis_type}")
    print(f"\n{'Dimension':<30}{'Weight':<10}{'Rating':<10}{'Score':<10}")
    print("-" * 60)
    
    for ds in assessment.dimension_scores:
        print(f"{ds.dimension:<30}{ds.weight*100:.0f}%{' '*5}{ds.rating}/5{' '*5}{ds.weighted_score:.1f}")
    
    print("-" * 60)
    print(f"{'TOTAL SCORE':<30}{'':<10}{'':<10}{assessment.total_score:.1f}")
    
    # Rating interpretation
    rating_color = {
        'Excellent': '✓',
        'Acceptable': '✓',
        'Needs Revision': '!',
        'Inadequate': '✗'
    }
    print(f"\n{rating_color.get(assessment.rating, '')} OVERALL RATING: {assessment.rating}")
    
    if assessment.rating == 'Excellent':
        print("  Analysis meets high quality standards.")
    elif assessment.rating == 'Acceptable':
        print("  Analysis is sound with minor improvements needed.")
    elif assessment.rating == 'Needs Revision':
        print("  Significant gaps present. Revise before proceeding.")
    else:
        print("  Fundamental issues. Consider restarting analysis.")
    
    # Recommendations
    if assessment.recommendations:
        print("\n--- RECOMMENDATIONS ---")
        for rec in assessment.recommendations:
            print(f"\n{rec}")
    
    # Offer to save
    save = input("\nSave assessment to JSON? (y/n): ").strip().lower()
    if save in ['y', 'yes']:
        filename = input("Filename [kt_assessment.json]: ").strip() or "kt_assessment.json"
        output = asdict(assessment)
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Assessment saved to {filename}")
    
    return assessment


def score_from_json(input_file: str, output_file: Optional[str] = None):
    """Score analysis from JSON input."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    analysis_type = data.get('analysis_type', 'FULL')
    ratings = data.get('ratings', {})
    notes = data.get('notes', {})
    
    assessment = calculate_assessment(analysis_type, ratings, notes)
    
    output = asdict(assessment)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Assessment saved to {output_file}")
    else:
        print(json.dumps(output, indent=2))
    
    return assessment


def main():
    parser = argparse.ArgumentParser(description='Kepner-Tregoe Quality Assessment')
    parser.add_argument('--input', '-i', help='Input JSON file with ratings')
    parser.add_argument('--output', '-o', help='Output JSON file')
    
    args = parser.parse_args()
    
    if args.input:
        score_from_json(args.input, args.output)
    else:
        interactive_scoring()


if __name__ == '__main__':
    main()
