"""
Validation module for RCCA standards ingestion.

Provides query-based validation for critical tables (AP matrix, severity scales)
to verify ingestion preserved table integrity for RCCA skill queries.
"""

from knowledge_mcp.validation.critical_tables import CRITICAL_TABLES, CriticalTable
from knowledge_mcp.validation.reports import ValidationReport
from knowledge_mcp.validation.table_validator import TableValidator, ValidationResult

__all__ = [
    "CRITICAL_TABLES",
    "CriticalTable",
    "TableValidator",
    "ValidationReport",
    "ValidationResult",
]
