# Skill Validation Checklist

Use this checklist to verify skill quality before packaging.

## Metadata Validation

- [ ] Name is max 64 characters
- [ ] Name uses hyphen-case (lowercase letters, numbers, hyphens only)
- [ ] Name does not start or end with hyphen
- [ ] Name has no consecutive hyphens
- [ ] Name does not contain reserved words ("anthropic", "claude")
- [ ] Name matches directory name exactly
- [ ] Description is non-empty
- [ ] Description is max 1024 characters
- [ ] Description contains no XML tags (angle brackets)
- [ ] Description is written in third person
- [ ] Description includes both what the skill does AND when to use it

## Structure Validation

- [ ] SKILL.md exists at root of skill directory
- [ ] SKILL.md is under 500 lines
- [ ] YAML frontmatter has only `name` and `description` fields
- [ ] Bundled resources are in appropriate directories (scripts/, references/, assets/)
- [ ] Reference files are one level deep from SKILL.md (no nested references)
- [ ] Reference files over 100 lines have a table of contents
- [ ] All file paths use forward slashes (Unix-style)
- [ ] No extraneous files (README.md, CHANGELOG.md, etc.)

## Content Quality

- [ ] Description is specific with key terms that trigger selection
- [ ] Instructions use imperative form (e.g., "Run the script" not "The script should be run")
- [ ] Examples are concrete and realistic
- [ ] Workflows have clear, sequential steps
- [ ] Complex operations have validation/verification steps
- [ ] Degree of freedom matches task fragility (more constraints for fragile operations)
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout

## Script Quality (if applicable)

- [ ] Scripts solve problems directly (don't punt decisions to Claude)
- [ ] Scripts have explicit error handling
- [ ] Magic constants are justified or configurable
- [ ] Required packages are listed and verified
- [ ] Comments explain "why" not "what"
- [ ] Scripts tested by actually running them

## Testing

- [ ] Created 3+ realistic test scenarios
- [ ] Tested with at least one model (ideally Haiku, Sonnet, and Opus)
- [ ] Edge cases considered and tested
- [ ] Evaluations built before extensive documentation

## Common Issues to Avoid

- [ ] No Windows-style paths (backslashes)
- [ ] No vague or generic naming (helper, utils, tools)
- [ ] No deeply nested file references
- [ ] No code without explanatory context
- [ ] No over-explanation of concepts Claude already knows
- [ ] No duplicate information between SKILL.md and reference files
