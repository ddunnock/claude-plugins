# MCPs — Claude Code MCP Servers

## Monorepo Structure
- Git is tracked at the repo root (`~/projects/claude-plugins`). **Never run `git init` in this subdirectory.**
- All git commands (commit, push, branch) operate from the repo root.
- This directory (`mcps/`) is a workspace within the monorepo.

## GSD / Planning
- `.planning/` lives HERE (`mcps/.planning/`), not at the repo root.
- GSD workflows scope to this subdirectory's concerns.

## Project Purpose
- Development and deployment of MCP servers (Model Context Protocol) for use with Claude Code.

## Required Skills
- **MCP-Builder** (`mcp-builder`): Use for all MCP server development workflows — scaffolding, tool definitions, transport setup.
- **Zod** (`zod`): Use when building schema validators or input validation for MCP tool parameters.
