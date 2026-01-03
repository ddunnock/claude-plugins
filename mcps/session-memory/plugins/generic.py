"""Generic plugin for session memory - default plugin for all skills."""

from typing import Any, Dict, List

from .base import SessionPlugin, PluginState, ResumptionContext


class GenericPlugin(SessionPlugin):
    """
    Default plugin that provides basic session tracking.

    Works with any skill by tracking:
    - Event counts by category
    - Phase transitions
    - Basic progress estimation
    """

    @property
    def name(self) -> str:
        return "generic"

    @property
    def supported_skills(self) -> List[str]:
        return ["*"]  # Matches all skills as fallback

    def get_state_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "phase": {"type": "string"},
                "progress": {"type": "number", "minimum": 0, "maximum": 1},
                "custom_data": {
                    "type": "object",
                    "properties": {
                        "event_counts": {
                            "type": "object",
                            "additionalProperties": {"type": "integer"}
                        },
                        "phases_completed": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        """Create initial state with event tracking."""
        return PluginState(
            custom_data={
                "event_counts": {},
                "phases_completed": [],
                "total_events": 0
            }
        )

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        """
        Estimate progress based on event patterns.

        Uses a simple heuristic: more events = more progress,
        capped at 0.9 (only handoff/finalize gets to 1.0).
        """
        total = state.custom_data.get("total_events", 0)

        # Simple log-based progress estimation
        # 10 events = ~0.3, 50 events = ~0.5, 200 events = ~0.7
        if total == 0:
            return 0.0

        import math
        progress = min(0.9, math.log10(total + 1) / 3)

        # Boost if phases have been completed
        phases = state.custom_data.get("phases_completed", [])
        if phases:
            progress = min(0.9, progress + len(phases) * 0.1)

        return round(progress, 2)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        """Generate basic resumption context from event history."""

        # Build summary from state
        event_counts = state.custom_data.get("event_counts", {})
        total = state.custom_data.get("total_events", 0)
        phases = state.custom_data.get("phases_completed", [])

        summary_parts = [f"Session with {total} events recorded"]

        if event_counts:
            top_categories = sorted(
                event_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            cats = ", ".join(f"{k}: {v}" for k, v in top_categories)
            summary_parts.append(f"Categories: {cats}")

        if phases:
            summary_parts.append(f"Completed phases: {', '.join(phases)}")

        if state.phase:
            summary_parts.append(f"Current phase: {state.phase}")

        # Determine next steps from recent events
        next_steps = []
        if events:
            last_event = events[-1] if events else None
            if last_event:
                cat = last_event.get("category", "")
                if cat == "question":
                    next_steps.append("Review and answer open questions")
                elif cat == "finding":
                    next_steps.append("Address reported findings")
                elif cat == "decision":
                    next_steps.append("Continue with implementation based on decisions")
                else:
                    next_steps.append("Continue from last action")

        if not next_steps:
            next_steps.append("Review session state and continue")

        return ResumptionContext(
            summary=". ".join(summary_parts),
            next_steps=next_steps,
            blocking_items=[],
            state=state
        )

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        """Track event counts and phase transitions."""

        # Initialize custom_data if needed
        if not state.custom_data:
            state.custom_data = {
                "event_counts": {},
                "phases_completed": [],
                "total_events": 0
            }

        # Track category counts
        category = event.get("category", "unknown")
        counts = state.custom_data.get("event_counts", {})
        counts[category] = counts.get(category, 0) + 1
        state.custom_data["event_counts"] = counts

        # Track total events
        state.custom_data["total_events"] = state.custom_data.get("total_events", 0) + 1

        # Track phase transitions
        if category == "phase":
            event_type = event.get("type", "")
            data = event.get("data", {})

            if event_type == "phase_start":
                state.phase = data.get("phase", state.phase)
            elif event_type == "phase_complete":
                completed_phase = data.get("phase")
                if completed_phase:
                    phases = state.custom_data.get("phases_completed", [])
                    if completed_phase not in phases:
                        phases.append(completed_phase)
                    state.custom_data["phases_completed"] = phases

        # Update progress
        state.progress = self.calculate_progress([], state)

        return state
