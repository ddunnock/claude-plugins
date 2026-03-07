#!/usr/bin/env python3
"""test_validate_skill.py — Unit and security tests for validate_skill.py.

Tests cover:
  - Secret pattern detection
  - Anti-pattern detection
  - Structural validation
  - Path traversal rejection
  - Edge cases (empty skill, no scripts, missing files)
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts dir to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from validate_skill import (
    check_anti_patterns,
    check_secrets,
    check_structure,
    run_scan,
)


def _make_skill(files: dict) -> Path:
    """Create a temporary skill directory with specified files.

    Args:
        files: Dict mapping relative path strings to file content strings.

    Returns:
        Path to the created temporary directory.
    """
    tmp = Path(tempfile.mkdtemp())
    for rel_path, content in files.items():
        fpath = tmp / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    return tmp


class TestSecretDetection(unittest.TestCase):
    """Tests for check_secrets()."""

    def test_detects_anthropic_key(self):
        """Should detect hardcoded Anthropic API key pattern."""
        skill = _make_skill({"scripts/foo.py": 'API_KEY = "sk-ant-api03-abcdefghijklmnopqrst"\n'})
        findings = check_secrets(skill)
        self.assertTrue(any(f["severity"] == "CRITICAL" for f in findings))

    def test_no_false_positive_env_var(self):
        """Should NOT flag os.environ.get('ANTHROPIC_API_KEY')."""
        skill = _make_skill({
            "scripts/foo.py": 'key = os.environ.get("ANTHROPIC_API_KEY")\n'
        })
        findings = check_secrets(skill)
        secret_findings = [f for f in findings if f["category"] == "SECRETS"]
        self.assertEqual(len(secret_findings), 0)

    def test_no_false_positive_placeholder(self):
        """Should NOT flag placeholder values in comments."""
        skill = _make_skill({
            "scripts/foo.py": '# Replace YOUR_KEY_HERE with your actual key\n'
        })
        findings = check_secrets(skill)
        self.assertEqual(len(findings), 0)

    def test_detects_aws_access_key(self):
        """Should detect AWS access key ID pattern."""
        skill = _make_skill({"scripts/foo.py": 'aws_key = "AKIAIOSFODNN7EXAMPLE"\n'})
        findings = check_secrets(skill)
        self.assertTrue(any(f["category"] == "SECRETS" for f in findings))

    def test_empty_scripts_dir(self):
        """Should return no findings for a skill with no scripts."""
        skill = _make_skill({"SKILL.md": "---\nname: empty\n---\n# Empty\n"})
        findings = check_secrets(skill)
        self.assertEqual(len(findings), 0)


class TestAntiPatternDetection(unittest.TestCase):
    """Tests for check_anti_patterns()."""

    def test_detects_eval(self):
        """Should detect eval() usage."""
        skill = _make_skill({"scripts/foo.py": "result = eval(user_input)\n"})
        findings = check_anti_patterns(skill)
        self.assertTrue(any(f["check_id"] == "AP-dangerous-eval" for f in findings))

    def test_detects_shell_true(self):
        """Should detect subprocess shell=True."""
        skill = _make_skill({
            "scripts/foo.py": 'subprocess.run(cmd, shell=True)\n'
        })
        findings = check_anti_patterns(skill)
        self.assertTrue(any(f["check_id"] == "AP-shell-true" for f in findings))

    def test_exempt_script_runner(self):
        """Should NOT flag subprocess in script_runner.py."""
        skill = _make_skill({
            "scripts/script_runner.py": 'result = subprocess.run([cmd], shell=True)\n'
        })
        findings = check_anti_patterns(skill)
        shell_findings = [f for f in findings if f["check_id"] == "AP-shell-true"]
        self.assertEqual(len(shell_findings), 0)

    def test_detects_pickle(self):
        """Should detect pickle.loads usage."""
        skill = _make_skill({"scripts/foo.py": "data = pickle.loads(raw_bytes)\n"})
        findings = check_anti_patterns(skill)
        self.assertTrue(any(f["check_id"] == "AP-pickle" for f in findings))

    def test_no_findings_on_clean_script(self):
        """Should produce zero anti-pattern findings for clean code."""
        clean = (
            "import json\nimport sys\nfrom pathlib import Path\n\n"
            "def main():\n    data = json.loads(Path('input.json').read_text())\n"
            "    print(json.dumps(data))\n\nif __name__ == '__main__':\n    main()\n"
        )
        skill = _make_skill({"scripts/clean.py": clean})
        findings = check_anti_patterns(skill)
        self.assertEqual(len(findings), 0)


class TestStructuralValidation(unittest.TestCase):
    """Tests for check_structure()."""

    def test_missing_skill_md(self):
        """Should flag missing SKILL.md."""
        skill = _make_skill({"scripts/foo.py": "pass\n"})
        findings = check_structure(skill)
        self.assertTrue(any("SKILL.md" in f["message"] and "missing" in f["message"] for f in findings))

    def test_missing_security_md(self):
        """Should flag missing SECURITY.md."""
        skill = _make_skill({
            "SKILL.md": "---\nname: test\nversion: 0.1.0\n---\n<security/><paths/><workflow/><behavior/>",
            "plugin.json": "{}",
        })
        findings = check_structure(skill)
        self.assertTrue(any("SECURITY.md" in f["message"] for f in findings))

    def test_missing_xml_sections(self):
        """Should flag missing <security> block in SKILL.md."""
        skill = _make_skill({
            "SKILL.md": "---\nname: test\nversion: 0.1.0\n---\n# Test\nNo XML here.",
            "plugin.json": "{}",
            "SECURITY.md": "# Security\n",
        })
        findings = check_structure(skill)
        section_findings = [f for f in findings if "missing-skill-section" in f.get("check_id", "")]
        self.assertGreater(len(section_findings), 0)

    def test_bare_relative_paths_flagged(self):
        """Should flag bare 'python scripts/' usage in SKILL.md."""
        skill = _make_skill({
            "SKILL.md": "---\nname: t\nversion: 0.1.0\n---\nRun: python scripts/foo.py",
            "plugin.json": "{}",
            "SECURITY.md": "# S\n",
        })
        findings = check_structure(skill)
        self.assertTrue(any("bare-relative-paths" in f.get("check_id", "") for f in findings))

    def test_compliant_skill_has_no_structural_findings(self):
        """A fully compliant skill should produce no structural findings."""
        skill = _make_skill({
            "SKILL.md": (
                "---\nname: test\nversion: 0.1.0\n---\n"
                "<security/>\n<paths/>\n<workflow/>\n<behavior/>\n"
            ),
            "plugin.json": '{"name": "test"}',
            "SECURITY.md": "# Security\n",
        })
        findings = check_structure(skill)
        structural = [f for f in findings if f.get("category") == "STRUCTURAL"
                      and f.get("severity") not in ("INFO", "LOW")]
        self.assertEqual(len(structural), 0)


class TestPathSecurity(unittest.TestCase):
    """Security tests for path traversal rejection."""

    def test_rejects_path_traversal(self):
        """run_scan should reject paths containing '..'."""
        with self.assertRaises(ValueError) as ctx:
            run_scan("../../../etc/passwd", "/tmp/session")
        self.assertIn("traversal", str(ctx.exception).lower())

    def test_rejects_nonexistent_path(self):
        """run_scan should raise FileNotFoundError for non-existent paths."""
        with self.assertRaises(FileNotFoundError):
            run_scan("/nonexistent/path/that/does/not/exist", "/tmp/session")


class TestRunScan(unittest.TestCase):
    """Integration tests for run_scan()."""

    def test_writes_scan_results_json(self):
        """run_scan should write scan_results.json to session dir."""
        skill = _make_skill({
            "SKILL.md": "---\nname: test\nversion: 0.1.0\n---\n<security/><paths/><workflow/><behavior/>",
            "plugin.json": "{}",
            "SECURITY.md": "# S\n",
        })
        with tempfile.TemporaryDirectory() as session_dir:
            result = run_scan(str(skill), session_dir)
            output_path = Path(session_dir) / "scan_results.json"
            self.assertTrue(output_path.exists())
            loaded = json.loads(output_path.read_text())
            self.assertIn("findings", loaded)
            self.assertIn("summary", loaded)
            self.assertIn("tool_coverage", loaded)

    def test_summary_has_risk_rating(self):
        """scan_results summary should always include risk_rating."""
        skill = _make_skill({
            "SKILL.md": "---\nname: t\nversion: 0.1.0\n---\n<security/><paths/><workflow/><behavior/>",
            "plugin.json": "{}",
            "SECURITY.md": "# S\n",
        })
        with tempfile.TemporaryDirectory() as session_dir:
            result = run_scan(str(skill), session_dir)
            self.assertIn("risk_rating", result["summary"])


if __name__ == "__main__":
    unittest.main()
