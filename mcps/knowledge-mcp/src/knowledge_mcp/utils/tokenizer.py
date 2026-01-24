"""
Token counting utilities using tiktoken.

Provides accurate token counting that matches OpenAI embedding API billing.
Uses cl100k_base encoding (same as text-embedding-3-small/large).

Example:
    >>> count = count_tokens("Hello world")
    >>> print(f"Token count: {count}")
    Token count: 2

    >>> truncated = truncate_to_tokens("Long text...", max_tokens=100)
    >>> print(f"Truncated to {count_tokens(truncated)} tokens")
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import tiktoken

__all__ = ["TokenizerConfig", "count_tokens", "truncate_to_tokens"]


@dataclass
class TokenizerConfig:
    """
    Configuration for tokenizer.

    Attributes:
        model: OpenAI model name for encoding selection.
        max_tokens: Maximum token limit for truncation.
    """

    model: str = "text-embedding-3-small"
    max_tokens: int = 500


@lru_cache(maxsize=4)
def _get_encoding(model: str) -> tiktoken.Encoding:
    """
    Get cached tiktoken encoding for a model.

    Args:
        model: OpenAI model name.

    Returns:
        tiktoken.Encoding instance.

    Note:
        Results are cached to avoid repeated encoding initialization.
    """
    return tiktoken.encoding_for_model(model)


def count_tokens(text: str, model: str = "text-embedding-3-small") -> int:
    """
    Count tokens in text using tiktoken.

    Matches OpenAI API token counting exactly, ensuring accurate
    cost estimation and chunk sizing.

    Args:
        text: Text to count tokens for.
        model: OpenAI model name (default: text-embedding-3-small).

    Returns:
        Number of tokens in the text.

    Example:
        >>> count_tokens("Hello world")
        2
        >>> count_tokens("")
        0
        >>> count_tokens("Unicode 你好")
        4
    """
    if not text:
        return 0

    encoding = _get_encoding(model)
    return len(encoding.encode(text))


def truncate_to_tokens(
    text: str,
    max_tokens: int,
    model: str = "text-embedding-3-small",
) -> str:
    """
    Truncate text to maximum token count.

    Preserves complete text when under limit. When truncating,
    decodes back to string to avoid cutting mid-character.

    Args:
        text: Text to truncate.
        max_tokens: Maximum number of tokens to keep.
        model: OpenAI model name (default: text-embedding-3-small).

    Returns:
        Truncated text (or original if under limit).

    Example:
        >>> text = "This is a longer piece of text"
        >>> truncated = truncate_to_tokens(text, max_tokens=5)
        >>> count_tokens(truncated) <= 5
        True
        >>> short = "Hi"
        >>> truncate_to_tokens(short, max_tokens=100) == short
        True
    """
    if not text:
        return text

    encoding = _get_encoding(model)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    # Truncate tokens and decode back to string
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)
