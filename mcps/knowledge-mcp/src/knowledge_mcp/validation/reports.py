"""User-facing validation report formatting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from knowledge_mcp.validation.table_validator import ValidationResult


@dataclass
class ValidationReport:
    """Aggregated validation report for CLI output."""

    collection: str
    results: list[ValidationResult] = field(default_factory=lambda: [])

    @property
    def all_passed(self) -> bool:
        """True if all validation tests passed."""
        return all(r.passed for r in self.results)

    @property
    def passed_count(self) -> int:
        """Count of passed validation tests."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        """Count of failed validation tests."""
        return sum(1 for r in self.results if not r.passed)

    @property
    def warning_count(self) -> int:
        """Count of tests with warnings."""
        return sum(1 for r in self.results if r.has_warnings)

    def format_summary(self) -> str:
        """Format summary line for CLI output."""
        total = len(self.results)
        if self.all_passed:
            return f"PASSED: {self.passed_count}/{total} tests passed"
        return f"FAILED: {self.failed_count}/{total} tests failed"

    def get_recommendations(self) -> list[str]:
        """Get all recommendations from failed tests."""
        return [
            r.recommendation
            for r in self.results
            if not r.passed and r.recommendation
        ]
