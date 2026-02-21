#!/usr/bin/env python3
"""
validate_speckit.py - Validate a SpecKit package

Usage: python validate_speckit.py <output-dir> [--level LEVEL] [--strict] [--json]

Validates all components of a SpecKit package:
- Commands: YAML frontmatter, structure, references
- Scripts: Syntax, JSON output support
- Templates: Structure, placeholders, principles
- State: Memory files, cross-references
- Grounding: Evidence markers, assumptions

Inputs:
  - output-dir: Path to the .claude directory to validate
  - --level: Validation level (syntax, structure, semantic, integration, all)
  - --strict: Fail on warnings
  - --check: Run specific check only
  - --json: Output results as JSON

Outputs:
  - Validation report with errors and warnings

Exit Codes:
  - 0: Validation passed
  - 1: Validation failed
  - 2: Input error
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.checks_passed: int = 0
        self.checks_failed: int = 0
    
    def add_error(self, message: str):
        self.errors.append(message)
        self.checks_failed += 1
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def add_info(self, message: str):
        self.info.append(message)
    
    def add_pass(self, message: str = None):
        self.checks_passed += 1
        if message:
            self.info.append(f"✓ {message}")
    
    def is_valid(self, strict: bool = False) -> bool:
        if strict:
            return len(self.errors) == 0 and len(self.warnings) == 0
        return len(self.errors) == 0
    
    def to_dict(self) -> dict:
        return {
            "success": self.is_valid(),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info
        }


def validate_yaml_frontmatter(content: str, file_path: str) -> Tuple[bool, Optional[dict], str]:
    """Validate YAML frontmatter in a markdown file."""
    if not content.startswith('---'):
        return False, None, f"{file_path}: Missing YAML frontmatter"
    
    # Find the closing ---
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return False, None, f"{file_path}: Unclosed YAML frontmatter"
    
    yaml_content = content[3:end_match.start() + 3]
    
    # Basic YAML parsing (simplified)
    frontmatter = {}
    for line in yaml_content.strip().split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"\'')
    
    return True, frontmatter, ""


def validate_commands(commands_dir: Path, result: ValidationResult):
    """Validate all command files."""
    if not commands_dir.exists():
        result.add_error(f"Commands directory not found: {commands_dir}")
        return
    
    command_files = list(commands_dir.rglob('*.md'))
    if not command_files:
        result.add_warning("No command files found")
        return
    
    for cmd_file in command_files:
        content = cmd_file.read_text()
        
        # C1: Valid YAML frontmatter
        valid, frontmatter, error = validate_yaml_frontmatter(content, str(cmd_file))
        if not valid:
            result.add_error(error)
            continue
        
        if not frontmatter.get('description'):
            result.add_error(f"{cmd_file}: Missing 'description' in frontmatter")
        else:
            result.add_pass(f"{cmd_file.name}: Valid frontmatter")
        
        # C2: Workflow structure
        required_sections = ['## Purpose', '## Workflow', '## Outputs']
        for section in required_sections:
            if section not in content:
                result.add_warning(f"{cmd_file}: Missing section '{section}'")
        
        # C3: Script references check
        script_refs = re.findall(r'(?:python|bash)\s+scripts?/([^\s]+)', content)
        for script_ref in script_refs:
            if '\\' in script_ref:
                result.add_error(f"{cmd_file}: Windows-style path in script reference: {script_ref}")
            if '--json' not in content:
                result.add_warning(f"{cmd_file}: Script references may not use --json flag")
        
        # C5: Handoff targets
        handoff_matches = re.findall(r'Use:\s+`/([^`]+)`', content)
        for handoff in handoff_matches:
            result.add_info(f"{cmd_file}: Handoff to /{handoff}")


def validate_scripts(scripts_dir: Path, result: ValidationResult):
    """Validate all script files."""
    if not scripts_dir.exists():
        result.add_warning(f"Scripts directory not found: {scripts_dir}")
        return
    
    # Python scripts
    py_files = list(scripts_dir.rglob('*.py'))
    for py_file in py_files:
        content = py_file.read_text()
        
        # S2: JSON output support
        if '--json' not in content and 'argparse' in content:
            result.add_warning(f"{py_file}: May not support --json flag")
        
        # S3: Error handling
        if 'try:' not in content:
            result.add_warning(f"{py_file}: No try/except error handling found")
        
        # S4: Documentation
        if '"""' not in content[:500]:
            result.add_warning(f"{py_file}: Missing docstring")
        else:
            result.add_pass(f"{py_file.name}: Has documentation")
    
    # Bash scripts
    sh_files = list(scripts_dir.rglob('*.sh'))
    for sh_file in sh_files:
        content = sh_file.read_text()
        
        if not content.startswith('#!/'):
            result.add_warning(f"{sh_file}: Missing shebang")


def validate_templates(templates_dir: Path, result: ValidationResult):
    """Validate all template files."""
    if not templates_dir.exists():
        result.add_warning(f"Templates directory not found: {templates_dir}")
        return
    
    template_files = list(templates_dir.rglob('*.md'))
    if not template_files:
        result.add_warning("No template files found")
        return
    
    for tmpl_file in template_files:
        content = tmpl_file.read_text()
        
        # T1: Required sections
        required_sections = ['## Document Control', '## Traceability']
        for section in required_sections:
            if section not in content:
                result.add_warning(f"{tmpl_file}: Missing section '{section}'")
        
        # T2: Placeholder consistency
        placeholders = re.findall(r'\[([A-Z_]+)\]', content)
        if placeholders:
            result.add_pass(f"{tmpl_file.name}: Uses [PLACEHOLDER] format")
        
        # Check for inconsistent placeholder formats
        other_formats = re.findall(r'{{[^}]+}}|<[A-Z_]+>', content)
        if other_formats:
            result.add_warning(f"{tmpl_file}: Inconsistent placeholder format: {other_formats[:3]}")


def validate_memory(memory_dir: Path, result: ValidationResult):
    """Validate memory/state files."""
    if not memory_dir.exists():
        result.add_warning(f"Memory directory not found: {memory_dir}")
        return
    
    # M1: Required files
    required_files = ['project-context.md', 'assumptions-log.md']
    for req_file in required_files:
        if not (memory_dir / req_file).exists():
            result.add_warning(f"Recommended memory file missing: {req_file}")
    
    memory_files = list(memory_dir.glob('*.md'))
    for mem_file in memory_files:
        content = mem_file.read_text()
        
        # M2: Structure compliance
        if '|' not in content:
            result.add_warning(f"{mem_file}: No tables found in memory file")
        else:
            result.add_pass(f"{mem_file.name}: Has table structure")


def validate_grounding(base_dir: Path, result: ValidationResult):
    """Validate evidence markers and assumptions."""
    all_md_files = list(base_dir.rglob('*.md'))
    
    evidence_markers = ['[VERIFIED:', '[DERIVED:', '[ASSUMPTION:', '[TBD]']
    files_with_markers = 0
    total_assumptions = 0
    
    for md_file in all_md_files:
        content = md_file.read_text()
        
        has_marker = False
        for marker in evidence_markers:
            if marker in content:
                has_marker = True
                if marker == '[ASSUMPTION:':
                    total_assumptions += content.count(marker)
        
        if has_marker:
            files_with_markers += 1
    
    if files_with_markers == 0:
        result.add_warning("No evidence markers found in any file")
    else:
        result.add_info(f"Evidence markers found in {files_with_markers} files")
        result.add_info(f"Total assumptions logged: {total_assumptions}")
    
    # Check assumptions log
    assumptions_log = base_dir / 'memory' / 'assumptions-log.md'
    if assumptions_log.exists():
        content = assumptions_log.read_text()
        logged = content.count('| A-')
        if total_assumptions > logged:
            result.add_warning(
                f"Assumptions in files ({total_assumptions}) exceed logged ({logged})"
            )


def validate_package(base_dir: Path, level: str, strict: bool) -> ValidationResult:
    """Run all validation checks on a SpecKit package."""
    result = ValidationResult()
    
    # Verify base directory exists
    if not base_dir.exists():
        result.add_error(f"Directory not found: {base_dir}")
        return result
    
    # Determine subdirectories
    commands_dir = base_dir / 'commands'
    scripts_dir = base_dir / 'scripts'
    templates_dir = base_dir / 'templates'
    memory_dir = base_dir / 'memory'
    
    # Run validation based on level
    if level in ['syntax', 'all']:
        validate_commands(commands_dir, result)
        validate_scripts(scripts_dir, result)
    
    if level in ['structure', 'all']:
        validate_templates(templates_dir, result)
        validate_memory(memory_dir, result)
    
    if level in ['semantic', 'all']:
        validate_grounding(base_dir, result)
    
    if level in ['integration', 'all']:
        # Basic integration check - verify cross-references
        result.add_info("Integration validation: Check handoff targets manually")
    
    return result



def _validate_path(filepath: str, allowed_extensions: set, label: str) -> str:
    """Validate file path: reject traversal and restrict extensions. Returns resolved path."""
    resolved = os.path.realpath(filepath)
    if ".." in os.path.relpath(resolved):
        print(f"Error: Path traversal not allowed in {label}: {filepath}")
        sys.exit(1)
    ext = os.path.splitext(resolved)[1].lower()
    if ext not in allowed_extensions:
        print(f"Error: {label} must be one of {allowed_extensions}, got \'{ext}\'")
        sys.exit(1)
    return resolved


def main():
    parser = argparse.ArgumentParser(
        description="Validate a SpecKit package"
    )
    parser.add_argument(
        "output_dir",
        help="Path to the .claude directory to validate"
    )
    parser.add_argument(
        "--level",
        choices=["syntax", "structure", "semantic", "integration", "all"],
        default="all",
        help="Validation level (default: all)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings"
    )
    parser.add_argument(
        "--check",
        help="Run specific check only"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()

    if args.output_dir:
        args.output_dir = os.path.realpath(args.output_dir)
    
    try:
        base_dir = Path(args.output_dir)
        result = validate_package(base_dir, args.level, args.strict)
        
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print("\n" + "="*60)
            print("SpecKit Validation Report")
            print("="*60)
            print(f"\nDirectory: {base_dir}")
            print(f"Level: {args.level}")
            print(f"\nChecks Passed: {result.checks_passed}")
            print(f"Checks Failed: {result.checks_failed}")
            
            if result.errors:
                print(f"\n❌ ERRORS ({len(result.errors)}):")
                for error in result.errors:
                    print(f"  - {error}")
            
            if result.warnings:
                print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
                for warning in result.warnings:
                    print(f"  - {warning}")
            
            if result.info:
                print(f"\nℹ️  INFO:")
                for info in result.info:
                    print(f"  - {info}")
            
            print("\n" + "="*60)
            if result.is_valid(args.strict):
                print("✅ VALIDATION PASSED")
            else:
                print("❌ VALIDATION FAILED")
            print("="*60 + "\n")
        
        return 0 if result.is_valid(args.strict) else 1
        
    except Exception as e:
        if args.json:
            print(json.dumps({
                "success": False,
                "errors": [str(e)]
            }))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
