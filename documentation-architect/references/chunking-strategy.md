# Chunking Strategy Reference

Strategies for processing large documentation projects within AI context limits while maintaining coherence and traceability.

## Core Problem

AI assistants have context window limits. Large documentation projects may include:
- Extensive source code requiring documentation
- Multiple existing document files
- Large specification documents
- External resources and references

This requires processing in chunks while maintaining:
- **Coherence**: Consistent terminology and structure across chunks
- **Traceability**: Every output traces to specific sources
- **Continuity**: Each session builds on previous work
- **Completeness**: Nothing falls through the cracks

## Chunking Principles

### 1. Index Before Content

Create index notes before processing content:

```markdown
## Master Index

### Source Documents
| ID | Document | Location | Tokens | Status |
|----|----------|----------|--------|--------|
| SRC-01 | README.md | /repo/README.md | ~1,200 | Pending |
| SRC-02 | API Spec | /repo/docs/api.md | ~8,500 | Pending |
| SRC-03 | Config Guide | /repo/docs/config.md | ~3,200 | Pending |

### Processing Order
1. SRC-01: Foundation context
2. SRC-03: Configuration (self-contained)
3. SRC-02: API (references SRC-03)
```

### 2. Dependency-Aware Ordering

Process chunks in dependency order:

```
Level 0 (No Dependencies):
├── Core terminology definitions
├── Project overview/context
└── Independent reference material

Level 1 (Depends on Level 0):
├── Feature documentation
├── API reference
└── Configuration guides

Level 2 (Depends on Level 1):
├── Tutorial content
├── Integration guides
└── Advanced how-tos
```

### 3. Carry-Forward Notes

Each chunk produces notes for subsequent chunks:

```markdown
## Carry-Forward Notes: Chunk 1 → Chunk 2

### Terminology Established
- **Widget**: Core processing unit (see SRC-01:15-20)
- **Pipeline**: Sequence of widgets (see SRC-01:25-30)

### Structural Decisions
- API reference uses RESTful conventions
- Configuration uses YAML format
- Naming follows kebab-case

### Open Questions
- [ ] How are widgets versioned? (Answer in Chunk 3)
- [ ] What's the deprecation policy? (Needs stakeholder input)

### Cross-References Needed
- Widget API endpoints (generate in Chunk 2)
- Configuration schema (generate in Chunk 3)
```

### 4. Source Reference Protocol

Every extracted piece of information includes source reference:

```markdown
The system uses a pipeline architecture [SRC-01:25-30] where widgets 
are connected in sequence [SRC-02:§3.1]. Configuration is stored in 
YAML format [SRC-03:10-15].
```

Reference format:
- `[SRC-XX:line-range]` - Specific lines
- `[SRC-XX:§section]` - Named section
- `[SRC-XX:~topic]` - Topic search
- `[WEB:url]` - Web source
- `[VERBAL:date]` - Verbal/stakeholder input

## Chunk Size Guidelines

### Optimal Chunk Sizes

| Content Type | Token Target | Rationale |
|--------------|--------------|-----------|
| Foundation context | 2,000-3,000 | Establish terminology |
| Reference section | 4,000-6,000 | Complete one section |
| Tutorial chapter | 3,000-5,000 | One learning unit |
| How-to guide | 2,000-4,000 | One complete task |
| Explanation topic | 3,000-5,000 | One concept |

### Buffer for Generation

Reserve ~30% of context for generation:
- If context limit is 100K tokens
- Allow ~70K for source + notes
- Reserve ~30K for output generation

## Chunk Session Protocol

### Starting a New Session

```markdown
## Session Start Checklist

### Load Context
- [ ] Master index (current state)
- [ ] Carry-forward notes from previous session
- [ ] Relevant source references for this chunk
- [ ] Work breakdown structure (current item)

### Verify State
- [ ] Previous chunk outputs available?
- [ ] Terminology consistent with established definitions?
- [ ] Dependencies from previous chunks resolved?

### Session Scope
- **Chunk ID**: [chunk identifier]
- **WBS Items**: [items to complete]
- **Sources Required**: [SRC-XX, SRC-YY]
- **Expected Outputs**: [deliverables]
```

### During Session

Track progress inline:

```markdown
## Session Progress: Chunk 3

### Completed
- [x] API endpoint documentation (SRC-02:100-250)
- [x] Error response reference (SRC-02:300-350)

### In Progress
- [ ] Authentication section (SRC-02:50-99)

### Blocked
- [ ] Rate limiting details (needs stakeholder clarification)

### Notes for Next Session
- Rate limit defaults unclear in source
- Consider adding code examples to auth section
```

### Ending a Session

```markdown
## Session End Checklist

### Outputs Produced
- [ ] [Document/file created]
- [ ] [Notes updated]

### Carry-Forward Notes Updated
- [ ] Terminology additions recorded
- [ ] Decisions documented
- [ ] Open questions listed
- [ ] Cross-references noted

### Master Index Updated
- [ ] Source status updated
- [ ] Chunk progress recorded
- [ ] Next chunk identified

### Handoff Ready
- [ ] All outputs saved
- [ ] Context summary created
- [ ] Next session can start cleanly
```

## Context Compression Techniques

### 1. Progressive Summarization

After processing a section, create compressed summary:

```markdown
## Summary: API Authentication (from SRC-02:50-99)

**Key Points**:
- Bearer token required for all endpoints
- Tokens expire after 24 hours
- Refresh via /auth/refresh endpoint

**Reference for Details**: See generated auth-reference.md

**Token Reduction**: 2,500 → 150 tokens
```

### 2. Reference Extraction

Extract frequently-needed information to standalone notes:

```markdown
## Quick Reference: HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | Success | All successful GET/POST |
| 201 | Created | Resource creation |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Auth required/failed |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limited | Slow down |
| 500 | Server Error | Internal failure |

**Source**: [SRC-02:300-350]
```

### 3. Decision Log

Track decisions without re-explaining rationale:

```markdown
## Decisions Log

| ID | Decision | Rationale | Source |
|----|----------|-----------|--------|
| D-01 | Use kebab-case for URLs | Consistency with existing API | [SRC-02:10] |
| D-02 | YAML for config | Stakeholder preference | [VERBAL:2025-01-15] |
| D-03 | No XML support | Low usage, maintenance burden | [SRC-05:§deprecation] |
```

## Multi-Session Workflow

### Session 0: Setup

```
Outputs:
├── master-index.md (all sources catalogued)
├── terminology.md (initial definitions)
├── structure-plan.md (target documentation structure)
└── wbs.md (work breakdown with chunk assignments)
```

### Sessions 1-N: Content Processing

```
Inputs:
├── master-index.md (current state)
├── carry-forward-notes.md (from previous session)
├── [sources for this chunk]
└── [previous outputs if dependencies]

Outputs:
├── [documentation content]
├── carry-forward-notes.md (updated)
└── master-index.md (updated)
```

### Final Session: Integration

```
Inputs:
├── All generated documentation
├── Complete carry-forward notes
└── Master index

Outputs:
├── Integrated documentation set
├── Cross-reference validation
├── Completion report
└── Gap analysis (if any)
```

## Troubleshooting

### Context Overflow

**Symptom**: Unable to load required sources
**Solutions**:
1. Split chunk into smaller pieces
2. Summarize completed sections more aggressively
3. Load only directly-needed sources
4. Use reference notes instead of full sources

### Lost Context

**Symptom**: Inconsistent terminology or contradictions
**Solutions**:
1. Always start with carry-forward notes
2. Include terminology reference in each session
3. Review previous session outputs before starting
4. Maintain decision log for rationale

### Source Gaps

**Symptom**: Information needed not in available sources
**Solutions**:
1. Mark as `[NEEDS: description]` in output
2. Add to open questions in carry-forward notes
3. Research via web search if appropriate
4. Escalate to stakeholder for input

### Chunk Boundaries

**Symptom**: Content doesn't fit neatly into chunks
**Solutions**:
1. Prefer natural content boundaries (chapters, sections)
2. When splitting mid-section, include overlap context
3. Document split points in master index
4. Include cross-references between related chunks
