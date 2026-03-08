import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { z } from "zod";
import path from "node:path";
import fs from "node:fs";
import { SchemaRegistry } from "../../src/schemas/registry.ts";
import { discoverSchemas } from "../../src/schemas/discovery.ts";

const FIXTURES_DIR = path.join(import.meta.dir, "__fixtures__");

describe("discoverSchemas", () => {
  beforeAll(() => {
    // Create fixture skill directories with schemas
    const skillDir = path.join(FIXTURES_DIR, "test-skill", "schemas");
    fs.mkdirSync(skillDir, { recursive: true });

    // Valid schema file exporting Zod schemas
    fs.writeFileSync(
      path.join(skillDir, "config.ts"),
      `import { z } from "zod";
export const pluginConfig = z.object({ name: z.string(), version: z.string() });
export const notASchema = "just a string";
`,
    );

    // Invalid file (will be skipped)
    const badSkillDir = path.join(FIXTURES_DIR, "bad-skill", "schemas");
    fs.mkdirSync(badSkillDir, { recursive: true });
    fs.writeFileSync(
      path.join(badSkillDir, "broken.ts"),
      `export const bad = {not a valid syntax
`,
    );
  });

  afterAll(() => {
    fs.rmSync(FIXTURES_DIR, { recursive: true, force: true });
  });

  test("discovers Zod schemas from skill paths", async () => {
    const registry = new SchemaRegistry();
    await discoverSchemas(
      [path.join(FIXTURES_DIR, "test-skill")],
      registry,
    );

    const found = registry.get("test-skill/pluginConfig");
    expect(found).toBeDefined();
    expect(found!.source).toBe("discovered");
    expect(found!.fieldCount).toBe(2);
  });

  test("skips non-Zod exports", async () => {
    const registry = new SchemaRegistry();
    await discoverSchemas(
      [path.join(FIXTURES_DIR, "test-skill")],
      registry,
    );

    // "notASchema" is a string, not a ZodType -- should not be registered
    expect(registry.get("test-skill/notASchema")).toBeUndefined();
  });

  test("skips invalid files with warning, does not throw", async () => {
    const registry = new SchemaRegistry();
    // Should not throw even though broken.ts has syntax errors
    await expect(
      discoverSchemas(
        [path.join(FIXTURES_DIR, "bad-skill")],
        registry,
      ),
    ).resolves.toBeUndefined();
  });

  test("handles nonexistent skill path gracefully", async () => {
    const registry = new SchemaRegistry();
    await expect(
      discoverSchemas(["/nonexistent/path"], registry),
    ).resolves.toBeUndefined();
  });
});
