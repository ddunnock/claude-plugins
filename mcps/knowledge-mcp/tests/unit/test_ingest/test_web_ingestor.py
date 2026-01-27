"""Unit tests for WebIngestor."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from knowledge_mcp.ingest.web_ingestor import (
    WebIngestionResult,
    WebIngestor,
    WebIngestorConfig,
    check_url_accessible,
)


class TestWebIngestorConfig:
    """Tests for WebIngestorConfig dataclass."""

    def test_config_defaults(self) -> None:
        """Test that config has correct default values."""
        config = WebIngestorConfig()

        assert config.respect_robots_txt is True
        assert config.max_concurrent == 3
        assert config.delay_between_requests == 1.5
        assert config.timeout == 30
        assert config.user_agent is None

    def test_config_custom_values(self) -> None:
        """Test that config accepts custom values."""
        config = WebIngestorConfig(
            respect_robots_txt=False,
            max_concurrent=5,
            delay_between_requests=2.0,
            timeout=60,
            user_agent="CustomBot/1.0",
        )

        assert config.respect_robots_txt is False
        assert config.max_concurrent == 5
        assert config.delay_between_requests == 2.0
        assert config.timeout == 60
        assert config.user_agent == "CustomBot/1.0"


class TestWebIngestionResult:
    """Tests for WebIngestionResult dataclass."""

    def test_result_success(self) -> None:
        """Test successful ingestion result structure."""
        result = WebIngestionResult(
            url="https://example.com",
            success=True,
            markdown="# Test\n\nContent",
            title="Test Page",
            word_count=2,
            status_code=200,
        )

        assert result.url == "https://example.com"
        assert result.success is True
        assert result.markdown == "# Test\n\nContent"
        assert result.title == "Test Page"
        assert result.word_count == 2
        assert result.error is None
        assert result.status_code == 200

    def test_result_failure(self) -> None:
        """Test failed ingestion result structure."""
        result = WebIngestionResult(
            url="https://example.com",
            success=False,
            error="Connection timeout",
            status_code=0,
        )

        assert result.url == "https://example.com"
        assert result.success is False
        assert result.markdown == ""
        assert result.title == ""
        assert result.word_count == 0
        assert result.error == "Connection timeout"
        assert result.status_code == 0


class TestWebIngestor:
    """Tests for WebIngestor class."""

    def test_ingestor_initialization_default(self) -> None:
        """Test ingestor initializes with default config."""
        ingestor = WebIngestor()

        assert ingestor.config is not None
        assert ingestor.config.respect_robots_txt is True
        assert ingestor.config.max_concurrent == 3

    def test_ingestor_initialization_custom(self) -> None:
        """Test ingestor initializes with custom config."""
        config = WebIngestorConfig(max_concurrent=10)
        ingestor = WebIngestor(config)

        assert ingestor.config.max_concurrent == 10

    def test_extract_title_from_html(self) -> None:
        """Test title extraction from HTML."""
        ingestor = WebIngestor()
        html = "<html><head><title>Test Page Title</title></head></html>"

        title = ingestor._extract_title(html, "https://example.com")

        assert title == "Test Page Title"

    def test_extract_title_with_whitespace(self) -> None:
        """Test title extraction cleans up whitespace."""
        ingestor = WebIngestor()
        html = "<html><head><title>  Test\n  Page\n  Title  </title></head></html>"

        title = ingestor._extract_title(html, "https://example.com")

        assert title == "Test Page Title"

    def test_extract_title_fallback_to_url(self) -> None:
        """Test title extraction falls back to URL when no title tag."""
        ingestor = WebIngestor()
        html = "<html><head></head></html>"

        title = ingestor._extract_title(html, "https://example.com")

        assert title == "https://example.com"

    def test_extract_title_case_insensitive(self) -> None:
        """Test title extraction is case insensitive."""
        ingestor = WebIngestor()
        html = "<html><head><TITLE>Test Page</TITLE></head></html>"

        title = ingestor._extract_title(html, "https://example.com")

        assert title == "Test Page"

    @pytest.mark.asyncio
    async def test_ingest_success(self) -> None:
        """Test successful web page ingestion."""
        ingestor = WebIngestor()

        # Mock the crawler result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.markdown = "# Test Page\n\nThis is test content."
        mock_result.html = "<html><head><title>Test Page</title></head></html>"
        mock_result.status_code = 200
        mock_result.error_message = None

        # Mock CrawlerRunConfig and AsyncWebCrawler
        with patch("knowledge_mcp.ingest.web_ingestor.CrawlerRunConfig") as mock_config_class, \
             patch("knowledge_mcp.ingest.web_ingestor.AsyncWebCrawler") as mock_crawler_class:
            mock_config_class.return_value = MagicMock()
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.arun.return_value = mock_result
            mock_crawler_class.return_value = mock_crawler

            result = await ingestor.ingest("https://example.com")

        assert result.success is True
        assert result.url == "https://example.com"
        assert result.markdown == "# Test Page\n\nThis is test content."
        assert result.title == "Test Page"
        assert result.word_count == 7  # "#", "Test", "Page", "This", "is", "test", "content"
        assert result.status_code == 200
        assert result.error is None

    @pytest.mark.asyncio
    async def test_ingest_crawl_failure(self) -> None:
        """Test handling of crawl failure."""
        ingestor = WebIngestor()

        # Mock a failed crawler result
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error_message = "HTTP 404: Not Found"
        mock_result.status_code = 404

        with patch("knowledge_mcp.ingest.web_ingestor.CrawlerRunConfig") as mock_config_class, \
             patch("knowledge_mcp.ingest.web_ingestor.AsyncWebCrawler") as mock_crawler_class:
            mock_config_class.return_value = MagicMock()
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.arun.return_value = mock_result
            mock_crawler_class.return_value = mock_crawler

            result = await ingestor.ingest("https://example.com/notfound")

        assert result.success is False
        assert result.url == "https://example.com/notfound"
        assert result.error == "HTTP 404: Not Found"
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_ingest_exception_handling(self) -> None:
        """Test handling of exceptions during crawling."""
        ingestor = WebIngestor()

        with patch("knowledge_mcp.ingest.web_ingestor.CrawlerRunConfig") as mock_config_class, \
             patch("knowledge_mcp.ingest.web_ingestor.AsyncWebCrawler") as mock_crawler_class:
            mock_config_class.return_value = MagicMock()
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.arun.side_effect = Exception("Network error")
            mock_crawler_class.return_value = mock_crawler

            result = await ingestor.ingest("https://example.com")

        assert result.success is False
        assert result.url == "https://example.com"
        assert result.error == "Network error"
        assert result.status_code == 0

    @pytest.mark.asyncio
    async def test_ingest_many_multiple_urls(self) -> None:
        """Test ingesting multiple URLs."""
        ingestor = WebIngestor()

        # Mock successful results for multiple URLs
        mock_result_1 = MagicMock()
        mock_result_1.success = True
        mock_result_1.markdown = "Content 1"
        mock_result_1.html = "<html><head><title>Page 1</title></head></html>"
        mock_result_1.status_code = 200
        mock_result_1.error_message = None

        mock_result_2 = MagicMock()
        mock_result_2.success = True
        mock_result_2.markdown = "Content 2"
        mock_result_2.html = "<html><head><title>Page 2</title></head></html>"
        mock_result_2.status_code = 200
        mock_result_2.error_message = None

        with patch("knowledge_mcp.ingest.web_ingestor.CrawlerRunConfig") as mock_config_class, \
             patch("knowledge_mcp.ingest.web_ingestor.AsyncWebCrawler") as mock_crawler_class:
            mock_config_class.return_value = MagicMock()
            mock_crawler = AsyncMock()
            mock_crawler.__aenter__.return_value = mock_crawler
            mock_crawler.arun.side_effect = [mock_result_1, mock_result_2]
            mock_crawler_class.return_value = mock_crawler

            results = await ingestor.ingest_many(
                ["https://example.com/1", "https://example.com/2"]
            )

        assert len(results) == 2
        assert results[0].success is True
        assert results[0].title == "Page 1"
        assert results[1].success is True
        assert results[1].title == "Page 2"


class TestCheckUrlAccessible:
    """Tests for check_url_accessible utility function."""

    def test_valid_http_url(self) -> None:
        """Test that valid HTTP URLs pass validation."""
        is_valid, error = check_url_accessible("http://example.com")

        assert is_valid is True
        assert error is None

    def test_valid_https_url(self) -> None:
        """Test that valid HTTPS URLs pass validation."""
        is_valid, error = check_url_accessible("https://example.com")

        assert is_valid is True
        assert error is None

    def test_valid_url_with_path(self) -> None:
        """Test that URLs with paths pass validation."""
        is_valid, error = check_url_accessible("https://example.com/path/to/page")

        assert is_valid is True
        assert error is None

    def test_valid_url_with_subdomain(self) -> None:
        """Test that URLs with subdomains pass validation."""
        is_valid, error = check_url_accessible("https://www.example.com")

        assert is_valid is True
        assert error is None

    def test_empty_url(self) -> None:
        """Test that empty URLs are rejected."""
        is_valid, error = check_url_accessible("")

        assert is_valid is False
        assert error == "URL is empty"

    def test_whitespace_only_url(self) -> None:
        """Test that whitespace-only URLs are rejected."""
        is_valid, error = check_url_accessible("   ")

        assert is_valid is False
        assert error == "URL is empty"

    def test_missing_scheme(self) -> None:
        """Test that URLs without scheme are rejected."""
        is_valid, error = check_url_accessible("example.com")

        assert is_valid is False
        assert error == "URL must start with http:// or https://"

    def test_invalid_scheme(self) -> None:
        """Test that URLs with invalid schemes are rejected."""
        is_valid, error = check_url_accessible("ftp://example.com")

        assert is_valid is False
        assert error == "URL must start with http:// or https://"

    def test_invalid_domain_format(self) -> None:
        """Test that URLs with invalid domain format are rejected."""
        is_valid, error = check_url_accessible("https://-invalid-.com")

        assert is_valid is False
        assert error == "Invalid URL format"
