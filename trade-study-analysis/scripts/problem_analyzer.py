#!/usr/bin/env python3
"""
Problem Statement Analyzer for Trade Study Analysis

Validates problem statements against 16 quality criteria.
All 11 required criteria must pass for approval.
"""

import json
import argparse
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple


class ProblemStatementAnalyzer:
    """Analyzes and scores problem statements against quality criteria."""
    
    # Structural criteria
    STRUCTURAL_CRITERIA = {
        'S1': {'name': 'Complete Sentence', 'required': True},
        'S2': {'name': 'Acronym Expansion', 'required': True},
        'S3': {'name': 'Length Bounds (15-75 words)', 'required': True},
        'S4': {'name': 'Active Voice', 'required': False},
        'S5': {'name': 'Present Tense', 'required': False}
    }
    
    # Content criteria
    CONTENT_CRITERIA = {
        'C1': {'name': 'Root Cause Focus', 'required': True},
        'C2': {'name': 'Actionable Scope', 'required': True},
        'C3': {'name': 'Measurable Impact', 'required': True},
        'C4': {'name': 'Stakeholder Clarity', 'required': False},
        'C5': {'name': 'Constraint Awareness', 'required': False},
        'C6': {'name': 'Domain Specificity', 'required': False}
    }
    
    # Validation criteria
    VALIDATION_CRITERIA = {
        'V1': {'name': 'Symptom Test (5 Whys)', 'required': True},
        'V2': {'name': 'Completability Test', 'required': True},
        'V3': {'name': 'Solution Neutrality', 'required': True},
        'V4': {'name': 'Scope Appropriateness', 'required': True},
        'V5': {'name': 'Stakeholder Consensus', 'required': False}
    }
    
    # Common acronyms to check
    COMMON_ACRONYMS = [
        'RF', 'API', 'UI', 'UX', 'CPU', 'GPU', 'RAM', 'SSD', 'HDD',
        'COTS', 'GOTS', 'SWaP', 'TRL', 'MRL', 'IRL', 'BER', 'SNR',
        'EIRP', 'MTBF', 'MTTR', 'SLA', 'KPI', 'ROI', 'TCO', 'NPV',
        'IoT', 'AI', 'ML', 'NLP', 'SaaS', 'PaaS', 'IaaS', 'DevOps',
        'CI', 'CD', 'QA', 'UAT', 'MVP', 'POC', 'R&D', 'IP', 'IT'
    ]
    
    # Symptom indicator words
    SYMPTOM_INDICATORS = [
        'slow', 'fails', 'broken', 'error', 'crash', 'timeout',
        'delayed', 'missing', 'wrong', 'incorrect', 'poor',
        'degraded', 'unreliable', 'inconsistent'
    ]
    
    # Solution indicator words
    SOLUTION_INDICATORS = [
        'should use', 'need to implement', 'must adopt', 'will deploy',
        'recommend', 'propose', 'suggest using', 'replace with',
        'upgrade to', 'migrate to', 'install', 'purchase'
    ]
    
    # Passive voice indicators
    PASSIVE_INDICATORS = [
        'is being', 'was being', 'has been', 'have been', 'had been',
        'will be', 'is done', 'was done', 'are affected', 'were affected',
        'is caused', 'was caused', 'is required', 'was required'
    ]
    
    def __init__(self):
        self.results = {}
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def check_complete_sentence(self, statement: str) -> Tuple[bool, str]:
        """Check if statement is a complete sentence."""
        statement = statement.strip()
        
        # Check for ending punctuation
        if not statement.endswith(('.', '!', '?')):
            return False, "Missing ending punctuation"
        
        # Check for capital letter start
        if not statement[0].isupper():
            return False, "Should start with capital letter"
        
        # Basic subject-verb check (simplified)
        words = statement.split()
        if len(words) < 3:
            return False, "Too short to be complete sentence"
        
        return True, "Complete declarative sentence"
    
    def check_acronym_expansion(self, statement: str) -> Tuple[bool, str]:
        """Check if acronyms are expanded on first use."""
        unexpanded = []
        
        # Find potential acronyms (2+ uppercase letters)
        words = re.findall(r'\b[A-Z]{2,}\b', statement)
        
        for word in words:
            if word in self.COMMON_ACRONYMS:
                # Check if expanded format exists: "Full Name (ACRONYM)"
                pattern = rf'\b\w+(?:\s+\w+)*\s+\({word}\)'
                if not re.search(pattern, statement, re.IGNORECASE):
                    unexpanded.append(word)
        
        if unexpanded:
            return False, f"Unexpanded acronyms: {', '.join(unexpanded)}"
        return True, "All acronyms properly expanded"
    
    def check_length_bounds(self, statement: str) -> Tuple[bool, str]:
        """Check if statement is 15-75 words."""
        word_count = self.count_words(statement)
        
        if word_count < 15:
            return False, f"Too short ({word_count} words, need 15+)"
        elif word_count > 75:
            return False, f"Too long ({word_count} words, max 75)"
        else:
            return True, f"Appropriate length ({word_count} words)"
    
    def check_active_voice(self, statement: str) -> Tuple[bool, str]:
        """Check for active voice usage."""
        passive_count = 0
        found_passive = []
        
        statement_lower = statement.lower()
        for indicator in self.PASSIVE_INDICATORS:
            if indicator in statement_lower:
                passive_count += 1
                found_passive.append(indicator)
        
        if passive_count > 2:
            return False, f"Heavy passive voice: {', '.join(found_passive)}"
        elif passive_count > 0:
            return True, f"Some passive voice detected but acceptable"
        else:
            return True, "Active voice used"
    
    def check_present_tense(self, statement: str) -> Tuple[bool, str]:
        """Check for present tense usage."""
        past_tense_patterns = [
            r'\bwas\b', r'\bwere\b', r'\bhad\b', r'\bdid\b',
            r'\b\w+ed\b'  # Past tense verbs
        ]
        
        past_count = 0
        for pattern in past_tense_patterns:
            matches = re.findall(pattern, statement.lower())
            past_count += len(matches)
        
        if past_count > 3:
            return False, "Heavy past tense usage detected"
        return True, "Present tense used appropriately"
    
    def check_root_cause_focus(self, statement: str) -> Tuple[bool, str]:
        """Check if statement focuses on root cause vs symptoms."""
        statement_lower = statement.lower()
        symptom_count = 0
        found_symptoms = []
        
        for indicator in self.SYMPTOM_INDICATORS:
            if indicator in statement_lower:
                symptom_count += 1
                found_symptoms.append(indicator)
        
        # Check for causal language
        causal_indicators = ['because', 'due to', 'caused by', 'results from',
                            'as a result of', 'owing to', 'leads to']
        has_causal = any(ind in statement_lower for ind in causal_indicators)
        
        if symptom_count > 2 and not has_causal:
            return False, f"Appears symptom-focused: {', '.join(found_symptoms)}"
        elif has_causal:
            return True, "Contains causal language indicating root cause focus"
        else:
            return True, "No obvious symptom focus detected"
    
    def check_actionable_scope(self, statement: str) -> Tuple[bool, str]:
        """Check if problem has actionable scope."""
        # Check for overly broad scope
        broad_indicators = ['everything', 'all systems', 'entire organization',
                           'completely', 'always', 'never']
        
        statement_lower = statement.lower()
        for indicator in broad_indicators:
            if indicator in statement_lower:
                return False, f"Scope may be too broad: '{indicator}'"
        
        # Check for specific scope indicators
        specific_indicators = ['system', 'component', 'process', 'capability',
                              'function', 'service', 'module', 'subsystem']
        has_specific = any(ind in statement_lower for ind in specific_indicators)
        
        if has_specific:
            return True, "Appropriately scoped to specific area"
        return True, "Scope appears bounded"
    
    def check_measurable_impact(self, statement: str) -> Tuple[bool, str]:
        """Check for measurable impact statement."""
        # Look for quantitative indicators
        has_numbers = bool(re.search(r'\d+', statement))
        
        # Look for measurement words
        measurement_words = ['percent', '%', 'hours', 'days', 'times',
                            'reduction', 'increase', 'decrease', 'improvement',
                            'performance', 'efficiency', 'throughput', 'latency',
                            'cost', 'revenue', 'productivity', 'reliability']
        
        statement_lower = statement.lower()
        has_measurement = any(word in statement_lower for word in measurement_words)
        
        # Look for impact words
        impact_words = ['affects', 'impacts', 'results in', 'causes', 'leads to',
                       'prevents', 'reduces', 'limits', 'hinders']
        has_impact = any(word in statement_lower for word in impact_words)
        
        if has_numbers and has_measurement:
            return True, "Contains quantified measurable impact"
        elif has_measurement or has_impact:
            return True, "Contains verifiable impact statement"
        else:
            return False, "Missing measurable or verifiable impact"
    
    def check_stakeholder_clarity(self, statement: str) -> Tuple[bool, str]:
        """Check if stakeholders are identified."""
        stakeholder_words = ['users', 'operators', 'engineers', 'team',
                            'customers', 'stakeholders', 'personnel',
                            'maintainers', 'developers', 'administrators',
                            'organization', 'department', 'division']
        
        statement_lower = statement.lower()
        found = [w for w in stakeholder_words if w in statement_lower]
        
        if found:
            return True, f"Stakeholders identified: {', '.join(found)}"
        return False, "No clear stakeholder identification"
    
    def check_constraint_awareness(self, statement: str) -> Tuple[bool, str]:
        """Check for constraint awareness without embedding solutions."""
        constraint_words = ['within', 'limited', 'constraint', 'requirement',
                           'must', 'budget', 'timeline', 'compliance',
                           'regulatory', 'existing', 'current']
        
        statement_lower = statement.lower()
        found = [w for w in constraint_words if w in statement_lower]
        
        if found:
            return True, f"Constraints acknowledged: {', '.join(found)}"
        return True, "No embedded constraints (acceptable)"
    
    def check_domain_specificity(self, statement: str) -> Tuple[bool, str]:
        """Check for domain-specific terminology."""
        # Count technical/domain terms (simplified)
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+(?:tion|ment|ity|ness)\b',  # Technical suffixes
            r'\b(?:system|module|component|interface|protocol)\b'
        ]
        
        technical_count = 0
        for pattern in technical_patterns:
            technical_count += len(re.findall(pattern, statement, re.IGNORECASE))
        
        if technical_count >= 3:
            return True, "Contains domain-specific terminology"
        return False, "Could benefit from more precise domain terms"
    
    def check_symptom_test(self, statement: str) -> Tuple[bool, str]:
        """Check if asking 'why' reveals a deeper problem."""
        # This is a heuristic check - real validation requires user input
        symptom_phrases = [
            'does not work', 'is broken', 'fails to', 'cannot',
            'is slow', 'has errors', 'is unreliable', 'crashes'
        ]
        
        statement_lower = statement.lower()
        for phrase in symptom_phrases:
            if phrase in statement_lower:
                return False, f"May be symptom-level: '{phrase}' - ask 'why?'"
        
        return True, "Passes basic symptom test"
    
    def check_completability(self, statement: str) -> Tuple[bool, str]:
        """Check if statement can be followed by 'because...'"""
        # Remove trailing punctuation
        clean = statement.rstrip('.!?')
        
        # Check if it grammatically accepts 'because'
        # Statements should describe a situation that has a cause
        
        if len(clean.split()) < 10:
            return False, "Too terse to support causal exploration"
        
        return True, "Can be logically followed by 'because...'"
    
    def check_solution_neutrality(self, statement: str) -> Tuple[bool, str]:
        """Check that no specific solution is embedded."""
        statement_lower = statement.lower()
        
        for indicator in self.SOLUTION_INDICATORS:
            if indicator in statement_lower:
                return False, f"Embedded solution detected: '{indicator}'"
        
        # Check for product/vendor names (simplified)
        if re.search(r'\b[A-Z][a-z]+(?:Corp|Inc|LLC|Ltd)\b', statement):
            return False, "May contain vendor/product name"
        
        return True, "Solution neutral"
    
    def check_scope_appropriateness(self, statement: str) -> Tuple[bool, str]:
        """Check scope is neither too narrow nor too broad."""
        word_count = self.count_words(statement)
        
        # Very short statements may be too narrow
        if word_count < 20:
            return False, "May be too narrow - consider broadening scope"
        
        # Check for unbounded language
        unbounded = ['all', 'every', 'any', 'always', 'never', 'completely']
        statement_lower = statement.lower()
        
        unbounded_count = sum(1 for w in unbounded if w in statement_lower)
        if unbounded_count > 1:
            return False, "Scope may be too broad - consider bounding"
        
        return True, "Scope appears appropriate for trade study"
    
    def check_stakeholder_consensus(self, statement: str) -> Tuple[bool, str]:
        """Assess likelihood of stakeholder agreement."""
        # Check for controversial or subjective language
        subjective = ['best', 'worst', 'should', 'must', 'obviously',
                     'clearly', 'simply', 'just', 'only']
        
        statement_lower = statement.lower()
        found = [w for w in subjective if w in statement_lower]
        
        if len(found) > 1:
            return False, f"Subjective language may hinder consensus: {', '.join(found)}"
        
        return True, "Neutral framing supports stakeholder consensus"
    
    def analyze(self, statement: str) -> Dict[str, Any]:
        """
        Analyze a problem statement against all criteria.
        
        Args:
            statement: Problem statement text
            
        Returns:
            Complete analysis results
        """
        results = {
            'statement': statement,
            'word_count': self.count_words(statement),
            'analyzed_at': datetime.now().isoformat(),
            'structural': {},
            'content': {},
            'validation': {},
            'summary': {}
        }
        
        # Structural checks
        checks = {
            'S1': self.check_complete_sentence,
            'S2': self.check_acronym_expansion,
            'S3': self.check_length_bounds,
            'S4': self.check_active_voice,
            'S5': self.check_present_tense
        }
        
        for cid, check_func in checks.items():
            passed, note = check_func(statement)
            results['structural'][cid] = {
                'name': self.STRUCTURAL_CRITERIA[cid]['name'],
                'required': self.STRUCTURAL_CRITERIA[cid]['required'],
                'passed': passed,
                'note': note
            }
        
        # Content checks
        checks = {
            'C1': self.check_root_cause_focus,
            'C2': self.check_actionable_scope,
            'C3': self.check_measurable_impact,
            'C4': self.check_stakeholder_clarity,
            'C5': self.check_constraint_awareness,
            'C6': self.check_domain_specificity
        }
        
        for cid, check_func in checks.items():
            passed, note = check_func(statement)
            results['content'][cid] = {
                'name': self.CONTENT_CRITERIA[cid]['name'],
                'required': self.CONTENT_CRITERIA[cid]['required'],
                'passed': passed,
                'note': note
            }
        
        # Validation checks
        checks = {
            'V1': self.check_symptom_test,
            'V2': self.check_completability,
            'V3': self.check_solution_neutrality,
            'V4': self.check_scope_appropriateness,
            'V5': self.check_stakeholder_consensus
        }
        
        for cid, check_func in checks.items():
            passed, note = check_func(statement)
            results['validation'][cid] = {
                'name': self.VALIDATION_CRITERIA[cid]['name'],
                'required': self.VALIDATION_CRITERIA[cid]['required'],
                'passed': passed,
                'note': note
            }
        
        # Calculate summary
        all_criteria = {**results['structural'], **results['content'], **results['validation']}
        
        total = len(all_criteria)
        passed = sum(1 for c in all_criteria.values() if c['passed'])
        required = [c for c in all_criteria.values() if c['required']]
        required_passed = sum(1 for c in required if c['passed'])
        preferred = [c for c in all_criteria.values() if not c['required']]
        preferred_passed = sum(1 for c in preferred if c['passed'])
        
        all_required_passed = required_passed == len(required)
        
        results['summary'] = {
            'total_score': f"{passed}/{total}",
            'required_score': f"{required_passed}/{len(required)}",
            'preferred_score': f"{preferred_passed}/{len(preferred)}",
            'all_required_passed': all_required_passed,
            'status': 'APPROVED' if all_required_passed else 
                     ('NEEDS_REVISION' if required_passed >= 8 else 'MAJOR_ISSUES'),
            'failed_required': [
                {'id': cid, 'name': c['name'], 'note': c['note']}
                for cid, c in all_criteria.items()
                if c['required'] and not c['passed']
            ]
        }
        
        self.results = results
        return results
    
    def print_report(self):
        """Print formatted analysis report."""
        if not self.results:
            print("No analysis results. Run analyze() first.")
            return
        
        r = self.results
        
        print("=" * 80)
        print("PROBLEM STATEMENT ANALYSIS")
        print("=" * 80)
        
        print(f"\nStatement ({r['word_count']} words):")
        print(f'"{r["statement"]}"')
        
        print("\n" + "-" * 80)
        print("STRUCTURAL CRITERIA:")
        print("-" * 80)
        for cid, c in r['structural'].items():
            status = "✓" if c['passed'] else "✗"
            req = "*" if c['required'] else " "
            print(f"  [{cid}]{req} {status} {c['name']}")
            print(f"       {c['note']}")
        
        print("\n" + "-" * 80)
        print("CONTENT CRITERIA:")
        print("-" * 80)
        for cid, c in r['content'].items():
            status = "✓" if c['passed'] else "✗"
            req = "*" if c['required'] else " "
            print(f"  [{cid}]{req} {status} {c['name']}")
            print(f"       {c['note']}")
        
        print("\n" + "-" * 80)
        print("VALIDATION CRITERIA:")
        print("-" * 80)
        for cid, c in r['validation'].items():
            status = "✓" if c['passed'] else "✗"
            req = "*" if c['required'] else " "
            print(f"  [{cid}]{req} {status} {c['name']}")
            print(f"       {c['note']}")
        
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        
        s = r['summary']
        print(f"\n  Total Score: {s['total_score']}")
        print(f"  Required Criteria: {s['required_score']}")
        print(f"  Preferred Criteria: {s['preferred_score']}")
        print(f"\n  Status: {s['status']}")
        
        if s['failed_required']:
            print("\n  FAILED REQUIRED CRITERIA:")
            for f in s['failed_required']:
                print(f"    - [{f['id']}] {f['name']}: {f['note']}")
        
        print("\n  * = Required criterion")
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze problem statement against quality criteria'
    )
    
    parser.add_argument('statement', nargs='?', help='Problem statement text')
    parser.add_argument('--file', '-f', help='Read statement from file')
    parser.add_argument('--json', '-j', action='store_true',
                       help='Output results as JSON')
    parser.add_argument('--output', '-o', help='Save results to file')
    
    args = parser.parse_args()
    
    # Get statement
    if args.file:
        with open(args.file) as f:
            statement = f.read().strip()
    elif args.statement:
        statement = args.statement
    else:
        print("Enter problem statement (press Ctrl+D when done):")
        statement = input().strip()
    
    # Analyze
    analyzer = ProblemStatementAnalyzer()
    results = analyzer.analyze(statement)
    
    # Output
    if args.json:
        output = json.dumps(results, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results saved to: {args.output}")
        else:
            print(output)
    else:
        analyzer.print_report()
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
    
    # Return exit code based on status
    return 0 if results['summary']['status'] == 'APPROVED' else 1


if __name__ == '__main__':
    exit(main())
