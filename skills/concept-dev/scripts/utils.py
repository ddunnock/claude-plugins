#!/usr/bin/env python3
"""
Shared utilities for concept-dev scripts.

Provides common validation functions used across multiple scripts.
"""

import os
import sys


def validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    resolved = os.path.realpath(filepath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got '{ext}'")
        sys.exit(1)
    return resolved
