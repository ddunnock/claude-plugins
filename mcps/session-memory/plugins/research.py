"""Research and Exploration session plugin.

This plugin provides structured tracking for research sessions:
- Phase-based workflow (scoping, gathering, analysis, synthesis, documentation)
- Source tracking and citation management
- Findings accumulation and categorization
- Knowledge synthesis and report generation
"""

from typing import Any, Dict, List

from .base import PluginState, ResumptionContext, SessionPlugin


class ResearchPlugin(SessionPlugin):
    """Plugin for research and exploration sessions."""

    PHASES = [
        "scoping",       # Define research questions
        "gathering",     # Collect information from sources
        "analysis",      # Analyze and evaluate findings
        "synthesis",     # Combine findings into insights
        "documentation"  # Write up results
    ]

    SOURCE_TYPES = [
        "documentation",  # Official docs
        "code",          # Source code analysis
        "article",       # Blog posts, articles
        "paper",         # Academic papers
        "discussion",    # Forums, issues, discussions
        "experiment",    # Personal testing/experimentation
        "expert"         # Expert knowledge/interview
    ]

    @property
    def name(self) -> str:
        return "research"

    @property
    def supported_skills(self) -> List[str]:
        return ["research", "explore", "investigation", "deep-dive", "analysis"]

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
                        "research_topic": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "questions": {"type": "array", "items": {"type": "string"}},
                                "scope": {"type": "string"},
                                "constraints": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "sources": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string", "enum": self.SOURCE_TYPES},
                                    "title": {"type": "string"},
                                    "url": {"type": "string"},
                                    "path": {"type": "string"},
                                    "relevance": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "notes": {"type": "string"}
                                }
                            }
                        },
                        "findings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "category": {"type": "string"},
                                    "description": {"type": "string"},
                                    "source_ids": {"type": "array", "items": {"type": "string"}},
                                    "confidence": {"type": "string", "enum": ["high", "medium", "low", "uncertain"]},
                                    "tags": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        },
                        "questions_answered": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "answer": {"type": "string"},
                                    "finding_ids": {"type": "array", "items": {"type": "string"}},
                                    "confidence": {"type": "string"}
                                }
                            }
                        },
                        "open_questions": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "synthesis": {
                            "type": "object",
                            "properties": {
                                "key_insights": {"type": "array", "items": {"type": "string"}},
                                "recommendations": {"type": "array", "items": {"type": "string"}},
                                "gaps": {"type": "array", "items": {"type": "string"}},
                                "next_steps": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        return PluginState(
            phase="scoping",
            progress=0.0,
            custom_data={
                "research_topic": {
                    "questions": [],
                    "constraints": []
                },
                "sources": [],
                "findings": [],
                "questions_answered": [],
                "open_questions": [],
                "synthesis": {
                    "key_insights": [],
                    "recommendations": [],
                    "gaps": [],
                    "next_steps": []
                }
            }
        )

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        phase = state.phase or "scoping"
        data = state.custom_data

        phase_weights = {
            "scoping": 0.1,
            "gathering": 0.3,
            "analysis": 0.5,
            "synthesis": 0.75,
            "documentation": 0.9
        }
        base = phase_weights.get(phase, 0.0)

        # Question-based progress
        topic = data.get("research_topic", {})
        questions = topic.get("questions", [])
        answered = data.get("questions_answered", [])

        if questions and phase in ("analysis", "synthesis"):
            answer_ratio = len(answered) / len(questions)
            base += 0.2 * answer_ratio

        # Source diversity bonus
        sources = data.get("sources", [])
        if len(sources) >= 3:
            base += 0.05
        if len(sources) >= 5:
            base += 0.05

        return min(1.0, base)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        data = state.custom_data
        topic = data.get("research_topic", {})

        # Build summary
        summary_parts = [f"Research session - Phase: {state.phase or 'scoping'}."]
        if topic.get("title"):
            summary_parts.append(f"Topic: {topic['title']}")

        sources = data.get("sources", [])
        findings = data.get("findings", [])
        answered = data.get("questions_answered", [])
        questions = topic.get("questions", [])

        summary_parts.append(f"Sources: {len(sources)}.")
        summary_parts.append(f"Findings: {len(findings)}.")
        if questions:
            summary_parts.append(f"Questions: {len(answered)}/{len(questions)} answered.")

        summary_text = " ".join(summary_parts)

        # Next steps
        next_steps = []
        blocking = []

        if state.phase == "scoping":
            if not topic.get("title"):
                next_steps.append("Define research topic and objectives")
            if not questions:
                next_steps.append("Formulate research questions")
            next_steps.append("Identify scope and constraints")
        elif state.phase == "gathering":
            next_steps.append("Search for relevant sources")
            open_q = data.get("open_questions", [])
            if open_q:
                next_steps.append(f"Investigate: {open_q[0][:50]}")
            if not sources:
                blocking.append("No sources collected yet")
        elif state.phase == "analysis":
            unanswered = [q for q in questions if q not in [a.get("question") for a in answered]]
            if unanswered:
                next_steps.append(f"Answer: {unanswered[0][:50]}")
            next_steps.append("Evaluate source reliability")
            next_steps.append("Categorize and tag findings")
        elif state.phase == "synthesis":
            synthesis = data.get("synthesis", {})
            if not synthesis.get("key_insights"):
                next_steps.append("Extract key insights from findings")
            next_steps.append("Identify patterns across sources")
            next_steps.append("Formulate recommendations")
            gaps = synthesis.get("gaps", [])
            for gap in gaps[:2]:
                blocking.append(f"Knowledge gap: {gap[:50]}")
        elif state.phase == "documentation":
            next_steps = [
                "Write executive summary",
                "Document methodology and sources",
                "Present findings and recommendations",
                "Note limitations and future work"
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

        # Track sources from web fetches and file reads
        if category == "tool_call":
            tool = data.get("tool", "")
            sources = state.custom_data.get("sources", [])

            if tool == "WebFetch":
                url = data.get("url", "")
                if url:
                    sources.append({
                        "id": event.get("id", ""),
                        "type": "article",
                        "url": url,
                        "relevance": "medium",
                        "notes": ""
                    })

            elif tool == "Read":
                path = data.get("file_path", "")
                if path:
                    # Determine source type from path
                    source_type = "code"
                    if any(ext in path for ext in [".md", ".txt", ".rst"]):
                        source_type = "documentation"

                    sources.append({
                        "id": event.get("id", ""),
                        "type": source_type,
                        "path": path,
                        "relevance": "medium",
                        "notes": ""
                    })

            state.custom_data["sources"] = sources

        # Track findings
        if category == "finding":
            findings = state.custom_data.get("findings", [])
            findings.append({
                "id": event.get("id", ""),
                "category": data.get("category", "general"),
                "description": data.get("description", ""),
                "source_ids": data.get("sources", []),
                "confidence": data.get("confidence", "medium"),
                "tags": data.get("tags", [])
            })
            state.custom_data["findings"] = findings

        # Track questions
        if category == "question":
            if data.get("answered"):
                answered = state.custom_data.get("questions_answered", [])
                answered.append({
                    "question": data.get("question", ""),
                    "answer": data.get("answer", ""),
                    "confidence": data.get("confidence", "medium")
                })
                state.custom_data["questions_answered"] = answered
            else:
                open_q = state.custom_data.get("open_questions", [])
                question = data.get("question", "")
                if question and question not in open_q:
                    open_q.append(question)
                state.custom_data["open_questions"] = open_q

        state.progress = self.calculate_progress([], state)
        return state
