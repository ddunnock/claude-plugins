#!/usr/bin/env python3
"""
Assumption Tracker for Trade Study Analysis

Manages assumption registration, tracking, and mandatory review.
All assumptions must be explicitly approved before report generation.
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
import sys


class AssumptionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class AssumptionCategory(Enum):
    DATA = "data"
    METHODOLOGY = "methodology"
    SCOPE = "scope"
    SOURCE_INTERPRETATION = "source_interpretation"
    WEIGHT_RATIONALE = "weight_rationale"
    SENSITIVITY_PARAMS = "sensitivity_parameters"
    OTHER = "other"


class AssumptionTracker:
    """Manages assumptions made during trade study analysis."""
    
    IMPACT_LEVELS = ['low', 'medium', 'high', 'critical']
    
    def __init__(self, registry_path: str = 'assumptions/assumption_registry.json'):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load existing registry or create new one."""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            },
            'assumptions': [],
            'ungrounded_claims': [],
            'review_history': []
        }
    
    def _save_registry(self):
        """Save registry to file."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry['metadata']['last_modified'] = datetime.now().isoformat()
        
        # Update summary
        self.registry['summary'] = self._calculate_summary()
        
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _generate_id(self) -> str:
        """Generate unique assumption ID."""
        existing_ids = [a['id'] for a in self.registry['assumptions']]
        counter = 1
        while f"A-{counter:03d}" in existing_ids:
            counter += 1
        return f"A-{counter:03d}"
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        assumptions = self.registry['assumptions']
        
        by_status = {}
        for status in AssumptionStatus:
            by_status[status.value] = len([a for a in assumptions if a['status'] == status.value])
        
        by_category = {}
        for cat in AssumptionCategory:
            by_category[cat.value] = len([a for a in assumptions if a['category'] == cat.value])
        
        by_impact = {}
        for impact in self.IMPACT_LEVELS:
            by_impact[impact] = len([a for a in assumptions if a['impact_level'] == impact])
        
        return {
            'total': len(assumptions),
            'by_status': by_status,
            'by_category': by_category,
            'by_impact': by_impact,
            'pending_count': by_status.get('pending', 0),
            'approved_count': by_status.get('approved', 0),
            'ready_for_report': by_status.get('pending', 0) == 0
        }
    
    def add_assumption(
        self,
        description: str,
        category: str,
        made_during: str,
        basis: str,
        source_id: Optional[str] = None,
        impact_level: str = 'medium',
        impact_explanation: str = '',
        alternatives_considered: Optional[List[str]] = None
    ) -> str:
        """
        Register a new assumption.
        
        Args:
            description: What is being assumed
            category: Category from AssumptionCategory
            made_during: Which step/phase this was made
            basis: Source or rationale for assumption
            source_id: Reference to source registry if applicable
            impact_level: Low/medium/high/critical
            impact_explanation: Explanation of impact if wrong
            alternatives_considered: Other options if assumption invalid
            
        Returns:
            Assumption ID
        """
        # Validate category
        valid_categories = [c.value for c in AssumptionCategory]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")
        
        if impact_level not in self.IMPACT_LEVELS:
            raise ValueError(f"Invalid impact level. Must be one of: {self.IMPACT_LEVELS}")
        
        assumption_id = self._generate_id()
        
        assumption = {
            'id': assumption_id,
            'description': description,
            'category': category,
            'made_during': made_during,
            'basis': basis,
            'source_id': source_id,
            'impact_level': impact_level,
            'impact_explanation': impact_explanation,
            'alternatives_considered': alternatives_considered or [],
            'status': AssumptionStatus.PENDING.value,
            'user_response': None,
            'modification_note': None,
            'created_at': datetime.now().isoformat(),
            'reviewed_at': None,
            'reviewed_by': None
        }
        
        self.registry['assumptions'].append(assumption)
        self._save_registry()
        
        return assumption_id
    
    def add_ungrounded_claim(
        self,
        claim: str,
        location: str,
        required_source_type: str
    ) -> str:
        """
        Register a claim that lacks source documentation.
        
        Args:
            claim: The ungrounded claim text
            location: Where this claim appears
            required_source_type: What type of source would ground this
            
        Returns:
            Claim ID
        """
        claim_id = f"UG-{len(self.registry['ungrounded_claims']) + 1:03d}"
        
        ungrounded = {
            'id': claim_id,
            'claim': claim,
            'location': location,
            'required_source_type': required_source_type,
            'status': 'unresolved',
            'resolution': None,
            'created_at': datetime.now().isoformat()
        }
        
        self.registry['ungrounded_claims'].append(ungrounded)
        self._save_registry()
        
        return claim_id
    
    def approve_assumption(
        self,
        assumption_id: str,
        reviewed_by: str = 'user',
        notes: Optional[str] = None
    ):
        """Approve an assumption."""
        for assumption in self.registry['assumptions']:
            if assumption['id'] == assumption_id:
                assumption['status'] = AssumptionStatus.APPROVED.value
                assumption['reviewed_at'] = datetime.now().isoformat()
                assumption['reviewed_by'] = reviewed_by
                if notes:
                    assumption['user_response'] = notes
                
                self._add_review_event(assumption_id, 'approved', notes)
                break
        
        self._save_registry()
    
    def reject_assumption(
        self,
        assumption_id: str,
        reason: str,
        reviewed_by: str = 'user'
    ):
        """Reject an assumption."""
        for assumption in self.registry['assumptions']:
            if assumption['id'] == assumption_id:
                assumption['status'] = AssumptionStatus.REJECTED.value
                assumption['user_response'] = reason
                assumption['reviewed_at'] = datetime.now().isoformat()
                assumption['reviewed_by'] = reviewed_by
                
                self._add_review_event(assumption_id, 'rejected', reason)
                break
        
        self._save_registry()
    
    def modify_assumption(
        self,
        assumption_id: str,
        new_description: str,
        modification_reason: str,
        reviewed_by: str = 'user'
    ):
        """Modify an assumption and mark as approved."""
        for assumption in self.registry['assumptions']:
            if assumption['id'] == assumption_id:
                old_description = assumption['description']
                assumption['description'] = new_description
                assumption['status'] = AssumptionStatus.MODIFIED.value
                assumption['modification_note'] = f"Changed from: '{old_description}'. Reason: {modification_reason}"
                assumption['reviewed_at'] = datetime.now().isoformat()
                assumption['reviewed_by'] = reviewed_by
                
                self._add_review_event(assumption_id, 'modified', modification_reason)
                break
        
        self._save_registry()
    
    def approve_all_pending(self, reviewed_by: str = 'user'):
        """Approve all pending assumptions."""
        approved_ids = []
        for assumption in self.registry['assumptions']:
            if assumption['status'] == AssumptionStatus.PENDING.value:
                assumption['status'] = AssumptionStatus.APPROVED.value
                assumption['reviewed_at'] = datetime.now().isoformat()
                assumption['reviewed_by'] = reviewed_by
                assumption['user_response'] = 'Bulk approved'
                approved_ids.append(assumption['id'])
        
        if approved_ids:
            self._add_review_event(
                ','.join(approved_ids),
                'bulk_approved',
                f"Bulk approved {len(approved_ids)} assumptions"
            )
        
        self._save_registry()
        return approved_ids
    
    def _add_review_event(self, assumption_id: str, action: str, notes: Optional[str]):
        """Add review event to history."""
        event = {
            'assumption_id': assumption_id,
            'action': action,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        self.registry['review_history'].append(event)
    
    def resolve_ungrounded_claim(
        self,
        claim_id: str,
        resolution: str,
        source_id: Optional[str] = None
    ):
        """Resolve an ungrounded claim."""
        for claim in self.registry['ungrounded_claims']:
            if claim['id'] == claim_id:
                claim['status'] = 'resolved'
                claim['resolution'] = resolution
                claim['resolved_source_id'] = source_id
                claim['resolved_at'] = datetime.now().isoformat()
                break
        self._save_registry()
    
    def get_assumption(self, assumption_id: str) -> Optional[Dict[str, Any]]:
        """Get assumption by ID."""
        for assumption in self.registry['assumptions']:
            if assumption['id'] == assumption_id:
                return assumption
        return None
    
    def list_assumptions(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List assumptions with optional filtering."""
        assumptions = self.registry['assumptions']
        
        if status:
            assumptions = [a for a in assumptions if a['status'] == status]
        
        if category:
            assumptions = [a for a in assumptions if a['category'] == category]
        
        return assumptions
    
    def get_pending_count(self) -> int:
        """Get count of pending assumptions."""
        return len([a for a in self.registry['assumptions'] 
                   if a['status'] == AssumptionStatus.PENDING.value])
    
    def is_ready_for_report(self) -> bool:
        """Check if all assumptions are resolved (no pending)."""
        pending = self.get_pending_count()
        unresolved_claims = len([c for c in self.registry['ungrounded_claims'] 
                                if c['status'] == 'unresolved'])
        return pending == 0 and unresolved_claims == 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of assumption status."""
        return self._calculate_summary()
    
    def print_review_prompt(self):
        """Print formatted assumption review prompt."""
        print("=" * 80)
        print("⚠️  MANDATORY ASSUMPTION REVIEW")
        print("=" * 80)
        
        summary = self.get_summary()
        print(f"\nTOTAL ASSUMPTIONS: {summary['total']}")
        print(f"  • Pending: {summary['pending_count']} ⚠️")
        print(f"  • Approved: {summary['approved_count']}")
        
        print("\n" + "-" * 80)
        print("BY CATEGORY:")
        print("-" * 80)
        for cat, count in summary['by_category'].items():
            if count > 0:
                print(f"  {cat}: {count}")
        
        # Show pending assumptions
        pending = self.list_assumptions(status='pending')
        if pending:
            print("\n" + "=" * 80)
            print("PENDING ASSUMPTIONS (require action):")
            print("=" * 80)
            
            for assumption in pending:
                print(f"\n[{assumption['id']}] {assumption['description']}")
                print(f"  Category: {assumption['category']}")
                print(f"  Made during: {assumption['made_during']}")
                print(f"  Basis: {assumption['basis']}")
                print(f"  Impact if wrong: {assumption['impact_level'].upper()} - {assumption['impact_explanation']}")
                print(f"\n  Actions:")
                print(f"    [A] Approve")
                print(f"    [R] Reject")
                print(f"    [M] Modify")
        
        # Show ungrounded claims
        unresolved = [c for c in self.registry['ungrounded_claims'] if c['status'] == 'unresolved']
        if unresolved:
            print("\n" + "=" * 80)
            print("UNGROUNDED CLAIMS (require source or removal):")
            print("=" * 80)
            
            for claim in unresolved:
                print(f"\n[{claim['id']}] \"{claim['claim']}\"")
                print(f"  Location: {claim['location']}")
                print(f"  Needs: {claim['required_source_type']}")
        
        # Ready status
        print("\n" + "=" * 80)
        if self.is_ready_for_report():
            print("✅ READY FOR REPORT GENERATION")
        else:
            print("⛔ NOT READY - Resolve all pending items above")
        print("=" * 80)
    
    def export_for_report(self) -> Dict[str, Any]:
        """Export assumptions formatted for report inclusion."""
        assumptions = self.registry['assumptions']
        
        # Group by category
        by_category = {}
        for cat in AssumptionCategory:
            cat_assumptions = [a for a in assumptions if a['category'] == cat.value]
            if cat_assumptions:
                by_category[cat.value] = cat_assumptions
        
        return {
            'summary': self.get_summary(),
            'by_category': by_category,
            'all_assumptions': assumptions,
            'ungrounded_claims': self.registry['ungrounded_claims'],
            'exported_at': datetime.now().isoformat()
        }
    
    def generate_assumptions_section(self) -> str:
        """Generate markdown text for report assumptions section."""
        lines = ["## Assumptions and Limitations\n"]
        
        summary = self.get_summary()
        lines.append(f"This analysis includes {summary['total']} documented assumptions.\n")
        
        assumptions = self.registry['assumptions']
        
        # Group by category
        for cat in AssumptionCategory:
            cat_assumptions = [a for a in assumptions if a['category'] == cat.value]
            if cat_assumptions:
                cat_name = cat.value.replace('_', ' ').title()
                lines.append(f"\n### {cat_name} Assumptions\n")
                
                for a in cat_assumptions:
                    status_icon = "✓" if a['status'] in ['approved', 'modified'] else "⚠️"
                    lines.append(f"\n**[{a['id']}]** {a['description']} {status_icon}\n")
                    lines.append(f"- Basis: {a['basis']}\n")
                    lines.append(f"- Impact if incorrect: {a['impact_level'].capitalize()} - {a['impact_explanation']}\n")
                    lines.append(f"- Status: {a['status'].capitalize()}")
                    if a.get('reviewed_at'):
                        lines.append(f" (reviewed: {a['reviewed_at'][:10]})")
                    lines.append("\n")
        
        # Ungrounded claims
        unresolved = [c for c in self.registry['ungrounded_claims'] if c['status'] == 'unresolved']
        if unresolved:
            lines.append("\n### Ungrounded Claims\n")
            lines.append("The following statements require source documentation:\n")
            for claim in unresolved:
                lines.append(f"\n- \"{claim['claim']}\" (Location: {claim['location']})\n")
        
        return ''.join(lines)




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
        description='Manage assumptions for trade study analysis'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add assumption
    add_parser = subparsers.add_parser('add', help='Add a new assumption')
    add_parser.add_argument('description', help='Assumption description')
    add_parser.add_argument('--category', required=True,
                          choices=[c.value for c in AssumptionCategory],
                          help='Assumption category')
    add_parser.add_argument('--during', required=True, help='Step/phase when made')
    add_parser.add_argument('--basis', required=True, help='Source or rationale')
    add_parser.add_argument('--source-id', help='Reference to source registry')
    add_parser.add_argument('--impact', choices=['low', 'medium', 'high', 'critical'],
                          default='medium', help='Impact level')
    add_parser.add_argument('--impact-explanation', default='', help='Impact explanation')
    
    # Approve
    approve_parser = subparsers.add_parser('approve', help='Approve an assumption')
    approve_parser.add_argument('id', help='Assumption ID (or "all" for all pending)')
    approve_parser.add_argument('--notes', help='Approval notes')
    
    # Reject
    reject_parser = subparsers.add_parser('reject', help='Reject an assumption')
    reject_parser.add_argument('id', help='Assumption ID')
    reject_parser.add_argument('--reason', required=True, help='Rejection reason')
    
    # Modify
    modify_parser = subparsers.add_parser('modify', help='Modify an assumption')
    modify_parser.add_argument('id', help='Assumption ID')
    modify_parser.add_argument('--new-description', required=True, help='New description')
    modify_parser.add_argument('--reason', required=True, help='Modification reason')
    
    # Review
    subparsers.add_parser('review', help='Show interactive review prompt')
    
    # Summary
    subparsers.add_parser('summary', help='Show summary')
    
    # List
    list_parser = subparsers.add_parser('list', help='List assumptions')
    list_parser.add_argument('--status', choices=['pending', 'approved', 'rejected', 'modified'])
    list_parser.add_argument('--category', choices=[c.value for c in AssumptionCategory])
    
    # Export
    export_parser = subparsers.add_parser('export', help='Export for report')
    export_parser.add_argument('-o', '--output', help='Output file')
    export_parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    
    # Check readiness
    subparsers.add_parser('ready', help='Check if ready for report')
    
    parser.add_argument('--registry', default='assumptions/assumption_registry.json',
                       help='Path to assumption registry file')
    
    args = parser.parse_args()

    _validate_path(args.registry, {'.json'}, "registry file")
    if args.command == "export" and hasattr(args, "output") and args.output:
        _validate_path(args.output, {'.md', '.json'}, "output file")
    
    tracker = AssumptionTracker(args.registry)
    
    if args.command == 'add':
        assumption_id = tracker.add_assumption(
            description=args.description,
            category=args.category,
            made_during=args.during,
            basis=args.basis,
            source_id=args.source_id,
            impact_level=args.impact,
            impact_explanation=args.impact_explanation
        )
        print(f"Added assumption: {assumption_id}")
    
    elif args.command == 'approve':
        if args.id.lower() == 'all':
            approved = tracker.approve_all_pending()
            print(f"Approved {len(approved)} assumptions: {', '.join(approved)}")
        else:
            tracker.approve_assumption(args.id, notes=args.notes)
            print(f"Approved: {args.id}")
    
    elif args.command == 'reject':
        tracker.reject_assumption(args.id, reason=args.reason)
        print(f"Rejected: {args.id}")
    
    elif args.command == 'modify':
        tracker.modify_assumption(args.id, args.new_description, args.reason)
        print(f"Modified: {args.id}")
    
    elif args.command == 'review':
        tracker.print_review_prompt()
    
    elif args.command == 'summary':
        summary = tracker.get_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.command == 'list':
        assumptions = tracker.list_assumptions(status=args.status, category=args.category)
        for a in assumptions:
            status_icon = "✓" if a['status'] == 'approved' else "⚠️" if a['status'] == 'pending' else "✗"
            print(f"[{a['id']}] {status_icon} {a['description'][:60]}...")
    
    elif args.command == 'export':
        if args.format == 'json':
            data = tracker.export_for_report()
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Exported to: {args.output}")
            else:
                print(json.dumps(data, indent=2))
        else:
            markdown = tracker.generate_assumptions_section()
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(markdown)
                print(f"Exported to: {args.output}")
            else:
                print(markdown)
    
    elif args.command == 'ready':
        if tracker.is_ready_for_report():
            print("✅ Ready for report generation")
            return 0
        else:
            print(f"⛔ Not ready - {tracker.get_pending_count()} pending assumptions")
            return 1
    
    else:
        parser.print_help()


if __name__ == '__main__':
    exit(main() or 0)
