#!/usr/bin/env python3
"""
Pareto Analysis Calculator

Calculates Pareto data from input categories and values.
Outputs sorted data with percentages, cumulative percentages, and vital few identification.

Usage:
    python3 calculate_pareto.py --input data.json
    python3 calculate_pareto.py --interactive
    python3 calculate_pareto.py --input data.json --threshold 80 --output results.json

Input JSON format:
{
    "problem_statement": "Description of the problem",
    "measurement_type": "frequency|cost|time|weighted",
    "data": [
        {"category": "Category A", "value": 45},
        {"category": "Category B", "value": 30},
        ...
    ]
}
"""

import json
import argparse
import sys
from typing import List, Dict, Any, Tuple


def calculate_pareto(data: List[Dict[str, Any]], threshold: float = 80.0) -> Dict[str, Any]:
    """
    Calculate Pareto analysis from input data.
    
    Args:
        data: List of dicts with 'category' and 'value' keys
        threshold: Cumulative percentage threshold for vital few (default 80%)
    
    Returns:
        Dict with sorted data, calculations, and vital few identification
    """
    if not data:
        return {"error": "No data provided"}
    
    # Sort by value descending
    sorted_data = sorted(data, key=lambda x: x['value'], reverse=True)
    
    # Calculate total
    total = sum(item['value'] for item in sorted_data)
    
    if total == 0:
        return {"error": "Total value is zero"}
    
    # Calculate percentages and cumulative
    results = []
    cumulative = 0.0
    vital_few_boundary = None
    vital_few_categories = []
    
    for i, item in enumerate(sorted_data):
        percentage = (item['value'] / total) * 100
        cumulative += percentage
        
        result = {
            "rank": i + 1,
            "category": item['category'],
            "value": item['value'],
            "percentage": round(percentage, 2),
            "cumulative_percentage": round(cumulative, 2),
            "is_vital_few": cumulative <= threshold or (vital_few_boundary is None and cumulative > threshold)
        }
        results.append(result)
        
        # Mark vital few boundary
        if vital_few_boundary is None and cumulative >= threshold:
            vital_few_boundary = i + 1
        
        if result['is_vital_few']:
            vital_few_categories.append(item['category'])
    
    # Calculate Pareto effect strength
    if vital_few_boundary:
        vital_few_percentage = (vital_few_boundary / len(sorted_data)) * 100
        effect_strength = cumulative_at_vital_few = results[vital_few_boundary - 1]['cumulative_percentage']
    else:
        vital_few_percentage = 100
        effect_strength = 100
    
    # Determine if strong Pareto effect exists
    if vital_few_percentage <= 30 and effect_strength >= 70:
        pareto_effect = "strong"
        pareto_description = f"Strong Pareto effect: {vital_few_percentage:.0f}% of categories account for {effect_strength:.0f}% of impact"
    elif vital_few_percentage <= 50 and effect_strength >= 60:
        pareto_effect = "moderate"
        pareto_description = f"Moderate Pareto effect: {vital_few_percentage:.0f}% of categories account for {effect_strength:.0f}% of impact"
    else:
        pareto_effect = "weak"
        pareto_description = f"Weak/No Pareto effect: Impact is distributed across many categories"
    
    return {
        "total": total,
        "count": len(sorted_data),
        "threshold": threshold,
        "results": results,
        "vital_few": {
            "categories": vital_few_categories,
            "count": vital_few_boundary or len(sorted_data),
            "cumulative_percentage": results[vital_few_boundary - 1]['cumulative_percentage'] if vital_few_boundary else 100
        },
        "pareto_effect": pareto_effect,
        "pareto_description": pareto_description,
        "summary": {
            "vital_few_count": vital_few_boundary or len(sorted_data),
            "vital_few_percentage_of_categories": round(vital_few_percentage, 1),
            "vital_few_cumulative_impact": round(effect_strength, 1)
        }
    }


def format_table(results: List[Dict], include_vital_marker: bool = True) -> str:
    """Format results as ASCII table."""
    lines = []
    
    # Header
    if include_vital_marker:
        lines.append(f"{'Rank':<6}{'Category':<30}{'Value':>10}{'%':>10}{'Cumul %':>12}{'Vital Few':>12}")
        lines.append("-" * 80)
    else:
        lines.append(f"{'Rank':<6}{'Category':<30}{'Value':>10}{'%':>10}{'Cumul %':>12}")
        lines.append("-" * 68)
    
    # Data rows
    for r in results:
        marker = "<<<" if r.get('is_vital_few') else ""
        if include_vital_marker:
            lines.append(f"{r['rank']:<6}{r['category']:<30}{r['value']:>10}{r['percentage']:>9.1f}%{r['cumulative_percentage']:>11.1f}%{marker:>12}")
        else:
            lines.append(f"{r['rank']:<6}{r['category']:<30}{r['value']:>10}{r['percentage']:>9.1f}%{r['cumulative_percentage']:>11.1f}%")
    
    return "\n".join(lines)


def interactive_mode() -> Dict[str, Any]:
    """Interactive data entry mode."""
    print("\n=== Pareto Analysis Calculator ===\n")
    
    problem = input("Problem statement: ").strip()
    
    print("\nMeasurement type:")
    print("  1. Frequency (count)")
    print("  2. Cost ($)")
    print("  3. Time (hours)")
    print("  4. Weighted score")
    mtype_choice = input("Select (1-4): ").strip()
    measurement_types = {"1": "frequency", "2": "cost", "3": "time", "4": "weighted"}
    measurement_type = measurement_types.get(mtype_choice, "frequency")
    
    print(f"\nEnter categories and values ({measurement_type}).")
    print("Enter blank category name when done.\n")
    
    data = []
    while True:
        category = input("Category name: ").strip()
        if not category:
            break
        
        try:
            value = float(input(f"Value for '{category}': ").strip())
            data.append({"category": category, "value": value})
        except ValueError:
            print("Invalid number, skipping this category.")
    
    if not data:
        print("No data entered.")
        sys.exit(1)
    
    threshold = 80.0
    custom_threshold = input("\nCustom threshold % (default 80): ").strip()
    if custom_threshold:
        try:
            threshold = float(custom_threshold)
        except ValueError:
            pass
    
    return {
        "problem_statement": problem,
        "measurement_type": measurement_type,
        "threshold": threshold,
        "data": data
    }


def main():
    parser = argparse.ArgumentParser(description="Pareto Analysis Calculator")
    parser.add_argument("--input", "-i", help="Input JSON file")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--threshold", "-t", type=float, default=80.0, help="Cumulative % threshold (default: 80)")
    parser.add_argument("--interactive", action="store_true", help="Interactive data entry mode")
    parser.add_argument("--format", "-f", choices=["json", "table", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    # Get input data
    if args.interactive:
        input_data = interactive_mode()
        threshold = input_data.get("threshold", args.threshold)
        data = input_data["data"]
    elif args.input:
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        data = input_data.get("data", [])
        threshold = args.threshold
    else:
        print("Error: Provide --input file or use --interactive mode")
        sys.exit(1)
    
    # Calculate Pareto
    results = calculate_pareto(data, threshold)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        sys.exit(1)
    
    # Add input metadata to results
    results["input"] = {
        "problem_statement": input_data.get("problem_statement", ""),
        "measurement_type": input_data.get("measurement_type", "frequency")
    }
    
    # Output
    if args.format in ["table", "both"]:
        print("\n" + "=" * 80)
        print("PARETO ANALYSIS RESULTS")
        print("=" * 80)
        if results["input"]["problem_statement"]:
            print(f"\nProblem: {results['input']['problem_statement']}")
        print(f"Measurement: {results['input']['measurement_type']}")
        print(f"Total: {results['total']}")
        print(f"Categories: {results['count']}")
        print(f"Threshold: {results['threshold']}%")
        print("\n" + format_table(results["results"]))
        print("\n" + "-" * 80)
        print(f"\n{results['pareto_description']}")
        print(f"\nVital Few ({results['vital_few']['count']} categories, {results['vital_few']['cumulative_percentage']}% of impact):")
        for cat in results['vital_few']['categories']:
            print(f"  • {cat}")
        print()
    
    if args.format in ["json", "both"]:
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        elif args.format == "json":
            print(json.dumps(results, indent=2))
    
    return results


if __name__ == "__main__":
    main()
