#!/usr/bin/env python3
"""
Web Researcher for Concept Development

Crawls and processes web content for domain research using crawl4ai.
Integrates with source_tracker.py for automatic source registration.
Supports single-page, batch, deep-crawl, and summary modes.

Requires: crawl4ai >= 0.7.4 (except 'summary' subcommand which reads local files only)
"""

import json
import sys
import asyncio
import argparse
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse


class WebResearcher:
    """Manages web research crawling and artifact storage for concept development."""

    VALID_PHASES = ['spitball', 'problem', 'blackbox', 'drilldown', 'document']

    def __init__(self, research_dir: str = '.concept-dev/research'):
        self.research_dir = Path(research_dir)
        self.index_path = self.research_dir / 'research_index.json'
        self.index = self._load_index()

    # ── Registry management ──────────────────────────────────────

    def _load_index(self) -> Dict[str, Any]:
        """Load existing research index or create new one."""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'version': '1.0'
            },
            'entries': []
        }

    def _save_index(self):
        """Save research index atomically."""
        self.research_dir.mkdir(parents=True, exist_ok=True)
        self.index['metadata']['last_modified'] = datetime.now().isoformat()
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.research_dir), suffix='.tmp'
        )
        try:
            with open(fd, 'w') as f:
                json.dump(self.index, f, indent=2)
            Path(tmp_path).replace(self.index_path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    def _generate_id(self) -> str:
        """Generate unique research artifact ID (WR-001, WR-002, ...)."""
        existing_ids = [e['id'] for e in self.index['entries']]
        counter = 1
        while f"WR-{counter:03d}" in existing_ids:
            counter += 1
        return f"WR-{counter:03d}"

    # ── Source tracker integration ───────────────────────────────

    def _get_source_tracker(self):
        """Import and return a SourceTracker instance."""
        sys.path.insert(0, str(Path(__file__).parent))
        from source_tracker import SourceTracker
        return SourceTracker()

    def _register_source(
        self,
        title: str,
        url: str,
        query: str,
        phase: str,
        md_path: str,
        confidence: str = 'medium'
    ) -> Optional[str]:
        """Register a crawled page as a source. Returns source ID or None on failure."""
        try:
            tracker = self._get_source_tracker()
            source_id = tracker.add_source(
                name=title,
                source_type='web_research',
                url=url,
                confidence=confidence,
                phase=phase,
                file_path=str(md_path),
                notes=f"Crawled for: {query}"
            )
            return source_id
        except Exception as e:
            print(f"  Warning: Failed to register source: {e}", file=sys.stderr)
            return None

    # ── Crawl4ai configuration helpers ───────────────────────────

    def _create_bm25_generator(self, query: str):
        """Create a BM25-filtered markdown generator with citations."""
        from crawl4ai.content_filter_strategy import BM25ContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

        bm25_filter = BM25ContentFilter(
            user_query=query,
            bm25_threshold=1.2,
            language="english"
        )
        md_generator = DefaultMarkdownGenerator(
            content_filter=bm25_filter,
            options={"citations": True}
        )
        return md_generator

    def _create_run_config(self, query: str, css_selector: Optional[str] = None, **kwargs):
        """Create a CrawlerRunConfig with standard settings."""
        from crawl4ai import CrawlerRunConfig, CacheMode

        md_generator = self._create_bm25_generator(query)

        config_kwargs = {
            'markdown_generator': md_generator,
            'cache_mode': CacheMode.BYPASS,
            'excluded_tags': ['nav', 'footer', 'header', 'aside'],
            'word_count_threshold': 10,
            'remove_overlay_elements': True,
            'page_timeout': 30000,
        }

        if css_selector:
            config_kwargs['css_selector'] = css_selector

        config_kwargs.update(kwargs)
        return CrawlerRunConfig(**config_kwargs)

    # ── Result processing ────────────────────────────────────────

    def _process_crawl_result(
        self,
        result,
        query: str,
        phase: str
    ) -> Optional[Dict[str, Any]]:
        """Process a single crawl result into a research artifact.

        Returns the index entry dict, or None if the crawl failed.
        """
        if not result.success:
            print(f"  FAILED: {result.url} — {result.error_message}", file=sys.stderr)
            return None

        wr_id = self._generate_id()

        # Extract content — prefer BM25-filtered, fall back to raw
        fit_content = getattr(result.markdown, 'fit_markdown', None) or ''
        raw_content = getattr(result.markdown, 'raw_markdown', None) or ''
        references = getattr(result.markdown, 'references_markdown', None) or ''

        content = fit_content if fit_content.strip() else raw_content
        if not content.strip():
            print(f"  SKIPPED: {result.url} — no content extracted", file=sys.stderr)
            return None

        # Extract metadata
        result_meta = result.metadata or {}
        title = result_meta.get('title', '') or urlparse(result.url).netloc
        description = result_meta.get('description', '')
        depth = result_meta.get('depth', 0)
        score = result_meta.get('score', 0)

        # Word counts
        fit_words = len(fit_content.split()) if fit_content else 0
        raw_words = len(raw_content.split()) if raw_content else 0
        relevance_ratio = round(fit_words / raw_words, 4) if raw_words > 0 else 0.0

        # Link counts
        links = result.links or {}
        internal_links = links.get('internal', [])
        external_links = links.get('external', [])

        # Confidence heuristic based on relevance ratio
        confidence = 'medium' if relevance_ratio >= 0.5 else 'low'

        # Save markdown artifact
        md_path = self.research_dir / f"{wr_id}.md"
        now_iso = datetime.now().isoformat()

        md_content = f"""---
id: {wr_id}
url: {result.url}
title: "{title.replace('"', '\\"')}"
query: "{query.replace('"', '\\"')}"
phase: {phase}
crawled_at: {now_iso}
relevance_ratio: {relevance_ratio}
---

{content}
"""
        if references.strip():
            md_content += f"\n## References\n\n{references}\n"

        self._write_file_atomic(md_path, md_content)

        # Save metadata JSON
        meta = {
            'id': wr_id,
            'url': result.url,
            'title': title,
            'description': description,
            'query': query,
            'phase': phase,
            'crawled_at': now_iso,
            'status_code': result.status_code,
            'relevance_ratio': relevance_ratio,
            'fit_word_count': fit_words,
            'raw_word_count': raw_words,
            'internal_link_count': len(internal_links),
            'external_link_count': len(external_links),
            'depth': depth,
            'score': score,
        }
        meta_path = self.research_dir / f"{wr_id}.meta.json"
        self._write_file_atomic(meta_path, json.dumps(meta, indent=2))

        # Register source
        source_id = self._register_source(
            title=title,
            url=result.url,
            query=query,
            phase=phase,
            md_path=str(md_path),
            confidence=confidence
        )

        # Add to index
        entry = {
            'id': wr_id,
            'url': result.url,
            'title': title,
            'query': query,
            'phase': phase,
            'source_id': source_id,
            'crawled_at': now_iso,
            'relevance_ratio': relevance_ratio,
            'fit_word_count': fit_words,
            'raw_word_count': raw_words,
            'md_file': str(md_path),
            'meta_file': str(meta_path),
        }
        self.index['entries'].append(entry)
        self._save_index()

        print(f"  [{wr_id}] {title[:60]}")
        print(f"    URL: {result.url}")
        print(f"    Relevance: {relevance_ratio:.1%} ({fit_words}/{raw_words} words)")
        if source_id:
            print(f"    Source: {source_id}")

        return entry

    def _write_file_atomic(self, path: Path, content: str):
        """Write a file atomically."""
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
        try:
            with open(fd, 'w') as f:
                f.write(content)
            Path(tmp_path).replace(path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

    # ── Subcommand: crawl ────────────────────────────────────────

    async def crawl(
        self,
        url: str,
        query: str,
        phase: str = 'drilldown',
        css_selector: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Crawl a single URL with BM25 relevance filtering."""
        from crawl4ai import AsyncWebCrawler

        print(f"\nCrawling: {url}")
        print(f"  Query: {query}")
        print(f"  Phase: {phase}")

        config = self._create_run_config(query, css_selector=css_selector)

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=config)

        entry = self._process_crawl_result(result, query, phase)
        if entry:
            print(f"\nDone. Artifact saved: {entry['id']}")
        return entry

    # ── Subcommand: batch ────────────────────────────────────────

    async def batch(
        self,
        urls: List[str],
        query: str,
        phase: str = 'drilldown',
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Crawl multiple URLs concurrently with BM25 filtering."""
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher

        print(f"\nBatch crawl: {len(urls)} URLs")
        print(f"  Query: {query}")
        print(f"  Phase: {phase}")
        print(f"  Max concurrent: {max_concurrent}")

        config = self._create_run_config(query)
        configs = [config] * len(urls)

        dispatcher = MemoryAdaptiveDispatcher(max_session_permit=max_concurrent)

        entries = []
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun_many(urls, config=configs, dispatcher=dispatcher)
            for result in results:
                entry = self._process_crawl_result(result, query, phase)
                if entry:
                    entries.append(entry)

        print(f"\nDone. {len(entries)}/{len(urls)} URLs processed successfully.")
        return entries

    # ── Subcommand: deep ─────────────────────────────────────────

    async def deep(
        self,
        base_url: str,
        query: str,
        phase: str = 'drilldown',
        max_depth: int = 2,
        max_pages: int = 20,
        pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Deep crawl with relevance-prioritized link following."""
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
        from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
        from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

        print(f"\nDeep crawl: {base_url}")
        print(f"  Query: {query}")
        print(f"  Phase: {phase}")
        print(f"  Max depth: {max_depth}, Max pages: {max_pages}")
        if pattern:
            print(f"  URL pattern: *{pattern}*")

        # Build keyword scorer from query
        keywords = query.split()
        scorer = KeywordRelevanceScorer(keywords=keywords, weight=0.7)

        # Optional URL filter
        filters = None
        if pattern:
            filters = FilterChain([URLPatternFilter(patterns=[f"*{pattern}*"])])

        strategy = BestFirstCrawlingStrategy(
            max_depth=max_depth,
            include_external=False,
            url_scorer=scorer,
            filter_chain=filters,
            max_pages=max_pages
        )

        config = self._create_run_config(
            query,
            deep_crawl_strategy=strategy,
            stream=True
        )

        entries = []
        page_count = 0

        async with AsyncWebCrawler() as crawler:
            async for result in await crawler.arun(base_url, config=config):
                page_count += 1
                result_meta = result.metadata or {}
                depth = result_meta.get('depth', 0)
                score = result_meta.get('score', 0)
                print(f"\n  Page {page_count} (depth={depth}, score={score:.2f}):")
                entry = self._process_crawl_result(result, query, phase)
                if entry:
                    entries.append(entry)

        print(f"\nDone. {len(entries)}/{page_count} pages processed successfully.")
        return entries

    # ── Subcommand: summary ──────────────────────────────────────

    def summary(self, query: Optional[str] = None) -> str:
        """Generate a research summary from the index. No crawl4ai needed."""
        entries = self.index.get('entries', [])
        if not entries:
            return "No research artifacts found. Run `crawl`, `batch`, or `deep` first."

        # Sort by relevance
        sorted_entries = sorted(entries, key=lambda e: e.get('relevance_ratio', 0), reverse=True)

        lines = []
        lines.append("# Research Summary")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Total artifacts: {len(entries)}")

        # Filter by query if provided
        if query:
            query_lower = query.lower()
            sorted_entries = [
                e for e in sorted_entries
                if query_lower in e.get('query', '').lower()
                or query_lower in e.get('title', '').lower()
            ]
            lines.append(f"Filter query: {query}")
            lines.append(f"Matching artifacts: {len(sorted_entries)}")

        lines.append("")

        # Phase summary
        phases = {}
        for e in sorted_entries:
            p = e.get('phase', 'unknown')
            phases[p] = phases.get(p, 0) + 1
        if phases:
            lines.append("## By Phase")
            for phase, count in sorted(phases.items()):
                lines.append(f"- **{phase}**: {count} artifacts")
            lines.append("")

        # Entries
        lines.append("## Artifacts (sorted by relevance)")
        lines.append("")
        for entry in sorted_entries:
            wr_id = entry['id']
            title = entry.get('title', 'Untitled')
            url = entry.get('url', '')
            ratio = entry.get('relevance_ratio', 0)
            src = entry.get('source_id', 'N/A')
            fit_words = entry.get('fit_word_count', 0)
            phase = entry.get('phase', '')

            lines.append(f"### [{wr_id}] {title}")
            lines.append(f"- **URL:** {url}")
            lines.append(f"- **Relevance:** {ratio:.1%} ({fit_words} relevant words)")
            lines.append(f"- **Phase:** {phase}")
            lines.append(f"- **Source:** {src}")
            lines.append(f"- **Query:** {entry.get('query', '')}")

            # Try to read a content excerpt from the .md file
            md_file = entry.get('md_file', '')
            if md_file and Path(md_file).exists():
                try:
                    with open(md_file, 'r') as f:
                        full_text = f.read()
                    # Skip frontmatter
                    parts = full_text.split('---', 2)
                    body = parts[2].strip() if len(parts) >= 3 else full_text
                    # Take first 300 chars as excerpt
                    excerpt = body[:300].strip()
                    if len(body) > 300:
                        excerpt += '...'
                    lines.append(f"\n> {excerpt}")
                except Exception:
                    pass

            lines.append("")

        return '\n'.join(lines)


# ── CLI ──────────────────────────────────────────────────────────

def _parse_urls(url_arg: str) -> List[str]:
    """Parse URLs from comma-separated string or file path."""
    path = Path(url_arg)
    if path.exists() and path.is_file():
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [u.strip() for u in url_arg.split(',') if u.strip()]


def main():
    parser = argparse.ArgumentParser(
        description='Web research tool for concept development using crawl4ai'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # crawl — single URL
    crawl_parser = subparsers.add_parser('crawl', help='Crawl a single URL with BM25 filtering')
    crawl_parser.add_argument('url', help='URL to crawl')
    crawl_parser.add_argument('--query', required=True, help='Research query for relevance filtering')
    crawl_parser.add_argument('--phase', default='drilldown', choices=WebResearcher.VALID_PHASES,
                              help='Concept-dev phase (default: drilldown)')
    crawl_parser.add_argument('--css-selector', help='CSS selector for focused extraction')

    # batch — multiple URLs
    batch_parser = subparsers.add_parser('batch', help='Crawl multiple URLs concurrently')
    batch_parser.add_argument('urls', help='Comma-separated URLs or path to file with one URL per line')
    batch_parser.add_argument('--query', required=True, help='Research query for relevance filtering')
    batch_parser.add_argument('--phase', default='drilldown', choices=WebResearcher.VALID_PHASES,
                              help='Concept-dev phase (default: drilldown)')
    batch_parser.add_argument('--max-concurrent', type=int, default=5,
                              help='Max concurrent crawls (default: 5)')

    # deep — deep crawl
    deep_parser = subparsers.add_parser('deep', help='Deep crawl with relevance-prioritized link following')
    deep_parser.add_argument('base_url', help='Starting URL for deep crawl')
    deep_parser.add_argument('--query', required=True, help='Research query for relevance filtering')
    deep_parser.add_argument('--phase', default='drilldown', choices=WebResearcher.VALID_PHASES,
                             help='Concept-dev phase (default: drilldown)')
    deep_parser.add_argument('--max-depth', type=int, default=2,
                             help='Max link-follow depth (default: 2)')
    deep_parser.add_argument('--max-pages', type=int, default=20,
                             help='Max pages to crawl (default: 20)')
    deep_parser.add_argument('--pattern', help='URL pattern filter (e.g., "docs", "blog")')

    # summary — generate research summary
    summary_parser = subparsers.add_parser('summary', help='Generate summary from research artifacts')
    summary_parser.add_argument('--query', help='Filter summary to artifacts matching this query')

    # Common arguments
    parser.add_argument('--research-dir', default='.concept-dev/research',
                        help='Path to research directory')

    args = parser.parse_args()

    researcher = WebResearcher(research_dir=args.research_dir)

    if args.command == 'crawl':
        asyncio.run(researcher.crawl(
            url=args.url,
            query=args.query,
            phase=args.phase,
            css_selector=args.css_selector
        ))

    elif args.command == 'batch':
        urls = _parse_urls(args.urls)
        if not urls:
            print("Error: No valid URLs provided.", file=sys.stderr)
            sys.exit(1)
        asyncio.run(researcher.batch(
            urls=urls,
            query=args.query,
            phase=args.phase,
            max_concurrent=args.max_concurrent
        ))

    elif args.command == 'deep':
        asyncio.run(researcher.deep(
            base_url=args.base_url,
            query=args.query,
            phase=args.phase,
            max_depth=args.max_depth,
            max_pages=args.max_pages,
            pattern=args.pattern
        ))

    elif args.command == 'summary':
        output = researcher.summary(query=args.query)
        print(output)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
