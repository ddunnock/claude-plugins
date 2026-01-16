# Diátaxis Documentation Framework

This project follows the [Diátaxis](https://diataxis.fr/) documentation framework, which organizes content into four distinct categories based on user needs and the nature of the information.

## The Four Quadrants

| Category          | Orientation   | Purpose                      |
|-------------------|---------------|------------------------------|
| **Tutorials**     | Learning      | Teach through guided lessons |
| **How-to Guides** | Tasks         | Solve specific problems      |
| **Reference**     | Information   | Describe the machinery       |
| **Explanation**   | Understanding | Clarify concepts             |

### Tutorials (`tutorials/`)

**Learning-oriented** documentation that takes readers through a series of steps to complete a project.

- **Goal**: Help newcomers get started and learn by doing
- **Approach**: Step-by-step instructions with a clear beginning and end
- **Focus**: The learning experience, not the final product

**Characteristics:**
- Follows a logical sequence
- Produces visible, working results
- Explains what the user will accomplish upfront
- Avoids distractions and tangents

**Example content:**
- "Getting Started with setechkit"
- "Build Your First Project"
- "A Complete Walkthrough"

### How-to Guides (`how-to/`)

**Task-oriented** documentation that provides practical steps to solve specific problems.

- **Goal**: Help users accomplish a specific task
- **Approach**: Direct instructions assuming basic knowledge
- **Focus**: The outcome, not the learning process

**Characteristics:**
- Addresses a specific question or problem
- Assumes the reader knows what they want to do
- Provides a clear sequence of actions
- Is self-contained and focused

**Example content:**
- "How to Configure X"
- "Migrating from Version 1 to Version 2"
- "Troubleshooting Common Errors"

### Reference (`reference/`)

**Information-oriented** documentation that describes the technical machinery.

- **Goal**: Provide accurate, complete technical descriptions
- **Approach**: Structured, consistent, factual
- **Focus**: What things are and how they work

**Characteristics:**
- Organized for quick lookup
- Consistent in structure and style
- Complete and accurate
- Purely descriptive, not instructional

**Example content:**
- API documentation
- Configuration options
- CLI command reference
- Data schemas

### Explanation (`explanation/`)

**Understanding-oriented** documentation that clarifies and illuminates concepts.

- **Goal**: Help users understand the "why" behind decisions and concepts
- **Approach**: Discursive, exploratory prose
- **Focus**: Context, background, and reasoning

**Characteristics:**
- Provides context and background
- Explains design decisions
- Discusses alternatives and trade-offs
- Connects concepts together

**Example content:**
- "Architecture Overview"
- "Why We Chose X Over Y"
- "Understanding the Data Model"
- "Design Principles"

## Decision Matrix

Use this matrix to determine where your content belongs:

```
                       ACTION                    COGNITION
                 (applied knowledge)          (pure knowledge)
                         │                           │
    ACQUISITION          │                           │
    (learning)    ┌──────┴──────┐            ┌───────┴───────┐
                  │  TUTORIALS  │            │  EXPLANATION  │
                  │  (Learning) │            │(Understanding)│
                  │ "Follow     │            │ "Here's       │
                  │  along..."  │            │  why..."      │
                  └─────────────┘            └───────────────┘
                         │                           │
    ─────────────────────┼───────────────────────────┼─────────────
                         │                           │
    APPLICATION          │                           │
    (using)      ┌───────┴───────┐            ┌──────┴──────┐
                 │ HOW-TO        │            │  REFERENCE  │
                 │ GUIDES(Goals) │            │(Information)│
                 │ "Do this      │            │ "X is Y,    │
                 │  to..."       │            │  does Z..." │
                 └───────────────┘            └─────────────┘
```

## Writing Guidelines

### General Principles

1. **One type per document**: Don't mix tutorials with reference material
2. **Clear purpose**: Each document should have a single, clear objective
3. **Consistent structure**: Follow the patterns established in each category
4. **Cross-reference**: Link between categories when helpful

### Category-Specific Guidelines

#### Tutorials
- Use "we" and "our" to create a collaborative tone
- Include all steps, even obvious ones
- Test your tutorial with real beginners
- Keep scope manageable (30-60 minutes)

#### How-to Guides
- Start with a clear problem statement
- Use numbered steps
- Include prerequisites upfront
- Provide only necessary context

#### Reference
- Use consistent formatting throughout
- Include all options/parameters
- Keep descriptions factual and concise
- Organize alphabetically or logically

#### Explanation
- Write in a conversational but professional tone
- Use analogies and examples
- Connect to other documentation
- Don't include step-by-step instructions

## Contributing Documentation

1. **Identify the type**: Determine which quadrant your content belongs to
2. **Check for overlap**: Ensure similar content doesn't already exist
3. **Follow the template**: Use the README in each directory as a guide
4. **Request review**: Have someone unfamiliar with the topic review

## Resources

- [Diátaxis Official Website](https://diataxis.fr/)
- [The Grand Unified Theory of Documentation](https://diataxis.fr/compass/)
