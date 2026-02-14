# Questioning Heuristics

Adaptive questioning strategies for concept development phases. Questions progress from open to structured as understanding deepens.

## Three Modes

### 1. Open Mode (Phase 1: Spit-Ball)

**Goal:** Expand the idea space. Learn what the user cares about.

**Characteristics:**
- No predetermined structure
- Follow the user's energy
- Ask "what if" to push boundaries
- Never evaluate or narrow

**Question Types:**
- **Expansion:** "What if [constraint] didn't exist?"
- **Amplification:** "What would make this 10x more valuable?"
- **Connection:** "How does this relate to [earlier idea]?"
- **Provocation:** "What's the most radical version of this?"
- **Clarification:** "When you say [X], what does that look like in practice?"

**Pacing:** Let the user lead. Ask 1-2 follow-ups per idea, then let them introduce the next topic. Don't interrogate.

**Transition signal:** User starts repeating themes, says "I think that's the main stuff," or asks "what do you think?"

### 2. Metered Mode (Phases 2-3: Problem Definition, Black-Box)

**Goal:** Systematically gather information without overwhelming.

**Characteristics:**
- Ask 3-4 questions per turn
- Checkpoint after each batch: summarize what you've learned, confirm, then proceed
- Mix closed questions (confirm facts) with open questions (explore unknowns)
- Track what's been covered vs. what's missing

**Checkpoint Format:**
```
-------------------------------------------------------------------
CHECKPOINT: [Topic]
-------------------------------------------------------------------

Here's what I've captured so far:

  1. [Confirmed fact or decision]
  2. [Confirmed fact or decision]
  3. [Captured but needs verification]

Still need to understand:
  - [Open question 1]
  - [Open question 2]

Does this look right? Anything to correct before we continue?
-------------------------------------------------------------------
```

**Question Design:**
- Start with context: "You mentioned [X]. Building on that..."
- Be specific: "What happens when [specific scenario]?" not "Tell me about edge cases"
- Offer examples: "For instance, does it need to handle [A], [B], or something else?"
- Respect "I don't know": Record as unknown, don't push

**Scope Guardrail (Phase 2):**
When the user offers a solution during problem definition:
```
"That's a solution approach — I'm noting it for the drill-down phase.
For now, let's stay with the problem: [redirect question]."
```

### 3. Structured Mode (Phases 4-5: Drill-Down, Document)

**Goal:** Systematically work through defined blocks with research validation.

**Characteristics:**
- Follow the block decomposition structure
- Each question targets a specific information need
- Research supports questioning (not the reverse)
- Explicit source tracking for every answer

**Question Types:**
- **Decomposition:** "For the [block name] function, what sub-functions does it need to perform?"
- **Boundary:** "Where does [block A]'s responsibility end and [block B]'s begin?"
- **Constraint:** "Are there hard constraints on how [function] must behave?"
- **Validation:** "I found [research finding]. Does this match your understanding?"
- **Gap identification:** "For [domain], I can't find information about [X]. Do you have insight?"

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Question dump | 10+ questions at once | Max 4, then checkpoint |
| Leading questions | Embed answer in question | Ask neutrally |
| Binary railroading | "Is it A or B?" when C exists | "How would you describe...?" |
| Premature narrowing | Forcing structure in spit-ball | Stay in open mode |
| Assumption-as-question | "Since X is true, how..." | "Is X the case? If so..." |
| Repeat asking | Same question rephrased | Track covered topics |

## Phase-Question Mapping

| Phase | Mode | Questions Per Turn | Checkpoint Frequency |
|-------|------|-------------------|---------------------|
| Spit-Ball | Open | 1-2 follow-ups | After 5+ ideas |
| Problem Definition | Metered | 3-4 questions | Every batch |
| Black-Box | Metered | 3-4 questions | Per section |
| Drill-Down | Structured | Per block | Per block |
| Document | Structured | Per section | Per section |
