---
name: documentation-architect
description: Transform documentation from any starting point (nothing, scattered notes, or complete docs) into professional, comprehensive documentation packages using the Diátaxis framework. Use when the user wants to create documentation from scratch, reorganize existing docs, assess documentation quality, migrate to Diátaxis structure, or build marketable documentation. Supports discovery Q&A, web research, file uploads, GitHub repo syncing, and handles AI context limits through intelligent chunking with source references. Includes strict guardrails for source verification, assumption approval, and quality gates.
---

# Documentation Architect

Create comprehensive, professional documentation packages organized around user needs using the Diátaxis framework. Works with any starting point: greenfield projects, scattered notes, or existing documentation requiring reorganization.

## Critical: Read GUARDRAILS.md First

Before proceeding with any phase, Claude **MUST** read and internalize the behavioral constraints defined in `GUARDRAILS.md`. These guardrails are **non-negotiable** and govern all interactions.

**Key Guardrails Summary** (12 total):

| # | Guardrail | Enforcement |
|---|-----------|-------------|
| 1 | NO ASSUMPTIONS WITHOUT APPROVAL | Every inference requires user confirmation |
| 2 | NO PROCEEDING WITHOUT CONFIRMATION | Phase gates block automatic progression |
| 3 | ALL CONTENT MUST BE SOURCE-GROUNDED | Every claim cites its source |
| 4 | MANDATORY CLARIFYING QUESTIONS | Ask before assuming |
| 5 | MANDATORY QUALITY GATES | Thresholds must be met before delivery |
| 6 | MANDATORY SOURCE REGISTRATION | No content without registered sources |
| 7 | MANDATORY SESSION STATE | Preserve state for resumption |
| 8 | NO OPINIONS WITHOUT BASIS | Recommendations require evidence |
| 9 | **MANDATORY DOCUMENT REVIEW LOOP** | Every document individually reviewed |
| 10 | **MANDATORY CHANGE LOGGING** | Every change logged to change-log.md |
| 11 | **MANDATORY CASCADE ANALYSIS** | Cross-document impact always assessed |
| 12 | **MANDATORY MEMORY FILE UPDATES** | All memory files kept current |

See `GUARDRAILS.md` for complete behavioral requirements.

---

## Normative Language

This skill uses RFC 2119 terminology:
- **MUST**: Absolute requirement—violation breaks the process
- **MUST NOT**: Absolute prohibition—violation breaks the process
- **SHOULD**: Strongly recommended—deviation requires explicit justification
- **SHOULD NOT**: Discouraged—use only with documented rationale
- **MAY**: Optional—user preference determines behavior

---

## Overview

This skill guides you through a systematic process to:
- Discover and understand documentation requirements
- Inventory and assess existing documentation  
- Organize content using the Diátaxis four-quadrant framework
- Handle AI context limits through intelligent chunking with source tracking
- Produce professional, marketable documentation

## Quick Start: Which Path?

```
Input Assessment:
├─ No existing docs → START: Phase 1 (Full Discovery)
├─ Scattered notes/files → START: Phase 1 (Focused Discovery) + Phase 2 (Inventory)
├─ Existing docs needing reorg → START: Phase 2 (Inventory) + Phase 3 (Analysis)
└─ Docs needing enhancement → START: Phase 3 (Analysis) + Phase 4 (Gap Planning)
```

## The Diátaxis Framework

Diátaxis organizes documentation around four user needs:

```
                    PRACTICAL                      THEORETICAL
              ┌─────────────────────────────┬─────────────────────────────┐
              │                             │                             │
   LEARNING   │      TUTORIALS              │      EXPLANATION            │
              │                             │                             │
              │  Learning-oriented          │  Understanding-oriented     │
              │  Lessons                    │  Discussions                │
              │  "Help me learn"            │  "Help me understand why"   │
              │                             │                             │
              ├─────────────────────────────┼─────────────────────────────┤
              │                             │                             │
   WORKING    │      HOW-TO GUIDES          │      REFERENCE              │
              │                             │                             │
              │  Goal-oriented              │  Information-oriented       │
              │  Directions                 │  Technical descriptions     │
              │  "Help me do X"             │  "Give me the facts"        │
              │                             │                             │
              └─────────────────────────────┴─────────────────────────────┘
```

See `references/diataxis-framework.md` for detailed guidance on each quadrant.

---

## Phase 1: Discovery

### 1.1 Determine Starting Point

Claude **MUST** ask these questions to classify the project (2-3 per message maximum):

**Project Scope (MUST ask all)**:
- What is this project/product about?
- Who are the primary audiences (users, developers, operators, decision-makers)?
- What's the current state of documentation (none, scattered, existing structure)?

**Source Material (MUST ask all)**:
- Are there files to upload or analyze?
- Is there a GitHub repository to sync?
- Are there existing docs websites to reference?

**Deliverable Goals (SHOULD ask)**:
- What documentation deliverables are needed (website, README, API docs, guides)?
- What makes this documentation "successful"?
- Should we research similar projects for patterns?

Claude **MUST NOT** proceed to Phase 2 until user has answered all MUST questions.

### 1.2 Gather Source Materials

Based on discovery, Claude **MUST** collect inputs using appropriate methods:

| Input Type | Collection Method | Requirement |
|------------|-------------------|-------------|
| Uploaded files | Inventory files in `/mnt/user-data/uploads` | MUST inventory before proceeding |
| GitHub repo | Clone and analyze: `git clone <repo-url>` | MUST verify accessibility |
| Web research | Use web search for patterns, competitors | SHOULD research if domain unfamiliar |
| Verbal description | Structured elicitation questions | MUST document in source registry |
| Existing docs site | Fetch and analyze key pages | MUST capture structure |

### 1.3 Research & Benchmarking

For projects with competitors or prior art, Claude **SHOULD** conduct research:

```bash
# Generate research template
python scripts/doc_research.py "<domain>" --output research-notes.md
```

Claude **MUST** then execute web searches and fill in the template.

**Research Checklist**:
- [ ] Search: `"<domain>" documentation best practices`
- [ ] Search: `"<domain>" getting started guide`
- [ ] Find 2-3 exemplar documentation sites in the domain
- [ ] Note structural patterns, navigation, content types

Claude **MUST** mark all findings with evidence grounding:
- `[VERIFIED: <url>]` - Confirmed from source
- `[INFERRED: <url>]` - Reasonable inference from patterns
- `[ASSUMPTION]` - Requires user validation before use

### Phase Gate: Discovery Complete

```markdown
## Phase Gate: Discovery

### Completed Items
- [ ] Project scope defined
- [ ] Primary audiences identified
- [ ] Current documentation state assessed
- [ ] Source materials identified
- [ ] Research conducted (if applicable)

### Sources Identified
| ID | Name | Type | Status |
|----|------|------|--------|
| [SRC-01] | [name] | [type] | [Pending/Accessible] |

### Assumptions Requiring Approval
[List any assumptions made during discovery]

---

**I will NOT proceed until you respond:**

[A] ✅ Approved - proceed to Phase 2 (Inventory)
[B] 🔄 Need changes - specify modifications
[C] ⏸️ Pause - save state for later
```

---

## Phase 2: Inventory

### 2.1 Source Registration

Claude **MUST** register all sources before analysis:

```markdown
## Source Registry

| ID | Name | Location | Type | Token Est. | Status |
|----|------|----------|------|------------|--------|
| SRC-01 | | | | | |
```

Claude **MUST NOT** generate content for topics without registered sources.

### 2.2 Document Catalog

Claude **MUST** create a comprehensive inventory of existing materials:

```markdown
## Documentation Inventory

### Source: [Source Name/Location]

| Document | Type | Status | Diátaxis Quadrant | Notes |
|----------|------|--------|-------------------|-------|
| [file/page] | [md/html/pdf/code] | [current/outdated/stub] | [T/H/R/E/Mixed] | [observations] |

### Key Observations
- [Pattern 1]
- [Gap 1]
```

### 2.3 Content Extraction Strategy

For large codebases or doc sets, Claude **MUST** use the chunking strategy:

```bash
# Analyze documentation structure
python scripts/analyze_docs.py <source-dir> --output inventory.json
```

**Chunking Principles** (see `references/chunking-strategy.md`):
1. Claude **MUST** create index notes that reference source locations
2. Claude **MUST** process in logical units (chapters, sections, features)
3. Claude **MUST** maintain source traceability for every extracted insight
4. Claude **SHOULD** keep chunks under 8,000 tokens for reliable processing

### 2.4 Source Reference Format

For every piece of source material, Claude **MUST** create tracking entries:

```markdown
## Source Reference: [SRC-XX]

**Location**: [file path | URL | repo:path]
**Last Updated**: [date]
**Content Type**: [Diátaxis quadrant or Mixed]
**Token Estimate**: [approximate size]
**Key Topics**: [topic1, topic2, ...]
**Dependencies**: [references other sources]

### Summary
[2-3 sentence summary of what this source contains]

### Extraction Status
- [ ] Content analyzed
- [ ] Quadrant classified
- [ ] Gaps identified
- [ ] Rewrite/reorg notes created
```

### Phase Gate: Inventory Complete

```markdown
## Phase Gate: Inventory

### Source Registry
[X] sources registered, [Y] accessible, [Z] pending

### Inventory Statistics
- Total documents: [N]
- Total tokens: ~[N]
- Processing chunks needed: [N]

### Issues Identified
[List any accessibility issues or gaps]

---

**I will NOT proceed until you respond:**

[A] ✅ Approved - proceed to Phase 3 (Analysis)
[B] 🔄 Need changes - add/modify sources
[C] ⏸️ Pause - save state for later
```

---

## Phase 3: Analysis

### 3.1 Diátaxis Assessment

Claude **MUST** classify content for each source document:

```markdown
## Diátaxis Assessment: [Source/Section]

### Current Content Distribution

| Quadrant | Content Found | Quality (1-5) | Completeness (%) |
|----------|---------------|---------------|------------------|
| Tutorial | [yes/no/partial] | [1-5] | [%] |
| How-To | [yes/no/partial] | [1-5] | [%] |
| Reference | [yes/no/partial] | [1-5] | [%] |
| Explanation | [yes/no/partial] | [1-5] | [%] |

### Issues Identified
1. [Mixed content: Tutorial + Reference in same doc]
2. [Missing: No quickstart/5-minute guide]
3. [Gap: Architecture explanation scattered across files]

### Recommendations
1. [Extract tutorial content to dedicated guide]
2. [Create quickstart.md from existing installation notes]
```

### 3.2 Gap Analysis

Claude **MUST** identify what's missing for complete documentation:

```markdown
## Gap Analysis

### By Diátaxis Quadrant

#### Tutorials (Learning by Doing)
- [ ] Quickstart (5-minute first experience) - **MUST HAVE**
- [ ] Full guided project - **SHOULD HAVE**
- [ ] Progressive skill-building path - **MAY HAVE**
**Status**: [None | Partial | Complete]
**Priority**: [High | Medium | Low]

#### How-To Guides (Goal-Oriented)
- [ ] [Common task 1] - **MUST HAVE**
- [ ] [Common task 2] - **SHOULD HAVE**
- [ ] Integration guides - **MAY HAVE**
**Status**: [None | Partial | Complete]
**Priority**: [High | Medium | Low]

#### Reference (Information-Oriented)
- [ ] API/CLI documentation - **MUST HAVE** (if applicable)
- [ ] Configuration options - **SHOULD HAVE**
- [ ] Schema definitions - **MAY HAVE**
**Status**: [None | Partial | Complete]
**Priority**: [High | Medium | Low]

#### Explanation (Understanding-Oriented)
- [ ] Why this exists (problem/solution) - **SHOULD HAVE**
- [ ] Architecture/design decisions - **SHOULD HAVE**
- [ ] Comparison with alternatives - **MAY HAVE**
**Status**: [None | Partial | Complete]
**Priority**: [High | Medium | Low]
```

### 3.3 User Journey Mapping

Claude **SHOULD** map documentation to user lifecycle:

```markdown
## User Journey Analysis

| Journey Stage | User Question | Required Doc | Current State | Priority |
|---------------|---------------|--------------|---------------|----------|
| Discovery | "What is this?" | Landing/Overview | [status] | MUST |
| Evaluation | "Why should I care?" | Explanation | [status] | SHOULD |
| Getting Started | "How do I begin?" | Quickstart | [status] | MUST |
| First Success | "What can I do?" | Tutorial | [status] | MUST |
| Daily Use | "How do I do X?" | How-To | [status] | MUST |
| Troubleshooting | "Why not working?" | Reference + How-To | [status] | SHOULD |
| Deep Dive | "How does this work?" | Explanation | [status] | MAY |
```

### Phase Gate: Analysis Complete

```markdown
## Phase Gate: Analysis

### Assessment Summary
- Sources analyzed: [N]/[Total]
- Quadrant coverage: T:[%] H:[%] R:[%] E:[%]
- Critical gaps: [N]

### Minimum Viable Documentation
Based on analysis, the following are **required** for launch:
1. [ ] [Document 1] - [Quadrant]
2. [ ] [Document 2] - [Quadrant]

### Assumptions Made
[List with status: APPROVED/PENDING/REJECTED]

---

**I will NOT proceed until you respond:**

[A] ✅ Approved - proceed to Phase 4 (Planning)
[B] 🔄 Need changes - modify assessment
[C] ⏸️ Pause - save state for later
```

---

## Phase 4: Planning

### 4.1 Documentation Architecture

Claude **MUST** design the target structure:

```markdown
## Target Documentation Structure

docs/
├── index.md                    # Landing: What is X?
├── getting-started/
│   ├── quickstart.md           # Tutorial: 5-minute intro (MUST)
│   ├── installation.md         # How-To: Setup (MUST)
│   └── first-project.md        # Tutorial: Full guided project (SHOULD)
├── guides/                     # How-To Guides
│   ├── [task-1].md            # (MUST)
│   └── [task-2].md            # (SHOULD)
├── concepts/                   # Explanation
│   ├── why-[product].md       # (SHOULD)
│   └── architecture.md        # (SHOULD)
└── reference/                  # Reference
    ├── api.md                 # (MUST if applicable)
    └── configuration.md       # (SHOULD)
```

### 4.2 Work Breakdown Structure

Claude **MUST** create actionable items with source references:

```markdown
## Work Breakdown Structure

### WBS-001: Landing Page (index.md)
**Diátaxis**: Overview (bridges all quadrants)
**Priority**: MUST
**Estimated Effort**: 2-3 hours
**Token Budget**: ~2,000 output tokens

**Source References**:
- [SRC-01]: Current README.md (lines 1-50)
- [SRC-02]: About page from website

**Content Requirements**:
- [ ] One-sentence value proposition
- [ ] Visual/diagram showing concept
- [ ] Navigation paths to each quadrant
- [ ] Quick links to quickstart

**Dependencies**: None
**Blocks**: WBS-002, WBS-003
```

### 4.3 Chunking for AI Context

When source material exceeds context limits, Claude **MUST** create a chunking plan:

```markdown
## Chunking Plan

### Token Budget
- Available context: ~100,000 tokens
- Reserved for generation: ~30,000 tokens
- Available for sources: ~70,000 tokens

### Processing Order
Claude **MUST** process in dependency order:

| Chunk | Description | Sources | Tokens | Dependencies |
|-------|-------------|---------|--------|--------------|
| 1 | Core concepts | SRC-01, SRC-02 | ~8,000 | None |
| 2 | API reference | SRC-03, SRC-04 | ~12,000 | Chunk 1 |
| 3 | Tutorial content | SRC-05 | ~6,000 | Chunk 1, 2 |

### Cross-Reference Protocol
- Claude **MUST** reference all sources by [SRC-XX]
- Claude **MUST** include page/section markers
- Claude **SHOULD** include token estimates for planning
```

See `references/chunking-strategy.md` for detailed protocols.

### Phase Gate: Planning Complete

```markdown
## Phase Gate: Planning

### WBS Summary
- Total items: [N]
- MUST items: [N]
- Estimated effort: [N] hours
- Processing chunks: [N]

### Approved Structure
[Show target structure]

### Chunking Plan Confirmed
[Show chunk processing order]

---

**I will NOT proceed until you respond:**

[A] ✅ Approved - proceed to Phase 5 (Execution)
[B] 🔄 Need changes - modify plan
[C] ⏸️ Pause - save state for later
```

---

## Phase 5: Execution

**Critical**: See `references/change-management.md` for complete document review loop and cascade analysis protocols.

### 5.1 Document Creation Workflow

For each WBS item, Claude **MUST** follow this workflow:

```markdown
## Execution Checklist: [WBS-ID]

### Pre-Writing (MUST complete all)
- [ ] Review all source references
- [ ] Confirm Diátaxis quadrant focus
- [ ] Verify dependencies completed
- [ ] Load relevant sources into context
- [ ] Check change-log.md for relevant prior changes
- [ ] Check terminology-registry.md for term usage

### Writing (MUST meet all criteria)
- [ ] Create file with proper frontmatter
- [ ] Write content following quadrant guidelines
- [ ] Cite sources for all factual claims
- [ ] Include cross-references to related docs
- [ ] Add navigation aids
- [ ] Use terms consistently per terminology-registry.md

### Post-Writing (MUST complete all)
- [ ] Validate against quadrant checklist
- [ ] Verify all source references included
- [ ] Check for TODO/placeholder markers (MUST be zero)
- [ ] Update WBS status
- [ ] ENTER DOCUMENT REVIEW LOOP (see 5.3)
```

### 5.2 Diátaxis Quadrant Checklists

Claude **MUST** pass ALL items in the relevant checklist:

**Tutorial Checklist** (100% required):
- [ ] Focuses on learning, not accomplishing a task
- [ ] Has clear starting and ending points
- [ ] Provides immediate, visible results at each step
- [ ] Doesn't explain concepts—just guides action
- [ ] Is repeatable—works the same every time

**How-To Checklist** (100% required):
- [ ] Has a clear goal in the title ("How to X")
- [ ] Assumes the reader already knows basics
- [ ] Focuses on solving a real problem
- [ ] Provides practical, actionable steps
- [ ] Keeps explanation to a minimum

**Reference Checklist** (100% required):
- [ ] Organized by the structure of the thing it describes
- [ ] Complete and accurate
- [ ] Neutral tone—just the facts
- [ ] Easy to navigate/search
- [ ] Doesn't mix in tutorials or explanations

**Explanation Checklist** (100% required):
- [ ] Provides context and background
- [ ] Explores "why" questions
- [ ] Can approach from different angles
- [ ] May include opinions and alternatives
- [ ] Helps build a mental model

### 5.3 Document Review Loop (MANDATORY)

Claude **MUST** execute this review loop for EVERY document. Claude **MUST NOT** proceed to the next document until the current document is approved.

```
┌─────────────────────────────────────────────────────────────┐
│               DOCUMENT REVIEW LOOP                          │
│                                                             │
│  Generate ──▶ Present ──▶ Collect ──┬──▶ [Approved]        │
│  Document     Review     Feedback   │        │              │
│                                     │        ▼              │
│                                     │   Update Memory       │
│                                     │   Files & Continue    │
│                                     │                       │
│                                     └──▶ [Changes]          │
│                                              │               │
│                                              ▼               │
│                                         Apply Changes        │
│                                              │               │
│                                              ▼               │
│                                         Log to change-log    │
│                                              │               │
│                                              ▼               │
│                                         Cascade Analysis     │
│                                              │               │
│                                     ┌────────┴────────┐     │
│                                     ▼                 ▼     │
│                               [No Impact]      [Has Impact] │
│                                     │                 │     │
│                                     │          Queue in     │
│                                     │       cascade-tracker │
│                                     │                 │     │
│                                     ▼                 ▼     │
│                                   Update Memory Files        │
│                                              │               │
│                                              ▼               │
│                                   Present Updated Document   │
│                                      (Loop back to Review)   │
└─────────────────────────────────────────────────────────────┘
```

#### Step 1: Present for Review

After generating any document, Claude **MUST** present it with these options:

```markdown
## Document Review: [filename]

### Document Summary
- **Path**: [target path]
- **Quadrant**: [Tutorial/How-To/Reference/Explanation]
- **Word Count**: [N]
- **Sources Used**: [SRC-XX, SRC-YY]
- **New Terms Introduced**: [term1, term2] or "None"

### Content Preview
[First 500 words or complete document if shorter]

### Quality Checklist Results
- [x] Quadrant guidelines followed (5/5)
- [x] Sources cited ([N] citations)
- [x] Cross-references included
- [x] No TODO/placeholder markers
- [x] Terms consistent with registry

---

**I will NOT proceed until you respond:**

[A] ✅ **Approve as-is** - Document is complete, continue to next
[B] 📝 **Request changes** - I will collect your feedback
[C] 👁️ **View full document** - See complete content before deciding
[D] 🔄 **Regenerate** - Start fresh with different approach
[E] ⏸️ **Pause** - Save state and continue later
```

#### Step 2: Collect Feedback (if changes requested)

When user selects [B], Claude **MUST** ask:

```markdown
## Change Request: [filename]

Please describe the changes needed. To help with cascade analysis, indicate which apply:

**Change Categories** (select all that apply):
- [ ] **Terminology** - Change terms, definitions, naming
- [ ] **Structure** - Reorganize sections, headings, flow
- [ ] **Content** - Add, remove, or modify information
- [ ] **Tone/Style** - Adjust writing style, audience level
- [ ] **Cross-references** - Update links to other docs
- [ ] **Examples** - Add, modify, or remove examples
- [ ] **Accuracy** - Correct factual errors

**Your Feedback**:
> [Awaiting user input]
```

#### Step 3: Apply Changes

Claude **MUST**:
1. Apply all requested changes to the document
2. Re-run the quadrant checklist
3. Verify changes fully address the feedback
4. Prepare the change log entry

#### Step 4: Log Changes (MANDATORY)

Claude **MUST** add an entry to `change-log.md` for EVERY change:

```markdown
### CL-[NNN]: [Brief Description]

**Document**: [path]
**Timestamp**: [ISO datetime]
**Session**: [session ID]
**Change Type**: [Terminology|Structure|Content|Tone|Cross-ref|Examples|Accuracy]

#### Changes Made
| Element | Before | After |
|---------|--------|-------|
| [what] | [old] | [new] |

#### User Feedback
> [Original feedback]

#### Implementation Notes
[How change was implemented]
```

#### Step 5: Cascade Analysis (MANDATORY)

After EVERY change, Claude **MUST** analyze cascade impact:

```markdown
## Cascade Analysis: CL-[NNN]

### Change Summary
[What was changed in this document]

### Impact Assessment

#### Terminology Impact
| Term Changed | Documents Using Term | Action Required |
|--------------|---------------------|-----------------|
| [term] | [doc1.md, doc2.md] | [Update/Review] |

**Terminology cascade detected**: [Yes/No]

#### Cross-Reference Impact  
| Link/Anchor Changed | Documents Linking Here | Action Required |
|---------------------|----------------------|-----------------|
| [link] | [doc1.md] | [Update link] |

**Cross-reference cascade detected**: [Yes/No]

#### Content Dependency Impact
| Content Changed | Documents Referencing | Action Required |
|-----------------|----------------------|-----------------|
| [concept] | [doc1.md] | [Verify consistency] |

**Content cascade detected**: [Yes/No]

### Cascade Queue Update

**New cascades to add to cascade-tracker.md**: [N]

| Priority | Affected Document | Required Action |
|----------|-------------------|-----------------|
| [1/2/3] | [doc.md] | [action] |
```

#### Step 6: Update Memory Files (MANDATORY)

After EVERY document change, Claude **MUST** update these files:

| File | Update Required | What to Update |
|------|-----------------|----------------|
| `change-log.md` | **ALWAYS** | Add CL-NNN entry |
| `cascade-tracker.md` | If cascades detected | Add PC-NNN entries |
| `terminology-registry.md` | If terms added/changed | Add/update term entries |
| `progress-tracker.md` | **ALWAYS** | Update document status |
| `source-registry.md` | If new sources used | Add source entries |

#### Step 7: Present Updated Document

After changes are applied and logged, Claude **MUST** loop back to Step 1 and present the updated document for review. This loop continues until the user selects [A] Approve.

### 5.4 Cascade Queue Processing

After a document is approved, if there are pending cascades, Claude **MUST** present:

```markdown
## Cascade Queue Status

**Document Approved**: [filename]
**Pending Cascades**: [N]

| Priority | Affected Document | Source Change | Required Action |
|----------|-------------------|---------------|-----------------|
| 1 | [doc.md] | CL-XXX | [action] |
| 2 | [doc.md] | CL-XXX | [action] |

---

**Cascade Processing Options:**

[A] 🔄 **Process cascades now** - Address affected documents before continuing
[B] ➡️ **Continue to next document** - Process cascades after all documents complete
[C] 📋 **Review cascade details** - See full impact analysis before deciding
[D] ⏸️ **Pause** - Save state for later
```

If user selects [A], Claude **MUST** open each affected document, apply required changes, and execute the full Document Review Loop (5.3) for each.

### 5.5 Iterative Chunk Processing

For large documentation projects spanning multiple chunks:

```
Chunk Processing Cycle:
1. Load chunk context (sources, carry-forward notes, memory files)
2. Process documents in chunk (each through Review Loop)
3. Update all memory files
4. Process any pending cascades from this chunk
5. Generate chunk completion summary
6. Save session state
7. Request user confirmation before next chunk

Memory Files to Load Each Chunk:
- change-log.md (for context continuity)
- cascade-tracker.md (for pending work)
- terminology-registry.md (for consistency)
- progress-tracker.md (for status)
```

### 5.6 Session Continuity

To maintain context across sessions, Claude **MUST** generate session summaries:

```markdown
## Session Summary: [Session ID]

### Documents Completed This Session
| Document | Changes Made | Cascades Triggered |
|----------|--------------|-------------------|
| [doc.md] | [N] | [N] |

### Change Log Entries Added
- CL-XXX: [summary]
- CL-XXX: [summary]

### Pending Cascades
| ID | Affected Doc | Priority | Status |
|----|--------------|----------|--------|
| PC-XXX | [doc.md] | [1/2/3] | ⬜ Pending |

### Memory Files Updated
- [x] change-log.md ([N] new entries)
- [x] cascade-tracker.md ([N] pending)
- [x] terminology-registry.md ([N] terms)
- [x] progress-tracker.md (current status)

### Resume Instructions
To continue: Load memory files and say "Resume from [last document/cascade queue]"
```

---

## Phase 6: Validation

### 6.1 Completeness Check

Claude **MUST** verify all requirements are met:

```markdown
## Documentation Completeness Validation

### Diátaxis Coverage

| Quadrant | Required | Completed | Quality (1-5) | Status |
|----------|----------|-----------|---------------|--------|
| Tutorial | [list] | [X/N] | [score] | [✅/❌] |
| How-To | [list] | [X/N] | [score] | [✅/❌] |
| Reference | [list] | [X/N] | [score] | [✅/❌] |
| Explanation | [list] | [X/N] | [score] | [✅/❌] |

### User Journey Coverage

| Journey Stage | Doc Exists | Path Tested | Status |
|---------------|------------|-------------|--------|
| Discovery | [yes/no] | [yes/no] | [✅/❌] |
| Getting Started | [yes/no] | [yes/no] | [✅/❌] |
| First Success | [yes/no] | [yes/no] | [✅/❌] |
| Daily Use | [yes/no] | [yes/no] | [✅/❌] |
| Deep Dive | [yes/no] | [yes/no] | [✅/❌] |
```

### 6.2 Quality Assessment

Claude **MUST** run quality checks:

```bash
python scripts/validate_docs.py <docs-dir> --output validation-report.md --strict
```

**Quality Thresholds** (MUST meet all blocking items):

| Metric | Minimum | Target | Blocking |
|--------|---------|--------|----------|
| Overall quality score | 60/100 | 80/100 | Yes |
| Source coverage | 80% | 100% | Yes |
| Quadrant checklist pass | 100% | 100% | Yes |
| Broken links | 0 | 0 | Yes |
| TODO/placeholder markers | 0 | 0 | Yes |
| Orphan pages | <10% | 0 | No |

### 6.3 Delivery Checklist

Claude **MUST** verify before delivery:

```markdown
## Documentation Package Delivery

### Structure (MUST pass all)
- [ ] Follows Diátaxis organization
- [ ] Clear navigation hierarchy
- [ ] Consistent file naming
- [ ] No orphan pages

### Content (MUST pass all)
- [ ] All MUST WBS items completed
- [ ] All source references honored
- [ ] Quadrant content properly separated
- [ ] No TODO/placeholder markers

### Quality (MUST pass all)
- [ ] Quality score ≥ 60/100
- [ ] Code examples tested (if applicable)
- [ ] Links validated
- [ ] Spelling/grammar checked

### Metadata (SHOULD complete)
- [ ] All docs have proper frontmatter
- [ ] Version/date information included
- [ ] Author/contributor attribution
```

### Final Gate: Delivery Approval

```markdown
## Phase Gate: Delivery

### Quality Report
- Overall score: [X]/100
- Blocking issues: [N]
- Warnings: [N]

### Package Contents
- Documents: [N]
- Total words: [N]
- Estimated reading time: [N] minutes

### Outstanding Items
[List any non-blocking issues]

---

**Delivery Options:**

[A] ✅ Deliver as-is - meets all requirements
[B] 🔄 Address warnings - fix non-blocking issues first
[C] ❌ Blocking issues exist - cannot deliver until resolved
```

---

## Session Management

### Saving Session State

At any pause point, Claude **MUST** generate session state:

```markdown
## Session State: [Timestamp]

### Project
- Name: [project name]
- Started: [date]
- Current Phase: [phase]

### Progress
- [x] Phase 1: Discovery - Complete
- [x] Phase 2: Inventory - Complete  
- [ ] Phase 3: Analysis - In Progress (50%)
- [ ] Phase 4-6: Pending

### Source Registry
[Current source registry snapshot]

### Decisions Made
[Decision log snapshot]

### Assumptions Approved
[Assumption log snapshot]

### Resume Instructions
To resume: provide this state and say "resume documentation project"
```

### Resuming a Session

When resuming, Claude **MUST**:
1. Verify session state is provided
2. Confirm source accessibility
3. Display progress summary
4. Confirm resume point with user

---

## Reference Documents

- **GUARDRAILS.md** - Behavioral constraints (MUST read first)
- **Diátaxis Framework**: See `references/diataxis-framework.md` for quadrant details
- **Chunking Strategy**: See `references/chunking-strategy.md` for AI context handling
- **Source Tracking**: See `references/source-tracking.md` for reference protocols
- **Quality Criteria**: See `references/quality-criteria.md` for assessment rubrics
- **Change Management**: See `references/change-management.md` for review loop and cascade analysis

## Memory Files

Claude **MUST** maintain these files throughout the project:

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `change-log.md` | Cumulative change history | Every document change |
| `cascade-tracker.md` | Pending cascade updates | When cascades detected/resolved |
| `terminology-registry.md` | Term definitions and usage | When terms added/changed |
| `progress-tracker.md` | Overall project progress | Every session, every document |
| `source-registry.md` | Source tracking | When sources added/updated |

## Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `scripts/analyze_docs.py` | Inventory existing documentation | Phase 2 |
| `scripts/doc_research.py` | Research competitor documentation | Phase 1 |
| `scripts/validate_docs.py` | Check documentation quality | Phase 6 |
| `scripts/generate_wbs.py` | Generate work breakdown structure | Phase 4 |

## Templates

| Template | Purpose |
|----------|---------|
| `templates/inventory.md` | Documentation inventory format |
| `templates/wbs-item.md` | Work breakdown structure item |
| `templates/source-reference.md` | Source tracking format |
| `templates/progress-tracker.md` | Session and overall progress tracking |
| `templates/change-log.md` | Cumulative change history |
| `templates/cascade-tracker.md` | Cascade impact tracking |
| `templates/terminology-registry.md` | Term definitions and usage tracking |

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Mixed quadrant content | Confuses users | Separate by user need |
| Specification as tutorials | Intimidates newcomers | Lead with learning, link to spec |
| No quickstart | Loses users at first contact | 5-minute first experience (MUST) |
| Scattered explanations | No coherent mental model | Dedicated concepts section |
| Reference-only docs | Only serves experts | Full quadrant coverage |
| No source tracking | Lost context between sessions | Rigorous reference protocols |
| Proceeding without confirmation | Unwanted outputs | Phase gates at every transition |
| Unsourced claims | Unreliable documentation | Cite every factual claim |
| Hidden assumptions | Flawed foundations | Explicit approval required |
