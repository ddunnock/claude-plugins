/**
 * Schema Validator MCP Server entry point.
 * Connects the MCP server to stdio transport for Claude Code integration.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { registerTools } from "./server/tools.ts";
import { registerResources } from "./server/resources.ts";

async function main() {
  const server = new McpServer({
    name: "schema-validator",
    version: "0.1.0",
  });

  registerTools(server);
  registerResources(server);

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Schema Validator MCP running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
