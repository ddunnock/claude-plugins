#!/usr/bin/env python3
"""
Fault Tree Analysis Calculator

Performs qualitative (minimal cut set) and quantitative (probability) analysis.
Supports AND, OR gates and basic event structures.

Usage:
    python calculate_fta.py [--qualitative|--quantitative] [input.json]
    
If no input file provided, runs in interactive mode.
"""

import os
import json
import sys
import argparse
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from itertools import combinations
from functools import reduce
import operator


@dataclass
class BasicEvent:
    """Represents a basic event (terminal node) in the fault tree."""
    id: str
    name: str
    probability: Optional[float] = None
    failure_rate: Optional[float] = None  # lambda (per hour)
    mission_time: Optional[float] = None  # hours
    data_source: str = "not specified"
    
    def get_probability(self) -> Optional[float]:
        """Calculate probability from failure rate if not directly specified."""
        if self.probability is not None:
            return self.probability
        if self.failure_rate is not None and self.mission_time is not None:
            # P = 1 - e^(-λt) ≈ λt for small λt
            lt = self.failure_rate * self.mission_time
            if lt < 0.1:
                return lt
            else:
                import math
                return 1 - math.exp(-lt)
        return None


@dataclass
class Gate:
    """Represents a logic gate (AND, OR) in the fault tree."""
    id: str
    name: str
    gate_type: str  # "AND", "OR"
    inputs: List[str] = field(default_factory=list)  # IDs of input events/gates


@dataclass
class FaultTree:
    """Complete fault tree structure."""
    top_event_id: str
    top_event_name: str
    gates: Dict[str, Gate] = field(default_factory=dict)
    basic_events: Dict[str, BasicEvent] = field(default_factory=dict)
    
    def get_node_type(self, node_id: str) -> str:
        """Determine if node is a gate or basic event."""
        if node_id in self.gates:
            return "gate"
        elif node_id in self.basic_events:
            return "basic"
        else:
            return "unknown"


def find_minimal_cut_sets(tree: FaultTree) -> List[Set[str]]:
    """
    Find all minimal cut sets using MOCUS algorithm.
    Returns list of sets, each containing basic event IDs.
    """
    
    def expand_node(node_id: str) -> List[Set[str]]:
        """Recursively expand a node into cut sets."""
        node_type = tree.get_node_type(node_id)
        
        if node_type == "basic":
            return [{node_id}]
        
        if node_type != "gate":
            # Unknown node - treat as undeveloped basic event
            return [{node_id}]
        
        gate = tree.gates[node_id]
        input_cut_sets = [expand_node(inp) for inp in gate.inputs]
        
        if gate.gate_type == "OR":
            # OR gate: union of all input cut sets
            result = []
            for cs_list in input_cut_sets:
                result.extend(cs_list)
            return result
        
        elif gate.gate_type == "AND":
            # AND gate: cross-product of input cut sets
            if not input_cut_sets:
                return []
            
            result = input_cut_sets[0]
            for next_cs_list in input_cut_sets[1:]:
                new_result = []
                for cs1 in result:
                    for cs2 in next_cs_list:
                        new_result.append(cs1 | cs2)
                result = new_result
            return result
        
        return []
    
    # Get all cut sets from top event
    all_cut_sets = expand_node(tree.top_event_id)
    
    # Remove non-minimal cut sets (supersets of other cut sets)
    minimal = []
    sorted_cs = sorted(all_cut_sets, key=len)
    
    for cs in sorted_cs:
        is_superset = False
        for existing in minimal:
            if existing <= cs:  # existing is subset of cs
                is_superset = True
                break
        if not is_superset:
            minimal.append(cs)
    
    return minimal


def calculate_cut_set_probability(cut_set: Set[str], tree: FaultTree) -> Optional[float]:
    """Calculate probability of a cut set (AND of all events)."""
    probabilities = []
    for event_id in cut_set:
        if event_id in tree.basic_events:
            p = tree.basic_events[event_id].get_probability()
            if p is None:
                return None
            probabilities.append(p)
        else:
            return None
    
    if not probabilities:
        return None
    
    return reduce(operator.mul, probabilities, 1.0)


def calculate_top_event_probability(cut_sets: List[Set[str]], tree: FaultTree) -> Optional[float]:
    """
    Calculate top event probability from minimal cut sets.
    Uses rare event approximation: P(top) ≈ sum of cut set probabilities
    """
    total = 0.0
    for cs in cut_sets:
        p = calculate_cut_set_probability(cs, tree)
        if p is None:
            return None
        total += p
    
    # For more accuracy with larger probabilities, use inclusion-exclusion
    # but rare event approximation is sufficient for most safety analyses
    return min(total, 1.0)


def calculate_importance_measures(
    cut_sets: List[Set[str]], 
    tree: FaultTree,
    top_prob: float
) -> Dict[str, Dict[str, float]]:
    """
    Calculate Fussell-Vesely importance for each basic event.
    FV = (sum of cut set probabilities containing event) / top event probability
    """
    importance = {}
    
    for event_id, event in tree.basic_events.items():
        # Find cut sets containing this event
        containing_cs = [cs for cs in cut_sets if event_id in cs]
        
        if not containing_cs:
            importance[event_id] = {"fussell_vesely": 0.0, "name": event.name}
            continue
        
        # Sum probabilities of containing cut sets
        cs_sum = 0.0
        for cs in containing_cs:
            p = calculate_cut_set_probability(cs, tree)
            if p is not None:
                cs_sum += p
        
        fv = cs_sum / top_prob if top_prob > 0 else 0.0
        importance[event_id] = {
            "fussell_vesely": fv,
            "name": event.name,
            "probability": event.get_probability()
        }
    
    return importance


def analyze_qualitative(tree: FaultTree) -> Dict[str, Any]:
    """Perform qualitative analysis - find cut sets, identify SPOFs."""
    cut_sets = find_minimal_cut_sets(tree)
    
    # Organize by order
    by_order = {}
    for cs in cut_sets:
        order = len(cs)
        if order not in by_order:
            by_order[order] = []
        by_order[order].append(cs)
    
    # Identify single points of failure (order 1)
    spofs = []
    if 1 in by_order:
        for cs in by_order[1]:
            event_id = list(cs)[0]
            if event_id in tree.basic_events:
                spofs.append({
                    "id": event_id,
                    "name": tree.basic_events[event_id].name
                })
    
    # Format cut sets with names
    formatted_cs = []
    for cs in cut_sets:
        events = []
        for eid in cs:
            name = tree.basic_events[eid].name if eid in tree.basic_events else eid
            events.append({"id": eid, "name": name})
        formatted_cs.append({
            "order": len(cs),
            "events": events
        })
    
    return {
        "total_cut_sets": len(cut_sets),
        "cut_sets_by_order": {k: len(v) for k, v in by_order.items()},
        "single_points_of_failure": spofs,
        "spof_count": len(spofs),
        "minimal_cut_sets": sorted(formatted_cs, key=lambda x: x["order"]),
        "analysis_type": "qualitative"
    }


def analyze_quantitative(tree: FaultTree) -> Dict[str, Any]:
    """Perform quantitative analysis - calculate probabilities and importance."""
    cut_sets = find_minimal_cut_sets(tree)
    
    # Calculate cut set probabilities
    cs_with_prob = []
    for cs in cut_sets:
        prob = calculate_cut_set_probability(cs, tree)
        events = []
        for eid in cs:
            name = tree.basic_events[eid].name if eid in tree.basic_events else eid
            events.append({"id": eid, "name": name})
        cs_with_prob.append({
            "order": len(cs),
            "events": events,
            "probability": prob
        })
    
    # Sort by probability (highest first)
    cs_with_prob.sort(key=lambda x: x["probability"] or 0, reverse=True)
    
    # Calculate top event probability
    top_prob = calculate_top_event_probability(cut_sets, tree)
    
    # Calculate importance measures
    importance = {}
    if top_prob is not None and top_prob > 0:
        importance = calculate_importance_measures(cut_sets, tree, top_prob)
    
    # Sort importance by FV (highest first)
    sorted_importance = sorted(
        importance.items(),
        key=lambda x: x[1].get("fussell_vesely", 0),
        reverse=True
    )
    
    return {
        "top_event_probability": top_prob,
        "total_cut_sets": len(cut_sets),
        "minimal_cut_sets": cs_with_prob,
        "importance_measures": dict(sorted_importance),
        "analysis_type": "quantitative"
    }


def load_from_json(filepath: str) -> FaultTree:
    """Load fault tree from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    tree = FaultTree(
        top_event_id=data["top_event"]["id"],
        top_event_name=data["top_event"]["name"]
    )
    
    # Load basic events
    for event_data in data.get("basic_events", []):
        event = BasicEvent(
            id=event_data["id"],
            name=event_data["name"],
            probability=event_data.get("probability"),
            failure_rate=event_data.get("failure_rate"),
            mission_time=event_data.get("mission_time"),
            data_source=event_data.get("data_source", "not specified")
        )
        tree.basic_events[event.id] = event
    
    # Load gates
    for gate_data in data.get("gates", []):
        gate = Gate(
            id=gate_data["id"],
            name=gate_data["name"],
            gate_type=gate_data["gate_type"],
            inputs=gate_data.get("inputs", [])
        )
        tree.gates[gate.id] = gate
    
    return tree


def interactive_mode():
    """Run interactive mode for building fault tree."""
    print("\n=== Fault Tree Analysis - Interactive Mode ===\n")
    
    # Get top event
    print("Step 1: Define the Top Event")
    top_name = input("Top event name: ").strip()
    top_id = "TOP"
    
    tree = FaultTree(top_event_id=top_id, top_event_name=top_name)
    
    # Build tree interactively
    print("\nStep 2: Build the fault tree")
    print("For each node, specify if it's a GATE (AND/OR) or BASIC event.")
    print("Commands: 'done' to finish, 'show' to display current tree\n")
    
    # Add top as a gate
    gate_type = input(f"Top event '{top_name}' - gate type (AND/OR): ").strip().upper()
    if gate_type not in ["AND", "OR"]:
        print("Invalid gate type, defaulting to OR")
        gate_type = "OR"
    
    tree.gates[top_id] = Gate(id=top_id, name=top_name, gate_type=gate_type)
    
    # Queue of gates to develop
    to_develop = [top_id]
    event_counter = 1
    
    while to_develop:
        current_gate_id = to_develop.pop(0)
        current_gate = tree.gates[current_gate_id]
        
        print(f"\nDeveloping gate: '{current_gate.name}' ({current_gate.gate_type})")
        print("Enter inputs (one per line, 'done' when finished):")
        
        while True:
            inp = input("  Input name (or 'done'): ").strip()
            if inp.lower() == 'done':
                break
            if not inp:
                continue
            
            inp_type = input(f"    Is '{inp}' a GATE or BASIC event? (g/b): ").strip().lower()
            
            event_id = f"E{event_counter}"
            event_counter += 1
            
            if inp_type == 'g':
                gate_type = input(f"    Gate type for '{inp}' (AND/OR): ").strip().upper()
                if gate_type not in ["AND", "OR"]:
                    gate_type = "OR"
                tree.gates[event_id] = Gate(id=event_id, name=inp, gate_type=gate_type)
                to_develop.append(event_id)
            else:
                prob_str = input(f"    Probability for '{inp}' (or Enter to skip): ").strip()
                prob = float(prob_str) if prob_str else None
                tree.basic_events[event_id] = BasicEvent(id=event_id, name=inp, probability=prob)
            
            current_gate.inputs.append(event_id)
    
    return tree



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
    parser = argparse.ArgumentParser(description="Fault Tree Analysis Calculator")
    parser.add_argument("input_file", nargs="?", help="JSON input file")
    parser.add_argument("--qualitative", "-q", action="store_true",
                       help="Perform qualitative analysis only")
    parser.add_argument("--quantitative", "-Q", action="store_true",
                       help="Perform quantitative analysis (requires probabilities)")
    parser.add_argument("--output", "-o", help="Output JSON file")
    
    args = parser.parse_args()

    if args.input_file:
        args.input_file = _validate_path(args.input_file, {'.json'}, "input file")
    if args.output:
        args.output = _validate_path(args.output, {'.json'}, "output file")
    
    # Load or build tree
    if args.input_file:
        tree = load_from_json(args.input_file)
    else:
        tree = interactive_mode()
    
    # Perform analysis
    print("\n=== Analysis Results ===\n")
    print(f"Top Event: {tree.top_event_name}")
    print(f"Basic Events: {len(tree.basic_events)}")
    print(f"Gates: {len(tree.gates)}")
    
    if args.quantitative:
        results = analyze_quantitative(tree)
    else:
        results = analyze_qualitative(tree)
    
    # Display results
    print(f"\nTotal Minimal Cut Sets: {results['total_cut_sets']}")
    
    if "cut_sets_by_order" in results:
        print("\nCut Sets by Order:")
        for order, count in sorted(results["cut_sets_by_order"].items()):
            print(f"  Order {order}: {count} cut sets")
    
    if results.get("spof_count", 0) > 0:
        print(f"\n⚠️  WARNING: {results['spof_count']} Single Point(s) of Failure found:")
        for spof in results["single_points_of_failure"]:
            print(f"  - {spof['name']} ({spof['id']})")
    
    if "top_event_probability" in results and results["top_event_probability"] is not None:
        print(f"\nTop Event Probability: {results['top_event_probability']:.2e}")
    
    if results.get("importance_measures"):
        print("\nImportance Measures (Fussell-Vesely):")
        for eid, data in list(results["importance_measures"].items())[:10]:
            fv = data.get("fussell_vesely", 0)
            print(f"  {data['name']}: {fv:.1%}")
    
    print("\nTop 5 Minimal Cut Sets:")
    for i, cs in enumerate(results["minimal_cut_sets"][:5], 1):
        event_names = [e["name"] for e in cs["events"]]
        prob_str = f" (P={cs['probability']:.2e})" if cs.get("probability") else ""
        print(f"  {i}. {{{', '.join(event_names)}}}{prob_str}")
    
    # Save output
    output_file = args.output or "fta_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    main()
