diff --git a/skills/requirements-dev/agents/quality-checker.md b/skills/requirements-dev/agents/quality-checker.md
index 1f0e76f..08c1835 100644
--- a/skills/requirements-dev/agents/quality-checker.md
+++ b/skills/requirements-dev/agents/quality-checker.md
@@ -4,4 +4,108 @@ description: Semantic quality checker for requirements using 9 INCOSE GtWR v4 LL
 model: sonnet
 ---
 
-<!-- Agent definition for quality-checker. See section-05 (quality checker). -->
+# Quality Checker Agent
+
+You are a requirements quality checker applying INCOSE GtWR v4 semantic rules. You evaluate requirement statements that have already passed Tier 1 deterministic checks.
+
+## Input
+
+You receive:
+- `statement`: The requirement statement to evaluate
+- `context`: Block name, requirement type, parent need statement
+- `existing_requirements`: (Optional) Previously registered requirements for terminology consistency
+
+## Rules to Evaluate
+
+### R31 - Solution-Free
+Does the requirement prescribe a specific solution or implementation technology?
+- Flag: "The system shall use PostgreSQL for data storage" (prescribes database)
+- Pass: "The system shall persist data with ACID transaction guarantees" (states need, not solution)
+
+### R34 - Measurable
+Are performance/quality criteria quantifiable and testable?
+- Flag: "The system shall respond quickly" (not measurable)
+- Pass: "The system shall respond within 200ms at the 95th percentile" (measurable)
+
+### R18 - Single Thought
+Does the statement contain exactly one requirement?
+- Flag: "The system shall encrypt data and shall log all access attempts" (two requirements)
+- Pass: "The system shall encrypt all data at rest using AES-256" (single requirement)
+
+### R1 - Structured
+Does it follow the "The [subject] shall [action]" pattern?
+- Flag: "Encryption is required for all data" (missing subject-shall pattern)
+- Pass: "The system shall encrypt all data at rest" (proper structure)
+
+### R11 - Separate Clauses
+Are conditions properly separated from the main requirement?
+- Flag: "The system shall, when the user is authenticated and the session is valid and the token has not expired, grant access"
+- Pass: "When the user session is valid, the system shall grant access to protected resources"
+
+### R22 - Enumeration
+Are lists complete and exhaustive?
+- Flag: "The system shall support common file formats" (which formats?)
+- Pass: "The system shall support PDF, DOCX, and CSV file formats"
+
+### R27 - Explicit Conditions
+Are all trigger conditions explicitly stated?
+- Flag: "The system shall send a notification" (when? under what conditions?)
+- Pass: "When a build fails, the system shall send a notification to the repository owner"
+
+### R28 - Multiple Conditions
+Are nested if/then/else conditions clear?
+- Flag: "If A and if B or C then the system shall do X" (ambiguous precedence)
+- Pass: "When condition A is true AND condition B is true, the system shall perform action X"
+
+### R36 - Consistent Terms
+Is terminology consistent with other requirements in the set?
+- Flag: Uses "user" when other requirements say "operator" for the same role
+- Pass: Consistent use of "operator" throughout the requirement set
+
+## Output Format
+
+Return a JSON array of findings:
+
+```json
+[
+  {
+    "rule_id": "R31",
+    "assessment": "flag",
+    "confidence": "high",
+    "reasoning": "The requirement specifies 'PostgreSQL' which is a specific implementation technology. This constrains solution space unnecessarily.",
+    "suggestion": "Rewrite as: 'The system shall persist data with ACID transaction guarantees and support concurrent access from up to 100 connections.'"
+  },
+  {
+    "rule_id": "R34",
+    "assessment": "pass",
+    "confidence": "high",
+    "reasoning": "The requirement specifies '200ms at the 95th percentile' which is a clear, measurable criterion with defined statistical basis.",
+    "suggestion": ""
+  }
+]
+```
+
+## Confidence Levels
+
+- **high**: Clear violation or clear pass, no ambiguity
+- **medium**: Likely violation but context-dependent; present to user for review
+- **low**: Possible concern but may be acceptable; informational only
+
+Only **high-confidence flags** should block registration. Medium and low flags are presented as informational findings for human review.
+
+## Process
+
+1. Read the requirement statement carefully
+2. For each of the 9 rules, evaluate independently
+3. Use Chain-of-Thought reasoning for each assessment
+4. Consider the requirement's context (block, type, parent need)
+5. For R36, compare terminology against existing requirements if provided
+6. Return all findings as the JSON array
+
+## Tool Access
+
+You may call `quality_rules.py check` to cross-reference deterministic Tier 1 results:
+
+```bash
+uv run scripts/quality_rules.py check "requirement statement here"
+```
diff --git a/skills/requirements-dev/scripts/quality_rules.py b/skills/requirements-dev/scripts/quality_rules.py
index 2fd5716..17c6bd5 100644
--- a/skills/requirements-dev/scripts/quality_rules.py
+++ b/skills/requirements-dev/scripts/quality_rules.py
@@ -1 +1,425 @@
-"""21 deterministic INCOSE GtWR v4 quality rules."""
+#!/usr/bin/env python3
+"""21 deterministic INCOSE GtWR v4 quality rules.
+
+Usage:
+    python3 quality_rules.py check "The system shall ..."
+    python3 quality_rules.py check-all --registry requirements_registry.json
+    python3 quality_rules.py rules
+
+Pure stdlib implementation -- no external dependencies.
+"""
+import argparse
+import json
+import os
+import re
+import sys
+from dataclasses import asdict, dataclass
+from pathlib import Path
+
+
+@dataclass
+class Violation:
+    """A single quality rule violation found in a requirement statement."""
+    rule_id: str
+    rule_name: str
+    severity: str
+    matched_text: str
+    position: int
+    suggestion: str
+
+
+@dataclass
+class RuleInfo:
+    """Metadata about an available quality rule."""
+    rule_id: str
+    rule_name: str
+    severity: str
+    description: str
+    detection_tier: str
+
+
+# --- Data file loading (lazy, cached) ---
+
+_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
+_cache: dict[str, list[str]] = {}
+
+
+def _load_wordlist(filename: str) -> list[str]:
+    if filename not in _cache:
+        path = _DATA_DIR / filename
+        with open(path) as f:
+            _cache[filename] = json.load(f)
+    return _cache[filename]
+
+
+# --- Passive voice whitelist ---
+
+_PASSIVE_WHITELIST = {"open", "green", "broken", "driven", "written", "given",
+                      "red", "blue", "yellow", "closed", "enabled", "disabled",
+                      "hidden", "shown", "known", "proven"}
+
+
+# --- Rule implementations ---
+
+def _check_r7(statement: str) -> list[Violation]:
+    """Vague terms."""
+    terms = _load_wordlist("vague_terms.json")
+    violations = []
+    for term in terms:
+        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
+        for m in pattern.finditer(statement):
+            violations.append(Violation(
+                rule_id="R7", rule_name="Vague terms", severity="error",
+                matched_text=m.group(), position=m.start(),
+                suggestion=f"Replace '{m.group()}' with a specific, measurable term",
+            ))
+    return violations
+
+
+def _check_r8(statement: str) -> list[Violation]:
+    """Escape clauses."""
+    clauses = _load_wordlist("escape_clauses.json")
+    violations = []
+    lower = statement.lower()
+    for clause in clauses:
+        idx = lower.find(clause.lower())
+        if idx >= 0:
+            violations.append(Violation(
+                rule_id="R8", rule_name="Escape clauses", severity="error",
+                matched_text=statement[idx:idx + len(clause)], position=idx,
+                suggestion=f"Remove escape clause '{clause}' and state the requirement unconditionally",
+            ))
+    return violations
+
+
+def _check_r9(statement: str) -> list[Violation]:
+    """Open-ended clauses."""
+    patterns = [
+        (r'including but not limited to', "Remove open-ended clause; list all items explicitly"),
+        (r'\betc\.', "Replace 'etc.' with an explicit, complete list"),
+        (r'\band so on\b', "Replace 'and so on' with specific items"),
+        (r'\bsuch as\b', "Consider whether 'such as' introduces ambiguity"),
+        (r'\bfor example\b', "Remove 'for example' and state requirements explicitly"),
+    ]
+    violations = []
+    for pat, suggestion in patterns:
+        for m in re.finditer(pat, statement, re.IGNORECASE):
+            violations.append(Violation(
+                rule_id="R9", rule_name="Open-ended clauses", severity="error",
+                matched_text=m.group(), position=m.start(), suggestion=suggestion,
+            ))
+    return violations
+
+
+def _check_r19(statement: str) -> list[Violation]:
+    """Combinators (multiple shall clauses)."""
+    violations = []
+    pattern = re.compile(r'shall\s+.+?\b(and|or)\b\s+.*?shall\b', re.IGNORECASE | re.DOTALL)
+    for m in pattern.finditer(statement):
+        violations.append(Violation(
+            rule_id="R19", rule_name="Combinators", severity="warning",
+            matched_text=m.group(), position=m.start(),
+            suggestion="Split into separate requirements, one 'shall' per statement",
+        ))
+    return violations
+
+
+def _check_r24(statement: str) -> list[Violation]:
+    """Pronouns."""
+    pronouns = _load_wordlist("pronouns.json")
+    violations = []
+    for pronoun in pronouns:
+        pattern = re.compile(r'\b' + re.escape(pronoun) + r'\b', re.IGNORECASE)
+        for m in pattern.finditer(statement):
+            violations.append(Violation(
+                rule_id="R24", rule_name="Pronouns", severity="error",
+                matched_text=m.group(), position=m.start(),
+                suggestion=f"Replace '{m.group()}' with the specific noun it refers to",
+            ))
+    return violations
+
+
+def _check_r26(statement: str) -> list[Violation]:
+    """Absolutes."""
+    absolutes = _load_wordlist("absolutes.json")
+    violations = []
+    for term in absolutes:
+        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
+        for m in pattern.finditer(statement):
+            violations.append(Violation(
+                rule_id="R26", rule_name="Absolutes", severity="error",
+                matched_text=m.group(), position=m.start(),
+                suggestion=f"Replace '{m.group()}' with specific quantified criteria",
+            ))
+    return violations
+
+
+def _check_r2(statement: str) -> list[Violation]:
+    """Passive voice (heuristic)."""
+    violations = []
+    be_forms = r'(?:is|are|was|were|been|being|be)'
+    pattern = re.compile(
+        be_forms + r'\s+((?:\w+\s+){0,2})(\w+(?:ed|en))\b',
+        re.IGNORECASE,
+    )
+    for m in pattern.finditer(statement):
+        # Check all words in the match against the whitelist
+        intervening = m.group(1).split() if m.group(1).strip() else []
+        participle = m.group(2).lower()
+        # If any word (intervening or participle) is whitelisted, skip
+        all_words = [w.lower() for w in intervening] + [participle]
+        if any(w in _PASSIVE_WHITELIST for w in all_words):
+            continue
+        violations.append(Violation(
+            rule_id="R2", rule_name="Passive voice", severity="warning",
+            matched_text=m.group(), position=m.start(),
+            suggestion="Rewrite in active voice: identify the subject performing the action",
+        ))
+    return violations
+
+
+def _check_r20(statement: str) -> list[Violation]:
+    """Purpose phrases."""
+    patterns = [
+        (r'\bin order to\b', "Remove 'in order to'; state the requirement directly"),
+        (r'\bso that\b', "Consider separating purpose from requirement"),
+        (r'\bto ensure\b', "Remove 'to ensure'; state what shall happen"),
+        (r'\bfor the purpose of\b', "Remove 'for the purpose of'; state the requirement directly"),
+    ]
+    violations = []
+    for pat, suggestion in patterns:
+        for m in re.finditer(pat, statement, re.IGNORECASE):
+            violations.append(Violation(
+                rule_id="R20", rule_name="Purpose phrases", severity="warning",
+                matched_text=m.group(), position=m.start(), suggestion=suggestion,
+            ))
+    return violations
+
+
+def _check_r21(statement: str) -> list[Violation]:
+    """Parentheses."""
+    violations = []
+    for m in re.finditer(r'\(.*?\)', statement):
+        violations.append(Violation(
+            rule_id="R21", rule_name="Parentheses", severity="warning",
+            matched_text=m.group(), position=m.start(),
+            suggestion="Remove parentheses; integrate content into the statement or a separate requirement",
+        ))
+    return violations
+
+
+def _check_r15(statement: str) -> list[Violation]:
+    """Logical and/or."""
+    violations = []
+    for m in re.finditer(r'\band/or\b', statement, re.IGNORECASE):
+        violations.append(Violation(
+            rule_id="R15", rule_name="Logical and/or", severity="error",
+            matched_text=m.group(), position=m.start(),
+            suggestion="Replace 'and/or' with explicit 'and' or 'or' (or split into separate requirements)",
+        ))
+    return violations
+
+
+def _check_r16(statement: str) -> list[Violation]:
+    """Negatives."""
+    violations = []
+    for m in re.finditer(r'\bnot\b', statement, re.IGNORECASE):
+        violations.append(Violation(
+            rule_id="R16", rule_name="Negatives", severity="warning",
+            matched_text=m.group(), position=m.start(),
+            suggestion="Consider restating as a positive requirement",
+        ))
+    return violations
+
+
+def _check_r10(statement: str) -> list[Violation]:
+    """Superfluous infinitives."""
+    patterns = [
+        (r'\bbe able to\b', "Remove 'be able to'; state the capability directly"),
+        (r'\bbe capable of\b', "Remove 'be capable of'; state the capability directly"),
+    ]
+    violations = []
+    for pat, suggestion in patterns:
+        for m in re.finditer(pat, statement, re.IGNORECASE):
+            violations.append(Violation(
+                rule_id="R10", rule_name="Superfluous infinitives", severity="error",
+                matched_text=m.group(), position=m.start(), suggestion=suggestion,
+            ))
+    return violations
+
+
+def _check_r35(statement: str) -> list[Violation]:
+    """Temporal dependencies."""
+    keywords = ["before", "after", "during", "while", "when"]
+    violations = []
+    for kw in keywords:
+        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
+        for m in pattern.finditer(statement):
+            violations.append(Violation(
+                rule_id="R35", rule_name="Temporal dependencies", severity="warning",
+                matched_text=m.group(), position=m.start(),
+                suggestion=f"Review temporal dependency '{kw}'; consider if timing is specified precisely",
+            ))
+    return violations
+
+
+def _check_r32(statement: str) -> list[Violation]:
+    """Universal quantifiers."""
+    quantifiers = ["each", "every", "all", "any"]
+    violations = []
+    for q in quantifiers:
+        pattern = re.compile(r'\b' + re.escape(q) + r'\b', re.IGNORECASE)
+        for m in pattern.finditer(statement):
+            violations.append(Violation(
+                rule_id="R32", rule_name="Universal quantifiers", severity="warning",
+                matched_text=m.group(), position=m.start(),
+                suggestion=f"Verify '{q}' is intended; consider specifying the exact set",
+            ))
+    return violations
+
+
+def _check_r40(statement: str) -> list[Violation]:
+    """Decimal format inconsistency."""
+    violations = []
+    has_comma_decimal = bool(re.search(r'\d+,\d+', statement))
+    has_dot_decimal = bool(re.search(r'\d+\.\d+', statement))
+    if has_comma_decimal and has_dot_decimal:
+        violations.append(Violation(
+            rule_id="R40", rule_name="Decimal format", severity="warning",
+            matched_text="mixed decimal separators", position=0,
+            suggestion="Use consistent decimal format (dot or comma, not both)",
+        ))
+    return violations
+
+
+def _check_r33(statement: str) -> list[Violation]:
+    """Range checking."""
+    violations = []
+    pattern = re.compile(r'\bbetween\s+(\d+[\.,]?\d*)\s+and\s+(\d+[\.,]?\d*)\b', re.IGNORECASE)
+    for m in pattern.finditer(statement):
+        # Check if units follow the range
+        after = statement[m.end():m.end() + 20].strip()
+        if not after or after[0] in '.,:;)':
+            violations.append(Violation(
+                rule_id="R33", rule_name="Range checking", severity="warning",
+                matched_text=m.group(), position=m.start(),
+                suggestion="Add units to numeric range",
+            ))
+    return violations
+
+
+# --- Rule registry ---
+
+_ALL_RULES: list[tuple[str, str, str, str, callable]] = [
+    ("R2", "Passive voice", "warning", "Flags passive voice constructions", _check_r2),
+    ("R7", "Vague terms", "error", "Flags vague/ambiguous terms from INCOSE list", _check_r7),
+    ("R8", "Escape clauses", "error", "Flags escape clause phrases", _check_r8),
+    ("R9", "Open-ended clauses", "error", "Flags open-ended qualifiers (etc., and so on)", _check_r9),
+    ("R10", "Superfluous infinitives", "error", "Flags 'be able to', 'be capable of'", _check_r10),
+    ("R15", "Logical and/or", "error", "Flags 'and/or' usage", _check_r15),
+    ("R16", "Negatives", "warning", "Flags negative requirements", _check_r16),
+    ("R19", "Combinators", "warning", "Flags multiple 'shall' clauses combined with and/or", _check_r19),
+    ("R20", "Purpose phrases", "warning", "Flags 'in order to', 'so that', etc.", _check_r20),
+    ("R21", "Parentheses", "warning", "Flags parenthetical content", _check_r21),
+    ("R24", "Pronouns", "error", "Flags pronoun usage (ambiguous references)", _check_r24),
+    ("R26", "Absolutes", "error", "Flags absolute terms (always, never, every)", _check_r26),
+    ("R32", "Universal quantifiers", "warning", "Flags universal quantifiers (each, every, all)", _check_r32),
+    ("R33", "Range checking", "warning", "Flags numeric ranges missing units", _check_r33),
+    ("R35", "Temporal dependencies", "warning", "Flags temporal keywords for precision review", _check_r35),
+    ("R40", "Decimal format", "warning", "Flags inconsistent decimal separators", _check_r40),
+]
+
+_RULE_MAP = {rule_id: fn for rule_id, _, _, _, fn in _ALL_RULES}
+
+
+# --- Public API ---
+
+def check_requirement(statement: str) -> list[Violation]:
+    """Run all deterministic INCOSE checks on a requirement statement.
+
+    Returns list of Violation objects sorted by position.
+    """
+    violations = []
+    for _, _, _, _, fn in _ALL_RULES:
+        violations.extend(fn(statement))
+    violations.sort(key=lambda v: v.position)
+    return violations
+
+
+def check_rule(statement: str, rule_id: str) -> Violation | None:
+    """Run a single rule check. Returns first Violation if triggered, None otherwise."""
+    fn = _RULE_MAP.get(rule_id)
+    if fn is None:
+        raise ValueError(f"Unknown rule: {rule_id}")
+    results = fn(statement)
+    return results[0] if results else None
+
+
+def list_rules() -> list[RuleInfo]:
+    """Return metadata for all available deterministic rules."""
+    return [
+        RuleInfo(
+            rule_id=rule_id, rule_name=name, severity=severity,
+            description=desc, detection_tier="deterministic",
+        )
+        for rule_id, name, severity, desc, _ in _ALL_RULES
+    ]
+
+
+# --- CLI ---
+
+def _validate_path(filepath: str, allowed_extensions: list[str]) -> str:
+    """Validate file path: reject traversal and restrict extensions."""
+    if ".." in Path(filepath).parts:
+        print(f"Error: Path contains '..' traversal: {filepath}", file=sys.stderr)
+        sys.exit(1)
+    resolved = os.path.realpath(filepath)
+    ext = os.path.splitext(resolved)[1].lower()
+    if ext not in allowed_extensions:
+        print(f"Error: Extension '{ext}' not in {allowed_extensions}", file=sys.stderr)
+        sys.exit(1)
+    return resolved
+
+
+def main():
+    """CLI entry point."""
+    parser = argparse.ArgumentParser(description="INCOSE quality rules checker")
+    subparsers = parser.add_subparsers(dest="command", required=True)
+
+    # check
+    sp = subparsers.add_parser("check", help="Check a single requirement statement")
+    sp.add_argument("statement", help="Requirement statement to check")
+
+    # check-all
+    sp = subparsers.add_parser("check-all", help="Check all requirements in a registry")
+    sp.add_argument("--registry", required=True, help="Path to requirements_registry.json")
+
+    # rules
+    subparsers.add_parser("rules", help="List all available rules")
+
+    args = parser.parse_args()
+
+    if args.command == "check":
+        violations = check_requirement(args.statement)
+        print(json.dumps([asdict(v) for v in violations], indent=2))
+
+    elif args.command == "check-all":
+        registry_path = _validate_path(args.registry, [".json"])
+        with open(registry_path) as f:
+            registry = json.load(f)
+        results = {}
+        reqs = registry if isinstance(registry, list) else registry.get("requirements", [])
+        for req in reqs:
+            req_id = req.get("id", "unknown")
+            statement = req.get("statement", "")
+            violations = check_requirement(statement)
+            results[req_id] = [asdict(v) for v in violations]
+        print(json.dumps(results, indent=2))
+
+    elif args.command == "rules":
+        rules = list_rules()
+        print(json.dumps([asdict(r) for r in rules], indent=2))
+
+
+if __name__ == "__main__":
+    main()
diff --git a/skills/requirements-dev/tests/test_quality_rules.py b/skills/requirements-dev/tests/test_quality_rules.py
new file mode 100644
index 0000000..d001726
--- /dev/null
+++ b/skills/requirements-dev/tests/test_quality_rules.py
@@ -0,0 +1,240 @@
+"""Golden tests for INCOSE deterministic quality rules.
+
+Each test provides a requirement statement and asserts the expected
+violations (or absence thereof). Tests are grouped by rule ID.
+"""
+import json
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+
+from quality_rules import Violation, check_requirement, check_rule, list_rules
+
+
+def _has_violation(violations: list[Violation], rule_id: str) -> bool:
+    return any(v.rule_id == rule_id for v in violations)
+
+
+def _get_violation(violations: list[Violation], rule_id: str) -> Violation | None:
+    return next((v for v in violations if v.rule_id == rule_id), None)
+
+
+# --- R7: Vague terms ---
+
+def test_r7_flags_appropriate():
+    vs = check_requirement("The system shall provide appropriate error handling")
+    v = _get_violation(vs, "R7")
+    assert v is not None
+    assert "appropriate" in v.matched_text.lower()
+
+
+def test_r7_clean_statement():
+    vs = check_requirement("The system shall provide structured error responses")
+    assert not _has_violation(vs, "R7")
+
+
+def test_r7_flags_several():
+    vs = check_requirement("Several modules shall be loaded")
+    v = _get_violation(vs, "R7")
+    assert v is not None
+    assert "several" in v.matched_text.lower()
+
+
+# --- R8: Escape clauses ---
+
+def test_r8_flags_where_possible():
+    vs = check_requirement("The system shall, where possible, cache results")
+    assert _has_violation(vs, "R8")
+
+
+def test_r8_clean_statement():
+    vs = check_requirement("The system shall cache all query results")
+    assert not _has_violation(vs, "R8")
+
+
+# --- R9: Open-ended clauses ---
+
+def test_r9_flags_including_but_not_limited_to():
+    vs = check_requirement("The system shall support formats including but not limited to JSON")
+    assert _has_violation(vs, "R9")
+
+
+def test_r9_clean_statement():
+    vs = check_requirement("The system shall support JSON, XML, and CSV formats")
+    assert not _has_violation(vs, "R9")
+
+
+# --- R19: Combinators ---
+
+def test_r19_flags_double_shall_and():
+    vs = check_requirement("The system shall log errors and shall send alerts")
+    assert _has_violation(vs, "R19")
+
+
+def test_r19_clean_compound_object():
+    vs = check_requirement("The system shall log errors and warnings")
+    assert not _has_violation(vs, "R19")
+
+
+def test_r19_flags_double_shall_or():
+    vs = check_requirement("The system shall respond or shall queue the request")
+    assert _has_violation(vs, "R19")
+
+
+# --- R24: Pronouns ---
+
+def test_r24_flags_it():
+    vs = check_requirement("It shall respond within 200ms")
+    assert _has_violation(vs, "R24")
+
+
+def test_r24_clean_statement():
+    vs = check_requirement("The API Gateway shall respond within 200ms")
+    assert not _has_violation(vs, "R24")
+
+
+# --- R26: Absolutes ---
+
+def test_r26_flags_always():
+    vs = check_requirement("The system shall always be available")
+    v = _get_violation(vs, "R26")
+    assert v is not None
+    assert "always" in v.matched_text.lower()
+
+
+def test_r26_clean_statement():
+    vs = check_requirement("The system shall maintain 99.9% availability")
+    assert not _has_violation(vs, "R26")
+
+
+# --- R2: Passive voice ---
+
+def test_r2_flags_passive():
+    vs = check_requirement("Errors shall be logged by the system")
+    assert _has_violation(vs, "R2")
+
+
+def test_r2_clean_active_voice():
+    vs = check_requirement("The system shall log errors")
+    assert not _has_violation(vs, "R2")
+
+
+def test_r2_whitelist_green():
+    vs = check_requirement("The indicator shall be green when ready")
+    assert not _has_violation(vs, "R2")
+
+
+def test_r2_whitelist_open():
+    vs = check_requirement("The port shall be open for connections")
+    assert not _has_violation(vs, "R2")
+
+
+# --- R20: Purpose phrases ---
+
+def test_r20_flags_in_order_to():
+    vs = check_requirement("The system shall cache results in order to improve latency")
+    assert _has_violation(vs, "R20")
+
+
+# --- R21: Parentheses ---
+
+def test_r21_flags_parentheses():
+    vs = check_requirement("The system shall return status codes (200, 404, 500)")
+    assert _has_violation(vs, "R21")
+
+
+# --- R15/R17: Logical and/or ---
+
+def test_r15_flags_and_or():
+    vs = check_requirement("The system shall accept JSON and/or XML")
+    assert _has_violation(vs, "R15")
+
+
+# --- R16: Negatives ---
+
+def test_r16_flags_not():
+    vs = check_requirement("The system shall not expose internal errors")
+    assert _has_violation(vs, "R16")
+
+
+# --- R10: Superfluous infinitives ---
+
+def test_r10_flags_be_able_to():
+    vs = check_requirement("The system shall be able to process 1000 requests")
+    assert _has_violation(vs, "R10")
+
+
+# --- R35: Temporal dependencies ---
+
+def test_r35_flags_before():
+    vs = check_requirement("The cache shall be invalidated before serving new data")
+    assert _has_violation(vs, "R35")
+
+
+# --- R32: Universal quantifiers ---
+
+def test_r32_flags_every():
+    vs = check_requirement("Every endpoint shall require authentication")
+    assert _has_violation(vs, "R32")
+
+
+# --- check_rule ---
+
+def test_check_rule_returns_violation():
+    v = check_rule("It shall respond", "R24")
+    assert v is not None
+    assert v.rule_id == "R24"
+
+
+def test_check_rule_returns_none_for_clean():
+    v = check_rule("The API shall respond", "R24")
+    assert v is None
+
+
+# --- list_rules ---
+
+def test_list_rules_returns_all():
+    rules = list_rules()
+    rule_ids = {r.rule_id for r in rules}
+    assert "R7" in rule_ids
+    assert "R2" in rule_ids
+    assert "R19" in rule_ids
+    assert len(rules) >= 15
+
+
+# --- CLI ---
+
+def test_cli_check_returns_json():
+    result = subprocess.run(
+        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
+         "check", "It shall be appropriate"],
+        capture_output=True, text=True,
+    )
+    assert result.returncode == 0
+    data = json.loads(result.stdout)
+    assert isinstance(data, list)
+    assert len(data) > 0
+
+
+def test_cli_check_clean_returns_empty():
+    result = subprocess.run(
+        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
+         "check", "The API Gateway shall respond within 200ms"],
+        capture_output=True, text=True,
+    )
+    assert result.returncode == 0
+    data = json.loads(result.stdout)
+    assert data == []
+
+
+def test_cli_rules_lists_all():
+    result = subprocess.run(
+        [sys.executable, str(Path(__file__).parent.parent / "scripts" / "quality_rules.py"),
+         "rules"],
+        capture_output=True, text=True,
+    )
+    assert result.returncode == 0
+    data = json.loads(result.stdout)
+    assert len(data) >= 15
