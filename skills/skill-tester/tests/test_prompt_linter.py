"""Tests for prompt_linter.py — deterministic prompt quality linter.

Covers:
  1. INTERACTION checks (AskUserQuestion completeness)
  2. DEAD_COLLECT checks (unused collected inputs)
  3. AGENT_USAGE checks (definition/invocation consistency)
  4. WORKFLOW checks (phase integrity, gates, branches)
  5. REFERENCE checks (file paths exist on disk)
  6. CONTEXT_READ checks (agent files read SKILL.md)
  7. Integration tests (run_lint end-to-end)
  8. Security tests (path traversal)
  9. Edge cases
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from prompt_linter import (
    check_interaction,
    check_dead_collect,
    check_agent_usage,
    check_workflow,
    check_references,
    check_context_reads,
    run_lint,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_skill(tmp_path, files: dict) -> Path:
    """Create a temp skill directory with given files."""
    skill = tmp_path / "test-skill"
    skill.mkdir(exist_ok=True)
    for rel, content in files.items():
        fpath = skill / rel
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    return skill


MINIMAL_SKILL_MD = """---
name: test-skill
version: 1.0.0
---

# Test Skill

<security>
  <rule name="test">Test rule</rule>
</security>

<paths>
  <pattern name="script">python3 ${CLAUDE_PLUGIN_ROOT}/scripts/example.py</pattern>
</paths>

<workflow>
  <phase name="intake" sequence="1">
    <objective>Collect inputs.</objective>
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>What mode?</question>
        <header>Analysis Mode</header>
        <options>["Full", "Audit"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
  </phase>
  <phase name="run" sequence="2" depends-on="intake">
    <objective>Run analysis.</objective>
    <step sequence="2.1">
      <branch condition="mode is Audit">Skip execution.</branch>
    </step>
  </phase>
</workflow>

<behavior>
  <rule id="B1" priority="high">Test rule</rule>
</behavior>

<agents>
  <agent name="test-agent" ref="${CLAUDE_PLUGIN_ROOT}/agents/test_agent.md" model="claude-sonnet-4-6">
    <purpose>Test agent</purpose>
  </agent>
</agents>
"""


# ---------------------------------------------------------------------------
# Check 1: INTERACTION
# ---------------------------------------------------------------------------

class TestInteraction:
    def test_complete_auq_no_findings(self, tmp_path):
        """Complete AskUserQuestion block produces no findings."""
        skill = _make_skill(tmp_path, {"SKILL.md": MINIMAL_SKILL_MD})
        findings = check_interaction(skill, MINIMAL_SKILL_MD)
        assert len(findings) == 0

    def test_prose_ask_without_interaction(self, tmp_path):
        """Prose 'ask the user' without <interaction> block is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      Ask the user which mode they want to use.
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_interaction(skill, md)
        assert any(f["check_id"] == "PL-ask-no-tool" for f in findings)

    def test_interaction_missing_tool_attr(self, tmp_path):
        """<interaction> without tool="AskUserQuestion" is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction>
        <question>What?</question>
        <header>Test</header>
        <options>["A", "B"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_interaction(skill, md)
        assert any(f["check_id"] == "PL-interaction-no-tool" for f in findings)

    def test_auq_missing_fields(self, tmp_path):
        """AskUserQuestion block missing required fields is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>What?</question>
      </interaction>
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_interaction(skill, md)
        assert any(f["check_id"] == "PL-auq-missing-field" for f in findings)
        # Should report header, options, multiSelect as missing
        missing_finding = [f for f in findings if f["check_id"] == "PL-auq-missing-field"][0]
        assert "header" in missing_finding["message"]

    def test_auq_single_option_warned(self, tmp_path):
        """AskUserQuestion with fewer than 2 options is warned."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>Continue?</question>
        <header>Confirm</header>
        <options>["Yes"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_interaction(skill, md)
        assert any(f["check_id"] == "PL-auq-few-options" for f in findings)


# ---------------------------------------------------------------------------
# Check 2: DEAD_COLLECT
# ---------------------------------------------------------------------------

class TestDeadCollect:
    def test_used_input_no_finding(self, tmp_path):
        """Input used downstream produces no dead-collect finding."""
        findings = check_dead_collect(MINIMAL_SKILL_MD)
        dead = [f for f in findings if f["check_id"] == "PL-dead-collect"]
        assert len(dead) == 0

    def test_unused_input_flagged(self, tmp_path):
        """Input collected but never referenced downstream is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>What color?</question>
        <header>Favorite Color</header>
        <options>["Red", "Blue"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
  </phase>
  <phase name="run" sequence="2" depends-on="intake">
    <objective>Do something unrelated.</objective>
  </phase>
</workflow>
"""
        findings = check_dead_collect(md)
        assert any(f["check_id"] == "PL-dead-collect" for f in findings)

    def test_mode_collected_but_no_branch(self, tmp_path):
        """Mode collected but no branch condition referencing it."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>Which mode?</question>
        <header>Analysis Mode</header>
        <options>["Full", "Audit"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
  </phase>
  <phase name="run" sequence="2" depends-on="intake">
    <objective>Always do everything.</objective>
  </phase>
</workflow>
"""
        findings = check_dead_collect(md)
        assert any(f["check_id"] == "PL-mode-no-branch" for f in findings)


# ---------------------------------------------------------------------------
# Check 3: AGENT_USAGE
# ---------------------------------------------------------------------------

class TestAgentUsage:
    def test_consistent_agent_no_findings(self, tmp_path):
        """Agent defined and invoked produces no findings."""
        md = """---
name: test
---
<workflow>
  <phase name="review" sequence="1">
    <step sequence="1.1">
      Invoke the test-agent agent.
    </step>
  </phase>
</workflow>
<agents>
  <agent name="test-agent" ref="${CLAUDE_PLUGIN_ROOT}/agents/test_agent.md" model="claude-sonnet-4-6">
    <purpose>Test</purpose>
  </agent>
</agents>
"""
        skill = _make_skill(tmp_path, {
            "SKILL.md": md,
            "agents/test_agent.md": "---\nname: test-agent\n---\nTest agent.",
        })
        findings = check_agent_usage(skill, md)
        dead = [f for f in findings if f["check_id"] == "PL-agent-dead"]
        undefined = [f for f in findings if f["check_id"] == "PL-agent-undefined"]
        missing_file = [f for f in findings if f["check_id"] == "PL-agent-file-missing"]
        assert len(dead) == 0
        assert len(undefined) == 0
        assert len(missing_file) == 0

    def test_defined_but_not_invoked(self, tmp_path):
        """Agent defined but never invoked in workflow is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1">
    <step sequence="1.1">Do nothing with agents.</step>
  </phase>
</workflow>
<agents>
  <agent name="orphan-agent" ref="${CLAUDE_PLUGIN_ROOT}/agents/orphan.md" model="claude-sonnet-4-6">
    <purpose>Never used</purpose>
  </agent>
</agents>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md, "agents/orphan.md": "test"})
        findings = check_agent_usage(skill, md)
        assert any(f["check_id"] == "PL-agent-dead" for f in findings)

    def test_invoked_but_not_defined(self, tmp_path):
        """Agent invoked in workflow but not in <agents> block is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="review" sequence="1">
    <step sequence="1.1">Invoke the ghost-agent agent.</step>
  </phase>
</workflow>
<agents>
</agents>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_agent_usage(skill, md)
        assert any(f["check_id"] == "PL-agent-undefined" for f in findings)

    def test_agent_file_missing_on_disk(self, tmp_path):
        """Agent ref path that doesn't exist on disk is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="review" sequence="1">
    <step sequence="1.1">Invoke the missing-agent agent.</step>
  </phase>
</workflow>
<agents>
  <agent name="missing-agent" ref="${CLAUDE_PLUGIN_ROOT}/agents/does_not_exist.md" model="claude-sonnet-4-6">
    <purpose>File missing</purpose>
  </agent>
</agents>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_agent_usage(skill, md)
        assert any(f["check_id"] == "PL-agent-file-missing" for f in findings)


# ---------------------------------------------------------------------------
# Check 4: WORKFLOW
# ---------------------------------------------------------------------------

class TestWorkflow:
    def test_valid_workflow_no_findings(self, tmp_path):
        """Valid workflow produces no findings."""
        findings = check_workflow(MINIMAL_SKILL_MD)
        assert len(findings) == 0

    def test_depends_on_missing_phase(self, tmp_path):
        """depends-on referencing non-existent phase is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1" depends-on="nonexistent">
    <objective>Test</objective>
  </phase>
</workflow>
"""
        findings = check_workflow(md)
        assert any(f["check_id"] == "PL-depends-missing" for f in findings)

    def test_branch_no_condition(self, tmp_path):
        """<branch> without condition attribute is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1">
    <step sequence="1.1">
      <branch>Skip this.</branch>
    </step>
  </phase>
</workflow>
"""
        findings = check_workflow(md)
        assert any(f["check_id"] == "PL-branch-no-condition" for f in findings)

    def test_branch_empty_condition(self, tmp_path):
        """<branch condition=""> is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1">
    <step sequence="1.1">
      <branch condition="">Skip this.</branch>
    </step>
  </phase>
</workflow>
"""
        findings = check_workflow(md)
        assert any(f["check_id"] == "PL-branch-empty-condition" for f in findings)

    def test_no_workflow_block(self, tmp_path):
        """Missing <workflow> block entirely is flagged."""
        md = "---\nname: test\n---\n# No workflow here.\n"
        findings = check_workflow(md)
        assert any(f["check_id"] == "PL-no-workflow" for f in findings)


# ---------------------------------------------------------------------------
# Check 5: REFERENCE
# ---------------------------------------------------------------------------

class TestReferences:
    def test_existing_script_no_finding(self, tmp_path):
        """Script that exists on disk produces no findings."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1">
    <step sequence="1.1">
      <script>${CLAUDE_PLUGIN_ROOT}/scripts/example.py --help</script>
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {
            "SKILL.md": md,
            "scripts/example.py": "print('hi')\n",
        })
        findings = check_references(skill, md)
        assert len([f for f in findings if f["check_id"] == "PL-script-missing"]) == 0

    def test_missing_script_flagged(self, tmp_path):
        """Script referenced in workflow but missing on disk is flagged."""
        md = ("---\nname: test\n---\n"
              "<workflow>\n"
              "  <phase name=\"run\" sequence=\"1\">\n"
              "    <step sequence=\"1.1\">\n"
              "<script>${CLAUDE_PLUGIN_ROOT}/scripts/ghost.py</script>\n"
              "    </step>\n"
              "  </phase>\n"
              "</workflow>\n")
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_references(skill, md)
        assert any(f["check_id"] == "PL-script-missing" for f in findings)

    def test_missing_reference_file_flagged(self, tmp_path):
        """Reference in <references> block that doesn't exist is flagged."""
        md = """---
name: test
---
<workflow>
  <phase name="run" sequence="1"><objective>Test</objective></phase>
</workflow>
<references>
  <file path="${CLAUDE_PLUGIN_ROOT}/references/nonexistent.md" load-when="always"/>
</references>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_references(skill, md)
        assert any(f["check_id"] == "PL-ref-missing" for f in findings)


# ---------------------------------------------------------------------------
# Check 6: CONTEXT_READ
# ---------------------------------------------------------------------------

class TestContextReads:
    def test_agent_with_context_no_findings(self, tmp_path):
        """Agent with proper <context><read> of SKILL.md produces no findings."""
        skill = _make_skill(tmp_path, {
            "agents/good.md": '---\nname: good\n---\n\n<context>\n  <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>\n</context>\n\nInstructions.',
        })
        findings = check_context_reads(skill)
        error_findings = [f for f in findings if f["severity"] == "ERROR"]
        assert len(error_findings) == 0

    def test_agent_no_context_block(self, tmp_path):
        """Agent file without <context> block is flagged."""
        skill = _make_skill(tmp_path, {
            "agents/bad.md": "---\nname: bad\n---\n\nNo context block here.",
        })
        findings = check_context_reads(skill)
        assert any(f["check_id"] == "PL-no-context" for f in findings)

    def test_agent_context_but_no_skill_md_read(self, tmp_path):
        """Agent with <context> but no SKILL.md read is flagged."""
        skill = _make_skill(tmp_path, {
            "agents/partial.md": '---\nname: partial\n---\n\n<context>\n  <read required="true">${CLAUDE_PLUGIN_ROOT}/references/other.md</read>\n</context>\n',
        })
        findings = check_context_reads(skill)
        assert any(f["check_id"] == "PL-context-no-skillmd" for f in findings)


# ---------------------------------------------------------------------------
# Integration: run_lint
# ---------------------------------------------------------------------------

class TestRunLint:
    def test_run_lint_writes_output(self, tmp_path):
        """run_lint writes prompt_lint.json to session dir."""
        skill = _make_skill(tmp_path, {
            "SKILL.md": MINIMAL_SKILL_MD,
            "agents/test_agent.md": '---\nname: test-agent\n---\n\n<context>\n  <read required="true">${CLAUDE_PLUGIN_ROOT}/SKILL.md</read>\n</context>\n',
        })
        session = tmp_path / "session"
        session.mkdir()
        result = run_lint(str(skill), str(session))

        output = session / "prompt_lint.json"
        assert output.exists()
        loaded = json.loads(output.read_text())
        assert "findings" in loaded
        assert "summary" in loaded
        assert loaded["summary"]["overall"] in ("PASS", "WARN", "FAIL")

    def test_run_lint_has_files_analyzed(self, tmp_path):
        """run_lint result includes list of files analyzed."""
        skill = _make_skill(tmp_path, {"SKILL.md": MINIMAL_SKILL_MD})
        session = tmp_path / "session"
        session.mkdir()
        result = run_lint(str(skill), str(session))
        assert "SKILL.md" in result["files_analyzed"]

    def test_run_lint_rejects_traversal(self, tmp_path):
        """run_lint rejects paths with '..' traversal."""
        session = tmp_path / "session"
        session.mkdir()
        with pytest.raises(ValueError, match="traversal"):
            run_lint("../../../etc", str(session))

    def test_run_lint_rejects_nonexistent(self, tmp_path):
        """run_lint raises FileNotFoundError for missing path."""
        session = tmp_path / "session"
        session.mkdir()
        with pytest.raises(FileNotFoundError):
            run_lint("/nonexistent/path", str(session))

    def test_run_lint_missing_skill_md(self, tmp_path):
        """run_lint handles skill dir with no SKILL.md."""
        skill = _make_skill(tmp_path, {"README.md": "# Not a skill"})
        session = tmp_path / "session"
        session.mkdir()
        result = run_lint(str(skill), str(session))
        assert result["summary"]["overall"] == "FAIL"
        assert any("PL-no-skill-md" in f["check_id"] for f in result["findings"])


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_skill_md_content(self, tmp_path):
        """Empty SKILL.md produces appropriate findings."""
        skill = _make_skill(tmp_path, {"SKILL.md": ""})
        session = tmp_path / "session"
        session.mkdir()
        result = run_lint(str(skill), str(session))
        assert result["summary"]["overall"] == "FAIL"

    def test_skill_md_no_workflow_no_agents(self, tmp_path):
        """SKILL.md with no workflow or agents."""
        md = "---\nname: bare\n---\n# Bare skill with nothing.\n"
        findings = check_workflow(md)
        assert any(f["check_id"] == "PL-no-workflow" for f in findings)

    def test_multiple_auq_blocks(self, tmp_path):
        """Multiple AskUserQuestion blocks are all checked."""
        md = """---
name: test
---
<workflow>
  <phase name="intake" sequence="1">
    <step sequence="1.1">
      <interaction tool="AskUserQuestion">
        <question>Q1?</question>
        <header>H1</header>
        <options>["A", "B"]</options>
        <multiSelect>false</multiSelect>
      </interaction>
    </step>
    <step sequence="1.2">
      <interaction tool="AskUserQuestion">
        <question>Q2?</question>
      </interaction>
    </step>
  </phase>
</workflow>
"""
        skill = _make_skill(tmp_path, {"SKILL.md": md})
        findings = check_interaction(skill, md)
        # Second block missing header, options, multiSelect
        missing = [f for f in findings if f["check_id"] == "PL-auq-missing-field"]
        assert len(missing) >= 1
