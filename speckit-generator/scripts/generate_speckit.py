#!/usr/bin/env python3
"""
generate_speckit.py - Generate a complete SpecKit package

Usage: python generate_speckit.py --requirements <file> --output-dir <dir> [options]

Generates the directory structure and starter files for a SpecKit package
based on requirements analysis.

Inputs:
  - --requirements: Path to requirements document or analysis
  - --output-dir: Output directory for generated package
  - --include-examples: Include example content in templates
  - --project-name: Project name for context
  - --json: Output generation report as JSON

Outputs:
  - Complete .claude directory structure with starter files

Exit Codes:
  - 0: Generation successful
  - 1: Generation failed
  - 2: Input error
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def create_directory_structure(base_dir: Path) -> Dict[str, Path]:
    """Create the standard SpecKit directory structure."""
    dirs = {
        'commands': base_dir / 'commands',
        'commands/requirements': base_dir / 'commands' / 'requirements',
        'commands/architecture': base_dir / 'commands' / 'architecture',
        'commands/trades': base_dir / 'commands' / 'trades',
        'commands/risk': base_dir / 'commands' / 'risk',
        'commands/test': base_dir / 'commands' / 'test',
        'commands/review': base_dir / 'commands' / 'review',
        'scripts': base_dir / 'scripts',
        'scripts/bash': base_dir / 'scripts' / 'bash',
        'scripts/python': base_dir / 'scripts' / 'python',
        'templates': base_dir / 'templates',
        'templates/requirements': base_dir / 'templates' / 'requirements',
        'templates/architecture': base_dir / 'templates' / 'architecture',
        'templates/trades': base_dir / 'templates' / 'trades',
        'memory': base_dir / 'memory',
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def create_project_context(memory_dir: Path, project_name: str):
    """Create the project context memory file."""
    content = f"""# Project Context

## Project Identity

| Field | Value |
|-------|-------|
| Project Name | {project_name} |
| Domain | [DOMAIN] |
| Created | {datetime.now().strftime('%Y-%m-%d')} |
| Status | ACTIVE |

## Stakeholders

| Role | Name | Concern | Contact |
|------|------|---------|---------|
| Project Lead | [NAME] | Overall delivery | [EMAIL] |
| Technical Lead | [NAME] | Architecture & implementation | [EMAIL] |
| Requirements Owner | [NAME] | Requirements quality | [EMAIL] |

## Lifecycle Gates

| Gate | Target Date | Status | Artifacts Required |
|------|-------------|--------|-------------------|
| SRR | [DATE] | PENDING | ConOps, StRS |
| PDR | [DATE] | PENDING | SRS, SDD (draft) |
| CDR | [DATE] | PENDING | SDD (final), ICD |
| TRR | [DATE] | PENDING | Test Plan, Procedures |

## Technical Context

| Aspect | Value |
|--------|-------|
| Primary Language | [LANGUAGE] |
| Framework | [FRAMEWORK] |
| Repository | [URL] |
| CI/CD | [PLATFORM] |

## Last Updated

{datetime.now().isoformat()}
"""
    (memory_dir / 'project-context.md').write_text(content)


def create_assumptions_log(memory_dir: Path):
    """Create the assumptions log memory file."""
    content = f"""# Assumptions Log

Track all assumptions made during the project lifecycle.

## Active Assumptions

| ID | Category | Assumption | Rationale | Validation Approach | Risk if Wrong | Status |
|----|----------|------------|-----------|---------------------|---------------|--------|
| A-001 | [CAT] | [ASSUMPTION] | [WHY] | [HOW TO VERIFY] | [IMPACT] | OPEN |

## Resolved Assumptions

| ID | Resolution | Resolution Date | Notes |
|----|------------|-----------------|-------|
| - | - | - | - |

## Categories

- **TECH**: Technical assumptions
- **SCOPE**: Scope/requirements assumptions
- **RESOURCE**: Resource/schedule assumptions
- **EXTERNAL**: External dependency assumptions

## Last Updated

{datetime.now().isoformat()}
"""
    (memory_dir / 'assumptions-log.md').write_text(content)


def create_requirements_status(memory_dir: Path):
    """Create the requirements status memory file."""
    content = f"""# Requirements Status

## Summary

| Metric | Value |
|--------|-------|
| Total Requirements | 0 |
| Baselined | 0 |
| In Review | 0 |
| Draft | 0 |

## Requirements by Category

| Category | Count | Baselined | Coverage |
|----------|-------|-----------|----------|
| Functional | 0 | 0 | 0% |
| Non-Functional | 0 | 0 | 0% |
| Interface | 0 | 0 | 0% |

## Recent Changes

| Date | Requirement | Change | Author |
|------|-------------|--------|--------|
| - | - | - | - |

## Next Actions

- [ ] Complete requirements elicitation
- [ ] Review with stakeholders
- [ ] Establish baseline

## Last Updated

{datetime.now().isoformat()}
"""
    (memory_dir / 'requirements-status.md').write_text(content)


def create_decisions_log(memory_dir: Path):
    """Create the decisions log memory file."""
    content = f"""# Decisions Log

Track all significant decisions made during the project.

## Active Decisions

| ID | Topic | Decision | Rationale | Date | Status |
|----|-------|----------|-----------|------|--------|
| D-001 | [TOPIC] | [DECISION] | [WHY] | [DATE] | APPROVED |

## Pending Decisions

| ID | Topic | Options | Target Date | Owner |
|----|-------|---------|-------------|-------|
| - | - | - | - | - |

## Decision Categories

- **ARCH**: Architecture decisions
- **TECH**: Technology selections
- **PROC**: Process decisions
- **SCOPE**: Scope decisions

## Last Updated

{datetime.now().isoformat()}
"""
    (memory_dir / 'decisions-log.md').write_text(content)


def create_sample_command(commands_dir: Path, category: str, name: str, description: str):
    """Create a sample command file."""
    content = f"""---
description: "{description}"
agent:
  model: sonnet
---

# {name.replace('.', ' ').title()}

## Purpose

[Describe the deliverable this command produces]

## Prerequisites

- [ ] [Required input 1]
- [ ] [Required input 2]

## Workflow

### Phase 1: Preparation

1. Verify prerequisites are met
2. Load required templates
3. Initialize output structure

### Phase 2: Execution

1. [Primary action 1]
2. [Primary action 2]
3. [Primary action 3]

### Phase 3: Validation

1. Verify output completeness
2. Run validation checks:

```bash
python scripts/python/validate-output.py <output-path> --json
```

3. Document any issues

## Outputs

- **Primary Output**: `[OUTPUT_PATH]`
- **Status Update**: `.claude/memory/[status-file].md`

## Completion Criteria

- [ ] All required sections completed
- [ ] Validation checks pass
- [ ] Status file updated

## Handoffs

### Proceed to Next Step

**Context**: [What was accomplished]
**Inputs Ready**: [What next command receives]

Use: `/[next-command]`
"""
    file_path = commands_dir / category / f"{name}.md"
    file_path.write_text(content)


def create_sample_template(templates_dir: Path, category: str, name: str):
    """Create a sample template file."""
    content = f"""# [DOCUMENT_TITLE]

## 1. Document Control

| Field | Value |
|-------|-------|
| Document ID | [DOC_ID] |
| Version | [VERSION] |
| Status | DRAFT |
| Author | [AUTHOR] |
| Date | [DATE] |

## 2. Purpose & Scope

**Purpose**: [Why this document exists]

**Scope**: [What it covers and doesn't cover]

**Audience**: [Who should read this]

## 3. Traceability

### 3.1 Parent Trace

| This Element | Traces To |
|--------------|-----------|
| [ELEMENT] | [PARENT_REF] |

### 3.2 Child Trace

| Child Element | Traces From |
|---------------|-------------|
| [CHILD_REF] | [THIS_ELEMENT] |

## 4. [Main Content]

[Template-specific content goes here]

## 5. Verification

| Element | Method | Evidence | Status |
|---------|--------|----------|--------|
| [ELEMENT] | [I/A/D/T] | [EVIDENCE] | OPEN |

## Appendices

### A. Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | [DATE] | [AUTHOR] | Initial draft |

### B. Open Items

| ID | Description | Owner | Due | Status |
|----|-------------|-------|-----|--------|
| [TBD_ID] | [DESCRIPTION] | [OWNER] | [DATE] | OPEN |

### C. Assumptions

| ID | Assumption | Rationale | Risk |
|----|------------|-----------|------|
| [A_ID] | [ASSUMPTION] | [WHY] | [IF WRONG] |

## Completeness Checklist

- [ ] All required sections completed
- [ ] Traceability established
- [ ] TBD items documented
- [ ] Reviewed by [ROLE]
"""
    file_path = templates_dir / category / f"{name}-template.md"
    file_path.write_text(content)


def create_sample_script(scripts_dir: Path, name: str, language: str = 'python'):
    """Create a sample utility script."""
    if language == 'python':
        content = f'''#!/usr/bin/env python3
"""
{name}.py - [Script description]

Usage: python {name}.py <input> [--json]

Inputs:
  - input: [Input description]
  - --json: Output as JSON

Outputs:
  - [Output description]

Exit Codes:
  - 0: Success
  - 1: Failure
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="[Description]")
    parser.add_argument("input", help="Input path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    try:
        # TODO: Implement logic
        result = {{"success": True, "data": {{}}}}
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Operation completed successfully")
        
        return 0
        
    except Exception as e:
        if args.json:
            print(json.dumps({{"success": False, "errors": [str(e)]}}))
        else:
            print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
        file_path = scripts_dir / 'python' / f"{name}.py"
    else:
        content = f'''#!/bin/bash
# {name}.sh - [Script description]
#
# Usage: ./{name}.sh <input>
#
# Exit Codes:
#   0: Success
#   1: Failure

set -e

INPUT="${{1:?Input required}}"

# TODO: Implement logic

echo "Operation completed successfully"
exit 0
'''
        file_path = scripts_dir / 'bash' / f"{name}.sh"
    
    file_path.write_text(content)


def generate_package(
    requirements_path: str,
    output_dir: str,
    project_name: str,
    include_examples: bool
) -> Dict:
    """Generate the complete SpecKit package."""
    base_dir = Path(output_dir)
    
    report = {
        "success": True,
        "output_dir": str(base_dir),
        "created_dirs": [],
        "created_files": [],
        "warnings": []
    }
    
    # Create directory structure
    dirs = create_directory_structure(base_dir)
    report["created_dirs"] = [str(d) for d in dirs.values()]
    
    # Create memory files
    memory_dir = dirs['memory']
    create_project_context(memory_dir, project_name)
    create_assumptions_log(memory_dir)
    create_requirements_status(memory_dir)
    create_decisions_log(memory_dir)
    report["created_files"].extend([
        str(memory_dir / 'project-context.md'),
        str(memory_dir / 'assumptions-log.md'),
        str(memory_dir / 'requirements-status.md'),
        str(memory_dir / 'decisions-log.md'),
    ])
    
    if include_examples:
        # Create sample commands
        commands = [
            ('requirements', 'requirements.capture', 'Capture and document requirements from stakeholder input'),
            ('requirements', 'requirements.trace', 'Build traceability matrix for requirements'),
            ('architecture', 'architecture.analyze', 'Analyze codebase to extract architecture insights'),
            ('trades', 'trades.initiate', 'Initiate a trade study with alternatives and criteria'),
        ]
        for category, name, desc in commands:
            create_sample_command(dirs['commands'], category, name, desc)
            report["created_files"].append(str(dirs['commands'] / category / f"{name}.md"))
        
        # Create sample templates
        templates = [
            ('requirements', 'srs'),
            ('requirements', 'traceability-matrix'),
            ('architecture', 'sdd'),
            ('trades', 'trade-study'),
        ]
        for category, name in templates:
            create_sample_template(dirs['templates'], category, name)
            report["created_files"].append(str(dirs['templates'] / category / f"{name}-template.md"))
        
        # Create sample scripts
        scripts = [
            ('validate-output', 'python'),
            ('check-coverage', 'bash'),
        ]
        for name, lang in scripts:
            create_sample_script(dirs['scripts'], name, lang)
            ext = 'py' if lang == 'python' else 'sh'
            report["created_files"].append(str(dirs['scripts'] / lang / f"{name}.{ext}"))
    
    # Create README
    readme_content = f"""# {project_name} - Claude Code Automation

Generated by SpecKit on {datetime.now().strftime('%Y-%m-%d')}

## Directory Structure

```
.claude/
├── commands/          # Claude Code /commands
│   ├── requirements/  # Requirements lifecycle
│   ├── architecture/  # Architecture lifecycle
│   ├── trades/        # Trade studies
│   ├── risk/          # Risk management
│   ├── test/          # Testing lifecycle
│   └── review/        # Reviews
├── scripts/           # Supporting scripts
│   ├── bash/
│   └── python/
├── templates/         # Document templates
└── memory/            # Persistent state
```

## Quick Start

1. Update `memory/project-context.md` with project details
2. Run `/requirements.capture` to begin elicitation
3. Follow command handoffs through the lifecycle

## Commands

| Command | Purpose |
|---------|---------|
| `/requirements.capture` | Capture stakeholder requirements |
| `/requirements.trace` | Build traceability matrix |
| `/architecture.analyze` | Analyze existing codebase |
| `/trades.initiate` | Start trade study |

## Validation

Run validation before delivery:

```bash
python scripts/python/validate-output.py .claude --json
```
"""
    (base_dir / 'README.md').write_text(readme_content)
    report["created_files"].append(str(base_dir / 'README.md'))
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate a complete SpecKit package"
    )
    parser.add_argument(
        "--requirements",
        required=True,
        help="Path to requirements document"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for generated package"
    )
    parser.add_argument(
        "--project-name",
        default="Project",
        help="Project name (default: Project)"
    )
    parser.add_argument(
        "--include-examples",
        action="store_true",
        help="Include example content"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        report = generate_package(
            args.requirements,
            args.output_dir,
            args.project_name,
            args.include_examples
        )
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"\n✅ SpecKit package generated successfully!")
            print(f"\nOutput directory: {report['output_dir']}")
            print(f"Directories created: {len(report['created_dirs'])}")
            print(f"Files created: {len(report['created_files'])}")
            if report['warnings']:
                print(f"\n⚠️ Warnings:")
                for warning in report['warnings']:
                    print(f"  - {warning}")
            print(f"\nNext steps:")
            print(f"  1. Update memory/project-context.md with project details")
            print(f"  2. Customize commands for your specific deliverables")
            print(f"  3. Run validation: python scripts/validate_speckit.py {args.output_dir}")
        
        return 0
        
    except Exception as e:
        if args.json:
            print(json.dumps({
                "success": False,
                "errors": [str(e)]
            }))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
