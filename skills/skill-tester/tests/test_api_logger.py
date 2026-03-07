#!/usr/bin/env python3
"""test_api_logger.py — Unit tests for api_logger.py inventory and shim.

Tests cover:
  - Inventory scan on a real skill directory
  - Secret and dangerous-call detection
  - URL extraction
  - Frontmatter parsing
  - Edge cases (empty dir, non-existent path)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from api_logger import inventory, _scan_script


def _make_dir(files: dict) -> Path:
    """Create a temporary directory with specified files.

    Args:
        files: Dict mapping relative path strings to file content.

    Returns:
        Path to the created temporary directory.
    """
    tmp = Path(tempfile.mkdtemp())
    for rel_path, content in files.items():
        fpath = tmp / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content, encoding="utf-8")
    return tmp


class TestInventory(unittest.TestCase):
    """Tests for the inventory() function."""

    def test_finds_scripts(self):
        """Should enumerate .py scripts in skills directory."""
        skill = _make_dir({
            "SKILL.md": "---\nname: myskill\n---\n# My Skill",
            "scripts/foo.py": "import json\nprint('hello')\n",
        })
        result = inventory(str(skill))
        self.assertEqual(result["summary"]["total_scripts"], 1)

    def test_parses_frontmatter(self):
        """Should extract name from SKILL.md frontmatter."""
        skill = _make_dir({
            "SKILL.md": "---\nname: my-skill\nversion: 1.0.0\n---\n# Title",
        })
        result = inventory(str(skill))
        self.assertEqual(result["frontmatter"]["name"], "my-skill")

    def test_detects_api_call(self):
        """Should flag scripts that call anthropic API."""
        skill = _make_dir({
            "scripts/caller.py": "import anthropic\nclient = anthropic.Anthropic()\n",
        })
        result = inventory(str(skill))
        self.assertEqual(result["summary"]["scripts_calling_api"], 1)

    def test_extracts_urls(self):
        """Should extract URLs from script content."""
        skill = _make_dir({
            "scripts/fetch.py": 'url = "https://example.com/api"\n',
        })
        result = inventory(str(skill))
        urls = [u for s in result["scripts"] for u in s.get("urls", [])]
        self.assertTrue(any("example.com" in u for u in urls))

    def test_empty_skill(self):
        """Should handle skill with no scripts gracefully."""
        skill = _make_dir({"SKILL.md": "---\nname: empty\n---\n# Empty"})
        result = inventory(str(skill))
        self.assertEqual(result["summary"]["total_scripts"], 0)

    def test_writes_output_file(self):
        """Should write inventory.json when output path is provided."""
        skill = _make_dir({"SKILL.md": "---\nname: t\n---\n"})
        with tempfile.TemporaryDirectory() as tmpdir:
            out = str(Path(tmpdir) / "inventory.json")
            inventory(str(skill), out)
            self.assertTrue(Path(out).exists())
            loaded = json.loads(Path(out).read_text())
            self.assertIn("summary", loaded)

    def test_raises_on_nonexistent_path(self):
        """Should raise FileNotFoundError for non-existent skill path."""
        with self.assertRaises(FileNotFoundError):
            inventory("/no/such/path/exists")


class TestScanScript(unittest.TestCase):
    """Tests for the _scan_script() helper."""

    def test_detects_dangerous_calls(self):
        """Should detect os.system and eval as dangerous calls."""
        tmp = Path(tempfile.mkdtemp())
        script = tmp / "bad.py"
        script.write_text("os.system('rm -rf /')\neval(user_input)\n")
        result = _scan_script(script)
        self.assertIn("os.system", result["dangerous_calls"])
        self.assertIn("eval", result["dangerous_calls"])

    def test_extracts_env_vars(self):
        """Should extract environment variable names accessed."""
        tmp = Path(tempfile.mkdtemp())
        script = tmp / "env.py"
        script.write_text("key = os.environ.get('MY_SECRET_KEY')\n")
        result = _scan_script(script)
        self.assertIn("MY_SECRET_KEY", result["env_vars"])


if __name__ == "__main__":
    unittest.main()
