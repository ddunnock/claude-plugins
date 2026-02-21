"""Smoke tests for tpm-researcher agent and /reqdev:research command."""
from pathlib import Path


SKILL_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# tpm-researcher agent tests
# ---------------------------------------------------------------------------

class TestTpmResearcherAgent:
    def test_agent_file_exists(self):
        """Agent prompt file exists at agents/tpm-researcher.md."""
        assert (SKILL_ROOT / "agents" / "tpm-researcher.md").is_file()

    def test_agent_has_correct_name(self):
        """Agent frontmatter contains name: tpm-researcher."""
        content = (SKILL_ROOT / "agents" / "tpm-researcher.md").read_text()
        assert "name: tpm-researcher" in content

    def test_agent_specifies_sonnet_model(self):
        """Agent frontmatter specifies model: sonnet."""
        content = (SKILL_ROOT / "agents" / "tpm-researcher.md").read_text()
        assert "model: sonnet" in content

    def test_agent_references_source_tracker(self):
        """Agent prompt references source_tracker.py for source registration."""
        content = (SKILL_ROOT / "agents" / "tpm-researcher.md").read_text()
        assert "source_tracker.py" in content

    def test_agent_references_tool_detection(self):
        """Agent prompt references check_tools.py or state.json for tool detection."""
        content = (SKILL_ROOT / "agents" / "tpm-researcher.md").read_text()
        assert "check_tools.py" in content or "state.json" in content


# ---------------------------------------------------------------------------
# reqdev.research command tests
# ---------------------------------------------------------------------------

class TestReqdevResearchCommand:
    def test_command_file_exists(self):
        """Command file exists at commands/reqdev.research.md."""
        assert (SKILL_ROOT / "commands" / "reqdev.research.md").is_file()

    def test_command_references_research_workflow(self):
        """Command references tpm-researcher agent or research workflow."""
        content = (SKILL_ROOT / "commands" / "reqdev.research.md").read_text()
        assert "tpm-researcher" in content
