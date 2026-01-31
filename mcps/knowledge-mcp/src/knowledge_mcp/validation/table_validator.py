"""Query-based table validation for critical RCCA tables."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from knowledge_mcp.models.chunk import KnowledgeChunk

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation test."""

    table_name: str
    passed: bool
    details: dict[str, bool] = field(default_factory=lambda: {})
    chunks_retrieved: int = 0
    recommendation: str = ""
    has_warnings: bool = False


class SearcherProtocol(Protocol):
    """Protocol for searcher dependency injection."""

    async def search(
        self,
        query: str,
        collection: str,
        n_results: int = 10,
    ) -> list[KnowledgeChunk]: ...


class TableValidator:
    """Validates critical RCCA lookup tables after ingestion.

    Uses query-based validation to verify tables are retrievable,
    not just parseable. Tests what RCCA skills actually need.

    Example:
        >>> from knowledge_mcp.search import SemanticSearcher
        >>> from knowledge_mcp.validation import TableValidator
        >>>
        >>> validator = TableValidator(searcher, "standards_collection")
        >>> result = await validator.validate_ap_matrix()
        >>> if not result.passed:
        ...     print(result.recommendation)
    """

    def __init__(self, searcher: SearcherProtocol, collection: str) -> None:
        """
        Initialize table validator.

        Args:
            searcher: Object implementing SearcherProtocol (e.g., SemanticSearcher).
            collection: Name of the collection to validate.
        """
        self.searcher = searcher
        self.collection = collection

    async def validate_ap_matrix(self) -> ValidationResult:
        """Validate AIAG-VDA Action Priority lookup table.

        The AP matrix is a 10x10 decision table mapping Severity (1-10)
        and Occurrence (1-10) to Action Priority (H/M/L).

        Critical for: FMEA skill Step 5 (risk prioritization)

        Returns:
            ValidationResult with pass/fail status and recommendations.
        """
        queries = [
            "Action Priority table Severity Occurrence matrix",
            "AP rating High Medium Low lookup table",
            "AIAG-VDA FMEA Action Priority decision table",
        ]

        all_chunks = await self._run_queries(queries)

        checks = {
            "table_found": self._check_table_found(
                all_chunks, ["action priority", "ap rating"]
            ),
            "severity_scale": self._check_pattern(
                all_chunks, r"severity.*\b([1-9]|10)\b"
            ),
            "occurrence_scale": self._check_pattern(
                all_chunks, r"occurrence.*\b([1-9]|10)\b"
            ),
            "ap_values": self._check_pattern(
                all_chunks, r"\b(high|medium|low|h|m|l)\b"
            ),
        }

        passed = all(checks.values())

        return ValidationResult(
            table_name="AIAG-VDA Action Priority Matrix",
            passed=passed,
            details=checks,
            chunks_retrieved=len(all_chunks),
            recommendation="" if passed else self._get_ap_recommendation(checks),
        )

    async def validate_mil_std_severity(self) -> ValidationResult:
        """Validate MIL-STD-882E Severity Categories table.

        Table I defines severity categories (1-4):
        Catastrophic, Critical, Marginal, Negligible.

        Critical for: Problem Definition severity classification

        Returns:
            ValidationResult with pass/fail status and recommendations.
        """
        queries = [
            "MIL-STD-882 severity categories table",
            "hazard severity categories catastrophic critical",
            "severity classification personnel environmental monetary",
        ]

        all_chunks = await self._run_queries(queries)

        checks = {
            "table_found": self._check_table_found(
                all_chunks, ["severity", "categories"]
            ),
            "catastrophic_present": self._check_pattern(all_chunks, r"catastrophic"),
            "critical_present": self._check_pattern(all_chunks, r"critical"),
            "marginal_present": self._check_pattern(all_chunks, r"marginal"),
            "negligible_present": self._check_pattern(all_chunks, r"negligible"),
        }

        passed = all(checks.values())

        return ValidationResult(
            table_name="MIL-STD-882E Severity Categories",
            passed=passed,
            details=checks,
            chunks_retrieved=len(all_chunks),
            recommendation=""
            if passed
            else (
                "Ingest MIL-STD-882E (Table I - Severity Categories). "
                "See docs/standards-acquisition/mil-std-882e.md"
            ),
        )

    async def validate_iso9001_capa(self) -> ValidationResult:
        """Validate ISO 9001:2015 CAPA templates.

        Clause 10.2 defines corrective action requirements.

        Critical for: RCCA Master D5 (CAPA recommendations)

        Returns:
            ValidationResult with pass/fail status and recommendations.
        """
        queries = [
            "ISO 9001 corrective action process clause 10.2",
            "nonconformity corrective action requirements",
            "CAPA corrective and preventive action template",
        ]

        all_chunks = await self._run_queries(queries)

        checks = {
            "clause_found": self._check_table_found(
                all_chunks, ["corrective action", "10.2"]
            ),
            "nonconformity_present": self._check_pattern(all_chunks, r"nonconformit"),
            "root_cause_present": self._check_pattern(
                all_chunks, r"root cause|cause.*analysis"
            ),
            "action_required": self._check_pattern(
                all_chunks, r"shall|must|required"
            ),
        }

        passed = all(checks.values())

        return ValidationResult(
            table_name="ISO 9001:2015 CAPA Templates",
            passed=passed,
            details=checks,
            chunks_retrieved=len(all_chunks),
            recommendation=""
            if passed
            else (
                "Ingest ISO 9001:2015 Clause 10.2 (Corrective Action). "
                "See docs/standards-acquisition/iso-9001-2015.md"
            ),
        )

    async def validate_all(self) -> list[ValidationResult]:
        """Run all critical table validations.

        Returns:
            List of ValidationResult for all critical tables.
        """
        return [
            await self.validate_ap_matrix(),
            await self.validate_mil_std_severity(),
            await self.validate_iso9001_capa(),
        ]

    async def _run_queries(self, queries: list[str]) -> list[KnowledgeChunk]:
        """Run multiple queries in parallel and deduplicate results.

        Args:
            queries: List of query strings to search for.

        Returns:
            Deduplicated list of KnowledgeChunk results.
        """
        # Run queries in parallel
        tasks = [
            self.searcher.search(query, collection=self.collection, n_results=10)
            for query in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful results, log failures
        all_chunks: list[KnowledgeChunk] = []
        for i, result in enumerate(results):
            if isinstance(result, BaseException):
                logger.warning(
                    "Validation query failed: %s - %s",
                    queries[i][:50],
                    type(result).__name__,
                )
            else:
                # result is list[KnowledgeChunk] here
                all_chunks.extend(result)

        # Deduplicate by chunk ID
        seen_ids: set[str] = set()
        unique_chunks: list[KnowledgeChunk] = []
        for chunk in all_chunks:
            if chunk.id not in seen_ids:
                seen_ids.add(chunk.id)
                unique_chunks.append(chunk)

        return unique_chunks

    def _check_table_found(
        self, chunks: list[KnowledgeChunk], keywords: list[str]
    ) -> bool:
        """Check if any chunk contains all required keywords.

        Args:
            chunks: List of chunks to check.
            keywords: List of keywords that must all be present.

        Returns:
            True if any chunk contains all keywords.
        """
        for chunk in chunks:
            content_lower = chunk.content.lower()
            if all(kw in content_lower for kw in keywords):
                return True
        return False

    def _check_pattern(self, chunks: list[KnowledgeChunk], pattern: str) -> bool:
        """Check if any chunk matches the regex pattern.

        Args:
            chunks: List of chunks to check.
            pattern: Regex pattern to match.

        Returns:
            True if any chunk matches the pattern.
        """
        for chunk in chunks:
            if re.search(pattern, chunk.content, re.IGNORECASE):
                return True
        return False

    def _get_ap_recommendation(self, checks: dict[str, bool]) -> str:
        """Generate recommendation for AP matrix validation failure.

        Args:
            checks: Dictionary of check results.

        Returns:
            Recommendation string for fixing the validation failure.
        """
        if not checks["table_found"]:
            return (
                "AP table not found. Ingest AIAG-VDA FMEA Handbook (2019). "
                "See docs/standards-acquisition/aiag-vda-2019.md"
            )
        if not checks["severity_scale"] or not checks["occurrence_scale"]:
            return (
                "Severity/Occurrence scales incomplete. "
                "Verify AIAG-VDA 2019 edition (not legacy FMEA-4)."
            )
        return "Unknown validation failure. Run with --verbose for details."
