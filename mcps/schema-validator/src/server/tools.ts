/**
 * Tool registrations for the schema-validator MCP server.
 * Phase 1 working tools: sv_parse_file, sv_detect_format
 * Phase 2+ stubs: sv_validate, sv_read, sv_write, sv_patch, sv_register_schema, sv_list_schemas, sv_heal
 */

import path from "node:path";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { getHandler, getSupportedExtensions } from "../formats/registry.ts";
import { FormatError } from "../formats/types.ts";
import {
  validatePath,
  PathValidationError,
} from "../security/path-validator.ts";

/** Stub response for tools not yet implemented. */
function notImplemented(phase: number, feature: string) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify({
          error: "NOT_IMPLEMENTED",
          message: `${feature} will be available in Phase ${phase}`,
        }),
      },
    ],
    isError: true as const,
  };
}

/**
 * Register all MCP tools on the server.
 * Phase 1 working tools use format handlers from Plan 02.
 * Phase 2+ tools return NOT_IMPLEMENTED errors.
 */
export function registerTools(server: McpServer): void {
  // --- Phase 1 working tools ---

  server.registerTool(
    "sv_parse_file",
    {
      description:
        "Parse a structured data file (JSON, YAML, XML, TOML) and return its contents as JSON",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to parse"),
        format: z
          .enum(["json", "yaml", "xml", "toml"])
          .optional()
          .describe(
            "Force a specific format (default: auto-detect from extension)",
          ),
      },
    },
    async (params) => {
      try {
        const { filePath, format } = params;

        // Validate path before any file I/O (SEC-01)
        const safePath = validatePath(filePath);

        // Read file content
        const file = Bun.file(safePath);
        const exists = await file.exists();
        if (!exists) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "FILE_NOT_FOUND",
                  message: `File not found: ${filePath}`,
                  filePath,
                }),
              },
            ],
            isError: true as const,
          };
        }
        const content = await file.text();

        // Determine handler: forced format or auto-detect from extension
        let handler;
        let detectedFormat: string;
        if (format) {
          const extMap: Record<string, string> = {
            json: ".json",
            yaml: ".yaml",
            xml: ".xml",
            toml: ".toml",
          };
          handler = getHandler(`file${extMap[format]}`);
          detectedFormat = format;
        } else {
          handler = getHandler(filePath);
          detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
          // Normalize yml -> yaml
          if (detectedFormat === "yml") detectedFormat = "yaml";
        }

        const data = handler.parse(content);

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({ data, format: detectedFormat, filePath }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof PathValidationError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
                  filePath: err.rejectedPath,
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof FormatError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
                  filePath: err.filePath || params.filePath,
                  line: err.line,
                  column: err.column,
                  suggestedFix: err.suggestedFix,
                }),
              },
            ],
            isError: true as const,
          };
        }
        const msg = err instanceof Error ? err.message : String(err);
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                error: "INTERNAL_ERROR",
                message: msg,
                filePath: params.filePath,
              }),
            },
          ],
          isError: true as const,
        };
      }
    },
  );

  server.registerTool(
    "sv_detect_format",
    {
      description:
        "Detect the format of a file based on its extension and return the detected format name",
      inputSchema: {
        filePath: z
          .string()
          .describe("Absolute path to the file to detect format for"),
      },
    },
    async (params) => {
      try {
        const { filePath } = params;

        // Validate path before any file I/O (SEC-01)
        validatePath(filePath);

        const handler = getHandler(filePath);
        let detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
        if (detectedFormat === "yml") detectedFormat = "yaml";

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                format: detectedFormat,
                extensions: handler.extensions,
                supportedFormats: getSupportedExtensions(),
              }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof PathValidationError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
                  filePath: err.rejectedPath,
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof FormatError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
                  filePath: params.filePath,
                  suggestedFix: err.suggestedFix,
                }),
              },
            ],
            isError: true as const,
          };
        }
        const msg = err instanceof Error ? err.message : String(err);
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                error: "INTERNAL_ERROR",
                message: msg,
              }),
            },
          ],
          isError: true as const,
        };
      }
    },
  );

  // --- Phase 2+ stub tools ---

  server.registerTool(
    "sv_validate",
    {
      description: "Validate a file against a registered schema",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to validate"),
        schemaName: z
          .string()
          .describe("Name of the registered schema to validate against"),
      },
    },
    async () => notImplemented(2, "Schema validation"),
  );

  server.registerTool(
    "sv_read",
    {
      description:
        "Read a structured file with schema validation and return typed data",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to read"),
        schemaName: z
          .string()
          .describe("Name of the registered schema for typed reading"),
      },
    },
    async () => notImplemented(2, "Schema-aware reading"),
  );

  server.registerTool(
    "sv_write",
    {
      description:
        "Write data to a structured file with schema validation and atomic writes",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to write"),
        schemaName: z
          .string()
          .describe("Name of the registered schema for validation"),
        data: z.unknown().describe("Data to write to the file"),
      },
    },
    async () => notImplemented(2, "Schema-validated writing"),
  );

  server.registerTool(
    "sv_patch",
    {
      description:
        "Patch specific fields in a structured file with schema validation",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to patch"),
        schemaName: z
          .string()
          .describe("Name of the registered schema for validation"),
        patch: z
          .record(z.unknown())
          .describe("Key-value pairs to merge into the file"),
      },
    },
    async () => notImplemented(2, "Schema-validated patching"),
  );

  server.registerTool(
    "sv_register_schema",
    {
      description: "Register a new schema for file validation",
      inputSchema: {
        name: z.string().describe("Unique name for the schema"),
        schema: z.unknown().describe("Schema definition (Zod-compatible)"),
      },
    },
    async () => notImplemented(2, "Schema registration"),
  );

  server.registerTool(
    "sv_list_schemas",
    {
      description: "List all registered schemas",
      inputSchema: {},
    },
    async () => notImplemented(2, "Schema listing"),
  );

  server.registerTool(
    "sv_heal",
    {
      description:
        "Attempt to fix a file that fails schema validation by auto-correcting or suggesting fixes",
      inputSchema: {
        filePath: z.string().describe("Absolute path to the file to heal"),
        schemaName: z
          .string()
          .describe("Name of the registered schema to heal against"),
        mode: z
          .enum(["auto", "suggest"])
          .describe(
            '"auto" applies fixes directly, "suggest" returns suggested changes',
          ),
      },
    },
    async () => notImplemented(3, "Self-healing"),
  );
}
