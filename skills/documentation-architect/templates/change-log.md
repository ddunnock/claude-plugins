# Documentation Change Log

**Project**: [Project Name]
**Created**: [Date]
**Last Updated**: [Timestamp]
**Total Changes**: 0

---

## How to Use This Log

This log tracks ALL changes to documentation throughout the project. It enables:
- Context preservation across sessions
- Cascade impact tracking
- Change history auditing
- Consistency maintenance

**Entry Format**: Each change gets a unique ID (CL-NNN) and full details.

---

## Active Session: [Session ID]

**Started**: [Timestamp]
**Documents Processed**: [N]
**Changes This Session**: [N]

---

## Change Entries

### CL-001: [Brief Description]

**Document**: [path/to/document.md]
**Timestamp**: [ISO datetime]
**Session**: [Session ID]
**Change Type**: [Terminology | Structure | Content | Tone | Cross-ref | Examples | Accuracy]
**Cascade Impact**: [None | Low | Medium | High]

#### Changes Made

| Element | Before | After |
|---------|--------|-------|
| [what changed] | [old value/state] | [new value/state] |

#### User Feedback
> [Original feedback that prompted this change]

#### Implementation Notes
[How the change was implemented, any decisions made]

#### Cascade Analysis
- **Terminology Impact**: [None | List affected docs]
- **Cross-Reference Impact**: [None | List affected links]
- **Content Dependency Impact**: [None | List dependent docs]
- **Structure Impact**: [None | List navigation changes]

#### Cascades Triggered
| ID | Affected Document | Required Action | Status |
|----|-------------------|-----------------|--------|
| PC-XXX | [doc.md] | [action] | [⬜ Pending | ✅ Complete] |

---

<!-- TEMPLATE FOR NEW ENTRIES - Copy this block for each change

### CL-NNN: [Brief Description]

**Document**: [path/to/document.md]
**Timestamp**: [ISO datetime]
**Session**: [Session ID]
**Change Type**: [Terminology | Structure | Content | Tone | Cross-ref | Examples | Accuracy]
**Cascade Impact**: [None | Low | Medium | High]

#### Changes Made

| Element | Before | After |
|---------|--------|-------|
| | | |

#### User Feedback
> 

#### Implementation Notes


#### Cascade Analysis
- **Terminology Impact**: 
- **Cross-Reference Impact**: 
- **Content Dependency Impact**: 
- **Structure Impact**: 

#### Cascades Triggered
| ID | Affected Document | Required Action | Status |
|----|-------------------|-----------------|--------|
| | | | |

---

END TEMPLATE -->

## Pending Cascades Summary

| ID | Source Change | Affected Document | Required Action | Priority | Status |
|----|---------------|-------------------|-----------------|----------|--------|
| PC-001 | CL-XXX | [doc.md] | [action] | [1-3] | ⬜ Pending |

**Total Pending**: [N]

---

## Resolved Cascades

| ID | Source Change | Affected Document | Resolution | Resolved In |
|----|---------------|-------------------|------------|-------------|
| | | | | |

---

## Session History

| Session ID | Date | Changes | Cascades Created | Cascades Resolved |
|------------|------|---------|------------------|-------------------|
| [ID] | [date] | [N] | [N] | [N] |

---

## Statistics

| Metric | Count |
|--------|-------|
| **Total Changes** | 0 |
| Terminology changes | 0 |
| Structure changes | 0 |
| Content changes | 0 |
| Tone/Style changes | 0 |
| Cross-reference changes | 0 |
| Example changes | 0 |
| Accuracy corrections | 0 |
| **Total Cascades Triggered** | 0 |
| Cascades resolved | 0 |
| Cascades pending | 0 |

---

## Change Type Definitions

| Type | Description | Typical Cascade Impact |
|------|-------------|----------------------|
| **Terminology** | Term definitions, naming conventions | High - affects all docs using term |
| **Structure** | Section reorganization, heading changes | Medium - affects navigation/links |
| **Content** | Information additions, removals, modifications | Medium - affects dependent docs |
| **Tone** | Writing style, audience level adjustments | Low - usually isolated |
| **Cross-ref** | Link updates, anchor changes | Medium - affects linking docs |
| **Examples** | Code samples, illustrations, scenarios | Low - usually isolated |
| **Accuracy** | Factual corrections, specification updates | High - may affect dependent content |

---

## Notes

[Any project-specific notes about change patterns, recurring issues, or decisions]
