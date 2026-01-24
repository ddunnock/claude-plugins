# src/knowledge_mcp/exceptions.py
"""
Custom exception hierarchy for Knowledge MCP.

This module defines a structured exception hierarchy that maps to
MCP error codes per AD-005 and A-REQ-DATA-004. All application-specific
exceptions inherit from KnowledgeMCPError, enabling unified error handling.

Example:
    >>> from knowledge_mcp.exceptions import ConfigurationError
    >>> try:
    ...     raise ConfigurationError("QDRANT_URL is required")
    ... except KnowledgeMCPError as e:
    ...     print(f"Error [{e.error_code}]: {e}")
    Error [config_error]: QDRANT_URL is required

Exception Hierarchy:
    KnowledgeMCPError (base)
    ├── ConfigurationError (config_error)
    ├── ConnectionError (connection_error)
    ├── TimeoutError (timeout_error)
    ├── AuthenticationError (auth_error)
    ├── NotFoundError (not_found)
    ├── ValidationError (invalid_input)
    ├── RateLimitError (rate_limited)
    └── InternalError (internal_error)
"""

from __future__ import annotations


class KnowledgeMCPError(Exception):
    """
    Base exception for all Knowledge MCP errors.

    All application-specific exceptions inherit from this class,
    enabling unified error handling across the application.

    Attributes:
        error_code: Machine-readable error code for MCP responses.
        message: Human-readable error description.

    Example:
        >>> try:
        ...     raise KnowledgeMCPError("Something went wrong")
        ... except KnowledgeMCPError as e:
        ...     print(f"[{e.error_code}] {e}")
        [internal_error] Something went wrong
    """

    __slots__ = ("message",)

    error_code: str = "internal_error"

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error description.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return the error message."""
        return self.message

    def to_dict(self) -> dict[str, str]:
        """
        Convert exception to dictionary for MCP responses.

        Returns:
            Dictionary with 'error_code' and 'message' keys.

        Example:
            >>> e = ConfigurationError("Missing API key")
            >>> e.to_dict()
            {'error_code': 'config_error', 'message': 'Missing API key'}
        """
        return {"error_code": self.error_code, "message": self.message}


class ConfigurationError(KnowledgeMCPError):
    """
    Raised when configuration is invalid or missing.

    Use this exception when:
    - Required environment variables are missing
    - Configuration values fail validation
    - Configuration files cannot be parsed

    Example:
        >>> raise ConfigurationError("OPENAI_API_KEY is required")
    """

    error_code: str = "config_error"


class ConnectionError(KnowledgeMCPError):
    """
    Raised when a network connection cannot be established.

    Use this exception when:
    - Vector store is unreachable
    - Embedding API endpoint is down
    - DNS resolution fails

    Example:
        >>> raise ConnectionError("Cannot connect to Qdrant Cloud at https://...")
    """

    error_code: str = "connection_error"


class TimeoutError(KnowledgeMCPError):
    """
    Raised when an operation exceeds its time limit.

    Use this exception when:
    - API calls exceed configured timeout
    - Database queries take too long
    - Embedding generation times out

    Example:
        >>> raise TimeoutError("Search operation timed out after 30s")
    """

    error_code: str = "timeout_error"


class AuthenticationError(KnowledgeMCPError):
    """
    Raised when authentication fails.

    Use this exception when:
    - API keys are invalid or expired
    - Credentials are rejected by external services
    - Token refresh fails

    Example:
        >>> raise AuthenticationError("Invalid Qdrant API key")
    """

    error_code: str = "auth_error"


class NotFoundError(KnowledgeMCPError):
    """
    Raised when a requested resource is not found.

    Use this exception when:
    - Collection does not exist in vector store
    - Document ID is not found
    - Requested file path does not exist

    Example:
        >>> raise NotFoundError("Collection 'ieee_standards' not found")
    """

    error_code: str = "not_found"


class ValidationError(KnowledgeMCPError):
    """
    Raised when input validation fails.

    Use this exception when:
    - Query string is empty or too long
    - Document format is unsupported
    - Chunk size parameters are invalid

    Example:
        >>> raise ValidationError("Query must be between 1 and 1000 characters")
    """

    error_code: str = "invalid_input"


class RateLimitError(KnowledgeMCPError):
    """
    Raised when rate limits are exceeded.

    Use this exception when:
    - OpenAI API rate limit is hit
    - Qdrant Cloud throttles requests
    - Too many concurrent requests

    Example:
        >>> raise RateLimitError("OpenAI rate limit exceeded, retry after 60s")
    """

    error_code: str = "rate_limited"


class InternalError(KnowledgeMCPError):
    """
    Raised for unexpected internal errors.

    Use this exception when:
    - Unexpected runtime errors occur
    - Internal state is corrupted
    - Catch-all for unhandled exceptions

    Example:
        >>> raise InternalError("Unexpected error during embedding generation")
    """

    error_code: str = "internal_error"


class IngestionError(KnowledgeMCPError):
    """
    Raised when document ingestion fails.

    Use this exception when:
    - Document cannot be parsed
    - Unsupported document format encountered
    - Document structure is corrupted

    Example:
        >>> raise IngestionError("Failed to parse PDF: corrupted document structure")
    """

    error_code: str = "ingestion_error"


# Convenience tuple for catching all specific exception types
ALL_EXCEPTIONS = (
    ConfigurationError,
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    InternalError,
    IngestionError,
)
