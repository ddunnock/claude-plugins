/**
 * Phase 3 Plan 02 integration tests for sv_heal tool.
 *
 * Tests exercise the sv_heal tool handler through the MCP server's tool
 * dispatch, covering auto mode, suggest mode, already-valid files, error
 * cases, and unknown field preservation.
 */

import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { z } from "zod";
import { mkdtemp, rm, writeFile, readFile } from "node:fs/promises";
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
  // Create tmpDir under cwd so validatePath (which defaults to [cwd]) allows access
  tmpDir = await mkdtemp(path.join(process.cwd(), ".tmp-phase3-"));

  // Setup registry with a test schema that has defaults, enums, nested objects
  registry = new SchemaRegistry();
  registry.register(
    "test/heal",
    z.object({
      name: z.string(),
      version: z.number(),
      enabled: z.boolean().default(true),
      level: z.enum(["low", "medium", "high"]),
      meta: z
        .object({
          author: z.string(),
          priority: z.number().default(0),
        })
        .optional(),
    }),
    "registered",
  );

  // Create MCP server with tools
  server = new McpServer({ name: "test-sv-phase3", version: "0.0.1" });
  registerTools(server, registry);

  // Connect via in-memory transport
  const [clientTransport, serverTransport] =
    InMemoryTransport.createLinkedPair();
  client = new Client({ name: "test-client-phase3", version: "0.0.1" });
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
  const text = (result.content as Array<{ type: string; text: string }>)[0]
    ?.text;
  return {
    data: JSON.parse(text || "{}"),
    isError: result.isError ?? false,
  };
}

// =============================================================================
// sv_heal auto mode
// =============================================================================
describe("sv_heal auto mode", () => {
  test("fixes wrong types and missing defaults, writes healed file", async () => {
    const filePath = path.join(tmpDir, "auto-fixable.json");
    // version is string instead of number (coercible), enabled is missing (has default)
    await writeFile(
      filePath,
      JSON.stringify({ name: "app", version: "42", level: "high" }),
    );

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(false);
    expect(data.healed).toBe(true);
    expect(data.applied.length).toBeGreaterThanOrEqual(1);
    expect(data.data.version).toBe(42); // coerced string->number
    expect(data.data.enabled).toBe(true); // default applied
    expect(data.filePath).toBe(filePath);
    expect(data.format).toBe("json");

    // Verify file on disk is updated
    const onDisk = JSON.parse(await readFile(filePath, "utf-8"));
    expect(onDisk.version).toBe(42);
    expect(onDisk.enabled).toBe(true);
  });

  test("already valid file returns clean response, no disk write", async () => {
    const filePath = path.join(tmpDir, "auto-valid.json");
    const validData = {
      name: "ok",
      version: 1,
      enabled: true,
      level: "low",
    };
    await writeFile(filePath, JSON.stringify(validData));
    const originalContent = await readFile(filePath, "utf-8");

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(false);
    expect(data.healed).toBe(true);
    expect(data.applied).toEqual([]);
    expect(data.remaining).toEqual([]);

    // File on disk should be unchanged
    const afterContent = await readFile(filePath, "utf-8");
    expect(afterContent).toBe(originalContent);
  });

  test("partial heal: fixable + unfixable issues", async () => {
    const filePath = path.join(tmpDir, "auto-partial.json");
    // version coercible, but level has invalid enum value (manual)
    await writeFile(
      filePath,
      JSON.stringify({
        name: "app",
        version: "5",
        enabled: true,
        level: "extreme",
      }),
    );

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(false);
    expect(data.healed).toBe(false); // not fully healed
    expect(data.applied.length).toBeGreaterThanOrEqual(1); // version coerced
    expect(data.remaining.length).toBeGreaterThanOrEqual(1); // level still bad
    expect(data.data.version).toBe(5);

    // File should still be written with partial fixes
    const onDisk = JSON.parse(await readFile(filePath, "utf-8"));
    expect(onDisk.version).toBe(5);
  });

  test("unknown fields preserved end-to-end", async () => {
    const filePath = path.join(tmpDir, "auto-unknown.json");
    await writeFile(
      filePath,
      JSON.stringify({
        name: "app",
        version: "10",
        enabled: true,
        level: "medium",
        customField: "keep-me",
        nested_extra: { x: 1 },
      }),
    );

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(false);
    // Unknown fields must survive in the response data
    expect(data.data.customField).toBe("keep-me");
    expect(data.data.nested_extra).toEqual({ x: 1 });

    // And on disk
    const onDisk = JSON.parse(await readFile(filePath, "utf-8"));
    expect(onDisk.customField).toBe("keep-me");
    expect(onDisk.nested_extra).toEqual({ x: 1 });
  });
});

// =============================================================================
// sv_heal suggest mode
// =============================================================================
describe("sv_heal suggest mode", () => {
  test("returns suggestions without modifying file", async () => {
    const filePath = path.join(tmpDir, "suggest-fixable.json");
    await writeFile(
      filePath,
      JSON.stringify({ name: "app", version: "7", level: "high" }),
    );
    const originalContent = await readFile(filePath, "utf-8");

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "suggest",
    });

    expect(isError).toBe(false);
    expect(data.suggestions.length).toBeGreaterThanOrEqual(1);

    // File on disk must NOT be modified
    const afterContent = await readFile(filePath, "utf-8");
    expect(afterContent).toBe(originalContent);
  });

  test("already valid file returns empty suggestions", async () => {
    const filePath = path.join(tmpDir, "suggest-valid.json");
    await writeFile(
      filePath,
      JSON.stringify({
        name: "ok",
        version: 1,
        enabled: true,
        level: "low",
      }),
    );

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "suggest",
    });

    expect(isError).toBe(false);
    expect(data.suggestions).toEqual([]);
    expect(data.remaining).toEqual([]);
  });
});

// =============================================================================
// sv_heal error cases
// =============================================================================
describe("sv_heal error cases", () => {
  test("FILE_NOT_FOUND for missing file", async () => {
    const filePath = path.join(tmpDir, "does-not-exist.json");

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("FILE_NOT_FOUND");
  });

  test("SCHEMA_NOT_FOUND for unknown schema", async () => {
    const filePath = path.join(tmpDir, "error-noschema.json");
    await writeFile(filePath, JSON.stringify({ name: "x" }));

    const { data, isError } = await callTool("sv_heal", {
      filePath,
      schemaName: "nonexistent/schema",
      mode: "auto",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("SCHEMA_NOT_FOUND");
  });

  test("path traversal returns error", async () => {
    const { data, isError } = await callTool("sv_heal", {
      filePath: "/etc/passwd",
      schemaName: "test/heal",
      mode: "auto",
    });

    expect(isError).toBe(true);
    expect(data.error).toBe("ERR_PATH_TRAVERSAL");
  });
});
