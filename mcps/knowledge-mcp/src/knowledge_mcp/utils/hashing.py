"""
Content hashing utilities for deduplication.

Provides deterministic SHA-256 hashing with text normalization.
Used to detect duplicate chunks across documents.

Example:
    >>> hash1 = compute_content_hash("Hello world")
    >>> hash2 = compute_content_hash("Hello world")
    >>> hash1 == hash2
    True
"""

from __future__ import annotations

import hashlib

__all__ = ["compute_content_hash"]


def compute_content_hash(text: str) -> str:
    """
    Compute SHA-256 hash of normalized text.

    Normalizes text before hashing to ensure consistent hashes
    for semantically identical content:
    - Strips leading/trailing whitespace
    - Converts \\r\\n to \\n
    - Encodes as UTF-8

    Args:
        text: Text content to hash.

    Returns:
        Hexadecimal SHA-256 hash string.

    Example:
        >>> compute_content_hash("Hello world")
        '64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c'
        >>> # Whitespace normalized
        >>> hash1 = compute_content_hash("  Hello world  ")
        >>> hash2 = compute_content_hash("Hello world")
        >>> hash1 == hash2
        True
        >>> # Line endings normalized
        >>> hash3 = compute_content_hash("Hello\\r\\nworld")
        >>> hash4 = compute_content_hash("Hello\\nworld")
        >>> hash3 == hash4
        True
    """
    # Normalize text
    normalized = text.strip()  # Remove leading/trailing whitespace
    normalized = normalized.replace("\r\n", "\n")  # Normalize line endings

    # Compute SHA-256 hash
    hash_obj = hashlib.sha256(normalized.encode("utf-8"))
    return hash_obj.hexdigest()
