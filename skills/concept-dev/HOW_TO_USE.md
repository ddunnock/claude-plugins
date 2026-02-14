# How to Use concept-dev

This guide walks through a complete concept development session, from initialization to final document.

## Before You Start

The plugin activates when you mention concept development, brainstorming a system concept, exploring a new idea, running Phase A, or similar phrases. You can also invoke commands directly with `/concept:*`.

No special setup is required beyond having the plugin installed. If you want deep web research capabilities, install crawl4ai:

```bash
pip install crawl4ai
crawl4ai-setup
```

## Starting a Session

### Initialize

```
/concept:init
```

This creates a `.concept-dev/` workspace in your current directory and probes for available research tools. You'll see a banner showing detected tools and the five phases ahead.

You can optionally name your project at this point, or skip straight to ideation.

### Resume a Previous Session

If you already have a `.concept-dev/` directory from a previous conversation:

```
/concept:resume
```

This loads your existing state and picks up where you left off.

### Check Status Anytime

```
/concept:status
```

Shows current phase, gate status, source counts, assumption counts, and skeptic findings.

## Phase 1: Spit-Ball

```
/concept:spitball
```

This is the wild ideas phase. There are no bad ideas here.

**What happens:**
- Claude opens with an invitation to share whatever's on your mind
- You describe problems, half-formed thoughts, "what if" scenarios
- Claude asks follow-up questions, probes feasibility via web searches, and pushes ideas further with "what if" extensions
- After several ideas, Claude clusters them into themes

**What you do:**
- Share ideas freely — no structure needed
- When themes are presented, select which ones have energy and should move forward

**Gate:** You must select themes to advance. Claude will not proceed until you choose.

**Output:** `IDEAS.md` — captured ideas organized by theme with feasibility notes.

### Example Interaction

```
You: I've been thinking about how hard it is to manage thermal loads
     on small satellites. What if there was a way to dynamically
     redistribute heat across the structure?

Claude: Interesting — that touches on both passive thermal management
        and active control. What if the redistribution happened
        autonomously based on sensor feedback? ...
        [probes feasibility, asks follow-ups]

You: Yeah, and maybe it could use phase-change materials that
     respond to temperature thresholds...

Claude: [searches for PCM thermal management in spacecraft]
        There's precedent here — ...
```

## Phase 2: Problem Definition

```
/concept:problem
```

Refines your selected themes into a clear, bounded problem statement.

**What happens:**
- Claude uses adapted 5W2H questioning (Who, What, Where, When, Why, How, How Much)
- Questions come in batches of 3-4, then a checkpoint — no question floods
- If you mention a specific technology or solution, Claude notes it for Phase 4 and redirects to keep the problem definition solution-agnostic

**What you do:**
- Answer questions about scope, stakeholders, constraints, success criteria
- Review and approve the problem statement when presented

**Gate:** You must approve the problem statement.

**Output:** `PROBLEM-STATEMENT.md`

## Phase 3: Black-Box Architecture

```
/concept:blackbox
```

Defines the concept at a functional level — blocks, relationships, and principles — without specifying implementation.

**What happens:**
- Claude proposes 2-3 architectural approaches with trade-offs
- You select one
- Claude elaborates with ASCII diagrams showing functional blocks and their relationships
- Each section is presented for individual approval

**What you do:**
- Choose an architectural approach
- Approve each section (or request revisions)

**Gate:** You must approve the architecture section by section.

**Output:** `BLACKBOX.md`

### What "Solution-Agnostic" Means

Through Phases 1-3, the focus is on WHAT the concept does, not HOW. For example:

- "Thermal regulation subsystem" (what it does) vs. "heat pipe array" (how)
- "Data fusion block" (function) vs. "Kalman filter" (implementation)

Solutions are explored in Phase 4.

## Phase 4: Drill-Down & Gap Analysis

```
/concept:drilldown
```

This is where research happens. Each functional block from Phase 3 gets decomposed.

**What happens:**
- For each block: Claude researches the domain, identifies knowledge gaps, and lists potential solution APPROACHES (not picks)
- Sources are registered with confidence ratings (HIGH, MEDIUM, LOW, UNGROUNDED)
- The skeptic agent verifies claims before presenting them
- Supports AUTO mode for autonomous research across all blocks

**What you do:**
- Review research findings per block
- Flag anything that seems wrong or needs more investigation
- Approve the complete drill-down

**Gate:** You must review and approve the complete drill-down.

**Output:** `DRILLDOWN.md`

### Using Web Research

During Phase 4 (or anytime), you can invoke deep web research:

```
/concept:research https://docs.example.com "thermal management approaches"
```

Or interactively:

```
/concept:research
```

This prompts you for a topic, URLs, and crawl mode (single, batch, or deep). Results are saved as numbered artifacts (`WR-001.md`, `WR-002.md`, ...) with YAML frontmatter and auto-registered as sources.

**Three crawl modes:**

| Mode | When to Use |
|------|-------------|
| `crawl` | Single URL deep-read with BM25 relevance filtering |
| `batch` | Multiple URLs concurrently |
| `deep` | Follow links from a base URL (great for documentation sites) |

## Phase 5: Document Generation

```
/concept:document
```

Produces the two final deliverables.

**What happens:**
- Claude composes the Concept Document and Solution Landscape
- Each section is presented for your approval before moving to the next
- Mandatory assumption review before finalization — all tracked assumptions must be addressed

**What you do:**
- Review and approve each section
- Address any pending assumptions
- Approve both final documents

**Gate:** Both documents must be approved.

**Outputs:**
- `CONCEPT-DOCUMENT.md` — Problem, concept overview, capabilities, ConOps, maturation path
- `SOLUTION-LANDSCAPE.md` — Per-domain approaches with pros/cons, citations, confidence ratings

## Source and Assumption Tracking

### Sources

Every research finding is registered with a confidence level:

| Level | Meaning |
|-------|---------|
| HIGH | Peer-reviewed, official documentation, or verified test data |
| MEDIUM | Credible but not independently verified (vendor docs, conference talks) |
| LOW | Single source, informal, or uncertain |
| UNGROUNDED | Known from training data but no citable source found |

View registered sources:

```bash
python3 scripts/source_tracker.py --registry .concept-dev/source_registry.json list
```

### Assumptions

Assumptions are tracked throughout and must be reviewed before document finalization:

```bash
python3 scripts/assumption_tracker.py --registry .concept-dev/assumption_registry.json review
```

Categories: scope, feasibility, architecture, domain_knowledge, technology, constraint, stakeholder.

### Skeptic Agent

An opus-powered agent checks for AI slop before research findings reach you:
- Vague feasibility claims without evidence
- Assumed capabilities
- Invented metrics or hallucinated features
- Overly optimistic assessments

You don't need to invoke this — it runs automatically during research phases.

## Tips

- **You can skip phases** if you already have a clear problem statement, jump to `/concept:problem` or later. But you'll miss the ideation benefits.
- **Gates are non-negotiable.** This is by design — it prevents the AI from running ahead with unvalidated assumptions.
- **Metered questioning** means you'll never get hit with 10 questions at once. Expect 3-4, then a checkpoint.
- **Solution ideas in early phases** are captured, not ignored. They're just deferred to Phase 4 where they can be properly researched.
- **Use `/concept:status`** anytime to see where you are and what's next.
- **The workspace is portable.** The `.concept-dev/` directory contains everything. You can share it, version control it, or pick it up in a new conversation with `/concept:resume`.

## File Reference

| File | Purpose |
|------|---------|
| `.concept-dev/state.json` | Session state — phases, gates, counters |
| `.concept-dev/source_registry.json` | All registered sources with confidence ratings |
| `.concept-dev/assumption_registry.json` | All tracked assumptions |
| `.concept-dev/IDEAS.md` | Phase 1 output |
| `.concept-dev/PROBLEM-STATEMENT.md` | Phase 2 output |
| `.concept-dev/BLACKBOX.md` | Phase 3 output |
| `.concept-dev/DRILLDOWN.md` | Phase 4 output |
| `.concept-dev/CONCEPT-DOCUMENT.md` | Phase 5 deliverable |
| `.concept-dev/SOLUTION-LANDSCAPE.md` | Phase 5 deliverable |
| `.concept-dev/research/` | Web research artifacts (WR-xxx.md) |
| `.concept-dev/research/research_index.json` | Research artifact index |

## Troubleshooting

**"No active session"** — Run `/concept:init` first.

**Phase gate won't pass** — The plugin requires explicit approval. Say something like "approved" or "looks good, let's move on."

**crawl4ai not found** — Install with `pip install crawl4ai && crawl4ai-setup`. The plugin falls back to WebSearch/WebFetch without it.

**State file corrupted** — Delete `.concept-dev/state.json` and run `/concept:init` with option B (start fresh). Your artifact markdown files are preserved.

**Skeptic flags everything** — This is working as intended. Review the flags — if a claim is valid, the skeptic finding gets marked as verified. If not, the claim gets corrected before it reaches your documents.
