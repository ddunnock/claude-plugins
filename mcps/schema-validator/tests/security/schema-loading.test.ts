import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import {
  validateSchemaFile,
  SchemaLoadError,
} from "../../src/security/schema-loader.ts";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";

describe("validateSchemaFile", () => {
  const tmpDir = path.resolve("/tmp/sv-test-schema-loader");

  beforeAll(() => {
    mkdirSync(tmpDir, { recursive: true });

    // Create valid test files
    writeFileSync(
      path.join(tmpDir, "valid.ts"),
      'export const schema = { type: "object" };\n',
    );
    writeFileSync(
      path.join(tmpDir, "valid.json"),
      '{ "type": "object" }\n',
    );
    writeFileSync(
      path.join(tmpDir, "valid.js"),
      'module.exports = { type: "object" };\n',
    );

    // Create binary file (with null bytes)
    const binaryBuf = Buffer.alloc(256);
    binaryBuf[0] = 0x89;
    binaryBuf[1] = 0x50;
    binaryBuf[10] = 0x00; // null byte
    writeFileSync(path.join(tmpDir, "binary.ts"), binaryBuf);

    // Create file with bad extension
    writeFileSync(path.join(tmpDir, "bad.exe"), "not a schema");

    // Create large file (over 1MB)
    const largeBuf = Buffer.alloc(1024 * 1024 + 1, "x");
    writeFileSync(path.join(tmpDir, "large.json"), largeBuf);
  });

  afterAll(() => {
    rmSync(tmpDir, { recursive: true, force: true });
  });

  test("valid .ts file passes validation", async () => {
    const result = await validateSchemaFile(path.join(tmpDir, "valid.ts"));
    expect(result.valid).toBe(true);
    expect(result.extension).toBe(".ts");
  });

  test("valid .json file passes validation", async () => {
    const result = await validateSchemaFile(path.join(tmpDir, "valid.json"));
    expect(result.valid).toBe(true);
    expect(result.extension).toBe(".json");
  });

  test("non-existent file throws FILE_NOT_FOUND", async () => {
    try {
      await validateSchemaFile(path.join(tmpDir, "nope.ts"));
      expect(true).toBe(false); // should not reach
    } catch (err) {
      expect(err).toBeInstanceOf(SchemaLoadError);
      expect((err as SchemaLoadError).code).toBe("FILE_NOT_FOUND");
    }
  });

  test("file with .exe extension throws INVALID_EXTENSION", async () => {
    try {
      await validateSchemaFile(path.join(tmpDir, "bad.exe"));
      expect(true).toBe(false);
    } catch (err) {
      expect(err).toBeInstanceOf(SchemaLoadError);
      expect((err as SchemaLoadError).code).toBe("INVALID_EXTENSION");
    }
  });

  test("file over 1MB throws FILE_TOO_LARGE", async () => {
    try {
      await validateSchemaFile(path.join(tmpDir, "large.json"));
      expect(true).toBe(false);
    } catch (err) {
      expect(err).toBeInstanceOf(SchemaLoadError);
      expect((err as SchemaLoadError).code).toBe("FILE_TOO_LARGE");
    }
  });

  test("file with binary content throws BINARY_FILE", async () => {
    try {
      await validateSchemaFile(path.join(tmpDir, "binary.ts"));
      expect(true).toBe(false);
    } catch (err) {
      expect(err).toBeInstanceOf(SchemaLoadError);
      expect((err as SchemaLoadError).code).toBe("BINARY_FILE");
    }
  });

  test("returns correct metadata (size, extension, filePath)", async () => {
    const fp = path.join(tmpDir, "valid.ts");
    const result = await validateSchemaFile(fp);
    expect(result.filePath).toBe(fp);
    expect(result.extension).toBe(".ts");
    expect(result.size).toBeGreaterThan(0);
  });
});
