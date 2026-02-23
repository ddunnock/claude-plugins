# Opus Review

**Model:** claude-opus-4
**Generated:** 2026-02-20T00:00:00Z

---

## Plan Review: requirements-dev Plugin

### Overall Assessment

This is a thorough, well-structured plan that follows established patterns from the concept-dev plugin. The phased approach is sound and the dependency ordering in Section 13 is logical. That said, there are several issues worth addressing before implementation.

---

### 1. Registry Concurrency and File Size Growth

**Section 3.3, 3.6** -- The plan specifies atomic writes via temp-file-then-rename, which is good. However, every quality check, traceability link, and requirement mutation reads and rewrites the entire JSON registry file. For projects with hundreds of requirements across decomposed subsystems (Phase 3), these files will grow substantially. The plan does not discuss:

- Maximum expected registry sizes or any pagination/chunking strategy
- Whether the LLM context window can accommodate dumping full registries for validation (Section 4.1 duplicate detection loads all requirements for n-gram comparison)
- What happens when `reqif_export.py` or `traceability.py coverage_report()` is called on a large registry

**Recommendation:** Add a note about expected scale limits (e.g., "designed for up to ~500 requirements") or describe how scripts handle large registries without loading everything into memory at once.

---

### 2. Passive Voice Detection Heuristic is Too Aggressive

**Section 3.4, Rule R2** -- The heuristic "forms of 'be' followed within 3 words by a word ending in -ed or -en" will produce many false positives. Consider: "The system shall be integrated" (passive, correct detection) vs. "The system shall be updated every 5 minutes" (this is a valid requirement stating frequency, and "updated" is a participle used adjectivally). Worse, phrases like "the screen is green" would match (is + green ends in -en).

**Recommendation:** Acknowledge this as a known limitation in the plan. Consider adding a whitelist for common past-participle adjectives that end in -en (e.g., "open", "green", "broken" when used predicatively). Alternatively, note that R2 violations should be warnings, not errors.

---

### 3. Duplicate Detection Threshold Lacks Justification

**Section 4.1** -- The plan specifies "3-grams, threshold 0.8" for cosine similarity duplicate detection but provides no justification for these values. With short requirement statements (typical 10-20 words), 3-gram vectors will be very sparse, and cosine similarity of 0.8 may either miss near-duplicates or flag unrelated requirements that share common phrasing like "The system shall."

**Recommendation:** Either specify that these values are tunable and will be calibrated during development, or provide example pairs showing what 0.8 similarity looks like with 3-grams on typical requirement statements. Consider using word-level n-grams (1-grams + 2-grams) instead of character-level 3-grams, as they are more semantically meaningful for this use case. Clarify whether these are character-level or word-level n-grams.

---

### 4. ReqIF Dependency is Underspecified

**Section 3.7, 6.3, 14** -- The `reqif` PyPI package is listed as the only external dependency, but the plan does not specify:

- Which `reqif` package (there are multiple on PyPI; the most maintained one is `reqif` by strictdoc)
- What version to pin to
- How to handle the case where it is not installed (graceful degradation? error message with install instructions?)
- Whether the ReqIF output has been validated against actual DOORS/Jama imports

**Recommendation:** Pin the package version, add an install instruction in the command, and handle the ImportError case explicitly in `reqif_export.py` with a user-facing message like "Install with: pip install reqif".

---

### 5. Missing Error Recovery for Mid-Block Interruptions

**Section 7, `/reqdev:resume`** -- The resume command describes reporting exact position, but the plan does not explain how state is persisted at the granularity needed. Specifically:

- During `/reqdev:requirements`, progress through the 5 type passes within a block is conversational flow, not script state. If the session is interrupted between registering a functional requirement and starting performance requirements, what state tracks "currently in functional pass for Block X"?
- The `state.json` template is referenced but never shown. Without seeing the state schema, it is unclear whether sub-block-level and type-pass-level tracking is planned.

**Recommendation:** Show the `state.json` template or at least its schema. Include fields like `current_block`, `current_type_pass`, and `requirements_in_draft` (for requirements that passed quality check but were not yet registered when the session dropped).

---

### 6. Combinator Rule (R19) Will Be Extremely Noisy

**Section 3.4** -- The regex `\b(and|or|then|unless)\b` will flag nearly every non-trivial requirement. Legitimate requirements frequently use "and" for compound subjects ("The system shall log errors and warnings") and "or" for alternatives ("The response shall be JSON or XML"). Flagging all of these will cause quality-checker fatigue and users will start ignoring violations.

**Recommendation:** Restrict the combinator check to detect "and" or "or" only between "shall" clauses (e.g., `shall .+ and .+ shall` or `shall .+ or shall`). Alternatively, make this a low-severity warning rather than an error, and note in the plan that the LLM tier (R18 - Single thought) is the more reliable check for compound requirements.

---

### 7. No Versioning or Migration Strategy for Registries

**Sections 3.2, 3.3, 3.6** -- The JSON registries have implicit schemas (the dataclass definitions), but there is no version field in the registry files. When the plugin evolves (new attributes, changed schema), existing `.requirements-dev/` workspaces will break silently.

**Recommendation:** Add a `schema_version` field to each registry JSON file and a migration check in `init_session.py` or `update_state.py` that detects and handles older schemas.

---

### 8. Concept-Dev Ingestion Brittleness

**Section 3.1** -- The ingestion script parses `BLACKBOX.md` and `CONCEPT-DOCUMENT.md` to extract blocks, capabilities, and scenarios. These are free-form Markdown files generated by an LLM. Parsing them reliably is non-trivial:

- What heading structure does `ingest_concept.py` expect? If concept-dev changes its document template, ingestion breaks.
- The plan says "parse" but does not specify the parsing strategy (regex on headings? full Markdown AST? search for specific section names?)

**Recommendation:** Either specify the exact Markdown structure expected (heading names, nesting levels) or consider having concept-dev write a structured `blocks.json` / `capabilities.json` alongside the Markdown deliverables, which would be far more reliable to ingest. Alternatively, state that ingestion is LLM-assisted (the command prompt tells Claude to read and extract, not a Python parser).

---

### 9. Hook Path Pattern May Miss Nested Artifacts

**Section 9** -- The hook matcher is `**/.requirements-dev/*.md`, which will not match files in subdirectories like `.requirements-dev/exports/requirements.reqif`. This is fine for the current structure, but if deliverables are ever reorganized into subdirectories (e.g., `.requirements-dev/deliverables/REQUIREMENTS-SPECIFICATION.md`), the hook silently stops working.

This mirrors the concept-dev hook pattern exactly, so it is consistent, but worth noting.

---

### 10. Quality Checker Agent Context Window Consumption

**Section 3.4, Tier 2** -- The quality-checker agent receives "12-20 validated examples with rationales" from `references/incose-rules.md` plus the requirement context. For a sonnet-class model, this is fine for a single requirement, but the plan does not address:

- Whether the agent is invoked once per requirement or batched
- The cumulative token cost of running it on every requirement (for a project with 100+ requirements, this could be expensive)

**Recommendation:** Specify batching strategy. Consider running Tier 2 on batches of 5-10 requirements to amortize the few-shot examples cost. Also consider allowing users to skip Tier 2 for lower-priority requirements.

---

### 11. "Baselined" Status Transition Rules Are Undefined

**Section 5.1** -- Phase 3 decomposition requires requirements to have `status: "baselined"`, but the plan never defines how a requirement transitions from `registered` to `baselined`. Is this automatic when deliverables are generated? Does the user explicitly baseline? Is there a `/reqdev:baseline` command?

**Recommendation:** Define the baselining workflow explicitly. Add either a command or a step within `/reqdev:deliver` that transitions requirements to baselined status, and describe what constraints apply to baselined requirements (e.g., can they still be edited?).

---

### 12. Security: HTML Escaping in Markdown is Misleading

**Section 12** -- The plan says "html.escape() on all user-provided content in generated markdown/HTML." But the deliverables are `.md` files, not HTML. Running `html.escape()` on Markdown content will produce visible `&amp;`, `&lt;`, etc. in the rendered Markdown, degrading readability for no security benefit (Markdown renderers that parse inline HTML are the actual threat surface, and that is a renderer-side concern).

**Recommendation:** Clarify that HTML escaping applies only to the ReqIF XML export (where it is genuinely needed) and to any HTML reports if generated. For Markdown deliverables, the concern is Markdown injection (e.g., user text containing `[link](javascript:...)`) which `html.escape()` does not address. Consider instead sanitizing user text by stripping or escaping Markdown special characters in requirement statements embedded in deliverables.

---

### 13. Missing: Conflict Resolution Between Blocks

**Section 4.2** -- The cross-cutting sweep checks INCOSE C11 (Consistency: "No conflicting requirements") but delegates it to "user-reviewed." There is no mechanism for:

- Detecting potential conflicts programmatically (e.g., Block A requires response time < 100ms while Block B requires encryption that adds 200ms latency)
- Recording conflict resolution decisions and rationale

**Recommendation:** At minimum, add a `conflict` link type to the traceability engine so that identified conflicts can be tracked with resolution status and rationale.

---

### 14. Missing: Requirement Deletion/Withdrawal

**Sections 3.2, 3.3** -- The needs tracker supports `defer` and `reject` but neither tracker has a `delete` or `withdraw` subcommand. Once a requirement is registered, how is it removed? In formal requirements management, requirements are typically withdrawn (not deleted) to preserve audit trail.

**Recommendation:** Add a `withdraw` subcommand to `requirement_tracker.py` that sets `status: "withdrawn"` with rationale, and ensure withdrawn requirements are excluded from coverage calculations but preserved in registries and traceability.

---

### 15. Ambiguity: What Constitutes "Manual Mode"

**Sections 3.1, 3.2** -- The plan mentions manual mode as a fallback when concept-dev artifacts are missing, but does not specify the interaction pattern. How does the user define blocks manually? Free-text? A structured questionnaire? How many blocks should the skill suggest? Without guidance, the LLM will improvise differently each time.

**Recommendation:** Specify the manual mode interaction pattern in the `/reqdev:init` command definition. For example: "Prompt user to name each block, provide a 1-2 sentence description, and list 3-5 capabilities. Present a summary table for approval before proceeding."

---

### Summary of Priorities

**Must address before implementation:**
1. State schema / resume granularity (item 5) -- without this, resume will not work
2. Baselining workflow (item 11) -- Phase 3 depends on it
3. Concept ingestion parsing strategy (item 8) -- core dependency for the entire flow
4. Combinator rule noise (item 6) -- will dominate quality checker output

**Should address:**
5. Registry versioning (item 7)
6. ReqIF dependency specifics (item 4)
7. Requirement withdrawal (item 14)
8. Manual mode specification (item 15)

**Nice to have:**
9. Scale limits documentation (item 1)
10. Passive voice false positives (item 2)
11. Duplicate detection calibration (item 3)
12. HTML escaping clarification (item 12)
