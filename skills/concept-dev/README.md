# concept-dev

A Claude Code plugin for structured concept development using the NASA Phase A lifecycle. Walks you from wild ideas to a polished concept document with cited research, tracked assumptions, and skeptic-verified claims.

## What It Does

concept-dev guides you through five progressive phases:

| Phase | Command | Output |
|-------|---------|--------|
| 1. Spit-Ball | `/concept:spitball` | IDEAS.md |
| 2. Problem Definition | `/concept:problem` | PROBLEM-STATEMENT.md |
| 3. Black-Box Architecture | `/concept:blackbox` | BLACKBOX.md |
| 4. Drill-Down & Gap Analysis | `/concept:drilldown` | DRILLDOWN.md |
| 5. Document Generation | `/concept:document` | CONCEPT-DOCUMENT.md, SOLUTION-LANDSCAPE.md |

Each phase has a mandatory gate — Claude will not advance until you explicitly approve the output.

## Final Deliverables

1. **Concept Document** — Problem statement, concept overview, capabilities, concept of operations, and maturation path
2. **Solution Landscape** — Per-domain solution approaches with pros/cons, cited references, and confidence ratings

## Installation

Copy or symlink the `concept-dev/` directory into your Claude Code plugins path. The plugin registers automatically via `.claude-plugin/plugin.json`.

### Optional: crawl4ai for Deep Web Research

```bash
pip install crawl4ai
crawl4ai-setup
```

Without crawl4ai, the plugin uses WebSearch and WebFetch (always available). With it, you get BM25-filtered deep crawls, batch processing, and intelligent link-following.

## Quick Start

```
/concept:init           # Create workspace, detect research tools
/concept:spitball       # Start ideation
```

That's it. The plugin guides you through each phase with prompts, gates, and suggested next steps.

## Commands

| Command | Description |
|---------|-------------|
| `/concept:init` | Initialize session, create `.concept-dev/` workspace, detect MCP research tools |
| `/concept:spitball` | Phase 1 — Open-ended ideation with feasibility probing |
| `/concept:problem` | Phase 2 — Refine ideas into a bounded problem statement |
| `/concept:blackbox` | Phase 3 — Define functional architecture without implementation details |
| `/concept:drilldown` | Phase 4 — Decompose blocks, research domains, identify gaps |
| `/concept:document` | Phase 5 — Generate final deliverables with section-by-section approval |
| `/concept:research` | Web research with crawl4ai (BM25 filtering, batch, deep crawl) |
| `/concept:status` | Session status dashboard with phase progress and metrics |
| `/concept:resume` | Resume an interrupted session |

## Agents

Seven specialized agents handle different aspects of the workflow:

| Agent | Role | Model |
|-------|------|-------|
| ideation-partner | Spit-ball questioning and feasibility probing | sonnet |
| problem-analyst | Problem definition with metered questioning | sonnet |
| concept-architect | Black-box architecture generation | sonnet |
| domain-researcher | Research execution and source verification | sonnet |
| gap-analyst | Gap identification and solution option listing | sonnet |
| skeptic | AI slop checker — verifies claims and solutions | opus |
| document-writer | Final document composition | sonnet |

## Scripts

Six Python scripts manage session state and research data:

| Script | Purpose |
|--------|---------|
| `init_session.py` | Create workspace and initialize state.json |
| `check_tools.py` | Report research tool tier definitions |
| `update_state.py` | Atomic state.json updates (phase, gate, artifact, dotted-path counters, gate checks, registry sync) |
| `source_tracker.py` | Manage source registry with confidence ratings, gap tracking, and auto-sync to state.json |
| `assumption_tracker.py` | Track and review assumptions and ungrounded claims with init and auto-sync to state.json |
| `web_researcher.py` | crawl4ai web research with BM25 filtering |

## Workspace Structure

After initialization, your project gets a `.concept-dev/` directory:

```
.concept-dev/
  state.json                  # Session state (phase, gates, counters)
  source_registry.json        # Registered sources with confidence ratings
  assumption_registry.json    # Tracked assumptions
  IDEAS.md                    # Phase 1 output
  PROBLEM-STATEMENT.md        # Phase 2 output
  BLACKBOX.md                 # Phase 3 output
  DRILLDOWN.md                # Phase 4 output
  CONCEPT-DOCUMENT.md         # Phase 5 output (deliverable 1)
  SOLUTION-LANDSCAPE.md       # Phase 5 output (deliverable 2)
  research/                   # Web research artifacts (WR-xxx.md files)
    research_index.json
```

## Key Design Principles

- **Solution-agnostic through Phase 3** — Phases 1-3 describe WHAT, not HOW. Solutions are deferred to Phase 4.
- **Source grounding** — All claims in Phases 4-5 must reference a registered source or be marked `UNVERIFIED_CLAIM`.
- **Skeptic verification** — An opus-powered agent checks for AI slop before findings reach the user. Invoked explicitly via Task tool in Phases 1, 4, and 5.
- **Assumption tracking** — Every phase registers assumptions to assumption_registry.json with auto-sync to state.json counters.
- **Gate checks** — Programmatic prerequisite validation (`check-gate`) prevents phase skipping.
- **Metered questioning** — 3-4 questions per turn, then checkpoint. No question floods.
- **Atomic state** — All state updates use temp-file-then-rename for crash safety.
- **Auto-sync counters** — Tracker scripts automatically push counts to state.json after every mutation.
- **Auto-state hooks** — Writing artifacts to `.concept-dev/*.md` automatically updates state.json via a PostToolUse hook.

## Research Tool Tiers

The plugin adapts to whatever research tools you have available:

| Tier | Tools | Notes |
|------|-------|-------|
| Always | WebSearch, WebFetch | Built-in to Claude Code |
| Tier 1 | crawl4ai, Jina Reader, MCP Fetch, Paper Search | Free MCP tools |
| Tier 2 | Tavily, Semantic Scholar, Context7 | Configurable |
| Tier 3 | Exa, Perplexity Sonar | Premium, optional |

`/concept:init` probes for each tool and records what's available.

## Plugin Structure

```
concept-dev/
  SKILL.md                          # Skill definition (triggers, phases, rules)
  README.md                         # This file
  HOW_TO_USE.md                     # Detailed walkthrough with examples
  .claude-plugin/plugin.json        # Plugin manifest
  commands/                         # 9 slash commands
  agents/                           # 7 specialized agents
  scripts/                          # 6 Python scripts
  templates/                        # Document templates and state.json template
  references/                       # Research strategies, verification protocol, etc.
  hooks/                            # PostToolUse hook for auto-state updates
    hooks.json
    scripts/update-state-on-write.sh
```

## Further Reading

- [HOW_TO_USE.md](HOW_TO_USE.md) — Step-by-step walkthrough with examples
- [SKILL.md](SKILL.md) — Full skill definition with behavioral rules
