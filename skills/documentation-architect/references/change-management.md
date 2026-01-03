# Change Management Reference

Protocols for managing document changes, cascade analysis, and maintaining consistency across the documentation set.

## Core Principles

1. **Every change is logged** - No modification without record
2. **Cascade impact is analyzed** - Changes may affect other documents
3. **Consistency is maintained** - Terminology and cross-references stay synchronized
4. **Context is preserved** - Cumulative log enables continuity across sessions

---

## Document Review Loop

### Overview

For each document generated or modified, Claude **MUST** execute this review loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT REVIEW LOOP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│   │ Generate │────▶│ Present  │────▶│ Collect  │               │
│   │ Document │     │ Review   │     │ Feedback │               │
│   └──────────┘     └──────────┘     └────┬─────┘               │
│                                          │                      │
│                    ┌─────────────────────┴─────────────────┐   │
│                    │                                       │   │
│                    ▼                                       ▼   │
│              [Approved]                            [Changes]   │
│                    │                                   │       │
│                    │         ┌──────────┐             │       │
│                    │         │  Apply   │◀────────────┘       │
│                    │         │ Changes  │                      │
│                    │         └────┬─────┘                      │
│                    │              │                             │
│                    │              ▼                             │
│                    │         ┌──────────┐                      │
│                    │         │   Log    │                      │
│                    │         │ Changes  │                      │
│                    │         └────┬─────┘                      │
│                    │              │                             │
│                    │              ▼                             │
│                    │         ┌──────────┐                      │
│                    │         │ Analyze  │                      │
│                    │         │ Cascade  │                      │
│                    │         └────┬─────┘                      │
│                    │              │                             │
│                    │    ┌────────┴────────┐                    │
│                    │    │                 │                    │
│                    │    ▼                 ▼                    │
│                    │ [No Impact]    [Has Impact]               │
│                    │    │                 │                    │
│                    │    │                 ▼                    │
│                    │    │          ┌──────────┐               │
│                    │    │          │  Queue   │               │
│                    │    │          │ Cascades │               │
│                    │    │          └────┬─────┘               │
│                    │    │               │                      │
│                    ▼    ▼               ▼                      │
│              ┌─────────────────────────────┐                   │
│              │    Update Progress &        │                   │
│              │    Present Next Options     │                   │
│              └─────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 1: Present for Review

After generating any document, Claude **MUST** present it with these options:

```markdown
## Document Review: [filename]

### Document Summary
- **Path**: [target path]
- **Quadrant**: [Tutorial/How-To/Reference/Explanation]
- **Word Count**: [N]
- **Sources Used**: [SRC-XX, SRC-YY]

### Content Preview
[First 500 words or key sections]

### Quality Checklist
- [x] Quadrant guidelines followed
- [x] Sources cited
- [x] Cross-references included
- [ ] [Any issues found]

---

**Review Options:**

[A] ✅ Approve as-is - Document is complete
[B] 📝 Request changes - Provide specific feedback
[C] 👁️ View full document - See complete content before deciding
[D] 🔄 Regenerate - Start fresh with different approach
[E] ⏸️ Pause - Save state and continue later
```

### Step 2: Collect Feedback

When user selects [B] Request changes, Claude **MUST** ask:

```markdown
## Change Request: [filename]

Please describe the changes needed:

**Change Categories** (helps with cascade analysis):
- [ ] **Terminology** - Change terms, definitions, naming
- [ ] **Structure** - Reorganize sections, headings, flow
- [ ] **Content** - Add, remove, or modify information
- [ ] **Tone/Style** - Adjust writing style, audience level
- [ ] **Cross-references** - Update links to other docs
- [ ] **Examples** - Add, modify, or remove examples
- [ ] **Accuracy** - Correct factual errors

**Your Feedback**:
[User provides feedback here]
```

### Step 3: Apply Changes

Claude **MUST**:
1. Apply requested changes to document
2. Verify changes address feedback
3. Re-run quadrant checklist
4. Prepare change log entry

### Step 4: Log Changes

Every change **MUST** be logged in the cumulative change log:

```markdown
## Change Log Entry: CL-[NNN]

**Document**: [path]
**Timestamp**: [ISO datetime]
**Session**: [session ID]
**Change Type**: [Terminology/Structure/Content/Tone/Cross-ref/Examples/Accuracy]

### Changes Made
| Item | Before | After |
|------|--------|-------|
| [element] | [old value] | [new value] |

### User Feedback
> [Original feedback that prompted change]

### Implementation Notes
[How the change was implemented]

### Files Modified
- [filename] - [what changed]
```

### Step 5: Analyze Cascade Impact

After logging, Claude **MUST** analyze cascade impact:

```markdown
## Cascade Analysis: CL-[NNN]

### Change Summary
[Brief description of what changed]

### Impact Assessment

#### Terminology Impact
| Term Changed | Documents Using Term | Impact |
|--------------|---------------------|--------|
| [term] | [doc1.md, doc2.md] | [Update required/Review recommended] |

#### Cross-Reference Impact
| Link Changed | Documents Linking Here | Impact |
|--------------|----------------------|--------|
| [anchor/path] | [doc1.md, doc2.md] | [Update required/Link broken] |

#### Content Dependency Impact
| Content Changed | Documents Referencing | Impact |
|-----------------|----------------------|--------|
| [section/concept] | [doc1.md] | [May need update/Inconsistency risk] |

#### Structure Impact
| Structure Changed | Navigation Impact | Documents Affected |
|-------------------|-------------------|-------------------|
| [heading/section] | [TOC update needed] | [doc1.md] |

### Cascade Queue
| Priority | Document | Required Action | Status |
|----------|----------|-----------------|--------|
| 1 | [doc.md] | [action] | ⬜ Pending |
| 2 | [doc.md] | [action] | ⬜ Pending |

### Cascade Decision Required

**Pending cascades detected: [N]**

[A] 🔄 Address cascades now - Process affected documents
[B] 📋 Queue for later - Continue with other documents first
[C] 🚫 Skip cascades - Mark as acknowledged but don't update
```

---

## Cascade Types

### 1. Terminology Cascade

**Trigger**: Term definition, name, or concept changed

**Detection**:
- Search all documents for old term
- Check terminology registry for dependencies
- Identify definition references

**Resolution**:
- Update all occurrences of old term
- Update terminology registry
- Log all affected documents

### 2. Cross-Reference Cascade

**Trigger**: File renamed, section heading changed, anchor modified

**Detection**:
- Search for links to old path/anchor
- Check navigation elements
- Identify breadcrumb dependencies

**Resolution**:
- Update all links to new path/anchor
- Update navigation components
- Verify no broken links remain

### 3. Content Dependency Cascade

**Trigger**: Factual content changed, example modified, specification updated

**Detection**:
- Identify documents that reference this content
- Check for contradictions with new content
- Find examples that depend on old content

**Resolution**:
- Update dependent documents
- Resolve contradictions
- Update related examples

### 4. Structure Cascade

**Trigger**: Document reorganized, sections moved, hierarchy changed

**Detection**:
- Check TOC references
- Identify sequential reading paths
- Find prerequisite dependencies

**Resolution**:
- Update TOC and navigation
- Update "next/previous" links
- Update prerequisite mentions

---

## Cumulative Change Log Format

The change log **MUST** be maintained across sessions:

```markdown
# Documentation Change Log

**Project**: [project name]
**Created**: [date]
**Last Updated**: [timestamp]
**Total Changes**: [N]

---

## Session: [Session ID] - [Date]

### CL-001: [Brief Description]
**Document**: [path]
**Type**: [Terminology/Structure/Content/etc.]
**Cascade Impact**: [None/Low/Medium/High]

**Changes**:
- [Change 1]
- [Change 2]

**Cascades Triggered**: [List or "None"]
**Cascades Resolved**: [List or "N/A"]

---

### CL-002: [Brief Description]
[...]

---

## Pending Cascades

| ID | Source Change | Affected Doc | Required Action | Status |
|----|---------------|--------------|-----------------|--------|
| PC-001 | CL-003 | guide.md | Update term "widget" | ⬜ Pending |

---

## Statistics

| Metric | Value |
|--------|-------|
| Total changes | [N] |
| Terminology changes | [N] |
| Structure changes | [N] |
| Content changes | [N] |
| Cascades triggered | [N] |
| Cascades resolved | [N] |
| Cascades pending | [N] |
```

---

## Terminology Registry

To enable cascade detection, maintain a terminology registry:

```markdown
# Terminology Registry

**Project**: [project name]
**Last Updated**: [timestamp]

## Defined Terms

| Term | Definition | Defined In | Used In | Status |
|------|------------|------------|---------|--------|
| [term] | [definition] | [source doc] | [doc1, doc2] | [Active/Deprecated] |

## Term Change History

| Term | Old Value | New Value | Change ID | Date |
|------|-----------|-----------|-----------|------|
| [term] | [old] | [new] | CL-XXX | [date] |
```

---

## Memory Files to Maintain

Claude **MUST** update these files as changes occur:

| File | Purpose | Update Trigger |
|------|---------|----------------|
| `change-log.md` | Cumulative change history | Every document change |
| `cascade-tracker.md` | Pending cascade updates | Cascade detected |
| `terminology-registry.md` | Term definitions and usage | Term added/changed |
| `progress-tracker.md` | Overall progress | Phase/document completion |
| `source-registry.md` | Source tracking | Source added/updated |

### Update Protocol

After ANY document modification:

1. **MUST** add entry to `change-log.md`
2. **MUST** run cascade analysis
3. **MUST** update `cascade-tracker.md` if cascades found
4. **MUST** update `terminology-registry.md` if terms changed
5. **MUST** update `progress-tracker.md` with current status
6. **SHOULD** summarize updates to user

---

## Review Loop Integration with Phases

### Phase 5 Enhancement

The standard Phase 5 execution now includes:

```
For each WBS item:
1. Generate document
2. ENTER REVIEW LOOP:
   a. Present for review
   b. Collect feedback (if changes requested)
   c. Apply changes
   d. Log changes
   e. Analyze cascade
   f. Update memory files
   g. REPEAT until approved or paused
3. Process cascade queue (if any)
4. Proceed to next document
```

### Cascade Processing Decision

After each document approval, if cascades are pending:

```markdown
## Cascade Queue Status

**Pending Cascades**: [N]

| Priority | Document | From Change | Action Required |
|----------|----------|-------------|-----------------|
| 1 | [doc.md] | CL-XXX | [action] |

**Processing Options**:

[A] 🔄 Process cascades now - Address before continuing
[B] ➡️ Continue to next document - Process cascades at end
[C] 📋 Review cascade details - See full impact analysis
```

---

## Context Preservation

### Session Handoff

When pausing or ending a session, Claude **MUST** generate:

```markdown
## Session Handoff: [Session ID]

### Session Summary
- **Documents completed**: [N]
- **Documents in review**: [N]
- **Changes made**: [N]
- **Cascades pending**: [N]

### Change Log Entries This Session
- CL-XXX: [summary]
- CL-XXX: [summary]

### Pending Work
1. [Document in progress]
2. [Cascade queue items]

### Memory Files Updated
- [x] change-log.md
- [x] progress-tracker.md
- [x] terminology-registry.md
- [ ] cascade-tracker.md (N items pending)

### Resume Context
To resume, load these files:
1. change-log.md (for context)
2. cascade-tracker.md (for pending work)
3. progress-tracker.md (for status)

Then say: "Resume documentation project from [last document/cascade queue]"
```

---

## Guardrail Integration

These rules from GUARDRAILS.md apply to change management:

1. **NO PROCEEDING WITHOUT CONFIRMATION** - Every document requires review approval
2. **ALL CHANGES MUST BE LOGGED** - No modification without change log entry
3. **CASCADE ANALYSIS IS MANDATORY** - Every change triggers impact assessment
4. **MEMORY FILES MUST BE CURRENT** - Update before proceeding
