# Research Checklist

Comprehensive checklist for systematic research and opportunity investigation.

---

## Phase 1: Research Scoping Checklist

### Target Definition
```
□ Target name clearly identified
□ Target type classified (IDE/Protocol/Framework/Tool)
□ Primary URL/repository documented
□ Target's core problem domain understood
```

### Objectives
```
□ Primary goal articulated
□ Specific research questions defined (3-5 questions)
□ Success criteria established (measurable outcomes)
```

### ACP Integration Focus
```
□ Integration type identified:
  □ Gap-filling opportunity
  □ Protocol integration
  □ Collaboration opportunity
  □ Competitive analysis
  □ Other (specified)
```

### Constraints
```
□ Out-of-scope areas documented
□ Timeline constraints noted
□ Resource constraints noted
□ Competing priorities identified
```

### Gate Verification
```
□ User has reviewed scope definition
□ User has confirmed scope is correct
□ User has approved proceeding to discovery
```

---

## Phase 2: Discovery & Collection Checklist

### Tier 1 - Primary Sources (MUST search)
```
□ Official documentation site found and catalogued
□ GitHub/GitLab repository identified
□ Official announcements/blog posts searched
□ API/Protocol specifications located (if applicable)
```

### Tier 2 - Secondary Sources (SHOULD search)
```
□ Technical blog posts from team members
□ Conference talks/presentations
□ Community discussions (Discord, Slack, Forums)
□ Integration guides from partners
```

### Tier 3 - Tertiary Sources (MAY search)
```
□ Third-party reviews and analyses
□ Comparison articles
□ Issue tracker discussions
□ Social media announcements
```

### Source Registration
```
□ All sources assigned [SRC-XXX] identifiers
□ Each source has:
  □ URL documented
  □ Type classified (documentation/source_code/announcement/etc.)
  □ Access date recorded
  □ Relevance rated (HIGH/MEDIUM/LOW)
  □ Key sections/files noted
```

### Source Gaps
```
□ Missing information areas identified
□ Gap impact on analysis assessed
□ Alternative sources for gaps explored
```

### Gate Verification
```
□ Source registry presented to user
□ User confirmed source coverage is sufficient
□ User approved proceeding to analysis
```

---

## Phase 3: Deep Analysis Checklist

### Technical Architecture
```
□ Core components identified
□ Data flow mapped
□ Key abstractions documented
□ All claims cite specific sources [SRC-XXX]
```

### Protocol/API Design (if applicable)
```
□ Communication pattern identified (request-response/streaming/event-driven)
□ Data format documented (JSON/Protocol Buffers/Other)
□ Transport mechanism noted (HTTP/WebSocket/IPC/Other)
□ Key endpoints/methods catalogued
```

### Extension Points
```
□ Plugin/extension mechanisms identified
□ Integration patterns documented
□ Customization options noted
```

### Feature Mapping
```
□ Feature comparison matrix created
□ Target capabilities documented
□ ACP capabilities mapped
□ Gaps/overlaps identified
```

### Gap Identification
```
□ Each gap assigned [GAP-XXX] identifier
□ Each gap has:
  □ Target status documented
  □ ACP capability mapped
  □ Integration potential rated
  □ Evidence cited [SRC-XXX]
```

### Evidence Grounding
```
□ All claims categorized:
  □ [VERIFIED] - confirmed from primary source
  □ [INFERRED] - logically derived
  □ [ASSUMED] - needs user confirmation
  □ [UNGROUNDED] - cannot verify
```

### Gate Verification
```
□ Analysis presented to user
□ User confirmed analysis accuracy
□ User approved proceeding to ACP summary
```

---

## Phase 4: ACP Context Summary Checklist

### Specification Overview
```
□ Current ACP version documented
□ Relevant spec chapters identified and summarized:
  □ 01-introduction.md
  □ 03-cache-format.md
  □ 04-config-format.md
  □ 05-annotations.md
  □ 06-constraints.md
  □ [Additional relevant chapters]
```

### Existing RFCs
```
□ All existing RFCs catalogued:
  □ RFC-001: Self-Documenting Annotations
  □ RFC-002: Documentation References
  □ RFC-003: Annotation Provenance
  □ [Additional RFCs]
□ Each RFC has:
  □ Status documented
  □ Summary provided
  □ Key changes noted
  □ Relevance to research explained
```

### Schema Inventory
```
□ All schemas catalogued:
  □ cache.schema.json
  □ config.schema.json
  □ vars.schema.json
  □ sync.schema.json
  □ [Additional schemas]
□ Each schema has:
  □ Purpose documented
  □ Key fields noted
```

### Integration Points
```
□ Existing integration mechanisms documented:
  □ MCP Integration (acp-mcp)
  □ CLI Interface (acp-cli)
  □ LSP Planning (acp-lsp)
□ Extension points for external protocols identified
```

### Design Principles
```
□ Core principles extracted from spec:
  □ Self-documenting annotations
  □ Token efficiency
  □ Deterministic constraints
  □ Language-agnostic syntax
  □ Progressive disclosure
□ Compatibility requirements documented:
  □ Backward compatibility policy
  □ Versioning approach
  □ RFC process requirements
```

### Gate Verification
```
□ ACP summary document created
□ User has reviewed summary
□ User has approved summary
□ User confirmed proceeding to opportunity assessment
```

---

## Phase 5: Opportunity Assessment Checklist

### Gap Analysis
```
□ All gaps from Phase 3 reviewed
□ Each gap assessed for:
  □ Strategic value (HIGH/MEDIUM/LOW)
  □ Implementation effort (HIGH/MEDIUM/LOW)
  □ Evidence grounding
```

### Collaboration Opportunities
```
□ Each opportunity assigned [OPP-XXX] identifier
□ Each opportunity has:
  □ Description
  □ Mutual benefit analysis
  □ Required changes (ACP side)
  □ Required changes (Target side)
  □ Feasibility rating
  □ Evidence citation
```

### Risk Assessment
```
□ Risks identified and assigned [RISK-XXX] identifiers
□ Each risk has:
  □ Description
  □ Likelihood rating
  □ Impact rating
  □ Mitigation strategy
```

### Recommendations
```
□ Clear recommendation provided:
  □ Opportunities to pursue
  □ Items to defer (with rationale)
  □ Items to decline (with rationale)
```

### Gate Verification
```
□ Opportunity assessment presented to user
□ User confirmed assessment accuracy
□ User approved which opportunities to pursue
□ User confirmed proceeding to RFC generation
```

---

## Phase 6: RFC Generation Checklist

### RFC Structure (per references/rfc-template.md)
```
□ Header with all required fields
□ Summary (2-3 sentences)
□ Motivation with:
  □ Problem statement
  □ Research basis with sources
  □ Gap analysis with IDs
□ Specification with:
  □ Affected components table
  □ Detailed changes with existing/proposed state
  □ Rationale for each change
□ Backward compatibility:
  □ Breaking changes (or "None")
  □ Migration path (if needed)
  □ Deprecation schedule (if any)
□ Implementation:
  □ Reference implementation approach
  □ Test cases table
□ Alternatives considered (at least 2)
□ Security considerations
□ References with access dates
```

### Validation Against ACP Summary
```
□ RFC does not conflict with existing RFCs
□ RFC is consistent with ACP design principles
□ All affected spec sections referenced correctly
□ Schema changes are compatible
```

### Gate Verification
```
□ RFC draft presented to user
□ User reviewed all sections
□ User approved RFC content
□ User confirmed RFC is ready for final packaging
```

---

## Phase 7: Deliverables Packaging Checklist

### Research Deliverables
```
□ research-summary-[target]-[date].md created:
  □ Complete research findings
  □ All sources catalogued
  □ Technical analysis complete
□ gap-analysis-[target]-[date].md created:
  □ All gaps with IDs
  □ Opportunity assessment
  □ Recommendations
```

### ACP Context Deliverables
```
□ acp-summary-[date].md created:
  □ RFCs summarized
  □ Schemas inventoried
  □ Spec chapters mapped
  □ Integration points identified
```

### RFC Deliverables
```
□ RFC-XXXX-[title].md created:
  □ Complete per template
  □ Validated against ACP summary
  □ All sections complete
```

### Quality Verification
```
□ All sources cited with [SRC-XXX] format
□ No ungrounded claims remain
□ All assumptions marked as [ASSUMED]
□ User approved each phase gate
□ RFC traces to existing specification
□ All deliverables presented to user
□ User confirmed all deliverables complete
```

---

## Final Sign-Off

```
═══════════════════════════════════════════════════════════════════════════════
RESEARCH COMPLETION VERIFICATION
═══════════════════════════════════════════════════════════════════════════════

Research Target: ______________________________
Research Date: ________________________________
Researcher: ___________________________________

PHASE COMPLETION:
  □ Phase 1: Research Scoping - COMPLETE
  □ Phase 2: Discovery & Collection - COMPLETE
  □ Phase 3: Deep Analysis - COMPLETE
  □ Phase 4: ACP Context Summary - COMPLETE
  □ Phase 5: Opportunity Assessment - COMPLETE
  □ Phase 6: RFC Generation - COMPLETE
  □ Phase 7: Deliverables Packaging - COMPLETE

DELIVERABLES:
  □ Research Summary Document
  □ Gap Analysis Report
  □ ACP Context Summary
  □ RFC Proposal(s)

USER SIGN-OFF:
  □ User has reviewed all deliverables
  □ User has approved all deliverables
  □ Research investigation is COMPLETE

═══════════════════════════════════════════════════════════════════════════════
```
