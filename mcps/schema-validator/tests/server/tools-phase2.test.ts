/**
 * Phase 2 Plan 02 integration tests for file operation tools:
 * sv_read, sv_write, sv_validate, sv_patch
 *
 * These tests exercise the tool handlers directly by importing registerTools
 * and calling handlers through the MCP server's tool dispatch.
 */

import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { z } from "zod";
import { mkdtemp, rm, mkdir, writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { SchemaRegistry } from "../../src/schemas/registry.ts";
import { registerTools } from "../../src/server/tools.ts";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";

let tmpDir: string;
let registry: SchemaRegistry;
let client: Client;
let server: McpServer;

beforeAll(async () => {
  // Create temp directory for test files
  // Create tmpDir under cwd so validatePath (which defaults to [cwd]) allows access
  tmpDir = await mkdtemp(path.join(process.cwd(), ".tmp-phase2-"));

  // Setup registry with a test schema
  registry = new SchemaRegistry();
  registry.register(
    "test/config",
    z.object({
      name: z.string(),
      version: z.number(),
      tags: z.array(z.string()).optional(),
    }),
    "registered",
  );

  // Create MCP server with tools
  server = new McpServer({ name: "test-sv", version: "0.0.1" });
  registerTools(server, registry);

  // Connect via in-memory transport
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  client = new Client({ name: "test-client", version: "0.0.1" });
  await Promise.all([
    server.connect(serverTransport),
    client.connect(clientTransport),
  ]);
});

afterAll(async () => {
  await rm(tmpDir, { recursive: true, force: true });
});

/** Helper: call a tool and parse the JSON response */
async function callTool(name: string, args: Record<string, unknown>) {
  const result = await client.callTool({ name, arguments: args });
  const text = (result.content as Array<{ type: string; text: string }>)[0]?.text;
  return {
    data: JSON.parse(text || "{}"),
    isError: result.isError ?? false,
  };
}

// =============================================================================
// sv_read tests
// =============================================================================
describe("sv_read", () => {
  test("reads and validates a valid JSON file", async () => {
    const filePath = path.join(tmpDir, "valid.json");
    await writeFile(filePath, JSON.stringify({ name: "myapp", version: 1, tags: ["a"] }));

    const { data, isError } = await callTool("sv_read", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(false);
    expect(data.data).toEqual({ name: "myapp", version: 1, tags: ["a"] });
    expect(data.format).toBe("json");
    expect(data.filePath).toBe(filePath);
  });

  test("returns SCHEMA_NOT_FOUND for unknown schema", async () => {
    const filePath = path.join(tmpDir, "any.json");
    await writeFile(filePath, "{}");

    const { data, isError } = await callTool("sv_read", {
      filePath,
      schemaName: "nonexistent/schema",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("SCHEMA_NOT_FOUND");
  });

  test("returns FILE_NOT_FOUND for missing file", async () => {
    const filePath = path.join(tmpDir, "does-not-exist.json");

    const { data, isError } = await callTool("sv_read", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("FILE_NOT_FOUND");
  });

  test("returns VALIDATION_ERROR with Zod issues for invalid data", async () => {
    const filePath = path.join(tmpDir, "invalid.json");
    await writeFile(filePath, JSON.stringify({ name: 123, version: "bad" }));

    const { data, isError } = await callTool("sv_read", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("VALIDATION_ERROR");
    expect(Array.isArray(data.issues)).toBe(true);
    expect(data.issues.length).toBeGreaterThanOrEqual(2);
    // Each issue should have path, code, message
    const issue = data.issues[0];
    expect(issue).toHaveProperty("path");
    expect(issue).toHaveProperty("code");
    expect(issue).toHaveProperty("message");
  });

  test("returns error for path traversal", async () => {
    const { data, isError } = await callTool("sv_read", {
      filePath: "/etc/passwd",
      schemaName: "test/config",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("ERR_PATH_TRAVERSAL");
  });
});

// =============================================================================
// sv_write tests
// =============================================================================
describe("sv_write", () => {
  test("writes valid data to a JSON file", async () => {
    const filePath = path.join(tmpDir, "output.json");
    const inputData = { name: "written", version: 2 };

    const { data, isError } = await callTool("sv_write", {
      filePath,
      schemaName: "test/config",
      data: inputData,
    });

    expect(isError).toBe(false);
    expect(data.written).toBe(true);
    expect(data.filePath).toBe(filePath);
    expect(data.format).toBe("json");

    // Verify file was actually written
    const content = await readFile(filePath, "utf-8");
    const parsed = JSON.parse(content);
    expect(parsed.name).toBe("written");
    expect(parsed.version).toBe(2);
  });

  test("rejects invalid data before writing to disk", async () => {
    const filePath = path.join(tmpDir, "should-not-exist.json");

    const { data, isError } = await callTool("sv_write", {
      filePath,
      schemaName: "test/config",
      data: { name: 999, version: "wrong" },
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("VALIDATION_ERROR");

    // File should NOT have been created
    const exists = await Bun.file(filePath).exists();
    expect(exists).toBe(false);
  });

  test("creates parent directories if missing", async () => {
    const filePath = path.join(tmpDir, "nested", "deep", "config.json");

    const { data, isError } = await callTool("sv_write", {
      filePath,
      schemaName: "test/config",
      data: { name: "deep", version: 1 },
    });

    expect(isError).toBe(false);
    expect(data.written).toBe(true);

    // Verify the file exists in nested dir
    const content = await readFile(filePath, "utf-8");
    expect(JSON.parse(content).name).toBe("deep");
  });

  test("returns SCHEMA_NOT_FOUND for unknown schema", async () => {
    const filePath = path.join(tmpDir, "write-noschema.json");

    const { data, isError } = await callTool("sv_write", {
      filePath,
      schemaName: "nonexistent/schema",
      data: {},
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("SCHEMA_NOT_FOUND");
  });
});

// =============================================================================
// sv_validate tests
// =============================================================================
describe("sv_validate", () => {
  test("returns valid:true for a file matching schema", async () => {
    const filePath = path.join(tmpDir, "validate-valid.json");
    await writeFile(filePath, JSON.stringify({ name: "ok", version: 1 }));

    const { data, isError } = await callTool("sv_validate", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(false);
    expect(data.valid).toBe(true);
    // Should NOT include data on success (lightweight)
    expect(data.data).toBeUndefined();
  });

  test("returns valid:false with errors for invalid file", async () => {
    const filePath = path.join(tmpDir, "validate-invalid.json");
    await writeFile(filePath, JSON.stringify({ name: 42 }));

    const { data, isError } = await callTool("sv_validate", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(false);
    expect(data.valid).toBe(false);
    expect(Array.isArray(data.errors)).toBe(true);
    expect(data.errors.length).toBeGreaterThanOrEqual(1);
  });

  test("returns SCHEMA_NOT_FOUND for unknown schema", async () => {
    const filePath = path.join(tmpDir, "validate-noschema.json");
    await writeFile(filePath, "{}");

    const { data, isError } = await callTool("sv_validate", {
      filePath,
      schemaName: "nonexistent/schema",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("SCHEMA_NOT_FOUND");
  });

  test("returns FILE_NOT_FOUND for missing file", async () => {
    const filePath = path.join(tmpDir, "validate-missing.json");

    const { data, isError } = await callTool("sv_validate", {
      filePath,
      schemaName: "test/config",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("FILE_NOT_FOUND");
  });
});

// =============================================================================
// sv_patch tests
// =============================================================================
describe("sv_patch", () => {
  test("merges patch fields preserving existing data", async () => {
    const filePath = path.join(tmpDir, "patch-base.json");
    await writeFile(filePath, JSON.stringify({ name: "original", version: 1, tags: ["old"] }));

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "test/config",
      patch: { version: 2 },
    });

    expect(isError).toBe(false);
    expect(data.patched).toBe(true);
    expect(data.data.name).toBe("original"); // preserved
    expect(data.data.version).toBe(2); // updated
    expect(data.data.tags).toEqual(["old"]); // preserved
    expect(data.filePath).toBe(filePath);

    // Verify file on disk
    const content = await readFile(filePath, "utf-8");
    const onDisk = JSON.parse(content);
    expect(onDisk.version).toBe(2);
    expect(onDisk.name).toBe("original");
  });

  test("null values in patch delete fields (RFC 7386)", async () => {
    const filePath = path.join(tmpDir, "patch-delete.json");
    await writeFile(filePath, JSON.stringify({ name: "app", version: 1, tags: ["x"] }));

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "test/config",
      patch: { tags: null },
    });

    expect(isError).toBe(false);
    expect(data.patched).toBe(true);
    expect(data.data.tags).toBeUndefined(); // deleted
    expect(data.data.name).toBe("app"); // preserved
  });

  test("returns full merged result after patching", async () => {
    const filePath = path.join(tmpDir, "patch-full.json");
    await writeFile(filePath, JSON.stringify({ name: "base", version: 1 }));

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "test/config",
      patch: { version: 5, tags: ["new"] },
    });

    expect(isError).toBe(false);
    expect(data.data).toEqual({ name: "base", version: 5, tags: ["new"] });
  });

  test("returns VALIDATION_ERROR if merged result is invalid", async () => {
    const filePath = path.join(tmpDir, "patch-invalid.json");
    await writeFile(filePath, JSON.stringify({ name: "ok", version: 1 }));

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "test/config",
      patch: { name: null }, // deletes required field
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("VALIDATION_ERROR");
  });

  test("returns FILE_NOT_FOUND for missing file", async () => {
    const filePath = path.join(tmpDir, "patch-missing.json");

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "test/config",
      patch: { version: 2 },
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("FILE_NOT_FOUND");
  });

  test("returns SCHEMA_NOT_FOUND for unknown schema", async () => {
    const filePath = path.join(tmpDir, "patch-noschema.json");
    await writeFile(filePath, JSON.stringify({ name: "x", version: 1 }));

    const { data, isError } = await callTool("sv_patch", {
      filePath,
      schemaName: "nonexistent/schema",
      patch: {},
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("SCHEMA_NOT_FOUND");
  });
});
