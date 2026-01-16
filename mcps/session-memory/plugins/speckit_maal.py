"""SpecKit-MAAL plugin for session memory.

Extends SpecKit plugin with source grounding state tracking for the maal-lang project.
Tracks extraction state, verification results, and source coverage.
"""

from typing import Any, Dict, List

from .base import SessionPlugin, PluginState, ResumptionContext


class SpecKitMaalState(PluginState):
    """SpecKit-MAAL specific state with source grounding tracking."""

    def __init__(
        self,
        phase: str = None,
        progress: float = 0.0,
        custom_data: Dict[str, Any] = None
    ):
        super().__init__(phase, progress, custom_data or {})

        # Initialize speckit-maal specific fields
        if "command" not in self.custom_data:
            self.custom_data["command"] = None

        # Task tracking (inherited from speckit)
        if "completed_tasks" not in self.custom_data:
            self.custom_data["completed_tasks"] = []
        if "pending_tasks" not in self.custom_data:
            self.custom_data["pending_tasks"] = []
        if "blocked_tasks" not in self.custom_data:
            self.custom_data["blocked_tasks"] = []
        if "failed_tasks" not in self.custom_data:
            self.custom_data["failed_tasks"] = []
        if "verified_tasks" not in self.custom_data:
            self.custom_data["verified_tasks"] = []

        # Extraction state (new for maal)
        if "extraction_state" not in self.custom_data:
            self.custom_data["extraction_state"] = {
                "sources_configured": 0,
                "sources_extracted": 0,
                "mappings_count": 0,
                "types_count": 0,
                "constraints_count": 0,
                "last_extracted": None,
                "source_hashes": {}
            }

        # Verification state (new for maal)
        if "verification_state" not in self.custom_data:
            self.custom_data["verification_state"] = {
                "total_checks": 0,
                "passed": 0,
                "errors": 0,
                "warnings": 0,
                "last_verified": None,
                "pending_files": [],
                "issues": []
            }

        # Coverage tracking (new for maal)
        if "coverage" not in self.custom_data:
            self.custom_data["coverage"] = {
                "mappings_covered": 0,
                "mappings_total": 0,
                "types_covered": 0,
                "types_total": 0,
                "constraints_addressed": 0,
                "constraints_total": 0
            }

        # Other tracking
        if "clarification_sessions" not in self.custom_data:
            self.custom_data["clarification_sessions"] = 0
        if "findings_count" not in self.custom_data:
            self.custom_data["findings_count"] = 0

    @property
    def command(self) -> str:
        return self.custom_data.get("command")

    @command.setter
    def command(self, value: str):
        self.custom_data["command"] = value

    @property
    def extraction_state(self) -> Dict:
        return self.custom_data.get("extraction_state", {})

    @property
    def verification_state(self) -> Dict:
        return self.custom_data.get("verification_state", {})

    @property
    def coverage(self) -> Dict:
        return self.custom_data.get("coverage", {})

    @property
    def completed_tasks(self) -> List[str]:
        return self.custom_data.get("completed_tasks", [])

    @property
    def verified_tasks(self) -> List[str]:
        return self.custom_data.get("verified_tasks", [])


class SpecKitMaalPlugin(SessionPlugin):
    """Plugin for speckit-maal skill with source grounding support."""

    COMMANDS = [
        "init", "extract", "plan", "analyze",
        "clarify", "tasks", "implement", "verify"
    ]

    @property
    def name(self) -> str:
        return "speckit-maal"

    @property
    def supported_skills(self) -> List[str]:
        return ["speckit-maal"]

    def get_state_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "phase": {"type": "string"},
                "command": {
                    "type": "string",
                    "enum": self.COMMANDS
                },
                "completed_tasks": {"type": "array", "items": {"type": "string"}},
                "pending_tasks": {"type": "array", "items": {"type": "string"}},
                "blocked_tasks": {"type": "array", "items": {"type": "string"}},
                "failed_tasks": {"type": "array", "items": {"type": "string"}},
                "verified_tasks": {"type": "array", "items": {"type": "string"}},
                "progress": {"type": "number", "minimum": 0, "maximum": 1},
                "extraction_state": {
                    "type": "object",
                    "properties": {
                        "sources_configured": {"type": "integer"},
                        "sources_extracted": {"type": "integer"},
                        "mappings_count": {"type": "integer"},
                        "types_count": {"type": "integer"},
                        "constraints_count": {"type": "integer"},
                        "last_extracted": {"type": "string"},
                        "source_hashes": {"type": "object"}
                    }
                },
                "verification_state": {
                    "type": "object",
                    "properties": {
                        "total_checks": {"type": "integer"},
                        "passed": {"type": "integer"},
                        "errors": {"type": "integer"},
                        "warnings": {"type": "integer"},
                        "last_verified": {"type": "string"},
                        "pending_files": {"type": "array"},
                        "issues": {"type": "array"}
                    }
                },
                "coverage": {
                    "type": "object",
                    "properties": {
                        "mappings_covered": {"type": "integer"},
                        "mappings_total": {"type": "integer"},
                        "types_covered": {"type": "integer"},
                        "types_total": {"type": "integer"},
                        "constraints_addressed": {"type": "integer"},
                        "constraints_total": {"type": "integer"}
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        """Create SpecKit-MAAL specific initial state."""
        return SpecKitMaalState()

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        """Calculate progress based on task completion and verification."""
        completed = len(state.custom_data.get("completed_tasks", []))
        verified = len(state.custom_data.get("verified_tasks", []))
        pending = len(state.custom_data.get("pending_tasks", []))
        blocked = len(state.custom_data.get("blocked_tasks", []))
        failed = len(state.custom_data.get("failed_tasks", []))

        total = completed + pending + blocked + failed
        if total == 0:
            # No tasks yet - estimate based on command and extraction state
            command = state.custom_data.get("command")
            extraction = state.custom_data.get("extraction_state", {})

            if command == "init":
                return 0.05
            elif command == "extract":
                # Progress based on sources extracted
                configured = extraction.get("sources_configured", 0)
                extracted = extraction.get("sources_extracted", 0)
                if configured > 0:
                    return 0.1 + (0.1 * extracted / configured)
                return 0.1
            elif command == "plan":
                return 0.25
            elif command == "analyze":
                return 0.3
            elif command == "tasks":
                return 0.35
            elif command == "implement":
                return 0.4
            elif command == "verify":
                return 0.9
            return 0.0

        # Weight verified tasks higher than just completed
        weighted_complete = completed + (verified * 0.1)  # Bonus for verified
        base_progress = round(weighted_complete / total, 2)

        # Cap at 0.95 until final verification passes
        verification = state.custom_data.get("verification_state", {})
        if verification.get("errors", 0) > 0:
            return min(base_progress, 0.9)

        return min(base_progress, 1.0)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        """Generate SpecKit-MAAL specific resumption context."""

        command = state.custom_data.get("command", "unknown")
        completed = state.custom_data.get("completed_tasks", [])
        verified = state.custom_data.get("verified_tasks", [])
        pending = state.custom_data.get("pending_tasks", [])
        blocked = state.custom_data.get("blocked_tasks", [])
        failed = state.custom_data.get("failed_tasks", [])
        extraction = state.custom_data.get("extraction_state", {})
        verification = state.custom_data.get("verification_state", {})

        # Build summary
        summary_parts = [f"SpecKit-MAAL session using command: {command}"]

        # Extraction status
        if extraction.get("sources_extracted", 0) > 0:
            summary_parts.append(
                f"Sources extracted: {extraction['sources_extracted']}/{extraction.get('sources_configured', '?')} "
                f"({extraction.get('mappings_count', 0)} mappings, "
                f"{extraction.get('types_count', 0)} types)"
            )

        # Task status
        if completed:
            summary_parts.append(f"Completed {len(completed)} tasks")
            if verified:
                summary_parts.append(f"({len(verified)} verified)")

        if pending:
            summary_parts.append(f"{len(pending)} tasks pending")

        # Verification status
        if verification.get("total_checks", 0) > 0:
            summary_parts.append(
                f"Verification: {verification.get('passed', 0)}/{verification['total_checks']} passed"
            )
            if verification.get("errors", 0) > 0:
                summary_parts.append(f"({verification['errors']} errors)")

        # Determine next steps
        next_steps = []

        # Check extraction status first
        if extraction.get("sources_configured", 0) > extraction.get("sources_extracted", 0):
            next_steps.append("Complete source extraction with /speckit-maal.extract")

        # Check verification errors
        if verification.get("errors", 0) > 0:
            issues = verification.get("issues", [])
            if issues:
                next_steps.append(f"Fix verification errors: {issues[0].get('description', 'unknown')}")
            else:
                next_steps.append(f"Fix {verification['errors']} verification error(s)")

        # Task-based next steps
        if failed:
            next_steps.append(f"Review and fix failed tasks: {', '.join(failed[:3])}")

        if blocked:
            next_steps.append(f"Resolve blockers for: {', '.join(blocked[:3])}")

        if pending:
            next_steps.append(f"Continue with task: {pending[0]}")

        # Final verification if tasks done
        if not pending and not failed and not blocked and completed:
            unverified = [t for t in completed if t not in verified]
            if unverified:
                next_steps.append(f"Verify completed tasks: {', '.join(unverified[:3])}")
            else:
                next_steps.append("All tasks complete and verified - ready to finalize")

        blocking_items = blocked + failed
        if verification.get("errors", 0) > 0:
            blocking_items.append("verification_errors")

        return ResumptionContext(
            summary=". ".join(summary_parts),
            next_steps=next_steps,
            blocking_items=blocking_items,
            state=state
        )

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        """Track task status, extraction, and verification events."""

        # Ensure we have MAAL state structure
        if "extraction_state" not in state.custom_data:
            state = SpecKitMaalState(
                phase=state.phase,
                progress=state.progress,
                custom_data=state.custom_data
            )

        category = event.get("category", "")
        event_type = event.get("type", "")
        data = event.get("data", {})

        # Track command changes
        if category == "phase" and event_type == "command_start":
            state.custom_data["command"] = data.get("command")

        # Track extraction events (new for maal)
        if category == "phase":
            if event_type == "extract_start":
                state.custom_data["extraction_state"]["sources_configured"] = \
                    data.get("source_count", 0)

            elif event_type == "extract_complete":
                extraction = state.custom_data["extraction_state"]
                extraction["sources_extracted"] = data.get("sources_extracted", 0)
                extraction["mappings_count"] = data.get("mappings_count", 0)
                extraction["types_count"] = data.get("types_count", 0)
                extraction["constraints_count"] = data.get("constraints_count", 0)
                extraction["last_extracted"] = data.get("timestamp")
                if "source_hashes" in data:
                    extraction["source_hashes"] = data["source_hashes"]

            elif event_type == "extract_source":
                # Individual source extracted
                extraction = state.custom_data["extraction_state"]
                extraction["sources_extracted"] = extraction.get("sources_extracted", 0) + 1

        # Track verification events (new for maal)
        if category == "phase":
            if event_type == "verify_start":
                state.custom_data["verification_state"]["pending_files"] = \
                    data.get("files", [])

            elif event_type == "verify_complete":
                verification = state.custom_data["verification_state"]
                verification["total_checks"] = data.get("total_checks", 0)
                verification["passed"] = data.get("passed", 0)
                verification["errors"] = data.get("errors", 0)
                verification["warnings"] = data.get("warnings", 0)
                verification["last_verified"] = data.get("timestamp")
                verification["issues"] = data.get("issues", [])
                verification["pending_files"] = []

            elif event_type == "verify_file":
                # Single file verified
                pending = state.custom_data["verification_state"].get("pending_files", [])
                file_path = data.get("file")
                if file_path in pending:
                    pending.remove(file_path)

        # Track task status changes
        if category == "phase":
            task_id = data.get("task_id")

            if event_type == "task_start" and task_id:
                pending = state.custom_data.get("pending_tasks", [])
                if task_id not in pending:
                    pending.append(task_id)
                state.custom_data["pending_tasks"] = pending

            elif event_type == "task_complete" and task_id:
                pending = state.custom_data.get("pending_tasks", [])
                completed = state.custom_data.get("completed_tasks", [])

                if task_id in pending:
                    pending.remove(task_id)
                if task_id not in completed:
                    completed.append(task_id)

                state.custom_data["pending_tasks"] = pending
                state.custom_data["completed_tasks"] = completed

            elif event_type == "task_verified" and task_id:
                # Task passed verification (new for maal)
                verified = state.custom_data.get("verified_tasks", [])
                if task_id not in verified:
                    verified.append(task_id)
                state.custom_data["verified_tasks"] = verified

            elif event_type == "task_failed" and task_id:
                pending = state.custom_data.get("pending_tasks", [])
                failed = state.custom_data.get("failed_tasks", [])

                if task_id in pending:
                    pending.remove(task_id)
                if task_id not in failed:
                    failed.append(task_id)

                state.custom_data["pending_tasks"] = pending
                state.custom_data["failed_tasks"] = failed

            elif event_type == "task_blocked" and task_id:
                pending = state.custom_data.get("pending_tasks", [])
                blocked = state.custom_data.get("blocked_tasks", [])

                if task_id in pending:
                    pending.remove(task_id)
                if task_id not in blocked:
                    blocked.append(task_id)

                state.custom_data["pending_tasks"] = pending
                state.custom_data["blocked_tasks"] = blocked

        # Track coverage updates (new for maal)
        if category == "phase" and event_type == "coverage_update":
            coverage = state.custom_data["coverage"]
            coverage["mappings_covered"] = data.get("mappings_covered", coverage.get("mappings_covered", 0))
            coverage["mappings_total"] = data.get("mappings_total", coverage.get("mappings_total", 0))
            coverage["types_covered"] = data.get("types_covered", coverage.get("types_covered", 0))
            coverage["types_total"] = data.get("types_total", coverage.get("types_total", 0))
            coverage["constraints_addressed"] = data.get("constraints_addressed", coverage.get("constraints_addressed", 0))
            coverage["constraints_total"] = data.get("constraints_total", coverage.get("constraints_total", 0))

        # Track clarification sessions
        if category == "phase" and event_type == "clarify_session":
            state.custom_data["clarification_sessions"] = \
                state.custom_data.get("clarification_sessions", 0) + 1

        # Track findings
        if category == "finding":
            state.custom_data["findings_count"] = \
                state.custom_data.get("findings_count", 0) + 1

        # Update progress
        state.progress = self.calculate_progress([], state)

        return state
