# Diátaxis Framework Reference

Detailed guidance for applying the Diátaxis documentation framework.

## Core Principle

Diátaxis identifies four distinct user needs, and four corresponding forms of documentation. Each serves a unique purpose and requires a tailored approach. Keeping these forms separate ensures documentation effectively meets its goals.

## The Four Quadrants

### 1. Tutorials (Learning-Oriented)

**Purpose**: Help users learn by doing
**User Question**: "How do I learn this?"
**Focus**: Acquisition of skills through guided experience

#### Characteristics
- **Learning-oriented**: The goal is education, not completion
- **Practical**: Users do something meaningful
- **Guided**: Teacher leads, student follows
- **Progressive**: Skills build on previous steps
- **Repeatable**: Works the same way every time

#### Writing Guidelines

**DO:**
- Start with a clear, achievable goal
- Provide immediate visible results at each step
- Keep explanations minimal—just enough to proceed
- Use simple, concrete examples
- Test every step in sequence
- Make the user feel successful

**DON'T:**
- Explain concepts in depth (that's Explanation)
- Offer choices or alternatives
- Cover edge cases or advanced scenarios
- Assume prior knowledge
- Skip steps or combine actions

#### Structure Template

```markdown
# Tutorial: [Learning Goal]

## What you'll learn
[Brief outcome description]

## Before you begin
[Minimal prerequisites—keep short]

## Step 1: [First action]
[Instructions]
[Expected result]

## Step 2: [Next action]
[Instructions]
[Expected result]

...

## What you've accomplished
[Celebrate the achievement]

## Next steps
[Where to go from here]
```

#### Quality Checklist
- [ ] Focuses on learning, not accomplishing
- [ ] Has clear start and end points
- [ ] Provides visible results at each step
- [ ] Doesn't explain—just guides
- [ ] Is repeatable

---

### 2. How-To Guides (Goal-Oriented)

**Purpose**: Help users accomplish specific tasks
**User Question**: "How do I do X?"
**Focus**: Practical application of skills

#### Characteristics
- **Goal-oriented**: Solves a specific problem
- **Practical**: Produces a concrete result
- **Focused**: Addresses one task
- **Flexible**: May offer options where appropriate
- **Assumes competence**: Reader knows the basics

#### Writing Guidelines

**DO:**
- State the goal clearly in the title
- Assume basic familiarity with the product
- Focus on solving the problem at hand
- Provide just enough context to proceed
- Link to related guides and reference
- Include troubleshooting for common issues

**DON'T:**
- Teach the basics (that's Tutorials)
- Explain why things work (that's Explanation)
- Document every option (that's Reference)
- Include step-by-step learning exercises

#### Structure Template

```markdown
# How to [accomplish specific goal]

## Overview
[One sentence describing what this achieves]

## Prerequisites
[What the reader needs before starting]

## Steps

### 1. [First action]
[Instructions]

### 2. [Next action]
[Instructions]

...

## Verification
[How to confirm success]

## Troubleshooting
[Common issues and solutions]

## Related guides
[Links to related how-tos]
```

#### Quality Checklist
- [ ] Goal is clear in the title
- [ ] Assumes reader knows basics
- [ ] Focuses on solving a problem
- [ ] Steps are actionable
- [ ] Explanation is minimal

---

### 3. Reference (Information-Oriented)

**Purpose**: Provide accurate, complete technical information
**User Question**: "What are the details of X?"
**Focus**: Description of the machinery

#### Characteristics
- **Information-oriented**: Describes what things are
- **Accurate**: Must be correct and current
- **Complete**: Covers everything relevant
- **Neutral**: States facts without opinion
- **Structured**: Organized by subject matter

#### Writing Guidelines

**DO:**
- Organize by the structure of the subject matter
- Be complete and accurate
- Use consistent formatting
- Include all parameters, options, values
- Cross-reference related items
- Keep it dry and factual

**DON'T:**
- Teach how to use features (that's Tutorials)
- Explain why things work (that's Explanation)
- Provide step-by-step guides (that's How-To)
- Include opinions or recommendations

#### Structure Template

```markdown
# [Subject Name]

## Overview
[Brief description of what this is]

## [Category 1]

### [Item]
**Type**: [type]
**Default**: [default value]
**Required**: [yes/no]

[Description of what this does]

**Example**:
```
[code example]
```

### [Item 2]
...

## [Category 2]
...

## See Also
[Links to related reference material]
```

#### Quality Checklist
- [ ] Organized by subject structure
- [ ] Complete and accurate
- [ ] Neutral tone
- [ ] Easy to navigate/search
- [ ] No tutorials or explanations mixed in

---

### 4. Explanation (Understanding-Oriented)

**Purpose**: Help users understand why and how things work
**User Question**: "Why does X work this way?"
**Focus**: Building mental models

#### Characteristics
- **Understanding-oriented**: Develops comprehension
- **Discursive**: Can explore from different angles
- **Contextual**: Provides background and history
- **Comparative**: May contrast with alternatives
- **Thoughtful**: Can include opinions and analysis

#### Writing Guidelines

**DO:**
- Provide context and background
- Explore "why" questions
- Compare with alternatives
- Discuss trade-offs and decisions
- Help build mental models
- Connect concepts together

**DON'T:**
- Provide step-by-step instructions (that's How-To)
- Document every detail (that's Reference)
- Teach through exercises (that's Tutorials)

#### Structure Template

```markdown
# [Concept/Topic]

## Background
[Context and history]

## Why [topic] matters
[Motivation and value]

## How [topic] works
[Conceptual explanation]

## Key concepts

### [Concept 1]
[Explanation]

### [Concept 2]
[Explanation]

## [Topic] vs [Alternative]
[Comparison and trade-offs]

## When to use [topic]
[Guidance and recommendations]

## Further reading
[Links to deeper resources]
```

#### Quality Checklist
- [ ] Provides context and background
- [ ] Explores "why" questions
- [ ] Approaches from different angles
- [ ] May include opinions/alternatives
- [ ] Builds a mental model

---

## The Two Axes

Diátaxis uses two conceptual axes:

### Horizontal: Acquisition → Application
- **Left (Study)**: Learning new skills/knowledge
- **Right (Work)**: Applying existing skills/knowledge

### Vertical: Action → Cognition
- **Top (Practical)**: Doing things
- **Bottom (Theoretical)**: Understanding things

This creates the four quadrants:
- Tutorial: Practical + Study (learning by doing)
- How-To: Practical + Work (getting things done)
- Explanation: Theoretical + Study (understanding concepts)
- Reference: Theoretical + Work (looking up facts)

---

## Common Mixing Problems

### Tutorial + Reference
**Symptom**: Long explanations of every option mid-tutorial
**Fix**: Link to reference, don't include it inline

### How-To + Explanation
**Symptom**: Lengthy "why" sections in task guides
**Fix**: Brief context only, link to explanation docs

### Reference + Tutorial
**Symptom**: Reference docs with "getting started" sections
**Fix**: Separate into distinct documents, link between them

### Explanation + How-To
**Symptom**: Conceptual docs with step-by-step instructions
**Fix**: Extract steps to how-to guide, keep concepts

---

## Navigating Between Quadrants

Good documentation creates paths between quadrants:

```
Tutorial → "Now that you've learned X, see the Reference for all options"
Reference → "For how to use this in practice, see the How-To guide"
How-To → "To understand why this works, see the Explanation"
Explanation → "To try this yourself, start with the Tutorial"
```

---

## Adoption Strategy

### Starting Fresh
1. Create landing page (navigation hub)
2. Write quickstart tutorial (first 5 minutes)
3. Add critical how-to guides (common tasks)
4. Build reference documentation (complete facts)
5. Add explanation documents (deeper understanding)

### Reorganizing Existing Docs
1. Audit all existing content
2. Classify each piece by dominant quadrant
3. Identify mixed content requiring separation
4. Create target structure
5. Migrate content piece by piece
6. Fill gaps identified in audit

### Iterative Improvement
1. Pick one document
2. Identify its primary quadrant
3. Extract content belonging to other quadrants
4. Create links between separated content
5. Apply quadrant-specific quality checklist
6. Repeat for next document
