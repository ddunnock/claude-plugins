#!/usr/bin/env python3
"""
Artifact Analysis Script

Deterministic, read-only analysis of project artifacts for consistency
and completeness. Produces stable finding IDs for tracking across runs.

Categories:
- GAPS: Missing required elements
- INCONSISTENCIES: Contradictions between artifacts
- AMBIGUITIES: Unclear or undefined items
- ORPHANS: Unreferenced elements
- ASSUMPTIONS: Untracked/unvalidated assumptions
"""

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TypedDict


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Category(Enum):
    GAPS = "GAPS"
    INCONSISTENCIES = "INCONSISTENCIES"
    AMBIGUITIES = "AMBIGUITIES"
    ORPHANS = "ORPHANS"
    ASSUMPTIONS = "ASSUMPTIONS"


@dataclass
class Finding:
    category: Category
    severity: Severity
    location: str
    description: str
    evidence: str = ""
    recommendation: str = ""

    @property
    def id(self) -> str:
        """Generate stable, deterministic finding ID."""
        content = f"{self.category.value}:{self.location}:{self.description}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"{self.category.value[:3]}-{hash_val}"


@dataclass
class AnalysisResult:
    findings: list[Finding] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    artifacts_analyzed: list[str] = field(default_factory=list)

    def add_finding(self, finding: Finding):
        self.findings.append(finding)

    def get_summary(self) -> dict:
        summary = {cat.value: {sev.value: 0 for sev in Severity} for cat in Category}
        for finding in self.findings:
            summary[finding.category.value][finding.severity.value] += 1
        return summary


class ArtifactAnalyzer:
    """Analyzer for project artifacts."""

    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path).resolve()
        self.claude_dir = self.project_path / ".claude"
        self.result = AnalysisResult()

    def analyze(self) -> AnalysisResult:
        """Run all analysis passes."""
        # Discover artifacts
        self._discover_artifacts()

        # Run analysis passes
        self._analyze_gaps()
        self._analyze_inconsistencies()
        self._analyze_ambiguities()
        self._analyze_orphans()
        self._analyze_assumptions()

        # Calculate metrics
        self._calculate_metrics()

        # Sort findings for deterministic output
        self.result.findings.sort(
            key=lambda f: (
                -list(Severity).index(f.severity),
                list(Category).index(f.category),
                f.id
            )
        )

        return self.result

    def _discover_artifacts(self):
        """Discover all analyzable artifacts."""
        artifacts = []

        # Memory files
        memory_dir = self.claude_dir / "memory"
        if memory_dir.exists():
            artifacts.extend(str(p) for p in memory_dir.glob("*.md"))

        # Resources (specs, plans)
        resources_dir = self.claude_dir / "resources"
        if resources_dir.exists():
            artifacts.extend(str(p) for p in resources_dir.glob("**/*.md"))

        self.result.artifacts_analyzed = sorted(artifacts)

    def _analyze_gaps(self):
        """Check for missing required elements."""
        # Check for constitution.md
        constitution = self.claude_dir / "memory" / "constitution.md"
        if not constitution.exists():
            self.result.add_finding(Finding(
                category=Category.GAPS,
                severity=Severity.CRITICAL,
                location=".claude/memory/constitution.md",
                description="Constitution file is missing",
                recommendation="Run /speckit.init to create foundation"
            ))

        # Check for spec files
        resources_dir = self.claude_dir / "resources"
        if resources_dir.exists():
            specs = list(resources_dir.glob("*spec*.md")) + list(resources_dir.glob("*requirement*.md"))
            plans = list(resources_dir.glob("*plan*.md"))
            tasks = list(resources_dir.glob("*task*.md"))

            # Check plan coverage
            if specs and not plans:
                self.result.add_finding(Finding(
                    category=Category.GAPS,
                    severity=Severity.HIGH,
                    location=str(resources_dir),
                    description="Specifications exist but no plans found",
                    recommendation="Run /speckit.plan to create implementation plans"
                ))

            # Check task coverage
            if plans and not tasks:
                self.result.add_finding(Finding(
                    category=Category.GAPS,
                    severity=Severity.MEDIUM,
                    location=str(resources_dir),
                    description="Plans exist but no tasks found",
                    recommendation="Run /speckit.tasks to generate implementation tasks"
                ))

            # Check task acceptance criteria
            for task_file in tasks:
                self._check_task_acceptance_criteria(task_file)

    def _check_task_acceptance_criteria(self, task_file: Path):
        """Check if tasks have acceptance criteria."""
        try:
            content = task_file.read_text()
            # Find tasks without acceptance criteria
            task_pattern = r"### (TASK-\d+):.*?(?=### TASK-|\Z)"
            tasks = re.findall(task_pattern, content, re.DOTALL)

            for i, task_match in enumerate(re.finditer(task_pattern, content, re.DOTALL)):
                task_content = task_match.group(0)
                task_id = re.search(r"TASK-\d+", task_content)
                if task_id and "Acceptance Criteria" not in task_content:
                    self.result.add_finding(Finding(
                        category=Category.GAPS,
                        severity=Severity.MEDIUM,
                        location=f"{task_file.name}:{task_id.group()}",
                        description=f"Task {task_id.group()} has no acceptance criteria",
                        recommendation="Add acceptance criteria to verify task completion"
                    ))
        except Exception:
            pass

    def _analyze_inconsistencies(self):
        """Check for contradictions between artifacts."""
        # Check for conflicting requirements
        resources_dir = self.claude_dir / "resources"
        if not resources_dir.exists():
            return

        # Look for duplicate requirement IDs
        req_locations: dict[str, list[str]] = {}

        for spec_file in resources_dir.glob("**/*.md"):
            try:
                content = spec_file.read_text()
                req_ids = re.findall(r"REQ-\d+", content)
                for req_id in req_ids:
                    if req_id not in req_locations:
                        req_locations[req_id] = []
                    if str(spec_file) not in req_locations[req_id]:
                        req_locations[req_id].append(str(spec_file))
            except Exception:
                pass

        # Check for IDs defined in multiple places (potential conflict)
        for req_id, locations in req_locations.items():
            if len(locations) > 2:  # In more than 2 files might indicate conflict
                self.result.add_finding(Finding(
                    category=Category.INCONSISTENCIES,
                    severity=Severity.MEDIUM,
                    location=", ".join(Path(l).name for l in locations),
                    description=f"Requirement {req_id} appears in {len(locations)} files",
                    evidence=f"Found in: {', '.join(locations)}",
                    recommendation="Verify requirement is consistently defined"
                ))

    def _analyze_ambiguities(self):
        """Detect unclear specifications."""
        resources_dir = self.claude_dir / "resources"
        if not resources_dir.exists():
            return

        # Patterns that indicate ambiguity
        ambiguity_patterns = [
            (r"\[TBD\]", Severity.HIGH, "TBD marker found"),
            (r"\[TODO\]", Severity.HIGH, "TODO marker found"),
            (r"\[NEEDS CLARIFICATION\]", Severity.HIGH, "Needs clarification marker"),
            (r"\bshould\b(?!\s+not)", Severity.MEDIUM, "Vague 'should' language (use 'must')"),
            (r"\bmight\b", Severity.MEDIUM, "Uncertain language 'might'"),
            (r"\bprobably\b", Severity.MEDIUM, "Uncertain language 'probably'"),
            (r"\bpossibly\b", Severity.MEDIUM, "Uncertain language 'possibly'"),
            (r"\betc\.?\b", Severity.LOW, "Incomplete list with 'etc'"),
            (r"\band so on\b", Severity.LOW, "Incomplete list"),
        ]

        for spec_file in resources_dir.glob("**/*.md"):
            try:
                content = spec_file.read_text()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern, severity, desc in ambiguity_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.result.add_finding(Finding(
                                category=Category.AMBIGUITIES,
                                severity=severity,
                                location=f"{spec_file.name}:{line_num}",
                                description=desc,
                                evidence=line.strip()[:100],
                                recommendation="Clarify with specific, definite language"
                            ))
            except Exception:
                pass

    def _analyze_orphans(self):
        """Find unreferenced elements."""
        resources_dir = self.claude_dir / "resources"
        if not resources_dir.exists():
            return

        # Collect all requirement IDs from specs
        spec_reqs: set[str] = set()
        plan_reqs: set[str] = set()

        for file in resources_dir.glob("**/*.md"):
            try:
                content = file.read_text()
                req_ids = set(re.findall(r"REQ-\d+", content))

                if "spec" in file.name.lower() or "requirement" in file.name.lower():
                    spec_reqs.update(req_ids)
                elif "plan" in file.name.lower():
                    plan_reqs.update(req_ids)
            except Exception:
                pass

        # Find orphan requirements (in spec but not in plan)
        orphan_reqs = spec_reqs - plan_reqs
        for req_id in sorted(orphan_reqs):
            self.result.add_finding(Finding(
                category=Category.ORPHANS,
                severity=Severity.HIGH,
                location="resources/",
                description=f"Requirement {req_id} has no plan coverage",
                recommendation=f"Add {req_id} to implementation plan or mark as out of scope"
            ))

    def _analyze_assumptions(self):
        """Track unvalidated assumptions."""
        resources_dir = self.claude_dir / "resources"
        if not resources_dir.exists():
            return

        # Look for assumption markers
        assumption_patterns = [
            r"\[ASSUMPTION\]",
            r"\[ASSUMES?\]",
            r"\bassume[sd]?\s+that\b",
            r"\bassuming\b",
        ]

        for spec_file in resources_dir.glob("**/*.md"):
            try:
                content = spec_file.read_text()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern in assumption_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.result.add_finding(Finding(
                                category=Category.ASSUMPTIONS,
                                severity=Severity.MEDIUM,
                                location=f"{spec_file.name}:{line_num}",
                                description="Unvalidated assumption found",
                                evidence=line.strip()[:100],
                                recommendation="Validate assumption or document as constraint"
                            ))
            except Exception:
                pass

    def _calculate_metrics(self):
        """Calculate coverage and quality metrics."""
        resources_dir = self.claude_dir / "resources"

        metrics = {
            "artifacts_count": len(self.result.artifacts_analyzed),
            "findings_count": len(self.result.findings),
            "coverage": {},
        }

        if resources_dir.exists():
            specs = list(resources_dir.glob("*spec*.md")) + list(resources_dir.glob("*requirement*.md"))
            plans = list(resources_dir.glob("*plan*.md"))
            tasks = list(resources_dir.glob("*task*.md"))

            # Calculate coverage percentages
            if specs:
                # Count requirements with plan coverage
                spec_reqs = set()
                plan_reqs = set()

                for f in specs:
                    try:
                        spec_reqs.update(re.findall(r"REQ-\d+", f.read_text()))
                    except Exception:
                        pass

                for f in plans:
                    try:
                        plan_reqs.update(re.findall(r"REQ-\d+", f.read_text()))
                    except Exception:
                        pass

                if spec_reqs:
                    covered = len(spec_reqs & plan_reqs)
                    metrics["coverage"]["spec_to_plan"] = round(covered / len(spec_reqs) * 100)

        self.result.metrics = metrics


def generate_report(result: AnalysisResult, format: str = "markdown") -> str:
    """Generate analysis report."""
    if format == "json":
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "artifacts_analyzed": result.artifacts_analyzed,
            "summary": result.get_summary(),
            "metrics": result.metrics,
            "findings": [
                {
                    "id": f.id,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "location": f.location,
                    "description": f.description,
                    "evidence": f.evidence,
                    "recommendation": f.recommendation,
                }
                for f in result.findings
            ]
        }, indent=2)

    # Markdown format
    lines = [
        "# Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Artifacts Analyzed: {len(result.artifacts_analyzed)}",
        "",
        "## Summary",
        "",
        "| Category | Critical | High | Medium | Low | Total |",
        "|----------|----------|------|--------|-----|-------|",
    ]

    summary = result.get_summary()
    for cat in Category:
        counts = summary[cat.value]
        total = sum(counts.values())
        lines.append(
            f"| {cat.value} | {counts['CRITICAL']} | {counts['HIGH']} | "
            f"{counts['MEDIUM']} | {counts['LOW']} | {total} |"
        )

    total_by_sev = {sev.value: 0 for sev in Severity}
    for cat_counts in summary.values():
        for sev, count in cat_counts.items():
            total_by_sev[sev] += count

    lines.append(
        f"| **Total** | **{total_by_sev['CRITICAL']}** | **{total_by_sev['HIGH']}** | "
        f"**{total_by_sev['MEDIUM']}** | **{total_by_sev['LOW']}** | "
        f"**{sum(total_by_sev.values())}** |"
    )

    if result.metrics.get("coverage"):
        lines.extend([
            "",
            "## Coverage Metrics",
            "",
            "| Traceability | Coverage |",
            "|--------------|----------|",
        ])
        for key, value in result.metrics["coverage"].items():
            lines.append(f"| {key.replace('_', ' → ')} | {value}% |")

    lines.extend(["", "## Findings", ""])

    # Group by severity
    for severity in Severity:
        sev_findings = [f for f in result.findings if f.severity == severity]
        if sev_findings:
            lines.append(f"### {severity.value} ({len(sev_findings)})")
            lines.append("")

            for finding in sev_findings:
                lines.extend([
                    f"#### {finding.id} [{finding.severity.value}]",
                    f"**Category**: {finding.category.value}",
                    f"**Location**: {finding.location}",
                    "",
                    f"**Description**: {finding.description}",
                ])

                if finding.evidence:
                    lines.extend([
                        "",
                        f"**Evidence**: {finding.evidence}",
                    ])

                if finding.recommendation:
                    lines.extend([
                        "",
                        f"**Recommendation**: {finding.recommendation}",
                    ])

                lines.extend(["", "---", ""])

    return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze project artifacts for consistency and completeness"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to project root (default: current directory)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--category",
        choices=[c.value.lower() for c in Category],
        help="Filter by category"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all findings including low severity"
    )

    args = parser.parse_args()

    analyzer = ArtifactAnalyzer(args.project_path)
    result = analyzer.analyze()

    # Filter by category if specified
    if args.category:
        cat = Category[args.category.upper()]
        result.findings = [f for f in result.findings if f.category == cat]

    # Filter low severity unless verbose
    if not args.verbose:
        result.findings = [f for f in result.findings if f.severity != Severity.LOW]

    report = generate_report(result, args.format)
    print(report)

    # Exit code based on severity
    severities = [f.severity for f in result.findings]
    if Severity.CRITICAL in severities:
        sys.exit(2)
    elif Severity.HIGH in severities:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
