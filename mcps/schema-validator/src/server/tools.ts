/**
 * Tool registrations for the schema-validator MCP server.
 * Phase 1 working tools: sv_parse_file, sv_detect_format
 * Phase 2 working tools: sv_register_schema, sv_list_schemas, sv_read, sv_write, sv_validate, sv_patch
 * Phase 3 working tools: sv_heal
 */

import path from "node:path";
import { mkdir } from "node:fs/promises";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z, ZodError } from "zod";
import { getHandler, getSupportedExtensions } from "../formats/registry.ts";
import { FormatError } from "../formats/types.ts";
import {
  validatePath,
  PathValidationError,
} from "../security/path-validator.ts";
import { atomicWrite } from "../security/atomic-write.ts";
import { jsonMergePatch } from "../schemas/merge-patch.ts";
import { healData } from "../schemas/healer.ts";
import type { SchemaRegistry } from "../schemas/registry.ts";
import { SchemaRegistryError } from "../schemas/types.ts";

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
export function registerTools(server: McpServer, registry: SchemaRegistry): void {
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

  // --- Phase 2 file operation tools ---

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
    async (params) => {
      try {
        const { filePath, schemaName } = params;
        const safePath = validatePath(filePath);

        // Check file exists
        const file = Bun.file(safePath);
        if (!(await file.exists())) {
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

        // Read and parse
        const content = await file.text();
        const handler = getHandler(filePath);
        const data = handler.parse(content);

        // Get schema
        const entry = registry.get(schemaName);
        if (!entry) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "SCHEMA_NOT_FOUND",
                  message: `Schema '${schemaName}' not found in registry`,
                }),
              },
            ],
            isError: true as const,
          };
        }

        // Validate with safeParse (no throw)
        const result = entry.zodSchema.safeParse(data);
        if (result.success) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({ valid: true }),
              },
            ],
          };
        }

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                valid: false,
                errors: result.error.issues,
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
                  filePath: err.filePath || params.filePath,
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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
    async (params) => {
      try {
        const { filePath, schemaName } = params;
        const safePath = validatePath(filePath);

        // Check file exists
        const file = Bun.file(safePath);
        if (!(await file.exists())) {
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

        // Read and parse with format handler
        const content = await file.text();
        const handler = getHandler(filePath);
        let detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
        if (detectedFormat === "yml") detectedFormat = "yaml";
        const data = handler.parse(content);

        // Get schema
        const entry = registry.get(schemaName);
        if (!entry) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "SCHEMA_NOT_FOUND",
                  message: `Schema '${schemaName}' not found in registry`,
                }),
              },
            ],
            isError: true as const,
          };
        }

        // Validate with parse (throws on failure)
        const validated = entry.zodSchema.parse(data);

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                data: validated,
                format: detectedFormat,
                filePath: safePath,
              }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof ZodError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "VALIDATION_ERROR",
                  message: "Data does not match schema",
                  issues: err.issues,
                }),
              },
            ],
            isError: true as const,
          };
        }
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
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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
    async (params) => {
      try {
        const { filePath, schemaName, data } = params;
        const safePath = validatePath(filePath);

        // Get schema first (fail fast before any disk I/O)
        const entry = registry.get(schemaName);
        if (!entry) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "SCHEMA_NOT_FOUND",
                  message: `Schema '${schemaName}' not found in registry`,
                }),
              },
            ],
            isError: true as const,
          };
        }

        // Validate data BEFORE writing (reject invalid data before disk)
        const validated = entry.zodSchema.parse(data);

        // Serialize with format handler
        const handler = getHandler(filePath);
        let detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
        if (detectedFormat === "yml") detectedFormat = "yaml";
        const serialized = handler.serialize(validated);

        // Create parent directories if missing
        await mkdir(path.dirname(safePath), { recursive: true });

        // Atomic write
        await atomicWrite(safePath, serialized);

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                written: true,
                filePath: safePath,
                format: detectedFormat,
              }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof ZodError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "VALIDATION_ERROR",
                  message: "Data does not match schema",
                  issues: err.issues,
                }),
              },
            ],
            isError: true as const,
          };
        }
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
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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
          .describe("Key-value pairs to merge into the file (null deletes fields per RFC 7386)"),
      },
    },
    async (params) => {
      try {
        const { filePath, schemaName, patch } = params;
        const safePath = validatePath(filePath);

        // Check file exists
        const file = Bun.file(safePath);
        if (!(await file.exists())) {
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

        // Read and parse existing file
        const content = await file.text();
        const handler = getHandler(filePath);
        let detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
        if (detectedFormat === "yml") detectedFormat = "yaml";
        const existingData = handler.parse(content);

        // Get schema
        const entry = registry.get(schemaName);
        if (!entry) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "SCHEMA_NOT_FOUND",
                  message: `Schema '${schemaName}' not found in registry`,
                }),
              },
            ],
            isError: true as const,
          };
        }

        // Merge with RFC 7386 semantics
        const merged = jsonMergePatch(existingData, patch);

        // Validate merged result
        const validated = entry.zodSchema.parse(merged);

        // Serialize and write atomically
        const serialized = handler.serialize(validated);
        await atomicWrite(safePath, serialized);

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                patched: true,
                data: validated,
                filePath: safePath,
                format: detectedFormat,
              }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof ZodError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "VALIDATION_ERROR",
                  message: "Merged data does not match schema",
                  issues: err.issues,
                }),
              },
            ],
            isError: true as const,
          };
        }
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
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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
    "sv_register_schema",
    {
      description:
        "Register a new schema for file validation. Accepts JSON Schema format.",
      inputSchema: {
        name: z.string().describe("Unique namespaced name for the schema (e.g. 'skill/config')"),
        schema: z.record(z.unknown()).describe("JSON Schema object defining the schema"),
        extends: z
          .string()
          .optional()
          .describe("Optional parent schema name to extend"),
      },
    },
    async (params) => {
      try {
        const { name, schema } = params;
        const extendsName = params.extends;
        registry.registerFromJsonSchema(
          name,
          schema as Record<string, unknown>,
          extendsName,
        );
        const registered = registry.get(name);
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                registered: true,
                name,
                fieldCount: registered?.fieldCount ?? 0,
              }),
            },
          ],
        };
      } catch (err) {
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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

  server.registerTool(
    "sv_list_schemas",
    {
      description: "List all registered schemas with metadata",
      inputSchema: {},
    },
    async () => {
      const schemas = registry.list();
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({ schemas }),
          },
        ],
      };
    },
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
    async (params) => {
      try {
        const { filePath, schemaName, mode } = params;
        const safePath = validatePath(filePath);

        // Check file exists
        const file = Bun.file(safePath);
        if (!(await file.exists())) {
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

        // Read and parse
        const content = await file.text();
        const handler = getHandler(filePath);
        let detectedFormat = path.extname(filePath).replace(".", "").toLowerCase();
        if (detectedFormat === "yml") detectedFormat = "yaml";
        const data = handler.parse(content);

        // Get schema
        const entry = registry.get(schemaName);
        if (!entry) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: "SCHEMA_NOT_FOUND",
                  message: `Schema '${schemaName}' not found in registry`,
                }),
              },
            ],
            isError: true as const,
          };
        }

        // Run healing engine
        const result = healData(data as Record<string, unknown>, entry.zodSchema);

        if (mode === "auto") {
          // Write to disk only if there are applied fixes
          if (result.applied.length > 0) {
            const serialized = handler.serialize(result.data);
            await atomicWrite(safePath, serialized);
          }

          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  healed: result.healed,
                  data: result.data,
                  applied: result.applied,
                  remaining: result.remaining,
                  filePath: safePath,
                  format: detectedFormat,
                }),
              },
            ],
          };
        }

        // mode === "suggest"
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify({
                suggestions: result.applied,
                remaining: result.remaining,
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
                  filePath: err.filePath || params.filePath,
                }),
              },
            ],
            isError: true as const,
          };
        }
        if (err instanceof SchemaRegistryError) {
          return {
            content: [
              {
                type: "text" as const,
                text: JSON.stringify({
                  error: err.code,
                  message: err.message,
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
}
