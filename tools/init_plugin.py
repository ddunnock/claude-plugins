#!/usr/bin/env python3
"""
Plugin Initializer - Creates a new skill or MCP from template

Usage:
    init_plugin.py skill <plugin-name> --path <path>
    init_plugin.py mcp <plugin-name> --path <path>

Examples:
    init_plugin.py skill my-new-skill --path skills
    init_plugin.py mcp my-new-mcp --path mcps
"""

import sys
from pathlib import Path

# =============================================================================
# Skill Templates
# =============================================================================

SKILL_TEMPLATE = """---
name: {plugin_name}
description: [TODO: Complete and informative explanation of what the skill does and when to use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]
---

# {plugin_title}

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Workflow

[TODO: Define the main workflow or capabilities]

## Resources

This skill includes example resource directories:

### scripts/
Executable code (Python/Bash/etc.) for automation tasks.

### references/
Documentation and reference material to be loaded into context as needed.

### assets/
Files used in output (templates, icons, fonts, etc.) - not loaded into context.

**Delete any unneeded directories.**
"""

SKILL_EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {plugin_name}

Replace with actual implementation or delete if not needed.
"""

def main():
    print("This is an example script for {plugin_name}")

if __name__ == "__main__":
    main()
'''

SKILL_EXAMPLE_REFERENCE = """# Reference Documentation for {plugin_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

## When Reference Docs Are Useful

- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
"""

# =============================================================================
# MCP Templates
# =============================================================================

MCP_TEMPLATE = """---
name: {plugin_name}
description: [TODO: Description of what this MCP server provides and when to use it.]
type: mcp
entry_point: server.py
dependencies:
  - mcp
---

# {plugin_title}

## Overview

[TODO: 1-2 sentences explaining what this MCP server provides]

## Installation

After packaging, install to ~/.claude/ using:

```bash
python tools/install_mcp.py dist/{plugin_name}.plugin
```

Then add to Claude Desktop config:

```json
{{
  "mcpServers": {{
    "{plugin_name}": {{
      "command": "python3",
      "args": ["~/.claude/{plugin_name}/server.py"]
    }}
  }}
}}
```

## Tools Provided

[TODO: List the MCP tools this server provides]

| Tool | Purpose |
|------|---------|
| `tool_name` | Description |

## Configuration

[TODO: Document configuration options if any]
"""

MCP_SERVER_TEMPLATE = '''#!/usr/bin/env python3
"""
{plugin_title} MCP Server

[TODO: Description of what this MCP server does]
"""

import asyncio
import json
from typing import Any

# Check for MCP SDK availability
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: MCP SDK not installed. Run: pip install mcp")


class {class_name}Server:
    """Main server implementation."""

    def __init__(self):
        self.initialized = False

    def initialize(self) -> dict:
        """Initialize the server."""
        self.initialized = True
        return {{"status": "initialized"}}

    def example_tool(self, param: str) -> dict:
        """Example tool implementation."""
        return {{"result": f"Processed: {{param}}"}}


def create_mcp_server(server_impl: {class_name}Server):
    """Create MCP server with tools."""
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")

    mcp_server = Server("{plugin_name}")

    @mcp_server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="example_tool",
                description="Example tool - replace with actual implementation",
                inputSchema={{
                    "type": "object",
                    "properties": {{
                        "param": {{
                            "type": "string",
                            "description": "Example parameter"
                        }}
                    }},
                    "required": ["param"]
                }}
            )
        ]

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "example_tool":
            result = server_impl.example_tool(arguments.get("param", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        else:
            raise ValueError(f"Unknown tool: {{name}}")

    return mcp_server


async def run_server():
    """Run the MCP server."""
    server_impl = {class_name}Server()
    mcp_server = create_mcp_server(server_impl)

    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


def main():
    if not HAS_MCP:
        print("Error: MCP SDK not installed. Run: pip install mcp")
        return

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
'''

MCP_CONFIG_TEMPLATE = """{
  "example_setting": "value"
}
"""


def title_case_name(name: str) -> str:
    """Convert hyphenated name to Title Case for display."""
    return " ".join(word.capitalize() for word in name.split("-"))


def class_case_name(name: str) -> str:
    """Convert hyphenated name to PascalCase for class names."""
    return "".join(word.capitalize() for word in name.split("-"))


def init_skill(plugin_name: str, path: str) -> Path | None:
    """Initialize a new skill plugin."""
    plugin_dir = Path(path).resolve() / plugin_name

    if plugin_dir.exists():
        print(f"Error: Directory already exists: {plugin_dir}")
        return None

    try:
        plugin_dir.mkdir(parents=True)
        print(f"Created skill directory: {plugin_dir}")

        plugin_title = title_case_name(plugin_name)

        # Create SKILL.md
        skill_md = plugin_dir / "SKILL.md"
        skill_md.write_text(SKILL_TEMPLATE.format(
            plugin_name=plugin_name,
            plugin_title=plugin_title
        ))
        print("Created SKILL.md")

        # Create scripts/
        scripts_dir = plugin_dir / "scripts"
        scripts_dir.mkdir()
        example_script = scripts_dir / "example.py"
        example_script.write_text(SKILL_EXAMPLE_SCRIPT.format(plugin_name=plugin_name))
        example_script.chmod(0o755)
        print("Created scripts/example.py")

        # Create references/
        references_dir = plugin_dir / "references"
        references_dir.mkdir()
        example_ref = references_dir / "reference.md"
        example_ref.write_text(SKILL_EXAMPLE_REFERENCE.format(plugin_title=plugin_title))
        print("Created references/reference.md")

        # Create assets/
        assets_dir = plugin_dir / "assets"
        assets_dir.mkdir()
        print("Created assets/")

        print(f"\nSkill '{plugin_name}' initialized at {plugin_dir}")
        print("\nNext steps:")
        print("1. Edit SKILL.md to complete the TODO items")
        print("2. Customize or delete example files")
        print("3. Run: python tools/validate_plugin.py", plugin_dir)

        return plugin_dir

    except Exception as e:
        print(f"Error creating skill: {e}")
        return None


def init_mcp(plugin_name: str, path: str) -> Path | None:
    """Initialize a new MCP plugin."""
    plugin_dir = Path(path).resolve() / plugin_name

    if plugin_dir.exists():
        print(f"Error: Directory already exists: {plugin_dir}")
        return None

    try:
        plugin_dir.mkdir(parents=True)
        print(f"Created MCP directory: {plugin_dir}")

        plugin_title = title_case_name(plugin_name)
        class_name = class_case_name(plugin_name)

        # Create MCP.md
        mcp_md = plugin_dir / "MCP.md"
        mcp_md.write_text(MCP_TEMPLATE.format(
            plugin_name=plugin_name,
            plugin_title=plugin_title
        ))
        print("Created MCP.md")

        # Create server.py
        server_py = plugin_dir / "server.py"
        server_py.write_text(MCP_SERVER_TEMPLATE.format(
            plugin_name=plugin_name,
            plugin_title=plugin_title,
            class_name=class_name
        ))
        print("Created server.py")

        # Create config.json
        config_json = plugin_dir / "config.json"
        config_json.write_text(MCP_CONFIG_TEMPLATE)
        print("Created config.json")

        print(f"\nMCP '{plugin_name}' initialized at {plugin_dir}")
        print("\nNext steps:")
        print("1. Edit MCP.md to complete the TODO items")
        print("2. Implement your tools in server.py")
        print("3. Install MCP SDK: pip install mcp")
        print("4. Run: python tools/validate_plugin.py", plugin_dir)

        return plugin_dir

    except Exception as e:
        print(f"Error creating MCP: {e}")
        return None


def main():
    if len(sys.argv) < 5 or sys.argv[3] != "--path":
        print("Usage: init_plugin.py <type> <plugin-name> --path <path>")
        print("\nTypes:")
        print("  skill    Create a new skill plugin (SKILL.md)")
        print("  mcp      Create a new MCP server plugin (MCP.md + server.py)")
        print("\nExamples:")
        print("  init_plugin.py skill my-new-skill --path skills")
        print("  init_plugin.py mcp my-new-mcp --path mcps")
        sys.exit(1)

    plugin_type = sys.argv[1].lower()
    plugin_name = sys.argv[2]
    path = sys.argv[4]

    print(f"Initializing {plugin_type}: {plugin_name}")
    print(f"Location: {path}")
    print()

    if plugin_type == "skill":
        result = init_skill(plugin_name, path)
    elif plugin_type == "mcp":
        result = init_mcp(plugin_name, path)
    else:
        print(f"Error: Unknown plugin type '{plugin_type}'. Use 'skill' or 'mcp'.")
        sys.exit(1)

    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
