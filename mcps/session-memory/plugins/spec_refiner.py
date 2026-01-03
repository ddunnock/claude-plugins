"""Specification Refiner plugin for session memory."""

from typing import Any, Dict, List

from .base import SessionPlugin, PluginState, ResumptionContext


class SpecRefinerState(PluginState):
    """Specification Refiner state."""

    PHASES = ["ASSESS", "INGEST", "ANALYZE", "PRESENT", "ITERATE", "SYNTHESIZE", "OUTPUT"]

    def __init__(
        self,
        phase: str = None,
        progress: float = 0.0,
        custom_data: Dict[str, Any] = None
    ):
        super().__init__(phase, progress, custom_data or {})
        # Initialize spec-refiner-specific fields
        if "mode" not in self.custom_data:
            self.custom_data["mode"] = None  # SIMPLE or COMPLEX
        if "iteration" not in self.custom_data:
            self.custom_data["iteration"] = 0
        if "open_questions" not in self.custom_data:
            self.custom_data["open_questions"] = []
        if "answered_questions" not in self.custom_data:
            self.custom_data["answered_questions"] = []
        if "deferred_questions" not in self.custom_data:
            self.custom_data["deferred_questions"] = []
        if "findings" not in self.custom_data:
            self.custom_data["findings"] = {"critical": [], "high": [], "medium": [], "low": []}
        if "resolved_findings" not in self.custom_data:
            self.custom_data["resolved_findings"] = []
        if "assumptions" not in self.custom_data:
            self.custom_data["assumptions"] = []

    @property
    def mode(self) -> str:
        return self.custom_data.get("mode")

    @mode.setter
    def mode(self, value: str):
        self.custom_data["mode"] = value

    @property
    def iteration(self) -> int:
        return self.custom_data.get("iteration", 0)

    @property
    def open_questions(self) -> List[Dict]:
        return self.custom_data.get("open_questions", [])

    @property
    def findings(self) -> Dict[str, List]:
        return self.custom_data.get("findings", {})

    @property
    def assumptions(self) -> List[Dict]:
        return self.custom_data.get("assumptions", [])


class SpecRefinerPlugin(SessionPlugin):
    """Plugin for specification-refiner skill."""

    PHASES = ["ASSESS", "INGEST", "ANALYZE", "PRESENT", "ITERATE", "SYNTHESIZE", "OUTPUT"]

    @property
    def name(self) -> str:
        return "spec-refiner"

    @property
    def supported_skills(self) -> List[str]:
        return ["specification-refiner", "spec-refiner"]

    def get_state_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "phase": {"type": "string", "enum": self.PHASES},
                "mode": {"type": "string", "enum": ["SIMPLE", "COMPLEX"]},
                "iteration": {"type": "integer"},
                "open_questions": {"type": "array"},
                "answered_questions": {"type": "array"},
                "deferred_questions": {"type": "array"},
                "findings": {
                    "type": "object",
                    "properties": {
                        "critical": {"type": "array"},
                        "high": {"type": "array"},
                        "medium": {"type": "array"},
                        "low": {"type": "array"}
                    }
                },
                "resolved_findings": {"type": "array"},
                "assumptions": {"type": "array"},
                "progress": {"type": "number"}
            }
        }

    def create_initial_state(self) -> PluginState:
        """Create SpecRefiner-specific initial state."""
        return SpecRefinerState()

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        """Calculate progress based on current phase."""
        phase = state.phase
        if not phase:
            return 0.0

        try:
            phase_idx = self.PHASES.index(phase)
            # Base progress from phase
            base = (phase_idx + 1) / len(self.PHASES)

            # Adjust based on questions answered
            open_q = len(state.custom_data.get("open_questions", []))
            answered_q = len(state.custom_data.get("answered_questions", []))
            total_q = open_q + answered_q

            if total_q > 0:
                q_factor = answered_q / total_q
                # Questions progress can boost up to 10%
                base = min(0.95, base + q_factor * 0.1)

            return round(base, 2)
        except ValueError:
            return 0.0

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        """Generate SpecRefiner-specific resumption context."""

        mode = state.custom_data.get("mode", "unknown")
        phase = state.phase or "unknown"
        iteration = state.custom_data.get("iteration", 0)

        # Count findings
        findings = state.custom_data.get("findings", {})
        total_findings = sum(len(v) for v in findings.values())
        critical_findings = len(findings.get("critical", []))

        # Count questions
        open_q = len(state.custom_data.get("open_questions", []))
        answered_q = len(state.custom_data.get("answered_questions", []))
        deferred_q = len(state.custom_data.get("deferred_questions", []))

        # Build summary
        summary_parts = [
            f"Spec Refiner in {mode} mode",
            f"Phase: {phase}",
            f"Iteration: {iteration}"
        ]

        if total_findings > 0:
            summary_parts.append(f"{total_findings} findings ({critical_findings} critical)")

        if open_q > 0:
            summary_parts.append(f"{open_q} open questions")

        # Determine next steps based on phase
        next_steps = []
        blocking_items = []

        if phase == "ASSESS":
            next_steps.append("Complete initial assessment and determine mode")
        elif phase == "INGEST":
            next_steps.append("Review document ingestion and confirm understanding")
        elif phase == "ANALYZE":
            next_steps.append("Continue analysis - run SEAMS framework")
            if mode == "COMPLEX":
                next_steps.append("Run Critical Path analysis")
        elif phase == "PRESENT":
            if open_q > 0:
                next_steps.append(f"Answer {open_q} open questions")
                blocking_items.extend([
                    q.get("question", "") for q in state.custom_data.get("open_questions", [])[:3]
                ])
            next_steps.append("Review findings with user")
        elif phase == "ITERATE":
            next_steps.append("Process user feedback and re-analyze if needed")
        elif phase == "SYNTHESIZE":
            next_steps.append("Finalize analysis and prepare for output")
            if critical_findings > 0:
                next_steps.append(f"Resolve {critical_findings} critical findings first")
                blocking_items.append(f"{critical_findings} critical findings unresolved")
        elif phase == "OUTPUT":
            next_steps.append("Generate refined specification output")

        return ResumptionContext(
            summary=". ".join(summary_parts),
            next_steps=next_steps,
            blocking_items=blocking_items,
            state=state
        )

    def on_event(self, event: Dict, state: PluginState) -> PluginState:
        """Track phase transitions, findings, and questions."""

        # Ensure we have SpecRefiner state structure
        if "mode" not in state.custom_data:
            state = SpecRefinerState(
                phase=state.phase,
                progress=state.progress,
                custom_data=state.custom_data
            )

        category = event.get("category", "")
        event_type = event.get("type", "")
        data = event.get("data", {})

        # Track phase transitions
        if category == "phase":
            if event_type == "phase_start":
                state.phase = data.get("phase", state.phase)
            elif event_type == "mode_selected":
                state.custom_data["mode"] = data.get("mode")
            elif event_type == "iteration_start":
                state.custom_data["iteration"] = \
                    state.custom_data.get("iteration", 0) + 1

        # Track questions
        if category == "question":
            question_data = {
                "id": data.get("id"),
                "question": data.get("question"),
                "category": data.get("category"),
                "raised_in": state.phase,
                "blocks": data.get("blocks", [])
            }

            if event_type == "question_raised":
                open_q = state.custom_data.get("open_questions", [])
                open_q.append(question_data)
                state.custom_data["open_questions"] = open_q

            elif event_type == "question_answered":
                # Move from open to answered
                open_q = state.custom_data.get("open_questions", [])
                answered_q = state.custom_data.get("answered_questions", [])

                # Find and remove from open
                question_id = data.get("id")
                open_q = [q for q in open_q if q.get("id") != question_id]

                # Add to answered with answer
                question_data["answer"] = data.get("answer")
                question_data["answered_in"] = state.phase
                answered_q.append(question_data)

                state.custom_data["open_questions"] = open_q
                state.custom_data["answered_questions"] = answered_q

            elif event_type == "question_deferred":
                open_q = state.custom_data.get("open_questions", [])
                deferred_q = state.custom_data.get("deferred_questions", [])

                question_id = data.get("id")
                open_q = [q for q in open_q if q.get("id") != question_id]

                question_data["deferred_reason"] = data.get("reason")
                question_data["revisit_when"] = data.get("revisit_when")
                deferred_q.append(question_data)

                state.custom_data["open_questions"] = open_q
                state.custom_data["deferred_questions"] = deferred_q

        # Track findings
        if category == "finding":
            severity = data.get("severity", "medium").lower()
            finding_data = {
                "id": data.get("id"),
                "description": data.get("description"),
                "evidence": data.get("evidence"),
                "remediation": data.get("remediation"),
                "raised_in": state.phase
            }

            if event_type == "finding_raised":
                findings = state.custom_data.get("findings", {
                    "critical": [], "high": [], "medium": [], "low": []
                })
                if severity in findings:
                    findings[severity].append(finding_data)
                state.custom_data["findings"] = findings

            elif event_type == "finding_resolved":
                findings = state.custom_data.get("findings", {})
                resolved = state.custom_data.get("resolved_findings", [])

                # Find and remove from active findings
                finding_id = data.get("id")
                for sev in findings:
                    findings[sev] = [f for f in findings[sev] if f.get("id") != finding_id]

                finding_data["resolution"] = data.get("resolution")
                finding_data["resolved_in"] = state.phase
                resolved.append(finding_data)

                state.custom_data["findings"] = findings
                state.custom_data["resolved_findings"] = resolved

        # Track assumptions
        if category == "assumption":
            assumption_data = {
                "id": data.get("id"),
                "assumption": data.get("assumption"),
                "category": data.get("category"),
                "validation_method": data.get("validation_method"),
                "risk_if_false": data.get("risk_if_false"),
                "status": data.get("status", "unvalidated"),
                "raised_in": state.phase
            }

            if event_type == "assumption_recorded":
                assumptions = state.custom_data.get("assumptions", [])
                assumptions.append(assumption_data)
                state.custom_data["assumptions"] = assumptions

            elif event_type == "assumption_validated":
                assumptions = state.custom_data.get("assumptions", [])
                assumption_id = data.get("id")
                for a in assumptions:
                    if a.get("id") == assumption_id:
                        a["status"] = "validated"
                        a["validation_result"] = data.get("result")
                state.custom_data["assumptions"] = assumptions

        # Update progress
        state.progress = self.calculate_progress([], state)

        return state
