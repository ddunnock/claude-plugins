"""
Normative/informative detection for standards documents.

Identifies whether text chunks contain normative (SHALL/MUST/SHOULD)
or informative (NOTE/EXAMPLE/MAY) content per RFC 2119 and ISO conventions.

Example:
    >>> from knowledge_mcp.utils.normative import detect_normative
    >>> result = detect_normative("The system SHALL verify credentials")
    >>> print(result)
    NormativeIndicator.NORMATIVE
"""

from __future__ import annotations

import re
from enum import Enum

__all__ = ["NormativeIndicator", "detect_normative"]


class NormativeIndicator(Enum):
    """
    Classification of text as normative or informative.

    Attributes:
        NORMATIVE: Contains binding requirements (SHALL/MUST/SHOULD).
        INFORMATIVE: Contains guidance or examples (NOTE/MAY).
        UNKNOWN: Cannot determine classification.
    """

    NORMATIVE = "normative"
    INFORMATIVE = "informative"
    UNKNOWN = "unknown"


# RFC 2119 normative keywords (case-insensitive)
_NORMATIVE_KEYWORDS = re.compile(
    r"\b(SHALL|MUST|REQUIRED|SHOULD|RECOMMENDED)\b",
    re.IGNORECASE,
)

# Informative indicators
_INFORMATIVE_KEYWORDS = re.compile(
    r"\b(MAY|OPTIONAL|CAN|NOTE|EXAMPLE|INFORMATIVE)\b",
    re.IGNORECASE,
)

# Section markers for normative/informative classification
_NORMATIVE_SECTION = re.compile(
    r"\(normative\)",
    re.IGNORECASE,
)

_INFORMATIVE_SECTION = re.compile(
    r"\(informative\)",
    re.IGNORECASE,
)


def detect_normative(text: str, section_path: str = "") -> NormativeIndicator:
    """
    Detect if text is normative or informative.

    Detection rules (in priority order):
    1. Explicit section markers: "(normative)" or "(informative)"
    2. Normative keywords: SHALL, MUST, REQUIRED, SHOULD, RECOMMENDED
    3. Informative keywords: MAY, OPTIONAL, CAN, NOTE, EXAMPLE
    4. Default: Body content is NORMATIVE, unable to classify is UNKNOWN

    Args:
        text: Text content to classify.
        section_path: Optional section path/title for context.

    Returns:
        NormativeIndicator classification.

    Example:
        >>> detect_normative("The system SHALL verify")
        <NormativeIndicator.NORMATIVE: 'normative'>
        >>> detect_normative("NOTE: This is for guidance")
        <NormativeIndicator.INFORMATIVE: 'informative'>
        >>> detect_normative("Annex A (normative)")
        <NormativeIndicator.NORMATIVE: 'normative'>
    """
    # Check section markers first (highest priority)
    if _NORMATIVE_SECTION.search(section_path) or _NORMATIVE_SECTION.search(text):
        return NormativeIndicator.NORMATIVE

    if _INFORMATIVE_SECTION.search(section_path) or _INFORMATIVE_SECTION.search(text):
        return NormativeIndicator.INFORMATIVE

    # Check for normative keywords (SHALL/MUST/SHOULD)
    if _NORMATIVE_KEYWORDS.search(text):
        return NormativeIndicator.NORMATIVE

    # Check for informative keywords (NOTE/EXAMPLE/MAY)
    if _INFORMATIVE_KEYWORDS.search(text):
        return NormativeIndicator.INFORMATIVE

    # Default: UNKNOWN if no explicit markers found
    # Only mark as normative/informative when there's clear evidence
    return NormativeIndicator.UNKNOWN
