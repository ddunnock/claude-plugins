"""
Production monitoring for knowledge-mcp.

This package provides:
- Token usage tracking for cost visibility
- Structured JSON logging
- Alerting for threshold violations
"""

from __future__ import annotations

from knowledge_mcp.monitoring.logger import setup_json_logger
from knowledge_mcp.monitoring.token_tracker import TokenTracker

__all__ = ["TokenTracker", "setup_json_logger"]
