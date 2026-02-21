#!/usr/bin/env python3
"""16 deterministic INCOSE GtWR v4 quality rules.

Usage:
    python3 quality_rules.py check "The system shall ..."
    python3 quality_rules.py check-all --registry requirements_registry.json
    python3 quality_rules.py rules

Pure stdlib implementation -- no external dependencies.
"""
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from shared_io import _validate_path as _shared_validate_path


@dataclass
class Violation:
    """A single quality rule violation found in a requirement statement."""
    rule_id: str
    rule_name: str
    severity: str
    matched_text: str
    position: int
    suggestion: str


@dataclass
class RuleInfo:
    """Metadata about an available quality rule."""
    rule_id: str
    rule_name: str
    severity: str
    description: str
    detection_tier: str


# --- Data file loading (lazy, cached) ---

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_cache: dict[str, list[str]] = {}


def _load_wordlist(filename: str) -> list[str]:
    if filename not in _cache:
        path = _DATA_DIR / filename
        with open(path) as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


# --- Passive voice whitelist ---

_PASSIVE_WHITELIST = {"open", "green", "broken", "driven", "written", "given",
                      "red", "blue", "yellow", "closed", "enabled", "disabled",
                      "hidden", "shown", "known", "proven", "when", "then",
                      "often", "golden", "widen", "lessen", "flatten"}


# --- Rule implementations ---

def _check_r7(statement: str) -> list[Violation]:
    """Vague terms."""
    terms = _load_wordlist("vague_terms.json")
    violations = []
    for term in terms:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(statement):
            violations.append(Violation(
                rule_id="R7", rule_name="Vague terms", severity="error",
                matched_text=m.group(), position=m.start(),
                suggestion=f"Replace '{m.group()}' with a specific, measurable term",
            ))
    return violations


def _check_r8(statement: str) -> list[Violation]:
    """Escape clauses."""
    clauses = _load_wordlist("escape_clauses.json")
    violations = []
    lower = statement.lower()
    for clause in clauses:
        idx = lower.find(clause.lower())
        if idx >= 0:
            violations.append(Violation(
                rule_id="R8", rule_name="Escape clauses", severity="error",
                matched_text=statement[idx:idx + len(clause)], position=idx,
                suggestion=f"Remove escape clause '{clause}' and state the requirement unconditionally",
            ))
    return violations


def _check_r9(statement: str) -> list[Violation]:
    """Open-ended clauses."""
    patterns = [
        (r'including but not limited to', "Remove open-ended clause; list all items explicitly"),
        (r'\betc\.', "Replace 'etc.' with an explicit, complete list"),
        (r'\band so on\b', "Replace 'and so on' with specific items"),
        (r'\bsuch as\b', "Consider whether 'such as' introduces ambiguity"),
        (r'\bfor example\b', "Remove 'for example' and state requirements explicitly"),
    ]
    violations = []
    for pat, suggestion in patterns:
        for m in re.finditer(pat, statement, re.IGNORECASE):
            violations.append(Violation(
                rule_id="R9", rule_name="Open-ended clauses", severity="error",
                matched_text=m.group(), position=m.start(), suggestion=suggestion,
            ))
    return violations


def _check_r19(statement: str) -> list[Violation]:
    """Combinators (multiple shall clauses)."""
    violations = []
    pattern = re.compile(r'shall\s+.+?\b(and|or)\b\s+.*?shall\b', re.IGNORECASE | re.DOTALL)
    for m in pattern.finditer(statement):
        violations.append(Violation(
            rule_id="R19", rule_name="Combinators", severity="warning",
            matched_text=m.group(), position=m.start(),
            suggestion="Split into separate requirements, one 'shall' per statement",
        ))
    return violations


def _check_r24(statement: str) -> list[Violation]:
    """Pronouns."""
    pronouns = _load_wordlist("pronouns.json")
    violations = []
    for pronoun in pronouns:
        pattern = re.compile(r'\b' + re.escape(pronoun) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(statement):
            violations.append(Violation(
                rule_id="R24", rule_name="Pronouns", severity="error",
                matched_text=m.group(), position=m.start(),
                suggestion=f"Replace '{m.group()}' with the specific noun it refers to",
            ))
    return violations


def _check_r26(statement: str) -> list[Violation]:
    """Absolutes."""
    absolutes = _load_wordlist("absolutes.json")
    violations = []
    for term in absolutes:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(statement):
            violations.append(Violation(
                rule_id="R26", rule_name="Absolutes", severity="error",
                matched_text=m.group(), position=m.start(),
                suggestion=f"Replace '{m.group()}' with specific quantified criteria",
            ))
    return violations


def _check_r2(statement: str) -> list[Violation]:
    """Passive voice (heuristic)."""
    violations = []
    be_forms = r'(?:is|are|was|were|been|being|be)'
    pattern = re.compile(
        be_forms + r'\s+((?:\w+\s+){0,2})(\w+(?:ed|en))\b',
        re.IGNORECASE,
    )
    for m in pattern.finditer(statement):
        participle = m.group(2).lower()
        if participle in _PASSIVE_WHITELIST:
            continue
        violations.append(Violation(
            rule_id="R2", rule_name="Passive voice", severity="warning",
            matched_text=m.group(), position=m.start(),
            suggestion="Rewrite in active voice: identify the subject performing the action",
        ))
    return violations


def _check_r20(statement: str) -> list[Violation]:
    """Purpose phrases."""
    patterns = [
        (r'\bin order to\b', "Remove 'in order to'; state the requirement directly"),
        (r'\bso that\b', "Consider separating purpose from requirement"),
        (r'\bto ensure\b', "Remove 'to ensure'; state what shall happen"),
        (r'\bfor the purpose of\b', "Remove 'for the purpose of'; state the requirement directly"),
    ]
    violations = []
    for pat, suggestion in patterns:
        for m in re.finditer(pat, statement, re.IGNORECASE):
            violations.append(Violation(
                rule_id="R20", rule_name="Purpose phrases", severity="warning",
                matched_text=m.group(), position=m.start(), suggestion=suggestion,
            ))
    return violations


def _check_r21(statement: str) -> list[Violation]:
    """Parentheses."""
    violations = []
    for m in re.finditer(r'\(.*?\)', statement):
        violations.append(Violation(
            rule_id="R21", rule_name="Parentheses", severity="warning",
            matched_text=m.group(), position=m.start(),
            suggestion="Remove parentheses; integrate content into the statement or a separate requirement",
        ))
    return violations


def _check_r15(statement: str) -> list[Violation]:
    """Logical and/or."""
    violations = []
    for m in re.finditer(r'\band/or\b', statement, re.IGNORECASE):
        violations.append(Violation(
            rule_id="R15", rule_name="Logical and/or", severity="error",
            matched_text=m.group(), position=m.start(),
            suggestion="Replace 'and/or' with explicit 'and' or 'or' (or split into separate requirements)",
        ))
    return violations


def _check_r16(statement: str) -> list[Violation]:
    """Negatives."""
    violations = []
    for m in re.finditer(r'\bnot\b', statement, re.IGNORECASE):
        violations.append(Violation(
            rule_id="R16", rule_name="Negatives", severity="warning",
            matched_text=m.group(), position=m.start(),
            suggestion="Consider restating as a positive requirement",
        ))
    return violations


def _check_r10(statement: str) -> list[Violation]:
    """Superfluous infinitives."""
    patterns = [
        (r'\bbe able to\b', "Remove 'be able to'; state the capability directly"),
        (r'\bbe capable of\b', "Remove 'be capable of'; state the capability directly"),
    ]
    violations = []
    for pat, suggestion in patterns:
        for m in re.finditer(pat, statement, re.IGNORECASE):
            violations.append(Violation(
                rule_id="R10", rule_name="Superfluous infinitives", severity="error",
                matched_text=m.group(), position=m.start(), suggestion=suggestion,
            ))
    return violations


def _check_r35(statement: str) -> list[Violation]:
    """Temporal dependencies."""
    keywords = ["before", "after", "during", "while", "when"]
    violations = []
    for kw in keywords:
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(statement):
            violations.append(Violation(
                rule_id="R35", rule_name="Temporal dependencies", severity="warning",
                matched_text=m.group(), position=m.start(),
                suggestion=f"Review temporal dependency '{kw}'; consider if timing is specified precisely",
            ))
    return violations


def _check_r32(statement: str) -> list[Violation]:
    """Universal quantifiers."""
    quantifiers = ["each", "every", "all", "any"]
    violations = []
    for q in quantifiers:
        pattern = re.compile(r'\b' + re.escape(q) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(statement):
            violations.append(Violation(
                rule_id="R32", rule_name="Universal quantifiers", severity="warning",
                matched_text=m.group(), position=m.start(),
                suggestion=f"Verify '{q}' is intended; consider specifying the exact set",
            ))
    return violations


def _check_r40(statement: str) -> list[Violation]:
    """Decimal format inconsistency."""
    violations = []
    has_comma_decimal = bool(re.search(r'\d+,\d+', statement))
    has_dot_decimal = bool(re.search(r'\d+\.\d+', statement))
    if has_comma_decimal and has_dot_decimal:
        violations.append(Violation(
            rule_id="R40", rule_name="Decimal format", severity="warning",
            matched_text="mixed decimal separators", position=0,
            suggestion="Use consistent decimal format (dot or comma, not both)",
        ))
    return violations


def _check_r33(statement: str) -> list[Violation]:
    """Range checking."""
    violations = []
    pattern = re.compile(r'\bbetween\s+(\d+[\.,]?\d*)\s+and\s+(\d+[\.,]?\d*)\b', re.IGNORECASE)
    for m in pattern.finditer(statement):
        # Check if units follow the range
        after = statement[m.end():m.end() + 20].strip()
        if not after or after[0] in '.,:;)':
            violations.append(Violation(
                rule_id="R33", rule_name="Range checking", severity="warning",
                matched_text=m.group(), position=m.start(),
                suggestion="Add units to numeric range",
            ))
    return violations


# --- Rule registry ---

_ALL_RULES: list[tuple[str, str, str, str, callable]] = [
    ("R2", "Passive voice", "warning", "Flags passive voice constructions", _check_r2),
    ("R7", "Vague terms", "error", "Flags vague/ambiguous terms from INCOSE list", _check_r7),
    ("R8", "Escape clauses", "error", "Flags escape clause phrases", _check_r8),
    ("R9", "Open-ended clauses", "error", "Flags open-ended qualifiers (etc., and so on)", _check_r9),
    ("R10", "Superfluous infinitives", "error", "Flags 'be able to', 'be capable of'", _check_r10),
    ("R15", "Logical and/or", "error", "Flags 'and/or' usage", _check_r15),
    ("R16", "Negatives", "warning", "Flags negative requirements", _check_r16),
    ("R19", "Combinators", "warning", "Flags multiple 'shall' clauses combined with and/or", _check_r19),
    ("R20", "Purpose phrases", "warning", "Flags 'in order to', 'so that', etc.", _check_r20),
    ("R21", "Parentheses", "warning", "Flags parenthetical content", _check_r21),
    ("R24", "Pronouns", "error", "Flags pronoun usage (ambiguous references)", _check_r24),
    ("R26", "Absolutes", "error", "Flags absolute terms (always, never, every)", _check_r26),
    ("R32", "Universal quantifiers", "warning", "Flags universal quantifiers (each, every, all)", _check_r32),
    ("R33", "Range checking", "warning", "Flags numeric ranges missing units", _check_r33),
    ("R35", "Temporal dependencies", "warning", "Flags temporal keywords for precision review", _check_r35),
    ("R40", "Decimal format", "warning", "Flags inconsistent decimal separators", _check_r40),
]

_RULE_MAP = {rule_id: fn for rule_id, _, _, _, fn in _ALL_RULES}


# --- Public API ---

def check_requirement(statement: str) -> list[Violation]:
    """Run all deterministic INCOSE checks on a requirement statement.

    Returns list of Violation objects sorted by position.
    """
    violations = []
    for _, _, _, _, fn in _ALL_RULES:
        violations.extend(fn(statement))
    violations.sort(key=lambda v: v.position)
    return violations


def check_rule(statement: str, rule_id: str) -> Violation | None:
    """Run a single rule check. Returns first Violation if triggered, None otherwise."""
    fn = _RULE_MAP.get(rule_id)
    if fn is None:
        raise ValueError(f"Unknown rule: {rule_id}")
    results = fn(statement)
    return results[0] if results else None


def list_rules() -> list[RuleInfo]:
    """Return metadata for all available deterministic rules."""
    return [
        RuleInfo(
            rule_id=rule_id, rule_name=name, severity=severity,
            description=desc, detection_tier="deterministic",
        )
        for rule_id, name, severity, desc, _ in _ALL_RULES
    ]


# --- CLI ---


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="INCOSE quality rules checker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # check
    sp = subparsers.add_parser("check", help="Check a single requirement statement")
    sp.add_argument("statement", help="Requirement statement to check")

    # check-all
    sp = subparsers.add_parser("check-all", help="Check all requirements in a registry")
    sp.add_argument("--registry", required=True, type=lambda p: _shared_validate_path(p, [".json"]), help="Path to requirements_registry.json")

    # rules
    subparsers.add_parser("rules", help="List all available rules")

    args = parser.parse_args()

    if args.command == "check":
        violations = check_requirement(args.statement)
        print(json.dumps([asdict(v) for v in violations], indent=2))

    elif args.command == "check-all":
        with open(args.registry) as f:
            registry = json.load(f)
        results = {}
        reqs = registry if isinstance(registry, list) else registry.get("requirements", [])
        for req in reqs:
            req_id = req.get("id", "unknown")
            statement = req.get("statement", "")
            violations = check_requirement(statement)
            results[req_id] = [asdict(v) for v in violations]
        print(json.dumps(results, indent=2))

    elif args.command == "rules":
        rules = list_rules()
        print(json.dumps([asdict(r) for r in rules], indent=2))


if __name__ == "__main__":
    main()
