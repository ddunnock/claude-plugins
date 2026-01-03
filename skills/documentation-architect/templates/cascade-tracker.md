# Cascade Tracker

**Project**: [Project Name]
**Last Updated**: [Timestamp]
**Pending Cascades**: 0
**Resolved This Session**: 0

---

## Purpose

This file tracks cascade impacts from document changes. When a change to one document affects others, those impacts are queued here until resolved.

**Update Triggers**:
- Document terminology changed
- Document structure modified
- Cross-references updated
- Content dependencies affected

---

## Pending Cascades

### Priority 1 (Critical - Address Immediately)

Critical cascades include: broken links, contradictory information, missing references.

| ID | Source | Affected Doc | Impact Type | Required Action | Created |
|----|--------|--------------|-------------|-----------------|---------|
| PC-XXX | CL-XXX | [doc.md] | [type] | [action] | [date] |

**Count**: 0

---

### Priority 2 (Important - Address Before Phase Completion)

Important cascades include: terminology consistency, navigation updates, related content sync.

| ID | Source | Affected Doc | Impact Type | Required Action | Created |
|----|--------|--------------|-------------|-----------------|---------|
| PC-XXX | CL-XXX | [doc.md] | [type] | [action] | [date] |

**Count**: 0

---

### Priority 3 (Minor - Address When Convenient)

Minor cascades include: style consistency, optional cross-references, enhancement suggestions.

| ID | Source | Affected Doc | Impact Type | Required Action | Created |
|----|--------|--------------|-------------|-----------------|---------|
| PC-XXX | CL-XXX | [doc.md] | [type] | [action] | [date] |

**Count**: 0

---

## Cascade Details

### PC-001: [Brief Description]

**Source Change**: CL-XXX ([source document])
**Affected Document**: [path/to/affected.md]
**Priority**: [1 | 2 | 3]
**Impact Type**: [Terminology | Cross-Reference | Content Dependency | Structure]
**Status**: ⬜ Pending

#### Impact Analysis

**What Changed**:
[Description of the original change that triggered this cascade]

**How It Affects This Document**:
[Specific impact on the affected document]

**Required Action**:
[Specific steps to resolve this cascade]

#### Resolution Checklist
- [ ] Open affected document
- [ ] Locate impacted content
- [ ] Apply required changes
- [ ] Verify consistency
- [ ] Log resolution in change-log.md
- [ ] Mark cascade as resolved

---

<!-- TEMPLATE FOR NEW CASCADE ENTRIES

### PC-NNN: [Brief Description]

**Source Change**: CL-XXX ([source document])
**Affected Document**: [path/to/affected.md]
**Priority**: [1 | 2 | 3]
**Impact Type**: [Terminology | Cross-Reference | Content Dependency | Structure]
**Status**: ⬜ Pending

#### Impact Analysis

**What Changed**:


**How It Affects This Document**:


**Required Action**:


#### Resolution Checklist
- [ ] Open affected document
- [ ] Locate impacted content
- [ ] Apply required changes
- [ ] Verify consistency
- [ ] Log resolution in change-log.md
- [ ] Mark cascade as resolved

---

END TEMPLATE -->

## Resolved Cascades (This Session)

| ID | Source | Affected Doc | Resolution Summary | Resolved |
|----|--------|--------------|-------------------|----------|
| | | | | |

---

## Cascade Statistics

### By Impact Type

| Impact Type | Pending | Resolved | Total |
|-------------|---------|----------|-------|
| Terminology | 0 | 0 | 0 |
| Cross-Reference | 0 | 0 | 0 |
| Content Dependency | 0 | 0 | 0 |
| Structure | 0 | 0 | 0 |
| **Total** | 0 | 0 | 0 |

### By Priority

| Priority | Pending | Resolved |
|----------|---------|----------|
| 1 (Critical) | 0 | 0 |
| 2 (Important) | 0 | 0 |
| 3 (Minor) | 0 | 0 |

### By Source Document

| Document | Cascades Triggered | Cascades Received |
|----------|-------------------|-------------------|
| [doc.md] | 0 | 0 |

---

## Cascade Resolution Protocol

When resolving a cascade:

1. **Review** the source change (CL-XXX) for context
2. **Open** the affected document
3. **Locate** the specific content requiring update
4. **Apply** the required changes
5. **Verify** no new cascades are triggered
6. **Log** the resolution as a new change entry (if substantive)
7. **Update** this tracker:
   - Move entry to "Resolved" section
   - Update statistics
   - Check for any new cascades from the resolution

---

## Priority Definitions

| Priority | Definition | Timeline |
|----------|------------|----------|
| **1 - Critical** | Broken functionality, contradictions, missing required content | Before next document |
| **2 - Important** | Inconsistencies, outdated references, related content | Before phase completion |
| **3 - Minor** | Style consistency, optional enhancements | Before delivery |

---

## Notes

[Any observations about cascade patterns, frequently affected documents, or systemic issues]
