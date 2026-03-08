/**
 * Resource registrations for the schema-validator MCP server.
 * Exposes metadata about supported formats and registered schemas.
 */

import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { SchemaRegistry } from "../schemas/registry.ts";

/**
 * Register all MCP resources on the server.
 */
export function registerResources(
  server: McpServer,
  registry: SchemaRegistry,
): void {
  // Supported formats and their file extensions
  server.resource(
    "supported-formats",
    "schema-validator://formats",
    async () => ({
      contents: [
        {
          uri: "schema-validator://formats",
          mimeType: "application/json",
          text: JSON.stringify({
            formats: ["json", "yaml", "xml", "toml"],
            extensions: {
              json: [".json"],
              yaml: [".yaml", ".yml"],
              xml: [".xml"],
              toml: [".toml"],
            },
          }),
        },
      ],
    }),
  );

  // Registered schemas -- live data from the registry
  server.resource(
    "registered-schemas",
    "schema-validator://schemas",
    async () => ({
      contents: [
        {
          uri: "schema-validator://schemas",
          mimeType: "application/json",
          text: JSON.stringify({
            schemas: registry.list(),
          }),
        },
      ],
    }),
  );
}
