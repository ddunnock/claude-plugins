#!/usr/bin/env python3
"""
Assumption Tracker for Concept Development

Manages assumption registration, tracking, and mandatory review.
Adapted from trade-study-analysis assumption_tracker.py with
concept-dev-specific categories.
"""

import os
import json
import sys
import argparse
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


class AssumptionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class AssumptionCategory(Enum):
    SCOPE = "scope"
    FEASIBILITY = "feasibility"
    ARCHITECTURE = "architecture"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    TECHNOLOGY = "technology"
    CONSTRAINT = "constraint"
    STAKEHOLDER = "stakeholder"
    OTHER = "other"


class AssumptionTracker:
    """Manages assumptions made during concept development."""

    IMPACT_LEVELS = ['low', 'medium', 'high', 'critical']

    def __init__(self, registry_path: str = '.concept-dev/assumption_registry.json'):
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
        """Save registry to file atomically."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry['metadata']['last_modified'] = datetime.now().isoformat()
        self.registry['summary'] = self._calculate_summary()
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.registry_path.parent), suffix='.tmp'
        )
        try:
            with open(fd, 'w') as f:
                json.dump(self.registry, f, indent=2)
            Path(tmp_path).replace(self.registry_path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def _generate_id(self, prefix: str, items_key: str) -> str:
        """Generate unique ID with the given prefix from the given registry list."""
        existing_ids = {item['id'] for item in self.registry[items_key]}
        counter = 1
        while f"{prefix}-{counter:03d}" in existing_ids:
            counter += 1
        return f"{prefix}-{counter:03d}"

    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        assumptions = self.registry['assumptions']

        by_status = {s.value: sum(1 for a in assumptions if a['status'] == s.value)
                     for s in AssumptionStatus}
        by_category = {c.value: sum(1 for a in assumptions if a['category'] == c.value)
                       for c in AssumptionCategory}
        by_impact = {level: sum(1 for a in assumptions if a['impact_level'] == level)
                     for level in self.IMPACT_LEVELS}

        by_phase: Dict[str, int] = {}
        for a in assumptions:
            phase = a.get('phase', 'unassigned')
            by_phase[phase] = by_phase.get(phase, 0) + 1

        return {
            'total': len(assumptions),
            'by_status': by_status,
            'by_category': by_category,
            'by_impact': by_impact,
            'by_phase': by_phase,
            'pending_count': by_status.get('pending', 0),
            'approved_count': by_status.get('approved', 0),
            'ready_for_document': by_status.get('pending', 0) == 0
        }

    def add_assumption(
        self,
        description: str,
        category: str,
        phase: str,
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
            phase: Which concept-dev phase this was made in
            basis: Source or rationale for assumption
            source_id: Reference to source registry if applicable
            impact_level: Low/medium/high/critical
            impact_explanation: Explanation of impact if wrong
            alternatives_considered: Other options if assumption invalid

        Returns:
            Assumption ID
        """
        valid_categories = [c.value for c in AssumptionCategory]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

        if impact_level not in self.IMPACT_LEVELS:
            raise ValueError(f"Invalid impact level. Must be one of: {self.IMPACT_LEVELS}")

        assumption_id = self._generate_id('A', 'assumptions')

        assumption = {
            'id': assumption_id,
            'description': description,
            'category': category,
            'phase': phase,
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
        required_source_type: str,
        phase: Optional[str] = None
    ) -> str:
        """
        Register a claim that lacks source documentation.

        Args:
            claim: The ungrounded claim text
            location: Where this claim appears
            required_source_type: What type of source would ground this
            phase: Which phase this was found in

        Returns:
            Claim ID
        """
        claim_id = self._generate_id('UG', 'ungrounded_claims')

        ungrounded = {
            'id': claim_id,
            'claim': claim,
            'location': location,
            'required_source_type': required_source_type,
            'phase': phase,
            'status': 'unresolved',
            'resolution': None,
            'created_at': datetime.now().isoformat()
        }

        self.registry['ungrounded_claims'].append(ungrounded)
        self._save_registry()

        return claim_id

    def _find_assumption(self, assumption_id: str) -> Dict[str, Any]:
        """Find assumption by ID or raise ValueError."""
        for assumption in self.registry['assumptions']:
            if assumption['id'] == assumption_id:
                return assumption
        raise ValueError(f"Assumption {assumption_id} not found")

    def _review_assumption(
        self,
        assumption_id: str,
        status: AssumptionStatus,
        action: str,
        reviewed_by: str = 'user',
        notes: Optional[str] = None
    ):
        """Apply a review action to an assumption and save."""
        assumption = self._find_assumption(assumption_id)
        assumption['status'] = status.value
        assumption['reviewed_at'] = datetime.now().isoformat()
        assumption['reviewed_by'] = reviewed_by
        if notes:
            assumption['user_response'] = notes
        self._add_review_event(assumption_id, action, notes)
        self._save_registry()
        return assumption

    def approve_assumption(
        self,
        assumption_id: str,
        reviewed_by: str = 'user',
        notes: Optional[str] = None
    ):
        """Approve an assumption."""
        self._review_assumption(assumption_id, AssumptionStatus.APPROVED, 'approved',
                                reviewed_by, notes)

    def reject_assumption(
        self,
        assumption_id: str,
        reason: str,
        reviewed_by: str = 'user'
    ):
        """Reject an assumption."""
        self._review_assumption(assumption_id, AssumptionStatus.REJECTED, 'rejected',
                                reviewed_by, reason)

    def modify_assumption(
        self,
        assumption_id: str,
        new_description: str,
        modification_reason: str,
        reviewed_by: str = 'user'
    ):
        """Modify an assumption and mark as modified."""
        assumption = self._find_assumption(assumption_id)
        old_description = assumption['description']
        assumption['description'] = new_description
        assumption['modification_note'] = (
            f"Changed from: '{old_description}'. Reason: {modification_reason}"
        )
        self._review_assumption(assumption_id, AssumptionStatus.MODIFIED, 'modified',
                                reviewed_by, modification_reason)

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
                self._save_registry()
                return
        raise ValueError(f"Ungrounded claim {claim_id} not found")

    def get_assumption(self, assumption_id: str) -> Optional[Dict[str, Any]]:
        """Get assumption by ID, or None if not found."""
        try:
            return self._find_assumption(assumption_id)
        except ValueError:
            return None

    def list_assumptions(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List assumptions with optional filtering."""
        assumptions = self.registry['assumptions']
        if status:
            assumptions = [a for a in assumptions if a['status'] == status]
        if category:
            assumptions = [a for a in assumptions if a['category'] == category]
        if phase:
            assumptions = [a for a in assumptions if a.get('phase') == phase]
        return assumptions

    def get_pending_count(self) -> int:
        """Get count of pending assumptions."""
        return len([a for a in self.registry['assumptions']
                   if a['status'] == AssumptionStatus.PENDING.value])

    def is_ready_for_document(self) -> bool:
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
        print("MANDATORY ASSUMPTION REVIEW")
        print("=" * 80)

        summary = self.get_summary()
        print(f"\nTOTAL ASSUMPTIONS: {summary['total']}")
        print(f"  Pending: {summary['pending_count']}")
        print(f"  Approved: {summary['approved_count']}")

        print("\n" + "-" * 80)
        print("BY CATEGORY:")
        print("-" * 80)
        for cat, count in summary['by_category'].items():
            if count > 0:
                print(f"  {cat}: {count}")

        print("\nBY PHASE:")
        print("-" * 80)
        for phase, count in summary.get('by_phase', {}).items():
            if count > 0:
                print(f"  {phase}: {count}")

        # Show pending assumptions
        pending = self.list_assumptions(status='pending')
        if pending:
            print("\n" + "=" * 80)
            print("PENDING ASSUMPTIONS (require action):")
            print("=" * 80)

            for assumption in pending:
                print(f"\n[{assumption['id']}] {assumption['description']}")
                print(f"  Category: {assumption['category']}")
                print(f"  Phase: {assumption.get('phase', 'N/A')}")
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
        if self.is_ready_for_document():
            print("READY FOR DOCUMENT GENERATION")
        else:
            print("NOT READY - Resolve all pending items above")
        print("=" * 80)

    def generate_assumptions_section(self) -> str:
        """Generate markdown text for document assumptions section."""
        lines = ["## Assumptions and Limitations\n"]

        summary = self.get_summary()
        lines.append(f"This concept includes {summary['total']} documented assumptions.\n")

        assumptions = self.registry['assumptions']

        for cat in AssumptionCategory:
            cat_assumptions = [a for a in assumptions if a['category'] == cat.value]
            if cat_assumptions:
                cat_name = cat.value.replace('_', ' ').title()
                lines.append(f"\n### {cat_name} Assumptions\n")

                for a in cat_assumptions:
                    status_icon = "V" if a['status'] in ['approved', 'modified'] else "?"
                    lines.append(f"\n**[{a['id']}]** {a['description']} [{status_icon}]\n")
                    lines.append(f"- Basis: {a['basis']}\n")
                    lines.append(f"- Phase: {a.get('phase', 'N/A')}\n")
                    lines.append(f"- Impact if incorrect: {a['impact_level'].capitalize()} - {a['impact_explanation']}\n")
                    lines.append(f"- Status: {a['status'].capitalize()}")
                    if a.get('reviewed_at'):
                        lines.append(f" (reviewed: {a['reviewed_at'][:10]})")
                    lines.append("\n")

        unresolved = [c for c in self.registry['ungrounded_claims'] if c['status'] == 'unresolved']
        if unresolved:
            lines.append("\n### Ungrounded Claims\n")
            lines.append("The following statements require source documentation:\n")
            for claim in unresolved:
                lines.append(f"\n- \"{claim['claim']}\" (Location: {claim['location']})\n")

        return ''.join(lines)


def _sync_to_state(registry_path: str, state_path: str):
    """Sync assumption counts from registry to state.json."""
    state_file = Path(state_path)
    if not state_file.exists():
        return
    reg_file = Path(registry_path)
    if not reg_file.exists():
        return
    with open(reg_file, 'r') as f:
        reg = json.load(f)
    assumptions = reg.get('assumptions', [])
    total = len(assumptions)
    pending = sum(1 for a in assumptions if a.get('status') == 'pending')
    approved = sum(1 for a in assumptions if a.get('status') in ('approved', 'modified'))

    with open(state_file, 'r') as f:
        state = json.load(f)
    state['assumptions']['total'] = total
    state['assumptions']['pending'] = pending
    state['assumptions']['approved'] = approved
    state['session']['last_updated'] = datetime.now().isoformat()
    tmp = state_file.with_suffix('.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    tmp.rename(state_file)




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
    parser = argparse.ArgumentParser(
        description='Manage assumptions for concept development'
    )
    parser.add_argument('--state', default='.concept-dev/state.json',
                       help='Path to state.json for auto-sync')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Init
    subparsers.add_parser('init', help='Initialize assumption registry')

    # Add assumption
    add_parser = subparsers.add_parser('add', help='Add a new assumption')
    add_parser.add_argument('description', help='Assumption description')
    add_parser.add_argument('--category', required=True,
                           choices=[c.value for c in AssumptionCategory],
                           help='Assumption category')
    add_parser.add_argument('--phase', required=True, help='Concept-dev phase')
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
    list_parser.add_argument('--phase')

    # Export
    export_parser = subparsers.add_parser('export', help='Export for document')
    export_parser.add_argument('-o', '--output', help='Output file')
    export_parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')

    # Check readiness
    subparsers.add_parser('ready', help='Check if ready for document generation')

    parser.add_argument('--registry', default='.concept-dev/assumption_registry.json',
                       help='Path to assumption registry file')

    args = parser.parse_args()

    args.registry = _validate_path(args.registry, {'.json'}, "registry file")
    args.state = _validate_path(args.state, {'.json'}, "state file")
    if args.command == "export" and hasattr(args, "output") and args.output:
        args.output = _validate_path(args.output, {'.md', '.json'}, "output file")

    tracker = AssumptionTracker(args.registry)

    if args.command == 'init':
        if tracker.registry_path.exists():
            summary = tracker.get_summary()
            print(f"Registry exists: {tracker.registry_path}")
            print(f"  Assumptions: {summary['total']} ({summary['pending_count']} pending)")
        else:
            tracker._save_registry()
            print(f"Created empty registry: {tracker.registry_path}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'add':
        assumption_id = tracker.add_assumption(
            description=args.description,
            category=args.category,
            phase=args.phase,
            basis=args.basis,
            source_id=args.source_id,
            impact_level=args.impact,
            impact_explanation=args.impact_explanation
        )
        print(f"Added assumption: {assumption_id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'approve':
        if args.id.lower() == 'all':
            approved = tracker.approve_all_pending()
            print(f"Approved {len(approved)} assumptions: {', '.join(approved)}")
        else:
            tracker.approve_assumption(args.id, notes=args.notes)
            print(f"Approved: {args.id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'reject':
        tracker.reject_assumption(args.id, reason=args.reason)
        print(f"Rejected: {args.id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'modify':
        tracker.modify_assumption(args.id, args.new_description, args.reason)
        print(f"Modified: {args.id}")
        _sync_to_state(args.registry, args.state)

    elif args.command == 'review':
        tracker.print_review_prompt()

    elif args.command == 'summary':
        summary = tracker.get_summary()
        print(json.dumps(summary, indent=2))

    elif args.command == 'list':
        assumptions = tracker.list_assumptions(
            status=args.status,
            category=args.category,
            phase=args.phase
        )
        status_icons = {'approved': 'V', 'pending': '?'}
        for a in assumptions:
            icon = status_icons.get(a['status'], 'X')
            print(f"[{a['id']}] {icon} {a['description'][:60]}...")

    elif args.command == 'export':
        if args.format == 'json':
            data = tracker.get_summary()
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
        if tracker.is_ready_for_document():
            print("Ready for document generation")
        else:
            print(f"Not ready - {tracker.get_pending_count()} pending assumptions")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
