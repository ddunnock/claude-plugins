# Solution Landscape — Requirements Development Plugin (requirements-dev)

**Version:** 1.0
**Date:** 2026-02-20
**Session:** 1f45143f
**Companion to:** CONCEPT-DOCUMENT.md

---

## Overview

This document presents solution approaches for each functional domain identified in the concept architecture. It does NOT recommend specific solutions — it maps the landscape of options with cited evidence to inform future implementation decisions.

### Scope
- Domains covered: 11 (from 11 functional blocks)
- Solution approaches documented: 34
- Sources cited: 108
- Open gaps: 31

### Research Methodology
- **Tools used:** WebSearch, WebFetch, crawl4ai
- **Search strategy:** Broad discovery via WebSearch, deep dives via crawl4ai with BM25 filtering
- **Time period:** Research conducted 2026-02-20
- **Confidence framework:** HIGH (peer-reviewed/official docs), MEDIUM (credible secondary/unverified), LOW (single source), UNGROUNDED (training data only)

---

## Domain: Concept Ingestion

### Context

Concept Ingestion reads `.concept-dev/` artifacts and extracts structured data organized by functional block. The challenge is reliable parsing of structured markdown and JSON artifacts, plus analytical extraction of needs candidates that goes beyond linguistic transformation.

### Needs Candidate Extraction

**What's needed:** Extract stakeholder needs candidates from concept-dev's capabilities, ConOps scenarios, and block behaviors.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Structured Section Parsing | Mature | Deterministic parser targeting known sections (capabilities, ConOps, block behaviors) | Reliable; targets known sections; no hallucination | Misses implicit needs in prose | SRC-001 | HIGH |
| LLM Semantic Extraction | Emerging | LLM reads full artifacts and identifies needs candidates | Catches implicit needs; flexible across formats | Hallucination risk; may fabricate needs not in source | SRC-005 | MEDIUM |
| Hybrid: Parse + LLM Review | Novel | Deterministic extraction base + LLM pass for implicit needs | Deterministic base + semantic coverage | Two-pass process; more complex | SRC-001, SRC-005 | MEDIUM |

**Gaps:**
- GAP-001: No proven pattern for LLM-based extraction of needs candidates from markdown concept documents
- GAP-002: State.json schema for requirements-dev needs design

**Next research steps:**
- Prototype structured parser against 2-3 real concept-dev outputs to measure extraction coverage
- Design state.json schema with phases, counters, and decomposition level tracking

---

## Domain: Needs Formalization

### Context

Needs Formalization transforms extracted candidates into INCOSE-compliant need statements. INCOSE distinguishes "needs" (validated expectations, "should") from "requirements" (verified obligations, "shall"). GtWR v4 introduced a Rule Applicability Matrix (Appendix D) that determines which rules apply at needs vs. requirements level.

### Need Pattern Application

**What's needed:** Apply INCOSE need statement patterns to candidate text with user refinement.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Template Fill | Emerging | Direct slot-filling: [Stakeholder] needs [capability] [qualifier] | Structured; predictable | Slot boundary ambiguity in complex needs | SRC-006 | MEDIUM |
| Rewrite and Validate | Emerging | LLM rewrites candidate in INCOSE style, then validates | Natural language flow | LLM self-validation unreliable (Kappa=0.05 per Lubos 2024) | SRC-041 | LOW |
| Hybrid Interactive | Novel | LLM drafts, user refines, system validates against patterns | Best evidence: human-LLM collaboration improves quality assessment (Lubos 2024 bound assessment) | More interaction rounds | SRC-041 | HIGH |

### Gap Detection

**What's needed:** Identify missing needs by cross-referencing against block responsibilities.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Coverage Matrix | Emerging | Automated cross-reference of needs against block functions | Systematic; comprehensive | LLM matching unproven; false confidence risk | SRC-004 | LOW |
| Guided Walkthrough | Mature | User walks through each block function, confirms coverage | User domain knowledge; reliable | Manual; slower for many blocks | SRC-004 | HIGH |

**Gaps:**
- GAP-003: Need statement patterns for software systems — standard INCOSE examples are often hardware-centric
- GAP-004: Which subset of GtWR rules apply at needs level vs. only at requirements level (Appendix D, paywalled)

**Next research steps:**
- Obtain GtWR v4 Appendix D or secondary source confirming rule applicability at needs level
- Develop software-domain need statement examples from real concept-dev outputs

---

## Domain: Block Requirements Engine

### Context

The Block Requirements Engine guides users through requirement types in order within each block. No INCOSE document prescribes a fixed type ordering for elicitation — MIL-STD-498 provides document organization, not empirically validated elicitation sequence. GtWR v4 discourages treating "interface requirements" as a standalone type category (confirmed via Wheaton 2024 secondary source).

### Type Pass Orchestration

**What's needed:** Guide users through requirement types in a structured order within each block.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Fixed Dependency Order | Convention | functional → performance → interface → constraint → quality | Predictable; simple state tracking | No empirical evidence; MIL-STD-498 is document org, not elicitation | SRC-038 | LOW |
| Context-First with Interface Folded In | Emerging | functional (including boundary interactions) → performance → constraint → quality | Aligns with GtWR v4; reduces pass count | Interface concerns may be overlooked without explicit pass | SRC-031 | MEDIUM |
| Adaptive with States/Modes Preamble | Mature | States/modes first, then types per state | Operationally grounded; flexible | More complex; states/modes may not apply to every block | SRC-038, SRC-021 | MEDIUM |

### Requirement Seeding

**What's needed:** Generate draft requirement statements from approved needs and block context.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Linguistic Template | Mature | [System] shall [action] [object] [constraint] pattern | Grounded in canonical SE patterns | Template is abstraction; NRM says transformation requires analysis | SRC-021, SRC-029 | MEDIUM |
| Batch Generation | Emerging | LLM generates multiple candidates per need for user selection | Fast; handles quantity | Hallucination risk; batch review cognitively heavy | SRC-025, SRC-036 | MEDIUM |

### TBD/TBR Management

**What's needed:** Track unresolved values with closure information.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| NASA Four-Field TBR | Mature | Each TBR has: estimate, resolution path, owner, deadline | Authoritative; actionable; grounded in NASA practice | More overhead per unknown | SRC-029, SRC-037 | HIGH |
| Simple TBD with Queue | Mature | Tag as TBD with priority; resolve in batch | Lower friction; faster | Less information captured per unknown | SRC-029 | MEDIUM |

**Gaps:**
- GAP-008: Complete GtWR v4 mandatory attribute list (A01-A49 with starred designations)
- GAP-009: INCOSE NRM specific needs-transformation steps and type-ordering rationale
- GAP-010: Empirical evidence for optimal requirement type ordering
- GAP-011: TBD/TBR closure tracking schema and resolution workflow standards

---

## Domain: Quality Checker

### Context

Quality checking is the most researched domain in this concept. QVscribe automates 24 of ~42 GtWR rules using POS tagging, keyword lists, and pattern matching. LLM-based approaches achieve high recall (74-89%) but low precision (12-50%). The hybrid approach (deterministic for syntactic + LLM for semantic) is a logical inference but not empirically demonstrated on the same dataset.

### Syntactic Rule Engine

**What's needed:** Automated checks for deterministic GtWR rules (vague terms, escape clauses, passive voice, etc.).

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| LLM-Only with Rule Prompts | Emerging | Prompt LLM with each rule definition and requirement text | No dependencies; flexible; covers all rules | 12-50% precision; high false positives | SRC-041 | LOW |
| Keyword/Pattern + LLM Semantic | Mature | Keyword dictionaries for syntactic rules; LLM for semantic | Higher precision on syntactic (~60-89%); deterministic where possible | Requires building keyword dictionaries | SRC-039, SRC-046 | MEDIUM |
| Python Script with spaCy NLP | Mature | Dedicated Python script with POS tagging and pattern matching | Reproducible; fast; follows concept-dev script pattern | Additional dependency (spaCy); maintenance burden | SRC-040, SRC-054 | MEDIUM |

### Assist-and-Flag UX

**What's needed:** Present quality findings to users without alert fatigue.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Inline Score + Detail on Request | Mature | Show pass/fail per rule; details on click/expand | Progressive disclosure; reduces fatigue | Score calibration needed | SRC-039, SRC-050 | HIGH |
| All Violations with Suggested Rewrites | Emerging | Show every violation with LLM-suggested fix | Transparent; bound assessment improves precision 13%→32% (Lubos 2024) | May overwhelm; alert fatigue risk at scale | SRC-041 | MEDIUM |

### Set-Level C10-C15

**What's needed:** Validate requirement sets against INCOSE set characteristics.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| LLM-Guided Checklist Walk-Through | Emerging | LLM walks through each characteristic with user | Covers all 6 characteristics; systematic | C12/C15 not automatable; may provide false comfort | SRC-049 | MEDIUM |
| Automated C10-C11 + Manual C12-C15 | Emerging | NLP for completeness and consistency; human judgment for rest | Honest about automation limits; targeted | Partial coverage only | SRC-049 | MEDIUM |

**Gaps:**
- GAP-012: QVscribe exact rule-by-rule coverage breakdown not retrieved
- GAP-013: GtWR v4 Appendix D full rule applicability matrix (paywalled)
- GAP-014: No published per-rule precision/recall benchmarks for individual INCOSE rule checks
- GAP-015: No integrated tool addresses all 6 set-level characteristics with known accuracy

---

## Domain: TPM Researcher

### Context

Technical Performance Measures sit within a four-level hierarchy: MOE → MOP → TPM, with KPPs as critical MOE subsets. No widely-known RE tool provides automated benchmark-based performance target recommendations — this is a confirmed capability gap and a genuine innovation opportunity for the plugin.

### Benchmark Search

**What's needed:** Search for comparable systems and published benchmarks when measurable requirements are encountered.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Pre-Built Reference DB + Live Search | Novel | Curated database for common metrics (response time, throughput, availability) + live search for novel metrics | Instant for common metrics; reliable baselines | Database maintenance; may become stale | SRC-061-065 | MEDIUM |
| Live Search Only | Emerging | Real-time search using tiered research tools for each metric | Always current; covers any metric | Slower; search quality variable by metric domain | SRC-059 | MEDIUM |
| Hybrid with Consequence Templates | Novel | Pre-built consequence templates (Nielsen thresholds, SLA tiers) + live benchmarks | Structured framing + grounded benchmarks; best of both | Templates need maintenance; limited to known domains initially | SRC-061, SRC-062, SRC-064 | HIGH |

### KPP Structure

**What's needed:** Frame performance targets with acceptable ranges, not just single values.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Full KPP Framework | Mature | Threshold (minimum acceptable) + Objective (desired goal) per metric | INCOSE-aligned; captures trade space; risk-informed | Overhead; too formal for most software requirements | SRC-066, SRC-071 | MEDIUM |
| Simple Target with Range | Mature | Target value + acceptable range + consequence description | Lower overhead; sufficient for most cases | Loses explicit risk/trade-space framing | SRC-072 | HIGH |

**Gaps:**
- GAP-016: INCOSE NRM document specifically (distinct from SE Handbook)
- GAP-017: Roedler & Jones 2005 PDF full text — TPM selection criteria
- GAP-018: No widely-known RE tool provides automated benchmark-based target recommendations — confirmed gap
- GAP-019: DORA medium/low tier thresholds behind registration wall
- GAP-020: NASA SE Handbook consequence analysis procedure for TPM tracking

**Key benchmark sources identified:**
- Nielsen response times: 100ms (instant) / 1s (flow maintained) / 10s (attention limit)
- Google RAIL model: 100ms input response, 16ms animation frame
- Core Web Vitals: LCP ≤2500ms, INP ≤200ms, CLS ≤0.1
- DORA metrics: Elite deploys on-demand, lead time <1hr (note: benchmarks shift annually based on survey responses)
- SLA tiers: 99.9% = 8h45m/yr downtime; 99.99% = 52m36s/yr

NOTE: Business impact claims require evidence quality assessment. Amazon "1% revenue per 100ms" originates from a 2006 blog post (Greg Linden), not peer-reviewed research. WPO Stats is useful but evidence quality varies by entry.

---

## Domain: V&V Planner

### Context

INCOSE GtWR v4 defines four mandatory V&V attributes: A6 (Success Criteria), A7 (Strategy), A8 (Method), A9 (Responsible Organization). INCOSE recognizes four verification methods: Inspection, Analysis, Demonstration, Test. SEBoK extends this with Analogy/Similarity and Sampling. No normative requirement-type-to-V&V-method mapping table exists in public INCOSE literature — SEBoK provides context-dependent selection guidance.

### V&V Method Selection

**What's needed:** Suggest appropriate verification method based on requirement type and content.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Type-to-Method Default Mapping | Emerging | Heuristic defaults: performance → test, interface → integration test, constraint → analysis | Fast; reduces cognitive load; predictable | No normative mapping exists; heuristic only | SRC-076 | MEDIUM |
| Context-Aware LLM Suggestion | Emerging | LLM analyzes requirement content and suggests method with rationale | Adapts to requirement content; handles edge cases | Less predictable; may suggest inappropriate methods | SRC-084 | MEDIUM |

**Gaps:**
- GAP-021: Full GtWR v4 attribute table (all 49 with definitions) — paywalled
- GAP-022: Attribute numbering discrepancy (A6 prose vs. A08 SysML) — likely zero-padding, not substantive
- GAP-023: No normative requirement-type-to-verification-method mapping table in public INCOSE sources

**Next research steps:**
- Build heuristic mapping from SEBoK selection considerations + IEEE 29119 test types
- Validate mapping against real requirements from concept-dev test cases

---

## Domain: Traceability Engine

### Context

Traceability is the backbone of the requirements-dev plugin. GtWR v4 mandates A2 (Trace to Parent) and A3 (Trace to Source) as starred mandatory attributes. The plugin needs a simple, Git-friendly, human-readable JSON format — not enterprise interchange standards.

### Registry Schema

**What's needed:** JSON schema for requirements with typed bidirectional links.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| ReqView-Style JSON with Typed Links | Mature | Link types (derives, verifies, satisfies) with source/target roles; flat JSON files | Simple; Git-friendly; human-readable; proven in production tool | Custom to plugin; non-standard interchange | SRC-081 | HIGH |
| OSLC-Aligned JSON-LD | Mature | RDF/JSON-LD linked data schema per OASIS standard | Standards-aligned; theoretically interoperable | Complex; overkill for Claude Code plugin context; heavyweight | SRC-080 | LOW |

**Gaps:**
- GAP-024: OSLC RM v2 archive 404; current v3 resource shape properties unconfirmed
- GAP-025: INCOSE Nov 2024 traceability PDF returned 404; most current guidance unavailable

**Next research steps:**
- Design requirements_registry.json schema extending concept-dev's source_registry pattern
- Define link type vocabulary: derives_from, satisfies, verified_by, allocated_to

---

## Domain: Set Validator

### Context

Set validation operates after each block completes, checking cross-block consistency, interface coverage, and set-level quality. Carson 1998 provides a formal INCOSE method for deterministic interface completeness checking. Duplicate detection uses NLP similarity but lacks a validated threshold for requirements classification.

### Interface Coverage

**What's needed:** Verify every block-to-block relationship from BLACKBOX.md has at least one interface requirement.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Interface Coverage Matrix (Carson 1998) | Mature | Enumerate all interfaces → identify conditions per interface → verify requirements exist | Deterministic; grounded in formal INCOSE method | Only checks interfaces; doesn't assess quality of coverage | SRC-087 | HIGH |

### Duplicate Detection

**What's needed:** Find semantically similar requirements across blocks.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| N-gram Cosine Similarity | Mature | Qualicen Scout pattern: n-gram tokenization + cosine distance | Proven in production RE tool; no ML dependencies | Misses semantic similarity with different wording | SRC-083 | HIGH |
| Transformer Embeddings | Emerging | sentence-transformers for semantic similarity | Catches semantic duplicates with different phrasing | Unvalidated on requirements corpora; threshold calibration needed | SRC-088 | MEDIUM |

### Feedback Loop

**What's needed:** Report validation findings back to the Block Requirements Engine for resolution.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Structured Annotation | Mature | { req_id, check_id, severity, message, suggestion } per finding | Actionable; educational; closes author feedback loop | Annotation schema is a design proposal, not extracted standard | SRC-084, SRC-090 | HIGH |

**Gaps:**
- GAP-026: No authoritative cosine similarity threshold for requirements duplicate classification

---

## Domain: Cross-Cutting Sweep

### Context

The Cross-Cutting Sweep validates the full requirement set after all blocks complete at the current level. It adds system-level requirements that no single block owns and checks the complete set against INCOSE characteristics C10-C15. Semantic goal-level completeness — verifying that requirements actually *satisfy* success criteria, not just that traceability links exist — remains an open research problem.

### Cross-Cutting Category Taxonomy

**What's needed:** A structured set of system-level concern categories to prompt users through during the sweep.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| ISO 25010 Full Taxonomy (9 categories) | Mature | Functional Suitability, Performance Efficiency, Compatibility, Usability, Reliability, Security, Maintainability, Portability, Safety | Standards-aligned; comprehensive; internationally recognized | May overlap with block-level quality pass; 9 categories is substantial | SRC-091 | HIGH |
| Software-Focused Minimum Set (6 categories) | Novel | Security, Reliability, Scalability, Maintainability, Data Integrity, Observability | Focused on software systems; avoids overlap with block-level passes; domain-appropriate | Custom set without standards backing; may miss categories | SRC-092, SRC-097 | MEDIUM |

### Problem Statement Coverage

Approach: Bidirectional traceability (needs → requirements) is the standard completeness mechanism (SRC-093). However, link existence does not guarantee semantic satisfaction — a requirement may link to a success criterion without actually addressing it (GAP-030).

DEFER: Semantic goal-level completeness checking could be addressed in a later phase. Impact of deferral: traceability-based coverage provides structural completeness but may miss semantic gaps. Risk: false confidence in coverage if links are created without substantive connection.

**Gaps:**
- GAP-030: No authoritative method for semantic goal-level completeness checking — open research problem
- GAP-031: INCOSE NRM Section 15 (management) content not retrieved

---

## Domain: Deliverable Assembly

### Context

Deliverable Assembly produces the final artifacts: specification document, traceability matrix, verification matrix, and JSON registries. MIL-STD-498 provides among the most prescriptive publicly available general-purpose SRS templates (18 requirement paragraphs), though it was canceled in 1998. IEEE 29148 is the current international standard but is paywalled. concept-dev's section-by-section approval pattern with mandatory assumption review gate is directly reusable as infrastructure (application logic requires adaptation).

### Specification Document Structure

**What's needed:** A document structure that organizes the full requirement set for human consumption.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| MIL-STD-498 SRS Structure | Mature | 18 paragraphs: states/modes (3.1), capabilities (3.2-3.6), external interfaces (3.7), internal interfaces (3.8), environment (3.9), resources (3.10), quality factors (3.15-3.16), etc. | Prescriptive; comprehensive; publicly available | Defense-oriented language; verbose; canceled 1998 | SRC-097 | HIGH |
| Block-Centric Custom Structure | Novel | Organized by functional block, then by requirement type within each block; matches the development workflow | Familiar to users; matches plugin architecture; natural reading order | Non-standard; external reviewers may not recognize structure | SRC-107 | MEDIUM |
| Hybrid: Block Body + MIL-STD-498 Cross-Cuts | Novel | Block-organized body for functional/performance/interface per block + MIL-STD-498 sections for cross-cutting (3.7-3.16) | Familiar structure for block requirements; standards-aligned cross-cutting | More complex template; two organizing principles | SRC-097, SRC-107 | HIGH |

**Gaps:**
- GAP-029: Full IEEE 29148 SRS section hierarchy unverified from primary source

---

## Domain: Subsystem Decomposer

### Context

The Subsystem Decomposer enables the re-entrant core by creating sub-blocks that feed back into the Requirements Development Core at a deeper abstraction level. NASA's logical decomposition follows three steps: partition into sub-blocks, allocate requirements with rationale, capture decisions/assumptions (SRC-102). The re-entrant process is a foundational SE principle ("System Definition processes are applied recursively" — SEBoK), not a novel innovation.

### Decomposition Approach

**What's needed:** Guide users through functional decomposition with allocation rationale.

| Approach | Maturity | Description | Pros | Cons | Sources | Confidence |
|----------|----------|-------------|------|------|---------|------------|
| Guided Decomposition with RAS | Mature | NASA three-step process + Requirements Allocation Sheet: sub-block definition, requirement allocation with rationale, decision/assumption capture | NASA-grounded; formal rationale; full traceability; allocation coverage validation | RAS format unfamiliar to software developers; overhead for simple decompositions | SRC-102, SRC-105 | HIGH |
| Lightweight Decomposition with Re-Entry Gate | Novel | concept-dev block definition pattern: name, responsibility, inputs, outputs + allocation as simple parent→child links + gate before re-entry | Lower overhead; familiar concept-dev pattern; faster | Less rigorous allocation rationale; no formal budgeting structure | SRC-093, SRC-101 | MEDIUM |

NOTE: LLM cannot make engineering budgeting judgments — user provides rationale for how quantitative values are divided across sub-blocks. The plugin scaffolds the process (presents parent value, lists sub-blocks, asks for allocation per sub-block with rationale) but does not suggest specific allocations.

**Gaps:**
- GAP-027: INCOSE NRM Section 6.4 exact content unverified (PDF 404)
- GAP-028: DoD RAS column format unverified (paywalled)

---

## Cross-Cutting Considerations

### Integration Patterns

Several patterns recur across multiple domains:

1. **concept-dev infrastructure reuse.** The init_session.py (atomic writes, UUID sessions), update_state.py (dotted-path mutations), source_tracker.py, and assumption_tracker.py patterns are structurally reusable with adaptation. Application logic differs but infrastructure patterns are proven. Note: some scripts (e.g., check_tools.py) need requirements-dev-specific modifications.

2. **Hybrid human-LLM collaboration.** Across Quality Checker, Needs Formalization, and Block Requirements Engine, the most evidence-aligned approaches combine deterministic/automated components with LLM-assisted suggestions validated by human review. Pure LLM approaches consistently show low precision (12-50%); pure automation misses semantic concerns. The "assist-and-flag" model appears throughout.

3. **Progressive disclosure UX.** Multiple domains face the interaction volume challenge: 13 attributes per requirement, multiple requirements per block, multiple blocks per system. Progressive disclosure (summary first, details on request) and batch-fill-then-review patterns address this across Quality Checker (inline score + detail) and Block Requirements Engine (attribute elicitation).

4. **JSON registry pattern.** Every domain that produces persistent data follows concept-dev's registry pattern: flat JSON files with unique IDs, typed links between entities, atomic writes via temp-file-then-rename. This extends naturally from source_registry.json to requirements_registry.json and needs_registry.json.

### Organizational Considerations

- **Guided process embeds SE knowledge.** The plugin aims to embed SE expertise in the process itself — users don't need to know INCOSE rules (the Quality Checker knows them) or V&V methods (the V&V Planner suggests them). Whether this is sufficient for non-SE-expert users requires user testing to validate.
- **Learning curve.** Users unfamiliar with the needs vs. requirements distinction will need the plugin to explain as it goes. The conversational, guided approach serves as on-the-job education.
- **Team coordination.** Session resume enables multi-person workflows, but the plugin doesn't manage permissions or conflict resolution for concurrent edits.

### Standards and Compliance

| Standard | Relevance | How Used |
|----------|-----------|----------|
| INCOSE GtWR v4 | Primary | ~42 rules for quality checking; 49 attributes per requirement; 15 set characteristics |
| INCOSE NRM | Primary | Needs-to-requirements transformation process; type taxonomy; allocation process |
| MIL-STD-498 | Template | SRS document structure (18 paragraphs) for specification deliverable |
| IEEE 29148 | Reference | Current international SRS standard (paywalled; MIL-STD-498 used as public alternative) |
| ISO 25010:2023 | Taxonomy | 9 quality characteristics for cross-cutting sweep categories |
| NASA NPR 7120.5 | Process | Recursive decomposition process; TBR management; verification matrix format |
| SEBoK | Reference | System definition process; V&V method definitions; requirements engineering guidance |

---

## Unresolved Gaps

Gaps requiring further investigation before implementation planning:

| Priority | Gap ID | Domain | Description | Needs |
|----------|--------|--------|-------------|-------|
| High | GAP-004 | Needs Formalization | GtWR v4 Appendix D rule applicability at needs vs. requirements level | standards_document |
| High | GAP-008 | Block Req Engine | Complete GtWR v4 mandatory attribute list (A01-A49 with starred designations) | standards_document |
| High | GAP-010 | Block Req Engine | Empirical evidence for optimal requirement type ordering | paper |
| High | GAP-013 | Quality Checker | GtWR v4 Appendix D full rule applicability matrix (paywalled) | standards_document |
| High | GAP-030 | Cross-Cutting Sweep | No authoritative method for semantic goal-level completeness checking | paper |
| Medium | GAP-001 | Concept Ingestion | No proven pattern for LLM-based needs extraction from markdown concept documents | web_research |
| Medium | GAP-003 | Needs Formalization | Need statement patterns for software systems (INCOSE examples are hardware-centric) | web_research |
| Medium | GAP-012 | Quality Checker | QVscribe exact rule-by-rule coverage breakdown not retrieved | web_research |
| Medium | GAP-015 | Quality Checker | No integrated tool addresses all 6 set-level characteristics with known accuracy | web_research |
| Medium | GAP-018 | TPM Researcher | No widely-known RE tool provides automated benchmark-based target recommendations | web_research |
| Medium | GAP-023 | V&V Planner | No normative requirement-type-to-verification-method mapping | standards_document |
| Medium | GAP-026 | Set Validator | No authoritative cosine similarity threshold for requirements duplicate classification | paper |
| Medium | GAP-027 | Subsystem Decomposer | INCOSE NRM Section 6.4 exact content unverified | standards_document |
| Low | GAP-002 | Concept Ingestion | State.json schema for requirements-dev needs design | existing_system |
| Low | GAP-009 | Block Req Engine | INCOSE NRM needs-transformation steps and type-ordering rationale | standards_document |
| Low | GAP-011 | Block Req Engine | TBD/TBR closure tracking schema standards | standards_document |
| Low | GAP-014 | Quality Checker | No published per-rule precision/recall benchmarks | paper |
| Low | GAP-016 | TPM Researcher | INCOSE NRM document (distinct from SE Handbook) | standards_document |
| Low | GAP-017 | TPM Researcher | Roedler & Jones 2005 TPM selection criteria | standards_document |
| Low | GAP-019 | TPM Researcher | DORA medium/low tier thresholds behind registration wall | web_research |
| Low | GAP-020 | TPM Researcher | NASA SE Handbook consequence analysis procedure | standards_document |
| Low | GAP-021 | V&V Planner | Full GtWR v4 attribute table (all 49 definitions) | standards_document |
| Low | GAP-022 | V&V Planner | Attribute numbering discrepancy (A6 vs. A08) | standards_document |
| Low | GAP-024 | Traceability Engine | OSLC RM v2 archive 404 | web_research |
| Low | GAP-025 | Traceability Engine | INCOSE Nov 2024 traceability PDF 404 | standards_document |
| Low | GAP-028 | Subsystem Decomposer | DoD RAS column format unverified | standards_document |
| Low | GAP-029 | Deliverable Assembly | IEEE 29148 SRS section hierarchy unverified | standards_document |
| Low | GAP-031 | Cross-Cutting Sweep | INCOSE NRM Section 15 management content | standards_document |

---

## Skeptic Review Summary

| Metric | Count |
|--------|-------|
| Claims reviewed | 40 |
| VERIFIED | 24 |
| UNVERIFIED_CLAIM | 9 |
| DISPUTED_CLAIM | 5 |
| NEEDS_USER_INPUT | 2 |

**High-priority flags:**

1. **Kappa 0.75 for needs formalization (DISPUTED):** Source misattribution — figure comes from Lubos 2024 (SRC-041) requirements quality assessment on the Stopwatch project, not need statement formalization. The DigitalHome project achieved only Kappa 0.22 under the same conditions. Cherry-picked metric applied to wrong domain.

2. **"44.4% outperformed" (DISPUTED):** LLMREI paper reports question type distribution, not comparative effectiveness. Context-deepening questions are common in effective LLM elicitation, but "outperformed" editorializes beyond the data.

3. **Rule count denominator (DISPUTED):** Varies 41/42/44 across sources. Best evidence: 42 rules in GtWR v4 per reqi.io. The "24" numerator is consistent; recommend "24 of ~42."

4. **Scripts "directly reusable" (DISPUTED):** Infrastructure patterns (atomic writes, UUID sessions, JSON templates) are reusable. Application logic (e.g., check_tools.py) needs requirements-dev-specific adaptation.

5. **C10/C11 automation percentages (UNVERIFIED):** Specific figures (~38% for C10, ~60% for C11) could not be traced to primary sources.

**Overall assessment:** 60% of claims verified — strong for a concept-phase document. The document's own skeptic annotations catch most issues found in this review.

---

## Source Bibliography

108 sources registered. Full metadata available in `.concept-dev/source_registry.json`.

### By Confidence Level

**HIGH (67 sources):**
Key sources include INCOSE GtWR v4 (SRC-006), QRA Corp QVscribe documentation (SRC-007, SRC-039, SRC-053), Lubos et al. 2024 LLM precision study (SRC-041), Paska/Rimay CNL tool (SRC-046), Carson 1998 interface completeness (SRC-087), MIL-STD-498 SRS (SRC-097), NASA NPR 7120.5 (SRC-102), Google Core Web Vitals (SRC-063), DORA metrics (SRC-059), ReqView JSON schema (SRC-081), concept-dev codebase artifacts (SRC-001, SRC-107, SRC-108).

**MEDIUM (41 sources):**
Key sources include SEBoK system verification (SRC-076), Innoslate requirements AI (SRC-025), LLMREI 2025 elicitation research (SRC-032), Qualicen Scout duplicate detection (SRC-083), ISO 25010:2023 quality model (SRC-091), DoD Requirements Allocation Sheet (SRC-105), WPO Stats performance impact (SRC-064).

**LOW (0 sources).**

**UNGROUNDED (0 sources).**

---

## Assumptions

| ID | Assumption | Category | Phase | Status |
|----|-----------|----------|-------|--------|
| A-001 | LLM-based INCOSE rule checking can reliably automate ~24 of ~42 syntactic rules; remaining semantic rules require human review | feasibility | spitball | Approved |
| A-002 | Concept-dev outputs provide sufficient starting material to seed INCOSE-compliant needs and requirements with user refinement | feasibility | spitball | Approved |
| A-003 | Subsystem decomposition scaffolded by LLM, engineering judgment from user | feasibility | spitball | Approved |
| A-004 | Software-only focus compatible with INCOSE practices | feasibility | spitball | Approved |
| A-005 | Solo developers will accept INCOSE-level rigor if guided and conversational | stakeholder | problem | Approved |
| A-006 | Requirements-dev output sufficient for downstream system-design skill | scope | problem | Approved |
| A-007 | Research-assisted TPM guidance more valuable than arbitrary targets | domain_knowledge | problem | Approved |
| A-008 | Block-centric organization maps to BLACKBOX.md structure | architecture | blackbox | Approved |
| A-009 | Type-guided passes produce more complete requirements than freeform writing | architecture | blackbox | Approved |
| A-010 | Re-entrant core operates at multiple abstraction levels without modification | architecture | blackbox | Approved |
