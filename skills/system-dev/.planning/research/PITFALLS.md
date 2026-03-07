# Pitfalls Research

**Domain:** AI-assisted systems design platform (Claude Code skill, 45 blocks, central Design Registry, hybrid agent orchestration)
**Researched:** 2026-02-28
**Confidence:** HIGH (based on verified upstream bugs, Anthropic docs, and documented Claude Code issues)

## Critical Pitfalls

### Pitfall 1: Context Window Exhaustion from Registry Bulk-Loading

**What goes wrong:**
A naive Design Registry implementation loads entire JSON registries into the context window for each agent operation. With 478 requirements across 45 blocks, plus design components, interfaces, behavioral contracts, traceability chains, and risk entries, the registry grows to hundreds of KB. Each agent invocation that reads "the current design state" consumes most of the available context, leaving insufficient room for reasoning, conversation history, and the agent's own instructions.

**Why it happens:**
Developers build the "happy path" first -- reading the full registry works fine with 5 components. By the time the registry holds 50+ components with full interface definitions and behavioral contracts, agents silently degrade. Claude does not error on context overflow; it truncates earlier conversation turns, losing critical instruction context. Anthropic's skill docs confirm: "the context window is a public good" shared with system prompt, conversation history, other skills, and the actual request.

**How to avoid:**
- Design the slot-api (REQ-001 through REQ-031) with **projection queries** from day one: agents request specific slots by component ID and field subset, never the full registry.
- Implement a `slot_query.py` script that accepts `--component X --fields name,interfaces,contracts` and returns only the requested slice.
- Budget context: SKILL.md ~250 lines (~500 tokens), each command file ~150 lines, each agent prompt ~200 lines, registry query results ~2000 tokens max per invocation. Total per-turn budget: ~5000 tokens of skill content + query results.
- The slot-storage-engine (42 reqs) must support indexed access, not just full-file reads.

**Warning signs:**
- Agent responses become generic or lose instruction adherence mid-session
- Agents "forget" earlier design decisions within the same session
- Registry JSON files exceed 50KB and agents read the full file
- Claude starts summarizing rather than providing specific details

**Phase to address:**
Phase 1 (Design Registry core). The slot-api and slot-storage-engine must ship with projection queries before any agent writes to the registry.

---

### Pitfall 2: SKILL.md Overload -- Cramming 45 Blocks into One File

**What goes wrong:**
The system has 12 top-level blocks and 33 sub-blocks. Attempting to describe all agent behaviors, registry schemas, command workflows, and block interactions in SKILL.md blows past Anthropic's 500-line recommendation. Claude either fails to discover the skill, partially reads it, or loses critical instructions buried in the middle.

**Why it happens:**
The requirements-dev SKILL.md is 246 lines for a 10-command, 5-agent, 6-registry system. system-dev has more agents (6 top-level + sub-blocks), more registry complexity, and more cross-agent coordination. Linear scaling would produce 600+ lines. Developers don't realize the line limit is a hard performance boundary, not a style suggestion.

**How to avoid:**
- SKILL.md stays under 300 lines: skill metadata, security rules, path conventions, command table with one-line descriptions, agent table with refs, registry overview (names only), and behavior rules.
- Each command gets a separate file in `commands/` (following requirements-dev pattern: 10 commands = 10 files, 1708 total lines).
- Each agent gets a separate file in `agents/` loaded only when that agent is invoked.
- Registry schemas go in `references/registry-schema.md`, loaded only during registry operations.
- Anthropic docs: "Keep references one level deep from SKILL.md" -- no chained references.

**Warning signs:**
- SKILL.md exceeds 400 lines
- Adding a new agent requires editing SKILL.md
- Claude reads SKILL.md but misses a command that's documented at line 450

**Phase to address:**
Phase 1 (skill scaffold). The directory structure and progressive disclosure hierarchy must be established before any content is written.

---

### Pitfall 3: JSON Registry Corruption from Concurrent Agent Writes

**What goes wrong:**
Two subagents (e.g., structural-decomposition-agent and interface-resolution-agent) run in parallel per the hybrid orchestration model. Both read `design_registry.json`, make independent modifications, and write back. The second write overwrites the first agent's changes. Alternatively, a write fails mid-operation (agent context limit hit, user cancels), leaving a partially-written JSON file that breaks all subsequent reads.

**Why it happens:**
JSON files have no built-in concurrency control. Claude Code subagents run in separate processes. The PROJECT.md states "Hybrid -- some agents spawn as Claude Code subagents for parallel work." Documented Claude Code issues confirm JSON serialization bottlenecks cause freezes with multi-agent task processing (GitHub issue #4580).

**How to avoid:**
- **Never have two agents write to the same JSON file.** Design the registry as multiple files: `components.json`, `interfaces.json`, `contracts.json`, `traceability.json`, `risks.json` -- each owned by one agent type.
- Implement a `change-journal` (11 reqs in the sub-blocks) as an append-only log. Agents append changes; a deterministic merge script applies them sequentially.
- Use file-level locking in the slot-api scripts: `fcntl.flock()` on write operations.
- The approval-gate sub-block (11 reqs) should validate registry consistency after each parallel agent batch completes, before the next batch starts.

**Warning signs:**
- Design decisions appear and disappear between agent invocations
- `json.decoder.JSONDecodeError` in agent output
- Agent reports "component X not found" when it was just created by another agent
- Registry file size decreases unexpectedly

**Phase to address:**
Phase 1 (Design Registry core) for file partitioning and locking. Phase 2 (agent implementation) for coordination protocol.

---

### Pitfall 4: Schema Mismatch at the Upstream Boundary

**What goes wrong:**
system-dev ingests requirements-dev output (needs_registry.json, requirements_registry.json, traceability_registry.json, etc.). The ingestion code reads keys that don't exist in the upstream schema, silently producing empty data. This is not hypothetical -- it is a documented, confirmed pattern: CROSS-SKILL-ANALYSIS.md identified 3 bugs in the concept-dev to requirements-dev boundary caused by exactly this failure mode (BUG-1: gate status reads `gates` key that doesn't exist; BUG-2: gap_analyzer reads `sources` and `assumptions` instead of `source_refs` and `assumption_refs`; BUG-3: empty dict evaluates as "all passed").

**Why it happens:**
Each skill develops its schema independently. The developer writes ingestion code against what they think the upstream schema looks like, rather than reading the actual upstream registry files. When the upstream skill evolves its schema, downstream ingestion silently breaks. The `.get(key, default)` pattern in Python makes silent failures the default behavior.

**How to avoid:**
- Write a `validate_upstream.py` script that loads the actual requirements-dev registry files and asserts expected keys exist before proceeding. Run this as the first step of `/sysdev:init`.
- Maintain a `upstream-schema.json` file that documents the exact shape of each upstream registry, and diff it against actual upstream files during ingestion.
- Never use `.get(key, {})` without logging when the default is returned for a key that should exist. Use explicit `KeyError` for required fields.
- Test ingestion against the actual requirements-dev output from the brainstorming project, not mocked data.

**Warning signs:**
- Ingestion report shows 0 items for a category that should have data
- "All gates passed" message when upstream phases are incomplete
- Coverage metrics show 100% when traceability links are actually missing
- Any `.get()` call returning the default for a required field

**Phase to address:**
Phase 1 (requirements-synchronizer agent). The ingestion pipeline must be validated against real upstream data before any design work begins.

---

### Pitfall 5: Agent Coordination Deadlocks in the Hub-and-Spoke Model

**What goes wrong:**
The architecture specifies "all agents read/write through slot-api, no direct agent-to-agent calls" (NEED-007). Agent A writes a component; Agent B needs that component to define an interface; Agent C needs the interface to write a behavioral contract. If the orchestrator launches B before A's write is visible in the registry, B operates on stale state and produces an interface definition for a component that doesn't match what A actually created. Worse, if A and B are launched in parallel, B may read an empty slot and create a placeholder that A later overwrites.

**Why it happens:**
The chief-systems-engineer orchestrator must maintain a dependency graph of agent operations, but the 478 requirements don't explicitly encode operation ordering between agents. The developer assumes agents can be parallelized because they access "different" registry slots, but structural decomposition creates new slots that interface resolution depends on.

**How to avoid:**
- Define explicit **operation phases** within each design command: (1) structural decomposition writes components, (2) interface resolution reads components and writes interfaces, (3) behavioral contracts reads interfaces and writes contracts. These are sequential batches, not freely parallel.
- The orchestrator (8 reqs in sub-blocks) must implement a `dependency_graph.json` that maps which agent outputs feed which agent inputs.
- Each agent returns a structured manifest of slots it wrote, which the orchestrator validates against expected outputs before launching dependent agents.
- The coherence-reviewer sub-block (9 reqs) runs after each phase boundary, not at the end.

**Warning signs:**
- Interface definitions reference components with different names than what structural decomposition created
- Behavioral contracts specify obligations for interfaces that were modified after the contract was written
- The orchestrator launches all agents simultaneously regardless of data dependencies
- "Slot not found" errors in agent B when agent A should have created it

**Phase to address:**
Phase 2 (chief-systems-engineer orchestrator). The dependency graph must be defined before agents are implemented. Phase 3 (agent implementation) must respect it.

---

### Pitfall 6: Loss of Traceability Chain Integrity

**What goes wrong:**
The system must maintain chains from need -> requirement -> component -> interface -> contract -> V&V. Each link is created by a different agent at a different time. When a component is renamed, split, or merged during iterative design, some links become stale (pointing to non-existent IDs) while others are never created (new components have no requirement trace). The traceability-weaver agent reports "100% traced" because it counts existing links, not missing ones.

**Why it happens:**
Traceability is treated as a final-step reporting concern rather than an invariant maintained on every write. The impact-analysis-agent (12 reqs) and change-tracer sub-block (8 reqs) exist to handle this, but if they run asynchronously or optionally, stale links accumulate. This mirrors GAP-8 from CROSS-SKILL-ANALYSIS.md: requirements-dev has no backward traceability to concept artifacts because traceability was an add-on, not an invariant.

**How to avoid:**
- Make traceability link creation atomic with the entity creation. When `slot-api` creates a component, it requires a `traces_to` field pointing to the source requirement ID. Reject writes without it.
- The traceability-weaver should run a **completeness check** (not just a consistency check): for every requirement, assert a component exists; for every component, assert an interface exists if the requirement implies one.
- The change-journal must record link invalidations when entities are modified, and the delta-detector sub-block must flag orphaned links.
- Never report traceability percentages without distinguishing "linked" from "verified as current."

**Warning signs:**
- Traceability report shows 100% coverage but design review reveals unimplemented requirements
- Component renames cause traceability report to show dangling IDs
- New components added without any requirement trace
- Traceability percentage never decreases even as design changes accumulate

**Phase to address:**
Phase 1 (Design Registry core) for mandatory trace fields. Phase 3 (traceability-weaver) for completeness checking. Phase 4 (impact-analysis) for change propagation.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single monolithic `design_registry.json` file | Simpler initial implementation | Every agent reads the full file; concurrent writes corrupt state; file exceeds 100KB within 20 components | Never -- partition from day one |
| Skipping schema validation on registry writes | Faster agent development | Malformed entries accumulate; downstream agents crash on unexpected data shapes | Never -- validate on every write |
| Hardcoding upstream registry paths | Avoids configuration complexity | Breaks when requirements-dev changes its directory structure or file names | Only in prototype; replace with config before Phase 2 |
| Deferring the change-journal | Fewer files to manage initially | No audit trail for design decisions; cannot roll back; impact analysis has no history | Only if shipping to validate within 1 week |
| Using `json.dumps(indent=2)` for all registry writes | Human-readable files | 3x file size inflation; context window waste when agents read registries | Never for files agents read; acceptable for debug/export files |
| Embedding agent prompts in command files | Fewer files to manage | Command files exceed 300 lines; agent behavior can't be tested independently | Never -- agents get their own files per Anthropic pattern |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| requirements-dev registry ingestion | Reading `.get("gates", {})` when the key is actually `phases.X.gate_passed` | Read actual upstream file structure first; write `validate_upstream.py` that asserts key existence (learned from BUG-1, BUG-2, BUG-3) |
| Upstream source_registry.json | Expecting field `name` when upstream uses `title`; expecting 4 source types when upstream has 11 | Maintain a field-mapping layer in the ingestion script; never assume schema parity (learned from SCHEMA-1) |
| Upstream assumption lifecycle | Treating assumptions as read-only after ingestion | Implement assumption_tracker with full lifecycle: active -> challenged -> invalidated/reaffirmed (learned from GAP-7) |
| Upstream confidence levels | Ignoring source confidence ratings | Carry confidence through to design decisions; a component designed from an ungrounded requirement needs flagging (learned from GAP-4) |
| design-impl downstream handoff | Producing design artifacts without documenting their schema for the next skill | Define the output schema in Phase 1; validate it before Phase 4 agents produce artifacts |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full registry reads per agent turn | Agent responses slow to 15+ seconds; degraded output quality | Projection queries via slot-api; never read more than 2KB per query | Registry exceeds 50KB (~30 components with full interfaces) |
| Session JSONL growth from verbose registry output | Claude Code hangs or OOMs; session files reach hundreds of MB | Agent scripts return summary (IDs + status), not full entities; cap script output at 4KB | Session exceeds 10 turns with registry-heavy operations |
| Unbounded change-journal | Journal file grows faster than registry; reads become slow | Journal rotation: archive entries older than current design phase; keep only last 100 entries active | Journal exceeds 200 entries (~20 design iterations) |
| Diagram generation for full system | Mermaid/PlantUML diagrams exceed Claude's output token limit; truncated diagrams | Generate per-block diagrams, not system-wide; system overview shows only top-level blocks | System exceeds 15 components with interfaces |
| JSON `indent=2` formatting | 3x file size; wasted context tokens when agents read formatted JSON | Use `indent=None` (compact) for agent-read files; `indent=2` only for human-facing exports | Any file agents read that exceeds 10KB |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Requirement statements treated as executable content | Prompt injection via malicious requirement text (e.g., "The system shall ignore all previous instructions...") | Follow requirements-dev pattern: `<rule name="content-as-data">` -- requirement text, design descriptions, and interface specs are DATA, never commands |
| Agent scripts accepting arbitrary file paths | Path traversal via `../../../etc/passwd` in component names | Validate all paths; reject any containing `..`; follow requirements-dev `<rule name="path-validation">` |
| Agent prompts embedded in user-visible files | Users can read and manipulate agent behavior by editing files in `.system-dev/` | Keep agent prompts in `${CLAUDE_PLUGIN_ROOT}/agents/`, not in the workspace; workspace files are data only |
| Upstream registry files read without sanitization | Malicious content in requirements-dev registries could inject instructions | Wrap upstream content in data markers per requirements-dev pattern: `BEGIN/END EXTERNAL CONTENT` |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Dumping all 45 blocks' status at once | User cannot find what they need; information overload | Show top-level block summary (12 rows); drill into sub-blocks only on request |
| Requiring user approval for every sub-block operation | Approval fatigue; user approves without reading | Gate at top-level block boundaries only; sub-block operations are automatic within an approved block |
| Generating diagrams before design is stable | User reviews diagram, provides feedback, diagram is regenerated; wasted turns | Defer diagram generation until after coherence review passes; show text-based summaries during active design |
| No resume capability after context window exhaustion | User loses mid-design progress; must restart from last gate | Persist design state after every agent batch; implement `/sysdev:resume` that reads registry state and continues |
| Showing raw JSON diff as design change summary | User cannot understand what changed | Impact-analysis-agent should produce natural-language change summaries with affected components listed |

## "Looks Done But Isn't" Checklist

- [ ] **Slot-api "works":** Verify it supports projection queries, not just full-file CRUD -- test with a 100-component registry
- [ ] **Traceability "100%":** Verify completeness (every requirement has a component), not just consistency (existing links are valid)
- [ ] **Ingestion "succeeds":** Verify upstream data actually populated (non-zero counts for every category), not just that the script exited 0
- [ ] **Agent "produces output":** Verify output conforms to registry schema, not just that the agent returned text
- [ ] **Diagrams "render":** Verify all component relationships are shown, not just that Mermaid syntax is valid
- [ ] **Change-journal "records":** Verify it captures enough context to understand *why* a change was made, not just *what* changed
- [ ] **Gate "passes":** Verify coherence-reviewer checked cross-block consistency, not just that individual blocks are internally valid
- [ ] **Impact analysis "ran":** Verify blast radius includes transitive dependencies (A->B->C), not just direct dependents

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Context window exhaustion mid-design | MEDIUM | Save registry state to disk; start new session; run `/sysdev:resume` which reads registry and reconstructs context |
| JSON registry corruption | HIGH | Restore from change-journal by replaying entries; if journal is also corrupted, restore from last git commit of `.system-dev/` directory |
| Schema mismatch with upstream | LOW | Fix field mappings in ingestion script; re-run `/sysdev:init` which re-ingests from upstream registries |
| Stale traceability links | MEDIUM | Run traceability-weaver in audit mode to identify all orphaned/stale links; present list to user for resolution |
| Agent coordination produced inconsistent design | HIGH | Roll back to last gate-approved state via change-journal; re-run the failed agent batch sequentially instead of in parallel |
| SKILL.md exceeds 500 lines | LOW | Refactor into command files and agent files per Anthropic pattern; this is a one-time structural fix |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Context window exhaustion | Phase 1: Design Registry core | Test with synthetic 100-component registry; measure context usage per agent turn |
| SKILL.md overload | Phase 1: Skill scaffold | Count lines; verify each command and agent has its own file; SKILL.md < 300 lines |
| JSON concurrent write corruption | Phase 1: Registry file partitioning | Test two agents writing simultaneously; verify no data loss |
| Schema mismatch at upstream boundary | Phase 1: Requirements-synchronizer | Run ingestion against real requirements-dev output; verify non-zero counts for all categories |
| Agent coordination deadlocks | Phase 2: Chief-systems-engineer | Define dependency graph; test agent B sees agent A output before executing |
| Traceability chain integrity | Phase 1 (mandatory fields) + Phase 3 (completeness checks) | Create component without trace field; verify rejection. Run completeness check; verify it catches missing links |
| Session file growth | Phase 2: Agent output formatting | Monitor session JSONL size across a full design cycle; cap at 10MB |
| Approval fatigue | Phase 2: Gate design | Count user approval prompts per design cycle; target < 15 gates for a full system design |

## Sources

- [CROSS-SKILL-ANALYSIS.md](/Users/dunnock/projects/claude-plugins/skills/requirements-dev/CROSS-SKILL-ANALYSIS.md) -- 3 bugs, 8 gaps, 5 missed opportunities from concept-dev to requirements-dev boundary (direct evidence for Pitfall 4)
- [Anthropic Skill Authoring Best Practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices) -- 500-line limit, progressive disclosure, context window as public good (direct evidence for Pitfalls 1, 2)
- [Claude Code Issue #22365: Large session JSONL files cause hanging](https://github.com/anthropics/claude-code/issues/22365) -- session files reaching 3.8GB
- [Claude Code Issue #4580: Freezes during multi-agent JSON serialization](https://github.com/anthropics/claude-code/issues/4580) -- JSON serialization bottlenecks with subagents
- [Claude Code Issue #5024: History accumulation causes performance issues](https://github.com/anthropics/claude-code/issues/5024) -- .claude.json growing to hundreds of MB
- [From Solo Act to Orchestra: Multi-Agent Architecture](https://www.cloudgeometry.com/blog/from-solo-act-to-orchestra-why-multi-agent-systems-demand-real-architecture) -- shared memory race conditions, append-only state patterns
- [ESAA: Event Sourcing for Autonomous Agents](https://arxiv.org/html/2602.23193) -- agents emit intentions validated by deterministic orchestrator, not direct state writes
- requirements-dev SKILL.md (246 lines, 10 commands, 5 agents, 6 registries) -- proven pattern for registry-centric skill at the boundary of Anthropic's recommendations

---
*Pitfalls research for: AI-assisted systems design platform (INCOSE System Design phase)*
*Researched: 2026-02-28*
