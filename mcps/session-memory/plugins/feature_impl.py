"""Feature Implementation session plugin.

This plugin provides structured tracking for feature development:
- Phase-based workflow (planning, design, implementation, testing, review)
- Task breakdown and progress tracking
- File changes and test coverage
- Integration and deployment readiness
"""

from typing import Any, Dict, List

from .base import PluginState, ResumptionContext, SessionPlugin


class FeatureImplementationPlugin(SessionPlugin):
    """Plugin for feature implementation sessions."""

    PHASES = [
        "planning",       # Requirements gathering and scoping
        "design",         # Architecture and design decisions
        "implementation", # Writing the code
        "testing",        # Unit/integration tests
        "review",         # Code review and refinement
        "integration"     # Merging and deployment prep
    ]

    @property
    def name(self) -> str:
        return "feature-implementation"

    @property
    def supported_skills(self) -> List[str]:
        return ["feature-implementation", "feature", "implement", "build-feature"]

    def get_state_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "enum": self.PHASES
                },
                "progress": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "custom_data": {
                    "type": "object",
                    "properties": {
                        "feature_info": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "requirements": {"type": "array", "items": {"type": "string"}},
                                "acceptance_criteria": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "design": {
                            "type": "object",
                            "properties": {
                                "approach": {"type": "string"},
                                "components": {"type": "array", "items": {"type": "string"}},
                                "dependencies": {"type": "array", "items": {"type": "string"}},
                                "decisions": {"type": "array", "items": {"type": "object"}}
                            }
                        },
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"]},
                                    "files": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "files_changed": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "action": {"type": "string", "enum": ["created", "modified", "deleted"]},
                                    "lines_added": {"type": "integer"},
                                    "lines_removed": {"type": "integer"}
                                }
                            }
                        },
                        "tests": {
                            "type": "object",
                            "properties": {
                                "unit_tests_added": {"type": "integer"},
                                "integration_tests_added": {"type": "integer"},
                                "tests_passing": {"type": "boolean"},
                                "coverage_change": {"type": "number"}
                            }
                        },
                        "review": {
                            "type": "object",
                            "properties": {
                                "pr_created": {"type": "boolean"},
                                "pr_number": {"type": "integer"},
                                "reviewers": {"type": "array", "items": {"type": "string"}},
                                "approved": {"type": "boolean"}
                            }
                        }
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        return PluginState(
            phase="planning",
            progress=0.0,
            custom_data={
                "feature_info": {
                    "requirements": [],
                    "acceptance_criteria": []
                },
                "design": {
                    "components": [],
                    "dependencies": [],
                    "decisions": []
                },
                "tasks": [],
                "files_changed": [],
                "tests": {
                    "unit_tests_added": 0,
                    "integration_tests_added": 0,
                    "tests_passing": False,
                    "coverage_change": 0.0
                },
                "review": {
                    "pr_created": False,
                    "approved": False
                }
            }
        )

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        phase = state.phase or "planning"
        data = state.custom_data

        phase_weights = {
            "planning": 0.1,
            "design": 0.2,
            "implementation": 0.5,
            "testing": 0.7,
            "review": 0.85,
            "integration": 0.95
        }
        base = phase_weights.get(phase, 0.0)

        # Task-based progress during implementation
        if phase == "implementation":
            tasks = data.get("tasks", [])
            if tasks:
                completed = len([t for t in tasks if t.get("status") == "completed"])
                base += 0.3 * (completed / len(tasks))

        # Testing progress
        if phase == "testing":
            tests = data.get("tests", {})
            if tests.get("tests_passing"):
                base += 0.1

        # Review progress
        if phase == "review":
            review = data.get("review", {})
            if review.get("pr_created"):
                base += 0.05
            if review.get("approved"):
                base += 0.1

        return min(1.0, base)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        data = state.custom_data
        feature_info = data.get("feature_info", {})

        # Build summary
        summary_parts = [f"Feature implementation - Phase: {state.phase or 'planning'}."]
        if feature_info.get("name"):
            summary_parts.append(f"Feature: {feature_info['name']}")

        tasks = data.get("tasks", [])
        if tasks:
            completed = len([t for t in tasks if t.get("status") == "completed"])
            summary_parts.append(f"Tasks: {completed}/{len(tasks)} completed.")

        files = data.get("files_changed", [])
        if files:
            summary_parts.append(f"Files changed: {len(files)}.")

        tests = data.get("tests", {})
        if tests.get("unit_tests_added") or tests.get("integration_tests_added"):
            summary_parts.append(f"Tests: {tests.get('unit_tests_added', 0)} unit, {tests.get('integration_tests_added', 0)} integration.")

        summary_text = " ".join(summary_parts)

        # Next steps
        next_steps = []
        blocking = []

        if state.phase == "planning":
            next_steps = [
                "Define feature requirements",
                "Document acceptance criteria",
                "Identify dependencies and constraints"
            ]
            if not feature_info.get("requirements"):
                blocking.append("No requirements documented yet")
        elif state.phase == "design":
            design = data.get("design", {})
            next_steps.append("Finalize architecture approach")
            if not design.get("components"):
                next_steps.append("Identify components to create/modify")
            next_steps.append("Document design decisions")
        elif state.phase == "implementation":
            in_progress = [t for t in tasks if t.get("status") == "in_progress"]
            pending = [t for t in tasks if t.get("status") == "pending"]
            blocked_tasks = [t for t in tasks if t.get("status") == "blocked"]

            if in_progress:
                next_steps.append(f"Continue: {in_progress[0].get('description', '')[:50]}")
            if pending:
                next_steps.append(f"Next: {pending[0].get('description', '')[:50]}")
            for bt in blocked_tasks[:2]:
                blocking.append(f"Blocked: {bt.get('description', '')[:50]}")
        elif state.phase == "testing":
            if not tests.get("tests_passing"):
                next_steps.append("Fix failing tests")
            next_steps.append("Add missing test coverage")
            next_steps.append("Run full test suite")
        elif state.phase == "review":
            review = data.get("review", {})
            if not review.get("pr_created"):
                next_steps.append("Create pull request")
            elif not review.get("approved"):
                next_steps.append("Address review feedback")
            else:
                next_steps.append("Prepare for merge")
        elif state.phase == "integration":
            next_steps = [
                "Merge to main branch",
                "Verify deployment",
                "Update documentation"
            ]

        return ResumptionContext(
            summary=summary_text,
            next_steps=next_steps,
            blocking_items=blocking,
            state=state
        )

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        category = event.get("category", "")
        event_type = event.get("type", "")
        data = event.get("data", {})

        # Track phase transitions
        if category == "phase":
            new_phase = data.get("name") or data.get("phase")
            if new_phase and new_phase in self.PHASES:
                state.phase = new_phase

        # Track design decisions
        if category == "decision":
            decisions = state.custom_data.get("design", {}).get("decisions", [])
            decisions.append({
                "id": event.get("id", ""),
                "title": data.get("title", ""),
                "rationale": data.get("rationale", ""),
                "timestamp": event.get("timestamp", "")
            })
            state.custom_data["design"]["decisions"] = decisions

        # Track file changes
        if category == "tool_call" and data.get("tool") in ("Write", "Edit"):
            file_path = data.get("file_path", "")
            if file_path:
                files = state.custom_data.get("files_changed", [])
                existing = next((f for f in files if f["path"] == file_path), None)
                action = "created" if data.get("tool") == "Write" else "modified"

                if existing:
                    existing["action"] = action
                else:
                    files.append({
                        "path": file_path,
                        "action": action,
                        "lines_added": 0,
                        "lines_removed": 0
                    })
                state.custom_data["files_changed"] = files

                # Track test files
                if "test" in file_path.lower() or "_test." in file_path or ".test." in file_path:
                    tests = state.custom_data.get("tests", {})
                    if "integration" in file_path.lower():
                        tests["integration_tests_added"] = tests.get("integration_tests_added", 0) + 1
                    else:
                        tests["unit_tests_added"] = tests.get("unit_tests_added", 0) + 1
                    state.custom_data["tests"] = tests

        state.progress = self.calculate_progress([], state)
        return state
