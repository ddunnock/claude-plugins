"""SpecKit-Generator plugin for session memory."""

from typing import Any, Dict, List

from .base import SessionPlugin, PluginState, ResumptionContext


class SpecKitState(PluginState):
    """SpecKit-specific state."""

    def __init__(
        self,
        phase: str = None,
        progress: float = 0.0,
        custom_data: Dict[str, Any] = None
    ):
        super().__init__(phase, progress, custom_data or {})
        # Initialize speckit-specific fields in custom_data
        if "command" not in self.custom_data:
            self.custom_data["command"] = None
        if "completed_tasks" not in self.custom_data:
            self.custom_data["completed_tasks"] = []
        if "pending_tasks" not in self.custom_data:
            self.custom_data["pending_tasks"] = []
        if "blocked_tasks" not in self.custom_data:
            self.custom_data["blocked_tasks"] = []
        if "failed_tasks" not in self.custom_data:
            self.custom_data["failed_tasks"] = []
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
    def completed_tasks(self) -> List[str]:
        return self.custom_data.get("completed_tasks", [])

    @property
    def pending_tasks(self) -> List[str]:
        return self.custom_data.get("pending_tasks", [])

    @property
    def blocked_tasks(self) -> List[str]:
        return self.custom_data.get("blocked_tasks", [])


class SpecKitPlugin(SessionPlugin):
    """Plugin for speckit-generator skill."""

    COMMANDS = ["init", "plan", "tasks", "analyze", "clarify", "implement"]

    @property
    def name(self) -> str:
        return "speckit"

    @property
    def supported_skills(self) -> List[str]:
        return ["speckit-generator", "speckit"]

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
                "progress": {"type": "number", "minimum": 0, "maximum": 1}
            }
        }

    def create_initial_state(self) -> PluginState:
        """Create SpecKit-specific initial state."""
        return SpecKitState()

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        """Calculate progress based on task completion."""
        completed = len(state.custom_data.get("completed_tasks", []))
        pending = len(state.custom_data.get("pending_tasks", []))
        blocked = len(state.custom_data.get("blocked_tasks", []))
        failed = len(state.custom_data.get("failed_tasks", []))

        total = completed + pending + blocked + failed
        if total == 0:
            # No tasks yet - estimate based on command
            command = state.custom_data.get("command")
            if command == "init":
                return 0.1
            elif command == "plan":
                return 0.2
            elif command == "tasks":
                return 0.3
            elif command == "implement":
                return 0.4
            return 0.0

        return round(completed / total, 2)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        """Generate SpecKit-specific resumption context."""

        command = state.custom_data.get("command", "unknown")
        completed = state.custom_data.get("completed_tasks", [])
        pending = state.custom_data.get("pending_tasks", [])
        blocked = state.custom_data.get("blocked_tasks", [])
        failed = state.custom_data.get("failed_tasks", [])

        # Build summary
        summary_parts = [f"SpecKit session using command: {command}"]

        if completed:
            summary_parts.append(f"Completed {len(completed)} tasks")
            if len(completed) <= 3:
                summary_parts.append(f"({', '.join(completed)})")

        if pending:
            summary_parts.append(f"{len(pending)} tasks pending")

        if blocked:
            summary_parts.append(f"{len(blocked)} tasks blocked")

        if failed:
            summary_parts.append(f"{len(failed)} tasks failed")

        # Determine next steps
        next_steps = []

        if failed:
            next_steps.append(f"Review and fix failed tasks: {', '.join(failed[:3])}")

        if blocked:
            next_steps.append(f"Resolve blockers for: {', '.join(blocked[:3])}")

        if pending:
            next_steps.append(f"Continue with task: {pending[0]}")
        elif not failed and not blocked:
            next_steps.append("All tasks complete - ready to finalize")

        return ResumptionContext(
            summary=". ".join(summary_parts),
            next_steps=next_steps,
            blocking_items=blocked + failed,
            state=state
        )

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        """Track task status changes and command usage."""

        # Ensure we have SpecKit state structure
        if "command" not in state.custom_data:
            state = SpecKitState(
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

        # Track task status changes
        if category == "phase":
            task_id = data.get("task_id")

            if event_type == "task_start" and task_id:
                pending = state.custom_data.get("pending_tasks", [])
                if task_id not in pending:
                    pending.append(task_id)
                state.custom_data["pending_tasks"] = pending

            elif event_type == "task_complete" and task_id:
                # Move from pending to completed
                pending = state.custom_data.get("pending_tasks", [])
                completed = state.custom_data.get("completed_tasks", [])

                if task_id in pending:
                    pending.remove(task_id)
                if task_id not in completed:
                    completed.append(task_id)

                state.custom_data["pending_tasks"] = pending
                state.custom_data["completed_tasks"] = completed

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
