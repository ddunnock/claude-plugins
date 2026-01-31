"""Critical table definitions for RCCA validation.

Defines which tables are critical for RCCA skill integration
and their validation requirements.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CriticalTable:
    """Definition of a critical RCCA lookup table.

    Attributes:
        name: Human-readable table name.
        standard: Source standard (e.g., "AIAG-VDA FMEA 2019").
        description: Brief description of table contents.
        required_for: List of RCCA skills that need this table.
        validation_method: TableValidator method name to call.
    """

    name: str
    standard: str
    description: str
    required_for: list[str]  # Which RCCA skills need this table
    validation_method: str  # Which TableValidator method to call


# Registry of critical tables for RCCA skill integration
CRITICAL_TABLES = [
    CriticalTable(
        name="Action Priority Matrix",
        standard="AIAG-VDA FMEA 2019",
        description=(
            "10x10 Severity x Occurrence -> Action Priority (H/M/L) lookup table"
        ),
        required_for=["fmea-analysis", "rcca-master"],
        validation_method="validate_ap_matrix",
    ),
    CriticalTable(
        name="Severity Categories",
        standard="MIL-STD-882E",
        description=(
            "4-level severity classification "
            "(Catastrophic, Critical, Marginal, Negligible)"
        ),
        required_for=["problem-definition", "fmea-analysis", "rcca-master"],
        validation_method="validate_mil_std_severity",
    ),
    CriticalTable(
        name="CAPA Templates",
        standard="ISO 9001:2015",
        description="Clause 10.2 Corrective Action process and requirements",
        required_for=["rcca-master", "five-whys-analysis"],
        validation_method="validate_iso9001_capa",
    ),
]
