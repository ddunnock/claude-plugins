# Research Findings for requirements-dev Plugin

## Part 1: Codebase Patterns (Existing Plugin Architecture)

### Concept-Dev Reference Implementation Structure

```
concept-dev/
├── .claude-plugin/plugin.json     # Minimal manifest (name, version, author)
├── SKILL.md                       # Skill definition with frontmatter + phases
├── README.md / HOW_TO_USE.md      # User documentation
├── agents/                        # 7 agent definitions (markdown files)
│   ├── ideation-partner.md        # sonnet model
│   ├── problem-analyst.md         # sonnet
│   ├── concept-architect.md       # sonnet
│   ├── domain-researcher.md       # sonnet
│   ├── gap-analyst.md             # sonnet
│   ├── skeptic.md                 # opus (critical verification)
│   └── document-writer.md         # sonnet
├── commands/                      # 9 slash commands (concept.init, concept.spitball, etc.)
├── hooks/                         # PostToolUse hooks for auto-state updates
│   ├── hooks.json
│   └── scripts/update-state-on-write.sh
├── scripts/                       # 6 Python scripts (stdlib only, no deps)
│   ├── init_session.py            # Workspace creation + state init
│   ├── update_state.py            # Atomic state management (subcommands)
│   ├── source_tracker.py          # Source registry CRUD
│   ├── assumption_tracker.py      # Assumption registry CRUD
│   ├── check_tools.py             # Research tool availability detection
│   └── web_researcher.py          # crawl4ai integration
├── templates/                     # state.json template + document templates
└── references/                    # Procedural guidelines
```

### Key Patterns

**State Management (state.json):**
- Phase-gated workflow: phases must pass prerequisite gates before proceeding
- Three statuses: `not_started` → `in_progress` → `completed`
- Atomic writes: temp-file-then-rename for crash safety
- Subcommands: set-phase, pass-gate, set-artifact, update, check-gate, sync-counts, show
- Dotted-path updates for nested counters

**JSON Registries (source_registry.json, assumption_registry.json):**
- Structured entries with unique IDs (SRC-xxx, ASN-xxx)
- Metadata block (created, last_modified, version)
- Auto-sync counts to state.json after mutations
- Atomic file operations (temp-file-then-rename)
- CLI interface via argparse with subcommands (add, resolve, list, export)

**Plugin Manifest (plugin.json):**
```json
{
  "name": "concept-dev",
  "description": "...",
  "version": "1.1.4",
  "author": { "name": "dunnock" },
  "keywords": [...]
}
```

**SKILL.md Frontmatter:**
```yaml
---
name: concept-dev
description: trigger conditions and use cases
version: 1.0.0
tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Grep, Glob, Task, AskUserQuestion
model: sonnet
---
```

**Security Patterns (mandatory across all plugins):**
- `_validate_path()` on all CLI file arguments — rejects `..` traversal, restricts extensions
- `html.escape()` via `esc()` helper for all user content in HTML output
- External content wrapped in BEGIN/END markers
- No hardcoded API keys (extracted to env vars)
- SHA-256 for content hashing (not MD5)

**Hook Pattern (hooks.json):**
```json
{
  "hooks": [{
    "event": "PostToolUse",
    "matcher": { "tool_name": "Write", "path_pattern": "**/.concept-dev/*.md" },
    "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/update-state-on-write.sh \"$TOOL_INPUT_PATH\""
  }]
}
```

**Agent Pattern:**
- Markdown file with frontmatter (name, description, model)
- Behavioral rules, output format, integration points
- Invoked via Task tool: `subagent_type: "concept-dev:skeptic"`
- Opus model reserved for critical verification (skeptic agent)

**Testing:**
- pytest with pytest-asyncio for MCP tests
- Coverage: `--cov-fail-under=80`
- Type checking: pyright (zero errors)
- Linting: ruff
- Secrets: extracted to conftest.py fixtures sourced from env vars

**Design Principles:**
1. Gate discipline — mandatory user approval before phase advancement
2. Source grounding — all claims backed by registered sources
3. Skeptic verification — critical claims reviewed before user presentation
4. Metered questioning — 3-4 questions per turn, checkpoint, then proceed
5. Workspace isolation — all session data in `.concept-dev/` subdirectory

---

## Part 2: INCOSE GtWR v4 Rule Automation

### Rule Classification by Automation Tier

**Fully Automatable (21 rules) — regex/NLP pattern matching:**

| Rule | Name | Detection Approach |
|------|------|--------------------|
| R2 | Active Voice | spaCy dependency parsing (nsubjpass) or PassivePy |
| R5 | Definite Articles | Regex for indefinite articles in definite contexts |
| R6 | Common Units of Measure | Regex against unit dictionary |
| R7 | Vague Terms | Word-list: "some", "any", "allowable", "several", "many", "adequate", "sufficient", etc. |
| R8 | Escape Clauses | Word-list: "so far as possible", "if practicable", "as appropriate", etc. |
| R9 | Open-Ended Clauses | Pattern: "including but not limited to", "etc.", "and so on" |
| R10 | Superfluous Infinitives | Regex: "be able to", "be capable of" |
| R12-14 | Grammar/Spelling/Punctuation | LanguageTool, spell-check |
| R15 | Logical Expressions | Regex: "and/or" |
| R16 | Use of "Not" | Regex: `\bnot\b` |
| R17 | Oblique Symbol | Regex: `/` as "and/or" |
| R19 | Combinators | Regex: `\b(and|or|then|unless)\b` |
| R20 | Purpose Phrases | Regex: "in order to", "so that" |
| R21 | Parentheses | Regex: `\(.*?\)` |
| R24 | Pronouns | Regex: `\b(it|they|this|that|these|those|which)\b` |
| R26 | Absolutes | Word-list: "always", "never", "every", "all", "none" |
| R32 | Universal Qualification | Regex: "each", "every", "all", "any" |
| R33 | Range of Values | Pattern matching for numeric ranges |
| R35 | Temporal Dependencies | Keywords: "before", "after", "during", "while", "when" |
| R40 | Decimal Format | Regex for numeric formatting consistency |

**Partially Automatable (9 rules) — LLM-assisted with human review:**

| Rule | Name | Notes |
|------|------|-------|
| R1 | Structured Statements | Check "shall" presence, but not semantic correctness |
| R11 | Separate Clauses | Sentence splitting heuristics |
| R18 | Single Thought | Sentence complexity metrics |
| R22 | Enumeration | Detect lists, completeness is semantic |
| R27 | Explicit Conditions | Detect "if/when" but not completeness |
| R28 | Multiple Conditions | Nested conditional detection |
| R31 | Solution Free | Technology name keywords, context-dependent |
| R34 | Measurable Performance | Flag missing quantifiers |
| R36 | Consistent Terms | Dictionary cross-checking |

**Not Automatable (12 rules) — require human judgment:**
R3 (Subject-Verb), R23 (Diagrams), R25 (Headings), R29 (Classification), R30 (Unique Expression), R39 (Style Guide), R41 (Related Requirements), R42 (Structured Sets), and others requiring domain knowledge.

### Implementation Architecture

Two-tier checker:
1. **Deterministic layer**: Regex + spaCy NLP for 21 fully automatable rules. Fast, precise, zero false negatives.
2. **LLM layer**: Chain-of-Thought prompting with 12-20 validated examples for 9 partially automatable rules. ~70% precision / ~97% recall.

### Available Tools

No comprehensive open-source INCOSE checker exists. Commercial tools (QVscribe, Reqi.io, Jama Connect Advisor) cover most rules. The `reqif` Python package and `doorstop` are open-source for data management but don't include quality checking.

---

## Part 3: LLM Requirements Quality Checking Precision

### Key Study Results

**Lubos et al. 2024** (Llama 2 70B, ISO 29148):
- Zero-shot precision: 13-50% (dataset-dependent)
- Zero-shot recall: 74-89%
- With LLM-aware human review: precision rises to 32-88%, recall to 100%
- False positive rate: ~28% (Stopwatch) to ~87% (complex domains)

**Context-Adaptive Defect Prediction 2025** (Chain-of-Thought + few-shot):
- Zero-shot: ~55% precision, >98% recall
- 20 examples + CoT: ~70% precision, ~97% recall (best cost/performance ratio)
- 320 examples: ~68% precision, ~91% recall (diminishing returns)
- HLC approach: F1 0.779 (best overall)

**Frontiers 2025 Systematic Review:**
- LLMs struggle with domain-specific subtleties, hallucination, complex dependencies
- Hybrid approaches (LLM + traditional tools + human-in-the-loop) recommended

### False Positive Rates by Check Type

| Check Type | Estimated FP Rate | Confidence |
|-----------|-------------------|------------|
| Syntactic (vague terms, passive voice) | 5-15% | High (regex-based) |
| Ambiguity (semantic) | 30-50% | Medium |
| Solution-free | 25-40% | Medium |
| Completeness | 40-60% | Low (subjective) |
| Verifiability | 20-35% | Medium |

### Best Practices for Reducing False Positives

1. **Chain-of-Thought prompting** — forces step-by-step reasoning before classifying
2. **Few-shot with validated explanations** — 12-20 examples with rationales (not just labels)
3. **Similarity-based shot selection** — select examples most similar to requirement under review
4. **Confidence thresholds** — auto-flag high-confidence; route medium to human review
5. **Deterministic pre-filter** — run regex/NLP checks first; reserve LLM for semantic rules
6. **Downstream symbolic validation** — cross-check LLM outputs with spaCy POS tags

### Recommendation for requirements-dev

Implement the concept document's proposed hybrid approach:
- ~24 syntactic rules via keyword/pattern matching (>95% precision)
- Remaining semantic rules via LLM with CoT + few-shot (target ~70% precision)
- Explicit confidence notes on all LLM-assisted checks
- Human review required for all semantic flags before requirement registration

---

## Part 4: Requirements Traceability Tool Patterns

### Industry Standards

**ReqIF (OMG Standard)** — XML schema for requirements interchange:
- Type-instance separation (SPEC-TYPES define schemas; SPEC-OBJECTS are instances)
- Typed traceability via SPEC-RELATIONS with custom attributes
- Hierarchical document structure via SPEC-HIERARCHY trees
- Python library: `reqif` on PyPI

**OSLC RM 2.1 (OASIS)** — REST/Linked Data approach:
- Resources: Requirement and RequirementCollection
- RDF triples for traceability
- Server-based (requires running services)

### Open-Source File-Based Tools

**StrictDoc (.sdoc format):**
```
[REQUIREMENT]
UID: REQ-001
STATEMENT: The system shall respond within 200ms.
RELATIONS:
- TYPE: Parent
  VALUE: SYS-REQ-010
- TYPE: File
  VALUE: src/handler.py
  LINE_RANGE: 45, 67
```
- Three relation types: Parent, Child, File (with LINE_RANGE/FUNCTION)
- Custom grammar system for extensible attributes
- JSON export, ReqIF export, web UI
- Git integration with version macros

**Doorstop (YAML-based):**
- File-per-requirement in version control
- Document tree hierarchy
- `doorstop link` for traceability
- Built-in validation of link consistency

### Recommended JSON Schema for requirements-dev Registries

Based on synthesis of all tools:
```json
{
  "metadata": { "created", "last_modified", "version" },
  "requirements": [{
    "uid": "REQ-001",
    "title": "...",
    "statement": "The system shall ...",
    "type": "functional|performance|interface|constraint|quality",
    "status": "draft|registered|baselined",
    "priority": "high|medium|low",
    "rationale": "...",
    "parent_need": "NEED-001",
    "source_block": "block-task-engine",
    "attributes": {
      "A1_uid": "REQ-001",
      "A2_parent_trace": "NEED-001",
      "A6_verification_method": "test",
      "A7_success_criteria": "...",
      "A8_responsible_party": "...",
      "A9_vv_level": "system"
    },
    "relations": [
      { "type": "parent", "target": "NEED-001", "role": "derives_from" },
      { "type": "verified_by", "target": "TC-001" }
    ],
    "quality_checks": {
      "syntactic_pass": true,
      "semantic_flags": [],
      "last_checked": "2026-02-20T10:00:00"
    },
    "tbd_tbr": {
      "status": "resolved",
      "estimate": null,
      "resolution_path": null,
      "owner": null,
      "deadline": null
    },
    "metadata": { "created", "modified", "author", "version" }
  }]
}
```

Key principles:
- Typed relations with roles (StrictDoc/ReqIF pattern)
- UID-based linking enables cross-registry references
- INCOSE attributes as structured sub-object
- Quality check results stored per-requirement
- TBD/TBR tracking with NASA four-field closure
- Atomic writes (temp-file-then-rename) per concept-dev pattern

### Bidirectional Traceability Implementation

Store links as `(source, target, type, role)` tuples:
- Forward: `REQ-001 → derives_from → NEED-001`
- Inverse computed at query time (no duplicate storage)
- Matrix computation on-the-fly for gap analysis

---

## Testing Considerations

### Existing Test Patterns (from codebase)
- pytest with pytest-asyncio
- Coverage threshold: 80%
- Fixtures in conftest.py with env var sourcing
- Type checking: pyright
- Linting: ruff

### Recommended Testing for requirements-dev
- Unit tests for quality checker regex patterns (high coverage, deterministic)
- Unit tests for state management (phase transitions, gate checking)
- Unit tests for registry CRUD (add, link, query, validate)
- Integration tests for full pipeline (needs → requirements → V&V → traceability)
- Golden tests for quality checker (known-good/bad requirements with expected flags)
- No external API dependencies in tests (mock LLM calls)
