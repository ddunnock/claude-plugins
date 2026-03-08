/**
 * Resource registrations for the schema-validator MCP server.
 * Exposes metadata about supported formats and registered schemas.
 */

import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

/**
 * Register all MCP resources on the server.
 */
export function registerResources(server: McpServer): void {
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

  // Registered schemas (empty until Phase 2 schema registry is built)
  server.resource(
    "registered-schemas",
    "schema-validator://schemas",
    async () => ({
      contents: [
        {
          uri: "schema-validator://schemas",
          mimeType: "application/json",
          text: JSON.stringify({
            schemas: [],
          }),
        },
      ],
    }),
  );
}
