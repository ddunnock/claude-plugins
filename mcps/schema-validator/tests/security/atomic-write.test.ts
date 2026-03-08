import { test, expect, describe, beforeAll, afterAll } from "bun:test";
import { atomicWrite } from "../../src/security/atomic-write.ts";
import { mkdirSync, rmSync } from "node:fs";
import path from "node:path";

describe("atomicWrite", () => {
  const tmpDir = path.resolve("/tmp/sv-test-atomic-write");

  beforeAll(() => {
    mkdirSync(tmpDir, { recursive: true });
  });

  afterAll(() => {
    rmSync(tmpDir, { recursive: true, force: true });
  });

  test("write a file and read it back -- content matches", async () => {
    const filePath = path.join(tmpDir, "test.json");
    const content = JSON.stringify({ hello: "world" });

    await atomicWrite(filePath, content);

    const readBack = await Bun.file(filePath).text();
    expect(readBack).toBe(content);
  });

  test("write to nested directory that exists succeeds", async () => {
    const nested = path.join(tmpDir, "nested", "deep");
    mkdirSync(nested, { recursive: true });
    const filePath = path.join(nested, "data.yaml");
    const content = "key: value\n";

    await atomicWrite(filePath, content);

    const readBack = await Bun.file(filePath).text();
    expect(readBack).toBe(content);
  });

  test("overwrites existing file atomically", async () => {
    const filePath = path.join(tmpDir, "overwrite.json");
    await atomicWrite(filePath, "original");
    await atomicWrite(filePath, "updated");

    const readBack = await Bun.file(filePath).text();
    expect(readBack).toBe("updated");
  });
});
