# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-28

### Added

- **16 Skills** organized into 5 categories:
  - **Root Cause Analysis & Quality (8)**:
    - `rcca-master` - Master orchestrator for root cause analysis workflows
    - `problem-definition` - Structured problem definition using 5W2H framework
    - `five-whys-analysis` - Iterative root cause discovery
    - `fishbone-diagram` - Ishikawa cause-and-effect analysis
    - `pareto-analysis` - 80/20 prioritization of causes
    - `kepner-tregoe-analysis` - Systematic problem analysis and decision making
    - `fault-tree-analysis` - Top-down failure analysis with boolean logic
    - `fmea-analysis` - Failure Mode and Effects Analysis with RPN scoring
  - **Specification & Documentation (4)**:
    - `speckit-generator` - Generate specification documents from templates
    - `specification-refiner` - Refine and improve specifications
    - `documentation-architect` - Design documentation structure
    - `research-opportunity-investigator` - Identify research opportunities
  - **Decision Support (1)**:
    - `trade-study-analysis` - Multi-criteria decision analysis
  - **Output & Streaming (2)**:
    - `streaming-output` - Structured streaming output utilities
    - `streaming-output-mcp` - MCP-based streaming output
  - **Development (1)**:
    - `plugin-creator` - Create new Claude Code plugins

- **2 MCP Servers**:
  - `session-memory` - Persistent session memory with checkpoints and semantic search
  - `knowledge-mcp` - Semantic search over systems engineering standards (IEEE, INCOSE, ISO)

- Plugin packaging tools in `tools/`:
  - `init_plugin.py` - Initialize new plugins from templates
  - `package_plugins.py` - Package plugins for distribution
  - `create_toc.py` - Generate table of contents

- Comprehensive README documentation

[1.0.0]: https://github.com/dunnock/claude-plugins/releases/tag/v1.0.0
