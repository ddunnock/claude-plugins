# Research Strategies

Tool tier definitions, usage patterns, and fallback chains for concept development research.

## Tool Tiers

### Always Available

**WebSearch** — Broad discovery
- Best for: Initial domain exploration, finding recent articles, identifying key players
- Limitations: Results are summaries, not deep content
- Strategy: Use for first pass, then follow up with deeper tools

**WebFetch** — URL content retrieval
- Best for: Reading specific pages identified via search
- Limitations: Some sites block; large pages may be truncated
- Strategy: Use after WebSearch identifies promising URLs

### Tier 1: Free MCP Tools

**crawl4ai** — Deep web crawling
- Best for: Comprehensive coverage of a specific site or domain
- Use when: You need to understand an entire documentation site, wiki, or resource collection
- Example: Crawl a standards body's documentation for relevant specifications

**Jina Reader** — Document parsing
- Best for: Extracting structured content from complex pages
- Use when: WebFetch returns messy content; need clean text from PDFs or complex layouts

**MCP Fetch** — Alternative URL fetching
- Best for: Fetching when WebFetch fails or is blocked
- Fallback for WebFetch

**Paper Search** — Academic paper discovery
- Best for: Finding peer-reviewed research and technical reports
- Use when: Need HIGH confidence sources for technical claims

### Tier 2: Configurable

**Tavily** — AI-powered search
- Best for: Getting synthesized answers with citations
- Use when: Need a quick overview of a technical topic with sources

**Semantic Scholar** — Academic API
- Best for: Systematic literature review, citation tracking
- Use when: Need to find the canonical papers in a domain

**Context7** — Documentation search
- Best for: Finding specific information in software/tool documentation
- Use when: Researching specific platforms or frameworks

### Tier 3: Premium

**Exa** — Neural search
- Best for: Finding conceptually similar content across the web
- Use when: Looking for analogous solutions in different domains

**Perplexity Sonar** — AI search with synthesis
- Best for: Comprehensive answers to complex technical questions
- Use when: Need a thorough overview of a domain quickly

## Research Strategy by Phase

### Phase 1 (Spit-Ball)
- **Tools:** WebSearch only
- **Depth:** Surface-level feasibility checks
- **Purpose:** Quick "does this concept area have precedent?" checks
- **Time per search:** 30 seconds max
- **Don't:** Deep-dive into any single idea

### Phase 2 (Problem Definition)
- **Tools:** WebSearch only
- **Depth:** Targeted fact-checking
- **Purpose:** Verify stakeholder claims, quantify consequences, check for existing solutions
- **Strategy:** Search for "[domain] current challenges", "[problem area] industry data"
- **Don't:** Deep-dive into solutions; note them for Phase 4

### Phase 3 (Black-Box Architecture)
- **Tools:** WebSearch, WebFetch
- **Depth:** Pattern discovery
- **Purpose:** Find analogous architectures, validate functional decomposition patterns
- **Strategy:** Search for "[domain] architecture patterns", "[capability] functional decomposition"
- **Don't:** Research implementation details; stay at the functional level

### Phase 4 (Drill-Down)
- **Tools:** All available tiers
- **Depth:** Thorough research per sub-function
- **Purpose:** Find prior art, assess maturity, identify gaps, catalog approaches
- **Strategy per sub-function:**
  1. WebSearch for broad discovery (2-3 queries)
  2. Paper Search / Semantic Scholar for academic grounding
  3. WebFetch on promising results for detailed reading
  4. crawl4ai for comprehensive site coverage if needed
  5. Exa/Perplexity for gap-filling

### Phase 5 (Document)
- **Tools:** Targeted verification only
- **Depth:** Fact-checking and gap-filling
- **Purpose:** Verify claims before publication, fill specific gaps
- **Strategy:** Targeted searches to verify skeptic-flagged claims

## Fallback Chain

When a tool is unavailable, fall back gracefully:

```
Preferred         → Fallback 1       → Fallback 2       → Last Resort
─────────────────────────────────────────────────────────────────────
Exa               → Tavily           → WebSearch         → Note limitation
Semantic Scholar  → Paper Search     → WebSearch + "paper" → Note limitation
crawl4ai          → WebFetch         → WebSearch         → Note limitation
Perplexity        → Tavily           → WebSearch         → Note limitation
Jina Reader       → WebFetch         → Note limitation
Context7          → WebFetch + docs  → WebSearch + docs  → Note limitation
```

When falling back, note in the research output:
```
NOTE: Research for [topic] used [tool] as fallback for [preferred tool].
Coverage may be less comprehensive than optimal.
```

## Search Query Patterns

### Domain Discovery
```
"[domain] state of the art [year]"
"[domain] approaches survey"
"[capability] architecture patterns"
```

### Prior Art
```
"[similar system] architecture design"
"[domain] case study [capability]"
"[concept] implementation experience"
```

### Academic
```
"[domain] survey paper [year range]"
"[capability] systematic review"
"[approach] evaluation comparison"
```

### Skeptical / Counter-Evidence
```
"[approach] limitations challenges"
"[technology] failure cases problems"
"[claim] criticism alternative"
"why not [approach]"
```

### Gap-Filling
```
"[specific gap] solution approaches"
"[standard] [specific requirement]"
"[domain] open problems research directions"
```
