# Clarify Session Log

Session ID: [SESSION_ID]
Started: [ISO_TIMESTAMP]
Completed: [ISO_TIMESTAMP]
Questions Asked: [COUNT]
Questions Answered: [COUNT]

## Session Summary

**Target File**: [SPEC_FILE]
**Initial Ambiguities**: [COUNT]
**Resolved This Session**: [COUNT]
**Remaining**: [COUNT]

---

## Questions & Answers

### CLARIFY-001 [CATEGORY]

**Timestamp**: [ISO_TIMESTAMP]
**Location**: [file:line]
**Priority**: [HIGH/MEDIUM/LOW]

**Context**:
[Why this question matters - what depends on the answer]

**Question**:
[The question that was asked]

**Options Presented**:
1. [Option 1]
2. [Option 2]
3. [Option 3]
4. Other

**Answer**: [OPTION_NUMBER or "Other: [text]"]
**Answer Text**: [Full answer text]

**Spec Update**:
```markdown
# Before
[Original text]

# After
[Updated text with clarification]
```

**Files Updated**:
- [file:line] - [brief description of change]

---

### CLARIFY-002 [CATEGORY]

**Timestamp**: [ISO_TIMESTAMP]
**Location**: [file:line]
**Priority**: [HIGH/MEDIUM/LOW]

**Context**:
[Context]

**Question**:
[Question]

**Options Presented**:
1. [Option 1]
2. [Option 2]
3. [Option 3]
4. Other

**Answer**: [Answer]

**Spec Update**:
```markdown
# Before
[Original]

# After
[Updated]
```

**Files Updated**:
- [file:line]

---

## Files Modified

| File | Changes | Lines Affected |
|------|---------|----------------|
| [file1] | [N] | [line numbers] |
| [file2] | [N] | [line numbers] |

## Remaining Ambiguities

### By Priority

**HIGH** ([COUNT]):
- [Location]: [Brief description]
- [Location]: [Brief description]

**MEDIUM** ([COUNT]):
- [Location]: [Brief description]

**LOW** ([COUNT]):
- [Location]: [Brief description]

### By Category

| Category | Count | Locations |
|----------|-------|-----------|
| SCOPE | [N] | [list] |
| BEHAVIOR | [N] | [list] |
| DATA | [N] | [list] |
| ERROR | [N] | [list] |
| SEQUENCE | [N] | [list] |
| CONSTRAINT | [N] | [list] |
| INTERFACE | [N] | [list] |
| AUTHORITY | [N] | [list] |
| TEMPORAL | [N] | [list] |

---

## Next Steps

1. [Recommended action based on session results]
2. [Additional clarifications needed]
3. [Related commands to run]
