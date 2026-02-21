# Subsystem Decomposition Patterns

Reference document for decomposing system-level requirements into subsystem allocations.

## When to Decompose

Decomposition is appropriate when:
- A functional block is too complex to implement as a single unit
- Multiple teams or components will share responsibility for a capability
- Requirements at the current level are too abstract for direct implementation
- Interface boundaries need to be formalized between sub-functions

Decomposition is NOT appropriate when:
- The block is already at implementation level
- Further decomposition would create artificial boundaries
- The requirement is a constraint that applies uniformly

## How to Identify Sub-Functions

1. **Functional decomposition:** Break a function into sequential steps or parallel sub-functions
2. **Data decomposition:** Separate by data domain (e.g., user data vs. transaction data)
3. **Component decomposition:** Separate by deployment unit or technology boundary
4. **Quality decomposition:** Separate by quality concern (e.g., security subsystem, monitoring subsystem)

## Allocation Rationale Templates

Each allocation should document:
- **Parent requirement:** REQ-xxx being decomposed
- **Child requirements:** REQ-xxx-01, REQ-xxx-02, etc.
- **Rationale:** Why this decomposition approach was chosen
- **Coverage:** How child requirements collectively satisfy the parent
- **Verification:** How parent-level verification is achieved through children

### Template:
```
REQ-{parent} is allocated to {sub-block} because {rationale}.
The child requirements {REQ-child-list} collectively satisfy the parent
by {coverage explanation}.
```

## Stopping Conditions

Stop decomposing when:
- Requirements are directly implementable by a single team/component
- Further decomposition adds complexity without clarity
- Maximum decomposition level (3) is reached
- All allocated requirements have clear verification methods

## Maximum Level Rationale (max_level=3)

Three levels of decomposition (system, subsystem, component) align with standard systems engineering practice:
- **Level 0:** System-level requirements (from needs)
- **Level 1:** Subsystem-level requirements (first decomposition)
- **Level 2:** Component-level requirements (second decomposition)
- **Level 3:** Detailed component requirements (maximum depth)

Beyond level 3, requirements typically transition to design specifications rather than formal requirements.
