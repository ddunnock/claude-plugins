# Source Tracking Reference

Protocols for maintaining traceability between source materials and generated documentation.

## Why Source Tracking

Source tracking ensures:
- **Auditability**: Every claim can be verified
- **Updates**: When sources change, affected docs are identifiable
- **Trust**: Clear evidence base for generated content
- **Collaboration**: Others can verify and extend work
- **AI Continuity**: Sessions can resume with clear context

## Source Reference System

### Source Identifiers

Assign unique identifiers to all sources:

| Prefix | Type | Example |
|--------|------|---------|
| `SRC-` | Document file | `SRC-01`, `SRC-02` |
| `REPO-` | Repository path | `REPO-01:/src/lib.rs` |
| `WEB-` | Web resource | `WEB-01:diataxis.fr` |
| `VERBAL-` | Verbal/stakeholder | `VERBAL-01:2025-01-15` |
| `INFER-` | Inference from context | `INFER-01:pattern-analysis` |

### Source Registry

Maintain a master registry:

```markdown
## Source Registry

### Documents

| ID | Name | Location | Type | Last Updated | Token Est. |
|----|------|----------|------|--------------|------------|
| SRC-01 | README | /repo/README.md | Markdown | 2025-01-15 | ~1,200 |
| SRC-02 | API Spec | /repo/docs/api.md | Markdown | 2025-01-10 | ~8,500 |
| SRC-03 | Config | /repo/docs/config.yaml | YAML | 2025-01-12 | ~500 |

### Repositories

| ID | Name | URL | Branch | Commit |
|----|------|-----|--------|--------|
| REPO-01 | Main | github.com/org/project | main | abc123 |

### Web Resources

| ID | Name | URL | Retrieved |
|----|------|-----|-----------|
| WEB-01 | Diátaxis | https://diataxis.fr | 2025-01-15 |
| WEB-02 | Competitor | https://example.com/docs | 2025-01-15 |

### Verbal/Stakeholder Input

| ID | Source | Date | Topic | Notes Location |
|----|--------|------|-------|----------------|
| VERBAL-01 | Product Manager | 2025-01-15 | Priorities | notes/pm-meeting.md |
```

## Reference Syntax

### Basic Reference

```markdown
The system uses REST APIs [SRC-02].
```

### Line-Specific Reference

```markdown
Authentication is handled via bearer tokens [SRC-02:45-52].
```

### Section Reference

```markdown
See the configuration schema [SRC-03:§authentication] for details.
```

### Multiple References

```markdown
The widget pipeline [SRC-01:25, SRC-02:100-120] connects components in sequence.
```

### Web Reference

```markdown
This follows Diátaxis principles [WEB-01:/tutorials].
```

### Verbal Reference

```markdown
Priority was given to API documentation [VERBAL-01:priorities].
```

### Inference Reference

```markdown
Based on code patterns, configuration follows YAML conventions [INFER-01:config-analysis].
```

## Evidence Grounding Markers

Mark the confidence level of information:

| Marker | Meaning | Usage |
|--------|---------|-------|
| `[VERIFIED: ref]` | Directly confirmed in source | Facts, specifications |
| `[INFERRED: ref]` | Reasonable inference | Patterns, conventions |
| `[ASSUMPTION]` | Not verified, needs validation | Best guesses |
| `[NEEDS: topic]` | Information gap | Placeholder for missing data |

### Examples

```markdown
## API Authentication

The API uses bearer tokens for authentication [VERIFIED: SRC-02:45].
Token expiration is set to 24 hours [VERIFIED: SRC-02:48].

Refresh tokens follow OAuth 2.0 conventions [INFERRED: SRC-02:50-55].
The refresh endpoint likely supports automatic renewal [ASSUMPTION].

Rate limit headers are not documented [NEEDS: rate-limiting-spec].
```

## Extraction Tracking

When extracting content from sources, track what was extracted:

### Extraction Log

```markdown
## Extraction Log: SRC-02 (API Spec)

### Extracted Content

| Lines | Destination | Type | Status |
|-------|-------------|------|--------|
| 1-20 | reference/api/overview.md | Overview | Complete |
| 21-44 | reference/api/endpoints.md | Endpoints | In Progress |
| 45-80 | reference/api/auth.md | Authentication | Complete |
| 81-120 | reference/api/errors.md | Error handling | Pending |

### Extraction Notes
- Lines 30-35: Contains outdated examples, need update
- Lines 60-65: References external OAuth spec, added [WEB-03]
- Lines 100-110: Conflicts with SRC-01, stakeholder clarification needed
```

## Output Tracking

For each generated document, track its sources:

### Document Source Map

```markdown
## Source Map: getting-started/quickstart.md

### Primary Sources
| Source | Usage | Sections |
|--------|-------|----------|
| SRC-01 | Installation steps | §Prerequisites, §Installation |
| SRC-02 | First API call | §Your First Request |
| VERBAL-01 | User journey | §Overview |

### Secondary Sources
| Source | Usage |
|--------|-------|
| WEB-02 | Structure inspiration |
| SRC-03 | Config defaults |

### Evidence Summary
- VERIFIED: 85% of content
- INFERRED: 10% of content
- ASSUMPTION: 5% of content (marked inline)

### Affected By Changes To
- SRC-01: Prerequisites, Installation sections
- SRC-02: First Request section
- SRC-03: Configuration defaults mention
```

## Cross-Reference Tracking

Track relationships between documentation pieces:

### Cross-Reference Matrix

```markdown
## Cross-Reference Matrix

| Document | Links To | Links From |
|----------|----------|------------|
| index.md | quickstart, concepts, reference | - |
| quickstart.md | installation, first-api | index |
| concepts/overview.md | quickstart, reference | index, quickstart |
| reference/api.md | concepts, how-to | index, quickstart |

### Orphan Detection
- [ORPHAN]: examples/advanced.md (no incoming links)
- [ORPHAN]: reference/deprecated.md (no incoming links)
```

## Version Tracking

Track source versions to detect staleness:

### Version Registry

```markdown
## Version Registry

### Current Versions

| Source | Version/Commit | Date | Hash |
|--------|----------------|------|------|
| SRC-01 | main:abc123 | 2025-01-15 | a1b2c3 |
| SRC-02 | v2.1.0 | 2025-01-10 | d4e5f6 |
| REPO-01 | main:abc123 | 2025-01-15 | - |

### Change Detection

| Source | Original Hash | Current Hash | Changed? |
|--------|---------------|--------------|----------|
| SRC-01 | a1b2c3 | a1b2c3 | No |
| SRC-02 | d4e5f6 | g7h8i9 | **YES** |

### Affected Documentation

When SRC-02 changed:
- reference/api/endpoints.md (HIGH impact)
- getting-started/quickstart.md (MEDIUM impact)
- concepts/architecture.md (LOW impact)
```

## Quality Markers

Track quality and completeness:

```markdown
## Quality Tracking: reference/api/auth.md

### Content Quality
| Aspect | Status | Notes |
|--------|--------|-------|
| Accuracy | ✅ Verified | All claims have source refs |
| Completeness | ⚠️ Partial | Missing OAuth flow diagram |
| Currency | ✅ Current | Matches SRC-02 v2.1.0 |
| Examples | ❌ Needs work | No code examples yet |

### Source Coverage
| Source Section | Covered | Notes |
|----------------|---------|-------|
| SRC-02:45-60 | 100% | Auth basics |
| SRC-02:61-75 | 80% | Token refresh |
| SRC-02:76-80 | 0% | Edge cases |

### Action Items
- [ ] Add code examples for token usage
- [ ] Document edge cases from SRC-02:76-80
- [ ] Create OAuth flow diagram
```

## Templates

### Source Entry Template

```markdown
## [SRC-XX]: [Document Name]

**Location**: [file path or URL]
**Type**: [Markdown/YAML/Code/External]
**Version**: [version or commit]
**Retrieved**: [date]
**Token Estimate**: [approximate tokens]

### Content Overview
[Brief description of what this source contains]

### Key Sections
- [Section 1]: [brief description]
- [Section 2]: [brief description]

### Extraction Status
| Section | Lines | Extracted | Destination |
|---------|-------|-----------|-------------|
| [name] | [range] | [yes/no] | [target doc] |

### Notes
[Any observations about quality, currency, gaps]
```

### Document Source Map Template

```markdown
## Source Map: [document-path]

**Created**: [date]
**Last Updated**: [date]
**Primary Quadrant**: [Tutorial/How-To/Reference/Explanation]

### Sources Used
| ID | Source | Sections | Confidence |
|----|--------|----------|------------|
| [ref] | [name] | [sections] | [VERIFIED/INFERRED/ASSUMPTION] |

### Dependencies
| Depends On | Reason |
|------------|--------|
| [doc-path] | [why] |

### Dependents
| Depended By | Reason |
|-------------|--------|
| [doc-path] | [why] |

### Change Impact
If this document changes, update:
- [doc-path]: [what to update]
```
