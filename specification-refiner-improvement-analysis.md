# Specification-Refiner Skill: Comprehensive Improvement Analysis

**Date**: January 15, 2026
**Author**: Claude Analysis
**Version**: 1.0

---

## Executive Summary

This analysis identifies critical gaps in the `specification-refiner` skill and provides actionable recommendations for improvement. The key issues are:

1. **Phase Skipping**: Phases are often bypassed due to lack of enforcement mechanisms
2. **Insufficient Research**: No structured research or external grounding requirements
3. **MCP Integration**: session-memory and streaming-output MCPs are not mandatory
4. **No Hook Integration**: Missing PreToolUse/PostToolUse hooks for phase enforcement

---

## Part 1: Phase Skipping Problem Analysis

### Root Causes Identified

#### 1.1 Gate Enforcement is Purely Advisory

The current skill says "Wait for user confirmation" but provides no enforcement mechanism. The agent can proceed without confirmation because:

- No hook validates phase completion before tool execution
- No MCP records phase transitions requiring acknowledgment
- No checksum or state validation between phases

**Evidence from SKILL.md**:
```
Each phase ends with a **full summary gate** requiring user confirmation before proceeding.
```

This is stated but not enforced programmatically.

#### 1.2 Phase 0 (ASSESS) is Particularly Vulnerable

Phase 0 is designed to determine SIMPLE vs COMPLEX mode, but:
- There's no mandatory delay or research requirement
- The complexity assessment factors are subjective
- Nothing prevents jumping straight to Phase 1

#### 1.3 Missing State Persistence

The `analysis-state.md` file is mentioned but:
- Writing it is not enforced via hooks
- No validation that it exists before phase transitions
- No checksum verification of state consistency

### Recommended Fixes for Phase Skipping

#### Fix 1.1: Add Mandatory Hook Configuration

Create `.claude/hooks.json` with phase enforcement:

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": ["Write", "Edit"],
      "type": "command",
      "command": "python3 $CLAUDE_PROJECT_DIR/.claude/scripts/validate-phase.py",
      "timeout": 5
    },
    {
      "event": "PostToolUse",
      "matcher": "mcp__session-memory__*",
      "type": "command",
      "command": "python3 $CLAUDE_PROJECT_DIR/.claude/scripts/verify-state.py"
    }
  ]
}
```

#### Fix 1.2: Add Phase Gate Checklist Requirements

Each phase should have explicit completion criteria that are machine-verifiable:

```markdown
### Phase 0 Gate Requirements (MANDATORY)
- [ ] session_init called with skill_name="specification-refiner"
- [ ] Complexity assessment recorded via session_record
- [ ] Mode selection (SIMPLE/COMPLEX) recorded
- [ ] User confirmation received (recorded as decision event)
- [ ] analysis-state.md created with Phase 0 data

**CANNOT PROCEED TO PHASE 1 UNTIL ALL BOXES CHECKED**
```

#### Fix 1.3: Integrate session-memory MCP as MANDATORY

Add to SKILL.md preamble:

```markdown
## MANDATORY MCP INTEGRATION

This skill REQUIRES the following MCPs to be active:

1. **session-memory**: For phase tracking, decision recording, and session handoff
2. **streaming-output**: For long specification documents (>1000 lines)

### On Skill Start
IMMEDIATELY call:
```json
{
  "tool": "mcp__session-memory__session_init",
  "params": {
    "skill_name": "specification-refiner"
  }
}
```

### On Every Phase Transition
MUST call:
```json
{
  "tool": "mcp__session-memory__session_record",
  "params": {
    "category": "phase",
    "type": "phase_start",
    "data": {"phase": "PHASE_NAME", "previous_phase": "PREV_NAME"}
  }
}
```

**Failure to use these MCPs is a skill violation.**
```

---

## Part 2: Research and Grounding Deficiencies

### Current State

The skill focuses on internal document analysis but lacks:

1. **External Research Requirements**: No mandate to verify against standards
2. **Source Grounding**: No requirement to cite sources for findings
3. **Validation Against Standards**: No reference to IEEE 830, ISO 29148, or INCOSE guidelines

### Industry Standards That Should Be Referenced

Based on research, the skill should integrate these frameworks:

#### 2.1 ISO/IEC/IEEE 29148:2018

This is the current international standard that supersedes IEEE 830. Key quality criteria from ISO 29148:

| Characteristic | Description |
|---------------|-------------|
| C1 - Necessary | Requirement is essential |
| C2 - Implementation-free | Describes WHAT not HOW |
| C3 - Unambiguous | Single interpretation |
| C4 - Consistent | No conflicts with other requirements |
| C5 - Complete | Sufficient information |
| C6 - Singular | One requirement per statement |
| C7 - Feasible | Technically achievable |
| C8 - Traceable | Linked to source |
| C9 - Verifiable | Can be tested |

**Recommendation**: Add ISO 29148 quality criteria as a mandatory analysis lens.

#### 2.2 INCOSE Guide to Writing Requirements (v4.0)

INCOSE provides 42 rules across 12 categories for requirement quality. Key rules include:

- **Rule 1**: Use "shall" for requirements, "will" for facts, "should" for goals
- **Rule 6**: Avoid vague terms (adequate, appropriate, as required)
- **Rule 12**: One requirement per sentence
- **Rule 23**: Include rationale for each requirement
- **Rule 35**: Requirements must be verifiable

**Recommendation**: Add INCOSE rules as a validation checklist in Phase 2 (ANALYZE).

### Recommended Research Integration

#### 2.3 Add Mandatory Research Phase

Insert a new Phase 1.5 or enhance Phase 2:

```markdown
## Phase 2: ANALYZE (Enhanced)

### Pre-Analysis Research (MANDATORY)

Before running SEAMS analysis, the agent MUST:

1. **Identify Domain Standards**
   - Use WebSearch to find applicable standards for the document's domain
   - Record findings via session_record with category="research"

2. **Retrieve Reference Materials**
   - If domain-specific standards exist, fetch key criteria
   - Document sources with URLs

3. **Ground Quality Criteria**
   - Map ISO 29148 characteristics to document requirements
   - Apply INCOSE rules to individual requirement statements

4. **Record Research Summary**
   Call session_record:
   ```json
   {
     "category": "research",
     "type": "standards_grounding",
     "data": {
       "standards_identified": ["ISO 29148", "INCOSE GTWR v4"],
       "domain_standards": ["list specific domain standards"],
       "sources": ["URLs"]
     }
   }
   ```

### Research-Grounded Analysis

All findings MUST include:
- **Source**: Standard or principle violated
- **Evidence**: Specific text from document
- **Confidence**: Based on standard clarity (High if explicit rule, Medium if interpreted, Low if heuristic)
```

#### 2.4 Add References Directory Content

The skill has a `references/` directory but lacks standards content. Add:

```
references/
├── iso-29148-criteria.md      # Summary of ISO 29148 characteristics
├── incose-rules-summary.md    # Key INCOSE rules (1-42)
├── seams-framework.md         # Existing
├── critical-path-analysis.md  # Existing
├── quality-checklist.md       # NEW: Combined validation checklist
└── research-sources.md        # NEW: Template for documenting research
```

---

## Part 3: Hook Integration Requirements

### Current Gap

The skill has no hook configuration. Hooks would solve the phase-skipping problem by:
- Validating state before tool execution
- Recording tool usage automatically
- Enforcing phase gates

### Recommended Hook Configuration

Create `/skills/specification-refiner/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ["Write", "Edit"],
        "type": "prompt",
        "prompt": "Before writing, verify: (1) Current phase is documented in analysis-state.md (2) Previous phase gate was completed (3) session_record was called for phase transition. If ANY of these are false, STOP and complete the missing step first."
      },
      {
        "matcher": "mcp__streaming-output__stream_write",
        "type": "command",
        "command": "test -f analysis-state.md && grep -q 'Phase: OUTPUT' analysis-state.md",
        "timeout": 3
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__session-memory__session_record",
        "type": "prompt",
        "prompt": "After recording, verify the event was captured correctly. If this was a phase transition, update analysis-state.md immediately."
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 -c \"import json; print('Session ended - creating handoff...')\" && mcp__session-memory__session_handoff",
        "timeout": 30
      }
    ]
  }
}
```

### Hook Use Cases for Phase Enforcement

| Phase | PreToolUse Check | PostToolUse Action |
|-------|-----------------|-------------------|
| ASSESS | Verify session_init called | Record mode selection |
| INGEST | Verify ASSESS complete | Update analysis-state.md |
| ANALYZE | Verify document parsed | Record findings |
| PRESENT | Verify findings exist | Record user choices |
| ITERATE | Verify user input received | Record delta |
| SYNTHESIZE | Verify user approval | Record synthesis |
| OUTPUT | Verify synthesis approved | Trigger streaming-output |
| VALIDATE | Verify output generated | Record final status |

---

## Part 4: MCP Integration Requirements

### 4.1 session-memory MCP (MANDATORY)

The existing `SpecRefinerPlugin` in `/mcps/session-memory/plugins/spec_refiner.py` is well-designed but not mandated. Changes needed:

#### Current Plugin Capabilities
- Tracks phases, findings, questions, assumptions
- Calculates progress based on phase
- Generates resumption context
- Handles phase transitions, question lifecycle, finding tracking

#### Required Changes to SKILL.md

Add mandatory integration section:

```markdown
## MCP Integration (MANDATORY)

### session-memory MCP

The specification-refiner skill MUST use the session-memory MCP for all phase tracking.

#### Required Calls

| Action | MCP Tool | When |
|--------|----------|------|
| Start session | `session_init` | Immediately on skill activation |
| Phase transition | `session_record` (category: phase) | Before starting any new phase |
| Finding discovered | `session_record` (category: finding) | Immediately when issue identified |
| Question raised | `session_record` (category: question) | When question arises |
| Decision made | `session_record` (category: decision) | When user chooses option |
| Checkpoint | `session_checkpoint` | At each phase gate |
| Session end | `session_handoff` | On completion or context limit |

#### Example: Phase Transition

```json
{
  "tool": "mcp__session-memory__session_record",
  "params": {
    "category": "phase",
    "type": "phase_start",
    "data": {
      "phase": "ANALYZE",
      "mode": "COMPLEX",
      "document_title": "API Specification v2.0"
    }
  }
}
```

#### Example: Creating Checkpoint at Gate

```json
{
  "tool": "mcp__session-memory__session_checkpoint",
  "params": {
    "name": "phase-2-complete",
    "summary": "ANALYZE phase complete. 12 findings (3 critical). 5 open questions."
  }
}
```

**CRITICAL**: Failure to use session-memory means phase state is lost on context compaction.
```

### 4.2 streaming-output MCP (CONDITIONAL MANDATORY)

Required when output exceeds 1000 lines (typical for COMPLEX mode specifications).

Add to SKILL.md:

```markdown
### streaming-output MCP (Conditional)

Use streaming-output for specifications exceeding 1000 lines:

#### When to Use
- COMPLEX mode output (multiple A-Spec/B-Spec files)
- Traceability matrices with >50 requirements
- Any specification with >15 sections

#### Workflow

1. **Initialize stream**:
```json
{
  "tool": "mcp__streaming-output__stream_start",
  "params": {
    "title": "Authentication A-Spec",
    "schema_type": "findings",
    "blocks": [
      {"key": "header", "type": "section"},
      {"key": "requirements", "type": "section"},
      {"key": "traceability", "type": "section"}
    ]
  }
}
```

2. **Write sections incrementally**:
```json
{
  "tool": "mcp__streaming-output__stream_write",
  "params": {
    "document_id": "doc_xxx",
    "block_key": "requirements",
    "content": {"title": "Requirements", "body": "..."},
    "block_type": "section"
  }
}
```

3. **Check status on resume**:
```json
{
  "tool": "mcp__streaming-output__stream_status",
  "params": {"document_id": "doc_xxx", "verify": true}
}
```

**CRITICAL**: For documents >1000 lines, using manual file writes risks content loss on context compaction.
```

---

## Part 5: Structural Improvements to SKILL.md

### 5.1 Add Explicit Anti-Skip Mechanisms

Insert after workflow diagram:

```markdown
## Phase Enforcement Mechanisms

### Verification Requirements

Each phase MUST complete these steps before the next phase can begin:

| Phase | Verification | Evidence Required |
|-------|--------------|-------------------|
| 0 ASSESS | Mode selected and recorded | session_record call with mode |
| 1 INGEST | Document structure captured | analysis-state.md updated |
| 2 ANALYZE | SEAMS analysis complete | Findings recorded |
| 3 PRESENT | User reviewed findings | Decision events recorded |
| 4 ITERATE | Changes incorporated | Delta analysis complete |
| 5 SYNTHESIZE | User approved summary | Approval decision recorded |
| 6 OUTPUT | Specs generated | Files exist, session updated |
| 7 VALIDATE | Validation complete | Status advanced |

### Skip Prevention

If the agent attempts to proceed without completing verification:
1. The hook will fail the PreToolUse check
2. The agent MUST return to complete the missing step
3. The missing step must be recorded before retry

### Emergency Bypass

If a user explicitly requests skipping a phase:
1. Record the skip decision: `session_record(category="decision", type="phase_skip", data={...})`
2. Document rationale in analysis-state.md
3. Note that skipped phases may result in incomplete analysis
```

### 5.2 Add Research Requirements Section

Insert new section after Phase 1:

```markdown
## Research Requirements

### Mandatory External Validation

The specification-refiner skill MUST ground its analysis in industry standards.

### Required Research Steps

1. **Domain Identification**
   - What domain does this specification address? (software, systems, embedded, etc.)
   - What industry standards apply?

2. **Standard Retrieval**
   - Use WebSearch to find current standards
   - Preference order: ISO > IEEE > INCOSE > Domain-specific

3. **Quality Framework Application**
   - Apply ISO 29148 quality characteristics
   - Apply relevant INCOSE rules
   - Document which standards inform each finding

### Research Documentation Template

For each finding, include:
```markdown
**Finding**: [Description]
**Grounding**:
  - Standard: [e.g., ISO 29148 C3 - Unambiguous]
  - Rule: [e.g., INCOSE Rule 6 - Avoid vague terms]
  - Source: [URL or reference]
**Confidence**: [High/Medium/Low based on standard clarity]
```

### Minimum Research Requirements by Mode

| Mode | Minimum Research |
|------|-----------------|
| SIMPLE | ISO 29148 characteristics applied |
| COMPLEX | ISO 29148 + INCOSE rules + domain standards |
```

### 5.3 Add VALIDATE Phase (Phase 7) Missing Content

The current Phase 7 exists but is underdeveloped. Enhance:

```markdown
## Phase 7: VALIDATE (Enhanced)

Phase 7 is MANDATORY for both SIMPLE and COMPLEX modes.

### Validation Checklist

#### Quality Validation
- [ ] All requirements are verifiable (ISO 29148 C9)
- [ ] All requirements are traceable (ISO 29148 C8)
- [ ] No ambiguous language (INCOSE Rules 6, 7, 8)
- [ ] Each requirement is singular (ISO 29148 C6)

#### Structural Validation
- [ ] All cross-references resolve
- [ ] Terminology is consistent
- [ ] Requirement IDs are unique and sequential
- [ ] RTM coverage ≥95% (COMPLEX mode)

#### Grounding Validation
- [ ] All critical findings cite a standard
- [ ] Research sources are documented
- [ ] Assumptions are marked with validation method

### Validation Report Template

Generate validation-report.md with:
1. Validation summary (pass/fail counts)
2. Standards compliance matrix
3. Research grounding summary
4. Outstanding issues
5. Approval recommendation
```

---

## Part 6: Implementation Priority Matrix

| Priority | Change | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Add session-memory MCP as mandatory | Low | High |
| P0 | Add phase enforcement hooks | Medium | High |
| P1 | Add research requirements section | Medium | High |
| P1 | Add ISO 29148 / INCOSE references | Low | Medium |
| P1 | Add streaming-output for long docs | Low | Medium |
| P2 | Enhance Phase 7 (VALIDATE) | Medium | Medium |
| P2 | Add verification checklist per phase | Low | Medium |
| P3 | Add anti-skip mechanisms | Low | Low |
| P3 | Create reference materials | Medium | Low |

---

## Part 7: Validation of Recommendations

### Against Known Issues

| Issue | Root Cause | Recommended Fix | Addresses Issue? |
|-------|------------|-----------------|------------------|
| Phases skipped | No enforcement | Hooks + MCP mandatory | ✓ Yes |
| Insufficient research | No requirement | Research section added | ✓ Yes |
| Poor grounding | No standards reference | ISO/INCOSE integration | ✓ Yes |
| State lost on compaction | No persistence | session-memory mandatory | ✓ Yes |
| Long docs corrupted | Manual file writes | streaming-output required | ✓ Yes |

### Against Industry Standards

| Standard | Current Compliance | After Changes |
|----------|-------------------|---------------|
| ISO 29148 | Not referenced | Mandatory application |
| INCOSE GTWR v4 | Not referenced | Rules 1-42 applied |
| IEEE 830 | Partially aligned | Superseded by ISO 29148 |

---

## Sources

- [IEEE 830-1998 Standard](https://ieeexplore.ieee.org/document/720574)
- [ISO/IEC/IEEE 29148:2018](https://drkasbokar.com/wp-content/uploads/2024/09/29148-2018-ISOIECIEEE.pdf)
- [INCOSE Guide to Writing Requirements v4](https://www.incose.org/docs/default-source/working-groups/requirements-wg/gtwr/incose_rwg_gtwr_v4_040423_final_drafts.pdf)
- [INCOSE 42-Rule Guide Summary](https://reqi.io/articles/incose-requirements-quality-42-rule-guide)
- [Claude Code Hooks Reference](https://docs.claude.com/en/docs/claude-code/hooks)
- [Requirements Validation Best Practices](https://testsigma.com/blog/requirement-validation/)
- [Generative AI in Requirements Engineering (2025)](https://onlinelibrary.wiley.com/doi/full/10.1002/spe.70029)

---

## Appendix A: Proposed Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ["Write", "Edit"],
        "type": "prompt",
        "prompt": "PHASE CHECK: Before writing any output, verify: (1) session_init was called (2) Current phase is recorded (3) Previous phase gate is complete. If not, STOP and complete missing steps.",
        "timeout": 5
      },
      {
        "matcher": "mcp__streaming-output__stream_write",
        "type": "prompt",
        "prompt": "STREAMING CHECK: Verify you are in Phase 6 (OUTPUT) and synthesis was approved. If not, return to appropriate phase."
      }
    ],
    "PostToolUse": [
      {
        "matcher": "mcp__session-memory__session_record",
        "type": "prompt",
        "prompt": "After recording event, update analysis-state.md to reflect current state. This is mandatory for phase tracking."
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "echo 'Generating handoff summary...'",
        "timeout": 5
      }
    ]
  }
}
```

---

## Appendix B: ISO 29148 Quality Characteristics Quick Reference

| ID | Characteristic | Test Question |
|----|---------------|---------------|
| C1 | Necessary | Is this requirement essential to stakeholder needs? |
| C2 | Implementation-free | Does it describe WHAT without specifying HOW? |
| C3 | Unambiguous | Is there only one possible interpretation? |
| C4 | Consistent | Does it conflict with any other requirement? |
| C5 | Complete | Is all information present to implement? |
| C6 | Singular | Does it express exactly one requirement? |
| C7 | Feasible | Is it technically and economically achievable? |
| C8 | Traceable | Can it be linked to source and downstream artifacts? |
| C9 | Verifiable | Can compliance be tested or demonstrated? |

---

## Appendix C: INCOSE Rules Summary (Top 20)

| Rule | Title | Description |
|------|-------|-------------|
| 1 | Use "shall" | Use "shall" for requirements, "will" for facts |
| 2 | Active voice | Write in active voice |
| 3 | Definite articles | Use "the" not "a/an" for specificity |
| 4 | Complete sentences | Each requirement is a complete sentence |
| 5 | Avoid pronouns | Replace pronouns with nouns |
| 6 | Avoid vague terms | No "adequate", "appropriate", "as required" |
| 7 | Avoid escape clauses | No "if practical", "as applicable" |
| 8 | Avoid subjective | No "user-friendly", "easy to use" |
| 9 | Positive form | State what shall be, not what shall not |
| 10 | One requirement | One requirement per statement |
| 11 | Avoid lists | Use separate requirements, not bulleted lists |
| 12 | Define terms | All terms must be defined |
| 13 | Units | Include units for all quantities |
| 14 | Tolerance | Specify acceptable ranges |
| 15 | Measurable | All requirements must be measurable |
| 16 | Complete | No TBD, TBS, TBR |
| 17 | Consistent | Use terms consistently throughout |
| 18 | Non-redundant | Don't repeat requirements |
| 19 | Rationale | Include rationale for each requirement |
| 20 | Unique ID | Each requirement has unique identifier |
