# Quality Criteria Reference

Assessment rubrics and quality standards for documentation evaluation.

## Quality Dimensions

### 1. Accuracy
Content is factually correct and up-to-date.

| Level | Description |
|-------|-------------|
| 5 - Excellent | All facts verified, sources cited, no errors found |
| 4 - Good | Verified content, minor omissions, sources available |
| 3 - Adequate | Generally accurate, some unverified claims |
| 2 - Poor | Contains errors, outdated information |
| 1 - Unacceptable | Major factual errors, misleading content |

### 2. Completeness
All necessary information is present.

| Level | Description |
|-------|-------------|
| 5 - Excellent | Comprehensive coverage, no gaps, includes edge cases |
| 4 - Good | Covers main topics, minor gaps in edge cases |
| 3 - Adequate | Basic coverage, notable gaps exist |
| 2 - Poor | Significant missing content, incomplete sections |
| 1 - Unacceptable | Fragmentary, major topics missing |

### 3. Clarity
Content is easy to understand for target audience.

| Level | Description |
|-------|-------------|
| 5 - Excellent | Crystal clear, no ambiguity, appropriate level |
| 4 - Good | Clear with minor ambiguities, mostly appropriate |
| 3 - Adequate | Understandable with effort, some jargon issues |
| 2 - Poor | Confusing, inconsistent terminology, wrong level |
| 1 - Unacceptable | Incomprehensible, misleading, wrong audience |

### 4. Structure
Content is well-organized and navigable.

| Level | Description |
|-------|-------------|
| 5 - Excellent | Logical flow, clear hierarchy, easy navigation |
| 4 - Good | Good organization, minor structural issues |
| 3 - Adequate | Basic structure, some navigation difficulties |
| 2 - Poor | Disorganized, hard to find information |
| 1 - Unacceptable | No discernible structure, chaotic |

### 5. Usability
Content serves its intended purpose effectively.

| Level | Description |
|-------|-------------|
| 5 - Excellent | Users accomplish goals efficiently, high satisfaction |
| 4 - Good | Users succeed with minor friction |
| 3 - Adequate | Users can succeed but with difficulty |
| 2 - Poor | Users struggle, frequent failures |
| 1 - Unacceptable | Users cannot accomplish goals |

## Diátaxis-Specific Criteria

### Tutorial Quality

| Criterion | Assessment Questions |
|-----------|---------------------|
| **Learning Focus** | Does it teach, not just tell? |
| **Guided Experience** | Are steps clear and sequential? |
| **Immediate Results** | Does each step produce visible outcome? |
| **Repeatability** | Will it work the same way every time? |
| **Minimal Prerequisites** | Can a newcomer actually start? |
| **Confidence Building** | Does the user feel successful? |

**Tutorial Scoring:**
```
□ Learning-oriented (not task-completion)         [0-2 pts]
□ Clear start and end points                      [0-2 pts]
□ Visible results at each step                    [0-2 pts]
□ Minimal explanation (just enough to proceed)    [0-2 pts]
□ Tested and repeatable                           [0-2 pts]
                                          Total: ___/10
```

### How-To Guide Quality

| Criterion | Assessment Questions |
|-----------|---------------------|
| **Goal Clarity** | Is the goal clear from the title? |
| **Assumed Competence** | Does it avoid teaching basics? |
| **Problem Focus** | Does it solve a specific problem? |
| **Actionable Steps** | Can each step be executed? |
| **Minimal Explanation** | Is context kept brief? |
| **Completeness** | Does it cover the full task? |

**How-To Scoring:**
```
□ Clear goal in title                             [0-2 pts]
□ Assumes basic knowledge                         [0-2 pts]
□ Problem-focused content                         [0-2 pts]
□ Actionable, concrete steps                      [0-2 pts]
□ Troubleshooting included                        [0-2 pts]
                                          Total: ___/10
```

### Reference Quality

| Criterion | Assessment Questions |
|-----------|---------------------|
| **Completeness** | Are all items documented? |
| **Accuracy** | Are specifications correct? |
| **Organization** | Is structure logical for lookup? |
| **Consistency** | Is formatting uniform? |
| **Neutrality** | Is content factual, not prescriptive? |
| **Currency** | Is information up-to-date? |

**Reference Scoring:**
```
□ Comprehensive coverage                          [0-2 pts]
□ Accurate specifications                         [0-2 pts]
□ Logical organization for lookup                 [0-2 pts]
□ Consistent formatting                           [0-2 pts]
□ Neutral, factual tone                          [0-2 pts]
                                          Total: ___/10
```

### Explanation Quality

| Criterion | Assessment Questions |
|-----------|---------------------|
| **Context Provided** | Is background given? |
| **Why Explored** | Are motivations explained? |
| **Conceptual Depth** | Is understanding developed? |
| **Multiple Angles** | Are different perspectives offered? |
| **Connections Made** | Are concepts linked together? |
| **Mental Model** | Does it build understanding? |

**Explanation Scoring:**
```
□ Provides context and background                 [0-2 pts]
□ Explores "why" questions                        [0-2 pts]
□ Multiple perspectives offered                   [0-2 pts]
□ Connects to related concepts                    [0-2 pts]
□ Builds clear mental model                       [0-2 pts]
                                          Total: ___/10
```

## Documentation Set Assessment

### Coverage Matrix

```markdown
## Coverage Assessment

### By Quadrant

| Quadrant | Docs Count | Quality Avg | Completeness |
|----------|------------|-------------|--------------|
| Tutorial | ___ | ___/10 | ___% |
| How-To | ___ | ___/10 | ___% |
| Reference | ___ | ___/10 | ___% |
| Explanation | ___ | ___/10 | ___% |

### By User Journey

| Stage | Coverage | Quality |
|-------|----------|---------|
| Discovery | [None/Partial/Full] | ___/10 |
| Onboarding | [None/Partial/Full] | ___/10 |
| First Success | [None/Partial/Full] | ___/10 |
| Daily Use | [None/Partial/Full] | ___/10 |
| Advanced Use | [None/Partial/Full] | ___/10 |
| Troubleshooting | [None/Partial/Full] | ___/10 |
```

### Navigation Assessment

| Criterion | Pass/Fail | Notes |
|-----------|-----------|-------|
| Clear entry point | □ | |
| Quadrant navigation obvious | □ | |
| Cross-references work | □ | |
| No orphan pages | □ | |
| No dead links | □ | |
| Search-friendly structure | □ | |
| Mobile-friendly | □ | |

### Content Health

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Orphan pages | 0 | ___ | □ |
| Dead links | 0 | ___ | □ |
| Mixed-quadrant docs | 0 | ___ | □ |
| Outdated content (>6mo) | <10% | ___% | □ |
| Missing examples | 0 | ___ | □ |
| Untested code | 0 | ___ | □ |

## Assessment Templates

### Individual Document Assessment

```markdown
## Document Assessment: [path]

**Assessed**: [date]
**Assessor**: [name/AI session]

### Classification
- **Quadrant**: [Tutorial/How-To/Reference/Explanation]
- **Target Audience**: [description]
- **Purpose**: [what it helps users do/understand]

### Quality Scores
| Dimension | Score | Notes |
|-----------|-------|-------|
| Accuracy | ___/5 | |
| Completeness | ___/5 | |
| Clarity | ___/5 | |
| Structure | ___/5 | |
| Usability | ___/5 | |
| **Total** | **___/25** | |

### Quadrant-Specific Score
[Use appropriate rubric above]
Score: ___/10

### Issues Identified
1. [Issue 1 - severity: High/Medium/Low]
2. [Issue 2 - severity: High/Medium/Low]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

### Source Verification
- Sources cited: [yes/no]
- Sources verified: [yes/no/partial]
- Outdated sources: [list if any]
```

### Documentation Set Assessment

```markdown
## Documentation Set Assessment

**Project**: [name]
**Assessed**: [date]
**Scope**: [what was assessed]

### Executive Summary
[2-3 sentences on overall quality and key findings]

### Quadrant Coverage

| Quadrant | Count | Avg Quality | Status |
|----------|-------|-------------|--------|
| Tutorial | | /10 | [Good/Needs Work/Missing] |
| How-To | | /10 | [Good/Needs Work/Missing] |
| Reference | | /10 | [Good/Needs Work/Missing] |
| Explanation | | /10 | [Good/Needs Work/Missing] |

### Strengths
1. [Strength 1]
2. [Strength 2]

### Weaknesses
1. [Weakness 1]
2. [Weakness 2]

### Critical Gaps
1. [Gap 1 - impact: High]
2. [Gap 2 - impact: Medium]

### Recommendations (Prioritized)

| Priority | Recommendation | Effort | Impact |
|----------|----------------|--------|--------|
| 1 | [action] | [H/M/L] | [H/M/L] |
| 2 | [action] | [H/M/L] | [H/M/L] |

### Metrics Summary
| Metric | Value | Target | Gap |
|--------|-------|--------|-----|
| Total docs | | | |
| Quality average | /25 | 20 | |
| Coverage score | % | 80% | |
| Navigation score | /7 | 7 | |
```

## Quality Gates

### Minimum Viable Documentation

For initial release:
- [ ] Landing/Overview page (explains what it is)
- [ ] Quickstart tutorial (5-minute first experience)
- [ ] At least one how-to for most common task
- [ ] Core reference documentation
- [ ] Installation/setup guide

### Professional Quality

For production documentation:
- [ ] All MVD requirements met
- [ ] Complete quadrant coverage
- [ ] Average quality score ≥ 20/25
- [ ] No critical gaps
- [ ] Navigation health: all checks pass
- [ ] All content dated within 6 months
- [ ] Code examples tested

### Exemplary Quality

For best-in-class documentation:
- [ ] All Professional requirements met
- [ ] Average quality score ≥ 23/25
- [ ] Interactive tutorials or playground
- [ ] Video content for key tutorials
- [ ] Community contribution guidelines
- [ ] Regular update cadence
- [ ] User feedback integration
- [ ] Analytics-informed improvements
