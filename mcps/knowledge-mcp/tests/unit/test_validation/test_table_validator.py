"""Unit tests for TableValidator."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest

from knowledge_mcp.validation.table_validator import TableValidator, ValidationResult


@dataclass
class MockChunk:
    """Mock KnowledgeChunk for testing."""

    id: str
    content: str
    chunk_type: str = "content"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_passed_result(self) -> None:
        """Test creating a passed validation result."""
        result = ValidationResult(
            table_name="Test Table",
            passed=True,
            details={"check1": True, "check2": True},
            chunks_retrieved=5,
        )
        assert result.passed is True
        assert result.chunks_retrieved == 5
        assert result.recommendation == ""

    def test_failed_result_with_recommendation(self) -> None:
        """Test creating a failed validation result with recommendation."""
        result = ValidationResult(
            table_name="Test Table",
            passed=False,
            details={"check1": False},
            recommendation="Fix the issue",
        )
        assert result.passed is False
        assert result.recommendation == "Fix the issue"

    def test_has_warnings_default_false(self) -> None:
        """Test has_warnings defaults to False."""
        result = ValidationResult(
            table_name="Test Table",
            passed=True,
        )
        assert result.has_warnings is False

    def test_details_default_empty(self) -> None:
        """Test details defaults to empty dict."""
        result = ValidationResult(
            table_name="Test Table",
            passed=True,
        )
        assert result.details == {}


class TestTableValidator:
    """Tests for TableValidator class."""

    @pytest.fixture
    def mock_searcher(self) -> AsyncMock:
        """Create a mock searcher."""
        return AsyncMock()

    @pytest.fixture
    def validator(self, mock_searcher: AsyncMock) -> TableValidator:
        """Create validator with mock searcher."""
        return TableValidator(mock_searcher, "test_collection")

    @pytest.mark.asyncio
    async def test_validate_ap_matrix_passes_with_complete_table(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test AP matrix validation passes when table is complete."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content=(
                    "Action Priority table with AP rating levels: "
                    "Severity 1-10, Occurrence 1-10, values High Medium Low"
                ),
            ),
        ]

        result = await validator.validate_ap_matrix()

        assert result.passed is True
        assert result.table_name == "AIAG-VDA Action Priority Matrix"
        assert result.details["table_found"] is True
        assert result.details["ap_values"] is True

    @pytest.mark.asyncio
    async def test_validate_ap_matrix_fails_when_not_found(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test AP matrix validation fails when table is missing."""
        mock_searcher.search.return_value = []  # No results

        result = await validator.validate_ap_matrix()

        assert result.passed is False
        assert "not found" in result.recommendation.lower()

    @pytest.mark.asyncio
    async def test_validate_ap_matrix_fails_with_incomplete_scales(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test AP matrix validation fails with incomplete severity/occurrence."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content="Action Priority table AP rating High Medium Low",
            ),
        ]

        result = await validator.validate_ap_matrix()

        # Table found, AP values found, but scales missing
        assert result.passed is False
        assert result.details["table_found"] is True
        assert result.details["ap_values"] is True
        assert result.details["severity_scale"] is False
        assert result.details["occurrence_scale"] is False

    @pytest.mark.asyncio
    async def test_validate_mil_std_severity_passes(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test MIL-STD severity validation passes with categories."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content=(
                    "Severity Categories: 1-Catastrophic, 2-Critical, "
                    "3-Marginal, 4-Negligible"
                ),
            ),
        ]

        result = await validator.validate_mil_std_severity()

        assert result.passed is True
        assert result.table_name == "MIL-STD-882E Severity Categories"
        assert result.details["catastrophic_present"] is True
        assert result.details["critical_present"] is True
        assert result.details["marginal_present"] is True
        assert result.details["negligible_present"] is True

    @pytest.mark.asyncio
    async def test_validate_mil_std_severity_fails_missing_categories(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test MIL-STD severity validation fails with missing categories."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content="Severity Categories: Catastrophic and Critical only",
            ),
        ]

        result = await validator.validate_mil_std_severity()

        assert result.passed is False
        assert result.details["marginal_present"] is False
        assert result.details["negligible_present"] is False

    @pytest.mark.asyncio
    async def test_validate_iso9001_capa_passes(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test ISO 9001 CAPA validation passes with clause 10.2."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content=(
                    "Clause 10.2 Corrective Action: Organization shall take action "
                    "to eliminate root cause of nonconformity"
                ),
            ),
        ]

        result = await validator.validate_iso9001_capa()

        assert result.passed is True
        assert result.table_name == "ISO 9001:2015 CAPA Templates"
        assert result.details["clause_found"] is True
        assert result.details["nonconformity_present"] is True
        assert result.details["root_cause_present"] is True
        assert result.details["action_required"] is True

    @pytest.mark.asyncio
    async def test_validate_iso9001_capa_fails_no_clause_reference(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test ISO 9001 CAPA validation fails without 10.2 reference."""
        mock_searcher.search.return_value = [
            MockChunk(
                id="chunk-1",
                content="Generic corrective action process",
            ),
        ]

        result = await validator.validate_iso9001_capa()

        assert result.passed is False
        assert "10.2" not in result.details or result.details["clause_found"] is False

    @pytest.mark.asyncio
    async def test_validate_all_returns_list(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test validate_all returns results for all tables."""
        mock_searcher.search.return_value = []  # All fail for simplicity

        results = await validator.validate_all()

        assert len(results) == 3
        assert all(isinstance(r, ValidationResult) for r in results)
        # Verify table names
        table_names = {r.table_name for r in results}
        assert "AIAG-VDA Action Priority Matrix" in table_names
        assert "MIL-STD-882E Severity Categories" in table_names
        assert "ISO 9001:2015 CAPA Templates" in table_names

    @pytest.mark.asyncio
    async def test_continues_when_search_fails(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test validation continues when search raises exception."""
        mock_searcher.search.side_effect = [
            Exception("Network error"),
            [],  # Second query succeeds but returns empty
            [],  # Third query
        ]

        # Should not raise, should return failed result
        result = await validator.validate_ap_matrix()

        assert result.passed is False  # No chunks found

    @pytest.mark.asyncio
    async def test_deduplicates_chunks(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test that duplicate chunks are removed."""
        # Same chunk returned from multiple queries
        duplicate_chunk = MockChunk(
            id="chunk-1",
            content=(
                "Action Priority table with AP rating: "
                "Severity 1-10, Occurrence 1-10, values High Medium Low"
            ),
        )
        mock_searcher.search.return_value = [duplicate_chunk]

        result = await validator.validate_ap_matrix()

        # Despite 3 queries returning same chunk, should only count once
        # (3 queries * 1 chunk each = 3 chunks, but deduplicated to 1)
        assert result.chunks_retrieved == 1
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_multiple_chunks_combined(
        self,
        validator: TableValidator,
        mock_searcher: AsyncMock,
    ) -> None:
        """Test that content from multiple chunks is combined for validation."""
        # Split content across chunks
        mock_searcher.search.side_effect = [
            [MockChunk(id="chunk-1", content="Action Priority table AP rating")],
            [MockChunk(id="chunk-2", content="Severity 5 Occurrence 7 High")],
            [MockChunk(id="chunk-3", content="Medium Low ratings")],
        ]

        result = await validator.validate_ap_matrix()

        assert result.chunks_retrieved == 3
        # All checks should pass with combined content
        assert result.details["ap_values"] is True
        assert result.details["severity_scale"] is True
        assert result.details["occurrence_scale"] is True


class TestCriticalTables:
    """Tests for critical table registry."""

    def test_critical_tables_registry_exists(self) -> None:
        """Test CRITICAL_TABLES registry is properly defined."""
        from knowledge_mcp.validation.critical_tables import CRITICAL_TABLES

        assert len(CRITICAL_TABLES) == 3

    def test_critical_tables_have_required_fields(self) -> None:
        """Test all critical tables have required fields."""
        from knowledge_mcp.validation.critical_tables import CRITICAL_TABLES

        for table in CRITICAL_TABLES:
            assert table.name
            assert table.standard
            assert table.description
            assert len(table.required_for) > 0
            assert table.validation_method

    def test_critical_tables_validation_methods_exist(self) -> None:
        """Test validation methods referenced in registry exist on TableValidator."""
        from knowledge_mcp.validation.critical_tables import CRITICAL_TABLES

        validator_methods = [
            "validate_ap_matrix",
            "validate_mil_std_severity",
            "validate_iso9001_capa",
        ]

        for table in CRITICAL_TABLES:
            assert table.validation_method in validator_methods


class TestValidationReport:
    """Tests for ValidationReport class."""

    def test_report_all_passed(self) -> None:
        """Test report with all passing results."""
        from knowledge_mcp.validation.reports import ValidationReport

        results = [
            ValidationResult(table_name="Table1", passed=True),
            ValidationResult(table_name="Table2", passed=True),
        ]
        report = ValidationReport(collection="test", results=results)

        assert report.all_passed is True
        assert report.passed_count == 2
        assert report.failed_count == 0
        assert "PASSED" in report.format_summary()

    def test_report_with_failures(self) -> None:
        """Test report with some failing results."""
        from knowledge_mcp.validation.reports import ValidationReport

        results = [
            ValidationResult(table_name="Table1", passed=True),
            ValidationResult(
                table_name="Table2",
                passed=False,
                recommendation="Fix Table2",
            ),
        ]
        report = ValidationReport(collection="test", results=results)

        assert report.all_passed is False
        assert report.passed_count == 1
        assert report.failed_count == 1
        assert "FAILED" in report.format_summary()
        assert "Fix Table2" in report.get_recommendations()

    def test_report_warning_count(self) -> None:
        """Test report warning count."""
        from knowledge_mcp.validation.reports import ValidationReport

        results = [
            ValidationResult(table_name="Table1", passed=True, has_warnings=True),
            ValidationResult(table_name="Table2", passed=True, has_warnings=False),
        ]
        report = ValidationReport(collection="test", results=results)

        assert report.warning_count == 1

    def test_report_empty_results(self) -> None:
        """Test report with no results."""
        from knowledge_mcp.validation.reports import ValidationReport

        report = ValidationReport(collection="test")

        assert report.all_passed is True  # vacuously true
        assert report.passed_count == 0
        assert report.failed_count == 0
        assert report.get_recommendations() == []
