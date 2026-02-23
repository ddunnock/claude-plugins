# Drill-Down & Gap Analysis — Requirements Development Plugin (requirements-dev)

**Session:** 1f45143f
**Date:** 2026-02-20
**Phase:** Drill-Down (Phase 4)

---

## Summary

| Metric | Count |
|--------|-------|
| Blocks analyzed | 11 |
| Sub-functions identified | 62 |
| Sources registered | 108 |
| Gaps identified | 31 |
| Solution approaches documented | 34 |
| Skeptic: Verified | 17 |
| Skeptic: Unverified | 11 |
| Skeptic: Disputed | 10 |
| Skeptic: Needs User Input | 5 |

---

## Block 1: Concept Ingestion

### Sub-Functions

1. **Artifact Discovery** — Locates and validates `.concept-dev/` artifacts (CONCEPT-DOCUMENT.md, BLACKBOX.md, SOLUTION-LANDSCAPE.md, PROBLEM-STATEMENT.md, registries)
2. **Gate Validation** — Verifies concept-dev phases completed with gates passed
3. **Block Metadata Extraction** — Extracts functional block definitions, responsibilities, inputs, outputs, and relationships from BLACKBOX.md
4. **Needs Candidate Extraction** — Mines capabilities, ConOps scenarios, and block behaviors for needs candidates
5. **Source/Assumption Linking** — Preserves source_registry.json and assumption_registry.json IDs for traceability
6. **Extraction Summary** — Reports N blocks found, N needs candidates, N sources available

### Research Findings

#### Artifact Discovery & Extraction

**Domain Context:** The concept-dev plugin produces structured markdown artifacts with consistent frontmatter and JSON registries. The ingestion challenge is parsing these reliably. INCOSE NRM describes needs extraction as requiring "underlying analysis" beyond linguistic transformation.

**Key Findings:**
1. Concept-dev artifacts contain functional blocks, stakeholders, constraints, and research sources — standard NRM inputs for needs extraction. (Source: SRC-001, SRC-002; Confidence: HIGH)
2. Skill authoring best practices recommend deterministic scripts for reliability, with one-level-deep file references. (Source: SRC-003; Confidence: HIGH)
3. INCOSE NRM needs transformation process requires analytical work, not just linguistic extraction. Concept-dev artifacts provide starting material, not deterministic transformation inputs. (Source: SRC-005; Confidence: HIGH)
4. Concept-dev artifacts may lack lifecycle concepts beyond ConOps — lifecycle stages, disposal, maintenance needs may require supplementary elicitation. (Skeptic finding; Confidence: MEDIUM)

**Prior Art:**
- concept-dev init_session.py — Atomic write pattern, UUID sessions, JSON template loading (Source: SRC-001)
- concept-dev state.json template — Phase tracking, tool detection, counter management (Source: SRC-002)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-001 | No proven pattern for LLM-based extraction of needs candidates from markdown concept documents | Concept Ingestion | web_research | Open |
| GAP-002 | State.json schema for requirements-dev needs design — what phases, counters, additional fields beyond concept-dev | Concept Ingestion | existing_system | Open |

### Solution Approaches

#### Needs Candidate Extraction

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Structured Section Parsing | Mature | Deterministic; targets known sections (capabilities, ConOps, block behaviors) | Misses implicit needs in prose | SRC-001 | HIGH |
| LLM Semantic Extraction | Emerging | Catches implicit needs; flexible | Hallucination risk; may fabricate needs | SRC-005 | MEDIUM |
| Hybrid: Parse + LLM Review | Novel | Deterministic base + semantic coverage | More complex; two-pass process | SRC-001, SRC-005 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| Concept-dev outputs provide sufficient starting material to seed needs | VERIFIED | Artifacts contain standard NRM inputs, but not all lifecycle concepts may be present |
| check_tools.py can be reused as-is | DISPUTED | Needs adaptation for requirements-dev context; different tool detection needs |
| Concept-dev artifacts cover all lifecycle stages | DISPUTED | ConOps covers operational scenarios but may miss disposal, maintenance, transition needs |

---

## Block 2: Needs Formalization

### Sub-Functions

1. **Need Pattern Application** — Apply INCOSE need statement patterns ([Stakeholder] needs [capability] [qualifier])
2. **Solution-Free Validation** — Ensure need statements describe expectations, not solutions
3. **Per-Block Presentation** — Present formalized needs organized by functional block from BLACKBOX.md
4. **Gap Detection** — Identify missing needs by cross-referencing against block responsibilities
5. **Needs Registry Management** — Store needs as structured JSON with attributes (ID, text, source block, stakeholder, type, status)
6. **Needs Gate** — User reviews and approves the complete needs set before proceeding

### Research Findings

#### Need Statement Patterns

**Domain Context:** INCOSE GtWR v4 provides explicit patterns for need statements. The NRM describes a formal transformation process from stakeholder expectations to structured need statements. GtWR v4 introduced a Rule Applicability Matrix (Appendix D) that distinguishes which rules apply at needs level vs requirements level.

**Key Findings:**
1. INCOSE distinguishes "needs" (validated expectations, "should") from "requirements" (verified obligations, "shall"). (Source: SRC-006, SRC-008; Confidence: HIGH)
2. QRA Corp's QVscribe automates 24 of 44 GtWR rules for requirement statements, but applicability to need statements requires Appendix D. (Source: SRC-007; Confidence: HIGH)
3. GtWR v4 Appendix D confirms NOT all rules apply equally at needs and requirements levels. The "~24 automatable rules" figure is validated for requirements only. (Skeptic finding; Source: SRC-006; Confidence: HIGH)
4. LLM precision for requirements quality checking: 12-50% on real projects (Lubos 2024). "Reliably" must be qualified — this is a drafting aid requiring human validation. (Skeptic finding; Confidence: HIGH)

**Prior Art:**
- INCOSE GtWR v4 — Need statement patterns, rule applicability matrix (Source: SRC-006)
- QRA Corp QVscribe — Automated rule checking for ~24 of 44 rules (Source: SRC-007)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-003 | Need statement patterns for software systems — standard INCOSE examples are often hardware-centric | Needs Formalization | web_research | Open |
| GAP-004 | Which subset of GtWR rules apply at needs level vs only at requirements level | Needs Formalization | standards_document | Open |

### Solution Approaches

#### Need Pattern Application

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Template Fill | Emerging | Direct pattern application | Slot boundary ambiguity | SRC-006 | MEDIUM |
| Rewrite and Validate | Emerging | Natural language flow | LLM self-validation unreliable (Kappa=0.05) | SRC-006, SRC-008 | LOW |
| Hybrid Interactive | Novel | Best evidence: human-LLM collab achieves Kappa 0.75 | More interaction rounds | SRC-006 | HIGH |

#### Gap Detection

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Coverage Matrix | Emerging | Automated cross-reference | LLM matching unproven; false confidence risk | SRC-004 | LOW |
| Guided Walkthrough | Mature | User domain knowledge; reliable | Manual; slower | SRC-004 | HIGH |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| LLM can reliably apply INCOSE need patterns | DISPUTED | 13% precision on real projects; reframe as "drafting aid requiring human validation" |
| Solution-free keyword validation is sufficient | UNVERIFIED | Catches obvious cases; misses implicit solution language |
| SEBoK recommends systematic coverage checking | DISPUTED | SEBoK describes general traceability, not "systematic coverage checking against system functions" — source mis-attributed |
| Software adaptation of INCOSE patterns is straightforward | NEEDS_INPUT | GAP-003; patterns may need domain-specific examples |

---

## Block 3: Block Requirements Engine

### Sub-Functions

1. **Type Pass Orchestration** — Guides user through requirement types in order: functional → performance → interface/API → constraint → quality
2. **Requirement Seeding** — Generates draft requirement statements from approved needs + block context
3. **Attribute Elicitation** — Prompts user for 13 mandatory INCOSE attributes per requirement
4. **TPM Trigger** — Detects measurable requirements and triggers TPM Researcher
5. **TBD/TBR Management** — Tracks unresolved values; carries forward concept-dev gaps
6. **Per-Block State Tracking** — Maintains progress for session resume

### Research Findings

#### Type-Guided Elicitation

**Domain Context:** No INCOSE document prescribes a fixed type ordering for elicitation. MIL-STD-498 provides document organization (states/modes → functional → interface → data → constraints → quality), and GtWR v4 discourages treating "interface requirements" as a separate type category.

**Key Findings:**
1. MIL-STD-498 SRS ordering reflects document organization, not empirically validated elicitation sequence. (Source: SRC-038; Confidence: MEDIUM)
2. GtWR v4 rejects "interface requirements" as a standalone type — interface requirements are functional requirements crossing system boundaries. (Source: SRC-031; Confidence: MEDIUM via secondary source)
3. LLMREI research (2025): context-deepening follow-ups (44.4% of effective questions) outperformed type-categorical questioning for open elicitation. (Source: SRC-032; Confidence: HIGH)
4. No empirical study found comparing type-guided vs freeform elicitation for completeness. (GAP-010)
5. NASA TBR with four closure fields (estimate, resolution path, owner, deadline) is explicitly superior to plain TBD. (Source: SRC-029; Confidence: HIGH)

**Prior Art:**
- MIL-STD-498 SRS — Document-level type ordering (Source: SRC-038)
- Innoslate Requirements AI — Three-phase generation: Setup → Configure → Verify/Create (Source: SRC-025)
- NASA Appendix C — TBR > TBD with four required fields (Source: SRC-029)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-008 | Complete GtWR v4 mandatory attribute list (A01-A49 with starred designations) | Attribute Elicitation | standards_document | Open |
| GAP-009 | INCOSE NRM specific needs-transformation steps and type-ordering rationale | Type Pass Orchestration | standards_document | Open |
| GAP-010 | Empirical evidence for optimal requirement type ordering | Type Pass Orchestration | paper | Open |
| GAP-011 | TBD/TBR closure tracking schema and resolution workflow standards | TBD/TBR Management | standards_document | Open |

### Solution Approaches

#### Type Pass Orchestration

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Fixed Dependency Order | Convention | Predictable; simple state tracking | No empirical evidence; MIL-STD-498 is document org, not elicitation | SRC-038 | LOW |
| Context-First with Interface Folded In | Emerging | Aligns with GtWR v4; reduces pass count | Interface concerns may be overlooked | SRC-031 | MEDIUM |
| Adaptive with States/Modes Preamble | Mature | Operationally grounded; flexible | More complex; states/modes may not apply to every block | SRC-038, SRC-021 | MEDIUM |

#### Requirement Seeding

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| SEBoK Linguistic Template | Mature | Grounded in canonical SE example | Template is abstraction, not direct SEBoK artifact; NRM says transformation requires analysis | SRC-021, SRC-029 | MEDIUM |
| Innoslate-Style Batch Generation | Emerging | Fast; handles quantity | Hallucination risk; batch review cognitively heavy | SRC-025, SRC-036 | MEDIUM |

#### TBD/TBR Management

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| NASA Four-Field TBR | Mature | Authoritative; actionable; grounded | More overhead per unknown | SRC-029, SRC-037 | HIGH |
| Simple TBD with Queue | Mature | Lower friction; faster | Less information captured | SRC-029 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| Fixed type ordering produces more complete requirements | UNVERIFIED | No empirical backing; MIL-STD-498 supports categorization not elicitation ordering |
| 13 mandatory starred attributes | UNVERIFIED | User-reported from GtWR v4 reading; public sources only confirm 5-6 |
| Linguistic seeding is sufficient transformation | DISPUTED | NRM requires "underlying analysis" not just linguistic rewriting; seeding is a draft starting point |
| GtWR v4 discourages interface as separate type | VERIFIED | Confirmed via Wheaton 2024 SysML paper (secondary source) |
| TBR > TBD | VERIFIED | NASA Appendix C explicitly states TBR with four fields is "better" |
| Interaction volume (15-20+ rounds/block) is feasible | UNVERIFIED | No precedent validates this density with AskUserQuestion |

---

## Block 4: Quality Checker

### Sub-Functions

1. **Syntactic Rule Engine** — Automated checks for ~24 deterministic GtWR rules (vague terms, escape clauses, passive voice, etc.)
2. **Semantic Rule Flagger** — LLM-assisted checks for remaining rules with explicit confidence notes
3. **Inline Per-Requirement Check** — Quality check triggered after each requirement draft
4. **Per-Block Set Check** — At block completion, checks set characteristics C10-C15
5. **Violation Resolution** — Presents flagged violations with suggested rewrites; requires user resolution
6. **Rule Applicability Filter** — Determines which rules apply at needs vs requirements level (per GtWR v4 Appendix D)

### Research Findings

#### Automated Rule Checking

**Domain Context:** QVscribe automates 24 of 44 GtWR rules using POS tagging, keyword lists, and pattern matching. LLM-based approaches achieve high recall but low precision. The hybrid approach (deterministic for syntactic + LLM for semantic) is a logical inference but not empirically demonstrated on the same dataset.

**Key Findings:**
1. QVscribe automates 24 of 44 rules using NLP (POS tagging, keyword/phrase lists, pattern matching). (Source: SRC-053; Confidence: HIGH)
2. LLM quality checking: 12-50% precision, 74-89% recall (Lubos 2024). "Bound assessment" (human sees LLM reasoning) improves precision from 13% to 32%. (Source: SRC-041; Confidence: HIGH)
3. Paska tool (NLP + Rimay CNL): 89% precision and recall on 2725 industrial requirements. Sets strong NLP baseline. (Source: SRC-046; Confidence: HIGH)
4. Set-level C10-C15: Only C10 (completeness, ~38% via BERT) and C11 (consistency, ~60% recall via NLI) have partial automation. C12 (Feasibility) and C15 (Correctness) require human judgment. (Source: SRC-049, SRC-050; Confidence: HIGH)
5. Alert fatigue: QuARS targets <10% false positive rate. No RE-specific threshold study exists. (Source: SRC-040; Confidence: MEDIUM)

**Prior Art:**
- QVscribe (QRA Corp) — 24/44 rules, inline NLP checker, five-star rating (Source: SRC-039, SRC-053)
- Paska/Rimay — CNL-based, 89% precision (Source: SRC-046)
- REUSE Company RAT — Real-time authoring guidance aligned to GtWR (Source: SRC-051)
- Innoslate Quality Check — 6 automated NLP checks with override model (Source: SRC-050)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-012 | QVscribe exact rule coverage table — specific rule-by-rule breakdown not retrieved | Syntactic Rule Engine | web_research | Open |
| GAP-013 | GtWR v4 Appendix D full rule applicability matrix (paywalled) | Rule Applicability Filter | standards_document | Open |
| GAP-014 | No published per-rule precision/recall benchmarks for individual INCOSE rule checks | Syntactic Rule Engine | paper | Open |
| GAP-015 | No integrated tool addresses all 6 set-level characteristics (C10-C15) with known accuracy | Per-Block Set Check | web_research | Open |

### Solution Approaches

#### Syntactic Rule Engine

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| LLM-Only with Rule Prompts | Emerging | No dependencies; flexible | 12-50% precision; high false positives | SRC-041 | LOW |
| Keyword/Pattern + LLM Semantic | Mature | Higher precision on syntactic rules (~60-89%); deterministic where possible | Requires keyword dictionaries | SRC-039, SRC-046 | MEDIUM |
| Python Script with spaCy NLP | Mature | Reproducible; fast; concept-dev script pattern | Additional dependency; maintenance burden | SRC-040, SRC-054 | MEDIUM |

#### Assist-and-Flag UX

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Inline Score + Detail on Request | Mature | Progressive disclosure; reduces fatigue | Score calibration needed | SRC-039, SRC-050 | HIGH |
| All Violations with Suggested Rewrites | Emerging | Transparent; bound assessment improves precision | May overwhelm; alert fatigue risk | SRC-041 | MEDIUM |

#### Set-Level C10-C15

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| LLM-Guided Checklist Walk-Through | Emerging | Covers all 6; systematic | C12/C15 not automatable; may provide false comfort | SRC-049 | MEDIUM |
| Automated C10-C11 + Manual C12-C15 | Emerging | Honest about limits; targeted | C10 only ~38% coverage; C11 ~60% recall | SRC-049 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| ~24 of 42 rules automatable | DISPUTED | Rule count discrepancy: 42 vs 44 vs 41 across sources; "24 of 44" per QVscribe's own docs |
| LLM precision 12-50%, recall 74-89% | VERIFIED | Lubos 2024 figures directly confirmed from source |
| Bound assessment improves precision 13%→32% | VERIFIED | DigitalHome study, directly verified |
| Set-level C12/C15 require human judgment | VERIFIED | Innoslate v4.10 partially automates C12 but still requires human confirmation |
| 10% alert fatigue threshold | UNVERIFIED | Borrowed from security/clinical domains; no RE-specific study |
| Hybrid approach outperforms LLM-only | UNVERIFIED | Logical inference from cross-study comparison, not controlled experiment |

---

## Block 5: TPM Researcher

### Sub-Functions

1. **Trigger Detection** — Recognizes measurable/quantifiable elements needing grounded baselines
2. **Benchmark Search** — Uses tiered research tools to find comparable systems and published benchmarks
3. **Baseline Table Assembly** — Presents benchmarks as structured table (system, metric, value, source)
4. **Consequence/Effect Descriptions** — Provides impact descriptions at different value ranges
5. **Source Registration** — Registers research sources with confidence levels
6. **User Value Selection** — Presents research; user makes informed value decision with rationale

### Research Findings

#### TPM Framework and Benchmarks

**Domain Context:** Technical Performance Measures sit within a four-level hierarchy: MOE → MOP → TPM, with KPPs as critical MOE subsets. No existing RE tool provides automated benchmark-based performance target recommendations — this is a confirmed capability gap and genuine innovation opportunity.

**Key Findings:**
1. KPP threshold/objective structure: threshold = minimum acceptable at low-moderate risk; objective = desired goal at higher risk. Failure to meet KPP threshold can cause program termination. (Source: SRC-066, SRC-071; Confidence: HIGH)
2. TPMs traditionally apply to <1% of requirements due to tracking cost. Plugin must calibrate scope. (Source: SRC-055; Confidence: MEDIUM)
3. Well-established software benchmark sources: Nielsen response times (100ms/1s/10s), Google RAIL model, Core Web Vitals (LCP ≤2500ms, INP ≤200ms), DORA metrics (elite: deploy on-demand, lead time <1hr), SLA tiers (99.9%=8h45m/yr downtime). (Source: SRC-061-063, SRC-059, SRC-069; Confidence: HIGH)
4. Business impact data provenance issues: Amazon "1% per 100ms" originates from a 2006 blog post, not peer-reviewed research. WPO Stats collection is useful but evidence quality varies. (Skeptic finding; Confidence: MEDIUM)
5. DORA benchmarks shift annually based on survey responses — not fixed universal standards. (Source: SRC-059; Confidence: HIGH)
6. concept-dev's web_researcher.py (crawl4ai + BM25 filtering + source registration) is reusable as infrastructure; application logic (numeric extraction, table structuring) would be new. (Source: direct code inspection; Confidence: HIGH)

**Prior Art:**
- Google Core Web Vitals — Three-tier thresholds with published CrUX methodology (Source: SRC-063)
- DORA Metrics — Annual benchmarks with elite/high/medium/low tiers (Source: SRC-059)
- Nielsen/RAIL — Foundational UX response time thresholds (Source: SRC-061, SRC-062)
- WPO Stats — Curated performance impact case studies (Source: SRC-064)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-016 | INCOSE NRM document specifically (distinct from SE Handbook) | TPM Framework | standards_document | Open |
| GAP-017 | Roedler & Jones 2005 PDF full text — TPM selection criteria | TPM Framework | standards_document | Open |
| GAP-018 | No RE tool provides automated benchmark-based target recommendations — confirmed gap | Benchmark Search | web_research | Open |
| GAP-019 | DORA medium/low tier thresholds behind registration wall | Benchmark Search | web_research | Open |
| GAP-020 | NASA SE Handbook consequence analysis procedure for TPM tracking | Consequence Descriptions | standards_document | Open |

### Solution Approaches

#### Benchmark Search

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Pre-Built Reference DB + Live Search | Novel | Instant for common metrics; reliable baselines | Database maintenance; may become stale | SRC-061-065 | MEDIUM |
| Live Search Only | Emerging | Always current; covers any metric | Slower; search quality variable | SRC-059 | MEDIUM |
| Hybrid with Consequence Templates | Novel | Structured framing + grounded benchmarks | Templates need maintenance | SRC-061, SRC-062, SRC-064 | HIGH |

#### KPP Structure

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Full KPP Framework | Mature | INCOSE-aligned; captures trade space | Overhead; too formal for most software reqs | SRC-066, SRC-071 | MEDIUM |
| Simple Target with Range | Mature | Lower overhead; sufficient for most cases | Loses risk/trade-space framing | SRC-072 | HIGH |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| No mainstream RE tool provides benchmark-based target recommendations | UNVERIFIED | Likely true but unfalsifiable negative; soften to "no widely-known tool found" |
| Benchmark sources are well-established | VERIFIED | Nielsen, RAIL, CWV, DORA, SLA tiers all confirmed authoritative |
| Business impact case studies are grounded | DISPUTED | Amazon 1%/100ms from blog post; Akamai 7%/1s from vendor marketing — must distinguish evidence quality |
| KPP framework applicable to software | VERIFIED | Structurally domain-agnostic; but TPMs apply to <1% of reqs in DoD practice |
| crawl4ai pattern reusable | VERIFIED | Infrastructure reusable; application logic (numeric extraction) is new |

---

## Block 6: V&V Planner

### Sub-Functions

1. **V&V Method Selection** — Suggests verification method based on requirement type
2. **Success Criteria Elicitation** — Prompts user to define "pass" criteria
3. **Responsible Party Assignment** — Records who verifies each requirement
4. **Strategy Notes** — Captures implementation notes and special considerations
5. **V&V Attribute Population** — Populates INCOSE attributes A6-A9

### Research Findings

**Key Findings:**
1. INCOSE GtWR v4 attributes: A6 = V&V Success Criteria, A7 = V&V Strategy, A8 = V&V Method, A9 = V&V Responsible Organization. Confirmed from multiple secondary sources. (Source: SRC-073, SRC-074, SRC-075; Confidence: HIGH)
2. Four INCOSE verification methods: Inspection, Analysis, Demonstration, Test. SEBoK adds Analogy/Similarity and Sampling. (Source: SRC-076; Confidence: HIGH)
3. IEEE 29119-3 provides test documentation structure templates, not parameterized success criteria. ISTQB provides conceptual frameworks. Both inform but don't provide plug-and-play templates. (Source: SRC-085, SRC-086; Confidence: HIGH)
4. No normative requirement-type-to-V&V-method mapping table exists in public INCOSE literature. SEBoK provides context-dependent selection guidance. (GAP-023; Confidence: HIGH)

**Prior Art:**
- SEBoK System Verification — Method definitions and partial artifact-to-method guidance (Source: SRC-076)
- Innoslate — INCOSE-aligned V&V attribute fields per requirement (Source: SRC-082)
- IBM Requirements Assistant / QuARS — Interactive verifiability checking (Source: SRC-084)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-021 | Full GtWR v4 attribute table (all 49 with definitions) — paywalled | V&V Attribute Population | standards_document | Open |
| GAP-022 | Attribute numbering discrepancy (A6 prose vs A08 SysML) — likely zero-padding, not substantive | V&V Attribute Population | standards_document | Open |
| GAP-023 | No normative requirement-type-to-verification-method mapping table | V&V Method Selection | standards_document | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Type-to-Method Default Mapping | Emerging | Fast; reduces cognitive load | No normative mapping exists; heuristic defaults | SRC-076 | MEDIUM |
| Context-Aware LLM Suggestion | Emerging | Adapts to requirement content | Less predictable; may suggest inappropriate methods | SRC-084 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| V&V attributes A6-A9 confirmed | VERIFIED | Zero-padded numbering (A8 = A08) is formatting, not genuine discrepancy |
| Type-to-method mapping derivable from SEBoK | DISPUTED | SEBoK provides selection considerations, not a derivable mapping; heuristic defaults only |
| IEEE 29119-3/ISTQB provide reusable success criteria templates | UNVERIFIED | They provide document structure and conceptual frameworks, not parameterized criteria |

---

## Block 7: Traceability Engine

### Sub-Functions

1. **ID Assignment** — Assigns unique IDs to all entities (NEED-xxx, REQ-xxx)
2. **Link Management** — Maintains parent traces (A2), source traces (A3), V&V links (A6-A9)
3. **Referential Integrity** — Validates no dangling links
4. **Query Support** — "Which requirements trace to NEED-003?" or "Which needs have no requirements?"
5. **Atomic Writes** — Temp-file-then-rename for crash safety (concept-dev pattern)

### Research Findings

**Key Findings:**
1. GtWR v4 mandates A2 (Trace to Parent) and A3 (Trace to Source) as starred mandatory attributes. (Source: SRC-073, SRC-074; Confidence: HIGH)
2. ReqView JSON link-type schema provides a practical, Git-friendly model: `{ linkTypeId: { name, source_role, target_role } }`. Link types: derives, verifies, satisfies. (Source: SRC-081; Confidence: HIGH)
3. ReqIF v1.2 is the de facto interchange standard but has practical interoperability gaps between tools. Not relevant since plugin uses own JSON. (Source: SRC-079; Confidence: HIGH)
4. OSLC RM v2 provides JSON-LD schema but is overkill for a Claude Code plugin. (Source: SRC-080; Confidence: HIGH)

**Prior Art:**
- ReqView — JSON-format RM tool with typed links, Git-friendly (Source: SRC-081)
- OMG ReqIF v1.2 — XML interchange standard for bidirectional traceability (Source: SRC-079)
- OSLC RM v2 — RDF/JSON-LD linked data schema (Source: SRC-080)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-024 | OSLC RM v2 archive 404; current v3 resource shape properties unconfirmed | Schema Design | web_research | Open |
| GAP-025 | INCOSE Nov 2024 traceability PDF returned 404; most current guidance unavailable | Link Management | standards_document | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| ReqView-Style JSON with Typed Links | Mature | Simple; Git-friendly; human-readable; proven | Custom to plugin; non-standard | SRC-081 | HIGH |
| OSLC-Aligned JSON-LD | Mature | Standards-aligned; interoperable | Complex; overkill for context | SRC-080 | LOW |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| ReqView JSON model is practical and Git-friendly | VERIFIED | Documented format with Git/SVN support confirmed |
| A2/A3 are mandatory traceability attributes | VERIFIED | Starred in GtWR v4 summary sheets |
| ReqIF is de facto interchange standard | VERIFIED | With caveat: practical interoperability gaps between tool implementations |

---

## Block 8: Set Validator

### Sub-Functions

1. **Interface Coverage Check** — Verifies every block-to-block relationship from BLACKBOX.md has at least one interface requirement
2. **Duplicate/Overlap Detection** — Finds semantically similar requirements across blocks
3. **Consistency Check** — Consistent terminology and units across the set (C11)
4. **Uncovered Needs Report** — Reports needs without requirements
5. **Feedback Loop** — Feeds gaps back to Block Requirements Engine

### Research Findings

**Key Findings:**
1. Carson 1998's deterministic completeness approach: enumerate all interfaces → identify conditions per interface → verify requirements exist for each condition. Formal INCOSE method. (Source: SRC-087; Confidence: HIGH)
2. Qualicen Scout uses n-gram + cosine similarity for duplicate detection in production — not transformer embeddings. Configurable threshold, no industry-standard default. (Source: SRC-083; Confidence: HIGH)
3. Transformer-based embeddings (sentence-transformers) outperform n-gram methods in NLP research but lack validation on requirements corpora specifically. (Source: SRC-088; Confidence: MEDIUM)
4. Structured annotation feedback pattern: { req_id, check_id, severity, message, suggestion }. Common in tools like SoftAudit and Jama Connect, though specific five-field schema is a design proposal. (Source: SRC-084, SRC-090; Confidence: MEDIUM)

**Prior Art:**
- Carson 1998 — Deterministic interface completeness (Source: SRC-087)
- Qualicen Scout — Production NLP duplicate detection with n-gram cosine similarity (Source: SRC-083)
- Jama Connect — Live Traceability with "suspect link" markers on changes (Source: SRC-090)
- SoftAudit — ~40-rule automated checker with structured deficiency reports (Source: SRC-084)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-026 | No authoritative cosine similarity threshold for requirements duplicate classification | Duplicate Detection | paper | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Interface Coverage Matrix | Mature | Deterministic; Carson 1998 grounded | Only checks interfaces | SRC-087 | HIGH |
| Embedding-Based Duplicate Detection | Emerging | Catches semantic duplicates | Threshold calibration needed; unproven on requirements corpora | SRC-088 | MEDIUM |
| Structured Annotation Feedback | Mature | Actionable; educational; closes author loop | Annotation schema needs design | SRC-084, SRC-090 | HIGH |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| Carson 1998 provides formal interface coverage method | VERIFIED | Three-step method confirmed from INCOSE symposium paper |
| Embeddings outperform n-grams for requirements | DISPUTED | Qualicen Scout (cited support) actually uses n-grams successfully in production |
| Structured annotation is "dominant pattern" | UNVERIFIED | Common pattern but specific five-field schema is a design proposal, not extracted standard |

---

## Block 9: Cross-Cutting Sweep

### Sub-Functions

1. **Cross-Cutting Category Prompting** — Prompts for system-level concerns: security, reliability, availability, scalability, maintainability, data integrity, logging/observability
2. **Full-Set C10-C15 Validation** — Checks completeness, consistency, feasibility, comprehensibility, validatability, correctness
3. **Problem Statement Coverage** — Verifies all PROBLEM-STATEMENT.md success criteria have at least one requirement
4. **Skeptic Review** — Skeptic agent verifies claims about coverage and completeness
5. **System-Level Requirement Registration** — Cross-cutting requirements go through standard Quality Checker → V&V → Trace path

### Research Findings

**Key Findings:**
1. ISO/IEC 25010:2023 defines 9 cross-cutting quality characteristics. Reasonable starting taxonomy but not exhaustive (arc42 critique notes missing terms). (Source: SRC-091; Confidence: HIGH)
2. MIL-STD-498 sections 3.7-3.16 enumerate cross-cutting categories as explicit specification sections (Safety, Security, Computer Resources, Quality Factors, Constraints, etc.). (Source: SRC-097; Confidence: HIGH)
3. Bidirectional traceability (needs → requirements) is the standard completeness mechanism. (Source: SRC-093; Confidence: HIGH)
4. Semantic goal-level completeness (verifying requirements actually SATISFY success criteria, not just that links exist) remains an open research problem. (GAP-030; Confidence: HIGH)

**Prior Art:**
- ISO 25010:2023 — 9 quality characteristics as sweep checklist (Source: SRC-091)
- MIL-STD-498 — 18 cross-cutting requirement paragraphs (Source: SRC-097)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-030 | No authoritative method for semantic goal-level completeness checking | Problem Statement Coverage | paper | Open |
| GAP-031 | INCOSE NRM Section 15 (management) content not retrieved | Full-Set Validation | standards_document | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| ISO 25010 Full Taxonomy (9 categories) | Mature | Standards-aligned; comprehensive | May overlap with block-level quality pass | SRC-091 | HIGH |
| Software-Focused Minimum Set (6 categories) | Novel | Focused; avoids overlap; domain-appropriate | Custom set without standards backing | SRC-092, SRC-097 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| ISO 25010 provides comprehensive taxonomy | VERIFIED | 9 characteristics confirmed; "comprehensive" slightly optimistic per arc42 critique |
| Traceability-based coverage verifies problem statement | VERIFIED | Standard mechanism; but link existence ≠ semantic satisfaction (GAP-030) |

---

## Block 10: Deliverable Assembly

### Sub-Functions

1. **Specification Document Generation** — REQUIREMENTS-SPECIFICATION.md organized by block then by type
2. **Traceability Matrix Generation** — TRACEABILITY-MATRIX.md: concept-dev source → need → requirement → V&V
3. **Verification Matrix Generation** — VERIFICATION-MATRIX.md: requirements × V&V method × success criteria
4. **Quality Summary** — Rules checked, violations resolved, TBD/TBR status, assumptions
5. **JSON Registry Export** — Machine-readable requirements_registry.json, needs_registry.json
6. **Per-Deliverable User Approval** — Section-by-section approval following concept-dev pattern

### Research Findings

**Key Findings:**
1. MIL-STD-498 SRS provides 18 requirement paragraphs (3.1-3.18) — among the most prescriptive publicly available general-purpose templates. IEEE 29148 is the current international standard. (Source: SRC-097, SRC-096; Confidence: HIGH)
2. Standard RTM columns: Requirement ID, Description, Test Case ID, Validation Status, Compliance Reference. Bidirectional is recommended. (Source: SRC-098; Confidence: MEDIUM)
3. NASA Verification Matrix: Only "shall" requirements included. Each entry: unique ID, source document, verification approach (AIDT). (Source: SRC-100; Confidence: HIGH)
4. concept-dev's section-by-section approval pattern with mandatory assumption review gate is directly reusable. Proven pattern in the same plugin ecosystem. (Source: SRC-107, SRC-108; Confidence: HIGH)

**Prior Art:**
- concept-dev /concept:document — Section-by-section generation with approval gates (Source: SRC-107)
- MIL-STD-498 SRS — 18-paragraph prescriptive template (Source: SRC-097)
- NASA Appendix D — Verification matrix format (Source: SRC-100)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-029 | Full IEEE 29148 SRS section hierarchy unverified from primary source | Spec Document Structure | standards_document | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| MIL-STD-498 SRS Structure | Mature | Prescriptive; comprehensive; public | Defense-oriented; verbose | SRC-097 | HIGH |
| Block-Centric Custom Structure | Novel | Matches plugin architecture; familiar to users | Non-standard | SRC-107 | MEDIUM |
| Hybrid: Block Body + MIL-STD-498 Cross-Cuts | Novel | Familiar structure with standards-aligned cross-cutting | More complex template | SRC-097, SRC-107 | HIGH |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| MIL-STD-498 is most prescriptive publicly available template | VERIFIED | With caveat: "among the most" — IEEE 29148 is current standard; MIL-STD-498 was canceled 1998 |
| concept-dev approval pattern is directly reusable | VERIFIED | Strongest claim — real codebase artifact with proven pattern |

---

## Block 11: Subsystem Decomposer

### Sub-Functions

1. **Decomposition Trigger** — After system-level deliverables, prompts whether to decompose any blocks
2. **Functional Decomposition** — Guides user through breaking a block into sub-blocks
3. **Allocation Rationale** — For each parent requirement: "Which sub-blocks does this allocate to? Why?"
4. **Allocation Coverage Validation** — Verifies every parent requirement allocates to at least one sub-block
5. **Sub-Block Relationship Diagram** — Creates ASCII diagram of sub-block relationships
6. **Decomposition Gate** — User approves before sub-blocks re-enter the core pipeline

### Research Findings

**Key Findings:**
1. NASA logical decomposition: 3 steps — (1) partition into sub-blocks, (2) allocate requirements with rationale, (3) capture decisions/assumptions. Terminates when requirements are "viable, verifiable, and internally consistent." (Source: SRC-102; Confidence: HIGH)
2. Requirements Allocation Sheet (RAS): DoD artifact with allocated requirements in measurable terms, traceability to originating requirement, and allocation rationale. (Source: SRC-105; Confidence: MEDIUM)
3. Re-entrant process is foundational SE principle: "System Definition processes are applied recursively" (SEBoK). Not a novel innovation. (Source: SRC-101; Confidence: HIGH)
4. Budgeting/apportionment is standard for quantitative requirements (mass, power, bandwidth, timing). For software: memory, CPU, bandwidth, response time. LLM cannot make these engineering judgments — user provides rationale. (Source: SRC-093; Confidence: HIGH)

**Prior Art:**
- NASA NPR 7120.5 — Formal recursive decomposition process (Source: SRC-102)
- DoD Requirements Allocation Sheet — Formal allocation artifact (Source: SRC-105)
- SEBoK System Definition — Recursive process application principle (Source: SRC-101)

### Gap Analysis

| Gap ID | Description | Required For | Needs | Status |
|--------|------------|-------------|-------|--------|
| GAP-027 | INCOSE NRM Section 6.4 exact content unverified (PDF 404) | Allocation Process | standards_document | Open |
| GAP-028 | DoD RAS column format unverified (paywalled) | Allocation Rationale | standards_document | Open |

### Solution Approaches

| Approach | Maturity | Pros | Cons | Sources | Confidence |
|----------|----------|------|------|---------|------------|
| Guided Decomposition with RAS | Mature | NASA-grounded; formal rationale; traceability | RAS unfamiliar to developers; overhead | SRC-102, SRC-105 | HIGH |
| Lightweight Decomposition with Re-Entry Gate | Novel | Lower overhead; concept-dev block definition pattern | Less rigorous allocation rationale | SRC-093, SRC-101 | MEDIUM |

### Skeptic Annotations

| Claim | Verdict | Note |
|-------|---------|------|
| Re-entrant process is foundational SE principle | VERIFIED | SEBoK, NASA both confirm recursive application |
| No AI tool implements re-entrant requirements passes | UNVERIFIED | Negative existence claim; softened to "no widely-known tool found" |
| Allocation requires budgeting for quantitative requirements | VERIFIED | Well-stated with honest limitation: LLM cannot make these judgments |

---

## Cross-Block Integration Gaps

| Gap | Blocks Involved | Description | Severity |
|-----|----------------|-------------|----------|
| GtWR v4 rule applicability at needs vs requirements level | Blocks 2, 4 | Appendix D needed to determine which rules apply to needs formalization vs requirements quality checking | High |
| Attribute numbering and mandatory count | Blocks 3, 6, 7 | "13 mandatory attributes" unverifiable from public sources; attribute numbering (A6 vs A08) is likely zero-padding but needs primary text confirmation | Medium |
| Interaction volume scalability | Blocks 3, 6 | 13+ attributes per requirement × 10+ requirements per block = 130+ attribute values. Metered questioning (3-4 per batch) may require 30+ rounds per block | High |
| Cross-cutting requirements in block-centric structure | Blocks 8, 9 | System-level cross-cutting requirements (security, reliability) don't belong to a single block; tracking mechanism needed | Medium |
| Decomposition level tracking | Blocks 7, 11 | State mechanism must track current decomposition level to prevent infinite regress in re-entrant pipeline | Low |

---

## Unresolved Questions

1. **Block 2:** Do you have access to GtWR v4 full document? Appendix D (Rule Applicability Matrix) is critical for determining which rules apply at needs level.
2. **Block 3:** Can you confirm "13 mandatory" starred attributes from your copy of GtWR v4?
3. **Block 3:** For attribute elicitation: metered questioning (15-20+ rounds) or batch-fill-then-review (LLM pre-fills, user corrects)?
4. **Block 3:** Should interface be folded into the functional pass per GtWR v4 guidance, or kept separate for visibility?
5. **Block 4:** GtWR version target: v3 (41 rules) or v4 (42 rules per reqi.io, 44 per QRA Corp)?
6. **Block 5:** Should TPM research trigger for every measurable requirement or only user-designated critical ones?
7. **Block 5:** How to handle evidence quality for business impact data? (quality ratings, controlled experiments only, or ranges with confidence?)
8. **Block 9:** Minimum viable cross-cutting category set: ISO 25010 full (9) or software-focused subset (6)?
9. **Block 10:** Specification document structure: MIL-STD-498, block-centric custom, or hybrid?
10. **Block 11:** Decomposition stopping condition: user-specified, leaf-level blocks, or atomic requirements?

---

## Source Coverage Summary

| Confidence | Sources |
|-----------|---------|
| HIGH | 56 |
| MEDIUM | 52 |
| LOW | 0 |
| UNGROUNDED | 0 |

Total sources: 108
Total gaps: 31 (all open)

---

## Assumptions Added This Phase

No new assumptions were registered during the drilldown phase. The 10 existing assumptions (A-001 through A-010) from spitball, problem, and blackbox phases remain pending.

Notable skeptic findings that may warrant new assumptions:
- The "~24 of 42" automatable rules claim (A-001) has a rule count discrepancy (42 vs 44) that should be resolved
- Fixed type ordering (A-009) lacks empirical backing; counter-evidence from LLMREI research
- Interaction volume for attribute elicitation (15-20+ rounds per block) is unvalidated

---

**Next Phase:** Document Generation (`/concept:document`)
