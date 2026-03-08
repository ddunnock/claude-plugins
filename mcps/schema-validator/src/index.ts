/**
 * Schema Validator MCP Server entry point.
 * Connects the MCP server to stdio transport for Claude Code integration.
 * Initializes schema registry with discovery from configured skill paths.
 */

import path from "node:path";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerTools } from "./server/tools.ts";
import { registerResources } from "./server/resources.ts";
import { SchemaRegistry } from "./schemas/registry.ts";
import type { SchemaRegistryConfig } from "./schemas/types.ts";

async function main() {
  const server = new McpServer({
    name: "schema-validator",
    version: "0.2.0",
  });

  // Initialize schema registry
  const registry = new SchemaRegistry();

  // Load config from schema-validator.config.json (gracefully handle missing)
  let config: SchemaRegistryConfig = { skillPaths: [] };
  try {
    const configPath = path.resolve("schema-validator.config.json");
    const configFile = Bun.file(configPath);
    if (await configFile.exists()) {
      const raw = await configFile.json();
      config = { skillPaths: raw.skillPaths ?? [] };
    }
  } catch (err) {
    console.error(
      `[schema-validator] Failed to load config: ${err instanceof Error ? err.message : err}`,
    );
  }

  // Discover schemas from configured skill paths
  await registry.discover(config);

  registerTools(server, registry);
  registerResources(server, registry);

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Schema Validator MCP running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
