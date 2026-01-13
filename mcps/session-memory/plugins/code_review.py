"""Code Review session plugin.

This plugin provides structured tracking for code review sessions:
- Phase-based workflow (setup, analysis, feedback, resolution)
- File tracking with review status
- Issue discovery and categorization
- Diff analysis and comment tracking
"""

from typing import Any, Dict, List

from .base import PluginState, ResumptionContext, SessionPlugin


class CodeReviewPlugin(SessionPlugin):
    """Plugin for code review workflow sessions."""

    PHASES = [
        "setup",      # PR/commit identification, context gathering
        "analysis",   # Reading and understanding the changes
        "feedback",   # Writing review comments
        "resolution"  # Addressing feedback, re-review
    ]

    ISSUE_CATEGORIES = [
        "bug",           # Functional issues
        "security",      # Security vulnerabilities
        "performance",   # Performance concerns
        "style",         # Code style/formatting
        "architecture",  # Design/architecture issues
        "documentation", # Missing/incorrect docs
        "testing"        # Test coverage/quality
    ]

    @property
    def name(self) -> str:
        return "code-review"

    @property
    def supported_skills(self) -> List[str]:
        return ["code-review", "review-pr", "pr-review"]

    def get_state_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "enum": self.PHASES,
                    "description": "Current review phase"
                },
                "progress": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0
                },
                "custom_data": {
                    "type": "object",
                    "properties": {
                        "pr_info": {
                            "type": "object",
                            "properties": {
                                "repo": {"type": "string"},
                                "pr_number": {"type": "integer"},
                                "title": {"type": "string"},
                                "author": {"type": "string"},
                                "base_branch": {"type": "string"},
                                "head_branch": {"type": "string"}
                            }
                        },
                        "files_reviewed": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"},
                                    "status": {"type": "string", "enum": ["pending", "in_progress", "reviewed"]},
                                    "lines_changed": {"type": "integer"},
                                    "issues_found": {"type": "integer"}
                                }
                            }
                        },
                        "issues": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "category": {"type": "string", "enum": self.ISSUE_CATEGORIES},
                                    "severity": {"type": "string", "enum": ["critical", "major", "minor", "nitpick"]},
                                    "file": {"type": "string"},
                                    "line": {"type": "integer"},
                                    "description": {"type": "string"},
                                    "resolved": {"type": "boolean"}
                                }
                            }
                        },
                        "summary": {
                            "type": "object",
                            "properties": {
                                "total_files": {"type": "integer"},
                                "files_reviewed": {"type": "integer"},
                                "issues_found": {"type": "integer"},
                                "issues_resolved": {"type": "integer"},
                                "approval_status": {"type": "string", "enum": ["pending", "approved", "changes_requested", "blocked"]}
                            }
                        }
                    }
                }
            }
        }

    def create_initial_state(self) -> PluginState:
        return PluginState(
            phase="setup",
            progress=0.0,
            custom_data={
                "pr_info": {},
                "files_reviewed": [],
                "issues": [],
                "summary": {
                    "total_files": 0,
                    "files_reviewed": 0,
                    "issues_found": 0,
                    "issues_resolved": 0,
                    "approval_status": "pending"
                }
            }
        )

    def calculate_progress(self, events: List[Dict], state: PluginState) -> float:
        phase = state.phase or "setup"
        data = state.custom_data

        # Base progress from phase
        phase_weights = {
            "setup": 0.1,
            "analysis": 0.4,
            "feedback": 0.7,
            "resolution": 0.9
        }
        base = phase_weights.get(phase, 0.0)

        # Additional progress within phase
        if phase == "analysis":
            total = data.get("summary", {}).get("total_files", 0)
            reviewed = data.get("summary", {}).get("files_reviewed", 0)
            if total > 0:
                base += 0.3 * (reviewed / total)
        elif phase == "resolution":
            issues = data.get("summary", {}).get("issues_found", 0)
            resolved = data.get("summary", {}).get("issues_resolved", 0)
            if issues > 0:
                base += 0.1 * (resolved / issues)

        return min(1.0, base)

    def generate_resumption_context(
        self,
        events: List[Dict],
        state: PluginState,
        checkpoint: Dict
    ) -> ResumptionContext:
        data = state.custom_data
        summary = data.get("summary", {})
        pr_info = data.get("pr_info", {})

        # Build summary text
        pr_desc = ""
        if pr_info.get("repo"):
            pr_desc = f"PR #{pr_info.get('pr_number', '?')} in {pr_info['repo']}"
            if pr_info.get("title"):
                pr_desc += f": {pr_info['title']}"

        summary_text = f"Code review session - Phase: {state.phase or 'setup'}."
        if pr_desc:
            summary_text += f" Reviewing {pr_desc}."
        summary_text += f" Files: {summary.get('files_reviewed', 0)}/{summary.get('total_files', 0)} reviewed."
        summary_text += f" Issues: {summary.get('issues_found', 0)} found, {summary.get('issues_resolved', 0)} resolved."

        # Determine next steps based on phase
        next_steps = []
        blocking = []

        if state.phase == "setup":
            next_steps = [
                "Identify the PR/commit to review",
                "Gather context about the changes",
                "List files to be reviewed"
            ]
        elif state.phase == "analysis":
            files = data.get("files_reviewed", [])
            pending = [f for f in files if f.get("status") != "reviewed"]
            if pending:
                next_steps.append(f"Continue reviewing {len(pending)} remaining files")
                next_steps.append(f"Next file: {pending[0].get('path', 'unknown')}")
            else:
                next_steps.append("All files reviewed - proceed to feedback phase")
        elif state.phase == "feedback":
            issues = [i for i in data.get("issues", []) if not i.get("resolved")]
            if issues:
                next_steps.append(f"Document {len(issues)} issues as review comments")
            next_steps.append("Prepare final review decision")
        elif state.phase == "resolution":
            issues = [i for i in data.get("issues", []) if not i.get("resolved")]
            if issues:
                blocking.append(f"{len(issues)} issues still need resolution")
                for issue in issues[:3]:
                    blocking.append(f"- {issue.get('category', 'issue')}: {issue.get('description', '')[:50]}")
            next_steps.append("Verify all issues are addressed")
            next_steps.append("Make final approval decision")

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

        # Track phase changes
        if category == "phase":
            new_phase = data.get("name") or data.get("phase")
            if new_phase and new_phase in self.PHASES:
                state.phase = new_phase

        # Track file reads during analysis
        if category == "tool_call" and data.get("tool") == "Read":
            file_path = data.get("file_path", "")
            if file_path and state.phase in ("analysis", "setup"):
                files = state.custom_data.get("files_reviewed", [])
                existing = next((f for f in files if f["path"] == file_path), None)
                if not existing:
                    files.append({
                        "path": file_path,
                        "status": "in_progress",
                        "lines_changed": 0,
                        "issues_found": 0
                    })
                    state.custom_data["files_reviewed"] = files
                    state.custom_data["summary"]["total_files"] = len(files)

        # Track findings as issues
        if category == "finding":
            issues = state.custom_data.get("issues", [])
            issue_category = data.get("category", "bug")
            if issue_category in self.ISSUE_CATEGORIES:
                issues.append({
                    "id": event.get("id", ""),
                    "category": issue_category,
                    "severity": data.get("severity", "minor"),
                    "file": data.get("file", ""),
                    "line": data.get("line"),
                    "description": data.get("description", ""),
                    "resolved": False
                })
                state.custom_data["issues"] = issues
                state.custom_data["summary"]["issues_found"] = len(issues)

        # Update progress
        state.progress = self.calculate_progress([], state)

        return state
