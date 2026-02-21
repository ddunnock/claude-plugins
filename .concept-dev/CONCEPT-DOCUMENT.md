# Requirements Development Plugin (requirements-dev)
## An Engineering Concept for AI-Assisted INCOSE Requirements Development

**Version:** 1.0
**Date:** 2026-02-20
**Session:** 1f45143f

---

## Executive Summary

Solo developers and small teams who complete concept development lack a structured, AI-assisted path to transform their concept artifacts into formal requirements. They either jump directly to implementation — treating concept documents as informal guides — or rely on spec-driven AI tools that conflate specifications with requirements, bypassing the formal needs-to-requirements transformation that INCOSE identifies as foundational to systems engineering. The result: solution decisions made without explicit evaluation criteria, missed stakeholder needs discovered late, and no traceability from needs through to validation methods.

The **requirements-dev** plugin addresses this gap by introducing an AI-assisted requirements development process calibrated for software-focused projects. Organized around the functional blocks users already know from concept-dev's architecture, the plugin walks users through requirement types in deliberate order — functional, performance, interface/API, constraint, quality — with inline quality checking against INCOSE GtWR v4 rules and verification planning at creation time, not as afterthoughts. Every requirement is traced bidirectionally: up to a stakeholder need and forward to a verification method, all stored in machine-readable JSON registries.

The concept's distinguishing capability is its **re-entrant core**: the same quality-checked, V&V-planned, traced requirements pipeline operates identically at system and subsystem levels. When blocks need decomposition, sub-blocks re-enter the same pipeline — no tool switching, no quality degradation at depth. Combined with research-grounded performance targets, a cross-cutting sweep for system-level concerns, and a skeptic agent that verifies claims about completeness and coverage, requirements-dev bridges the gap between concept development and system design with the same rigor that concept-dev brings to ideation and problem definition. This is an engineering concept, not a system design — it defines what the plugin must do at a functional level while leaving implementation decisions to the downstream planning phase.

---

## 1. The Problem

### How Things Work Today

After completing concept development — whether through the concept-dev plugin or an equivalent process — a solo developer or small team has a well-researched concept document, a functional architecture with defined blocks and relationships, a solution landscape mapping approaches per domain, and JSON registries tracking 100+ sources and assumptions. This represents significant analytical investment: problem definition, stakeholder identification, feasibility research, skeptic-verified claims, and structured gap analysis.

Then the process breaks. No structured follow-on exists to transform these artifacts into formal requirements. Teams take one of four paths:

**Jump to implementation.** The concept document becomes an informal reference. Requirements are implicit — embedded in code, user stories, and pull request descriptions. When a design decision is questioned, there's no requirement to evaluate it against. When a feature is cut, there's no traceability to know which stakeholder need is now unmet.

**Use spec-driven AI tools.** Tools like GSD and spec-kit generate specifications that define *what to build* — file structures, API endpoints, data models. These are solutions, not requirements. They skip the formal needs-to-requirements transformation entirely, conflating "how the system is built" with "what the system must do." The result is a specification that can't be verified against stakeholder needs because the needs were never formally captured.

**Write ad-hoc requirements lists.** Some teams produce informal requirement lists — bullet points in a wiki or markdown file. These lack structured attributes, traceability to needs, quality checking against standards, and verification planning. They look like requirements but can't function as them.

**Defer V&V planning.** Across all approaches, verification and validation strategy is deferred until testing. Requirements written without "how will we verify this?" produce untestable requirements discovered only when someone tries to write the test.

### The Cost of the Current Approach

**Sub-optimal solution selection.** Without explicit, verifiable requirements, solutions are chosen based on intuition and habit rather than evaluated against concrete criteria. The solution landscape from concept-dev — with its researched approaches and trade-off dimensions — has no formal requirements to evaluate against. The investment in structured concept development doesn't carry forward into structured decision-making.

**Lost rigor at the phase boundary.** Concept-dev produces source-grounded research, skeptic-verified claims, and tracked assumptions. When teams jump to implementation or spec-driven tools, this chain of evidence breaks. There's no traceability from the 108 sources researched during concept development through to the design decisions made during implementation.

**Reactive test planning.** V&V criteria defined after code is written are constrained by what's testable in the existing implementation, rather than what should be verifiable based on the requirement. Performance targets are set without research — arbitrary numbers rather than grounded baselines informed by comparable benchmarks and published data.

**Scope creep without detection.** Without formal scope boundaries defined by requirements traced to needs, feature additions go unchecked. There's no mechanism to ask "which stakeholder need does this feature serve?" or "does this addition conflict with an existing requirement?"

### The Root Cause

The root cause is not a lack of standards — INCOSE's Guide for Writing Requirements (GtWR v4) provides 42 rules, 15 set characteristics, and 49 requirement attributes that define what good requirements look like. The root cause is accessibility. These practices require dedicated systems engineering support that solo developers and small teams don't have. The INCOSE practices exist; the guided, AI-assisted process to make them practical for small teams does not.

Incremental fixes — better user story templates, improved spec generators, requirement checklists — don't address this structural gap. They either operate at the wrong abstraction level (solutions vs. requirements) or provide the form without the substance (checklists without quality checking, templates without traceability). What's needed is a process that understands the difference between a need and a requirement, checks quality against specific rules, plans verification at creation time, and maintains traceability throughout — all guided conversationally so that SE expertise is embedded in the process, not required of the user.

---

## 2. The Concept

### From Ad-Hoc Requirements to Block-Centric, Quality-Checked Requirements Development

Requirements-dev replaces the unstructured jump from concept to implementation with a guided, block-by-block requirements development process. Instead of writing requirements in isolation or generating specifications that prescribe solutions, the plugin walks users through each functional block from their concept architecture, developing requirements by type — functional, performance, interface/API, constraint, quality — with every requirement quality-checked against INCOSE rules and paired with a verification plan before it's registered.

The key architectural insight is that the requirements development pipeline is **re-entrant**: the same process — type-guided passes, inline quality checking, V&V planning, traceability registration — operates identically whether developing system-level requirements or subsystem-level requirements after decomposition. Depth scales without tool switching or quality degradation.

### Functional Architecture

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
                     └──────────▶ Re-enter REQUIREMENTS
                                  DEVELOPMENT CORE at
                                  subsystem level
```

### Functional Blocks

**Concept Ingestion** — Reads `.concept-dev/` artifacts and extracts structured data organized by functional block.
Validates that concept-dev phases are complete, extracts needs candidates from capabilities, ConOps scenarios, and block behaviors, and preserves source and assumption IDs for traceability linking. Reports an extraction summary so users know exactly what starting material is available.

**Needs Formalization** — Transforms extracted needs candidates into INCOSE-compliant need statements with user review.
Applies INCOSE need statement patterns ([Stakeholder] needs [capability] [qualifier]), validates each need is solution-free, and registers approved needs in a structured JSON registry. Users review and approve the complete needs set per block before proceeding — needs are expectations ("should"), not obligations.

**Block Requirements Engine** — Guides users through requirement types in deliberate order within each block.
For each block, walks through functional → performance → interface/API → constraint → quality requirements. Seeds draft statements from approved needs and block context, prompts for 13 mandatory INCOSE attributes, triggers TPM Researcher for measurable requirements, and tracks TBD/TBR items with NASA-style four-field closure tracking (estimate, resolution path, owner, deadline).

**Quality Checker** — Applies INCOSE GtWR v4 rules inline per requirement and at set level per block.
Automated syntactic checks for ~24 deterministic rules (vague terms, escape clauses, passive voice, combinators, pronouns, absolutes). LLM-assisted semantic checks for remaining rules (solution-free, completeness, appropriate level) flagged for human review with explicit confidence notes. Requires violation resolution before registration.

**TPM Researcher** — Researches grounded baselines for performance and measurable requirements.
Triggered when the Block Requirements Engine encounters a measurable requirement. Searches for comparable systems and published benchmarks using tiered research tools, presents results as a structured table with sources, and includes consequence/effect descriptions at different value ranges. Users make the final value selection informed by research, not arbitrary guesses.

**V&V Planner** — Attaches verification method, success criteria, and responsible party to each requirement.
Populates INCOSE attributes A6-A9. Suggests appropriate V&V methods based on requirement type (performance → load test; interface → integration test; functional → unit/system test). Every registered requirement has V&V attributes populated — verification planning is proactive, not deferred.

**Traceability Engine** — Maintains bidirectional traceability links and machine-readable JSON registries.
Assigns unique IDs (NEED-xxx, REQ-xxx), maintains parent traces, source traces, and V&V links, validates referential integrity, and supports queries ("which requirements trace to NEED-003?"). Uses atomic writes (temp-file-then-rename) for crash safety, following the proven concept-dev pattern.

**Set Validator** — After each block completes, validates cross-block consistency and interface coverage.
Checks that every block-to-block relationship from the architecture has at least one interface requirement, identifies duplicates and overlaps, checks terminology consistency, and reports uncovered needs. Feeds gaps back to the Block Requirements Engine for resolution.

**Cross-Cutting Sweep** — After all blocks complete, validates the full set for system-level concerns.
Prompts for cross-cutting categories (security, reliability, availability, scalability, maintainability, data integrity, logging/observability). Checks full-set INCOSE characteristics C10-C15 (completeness, consistency, feasibility, comprehensibility, validatability, correctness). Runs skeptic review to verify claims about coverage.

**Deliverable Assembly** — Produces final deliverable artifacts from the registered requirement set.
Generates REQUIREMENTS-SPECIFICATION.md (organized by block then by type), TRACEABILITY-MATRIX.md (concept-dev source → need → requirement → V&V), VERIFICATION-MATRIX.md (requirements × method × criteria), and JSON registries for machine consumption by downstream tools. Each deliverable approved by the user before finalization.

**Subsystem Decomposer** — Decomposes system-level blocks into sub-blocks for re-entrant processing.
Guides functional decomposition per block, prompts for allocation rationale ("which parent requirements does this sub-block address?"), validates allocation coverage, and creates parent-to-child traces. Sub-blocks re-enter the Requirements Development Core at subsystem level — same pipeline, deeper abstraction.

### Architectural Principles

1. **Block-centric organization** — Functional blocks from concept-dev's architecture are the primary organizing structure. Users work through requirements one block at a time, maintaining the mental model they built during concept development.

2. **Type-guided passes within blocks** — Within each block, users are guided through requirement types in deliberate order. This keeps requirements singular and focused, preventing the common failure of conflating functional and performance concerns in a single statement.

3. **Inline quality and V&V** — Every requirement is quality-checked and V&V-planned before registration. No requirement exists in a "draft-only" state. This prevents the late-stage rework that occurs when quality checking is deferred.

4. **Research-on-demand** — TPM research is triggered when writing measurable requirements, not as a separate stage. Baselines and benchmarks arrive in context, when the user is making the value decision.

5. **Progressive validation** — Set validation at three levels: per-requirement (inline quality), per-block (interface coverage, consistency), and full-set (cross-cutting sweep). Issues caught at the earliest possible level.

6. **Traceability from birth** — Every requirement is linked to its parent need, source block, and V&V method at creation time. Traceability is not a post-hoc activity.

7. **Solution-free needs; solution-informed requirements** — Need statements remain solution-free (expectations). Design input requirements may reference technology constraints from the solution landscape but do not prescribe design.

8. **Re-entrant core** — The requirements development pipeline operates identically at system and subsystem levels. Subsystem decomposition creates new blocks; the same core processes them.

9. **Skeptic verification at boundaries** — Skeptic reviews at block completion and during the cross-cutting sweep, verifying claims about completeness, feasibility, and coverage against registered sources.

---

## 3. Enabled Capabilities

### Direct Capabilities

**Structured Needs Extraction**
Concept-dev artifacts are systematically mined for stakeholder needs, organized by the functional blocks users already defined during concept development. Needs candidates are extracted from capabilities, ConOps scenarios, and block behaviors — then formalized into INCOSE-compliant need statements with user review. No needs lost in translation between concept and requirements phases. (Concept Ingestion + Needs Formalization)

**Type-Guided Requirement Writing**
Users are walked through each requirement type in deliberate order within each block: functional, performance, interface/API, constraint, quality. This prevents the common failure of neglecting non-functional requirements — performance targets omitted, interface contracts undefined, quality characteristics unspecified. Each type pass focuses attention on a single concern, keeping requirements singular and verifiable. (Block Requirements Engine)

**Inline Quality Assurance**
Every requirement is checked against INCOSE GtWR v4 rules before registration. Approximately 24 syntactic rules are checked automatically — vague terms ("appropriate," "sufficient"), escape clauses ("if possible"), combinators ("and/or"), passive voice, pronouns, absolutes. Remaining semantic rules (solution-free, completeness, appropriate abstraction level) are LLM-assisted with explicit confidence notes, flagged for human review. Users resolve flagged violations with suggested rewrites before a requirement is registered. (Quality Checker)

**Verification Planning from Birth**
Every requirement has a verification method, success criteria, and responsible party assigned at creation time. V&V is not deferred to a testing phase — it's part of the requirement's definition. This means when the requirement states "the system shall respond within 200ms at p99," the verification plan already specifies: load test, threshold criterion, and who runs the test. (V&V Planner)

**Research-Grounded Performance Targets**
When a measurable requirement is encountered, the TPM Researcher searches for comparable systems and published benchmarks — Nielsen response time thresholds, Google Core Web Vitals, DORA deployment metrics, industry SLA tiers. Results are presented as a structured table with sources and consequence descriptions ("Below 100ms: imperceptible; 100-500ms: noticeable; >500ms: frustrating"). Users set targets informed by evidence, not arbitrary guesses. (TPM Researcher)

**Full Bidirectional Traceability**
Every entity has a unique ID (NEED-xxx, REQ-xxx) with bidirectional links: each requirement traces up to a stakeholder need and forward to a V&V method, stored in machine-readable JSON registries. Cross-references back to concept-dev's source and assumption registries maintain the full evidence chain. Query support enables questions like "which requirements trace to NEED-003?" and "which needs have no requirements?" (Traceability Engine)

**Rigorous Subsystem Decomposition**
When system-level requirements are baselined and a block needs deeper decomposition, the Subsystem Decomposer guides functional decomposition with allocation rationale. Every parent requirement is allocated to at least one sub-block with documented reasoning. Sub-blocks then re-enter the same requirements development pipeline at subsystem level. (Subsystem Decomposer)

### Emergent Capabilities

Capabilities that arise from the integration of functional blocks — things not possible when components operate in isolation:

**Cross-Cutting Integrity**
The combination of per-block Set Validator and full-set Cross-Cutting Sweep catches requirements that no single block owns. After all blocks complete, the sweep prompts for system-level concerns — security, reliability, availability, data integrity, observability — and validates the complete set against INCOSE characteristics C10-C15 (completeness, consistency, feasibility, comprehensibility, validatability, correctness). A skeptic review during the sweep verifies claims about coverage, catching false confidence about completeness. Neither the per-block validator nor the cross-cutting sweep achieves this alone; the layered validation catches issues at different granularities. (Set Validator + Cross-Cutting Sweep)

**Pipeline Continuity**
The full chain from concept-dev ideation through requirements-dev to system-design inputs has formal traceability. A source researched during concept-dev's drilldown phase (SRC-xxx) traces through to the need it informed (NEED-yyy), to the requirement derived from that need (REQ-zzz), to the verification method that will confirm it. No rigor is lost at phase boundaries — the JSON registries maintain referential integrity across workspaces. This means a disputed claim from concept-dev's skeptic review can be traced forward to see which requirements depend on it. (Concept Ingestion + Traceability Engine + Deliverable Assembly)

**Re-Entrant Depth**
The same quality-checked, V&V-planned, traced process operates at any abstraction level. When the Subsystem Decomposer creates sub-blocks, those blocks enter the identical pipeline — type-guided passes, inline quality checking, V&V planning, traceability registration, set validation. Teams go as deep as their project demands without switching tools or accepting reduced quality at lower levels. A subsystem requirement receives the same INCOSE rule checking as a system requirement. (Re-entrant Core + Subsystem Decomposer)

**Informed Solution Evaluation**
With explicit, verifiable requirements in place, solution alternatives from concept-dev's Solution Landscape can be systematically evaluated against concrete criteria. Instead of "which database feels right?", the question becomes "which database meets REQ-017 (p99 < 50ms for 10K concurrent reads) and REQ-023 (ACID compliance for financial transactions)?" The requirements provide the evaluation framework that makes the solution landscape actionable. (Traceability Engine + Deliverable Assembly)

**Session Resilience**
Per-requirement state persistence — with atomic writes and structured JSON registries — means work is never lost. A user can stop mid-block, resume days later, and pick up at exactly the same point: "15 needs approved. 23 requirements registered (Blocks 1-2 complete, Block 3: 2/5 types done). Resuming at Block 3, interface/API requirements." The Traceability Engine's persistent state makes this possible without context degradation. (Traceability Engine + state management)

---

## 4. Concept of Operations

### Scenario 1: Solo Developer — Full Pipeline from Concept-Dev

Alex completed concept-dev for a task management API. The concept architecture defines 4 functional blocks: Task Engine, Dependency Tracker, Notification Hub, and API Gateway. The concept document, solution landscape, and 42 registered sources are ready in `.concept-dev/`.

| Step | Action | Block(s) Involved |
|------|--------|-------------------|
| 1 | Alex runs `/reqdev:init`. Concept Ingestion reads `.concept-dev/`, validates all gates passed, and reports: 4 blocks found, 12 needs candidates extracted, 42 sources available for traceability linking. | Concept Ingestion |
| 2 | Alex runs `/reqdev:needs`. Needs Formalization walks through each block, presenting candidates extracted from capabilities and ConOps scenarios. For the Task Engine block: "The task management system should enable users to create, organize, and track tasks with dependencies." Alex refines wording, approves 10 needs, defers 2 as out-of-scope with documented rationale. Gate passed. | Needs Formalization |
| 3 | Alex runs `/reqdev:requirements`. Block Requirements Engine starts with Task Engine, functional requirements first. Seeds a draft: "The Task Engine shall create, update, and delete tasks with unique identifiers." Quality Checker flags R7 (vague term: "update" — what does update include?). Alex rewrites to "The Task Engine shall modify task title, description, status, and priority fields." Passes quality check. V&V Planner asks for verification method — Alex picks "system test" with criteria "all CRUD operations return correct state." Registered as REQ-001 with 13 attributes populated. | Block Requirements Engine, Quality Checker, V&V Planner, Traceability Engine |
| 4 | Moving to performance requirements for Task Engine. The Block Requirements Engine flags a measurable requirement. TPM Researcher fires, searches for comparable task API benchmarks. Finds: "Comparable APIs: Todoist handles 500K+ users; Asana p99 < 200ms; industry median for CRUD APIs: 50-150ms p99." Presents a consequence table: "Below 100ms: imperceptible; 100-200ms: acceptable; >500ms: user frustration." Alex sets target at 150ms p99, informed by the research. Source registered as SRC-043. | Block Requirements Engine, TPM Researcher |
| 5 | After completing all 5 type passes for Task Engine, Set Validator checks interface coverage against other blocks. Flags: "Block relationship Task Engine → Dependency Tracker has no interface requirement." Alex writes: "The Task Engine shall provide a dependency query interface returning all blocking and blocked tasks for a given task ID." Interface gap closed. | Set Validator, Block Requirements Engine |
| 6 | Process repeats for Dependency Tracker, Notification Hub, and API Gateway. Each block gets type-guided passes, inline quality checking, V&V planning, and set validation. | All core blocks |
| 7 | After all 4 blocks complete, Cross-Cutting Sweep runs. Prompts for system-level concerns. Alex realizes no security requirements exist across any block — no authentication, no authorization, no input validation. Adds 5 system-level security requirements through the standard pipeline (quality-checked, V&V-planned, traced). Skeptic review flags: "Claim that requirements cover all OWASP Top 10 is unverified — only 5 of 10 categories addressed." Alex acknowledges and adds 3 more requirements. | Cross-Cutting Sweep, Quality Checker, V&V Planner |
| 8 | Alex runs `/reqdev:deliver`. Deliverable Assembly generates: REQUIREMENTS-SPECIFICATION.md (organized by block, 47 requirements), TRACEABILITY-MATRIX.md (full chain from concept sources through needs to requirements to V&V), VERIFICATION-MATRIX.md (47 requirements × method × criteria), and JSON registries. Alex approves each deliverable section by section. | Deliverable Assembly |
| 9 | Alex decides to decompose the Dependency Tracker into 3 sub-blocks: Graph Engine, Cycle Detector, and Critical Path Calculator. Subsystem Decomposer guides the decomposition with allocation rationale. The 8 parent requirements for Dependency Tracker are allocated across sub-blocks. Sub-blocks re-enter the core pipeline — same type-guided passes, same quality checking, same V&V planning — producing 14 child requirements at subsystem level. | Subsystem Decomposer, Re-entrant Core |

### Scenario 2: Small Team — Resuming Across Sessions

A 3-person team building a data pipeline platform completed concept-dev last week. Their architecture has 6 functional blocks.

| Step | Action | Block(s) Involved |
|------|--------|-------------------|
| 1 | **Session 1 (Monday)** — Sarah runs `/reqdev:init`, works through needs formalization (18 needs approved), and completes requirements for Blocks 1-2 (Ingestion Engine, Transform Pipeline). 23 requirements registered. Stops mid-Block 3 after functional and performance types. | Concept Ingestion, Needs Formalization, Block Requirements Engine |
| 2 | **Session 2 (Wednesday)** — Marcus runs `/reqdev:resume`. Dashboard shows: "18 needs approved. 23 requirements registered. Blocks 1-2 complete. Block 3 (Schema Registry): 2/5 types done. Resuming at interface/API requirements." Marcus finishes Block 3 and completes Blocks 4-6. Total: 52 requirements. | Block Requirements Engine, Quality Checker, V&V Planner |
| 3 | **Session 3 (Friday)** — Sarah runs Cross-Cutting Sweep. Team reviews skeptic findings together: "Claim that performance requirements cover all critical paths is unverified — Block 5 has no p99 latency requirement." Team adds the missing requirement. Deliverables generated and approved collectively. | Cross-Cutting Sweep, Deliverable Assembly |

### Today vs. With Requirements-Dev

| Aspect | Today | With Requirements-Dev |
|--------|-------|----------------------|
| Needs extraction | Implicit; lost in translation from concept to code | Systematic extraction from concept artifacts, formalized per INCOSE patterns |
| Requirement writing | Ad-hoc lists, informal language, no attribute structure | Type-guided passes with 13 mandatory attributes per requirement |
| Quality checking | None, or informal peer review | Inline INCOSE rule checking (~24 automated + semantic flags) |
| Performance targets | Arbitrary numbers or copied from tutorials | Research-grounded baselines with comparable benchmarks and sources |
| V&V planning | Deferred to test phase; reactive | At creation time; every requirement has method + success criteria |
| Traceability | None, or manual spreadsheet | Bidirectional JSON registries: need → requirement → V&V |
| Cross-cutting concerns | Discovered during testing or production incidents | Systematic sweep with INCOSE C10-C15 validation |
| Subsystem depth | Flat list of requirements regardless of abstraction | Re-entrant pipeline; same quality at any decomposition level |
| Session resilience | Start over if interrupted | Resume at exact point with full context preserved |

---

## 5. Maturation Path

### Phase 1: Foundation

**Focus:** Core pipeline — Concept Ingestion, Needs Formalization, Block Requirements Engine, Quality Checker, V&V Planner, Traceability Engine, and Deliverable Assembly. This is the minimum viable plugin: ingest concept-dev outputs, develop requirements block-by-block with type-guided passes, check quality inline, plan V&V, maintain traceability, and produce deliverables.

**Enables:**
- Complete needs-to-requirements transformation for a single abstraction level
- Inline INCOSE quality checking (syntactic rules via keyword/pattern matching)
- Per-requirement V&V planning
- Bidirectional traceability in JSON registries
- Session resume across interruptions
- Specification document, traceability matrix, and verification matrix generation

**Dependencies:**
- Completed concept-dev session with gates passed (`.concept-dev/` artifacts)
- Python 3 runtime (for scripts: init_session.py, update_state.py, source_tracker.py, assumption_tracker.py — adapted from concept-dev)
- Claude Code plugin infrastructure

**Key decisions in this phase:**
- Quality Checker implementation: keyword/pattern-based syntactic checks vs. LLM-only vs. hybrid. Drilldown research indicates keyword/pattern + LLM semantic is the strongest approach (SRC-039, SRC-046), but LLM-only has lower implementation cost.
- Attribute elicitation UX: metered questioning (3-4 per batch) vs. batch-fill-then-review. Interaction volume (13+ attributes × N requirements) is the primary scalability risk.
- Specification document structure: MIL-STD-498 SRS (prescriptive, public) vs. block-centric custom vs. hybrid.

### Phase 2: Validation and Research

**Focus:** Set Validator, Cross-Cutting Sweep, and TPM Researcher. These add progressive validation beyond inline quality checking, system-level requirement coverage, and research-grounded performance targets.

**Enables:**
- Interface coverage validation (Carson 1998 deterministic completeness)
- Cross-block duplicate and overlap detection
- System-level cross-cutting requirements (security, reliability, availability, etc.)
- Full-set INCOSE C10-C15 validation with skeptic review
- Research-grounded performance baselines with consequence descriptions
- Problem statement coverage verification

**Dependencies:**
- Phase 1 complete and stable
- Tiered research tools configured (WebSearch always available; crawl4ai, MCP tiers optional)
- BLACKBOX.md block relationships for interface coverage checking

**Key decisions in this phase:**
- Cross-cutting category set: ISO 25010 full taxonomy (9 categories) vs. software-focused minimum set (6). Research shows ISO 25010 is comprehensive but may overlap with block-level quality passes.
- Duplicate detection method: n-gram cosine similarity (proven in Qualicen Scout) vs. transformer embeddings (better NLP benchmarks but unvalidated on requirements corpora).
- TPM scope: trigger for every measurable requirement vs. only user-designated critical requirements. Research indicates TPMs traditionally apply to <1% of requirements due to tracking cost.

### Phase 3: Decomposition and Depth

**Focus:** Subsystem Decomposer and re-entrant core validation. This is the advanced capability that enables the plugin to operate at multiple abstraction levels.

**Enables:**
- Functional decomposition of system-level blocks into sub-blocks
- Allocation rationale documentation (which parent requirements allocate to which sub-blocks)
- Parent-to-child requirement traces (INCOSE A2)
- Re-entrant pipeline: sub-blocks processed through the same core at subsystem level
- Allocation coverage validation (every parent requirement allocated)
- Multi-level deliverables (system + subsystem specifications)

**Dependencies:**
- Phase 2 complete (set validation must work reliably before adding decomposition depth)
- Baselined system-level requirements for the blocks being decomposed
- User engineering judgment for allocation rationale and budgeting decisions

**Key decisions in this phase:**
- Decomposition approach: guided with Requirements Allocation Sheet (NASA-grounded, formal) vs. lightweight with re-entry gate (lower overhead, concept-dev pattern).
- Stopping condition: user-specified, leaf-level blocks, or atomic (single-function) requirements.
- Level tracking in state.json to prevent infinite regress in re-entrant pipeline.

### Risk Reduction

| Risk | Mitigation | Decision Point |
|------|-----------|---------------|
| **Interaction volume overload**: 13 attributes × N requirements per block may produce 130+ elicitation rounds | Test metered questioning vs. batch-fill-then-review in Phase 1; measure user abandonment | End of Phase 1 — if abandonment is high, switch to batch-fill UX |
| **Quality checker false positives**: LLM semantic checks at 12-50% precision may cause alert fatigue | Start with syntactic-only checks in Phase 1; add LLM semantic checks incrementally with explicit confidence notes | Phase 1 user testing — if false positive rate >10%, defer semantic checks |
| **GtWR v4 access**: Rule applicability matrix (Appendix D) is paywalled; rule count discrepancy (42 vs 44) unresolved | Implement against publicly confirmed rules; design for rule set to be configurable | Before Phase 1 implementation — resolve rule count and get primary source access |
| **Re-entrant pipeline complexity**: State tracking across decomposition levels may introduce bugs | Defer Phase 3 until Phases 1-2 are battle-tested; design state schema for multi-level from the start | Phase 2 completion — assess state management reliability before adding depth |
| **Concept-dev artifact variability**: Different concept-dev sessions may produce artifacts of varying completeness | Concept Ingestion validates artifact quality and reports gaps; graceful degradation for missing sections | Phase 1 implementation — define minimum viable artifact set |

---

## 6. Glossary

| Term | Definition |
|------|-----------|
| **Assumption** | A statement accepted as true without proof, tracked with impact level and reviewed at phase gates. Registered in `assumption_registry.json`. |
| **Block-centric organization** | Structuring requirements development around the functional blocks defined in the concept architecture, rather than by requirement type or document section. |
| **ConOps** | Concept of Operations — a narrative description of how the system operates in representative scenarios, identifying human and automated roles. |
| **Cross-cutting requirement** | A requirement that spans multiple functional blocks (e.g., security, reliability, observability) and cannot be assigned to a single block. |
| **Design input requirement** | A requirement that constrains the solution space sufficiently to inform design decisions. Distinct from a stakeholder need (which describes an expectation) and a specification (which prescribes a solution). |
| **GtWR v4** | INCOSE Guide for Writing Requirements, version 4. Defines 42 rules for individual requirements, 15 characteristics for requirement sets, and 49 attributes per requirement. |
| **INCOSE** | International Council on Systems Engineering. The professional body that defines systems engineering standards and best practices. |
| **KPP** | Key Performance Parameter — a critical subset of MOEs with threshold (minimum acceptable) and objective (desired goal) values. Failure to meet threshold can warrant project termination. |
| **MOE / MOP / TPM** | Measures of Effectiveness (mission success) / Measures of Performance (system behavior) / Technical Performance Measures (design parameters tracked over time). A four-level hierarchy for performance measurement. |
| **Need** | A stakeholder expectation, expressed using "should." Validated against stakeholder intent. Distinct from a requirement (an obligation, expressed using "shall," verified against criteria). |
| **NRM** | INCOSE Needs and Requirements Manual. Describes the formal process for transforming lifecycle concepts into needs and requirements. |
| **Re-entrant core** | The architectural pattern where the same requirements development pipeline operates identically at system and subsystem abstraction levels. |
| **Requirement** | A formal obligation that the system must satisfy, expressed using "shall." Each requirement has mandatory attributes including rationale, traceability, priority, risk, and V&V method. Verified against acceptance criteria. |
| **Set characteristics (C10-C15)** | INCOSE quality characteristics for requirement sets (not individual requirements): C10 Completeness, C11 Consistency, C12 Feasibility, C13 Comprehensibility, C14 Able to be Validated, C15 Correctness. |
| **Skeptic review** | An adversarial verification step that checks feasibility claims, coverage assertions, and solution descriptions against registered sources. Produces verdicts: verified, unverified, disputed, needs user input. |
| **TBD / TBR** | To Be Determined (value unknown) / To Be Resolved (value contested). NASA practice recommends four closure fields: estimate, resolution path, owner, deadline. |
| **Type-guided pass** | Walking through requirements within a block by type in deliberate order: functional → performance → interface/API → constraint → quality. |
| **V&V** | Verification and Validation. Verification: "Did we build the system right?" (against requirements). Validation: "Did we build the right system?" (against stakeholder needs). |

---

## Appendices

### A. Solution Landscape Summary

See `.concept-dev/SOLUTION-LANDSCAPE.md` for detailed solution approaches per domain, covering 11 functional blocks with 34 documented approaches across 62 sub-functions.

### B. Sources

108 sources registered during concept development. By confidence level:

| Confidence | Count |
|-----------|-------|
| HIGH | 67 |
| MEDIUM | 41 |
| LOW | 0 |
| UNGROUNDED | 0 |

Full bibliography available in `.concept-dev/source_registry.json`.

Key source categories:
- INCOSE standards and guides (GtWR v4, NRM, SEBoK)
- Commercial RE tools (QVscribe, Innoslate, ReqView, Qualicen Scout)
- Academic research (Lubos 2024 LLM precision, Carson 1998 interface completeness, LLMREI 2025 elicitation)
- Government standards (MIL-STD-498, NASA NPR 7120.5, IEEE 29148)
- Industry benchmarks (Nielsen, Google RAIL/CWV, DORA, SLA tiers)

### C. Assumptions

10 assumptions tracked across 4 phases, all approved during Phase 5 mandatory review.

| ID | Assumption | Category | Impact | Status |
|----|-----------|----------|--------|--------|
| A-001 | LLM-based INCOSE rule checking can reliably automate ~24 of 42 syntactic rules; remaining semantic rules require human review | feasibility | HIGH | Approved |
| A-002 | Concept-dev outputs provide sufficient starting material to seed INCOSE-compliant needs and requirements with user refinement | feasibility | HIGH | Approved |
| A-003 | Subsystem decomposition scaffolded by LLM, engineering judgment from user | feasibility | MEDIUM | Approved |
| A-004 | Software-only focus compatible with INCOSE practices | feasibility | LOW | Approved |
| A-005 | Solo developers will accept INCOSE-level rigor if guided and conversational | stakeholder | HIGH | Approved |
| A-006 | Requirements-dev output sufficient for downstream system-design skill | scope | MEDIUM | Approved |
| A-007 | Research-assisted TPM guidance more valuable than arbitrary targets | domain_knowledge | LOW | Approved |
| A-008 | Block-centric organization maps to BLACKBOX.md structure | architecture | MEDIUM | Approved |
| A-009 | Type-guided passes produce more complete requirements than freeform writing | architecture | MEDIUM | Approved |
| A-010 | Re-entrant core operates at multiple abstraction levels without modification | architecture | HIGH | Approved |

Full assumption details available in `.concept-dev/assumption_registry.json`.
