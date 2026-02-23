# Tell AI *What*, Never *How*: The Requirements Engineering Principle That Transforms AI Reliability

*Why telling an AI to "use Redis" produces worse results than describing the problem Redis would solve — and what sixty years of requirements engineering already knew about it.*

**[IMAGE: A stylized split-screen illustration. On the left, a tangled web of code, technology logos, and implementation details funneling into a narrow pipe labeled "HOW." On the right, a clean problem statement radiating outward into multiple possible solution paths labeled "WHAT." The visual metaphor: solution-embedded thinking constrains; problem-focused thinking liberates.]**

In [Part 1 of this series](https://medium.com/@dunnoda/the-60-year-old-framework-that-makes-ai-actually-reliable-7155682d01a3), I made the case that the most effective AI workflows keep reinventing Systems Engineering — phases, gates, verification, traceability — because those patterns aren't bureaucratic artifacts. They're fundamental to getting reliable outputs from unreliable components. I introduced a concept development skill that applies NASA's Phase A lifecycle to the front end of AI-assisted engineering, and I argued that applying SE principles *deliberately* beats rediscovering them accidentally.

That article covered the beginning of the system development lifecycle: defining the concept. Understanding the problem before jumping to solutions.

This article covers what comes next — and where most AI workflows fall apart completely.

You've defined your concept. You know *what* you're building and *why*. Now you need to define *what the system must do* — precisely, unambiguously, and without accidentally embedding a solution. In systems engineering, this is requirements definition. In AI workflows, this is the moment where a single misplaced technology name in your prompt can shape every decision that follows.

Why does asking an AI to "build a React dashboard with a sidebar nav and a Chart.js component" consistently produce worse results than asking it to "display real-time operational metrics with sub-second refresh, accessible to colorblind users, navigable without a mouse"?

The answer is the same principle that requirements engineers have enforced for over sixty years.

## What Requirements Actually Are

Most developers hear "requirements" and think of a Jira backlog, a feature list, or maybe a product spec scribbled on a whiteboard. That's unfortunate, because requirements engineering is a rigorous discipline with a specific purpose — one that maps almost perfectly onto the challenges of working with AI.

INCOSE's Guide to Writing Requirements, now in its fourth revision, draws a careful distinction that most people miss. In the Guide's terms, a *need statement* is the result of a formal transformation of one or more sources or lifecycle concepts into an agreed-to expectation for an entity to perform some function or possess some quality within specified constraints, with acceptable risk. A *requirement statement* is the result of a formal transformation of one or more sources, needs, or higher-level requirements into an agreed-to *obligation* for that entity, again within specified constraints and with acceptable risk.

Two things to notice. First, needs can flow from sources beyond just stakeholder expectations — operational scenarios, lifecycle concepts, regulatory environments. Second, requirements can derive from higher-level requirements, not only from needs. The Guide builds this breadth in deliberately, because narrowing the input funnel too early is itself a form of premature convergence.

The operative phrase in both definitions is *formal transformation*. Requirements don't emerge from brainstorming sessions or stream-of-consciousness conversations. They are the product of deliberate analysis — the disciplined act of transforming fuzzy human desires into statements precise enough that someone (or something) can build to them, and someone else can verify the result.

Why does this formality matter? Because humans are terrible at communicating intent. We're ambiguous. We overload statements with multiple ideas. We assume shared context that doesn't exist. And most critically, we conflate what we *want* with how we think we should *get it*. The entire discipline of requirements engineering exists to defend against these tendencies.

**[IMAGE: A diagram showing the INCOSE transformation chain — stakeholder expectations flowing through "Formal Transformation" into an Integrated Set of Needs, then through another "Formal Transformation" into Design Input Requirements (the "What"), then through Architecture & Design into Design Output Specifications (the "How"), and finally into the realized System Element. The key visual distinction: a clear boundary separating "Design Inputs" from "Design Outputs." Inspired by GtWR v4 Figure 2.]**

INCOSE defines nine characteristics that every well-formed requirement must possess. Four are directly relevant to the AI parallel:

**Necessary (C1):** The requirement must trace to a real need — not an assumption, not a preference, not a habit. Every requirement should answer the question "what stakeholder need does this satisfy?" If it can't, it shouldn't exist.

**Unambiguous (C3):** The requirement must be interpretable in only one way by all intended audiences. Not "generally clear" — *only one way*. This bar exists because requirements engineers learned the hard way that if a statement *can* be misinterpreted, it *will* be.

**Singular (C5):** One requirement, one thought. No compound statements joined by "and" or "or" or "but." The moment you combine two ideas in a single requirement, you've created ambiguity about priority, scope, and verification. If one half is met and the other isn't, has the requirement been satisfied?

**Verifiable/Validatable (C7):** You must be able to prove the requirement has been met *and* confirm that it reflects the actual need. If you can't define a test, measurement, or inspection that would demonstrate compliance, the requirement is not a requirement — it's a wish. The dual label is intentional: verification confirms the system meets the requirement; validation confirms the requirement meets the need.

These aren't bureaucratic checkboxes. They're defenses against the exact failure modes humans exhibit when communicating intent. And an LLM is the most literal-minded, gap-filling "audience" your requirements will ever have. Every weakness that requirements engineering was designed to compensate for in human teams is amplified when your "team member" is a stochastic language model.

GitHub's spec-kit project — which I discussed in Part 1 as an example of the community rediscovering SE lifecycle patterns — provides an unintentional validation of this point. Their Spec-Driven Development manifesto describes specifications that must be "precise, complete, and unambiguous enough to generate working systems." That's C4 (Complete), C3 (Unambiguous), and the kind of precision that enables C7 (Verifiable/Validatable) — rolled into a single sentence. Their quality checklists are described as "unit tests for English." I've spent twenty years in requirements engineering and I've never heard the intent of requirements verification stated more elegantly.

## The Solution-Free Principle

Of all the rules in INCOSE's Guide to Writing Requirements — there are forty-two of them — one stands above the rest in its relevance to AI workflows. It's Rule R31, filed under the category of "Abstraction," and it essentially says: needs and requirements statements shall not include implementation (solution domain) specifics unless there is justification to constrain the design.

This is the Solution-Free principle. It draws a hard line between design inputs — what the system must *do* — and design outputs — *how* the system does it. These are fundamentally different artifacts that serve fundamentally different purposes, and conflating them is one of the most expensive mistakes in engineering.

**[IMAGE: A visual representation of the "For what purpose?" diagnostic. Show a requirement statement like "Traffic lights shall be used to control traffic" with an arrow asking "For what purpose?" leading to the real requirement: "The Traffic Control System shall enable safe pedestrian crossing while limiting vehicle wait time." Below, show how the solution-free requirement opens a trade space of possible implementations: traditional traffic lights, smart sensors, bollards, AI-controlled signage, roundabouts — while the solution-embedded version closes all paths except one.]**

When you embed a solution in a requirement, three things happen.

First, you close the trade space prematurely. By specifying *how*, you've eliminated every alternative the design team never gets to evaluate. Maybe the solution you named is optimal. Maybe it isn't. You never looked.

Second, you lose traceability to purpose. When someone asks "why did we use traffic lights at this intersection?", the answer *should* trace to a need for safe pedestrian crossing with acceptable vehicle wait times. But if the requirement said "use traffic lights," the answer is just "because the requirement said so" — a circular reference that tells you nothing about whether the actual need is being met.

Third, you create brittle specifications. If the embedded solution becomes infeasible — the technology is deprecated, the vendor goes under, the cost profile changes — you have to rewrite the requirement itself, because the *actual need* was never captured separately. Spec-kit's manifesto puts this in developer terms: "code is inherently a binding artifact — once you write an implementation, it's very hard to decouple from it." That's INCOSE's rationale for the design inputs versus design outputs distinction, restated in developer vernacular.

INCOSE's diagnostic for detecting this failure is a single question: *"For what purpose?"* When you encounter a requirement that states implementation, ask "for what purpose?" and the answer reveals the real requirement hiding behind the premature solution. The distinction is essentially teleological — asking what end this serves rather than what caused us to write it.

The Guide's traffic light example makes this concrete. The bad requirement — "Traffic lights shall be used to control traffic at the intersection" — names a solution. The improved version (paraphrased from GtWR v4) describes the behavior needed: when a pedestrian signals their intent to cross the street, the traffic control system shall provide the pedestrian a "Walk" signal and provide the traffic a "Stop" signal. The improved version admits any solution — smart sensors, bollards, AI-controlled signage, traditional lights — because it describes *what must happen*, not *what technology to use*.

This isn't just good SE practice. It's the single most important principle you can apply to working with AI. And the community is discovering this independently. Spec-kit's documentation includes a line in its `/speckit.specify` command that could have been pulled directly from R31: "Be as explicit as possible about what you are trying to build and why. Do not focus on the tech stack at this point."

## Solution Contamination: The AI Failure Mode

Here's what happens when you violate the Solution-Free principle in an AI workflow: the solution you provide doesn't get evaluated. It gets *adopted*. It becomes the anchor around which every subsequent decision orbits. The LLM doesn't ask "for what purpose?" It asks "what comes next, given that this solution has been chosen?"

This isn't a bug. It's how the technology works. LLMs are next-token predictors optimized for plausibility given context. If you put a solution in the context, the most plausible next tokens elaborate on that solution — they don't question it. An LLM will not push back on your technology choice. It will not suggest alternatives. It will not surface that your assumption is suboptimal.

In systems engineering, this failure mode has a name: premature convergence. INCOSE identifies it as one of the most common and costly failures in engineering programs — converging on a solution before the problem space has been adequately explored. In traditional SE, premature convergence happens because humans get excited about solutions, because organizational inertia favors the familiar, because exploring alternatives takes time.

In AI workflows, premature convergence is the *default behavior*. The system is architecturally incapable of doing anything else unless you structure your inputs to prevent it.

Jesse Vincent's Superpowers framework — which I discussed in Part 1 for its multi-agent orchestration patterns — attacks this problem directly through its brainstorming skill. Users describe a distinctive experience: instead of accepting a vague request, the skill forces a structured dialogue. It asks questions like "What brand identity are you aiming for?", "Should we prioritize a mobile-first layout or a desktop-centric one?", and "Here are three common UI patterns for displaying this data — which aligns best with your goals?" By forcing this dialogue before any implementation begins, the skill decomposes a vague, solution-embedded request into needs, constraints, and quality attributes before a single line of code is considered.

**The caching trap.** You tell the AI: "Build a caching layer using Redis to speed up our API responses." What you get is a Redis implementation. Connection pooling, serialization strategies, TTL policies, cache invalidation logic — all Redis-specific. And the AI will never mention that your actual problem — API responses taking 800ms — might be caused by an unindexed database query that a five-minute schema change would fix. Or that an in-memory LRU cache would eliminate the network hop to Redis entirely. Or that a CDN-level cache would handle the 60% of identical requests without touching your application code at all.

Now rewrite the prompt solution-free: "API responses currently take 800ms at P95. Users need sub-200ms for the dashboard workflow. The system processes 10K requests/minute with a 60% read-repeat ratio. What are my options?" The AI considers Redis — but also query optimization, application-level caching, CDN strategies, and read replicas. It may still recommend Redis. But as a considered choice against alternatives, not an unexamined assumption.

**The architecture lock-in.** You tell the AI: "Design a microservices architecture with Kafka for event streaming between services." You get microservices and Kafka. Service boundaries, topic schemas, consumer groups, exactly-once semantics — all built around the architecture you specified. The AI will never surface that a modular monolith with an internal event bus might be simpler, cheaper to operate, and entirely sufficient for your actual throughput requirements.

Rewrite it: "The system must support independent deployment of business domains, handle 50K events per second with at-least-once delivery, and allow team autonomy over technology choices within domain boundaries." Now the AI is solving a *problem* rather than implementing a *decision*.

**[IMAGE: A side-by-side comparison diagram. Left side: "Solution-Embedded Prompt" → shows a single path from prompt to implementation, with the solution propagating through every decision (architecture, error handling, testing, deployment — all contaminated by the initial solution choice). Right side: "Solution-Free Prompt" → shows the prompt branching into an analysis phase that evaluates multiple alternatives, then converging on a reasoned recommendation with trade-offs documented. Title: "The Propagation Effect."]**

The compounding effect is what makes this particularly damaging. Solution contamination doesn't just affect one decision — it shapes the entire conversation. Ask about error handling and you get Redis-specific error handling. Testing becomes Redis-specific test patterns. Three exchanges in, you're so deep in implementation details that the original problem — "API responses are slow" — has been completely forgotten.

INCOSE's Guide identifies this same failure pattern in human engineering teams. Section 4.9.1 describes how projects developing upgrades to existing systems will document design-output-level requirements as design inputs — focusing on known solutions rather than asking "for what purpose?" The result is requirements that describe *what exists* rather than *what is needed*. The AI version is identical in structure. The only difference is speed: a human team might take weeks to realize they've been specifying implementation. An AI locks into a premature solution in the first response.

## The Rules That Map

The Solution-Free principle is the headliner, but it's not the only rule in the Guide that maps to AI workflows. Two others are worth examining in depth — not because they're the only relevant rules (the Guide's forty-two rules on singularity, explicit conditions, and combinators all have clear parallels), but because they address the two AI failure modes I see most often after premature convergence: vagueness and lack of structure.

**Vague Terms (R7) and Measurable Performance (R34).** The Guide maintains a list of terms that should never appear in a requirement, including: "some," "any," "allowable," "several," "many," "approximate," "sufficient," "adequate," "appropriate," "efficient," "effective," "reasonable." Each creates an interpretation gap — a space where the reader fills in their own definition of what "adequate" means.

That list describes the average AI prompt. And it explains a failure mode that most people attribute to the model rather than to themselves.

Tell an AI to "make it efficient" and watch what happens. The model has to decide: efficient in terms of what? Memory? Latency? Cost? Lines of code? Developer time? It will pick one — usually whatever interpretation is most statistically common in its training data for the surrounding context — and optimize for that without telling you what it chose. You'll review the output, find it doesn't match your intent, and conclude the AI "doesn't understand." It understood fine. You just didn't say what you meant.

Replace "make it efficient" with "reduce memory allocation to under 512MB while maintaining sub-200ms P95 latency under 10K concurrent connections" and the output transforms. Not because the AI became more capable, but because there's nothing left to interpret. Rule R34 formalizes this: every quantitative requirement needs specific, measurable performance targets. Not "fast" but "sub-200ms." Not "high availability" but "99.95% uptime measured monthly." Not "scalable" but "linear throughput increase to 100K concurrent users with no single-request latency exceeding 500ms."

The practical test is simple: could two different engineers (or two different AI sessions) read your prompt and produce outputs that satisfy it in incompatible ways? If yes, you have a vague term somewhere. The requirement isn't wrong — it's incomplete.

GSD — which I covered in Part 1 for its milestone-based lifecycle patterns — has independently codified the same principle. Its documentation flags the anti-pattern "Authentication works" and corrects it to "User can log in with email/password." The first is untestable — what does "works" mean? The second satisfies both Verifiable/Validatable (C7) and Measurable Performance (R34). You can write a test for it. You know when you're done. GSD generalizes the insight: "Task Completion ≠ Goal Achievement — Verify outcomes, not just task completion." A systems engineer would recognize that instantly as the difference between verification and validation — and GSD's "goal-backward verification" implements both, asking not "what tasks did we do?" but "what must be TRUE for this to work?"

**Structured Statements (R1) and Requirement Patterns.** The Guide's very first rule requires that requirements conform to agreed-upon patterns — structured templates with defined building blocks for conditions, subjects, actions, constraints, and values. A typical INCOSE requirement pattern looks something like: *[Condition] [Subject] [Action] [Object] [Constraint] [Value]*. "When battery level drops below 10%, the power management system shall reduce display brightness to 40% within 2 seconds."

The pattern forces completeness. Every slot is a question the author must answer: under what condition? What entity is responsible? What action? On what object? Within what constraints? To what measurable value? Leave any slot empty and you've left a gap that the reader — or the AI — fills with assumptions.

This maps more directly to AI prompt engineering than any other rule in the Guide, because the most effective prompting techniques *are* requirement patterns.

System prompt templates are requirement patterns. When Anthropic's own documentation recommends structuring prompts with XML-tagged sections — `<context>`, `<instructions>`, `<constraints>`, `<output_format>` — that's R1. Each tag is a slot in a pattern, and the tags exist for the same reason INCOSE's building blocks exist: to force the author to address each dimension of the requirement explicitly rather than hoping the audience infers it.

Few-shot examples are requirement patterns. When you show an AI three input-output pairs before asking it to process new input, you're providing a pattern that constrains interpretation. The examples don't just illustrate what you want — they define the structure of what "correct" looks like, eliminating ambiguity that prose instructions leave open. INCOSE's Appendix C catalogs requirement patterns for the same purpose: not because engineers can't write freeform text, but because patterns produce more consistent results than unstructured prose.

Structured output formats are requirement patterns. Specifying that the AI should respond in JSON with defined fields, or in a markdown template with specific sections, constrains the output space in the same way that a requirement pattern constrains the requirement space. The AI isn't generating from the full distribution of possible responses — it's generating within a structure that makes omissions visible.

Superpowers' plan-writing phase provides a concrete implementation. It breaks work into tasks where each task follows a consistent structure: what to do, what success looks like, what constraints apply. The framework's creator described the target audience for these plans as "an enthusiastic junior engineer with poor taste, no judgement, no project context, and an aversion to testing" — and noted that the plan needs to be *that explicit*. That's R1 and C3 (Unambiguous) working together: define a pattern, fill every slot, and leave nothing to interpretation.

The underlying insight is the same one INCOSE arrived at decades ago: unstructured communication fails not because the communicator lacks knowledge, but because prose gives no signal when something has been omitted. Patterns do. A template with an empty slot is visibly incomplete. A paragraph missing a constraint is just a paragraph.

**[IMAGE: A visual "translation table" showing three INCOSE rules on the left mapped to their AI prompt engineering equivalents on the right, with the community tool that independently implements each: R31 (Solution Free) → Problem-first prompting → Spec-kit's "do not focus on the tech stack." R7/R34 (Vague Terms/Measurable Performance) → Specific, measurable prompt criteria → GSD's success criteria anti-patterns. R1 (Structured Statements) → System prompt templates, XML tags, few-shot examples, structured output → Superpowers' task structure. The visual makes the parallel unmistakable.]**

## Requirements Engineering *Is* Prompt Engineering

The INCOSE Guide to Writing Requirements anticipated this convergence. In its audience section, the Guide notes that it "may also assist tool vendors who are applying Artificial Intelligence (AI) and Natural Language Processing (NLP) to the evaluation of needs and requirement statements." The authors understood that the principles of clear, unambiguous, solution-free, verifiable communication would apply regardless of whether the audience was a human engineer or a machine.

The community is proving them right. The spec-kit community has recently started debating whether specifications should represent the "target state" rather than incremental changes, and whether the concept of a "spec" should be separated from a "spec change." They're independently discovering what INCOSE calls requirements management — the practice of maintaining a baseline set of requirements as a living document, distinct from the change management process that modifies that baseline. They're rediscovering why it matters, one GitHub discussion at a time.

GSD reframed its entire development philosophy around a question that is, functionally, the Solution-Free principle expressed as a methodology: "Instead of asking 'what should we build?', ask 'what must be TRUE for the goal to be achieved?'" The first question invites implementation in the answer. The second invites measurable conditions of satisfaction. That single reframing is the difference between R31-violating specifications and R31-compliant ones.

These disciplines are solving the same problem with the same tools: precision, structure, constraints, verification. The fact that one audience is human and the other is a neural network doesn't change the fundamental challenge — *how do you communicate intent clearly enough that the receiver builds what you actually need?*

The AI tooling community is writing the Guide to Writing Requirements. They're just writing it in YAML and markdown instead of IEEE format.

So here's the invitation, same as Part 1 but one level deeper: if you're writing prompts for AI, you are writing requirements. Full stop. The question isn't whether requirements engineering principles apply — they do, by the nature of what you're doing. The question is whether you're applying them deliberately, or writing them the way most untrained humans write requirements: vaguely, ambiguously, loaded with implicit conditions, and contaminated with premature solutions.

## Applying It on Purpose

Everything I've described so far represents the parallels between established SE practice and the organic discovery happening in the AI community. But as with concept development in Part 1, the question is: what happens when you apply these principles *intentionally*?

That's the purpose of the requirements definition skill I'm currently building — the next component in the SE-based skill suite that began with concept-dev. Where concept-dev implements NASA's Phase A to establish *what you're building and why*, the requirements definition skill implements the left leg of the Vee Model's next phase: formally defining *what the system must do*, with the full discipline of INCOSE's forty-two rules and nine characteristics built into the workflow.

### Design Philosophy: Make the Rules Structural, Not Advisory

The central design problem was this: INCOSE's forty-two rules and nine characteristics are well-documented, but in practice they're advisory. A human requirements engineer reads the Guide, internalizes the principles, and applies judgment. An AI doesn't internalize anything — it processes context. Telling an LLM "follow INCOSE's rules" is about as effective as telling a junior engineer "write good requirements." The rules need to be *structural* — embedded in the workflow so that violating them requires actively working around the system rather than passively forgetting to apply them.

The skill — `requirements-dev` — addresses this by splitting quality enforcement into two tiers that run on every requirement before it can be registered.

**Tier 1 is deterministic.** Sixteen rules from the Guide are implemented as pattern-matching checks in a Python script — no LLM involved, no interpretation, no variability. The script maintains curated word lists drawn from the Guide's own appendices: fifty-plus vague terms (R7), escape clauses like "where possible" and "if practical" (R8), ambiguous pronouns (R24), absolutist language (R26). It detects passive voice (R2), flags combinators that signal compound requirements (R19), catches open-ended clauses like "etc." and "including but not limited to" (R9), and identifies purpose phrases that suggest a requirement is actually a rationale (R20). Each violation returns the exact matched text, its character position in the statement, the rule it violates, and a concrete suggestion for fixing it.

This matters because these sixteen rules account for the majority of quality failures in practice, and they're precisely the failures that LLMs are worst at self-detecting. An LLM will happily generate "The system shall provide adequate performance under normal conditions" — a statement that violates R7 (vague: "adequate," "normal"), is unverifiable (C8), and would be flagged by any trained requirements engineer. The deterministic tier catches it instantly, before the LLM has a chance to elaborate on a fundamentally flawed statement.

**Tier 2 is semantic.** Nine rules that require contextual judgment — necessity, feasibility, singularity, verifiability, completeness, non-ambiguity, design-freedom, traceability, and conformance — are evaluated by a dedicated quality-checker agent using chain-of-thought reasoning. This agent receives the requirement statement, the block it belongs to, its parent need, and the existing requirements set (for terminology consistency, per R36). It produces reasoned assessments for each semantic rule, with high-confidence flags blocking registration and lower-confidence flags presented as informational.

The two-tier split is deliberate. Deterministic checks are fast, reproducible, and non-negotiable — they enforce the floor. Semantic checks handle the judgment calls that pattern matching can't reach. Together, they implement what the INCOSE Guide envisions but rarely achieves in practice: quality checking that's both rigorous and scalable.

### The Workflow: Concept In, Specification Out

The skill operates in three phases with mandatory gates between them — the same phase-gate discipline from Part 1's concept-dev, applied one level deeper.

**Phase 1 (Foundation)** begins by ingesting the artifacts that concept-dev produced. The blackbox diagram provides the system's functional blocks. The source and assumption registries carry forward as traceability anchors. ConOps scenarios and capability descriptions become candidates for stakeholder needs. If no concept-dev artifacts exist — because the user is starting from scratch or working with an existing system — the skill falls back to guided manual entry, collecting block definitions, capabilities, and inter-block relationships through a structured dialogue.

From those blocks and capabilities, the skill formalizes stakeholder needs using INCOSE's need-statement patterns. Each need gets a unique identifier, a structured statement, source traceability back to its concept-dev origin, and a status that the user must explicitly set: approved, deferred with rationale, or rejected with rationale. Needs are presented in batches of two or three for review — not dumped in a list of thirty. The metered interaction pattern prevents the failure mode where an AI generates an impressive-looking wall of content that the user rubber-stamps without reading.

Once needs are formalized, the requirements engine walks through each functional block with five type-guided passes: functional (what the block must do), performance (how well), interface (how it connects), constraint (what limits it), and quality (non-functional characteristics like reliability and maintainability). The fixed ordering matters. Functional requirements come first because they establish the behavioral baseline. Performance requirements quantify that baseline. Interface requirements define the boundaries. Constraints and quality attributes bound the solution space. This sequence mirrors the natural dependency chain — you can't specify how fast something must respond until you've defined what it's responding to.

For each requirement, the pipeline is: the AI drafts a statement using the INCOSE pattern (*"The [subject] shall [action] [measurable criterion]"*), Tier 1 deterministic checks run, violations are presented and resolved, Tier 2 semantic checks run, the user reviews and approves, a verification method is planned based on the requirement type, and only then is the requirement registered with a traceability link to its parent need. No requirement enters the registry without passing both quality tiers. No requirement exists without a parent need. No need exists without a source.

The phase concludes with deliverable generation: a requirements specification organized by block and type, a bidirectional traceability matrix linking sources through needs through requirements through verification methods, and a verification matrix mapping every requirement to its planned test method and success criteria. Optionally, the registries export to ReqIF — the industry-standard XML interchange format — for integration with tools like DOORS or Polarion.

**Phase 2 (Validation and Research)** runs cross-block analysis that individual requirement checks can't catch. A set validator scans for interface coverage gaps (block-to-block relationships that lack interface requirements), near-duplicate statements across blocks (using n-gram cosine similarity), terminology inconsistencies (the same concept called "user" in one block and "client" in another), uncovered needs (approved needs with no derived requirements), and open TBD/TBR items. A separate cross-cutting sweep checks the six INCOSE set-level characteristics (C10–C15): completeness, consistency, feasibility, comprehensibility, validatability, and correctness.

A dedicated research agent handles the measurable-performance problem. When requirements contain performance targets — response times, throughput thresholds, availability percentages — the agent searches for published industry benchmarks to validate that the targets are both ambitious and feasible. Results come back as structured tables with source citations, giving the user evidence to support or revise their numbers rather than guessing.

**Phase 3 (Decomposition)** handles what happens when system-level requirements need to be allocated to subsystems. The decomposer takes baselined requirements and distributes them across sub-blocks with documented allocation rationale — why this requirement goes to this subsystem, what portion of the performance budget it receives, what interface obligations it creates. Each decomposition level re-enters the full quality-checking pipeline. The skill enforces a maximum of three decomposition levels, because in practice, going deeper than that means you're doing detailed design, not requirements development.

### What the Skill Actually Enforces

The design philosophy boils down to three structural constraints that the skill makes difficult to violate.

First, **quality is not optional.** Every requirement passes through twenty-five quality checks (sixteen deterministic, nine semantic) before registration. There's no "skip quality check" shortcut, no way to batch-register unchecked statements, no override that bypasses the pipeline. This is the structural equivalent of a compiler refusing to build code with syntax errors — except the "syntax" is INCOSE's Guide to Writing Requirements.

Second, **traceability is not an afterthought.** The skill won't register a requirement without a parent need. It won't formalize a need without a source. Every link in the chain — source to need to requirement to verification method — is captured at the moment of creation, not reconstructed after the fact. The bidirectional traceability matrix is a natural byproduct of the workflow, not a separate documentation exercise.

Third, **the human stays in the loop.** The metered interaction pattern — two to three requirements per round, explicit approval at every gate, batched presentation with review options — prevents the AI from generating a fifty-requirement specification that the user accepts wholesale. The skill is designed to be *slow on purpose*, because the history of requirements engineering teaches that speed in requirements development correlates with defects in the final system.

### Getting Started

The skill is available as a Claude Code plugin. Copy or symlink the `requirements-dev/` directory into your Claude Code plugins path — it registers automatically via its plugin manifest. The only hard dependency is Python 3.11 or later for the quality-checking scripts. Optional packages (`reqif` for ReqIF XML export, `crawl4ai` for deep web crawling during TPM research) enhance specific capabilities but aren't required for the core workflow.

If you've already run concept-dev on your project, the path is:

```
/reqdev:init           → Ingest concept-dev artifacts, create workspace
/reqdev:needs          → Formalize stakeholder needs per block
/reqdev:requirements   → Develop requirements with quality checking
/reqdev:deliver        → Generate specification documents
```

If you're starting fresh without concept-dev artifacts, `/reqdev:init` walks you through manual block and stakeholder definition before proceeding through the same pipeline.

Use `/reqdev:status` at any point to see where you are. Use `/reqdev:resume` to pick up exactly where you left off after an interruption — the skill tracks your position down to the current block and type pass.

---

## Where This Is Going

With concepts defined (Part 1) and requirements established (Part 2), the Vee Model's left leg continues downward into architecture and design. Part 3 will address functional decomposition and architectural design — how to move from *what* the system must do to *how* it's organized to do it, and how the same SE principles prevent AI from producing monolithic, untestable designs that technically satisfy every requirement while being impossible to maintain, extend, or verify.

**[IMAGE: The stylized INCOSE Vee Model from Part 1, but with Part 1's "Concept Development" phase and Part 2's "Requirements Definition" phase both highlighted as completed, and Part 3's "Architecture & Design" phase highlighted as the next focus. The visual shows progression down the left leg of the Vee.]**

Each article in this series walks through a phase of the lifecycle, introduces the relevant skill, and connects the SE principles back to patterns you're probably already discovering in your own AI workflows. If you haven't read Part 1, it covers the foundational case for why these principles apply to AI at all — and introduces the concept-dev skill that precedes the requirements work discussed here.

The core insight of this article is simple enough to fit on an index card: **stop telling AI** ***how.*** **Start telling it** ***what*** **— precisely, measurably, and traceably.**

It's not a new idea. It's a sixty-year-old idea that works.

---

*This is Part 2 of a series on applying Systems Engineering principles to AI workflows. Part 1: "[The 60-Year-Old Framework That Makes AI Actually Reliable](https://medium.com/@dunnoda/the-60-year-old-framework-that-makes-ai-actually-reliable-7155682d01a3)." Next up: how functional decomposition and architectural design prevent AI from producing monolithic, unmaintainable systems — and the skill that enforces it.*
