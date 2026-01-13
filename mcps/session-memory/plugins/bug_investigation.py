"""Bug Investigation session plugin.

This plugin provides structured tracking for debugging sessions:
- Phase-based workflow (triage, investigation, hypothesis, fix, verification)
- Evidence collection and hypothesis tracking
- Root cause analysis
- Fix verification and regression prevention
"""

from typing import Any, Dict, List

from .base import PluginState, ResumptionContext, SessionPlugin


class BugInvestigationPlugin(SessionPlugin):
    """Plugin for bug investigation/debugging sessions."""

    PHASES = [
        "triage",        # Understanding the bug report
        "reproduction",  # Reproducing the issue
        "investigation", # Gathering evidence
        "hypothesis",    # Forming theories
        "fix",           # Implementing the fix
        "verification"   # Testing the fix
    ]

    @property
    def name(self) -> str:
        return "bug-investigation"

    @property
    def supported_skills(self) -> List[str]:
        return ["bug-investigation", "debug", "fix-bug", "investigate"]

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
                        "bug_info": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                                "reported_by": {"type": "string"},
                                "affected_area": {"type": "string"},
                                "symptoms": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "reproduction": {
                            "type": "object",
                            "properties": {
                                "steps": {"type": "array", "items": {"type": "string"}},
                                "reproduced": {"type": "boolean"},
                                "environment": {"type": "string"}
                            }
                        },
                        "evidence": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "enum": ["log", "stack_trace", "code", "test", "screenshot", "metric"]},
                                    "source": {"type": "string"},
                                    "content": {"type": "string"},
                                    "timestamp": {"type": "string"}
                                }
                            }
                        },
                        "hypotheses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "description": {"type": "string"},
                                    "status": {"type": "string", "enum": ["active", "confirmed", "rejected"]},
                                    "evidence_for": {"type": "array", "items": {"type": "string"}},
                                    "evidence_against": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "root_cause": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "file": {"type": "string"},
                                "line": {"type": "integer"},
                                "cause_type": {"type": "string", "enum": ["logic_error", "race_condition", "null_pointer", "type_error", "config", "dependency", "data_corruption", "resource_leak", "other"]}
                            }
                        },
                        "fix": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "files_changed": {"type": "array", "items": {"type": "string"}},
                                "tested": {"type": "boolean"},
                                "regression_tests_added": {"type": "boolean"}
                            }
                        }
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        return PluginState(
            phase="triage",
            progress=0.0,
            custom_data={
                "bug_info": {
                    "symptoms": []
                },
                "reproduction": {
                    "steps": [],
                    "reproduced": False
                },
                "evidence": [],
                "hypotheses": [],
                "root_cause": None,
                "fix": {
                    "files_changed": [],
                    "tested": False,
                    "regression_tests_added": False
                }
            }
        )

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        phase = state.phase or "triage"
        data = state.custom_data

        phase_weights = {
            "triage": 0.1,
            "reproduction": 0.2,
            "investigation": 0.4,
            "hypothesis": 0.6,
            "fix": 0.8,
            "verification": 0.95
        }
        base = phase_weights.get(phase, 0.0)

        # Bonus for confirmed reproduction
        if data.get("reproduction", {}).get("reproduced"):
            base += 0.05

        # Bonus for confirmed hypothesis
        hypotheses = data.get("hypotheses", [])
        if any(h.get("status") == "confirmed" for h in hypotheses):
            base += 0.1

        # Bonus for identified root cause
        if data.get("root_cause", {}).get("description"):
            base += 0.1

        # Bonus for tested fix
        if data.get("fix", {}).get("tested"):
            base += 0.05

        return min(1.0, base)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        data = state.custom_data
        bug_info = data.get("bug_info", {})

        # Build summary
        summary_parts = [f"Bug investigation - Phase: {state.phase or 'triage'}."]
        if bug_info.get("title"):
            summary_parts.append(f"Bug: {bug_info['title']}")
        if bug_info.get("severity"):
            summary_parts.append(f"(Severity: {bug_info['severity']})")

        reproduction = data.get("reproduction", {})
        if reproduction.get("reproduced"):
            summary_parts.append("Bug reproduced successfully.")
        elif reproduction.get("steps"):
            summary_parts.append(f"Reproduction attempted with {len(reproduction['steps'])} steps.")

        hypotheses = data.get("hypotheses", [])
        active = [h for h in hypotheses if h.get("status") == "active"]
        confirmed = [h for h in hypotheses if h.get("status") == "confirmed"]
        if confirmed:
            summary_parts.append(f"Root cause confirmed: {confirmed[0].get('description', '')[:50]}")
        elif active:
            summary_parts.append(f"{len(active)} active hypotheses being investigated.")

        evidence = data.get("evidence", [])
        if evidence:
            summary_parts.append(f"Collected {len(evidence)} pieces of evidence.")

        summary_text = " ".join(summary_parts)

        # Next steps
        next_steps = []
        blocking = []

        if state.phase == "triage":
            next_steps = [
                "Document bug symptoms and affected area",
                "Determine severity and priority",
                "Identify reproduction environment"
            ]
        elif state.phase == "reproduction":
            if not reproduction.get("reproduced"):
                next_steps.append("Attempt to reproduce the bug")
                next_steps.append("Document reproduction steps")
            else:
                next_steps.append("Bug reproduced - proceed to investigation")
        elif state.phase == "investigation":
            next_steps.append("Gather evidence (logs, stack traces, code)")
            next_steps.append("Form initial hypotheses")
            if not evidence:
                blocking.append("No evidence collected yet")
        elif state.phase == "hypothesis":
            if not hypotheses:
                next_steps.append("Form hypotheses based on evidence")
            elif active:
                next_steps.append(f"Test hypothesis: {active[0].get('description', '')[:50]}")
            if not confirmed:
                blocking.append("No confirmed root cause yet")
        elif state.phase == "fix":
            root_cause = data.get("root_cause", {})
            if root_cause.get("description"):
                next_steps.append(f"Fix: {root_cause['description'][:50]}")
            next_steps.append("Implement and test the fix")
            fix = data.get("fix", {})
            if fix.get("files_changed"):
                next_steps.append(f"Modified: {', '.join(fix['files_changed'][:3])}")
        elif state.phase == "verification":
            fix = data.get("fix", {})
            if not fix.get("tested"):
                next_steps.append("Test the fix thoroughly")
            if not fix.get("regression_tests_added"):
                next_steps.append("Add regression tests")
            next_steps.append("Verify fix doesn't break existing functionality")

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

        # Collect evidence from findings
        if category == "finding":
            evidence = state.custom_data.get("evidence", [])
            evidence.append({
                "type": data.get("evidence_type", "code"),
                "source": data.get("source", ""),
                "content": data.get("description", ""),
                "timestamp": event.get("timestamp", "")
            })
            state.custom_data["evidence"] = evidence

        # Track decisions as hypotheses
        if category == "decision":
            if "hypothesis" in data.get("title", "").lower() or event_type == "hypothesis":
                hypotheses = state.custom_data.get("hypotheses", [])
                hypotheses.append({
                    "id": event.get("id", ""),
                    "description": data.get("title", "") or data.get("description", ""),
                    "status": "active",
                    "evidence_for": [],
                    "evidence_against": []
                })
                state.custom_data["hypotheses"] = hypotheses

            # Check for root cause identification
            if "root cause" in data.get("title", "").lower():
                state.custom_data["root_cause"] = {
                    "description": data.get("description", data.get("title", "")),
                    "file": data.get("file"),
                    "cause_type": data.get("cause_type", "other")
                }

        # Track file edits during fix phase
        if state.phase == "fix" and category == "tool_call":
            if data.get("tool") in ("Edit", "Write"):
                file_path = data.get("file_path", "")
                if file_path:
                    files_changed = state.custom_data.get("fix", {}).get("files_changed", [])
                    if file_path not in files_changed:
                        files_changed.append(file_path)
                        state.custom_data["fix"]["files_changed"] = files_changed

        state.progress = self.calculate_progress([], state)
        return state
