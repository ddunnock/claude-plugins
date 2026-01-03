#!/usr/bin/env python3
"""
5 Whys Analysis Tool for Trade Study Analysis

Interactive root cause analysis using the 5 Whys methodology.
Enforces source documentation for each answer.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class FiveWhysAnalysis:
    """Interactive 5 Whys root cause analysis."""
    
    MAX_LEVELS = 7
    MIN_LEVELS = 3
    TYPICAL_LEVELS = 5
    
    STOP_CONDITIONS = [
        'actionable_level_reached',
        'no_meaningful_answer',
        'outside_control_boundary',
        'user_indicates_root_cause'
    ]
    
    def __init__(self):
        self.analysis = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'status': 'in_progress'
            },
            'initial_problem': None,
            'chain': [],
            'root_cause': None,
            'sources': [],
            'assumptions': []
        }
    
    def set_initial_problem(self, problem: str, source: Optional[str] = None):
        """Set the initial observable problem."""
        self.analysis['initial_problem'] = {
            'statement': problem,
            'source': source or 'User-provided',
            'timestamp': datetime.now().isoformat()
        }
    
    def add_why_level(
        self,
        level: int,
        question: str,
        answer: str,
        source: Optional[str] = None,
        source_id: Optional[str] = None,
        is_assumption: bool = False,
        assumption_basis: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a level to the 5 Whys chain.
        
        Args:
            level: Level number (1-7)
            question: The "why" question asked
            answer: User's answer
            source: Source document for the answer
            source_id: Reference to source registry
            is_assumption: Whether this answer is an assumption
            assumption_basis: Basis for assumption if applicable
            
        Returns:
            The created level entry
        """
        if level < 1 or level > self.MAX_LEVELS:
            raise ValueError(f"Level must be between 1 and {self.MAX_LEVELS}")
        
        entry = {
            'level': level,
            'question': question,
            'answer': answer,
            'source': source or 'User-provided (no document)',
            'source_id': source_id,
            'is_assumption': is_assumption,
            'assumption_basis': assumption_basis,
            'timestamp': datetime.now().isoformat()
        }
        
        self.analysis['chain'].append(entry)
        
        # Track sources and assumptions
        if source and source not in self.analysis['sources']:
            self.analysis['sources'].append(source)
        
        if is_assumption:
            self.analysis['assumptions'].append({
                'level': level,
                'assumption': answer,
                'basis': assumption_basis
            })
        
        return entry
    
    def set_root_cause(
        self,
        root_cause: str,
        level: int,
        confidence: str = 'medium',
        rationale: str = ''
    ):
        """
        Set the identified root cause.
        
        Args:
            root_cause: The root cause statement
            level: The level at which root cause was identified
            confidence: High/medium/low confidence
            rationale: Why this is considered the root cause
        """
        self.analysis['root_cause'] = {
            'statement': root_cause,
            'identified_at_level': level,
            'confidence': confidence,
            'rationale': rationale,
            'timestamp': datetime.now().isoformat()
        }
        self.analysis['metadata']['status'] = 'complete'
    
    def is_at_root_cause(self, answer: str) -> Dict[str, Any]:
        """
        Assess if the current answer represents a root cause.
        
        Args:
            answer: The current answer to evaluate
            
        Returns:
            Assessment with indicators
        """
        assessment = {
            'likely_root_cause': False,
            'indicators': [],
            'concerns': []
        }
        
        answer_lower = answer.lower()
        
        # Root cause indicators
        root_indicators = [
            ('because', 'Contains causal language'),
            ('lack of', 'Identifies deficiency'),
            ('no', 'Identifies absence'),
            ('insufficient', 'Identifies gap'),
            ('design', 'Points to design issue'),
            ('architecture', 'Points to architecture issue'),
            ('process', 'Points to process issue'),
            ('policy', 'Points to policy issue'),
            ('requirement', 'Points to requirement issue')
        ]
        
        for indicator, description in root_indicators:
            if indicator in answer_lower:
                assessment['indicators'].append(description)
        
        # Symptom indicators (suggests not at root cause yet)
        symptom_indicators = [
            ('fails', 'Describes failure (symptom)'),
            ('slow', 'Describes performance issue (symptom)'),
            ('error', 'Describes error occurrence (symptom)'),
            ('breaks', 'Describes breakage (symptom)'),
            ('does not work', 'Describes malfunction (symptom)')
        ]
        
        for indicator, description in symptom_indicators:
            if indicator in answer_lower:
                assessment['concerns'].append(description)
        
        # Assess likelihood
        if len(assessment['indicators']) >= 2 and len(assessment['concerns']) == 0:
            assessment['likely_root_cause'] = True
        
        return assessment
    
    def get_next_question(self, previous_answer: str) -> str:
        """Generate the next "why" question based on previous answer."""
        # Clean up answer for question formation
        answer = previous_answer.strip().rstrip('.')
        
        return f'Why does "{answer}" occur?'
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        return {
            'initial_problem': self.analysis['initial_problem']['statement'] if self.analysis['initial_problem'] else None,
            'levels_explored': len(self.analysis['chain']),
            'root_cause': self.analysis['root_cause']['statement'] if self.analysis['root_cause'] else None,
            'root_cause_confidence': self.analysis['root_cause']['confidence'] if self.analysis['root_cause'] else None,
            'sources_used': len(self.analysis['sources']),
            'assumptions_made': len(self.analysis['assumptions']),
            'status': self.analysis['metadata']['status']
        }
    
    def get_causal_chain(self) -> List[str]:
        """Get the causal chain as a list of statements."""
        chain = []
        if self.analysis['initial_problem']:
            chain.append(self.analysis['initial_problem']['statement'])
        
        for entry in self.analysis['chain']:
            chain.append(entry['answer'])
        
        return chain
    
    def export(self, path: str):
        """Export analysis to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.analysis, f, indent=2)
    
    def print_chain(self):
        """Print formatted causal chain."""
        print("=" * 70)
        print("5 WHYS CAUSAL CHAIN")
        print("=" * 70)
        
        if self.analysis['initial_problem']:
            print(f"\nOBSERVABLE PROBLEM:")
            print(f"  {self.analysis['initial_problem']['statement']}")
            print(f"  Source: {self.analysis['initial_problem']['source']}")
        
        print("\n" + "-" * 70)
        
        for entry in self.analysis['chain']:
            print(f"\nWHY #{entry['level']}:")
            print(f"  Q: {entry['question']}")
            print(f"  A: {entry['answer']}")
            print(f"  Source: {entry['source']}")
            if entry['is_assumption']:
                print(f"  ⚠️  ASSUMPTION: {entry['assumption_basis']}")
        
        print("\n" + "-" * 70)
        
        if self.analysis['root_cause']:
            rc = self.analysis['root_cause']
            print(f"\nROOT CAUSE IDENTIFIED (Level {rc['identified_at_level']}):")
            print(f"  {rc['statement']}")
            print(f"  Confidence: {rc['confidence'].upper()}")
            print(f"  Rationale: {rc['rationale']}")
        
        print("\n" + "-" * 70)
        print(f"Sources used: {len(self.analysis['sources'])}")
        print(f"Assumptions made: {len(self.analysis['assumptions'])}")
        print("=" * 70)
    
    def run_interactive(self):
        """Run interactive 5 Whys session."""
        print("=" * 70)
        print("5 WHYS ROOT CAUSE ANALYSIS")
        print("=" * 70)
        print("\nThis analysis will help identify the root cause of a problem.")
        print("At each level, provide your answer and its source.\n")
        
        # Get initial problem
        print("-" * 70)
        print("STEP 1: Define the observable problem")
        print("-" * 70)
        problem = input("\nWhat is the observable problem?\n> ").strip()
        
        source = input("\nSource for this problem observation (or 'none'):\n> ").strip()
        if source.lower() == 'none':
            source = None
        
        self.set_initial_problem(problem, source)
        
        # Iterate through why levels
        current_answer = problem
        
        for level in range(1, self.MAX_LEVELS + 1):
            print("\n" + "=" * 70)
            print(f"WHY #{level}")
            print("=" * 70)
            
            question = self.get_next_question(current_answer)
            print(f"\n{question}")
            
            answer = input("\nYour answer:\n> ").strip()
            
            if not answer:
                print("Answer required. Please provide an answer.")
                answer = input("> ").strip()
            
            # Get source
            print("\nWhat source supports this answer?")
            print("  [1] Document (specify name)")
            print("  [2] User knowledge/experience (no document)")
            print("  [3] This is an assumption")
            
            source_choice = input("> ").strip()
            
            source = None
            is_assumption = False
            assumption_basis = None
            
            if source_choice == '1':
                source = input("Document name: ").strip()
            elif source_choice == '2':
                source = "User knowledge (no document)"
            elif source_choice == '3':
                is_assumption = True
                assumption_basis = input("Basis for assumption: ").strip()
                source = "ASSUMPTION"
            
            self.add_why_level(
                level=level,
                question=question,
                answer=answer,
                source=source,
                is_assumption=is_assumption,
                assumption_basis=assumption_basis
            )
            
            # Check if at root cause
            assessment = self.is_at_root_cause(answer)
            
            print("\n" + "-" * 70)
            print("DEPTH CHECK:")
            
            if assessment['indicators']:
                print(f"  Root cause indicators: {', '.join(assessment['indicators'])}")
            if assessment['concerns']:
                print(f"  Symptom indicators: {', '.join(assessment['concerns'])}")
            
            print("\nHave we reached the root cause?")
            print("  [Y] Yes - this is the root cause")
            print("  [N] No - continue asking why")
            print("  [U] Unsure - help me decide")
            
            choice = input("> ").strip().upper()
            
            if choice == 'Y':
                confidence = input("\nConfidence level (high/medium/low): ").strip().lower()
                rationale = input("Why is this the root cause?\n> ").strip()
                
                self.set_root_cause(answer, level, confidence, rationale)
                break
            
            elif choice == 'U':
                if assessment['likely_root_cause']:
                    print("\n✓ Analysis suggests this MAY be a root cause.")
                    print("  Consider: Can a solution be implemented at this level?")
                else:
                    print("\n✗ Analysis suggests more depth may be needed.")
                    print("  The answer still contains symptom-like language.")
                
                confirm = input("\nContinue with this as root cause? [Y/N]: ").strip().upper()
                if confirm == 'Y':
                    confidence = input("Confidence level (high/medium/low): ").strip().lower()
                    rationale = input("Why is this the root cause?\n> ").strip()
                    self.set_root_cause(answer, level, confidence, rationale)
                    break
            
            current_answer = answer
            
            if level >= self.MAX_LEVELS:
                print(f"\n⚠️  Reached maximum depth ({self.MAX_LEVELS} levels).")
                print("The last answer will be used as the root cause.")
                self.set_root_cause(answer, level, 'low', 'Maximum depth reached')
        
        # Print results
        print("\n")
        self.print_chain()
        
        # Offer to save
        save = input("\nSave analysis to file? [Y/N]: ").strip().upper()
        if save == 'Y':
            filename = input("Filename (default: five_whys_analysis.json): ").strip()
            if not filename:
                filename = "five_whys_analysis.json"
            self.export(filename)
            print(f"Saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='5 Whys root cause analysis'
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive analysis session')
    parser.add_argument('--load', '-l', help='Load existing analysis from JSON')
    parser.add_argument('--output', '-o', help='Output file for results')
    
    args = parser.parse_args()
    
    analysis = FiveWhysAnalysis()
    
    if args.load:
        with open(args.load) as f:
            analysis.analysis = json.load(f)
        analysis.print_chain()
    elif args.interactive:
        analysis.run_interactive()
    else:
        # Default to interactive
        analysis.run_interactive()
    
    if args.output:
        analysis.export(args.output)
        print(f"Analysis saved to: {args.output}")


if __name__ == '__main__':
    main()
