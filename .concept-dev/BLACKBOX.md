# Black-Box Architecture — Requirements Development Plugin (requirements-dev)

**Session:** 1f45143f
**Date:** 2026-02-20
**Phase:** Black-Box Architecture (Phase 3)
**Selected Approach:** Block-Centric with Type Guided Passes + Cross-Cutting Sweep + Re-entrant Core

---

## Concept Overview

The requirements-dev plugin is organized around the functional blocks that users already know from concept-dev's BLACKBOX.md. Rather than processing all requirements in a single linear pass or developing each requirement in isolation, the plugin walks users through requirements one architectural block at a time, with guided type passes (functional → performance → interface/API → constraint → quality) within each block. Every requirement is quality-checked and V&V-planned inline before registration.

The distinguishing insight is the **re-entrant core**: the same requirements development pipeline (type-guided passes, quality checking, V&V planning, traceability) operates identically at system and subsystem levels. Subsystem decomposition is a separate analytical step that creates new blocks; those blocks then re-enter the same pipeline. This means the quality framework scales to any depth without switching tools or processes.

After all blocks complete at any level, a cross-cutting sweep validates the full requirement set for system-level concerns (security, reliability, data consistency) and checks INCOSE set characteristics C10-C15 (completeness, consistency, feasibility, comprehensibility, able to be validated, correctness). A skeptic review runs during this sweep to catch unverified claims about coverage or completeness.

---

## Functional Block Diagram

```
                         ┌──────────────────┐
                         │ Concept Ingestion │
                         │  (reads .concept- │
                         │   dev/ artifacts) │
                         └────────┬─────────┘
                                  │ block-organized
                                  │ needs candidates
                         ┌────────▼─────────┐
                         │Needs Formalization│
                         │ (per-block needs  │
                         │  extraction & user│
                         │  review)          │
                         └────────┬─────────┘
                                  │ approved needs per block
                                  │
       ┌──────────────────────────▼──────────────────────────┐
       │          REQUIREMENTS DEVELOPMENT CORE              │
       │  (re-entrant: runs at system or subsystem level)    │
       │                                                     │
       │  ┌───────────────────────────────────────────┐      │
       │  │     Block Requirements Engine             │      │
       │  │  For each block:                          │      │
       │  │   functional → performance →              │◄─┐   │
       │  │   interface/API → constraint → quality    │  │   │
       │  └──────────┬────────────────────────────────┘  │   │
       │             │ per requirement                    │   │
       │  ┌──────────▼──────────┐  ┌──────────────────┐  │   │
       │  │  Quality Checker    │  │  TPM Researcher   │  │   │
       │  │  (inline per req +  │  │  (baselines,      │──┘   │
       │  │   per block set)    │  │   benchmarks,     │      │
       │  └──────────┬──────────┘  │   sources)        │      │
       │             │             └──────────────────┘       │
       │  ┌──────────▼──────────┐                             │
       │  │  V&V Planner        │                             │
       │  │  (method, criteria, │                             │
       │  │   responsible party)│                             │
       │  └──────────┬──────────┘                             │
       │             │                                        │
       │  ┌──────────▼──────────┐                             │
       │  │  Traceability Engine│                             │
       │  │  (bidirectional     │                             │
       │  │   links, registries)│                             │
       │  └──────────┬──────────┘                             │
       │             │                                        │
       │  ┌──────────▼──────────┐                             │
       │  │  Set Validator      │  after each block           │
       │  │  (cross-block,      │◄── gaps feed back           │
       │  │   interface coverage│    to Block Engine           │
       │  └──────────┬──────────┘                             │
       │             │                                        │
       └─────────────┼────────────────────────────────────────┘
                     │ all blocks at current level complete
       ┌─────────────▼──────────┐
       │  Cross-Cutting Sweep   │
       │  (system-level reqs,   │
       │   security, reliability│
       │   full-set C10-C15,    │
       │   skeptic review)      │
       └─────────────┬──────────┘
                     │
       ┌─────────────▼──────────┐
       │  Deliverable Assembly  │
       │  (spec document,       │
       │   traceability matrix, │
       │   JSON registries)     │
       └─────────────┬──────────┘
                     │ optional
       ┌─────────────▼──────────┐
       │ Subsystem Decomposer   │
       │  (functional decomp,   │
       │   allocation rationale,│
       │   sub-block definition,│
       │   gate checks)         │
       └─────────────┬──────────┘
                     │ sub-blocks become new
                     │ "blocks" input
                     │
                     └──────────▶ Re-enter REQUIREMENTS
                                  DEVELOPMENT CORE at
                                  subsystem level
```

---

## Functional Blocks

### Concept Ingestion

**Responsibility:** Reads concept-dev artifacts from `.concept-dev/` and extracts structured data organized by functional block for downstream processing.

**Inputs:**
- CONCEPT-DOCUMENT.md (stakeholder needs, capabilities, problem context)
- BLACKBOX.md (functional blocks, relationships, principles, ConOps)
- SOLUTION-LANDSCAPE.md (researched approaches, gaps, sources)
- PROBLEM-STATEMENT.md (scope, constraints, success criteria)
- source_registry.json (registered sources with confidence levels)
- assumption_registry.json (tracked assumptions with status)

**Outputs:**
- Needs candidates organized by functional block
- Block metadata (responsibilities, inputs, outputs, relationships)
- Available sources and assumptions for traceability linking
- Session context (project name, scope, constraints)

**Key Behaviors:**
- Validates concept-dev artifacts exist and gates have passed
- Extracts needs candidates from capabilities, ConOps scenarios, and block behaviors
- Preserves source and assumption IDs for traceability linking
- Reports extraction summary (N blocks found, N needs candidates, N sources available)

---

### Needs Formalization

**Responsibility:** Transforms extracted needs candidates into INCOSE-compliant need statements with user review and approval per need.

**Inputs:**
- Needs candidates organized by block (from Concept Ingestion)
- INCOSE need statement patterns (from GtWR v4)

**Outputs:**
- Approved need statements with unique IDs (NEED-xxx)
- Need-to-source traceability links
- Deferred/out-of-scope needs with rationale

**Key Behaviors:**
- Presents needs candidates per block for user review
- Applies INCOSE need statement patterns (R1 structured statements)
- Seeds need wording from concept artifacts; user refines
- Validates each need is solution-free (describes expectation, not implementation)
- Registers approved needs in needs_registry.json
- Gate: user approves the integrated set of needs before proceeding

---

### Block Requirements Engine

**Responsibility:** For each block, guides the user through requirement types in order (functional → performance → interface/API → constraint → quality), seeding draft requirements from approved needs and block context.

**Inputs:**
- Approved needs for the current block
- Block metadata (responsibilities, inputs, outputs, relationships)
- SOLUTION-LANDSCAPE.md context (for technology-informed constraints)
- INCOSE requirement patterns and attribute definitions

**Outputs:**
- Draft requirements for quality checking
- Requirement type classification
- Attribute values for 13 mandatory INCOSE attributes

**Key Behaviors:**
- Guides user through one requirement type at a time per block
- Seeds draft requirement statements from needs + block context
- Prompts user for each mandatory attribute (rationale, priority, risk, etc.)
- Triggers TPM Researcher for measurable requirements
- Maintains focus: one type at a time, one block at a time
- Tracks TBD/TBR items for unresolved values

---

### Quality Checker

**Responsibility:** Applies INCOSE GtWR v4 rules against each requirement statement, both inline (per requirement) and at set level (per block completion).

**Inputs:**
- Draft requirement statement and attributes
- INCOSE GtWR v4 rules (R1-R42)
- Requirement set for the current block (at set-level checkpoints)

**Outputs:**
- Per-requirement quality report (rule violations with specific rule IDs)
- Suggested rewrites for flagged violations
- Set-level consistency/completeness assessment

**Key Behaviors:**
- Automated syntactic checks (~24 rules): vague terms (R7), escape clauses (R8), combinators (R19), passive voice (R2), missing articles (R5), open-ended clauses (R9), superfluous infinitives (R10), pronouns (R24), absolutes (R26), etc.
- LLM-assisted semantic checks (remaining rules): solution-free (R31), completeness (R4/C4), correctness (C8), appropriate level (C2) — flagged for human review with explicit confidence note
- Requires user to resolve flagged violations before registration
- At block completion: checks set characteristics C10-C15 within the block

---

### TPM Researcher

**Responsibility:** Researches grounded baselines for performance and measurable requirements using tiered research tools. Presents comparable benchmarks with sources so users can make informed value selections.

**Inputs:**
- Requirement context (what is being measured, for which block)
- Available research tools (WebSearch, WebFetch, crawl4ai, MCP tiers)
- Domain context from SOLUTION-LANDSCAPE.md

**Outputs:**
- Comparable benchmarks table (system, metric, value, source)
- Grounded baseline recommendation with confidence level
- Consequence/effect descriptions (what happens at different values)
- Registered sources in source_registry.json

**Key Behaviors:**
- Triggered when Block Requirements Engine encounters a measurable requirement
- Searches for comparable systems and published benchmarks
- Presents results as a table with sources, not as prescriptive recommendations
- Includes consequence descriptions (e.g., "Below 100ms p99: imperceptible; 100-500ms: noticeable; >500ms: frustrating")
- Registers all research sources with confidence levels
- User makes the final value selection

---

### V&V Planner

**Responsibility:** Attaches verification method, success criteria, and responsible party to each requirement (INCOSE attributes A6-A9).

**Inputs:**
- Quality-checked requirement statement and attributes
- Requirement type (functional, performance, interface, constraint, quality)
- Software V&V methods (unit test, integration test, system test, code review, static analysis, demonstration, analysis)

**Outputs:**
- V&V attributes per requirement (method, success criteria, responsible party)
- Verification strategy notes

**Key Behaviors:**
- Suggests appropriate V&V method based on requirement type (e.g., performance → load test; interface → integration test)
- Prompts user to define success criteria (what does "pass" look like?)
- Records responsible party (who verifies this?)
- Ensures every registered requirement has V&V attributes populated

---

### Traceability Engine

**Responsibility:** Maintains bidirectional traceability links throughout the requirements lifecycle and produces machine-readable JSON registries.

**Inputs:**
- Registered requirements with all attributes
- Need-to-requirement links
- Requirement-to-V&V links
- Concept-dev source_registry.json and assumption_registry.json references

**Outputs:**
- requirements_registry.json (structured requirement objects with all attributes and links)
- needs_registry.json (formalized needs with traceability)
- Traceability matrix (needs ↔ requirements ↔ V&V)
- Cross-references to concept-dev registries

**Key Behaviors:**
- Assigns unique IDs to all entities (NEED-xxx, REQ-xxx)
- Maintains parent traces (A2), source traces (A3), and V&V links (A6-A9)
- Validates referential integrity (no dangling links)
- Supports querying: "which requirements trace to NEED-003?" or "which needs have no requirements?"
- Atomic writes (temp-file-then-rename) for crash safety

---

### Set Validator

**Responsibility:** After each block completes, validates cross-block consistency, interface coverage, and set-level quality characteristics.

**Inputs:**
- All registered requirements for completed blocks
- Block relationship data from BLACKBOX.md
- INCOSE set characteristics C10-C15

**Outputs:**
- Validation report (gaps, overlaps, inconsistencies)
- Interface coverage assessment (are all block-to-block flows covered?)
- Feedback items for Block Requirements Engine (gaps to address)

**Key Behaviors:**
- Checks that every block-to-block relationship from BLACKBOX.md has at least one interface requirement
- Identifies duplicate or overlapping requirements across blocks
- Checks consistent terminology and units across the set (C11)
- Reports uncovered needs (needs without requirements)
- Feeds gaps back to Block Requirements Engine for resolution

---

### Cross-Cutting Sweep

**Responsibility:** After all blocks at the current level are complete, validates the full requirement set for system-level concerns and runs a skeptic review.

**Inputs:**
- Complete requirement set across all blocks
- INCOSE set characteristics C10-C15
- Skeptic review criteria

**Outputs:**
- System-level requirements added (security, reliability, data consistency, etc.)
- Full-set validation report
- Skeptic findings (verified/unverified/disputed claims about coverage)

**Key Behaviors:**
- Prompts for cross-cutting requirement categories: security, reliability, availability, scalability, maintainability, data integrity, logging/observability
- Checks full-set completeness (C10): are all problem statement success criteria addressed?
- Checks full-set consistency (C11): terminology, units, no conflicts
- Checks full-set feasibility (C12): collectively achievable?
- Runs skeptic agent to verify claims about coverage and completeness
- User approves system-level additions and resolves skeptic findings

---

### Deliverable Assembly

**Responsibility:** Produces the final deliverable artifacts from the registered requirement set and traceability data.

**Inputs:**
- requirements_registry.json (complete requirement set)
- needs_registry.json (formalized needs)
- Traceability links
- V&V data
- Source and assumption registries

**Outputs:**
- REQUIREMENTS-SPECIFICATION.md (structured document per INCOSE R42)
- TRACEABILITY-MATRIX.md (needs ↔ requirements ↔ V&V)
- VERIFICATION-MATRIX.md (requirements × V&V method × success criteria)
- JSON registries (machine-readable for downstream tools)

**Key Behaviors:**
- Generates specification document organized by block, then by requirement type
- Produces traceability matrix showing full chain: concept-dev source → need → requirement → V&V
- Produces verification matrix for test planning
- Includes quality summary (rules checked, violations resolved)
- Includes assumption and source appendices
- User approves each deliverable before finalization

---

### Subsystem Decomposer

**Responsibility:** Decomposes system-level blocks into sub-blocks with allocation rationale, creating the input for a re-entrant pass through the Requirements Development Core.

**Inputs:**
- Baselined system-level requirements per block
- Block metadata from BLACKBOX.md
- User's engineering judgment (guided by prompts)

**Outputs:**
- Sub-block definitions (name, responsibility, inputs, outputs)
- Allocation rationale (which parent requirements allocate to which sub-blocks)
- Sub-block relationship diagram
- Gate approval for decomposition

**Key Behaviors:**
- Guides user through functional decomposition per block
- Prompts for allocation rationale: "Which parent requirements does this sub-block address?"
- Creates parent-to-child requirement traces (INCOSE A2)
- Validates allocation coverage: every parent requirement allocated to at least one sub-block
- Gate check: user approves decomposition before re-entering the core pipeline
- Sub-blocks feed back into the Requirements Development Core at subsystem level

---

## Block Relationships

| From | To | Relationship | What Flows |
|------|----|-------------|------------|
| Concept Ingestion | Needs Formalization | provides | Block-organized needs candidates, source/assumption IDs |
| Needs Formalization | Block Requirements Engine | provides | Approved needs per block with unique IDs |
| Block Requirements Engine | Quality Checker | triggers | Draft requirement for inline checking |
| Block Requirements Engine | TPM Researcher | triggers | Baseline research request for measurable requirements |
| TPM Researcher | Block Requirements Engine | returns | Benchmarks table, baseline recommendations, sources |
| Quality Checker | V&V Planner | passes | Quality-checked requirement |
| V&V Planner | Traceability Engine | registers | Complete requirement expression with all attributes |
| Traceability Engine | Set Validator | provides | Registered requirements for cross-block validation |
| Set Validator | Block Requirements Engine | feeds back | Gaps, missing interface requirements, inconsistencies |
| Set Validator | Cross-Cutting Sweep | triggers | When all blocks complete at current level |
| Cross-Cutting Sweep | Traceability Engine | registers | System-level cross-cutting requirements |
| Traceability Engine | Deliverable Assembly | provides | Complete traced requirement set |
| Deliverable Assembly | Subsystem Decomposer | provides | Baselined system requirements (optional) |
| Subsystem Decomposer | Block Requirements Engine | re-enters | Sub-blocks as new "blocks" at subsystem level |

---

## Architectural Principles

1. **Block-centric organization** — Functional blocks from concept-dev's BLACKBOX.md are the primary organizing structure. Users work through requirements one block at a time, maintaining the mental model they already built.

2. **Type-guided passes within blocks** — Within each block, the user is guided through requirement types in deliberate order: functional → performance → interface/API → constraint → quality. This keeps requirements singular (INCOSE R18) and focused.

3. **Inline quality and V&V** — Every requirement is quality-checked and V&V-planned before registration. No requirement exists in a "draft-only" state. This prevents late-stage rework.

4. **Research-on-demand** — TPM research is triggered when writing measurable requirements, not as a separate stage. Baselines and benchmarks arrive in context, when the user is making the value decision.

5. **Progressive validation** — Set validation at three levels: per-requirement (inline quality), per-block (interface coverage, consistency), and full-set (cross-cutting sweep). Issues caught at the earliest possible level.

6. **Traceability from birth** — Every requirement is linked to its parent need, source block, and V&V method at creation time. Traceability is not a post-hoc activity.

7. **Solution-free needs; solution-informed requirements** — Need statements remain solution-free. Design input requirements may reference technology constraints from SOLUTION-LANDSCAPE.md but do not prescribe design.

8. **Re-entrant core** — The requirements development pipeline operates identically at system and subsystem levels. Subsystem decomposition creates new blocks; the same core processes them.

9. **Skeptic verification at boundaries** — Skeptic reviews at block completion and during the cross-cutting sweep, verifying claims about completeness, feasibility, and coverage.

---

## Enabled Capabilities

### Direct Capabilities

1. **Structured needs extraction** — Concept-dev artifacts are systematically mined for stakeholder needs, organized by functional block. No needs lost in translation. (Concept Ingestion + Needs Formalization)

2. **Type-guided requirement writing** — Users walked through each requirement type in deliberate order, preventing neglect of performance, interface, constraint, and quality requirements. (Block Requirements Engine)

3. **Inline quality assurance** — Every requirement checked against INCOSE GtWR rules before registration. ~24 syntactic rules automated; semantic concerns flagged for human review. (Quality Checker)

4. **V&V from birth** — Every requirement has verification method, success criteria, and responsible party at creation time. Test planning is proactive. (V&V Planner)

5. **Research-grounded performance targets** — Comparable benchmarks, grounded baselines with sources, and consequence descriptions for informed value selection. (TPM Researcher)

6. **Full traceability** — Bidirectional links from stakeholder needs through requirements to V&V methods in machine-readable JSON registries. (Traceability Engine)

7. **Rigorous subsystem decomposition** — Blocks decomposed into sub-blocks with allocation rationale; same pipeline re-enters at subsystem level. (Subsystem Decomposer)

### Emergent Capabilities

8. **Cross-cutting integrity** — Per-block Set Validator + full-set Cross-Cutting Sweep catches requirements spanning blocks and validates complete set against INCOSE C10-C15. (Set Validator + Cross-Cutting Sweep)

9. **Pipeline continuity** — Full chain from concept-dev ideation through requirements-dev to system-design has formal traceability. No rigor lost at phase boundaries. (Concept Ingestion + Traceability Engine + Deliverable Assembly)

10. **Re-entrant depth** — Same quality-checked, V&V-planned, traced process at any abstraction level. Teams go as deep as projects demand without switching tools. (Re-entrant Core + Subsystem Decomposer)

11. **Informed solution evaluation** — Explicit, verifiable requirements enable systematic evaluation of solution alternatives from SOLUTION-LANDSCAPE against concrete criteria. (Traceability Engine + Deliverable Assembly)

12. **Session resilience** — Per-requirement state persistence means work is never lost. Resume mid-block days later at the same point with same context. (Traceability Engine + state management)

---

## Concept of Operations

### Scenario 1: Solo Developer — Full Pipeline from Concept-Dev

Alex completed concept-dev for a task management API with 4 functional blocks (Task Engine, Dependency Tracker, Notification Hub, API Gateway).

1. **Init** — Alex runs `/reqdev:init`. Concept Ingestion reads `.concept-dev/`, reports: 4 blocks, 12 needs candidates, 6 sources, 3 assumptions.
2. **Needs** — Alex runs `/reqdev:needs`. Needs Formalization walks through each block, presenting candidates. Alex refines wording, approves 10 needs, defers 2 as out-of-scope. Gate passed.
3. **Requirements (Block 1)** — Alex runs `/reqdev:requirements`. Block Requirements Engine starts with Task Engine, functional requirements first. Seeds draft: "The Task Engine shall create, update, and delete tasks with unique identifiers." Quality Checker flags R7 (vague "update"). Alex rewrites. V&V Planner asks for method. Alex picks test, defines criteria. Registered with 13 attributes.
4. **Performance research** — Moving to performance requirements, TPM Researcher fires. Finds benchmarks: "Comparable APIs: 500-2000 concurrent users, p99 < 200ms." Alex sets targets informed by research. Source registered.
5. **Block validation** — After Block 1, Set Validator checks interface coverage against Block 2. Flags: "No interface requirement for Task Engine → Dependency Tracker." Alex writes the interface requirement.
6. **All blocks** — Process repeats for all 4 blocks.
7. **Cross-cutting** — Cross-Cutting Sweep runs. Skeptic reviews. Flags: "No security requirements across any block." Alex adds system-level security requirements.
8. **Deliver** — Alex runs `/reqdev:deliver`. Specification document, traceability matrix, verification matrix, and JSON registries produced. 47 requirements, all quality-checked, V&V-planned, traced.
9. **Decompose (optional)** — Alex decomposes Block 2 (Dependency Tracker) into 3 sub-blocks. Re-enters the core pipeline at subsystem level.

### Scenario 2: Small Team — Resuming Across Sessions

A 3-person team building a data pipeline platform completed concept-dev last week.

1. **Session 1** — Sarah runs `/reqdev:init`, works through needs formalization and Blocks 1-2. Stops mid-Block 3.
2. **Session 2 (2 days later)** — Marcus runs `/reqdev:resume`. Shows: "15 needs approved. 23 requirements registered (Blocks 1-2 complete, Block 3: 2/5 types done). Resuming at Block 3, interface/API requirements." Marcus finishes Blocks 3-4.
3. **Session 3** — Sarah runs Cross-Cutting Sweep, reviews skeptic findings with team, collectively approves deliverables.

---

## Alternative Approaches Considered

| Approach | Core Idea | Why Not Selected |
|----------|-----------|-----------------|
| Linear Pipeline | Sequential stages: all needs → all requirements → all quality → all V&V → deliverables | Quality issues discovered late; no feedback loop; V&V deferred from writing context |
| Integrated Per-Requirement Loop | Each requirement fully developed in single pass (need → req → quality → V&V) | More complex flow; switching between types within a block feels less structured; set-level issues only at checkpoints |

---

## Assumptions

| ID | Assumption | Category | Impact if Wrong |
|----|-----------|----------|-----------------|
| A-001 | LLM-based INCOSE rule checking can reliably automate ~24 of 42 syntactic rules | feasibility | Quality checking would need to be fully manual |
| A-002 | Concept-dev outputs provide sufficient starting material to seed needs and requirements | feasibility | Would need additional elicitation phases |
| A-003 | Subsystem decomposition can be scaffolded by LLM with guided prompts | feasibility | Under-scaffolding would leave users without guidance |
| A-004 | Software-only focus compatible with INCOSE practices | feasibility | Would need custom adaptation |
| A-005 | Solo developers will accept INCOSE rigor if guided and conversational | stakeholder | Process may be too heavyweight |
| A-008 | Block-centric organization maps naturally to concept-dev's BLACKBOX.md structure | architecture | Would need alternative organizing principle |
| A-009 | Type-guided passes produce more complete requirements than freeform writing | architecture | Rigid ordering may constrain experienced users |
| A-010 | Re-entrant core can operate at multiple abstraction levels without modification | architecture | May need level-specific adaptations for subsystem requirements |

---

## Open Questions

1. How should cross-cutting requirements (security, reliability) that don't belong to a single block be tracked in the block-centric structure? (Cross-Cutting Sweep)
2. Should the type order (functional → performance → interface → constraint → quality) be configurable, or is the fixed order essential for quality? (Block Requirements Engine)
3. What is the minimum viable set of cross-cutting categories to prompt for during the sweep? (Cross-Cutting Sweep)
4. How should TBD/TBR items be tracked when they span blocks? (Traceability Engine)
5. At what point does the Set Validator interrupt the user vs. queue findings for block completion? (Set Validator)

---

**Next Phase:** Drill-Down & Gap Analysis (`/concept:drilldown`)
