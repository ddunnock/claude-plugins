#!/usr/bin/env python3
"""
Plan Validation Script

Validates implementation plan files for completeness and consistency.
Checks:
- Required sections present
- Requirements traceability
- Architecture decision format
- Phase definitions
- Cross-references validity
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict


class ValidationIssue(TypedDict):
    severity: str  # ERROR, WARNING, INFO
    location: str
    message: str
    suggestion: str


@dataclass
class ValidationResult:
    valid: bool
    issues: list[ValidationIssue]
    stats: dict


# Required sections for simple plan
SIMPLE_PLAN_SECTIONS = [
    "Overview",
    "Requirements Mapping",
    "Architecture Decisions",
    "Implementation Approach",
    "Verification Strategy",
]

# Required sections for master plan
MASTER_PLAN_SECTIONS = [
    "Overview",
    "Domain Overview",
    "Cross-Domain Concerns",
    "Execution Order",
]

# Required sections for domain plan
DOMAIN_PLAN_SECTIONS = [
    "Domain Info",
    "Scope",
    "Requirements Covered",
    "Implementation Approach",
    "Integration Points",
]


def validate_plan(plan_path: str | Path) -> ValidationResult:
    """
    Validate a plan file.

    Args:
        plan_path: Path to the plan file

    Returns:
        ValidationResult with validity status, issues, and statistics
    """
    plan_path = Path(plan_path)
    issues: list[ValidationIssue] = []
    stats = {
        "sections_found": 0,
        "requirements_mapped": 0,
        "architecture_decisions": 0,
        "phases_defined": 0,
    }

    if not plan_path.exists():
        return ValidationResult(
            valid=False,
            issues=[{
                "severity": "ERROR",
                "location": str(plan_path),
                "message": "Plan file not found",
                "suggestion": "Create plan file or check path"
            }],
            stats=stats
        )

    try:
        content = plan_path.read_text()
    except Exception as e:
        return ValidationResult(
            valid=False,
            issues=[{
                "severity": "ERROR",
                "location": str(plan_path),
                "message": f"Failed to read plan file: {e}",
                "suggestion": "Check file permissions"
            }],
            stats=stats
        )

    # Determine plan type
    is_master = "Domain Overview" in content or "Master" in content.split("\n")[0]
    is_domain = "Domain Info" in content or "Parent Plan" in content

    if is_master:
        required_sections = MASTER_PLAN_SECTIONS
        plan_type = "master"
    elif is_domain:
        required_sections = DOMAIN_PLAN_SECTIONS
        plan_type = "domain"
    else:
        required_sections = SIMPLE_PLAN_SECTIONS
        plan_type = "simple"

    # Check required sections
    sections_found = []
    for section in required_sections:
        pattern = rf"^##\s+{re.escape(section)}"
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            sections_found.append(section)
        else:
            issues.append({
                "severity": "ERROR",
                "location": plan_path.name,
                "message": f"Missing required section: {section}",
                "suggestion": f"Add '## {section}' section to plan"
            })

    stats["sections_found"] = len(sections_found)

    # Check requirements mapping
    req_pattern = r"REQ-\d+"
    requirements = re.findall(req_pattern, content)
    stats["requirements_mapped"] = len(set(requirements))

    if not requirements and plan_type != "master":
        issues.append({
            "severity": "WARNING",
            "location": plan_path.name,
            "message": "No requirements (REQ-XXX) found in plan",
            "suggestion": "Add requirements mapping table"
        })

    # Check architecture decisions
    ad_pattern = r"###\s+(AD|DAD|GAD)-\d+"
    decisions = re.findall(ad_pattern, content)
    stats["architecture_decisions"] = len(decisions)

    # Validate AD format
    ad_sections = re.findall(r"###\s+((?:AD|DAD|GAD)-\d+).*?(?=###|\Z)", content, re.DOTALL)
    for ad_match in re.finditer(r"###\s+((?:AD|DAD|GAD)-\d+).*?(?=###|\Z)", content, re.DOTALL):
        ad_content = ad_match.group(0)
        ad_id = re.search(r"((?:AD|DAD|GAD)-\d+)", ad_content).group(1)

        # Check for required AD fields
        required_ad_fields = ["Context", "Decision", "Rationale"]
        for field in required_ad_fields:
            if field.lower() not in ad_content.lower():
                issues.append({
                    "severity": "WARNING",
                    "location": f"{plan_path.name}:{ad_id}",
                    "message": f"Architecture decision {ad_id} missing '{field}' field",
                    "suggestion": f"Add **{field}**: section to {ad_id}"
                })

    # Check phase definitions
    phase_pattern = r"###\s+Phase\s+\d+"
    phases = re.findall(phase_pattern, content)
    stats["phases_defined"] = len(phases)

    if not phases and plan_type != "master":
        issues.append({
            "severity": "WARNING",
            "location": plan_path.name,
            "message": "No phases defined in Implementation Approach",
            "suggestion": "Add '### Phase N: [Name]' subsections"
        })

    # Validate phase format
    for phase_match in re.finditer(r"###\s+(Phase\s+\d+).*?(?=###\s+Phase|\Z)", content, re.DOTALL):
        phase_content = phase_match.group(0)
        phase_name = phase_match.group(1)

        required_phase_fields = ["Objective", "Scope"]
        for field in required_phase_fields:
            if field.lower() not in phase_content.lower():
                issues.append({
                    "severity": "INFO",
                    "location": f"{plan_path.name}:{phase_name}",
                    "message": f"{phase_name} missing '{field}' field",
                    "suggestion": f"Add **{field}**: to {phase_name}"
                })

    # Check for broken internal references
    ref_pattern = r"\[(.*?)\]\((#.*?)\)"
    for match in re.finditer(ref_pattern, content):
        link_text = match.group(1)
        link_target = match.group(2)

        # Check if anchor exists
        anchor_name = link_target[1:].lower().replace("-", " ")
        if anchor_name not in content.lower():
            issues.append({
                "severity": "WARNING",
                "location": plan_path.name,
                "message": f"Broken internal link: {link_target}",
                "suggestion": f"Fix link target or create section '{link_text}'"
            })

    # Check for master plan domain references
    if is_master:
        domain_refs = re.findall(r"plans/[\w-]+-plan\.md", content)
        plan_dir = plan_path.parent / "plans"

        for ref in domain_refs:
            domain_plan = plan_path.parent / ref
            if not domain_plan.exists():
                issues.append({
                    "severity": "ERROR",
                    "location": f"{plan_path.name}:{ref}",
                    "message": f"Referenced domain plan not found: {ref}",
                    "suggestion": f"Create {ref} or update reference"
                })

    # Determine overall validity
    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    valid = error_count == 0

    return ValidationResult(valid=valid, issues=issues, stats=stats)


def validate_all_plans(project_path: str | Path) -> dict:
    """
    Validate all plan files in a project.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with validation results for all plans
    """
    project_path = Path(project_path)
    resources_dir = project_path / ".claude" / "resources"

    results = {}

    if not resources_dir.exists():
        return {
            "error": "Resources directory not found",
            "path": str(resources_dir)
        }

    # Find all plan files
    plan_files = list(resources_dir.glob("*plan*.md")) + list(resources_dir.glob("plans/*.md"))

    for plan_file in plan_files:
        result = validate_plan(plan_file)
        results[str(plan_file.relative_to(project_path))] = {
            "valid": result.valid,
            "issues": result.issues,
            "stats": result.stats
        }

    return results


def generate_report(results: dict, format: str = "text") -> str:
    """Generate validation report."""
    if format == "json":
        return json.dumps(results, indent=2)

    lines = ["Plan Validation Report", "=" * 50, ""]

    if "error" in results:
        lines.append(f"Error: {results['error']}")
        return "\n".join(lines)

    total_valid = 0
    total_invalid = 0
    all_issues = []

    for plan_path, result in results.items():
        if result["valid"]:
            total_valid += 1
            status = "✓ VALID"
        else:
            total_invalid += 1
            status = "✗ INVALID"

        lines.extend([
            f"\n{plan_path}",
            f"  Status: {status}",
            f"  Stats:",
            f"    - Sections: {result['stats']['sections_found']}",
            f"    - Requirements: {result['stats']['requirements_mapped']}",
            f"    - Architecture Decisions: {result['stats']['architecture_decisions']}",
            f"    - Phases: {result['stats']['phases_defined']}",
        ])

        if result["issues"]:
            lines.append(f"  Issues ({len(result['issues'])}):")
            for issue in result["issues"]:
                lines.append(f"    [{issue['severity']}] {issue['message']}")
                if issue["suggestion"]:
                    lines.append(f"             → {issue['suggestion']}")

            all_issues.extend(result["issues"])

    lines.extend([
        "",
        "=" * 50,
        f"Summary: {total_valid} valid, {total_invalid} invalid",
        f"Total issues: {len(all_issues)}",
        f"  - Errors: {sum(1 for i in all_issues if i['severity'] == 'ERROR')}",
        f"  - Warnings: {sum(1 for i in all_issues if i['severity'] == 'WARNING')}",
        f"  - Info: {sum(1 for i in all_issues if i['severity'] == 'INFO')}",
    ])

    return "\n".join(lines)



def _validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    resolved = os.path.realpath(filepath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)
    return resolved


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate implementation plan files"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=os.getcwd(),
        help="Path to plan file or project root (default: current directory)"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )

    args = parser.parse_args()

    if args.path:
        args.path = os.path.realpath(args.path)

    path = Path(args.path)

    if path.is_file():
        # Single file validation
        result = validate_plan(path)
        results = {str(path): {
            "valid": result.valid,
            "issues": result.issues,
            "stats": result.stats
        }}
    else:
        # Project-wide validation
        results = validate_all_plans(path)

    report = generate_report(results, args.format)
    print(report)

    # Exit code
    if "error" in results:
        sys.exit(1)

    has_errors = any(
        any(i["severity"] == "ERROR" for i in r.get("issues", []))
        for r in results.values() if isinstance(r, dict)
    )

    has_warnings = any(
        any(i["severity"] == "WARNING" for i in r.get("issues", []))
        for r in results.values() if isinstance(r, dict)
    )

    if has_errors or (args.strict and has_warnings):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
