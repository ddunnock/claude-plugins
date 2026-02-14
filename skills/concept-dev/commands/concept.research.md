---
name: concept:research
description: Research web sources for concept development using crawl4ai. Crawls URLs, extracts relevant content with BM25 filtering, and auto-registers sources.
---

# /concept:research

Research web sources for concept development. Crawls URLs with relevance filtering and automatically registers findings in the source registry.

## Usage

```
/concept:research [url] [query]
/concept:research                         # Interactive — prompts for topic and URLs
/concept:research https://example.com/docs "spacecraft thermal management"
```

## Procedure

### Step 1: Gather Research Parameters

If no arguments provided, ask the user:

1. **Research topic/query** — What are you researching? (used for BM25 relevance filtering)
2. **URL(s)** — Specific URLs, or should we start with a WebSearch?
3. **Mode** — Single page, batch, or deep crawl of a documentation site?

If URL(s) and query are provided as arguments, proceed directly.

### Step 2: Check crawl4ai Availability

Verify crawl4ai is installed:

```bash
python3 -c "import crawl4ai; print(f'crawl4ai {crawl4ai.__version__}')"
```

If not installed, inform the user:

> crawl4ai is not installed. Install it with: `pip install crawl4ai`
>
> In the meantime, I can use WebSearch and WebFetch for research.

Fall back to WebSearch + WebFetch workflow if crawl4ai is unavailable.

### Step 3: Determine Current Phase

Check state.json for the current phase:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/update_state.py --state .concept-dev/state.json show
```

Use the current phase for source tagging. Default to `drilldown` if no session is active.

### Step 4: Execute Research

Choose the appropriate mode based on user input:

**Single URL — focused deep-read:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_researcher.py crawl "<url>" --query "<query>" --phase <phase>
```

Use `--css-selector` if the user wants to focus on a specific page section (e.g., `.main-content`, `article`).

**Multiple URLs — batch crawl:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_researcher.py batch "<url1>,<url2>,<url3>" --query "<query>" --phase <phase> --max-concurrent 5
```

URLs can also be provided as a file path (one URL per line).

**Documentation site — deep crawl with link following:**

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_researcher.py deep "<base_url>" --query "<query>" --phase <phase> --max-depth 2 --max-pages 20
```

Use `--pattern` to restrict crawled URLs (e.g., `--pattern docs` only follows links containing "docs").

### Step 5: Report Results

After crawling completes, summarize:

```
===================================================================
RESEARCH RESULTS
===================================================================

Query: "<query>"
Phase: <phase>
Mode: <crawl|batch|deep>

ARTIFACTS:
  [WR-001] Page Title (relevance: 72%, source: SRC-012)
  [WR-002] Another Page (relevance: 45%, source: SRC-013)

Files saved to: .concept-dev/research/
Sources registered: SRC-012, SRC-013

Next steps:
  - Review artifacts in .concept-dev/research/
  - Run /concept:research again for additional URLs
  - Generate summary: python3 scripts/web_researcher.py summary
===================================================================
```

### Step 6: Generate Summary (Optional)

If the user wants an overview of all research so far:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_researcher.py summary --query "<query>"
```

This reads the local research index — no crawling needed.

## Tips

- **BM25 filtering** automatically extracts the most relevant paragraphs matching your query. Higher relevance ratios mean better topic match.
- **Deep crawl** is ideal for documentation sites — it follows links intelligently, prioritizing pages whose URLs and content match your keywords.
- **All sources are auto-registered** in the source registry. Use `python3 scripts/source_tracker.py list` to see them.
- Research artifacts include YAML frontmatter with metadata for easy programmatic access.
