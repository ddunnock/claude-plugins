# Concept Document Structure

Reference structure for concept documents, modeled on engineering concept papers. This defines the target output structure for Phase 5 document generation.

## Document Sections

### 1. Executive Summary
- 2-3 paragraphs
- States the problem, the concept approach, and the key value proposition
- Highlights emergent capabilities (things only possible through integration)
- Not a system design — an engineering-level concept

### 2. The Problem
- Current state description with operational realities
- Cost of stove-piped / current approach (quantified where possible)
- Root cause analysis — why is this the situation?
- Scaling / complexity analysis showing why incremental fixes don't work

### 3. The Concept
- From current state to proposed architectural approach
- Core insight / architectural principle
- Functional block diagram (ASCII)
- Block descriptions and responsibilities
- Block relationships and data flows
- Key principles governing the architecture

### 4. Enabled Capabilities
- **Direct Capabilities** — What individual blocks provide
- **Emergent Capabilities** — What integration enables that can't exist in isolation
- For each capability:
  - What it does
  - Why it matters (reference to problem)
  - Which blocks contribute
  - Example scenario

### 5. Concept of Operations
- Representative operational scenarios
- Step-by-step walkthrough of how the concept functions
- Comparison: today's workflow vs. concept workflow
- Human roles in the concept (what operators do vs. what's automated)

### 6. Maturation Path
- Phased implementation approach
- Phase 1: Foundation (what to build first)
- Phase 2: Integration (what connects next)
- Phase 3: Advanced capabilities (what becomes possible)
- Risk-reduction strategy
- Decision points and off-ramps

### 7. Glossary
- Domain-specific terms defined
- Acronyms expanded

### Appendices
- A: Solution Landscape Summary (reference to separate document)
- B: Research Sources (bibliography from source_tracker)
- C: Assumptions Register (from assumption_tracker)

## Formatting Conventions

- Use ASCII diagrams (not images) for portability
- Section headers use ## and ###
- Tables for structured comparisons
- Block quotes for key principles or callouts
- Source citations inline: `(Source: [name], [section]; Confidence: [level])`

## Tone

- Engineering-level: precise but accessible
- Problem-first: every section traces back to the problem
- Honest about unknowns: gaps flagged, not papered over
- Solution-agnostic through Section 4; implementation approaches only in Section 6 maturation path and the separate Solution Landscape
