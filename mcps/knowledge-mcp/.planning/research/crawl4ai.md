# Crawl4AI Research

**Researched:** 2026-01-27
**Overall Confidence:** HIGH (official documentation verified)
**Purpose:** Web content ingestion for Knowledge MCP v2.0

---

## Executive Summary

Crawl4AI is a mature, well-maintained open-source web crawler specifically designed for LLM and AI pipeline integration. It provides async-first architecture built on Playwright, making it an excellent fit for Knowledge MCP's Python async architecture. The library outputs clean Markdown by default, which aligns perfectly with RAG use cases.

**Key strengths for Knowledge MCP:**
- Native async support (matches our async architecture)
- Clean Markdown output (ready for chunking/embedding)
- JavaScript rendering via Playwright (handles modern dynamic sites)
- robots.txt compliance support
- Active maintenance with 50k+ star community

**Key risks:**
- Playwright dependency adds complexity (browser management)
- Memory usage can be significant for parallel crawling
- Some session-based authentication scenarios are challenging

---

## Installation & Requirements

### Version Information

| Attribute | Value |
|-----------|-------|
| Current Version | v0.8.0 (January 16, 2026) |
| Previous Stable | v0.7.8 (December 2025) |
| License | Apache-2.0 |
| Repository | github.com/unclecode/crawl4ai |

### Python Compatibility

| Python Version | Status |
|----------------|--------|
| 3.10 | Supported |
| 3.11 | Supported |
| 3.12 | Supported |
| 3.13 | Supported |
| 3.14+ | Not yet tested |

**Knowledge MCP compatibility:** Fully compatible (requires Python >=3.11,<3.14)

### Installation Options

```bash
# Standard installation (async with Playwright)
pip install -U crawl4ai
crawl4ai-setup      # Install Playwright browsers
crawl4ai-doctor     # Verify installation

# With ML features (sentence-transformers)
pip install crawl4ai[transformer]

# Full installation (all features)
pip install crawl4ai[all]

# Pre-release versions
pip install crawl4ai --pre
```

### Post-Installation Setup

The `crawl4ai-setup` command installs Playwright browsers. This is **required** for the crawler to function.

```bash
# Manual browser installation if needed
playwright install chromium
```

### System Requirements

- **Memory:** 2GB+ recommended for single crawls, 4GB+ for parallel
- **Disk:** Browser binaries require ~500MB
- **Network:** Outbound HTTP/HTTPS access

---

## Core API Reference

### Primary Classes

| Class | Purpose |
|-------|---------|
| `AsyncWebCrawler` | Main async crawler class |
| `BrowserConfig` | Browser launch settings |
| `CrawlerRunConfig` | Per-crawl behavior settings |
| `CrawlResult` | Result object from crawling |

### BrowserConfig Parameters

Controls how the browser is launched:

```python
from crawl4ai import BrowserConfig

browser_config = BrowserConfig(
    headless=True,              # Run without UI (default: True)
    verbose=True,               # Enable logging
    viewport_width=1920,        # Browser width
    viewport_height=1080,       # Browser height
    proxy="http://user:pass@proxy:8080",  # Proxy configuration
    text_mode=False,            # Skip images/media (faster)
    user_data_dir=None,         # Persistent profile directory
    use_persistent_context=False,  # Reuse browser context
)
```

### CrawlerRunConfig Parameters

Controls per-crawl behavior:

```python
from crawl4ai import CrawlerRunConfig, CacheMode

run_config = CrawlerRunConfig(
    # Content processing
    word_count_threshold=200,   # Minimum words for content
    excluded_tags=['form', 'header', 'footer'],  # Tags to skip
    exclude_external_links=False,
    process_iframes=True,       # Extract iframe content
    remove_overlay_elements=True,  # Remove popups/modals

    # Caching
    cache_mode=CacheMode.BYPASS,  # BYPASS, ENABLED, WRITE_ONLY, READ_ONLY

    # JavaScript execution
    js_code=None,               # Custom JS to execute
    wait_for=None,              # CSS selector or JS condition

    # Output options
    screenshot=False,           # Capture screenshot
    pdf=False,                  # Generate PDF

    # Compliance
    check_robots_txt=True,      # Respect robots.txt

    # Rate limiting
    # (handled via dispatcher, see below)
)
```

### CrawlResult Object

```python
result = await crawler.arun(url, config=run_config)

# Key properties
result.success          # bool - did crawl succeed
result.url              # str - final URL (after redirects)
result.html             # str - original HTML
result.cleaned_html     # str - sanitized HTML
result.markdown         # MarkdownResult object
result.markdown.raw_markdown    # str - clean markdown
result.markdown.fit_markdown    # str - heuristic-filtered markdown
result.extracted_content  # any - if extraction strategy used
result.media            # dict - discovered images
result.links            # dict - discovered links
result.screenshot       # bytes - if requested
result.pdf              # bytes - if requested
result.error_message    # str - error details if failed
result.status_code      # int - HTTP status
```

---

## Usage Patterns

### Basic Single-URL Crawl

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_single(url: str) -> str:
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if result.success:
            return result.markdown.raw_markdown
        else:
            raise RuntimeError(f"Crawl failed: {result.error_message}")

# Usage
markdown = asyncio.run(crawl_single("https://example.com"))
```

### Parallel Multi-URL Crawling

```python
import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode
)
from crawl4ai.dispatcher import SemaphoreDispatcher, RateLimiter

async def crawl_many(urls: list[str], max_concurrent: int = 5) -> list[dict]:
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        check_robots_txt=True,
        stream=True,  # Enable streaming for memory efficiency
    )

    # Control concurrency with SemaphoreDispatcher
    dispatcher = SemaphoreDispatcher(
        semaphore_count=max_concurrent,
        rate_limiter=RateLimiter(
            base_delay=(0.5, 1.0),  # Random delay between requests
            max_delay=10.0,         # Max backoff delay
        )
    )

    results = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        async for result in await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        ):
            results.append({
                "url": result.url,
                "success": result.success,
                "markdown": result.markdown.raw_markdown if result.success else None,
                "error": result.error_message if not result.success else None,
            })

    return results
```

### With JavaScript Execution

```python
async def crawl_dynamic_page(url: str) -> str:
    """Crawl a page that requires JavaScript interaction."""
    run_config = CrawlerRunConfig(
        js_code="""
            // Click "Load More" button if present
            const loadMore = document.querySelector('.load-more');
            if (loadMore) loadMore.click();
        """,
        wait_for="css:.content-loaded",  # Wait for element
        # or wait_for="js:() => document.querySelectorAll('.item').length > 10"
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=run_config)
        return result.markdown.raw_markdown
```

### With Authentication (Storage State)

```python
async def crawl_authenticated(url: str, storage_state_path: str) -> str:
    """Crawl using pre-saved authentication state."""
    browser_config = BrowserConfig(
        headless=True,
    )
    run_config = CrawlerRunConfig(
        storage_state=storage_state_path,  # Path to saved session JSON
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        return result.markdown.raw_markdown

# To save a storage state after manual login:
# await context.storage_state(path="my_storage.json")
```

### With Persistent Browser Profile

```python
async def crawl_with_profile(url: str, profile_dir: str) -> str:
    """Use persistent browser profile for cookies/localStorage."""
    browser_config = BrowserConfig(
        headless=True,
        user_data_dir=profile_dir,
        use_persistent_context=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url)
        return result.markdown.raw_markdown
```

---

## Extraction Strategies

### Default: Markdown Generation

By default, Crawl4AI converts HTML to clean Markdown suitable for LLM consumption.

```python
result.markdown.raw_markdown    # Full markdown
result.markdown.fit_markdown    # Heuristic-filtered (less noise)
```

### LLM-Free: CSS/XPath Extraction

For structured data extraction without LLM costs:

```python
from crawl4ai.extraction import JsonCssExtractionStrategy

strategy = JsonCssExtractionStrategy(
    schema={
        "name": "articles",
        "baseSelector": "article.post",
        "fields": [
            {"name": "title", "selector": "h2", "type": "text"},
            {"name": "author", "selector": ".author", "type": "text"},
            {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"},
        ]
    }
)

run_config = CrawlerRunConfig(
    extraction_strategy=strategy,
)
```

### LLM-Based Extraction

For semantic extraction (provider-agnostic via LiteLLM):

```python
from crawl4ai.extraction import LLMExtractionStrategy
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    summary: str
    topics: list[str]

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4o-mini",
    schema=Article,
    instruction="Extract article metadata",
)

run_config = CrawlerRunConfig(
    extraction_strategy=strategy,
)
```

---

## Rate Limiting & Compliance

### robots.txt Support

```python
run_config = CrawlerRunConfig(
    check_robots_txt=True,  # Enable robots.txt checking
)

# Robots.txt behavior:
# - Files cached in ~/.crawl4ai/robots/robots_cache.db
# - Cache TTL: 7 days
# - If fetch fails, crawling is allowed
# - Returns 403 status if URL is disallowed
```

### Rate Limiting with Dispatchers

```python
from crawl4ai.dispatcher import (
    SemaphoreDispatcher,
    MemoryAdaptiveDispatcher,
    RateLimiter,
)

# Fixed concurrency limit
dispatcher = SemaphoreDispatcher(
    semaphore_count=5,
    rate_limiter=RateLimiter(
        base_delay=(0.5, 1.0),  # Random delay range
        max_delay=10.0,         # Max backoff
    )
)

# Memory-adaptive (default)
dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold=0.7,  # Pause if memory exceeds 70%
)
```

### Best Practices for Ethical Crawling

1. **Always enable robots.txt checking** for public websites
2. **Use rate limiting** to avoid overwhelming servers
3. **Set a descriptive User-Agent** to identify your crawler
4. **Cache results** to avoid redundant requests
5. **Review ToS** of sites you crawl

---

## Integration Recommendations for Knowledge MCP

### Recommended Configuration

```python
# knowledge_mcp/ingest/web_ingestor.py

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.dispatcher import SemaphoreDispatcher, RateLimiter

class WebIngestorConfig:
    """Default configuration for Knowledge MCP web ingestion."""

    @staticmethod
    def browser_config() -> BrowserConfig:
        return BrowserConfig(
            headless=True,
            verbose=False,
            text_mode=False,  # Keep images for reference
        )

    @staticmethod
    def run_config(respect_robots: bool = True) -> CrawlerRunConfig:
        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            check_robots_txt=respect_robots,
            word_count_threshold=100,  # Lower threshold for technical docs
            remove_overlay_elements=True,
            exclude_external_links=False,  # Keep for link extraction
            process_iframes=True,
        )

    @staticmethod
    def dispatcher(max_concurrent: int = 3) -> SemaphoreDispatcher:
        return SemaphoreDispatcher(
            semaphore_count=max_concurrent,
            rate_limiter=RateLimiter(
                base_delay=(1.0, 2.0),  # Conservative rate limiting
                max_delay=30.0,
            )
        )
```

### Integration Architecture

```
WebIngestor
    |
    +-- AsyncWebCrawler (Crawl4AI)
    |       |
    |       +-- BrowserConfig (shared across crawls)
    |       +-- CrawlerRunConfig (per-URL settings)
    |       +-- SemaphoreDispatcher (rate limiting)
    |
    +-- ContentProcessor
    |       |
    |       +-- markdown -> hierarchical chunker
    |       +-- metadata extraction (title, date, etc.)
    |
    +-- QualityAssessor
            |
            +-- word count validation
            +-- language detection
            +-- relevance scoring
```

### Error Handling Pattern

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class WebIngestionResult:
    url: str
    success: bool
    markdown: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

async def ingest_url(url: str) -> WebIngestionResult:
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            return WebIngestionResult(
                url=url,
                success=False,
                error=result.error_message,
                status_code=result.status_code,
            )

        if result.status_code == 403:
            return WebIngestionResult(
                url=url,
                success=False,
                error="Blocked by robots.txt",
                status_code=403,
            )

        markdown = result.markdown.raw_markdown
        if len(markdown.split()) < 50:
            return WebIngestionResult(
                url=url,
                success=False,
                error="Insufficient content",
            )

        return WebIngestionResult(
            url=url,
            success=True,
            markdown=markdown,
            title=extract_title(result.html),
            status_code=result.status_code,
        )
```

---

## Known Issues & Limitations

### Current Limitations

| Issue | Severity | Mitigation |
|-------|----------|------------|
| Memory usage with parallel crawls | Medium | Use MemoryAdaptiveDispatcher, limit concurrency |
| Complex multi-step authentication | Medium | Use storage_state or persistent profiles |
| Playwright browser size (~500MB) | Low | Accept for production, use Docker for isolation |
| Rate limit backoff was hardcoded (fixed in 0.7.8) | Fixed | Update to latest version |
| Docker API security concerns | High | Hooks disabled by default in 0.8.0, avoid Docker API for untrusted input |

### Version-Specific Issues

**v0.7.x:**
- ContentRelevanceFilter deserialization failed in Docker API (fixed in 0.7.8)
- ProxyConfig serialization issues (fixed in 0.7.8)
- Relative URL resolution after JS redirects (fixed in 0.7.8)

**v0.8.0:**
- New release, may have undiscovered issues
- Consider using 0.7.8 for stability initially

### Recommendations

1. **Pin version in pyproject.toml:**
   ```toml
   crawl4ai = "^0.7.8"  # or "^0.8.0" after testing
   ```

2. **Run `crawl4ai-doctor` in CI** to verify installation

3. **Handle errors gracefully** - network and browser issues are common

4. **Set reasonable timeouts** for long-running pages

---

## Comparison with Alternatives

| Feature | Crawl4AI | Firecrawl | Scrapy |
|---------|----------|-----------|--------|
| Async native | Yes | API-based | Via Twisted |
| JS rendering | Playwright | Playwright | Via Splash |
| Markdown output | Native | Native | Manual |
| Rate limiting | Built-in | API limit | Manual |
| Open source | Yes (Apache-2.0) | Partially | Yes (BSD) |
| LLM extraction | Built-in | Built-in | Manual |
| Memory adaptive | Yes | N/A | Manual |
| Cost | Free | Paid tiers | Free |

**Recommendation:** Crawl4AI is the best choice for Knowledge MCP due to:
- Native async architecture matching our stack
- Built-in Markdown output for RAG pipelines
- Open source with no API costs
- Active maintenance and community

---

## Dependencies

When installed, Crawl4AI brings:

```
crawl4ai
├── playwright (browser automation)
├── beautifulsoup4 (HTML parsing)
├── httpx (async HTTP)
├── pydantic (data validation)
├── aiofiles (async file I/O)
├── litellm (optional, for LLM extraction)
└── sentence-transformers (optional, for [transformer] install)
```

**Compatibility with Knowledge MCP:**
- No conflicts with existing dependencies (Docling, SQLAlchemy, Qdrant)
- Playwright browser management adds complexity but is well-isolated
- Memory requirements increase when running parallel crawls

---

## Sources

### Official Documentation (HIGH confidence)
- [Crawl4AI Documentation (v0.7.x)](https://docs.crawl4ai.com/)
- [Quick Start Guide](https://docs.crawl4ai.com/core/quickstart/)
- [AsyncWebCrawler API](https://docs.crawl4ai.com/api/async-webcrawler/)
- [Browser & Crawler Config](https://docs.crawl4ai.com/core/browser-crawler-config/)
- [Multi-URL Crawling](https://docs.crawl4ai.com/advanced/multi-url-crawling/)
- [Hooks & Auth](https://docs.crawl4ai.com/advanced/hooks-auth/)
- [LLM-Free Strategies](https://docs.crawl4ai.com/extraction/no-llm-strategies/)

### GitHub & Releases (HIGH confidence)
- [GitHub Repository](https://github.com/unclecode/crawl4ai)
- [Releases](https://github.com/unclecode/crawl4ai/releases)
- [PyPI Package](https://pypi.org/project/Crawl4AI/)

### Community Resources (MEDIUM confidence)
- [Crawl4AI vs Firecrawl Comparison](https://www.scrapeless.com/en/blog/crawl4ai-vs-firecrawl)
- [ScrapingBee Crawl4AI Guide](https://www.scrapingbee.com/blog/crawl4ai/)
- [Crawl4AI Setup Guide](https://www.crawl4.com/blog/crawl4ai-setup-guide-install-config-best-practices)
