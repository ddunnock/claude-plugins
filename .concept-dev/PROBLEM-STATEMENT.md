# Problem Statement — Requirements Development Plugin (requirements-dev)

**Session:** 1f45143f
**Date:** 2026-02-20
**Phase:** Problem Definition (Phase 2)

---

## The Problem

Solo developers and small teams who complete concept development lack a structured, AI-assisted path to transform their concept artifacts into INCOSE-compliant needs and requirements. Without this intermediate step, they either jump directly to system design and implementation — or rely on spec-driven AI tools that conflate specifications with requirements, bypassing the formal needs-to-requirements transformation that INCOSE identifies as foundational.

This creates two compounding problems: solution decisions cannot be evaluated against explicit, verifiable criteria, and there is no traceability chain from stakeholder needs through to validation methods. INCOSE's requirements development practices address both problems but are inaccessible to small teams without dedicated systems engineering support. An AI-assisted requirements development skill — integrated into the concept-dev pipeline and calibrated for software-only systems — would make SE-grade requirements discipline practical for teams that currently skip this step entirely.

---

## Current State

After completing concept development (via the concept-dev skill or equivalent), teams have well-researched concept documents, functional architectures, and solution landscapes. However, no structured follow-on process exists to transform these into formal requirements. The current approaches are:

- **Jump to implementation:** Teams go directly from concept to code, treating the concept document as an informal guide rather than a formal input to requirements definition. Requirements are implicit, embedded in code and user stories.
- **Spec-driven AI tools:** Tools like GSD and spec-kit generate specifications that define *what to build* (solutions) rather than *what the system must do* (requirements). They skip the needs-to-requirements transformation, conflating specification with requirement.
- **Ad-hoc requirements lists:** Some teams write informal requirement lists without structured attributes, traceability, or quality checking. These lack the rigor needed for systematic V&V planning.
- **No V&V planning upfront:** Verification and validation strategies are deferred until testing phase, leading to untestable or poorly testable requirements.
- **No grounded performance targets:** When performance requirements are written, target values are arbitrary rather than informed by researched baselines and comparable benchmarks.

---

## Consequences

| Consequence | Impact | Affected Stakeholders |
|-------------|--------|----------------------|
| Sub-optimal solution selection | Solutions chosen without explicit evaluation criteria; no way to compare alternatives against requirements | Developers, end users |
| Missed stakeholder needs | Needs not formally traced through to verifiable requirements; gaps discovered late in development | End users, product owners |
| Untestable features | No V&V criteria defined upfront; test planning becomes reactive rather than proactive | Developers, QA |
| Arbitrary performance targets | Performance requirements set without grounded baselines; targets may be unachievable or insufficiently ambitious | Developers, end users |
| Lost concept rigor | Investment in structured concept development (source-grounded research, skeptic-verified claims, assumption tracking) not carried forward | All stakeholders |
| Scope creep | Without formal scope boundaries defined by requirements, feature additions go unchecked against original needs | Developers, product owners |

---

## Desired State

Teams completing requirements-dev have:

- A comprehensive, formally structured set of stakeholder needs extracted and formalized from concept-dev outputs
- A complete set of design input requirements transformed from needs, organized by type (functional, performance, interface/API, constraint, quality), each with INCOSE-mandated attributes
- Per-requirement V&V strategy with method, success criteria, and responsible party — providing the starting point for systematic validation
- Bidirectional traceability from stakeholder needs through requirements to V&V methods, with machine-readable JSON registries
- Quality-checked requirements with specific INCOSE GtWR rule violations flagged and addressed
- Grounded performance targets informed by researched baselines, comparable benchmarks, and documented consequences
- Optional subsystem-level decomposition with full rigor when needed
- All artifacts structured as inputs to a downstream system-design skill

---

## Stakeholders

| Stakeholder | Role | How Affected | Priority Need |
|-------------|------|-------------|---------------|
| Solo developer | Primary user | Currently skips requirements or writes ad-hoc lists | Guided, conversational process that produces SE-grade requirements without requiring SE expertise |
| Small team (2-5) | Primary user | Lacks dedicated SE support; requirements are informal | Structured requirements that the whole team can reference and trace |
| Future system-design skill | Downstream consumer | Needs well-formed requirements as input | Complete, traceable, attribute-rich requirements with V&V criteria |
| End users of developed software | Indirect beneficiary | Needs may be missed without formal traceability | Assurance that requirements trace back to their stated needs |

---

## Scope

### In Scope
- Needs extraction from concept-dev outputs (CONCEPT-DOCUMENT, BLACKBOX, SOLUTION-LANDSCAPE, registries)
- Formal transformation of needs into design input requirements following INCOSE practices
- INCOSE GtWR v4 quality checking using assist-and-flag model (~24 syntactic rules automated, semantic rules LLM-assisted with human review)
- V&V strategy planning per requirement (method, success criteria, responsible party)
- Bidirectional traceability (needs <-> requirements <-> V&V) with JSON registries
- Optional subsystem decomposition with dedicated command, agent, and gate checks
- Research-assisted TPM guidance with grounded baselines, comparable benchmarks, and consequence/effect descriptions
- Session resume functionality (adapted from concept-dev pattern)
- JSON requirements registry extending concept-dev's registry pattern
- Tiered research tools (WebSearch, WebFetch, crawl4ai, MCP tiers — same detection as concept-dev)
- Software-only systems focus
- 13 mandatory INCOSE attributes per requirement; remaining attributes optional
- TBD/TBR tracking for unresolved items from concept-dev gaps

### Out of Scope
- System design (next skill in pipeline — requirements-dev produces all necessary inputs)
- Hardware/mixed-system requirements
- Integration with external RM tools (DOORS, Jama, Innoslate)
- Code or test generation

---

## Design Influences

Proven patterns from existing tools that will inform the design:

| Influence | Source | Pattern to Adopt |
|-----------|--------|-----------------|
| Rule-by-rule quality checking | QVscribe (QRA Corp) | Encode each automatable INCOSE rule as a discrete check; ~24 syntactic rules automated, semantic rules as LLM-assisted flags for human review |
| Attribute-based requirement data model | Innoslate (SPEC Innovations) | Each requirement as a structured object with rationale, parent trace, source trace, V&V method, priority, risk — not just a text string |
| Spec-driven approach (counter-example) | GSD, spec-kit | These define solutions, not requirements. Requirements-dev explicitly separates the two, maintaining solution-free requirements through Phase 2 |

---

## Constraints

| Constraint | Type | Details |
|-----------|------|---------|
| Must chain from concept-dev outputs | Technical | Reads .concept-dev/ artifacts; does not modify them |
| LLM quality checking limitations | Technical | ~24 of 42 INCOSE rules automatable; semantic rules need human review; must frame as assist-and-flag, not autonomous scoring |
| Solo/small team context | Organizational | Process must be completable by individuals without SE expertise; guided and conversational |
| Single sitting or continuable | Schedule | Must support session persistence; no context/quality loss between sessions |
| Software-only domain | Technical | Hardware-specific attributes (weight, environmental) marked N/A; API/interface focus |

---

## Success Criteria

1. A completed requirements-dev session produces a structured requirements specification with all mandatory INCOSE attributes populated for each requirement
2. Every requirement traces bidirectionally: up to a stakeholder need (from concept-dev) and forward to a V&V method
3. Requirements pass quality checking against automatable INCOSE GtWR rules with specific violations flagged and resolved
4. Performance and measurable requirements have grounded baseline values with cited sources
5. The output artifacts contain all necessary inputs for a downstream system-design skill (minus user-provided design decisions)
6. A solo developer can complete the process in a single sitting for a moderately complex system, or resume across sessions without quality loss

---

## Deferred Solution Ideas

| # | Solution Idea | Captured During | Notes |
|---|--------------|-----------------|-------|
| 1 | concept-dev's /concept:resume pattern for session continuability | Batch 2 Q3 | Proven pattern; adapt for requirements-dev |
| 2 | Concept-dev's source_registry and assumption_registry patterns | Batch 1 Q1 | Extend with requirements_registry.json |
| 3 | WebSearch/crawl4ai for TPM baseline research | Batch 2 revision | Same tiered tool strategy as concept-dev |

---

## Assumptions

| ID | Assumption | Category | Impact if Wrong |
|----|-----------|----------|-----------------|
| A-001 | LLM-based INCOSE rule checking can reliably automate ~24 of 42 syntactic rules; remaining semantic rules require human review | feasibility | Quality checking would need to be fully manual; reduces the value proposition of AI assistance |
| A-002 | Concept-dev outputs provide sufficient starting material to seed INCOSE-compliant needs and requirements with user refinement | feasibility | Would need additional elicitation phases or external inputs before requirements can begin |
| A-003 | Subsystem decomposition and allocation can be scaffolded by an LLM with guided prompts, but engineering judgment for budgeting and allocation rationale must come from the user | feasibility | Over-automation would produce unreliable decompositions; under-scaffolding would leave users without guidance |
| A-004 | Software-only focus is compatible with INCOSE practices without significant adaptation | feasibility | Would need custom adaptation of INCOSE practices for software domain; some attributes may not translate |
| A-005 | Solo developers and small teams will accept INCOSE-level rigor if the process is guided and conversational | stakeholder | Target audience may find the process too heavyweight; would need to simplify or make phases more optional |
| A-006 | The requirements-dev output will provide sufficient input for a downstream system-design skill | scope | System-design skill may require additional inputs not captured during requirements development |
| A-007 | Research-assisted TPM guidance with grounded baselines is more valuable than arbitrary developer-chosen targets | domain_knowledge | Developers may prefer setting their own targets without research overhead |

---

**Next Phase:** Black-Box Architecture (`/concept:blackbox`)
