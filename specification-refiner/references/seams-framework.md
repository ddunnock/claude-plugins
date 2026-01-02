# SEAMS Framework - Detailed Reference

Comprehensive guide for applying the SEAMS gap analysis methodology.

## Table of Contents
- [S - Structure Analysis](#s---structure-analysis)
  - [Completeness Checks](#completeness-checks)
  - [Cohesion Assessment](#cohesion-assessment)
  - [Coupling Analysis](#coupling-analysis)
  - [Boundary Clarity](#boundary-clarity)
- [E - Execution Path Analysis](#e---execution-path-analysis)
  - [Happy Path Validation](#happy-path-validation)
  - [Edge Case Catalog](#edge-case-catalog)
  - [Failure Mode Analysis](#failure-mode-analysis)
  - [Recovery Assessment](#recovery-assessment)
- [A - Assumption Inventory](#a---assumption-inventory)
  - [Technical Assumptions](#technical-assumptions)
  - [Organizational Assumptions](#organizational-assumptions)
  - [Environmental Assumptions](#environmental-assumptions)
  - [Assumption Validation Template](#assumption-validation-template)
- [M - Mismatch Detection](#m---mismatch-detection)
  - [Requirements ↔ Design Traceability](#requirements--design-traceability)
  - [Design ↔ Implementation Drift](#design--implementation-drift)
  - [Documentation ↔ Reality](#documentation--reality)
- [S - Stakeholder Perspectives](#s---stakeholder-perspectives)
  - [Operator View](#operator-view)
  - [Security View](#security-view)
  - [Integrator View](#integrator-view)
  - [End User View](#end-user-view)
  - [Future Maintainer View](#future-maintainer-view)

---

## S - Structure Analysis

Evaluate architecture and design integrity.

### Completeness Checks

| Check | What to Look For |
|-------|------------------|
| Input Coverage | Every expected input has a defined handler |
| Output Mapping | Every required output has a generation path |
| Interface Specs | All component boundaries have defined contracts |
| Error Paths | Every operation has failure handling specified |

### Cohesion Assessment

**High Cohesion (Good)**:
- Component has single, clear responsibility
- All methods/functions relate to core purpose
- Name accurately describes what it does

**Low Cohesion (Problem)**:
- Component does multiple unrelated things
- "And" in the description suggests split needed
- Utility grab-bag with no unifying theme

### Coupling Analysis

Build dependency matrix:

```
          A    B    C    D
     A    -    X    X    
     B    X    -         X
     C              -    X
     D         X    X    -
```

- Dense clusters = high coupling risk
- Empty rows/columns = potentially orphaned
- Circular dependencies = architectural smell

### Boundary Clarity

Questions to answer:
1. Where does responsibility for X begin and end?
2. Who owns the data at this interface?
3. What happens when component A wants to access component B's internals?
4. Are there implicit dependencies not captured in the architecture?

## E - Execution Path Analysis

### Happy Path Validation

For each major use case:
1. Identify entry point
2. Trace every step to completion
3. Verify each handoff has defined protocol
4. Confirm success criteria are specified

### Edge Case Catalog

| Category | Examples to Check |
|----------|-------------------|
| Boundaries | Zero, one, max, max+1 values |
| Empty states | No data, no users, no history |
| Concurrency | Simultaneous operations, race conditions |
| Timing | Timeout, slow network, clock skew |
| Resource | Disk full, memory pressure, connection pool exhausted |

### Failure Mode Analysis

For each component, ask:
- What if it fails silently (no error signal)?
- What if it fails loudly (exception/crash)?
- What if it fails partially (some operations succeed)?
- What if it hangs (no response at all)?

### Recovery Assessment

| Recovery Type | Criteria |
|---------------|----------|
| Self-healing | System returns to normal without intervention |
| Graceful degradation | Reduced function but stable |
| Manual recovery | Documented procedure, tested |
| Catastrophic | No defined recovery path |

## A - Assumption Inventory

### Technical Assumptions

| Domain | Example Assumptions |
|--------|---------------------|
| Infrastructure | "Kubernetes is available", "Network latency < 50ms" |
| Dependencies | "Library X supports feature Y", "API version 2.0 deployed" |
| Data | "Records fit in memory", "IDs are unique", "UTF-8 encoding" |
| Performance | "Peak load is 1000 RPS", "Response time < 200ms acceptable" |

### Organizational Assumptions

| Domain | Example Assumptions |
|--------|---------------------|
| Skills | "Team knows Rust", "DevOps can manage K8s" |
| Process | "CI/CD pipeline exists", "Code reviews happen" |
| Authority | "We can modify the database schema", "API changes approved" |
| Resources | "Two developers available", "Budget for cloud hosting" |

### Environmental Assumptions

| Domain | Example Assumptions |
|--------|---------------------|
| Security | "VPN required for access", "Secrets managed externally" |
| Compliance | "GDPR applies", "Data residency in EU" |
| Integration | "Third-party API stable", "Legacy system continues operating" |
| Timeline | "Feature X available by Q2", "Migration window exists" |

### Assumption Validation Template

For each critical assumption:
```markdown
**Assumption**: [Statement]
**Category**: Technical / Organizational / Environmental
**Risk if false**: [What breaks]
**Validation method**: [How to verify]
**Status**: Unverified / Confirmed / Invalidated
**Notes**: [Any context]
```

## M - Mismatch Detection

### Requirements ↔ Design Traceability

Create mapping table:
| Requirement ID | Design Element | Coverage | Notes |
|----------------|----------------|----------|-------|
| REQ-001 | Component A.method() | Full | |
| REQ-002 | Component B | Partial | Missing error case |
| REQ-003 | ??? | None | Not addressed |

**Gap indicators**:
- Requirements with no design coverage
- Design elements with no requirement source (gold-plating)
- Partial coverage without documented decision

### Design ↔ Implementation Drift

Common drift patterns:
- Shortcuts taken during implementation
- "Temporary" solutions that persisted
- Features added without design update
- Deprecated approaches still in use

### Documentation ↔ Reality

| Document | Reality Check |
|----------|---------------|
| Architecture diagram | Does deployed system match? |
| API documentation | Do endpoints work as documented? |
| Configuration guide | Are default values current? |
| Runbook | Has someone actually followed it recently? |

## S - Stakeholder Perspectives

### Operator View

Questions an operator would ask:
- How do I know if this is healthy?
- How do I troubleshoot when it's not?
- What are the common failure modes and fixes?
- Where do I look for logs/metrics?
- What manual interventions might I need?

### Security View

Questions a security reviewer would ask:
- What's the attack surface?
- Where is authentication/authorization enforced?
- What data is sensitive and how is it protected?
- What happens if credentials are compromised?
- Is there audit logging?

### Integrator View

Questions someone integrating this would ask:
- What are the exact API contracts?
- What are the SLAs (latency, availability)?
- How do I test against this safely?
- What versioning strategy is used?
- How will breaking changes be communicated?

### End User View

Questions an end user would ask:
- Does this solve my actual problem?
- Is it obvious how to accomplish my goal?
- What happens when I make a mistake?
- How do I get help?

### Future Maintainer View

Questions someone inheriting this would ask:
- Why was this built this way?
- What are the known limitations?
- Where are the dragons (fragile areas)?
- What would I need to understand to modify this safely?
