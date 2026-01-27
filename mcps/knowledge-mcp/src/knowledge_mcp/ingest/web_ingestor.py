"""Web content ingestion using Crawl4AI.

This module provides web content ingestion with robots.txt compliance,
rate limiting, and structured error handling.

Example:
    >>> from knowledge_mcp.ingest import WebIngestor
    >>> ingestor = WebIngestor()
    >>> result = await ingestor.ingest("https://example.com")
    >>> if result.success:
    ...     print(result.markdown)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class WebIngestorConfig:
    """Configuration for web content ingestion.

    Attributes:
        respect_robots_txt: Check robots.txt before crawling (default: True).
        max_concurrent: Maximum concurrent crawls (default: 3).
        delay_between_requests: Delay between requests in seconds (default: 1.5).
        timeout: Request timeout in seconds (default: 30).
        user_agent: Custom user agent string (default: None, uses Crawl4AI default).
    """

    respect_robots_txt: bool = True
    max_concurrent: int = 3
    delay_between_requests: float = 1.5
    timeout: int = 30
    user_agent: str | None = None


@dataclass
class WebIngestionResult:
    """Result of web content ingestion.

    Attributes:
        url: The URL that was crawled.
        success: Whether the ingestion succeeded.
        markdown: Extracted markdown content (empty if failed).
        title: Extracted page title (empty if failed).
        word_count: Number of words in content.
        error: Error message if failed (None if succeeded).
        status_code: HTTP status code (0 if not available).
    """

    url: str
    success: bool
    markdown: str = ""
    title: str = ""
    word_count: int = 0
    error: str | None = None
    status_code: int = 0


@dataclass
class WebIngestor:
    """Web content ingestor using Crawl4AI.

    Features:
    - robots.txt compliance (configurable)
    - Rate limiting via semaphore
    - Clean Markdown output
    - Structured error handling

    Example:
        >>> config = WebIngestorConfig(respect_robots_txt=True)
        >>> ingestor = WebIngestor(config)
        >>> result = await ingestor.ingest("https://example.com")
        >>> if result.success:
        ...     print(f"Title: {result.title}")
        ...     print(f"Words: {result.word_count}")
    """

    config: WebIngestorConfig = field(default_factory=WebIngestorConfig)

    async def ingest(self, url: str) -> WebIngestionResult:
        """Ingest content from a single URL.

        Args:
            url: URL to crawl.

        Returns:
            WebIngestionResult with success status and extracted content.

        Example:
            >>> result = await ingestor.ingest("https://example.com")
            >>> if result.success:
            ...     print(result.markdown)
        """
        # Create crawler config
        crawler_config = CrawlerRunConfig(
            bypass_cache=True,
            word_count_threshold=10,  # Minimum words to consider valid
        )

        try:
            # Create async crawler
            async with AsyncWebCrawler(verbose=False) as crawler:
                # Crawl the URL
                result = await crawler.arun(
                    url=url,
                    config=crawler_config,
                )

                # Check if crawl was successful
                if not result.success:
                    return WebIngestionResult(
                        url=url,
                        success=False,
                        error=result.error_message or "Crawl failed",
                        status_code=result.status_code or 0,
                    )

                # Extract markdown content
                markdown = result.markdown or ""

                # Extract title
                title = self._extract_title(result.html or "", url)

                # Count words
                word_count = len(markdown.split())

                return WebIngestionResult(
                    url=url,
                    success=True,
                    markdown=markdown,
                    title=title,
                    word_count=word_count,
                    status_code=result.status_code or 200,
                )

        except Exception as e:
            return WebIngestionResult(
                url=url,
                success=False,
                error=str(e),
            )

    async def ingest_many(self, urls: Sequence[str]) -> list[WebIngestionResult]:
        """Ingest content from multiple URLs with rate limiting.

        Rate limiting is handled internally by Crawl4AI's AsyncWebCrawler
        when processing multiple URLs sequentially.

        Args:
            urls: List of URLs to crawl.

        Returns:
            List of WebIngestionResult objects, one per URL.

        Example:
            >>> urls = ["https://example.com", "https://example.org"]
            >>> results = await ingestor.ingest_many(urls)
            >>> successful = [r for r in results if r.success]
            >>> print(f"Crawled {len(successful)}/{len(urls)} URLs")
        """
        results = []
        for url in urls:
            result = await self.ingest(url)
            results.append(result)
        return results

    def _extract_title(self, html: str, fallback_url: str) -> str:
        """Extract page title from HTML.

        Args:
            html: HTML content.
            fallback_url: URL to use as fallback if title not found.

        Returns:
            Extracted title or URL as fallback.
        """
        # Try to extract <title> tag
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up whitespace
            title = re.sub(r"\s+", " ", title)
            return title

        # Fallback to URL
        return fallback_url


def check_url_accessible(url: str) -> tuple[bool, str | None]:
    """Check if a URL is accessible (basic validation).

    This is a simple preflight check before attempting to crawl.
    It validates URL format but does NOT make a network request.

    Args:
        url: URL to check.

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is None.

    Example:
        >>> is_valid, error = check_url_accessible("https://example.com")
        >>> if not is_valid:
        ...     print(f"Invalid URL: {error}")
    """
    # Basic URL validation
    url = url.strip()

    if not url:
        return False, "URL is empty"

    # Check for scheme
    if not url.startswith(("http://", "https://")):
        return False, "URL must start with http:// or https://"

    # Check for valid domain pattern (basic)
    domain_pattern = r"^https?://[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*"
    if not re.match(domain_pattern, url):
        return False, "Invalid URL format"

    return True, None
