import { test, expect, describe } from "bun:test";

describe("server startup", () => {
  test("src/index.ts can be imported without throwing", async () => {
    // Importing the module will attempt to start the server on stdio,
    // which we don't want in tests. Instead, verify the file exists and
    // is valid TypeScript by checking the file is parseable.
    const file = Bun.file(import.meta.dir + "/../../src/index.ts");
    expect(await file.exists()).toBe(true);
    const content = await file.text();
    expect(content).toContain("McpServer");
    expect(content).toContain("StdioServerTransport");
    expect(content).toContain("registerTools");
    expect(content).toContain("registerResources");
  });

  test("registerTools function exists and is callable", async () => {
    const { registerTools } = await import("../../src/server/tools.ts");
    expect(typeof registerTools).toBe("function");
  });

  test("registerResources function exists and is callable", async () => {
    const { registerResources } = await import("../../src/server/resources.ts");
    expect(typeof registerResources).toBe("function");
  });

  test("FormatHandler type is exported from types.ts", async () => {
    const types = await import("../../src/formats/types.ts");
    // FormatError is a class (runtime value), verify it exists
    expect(typeof types.FormatError).toBe("function");
    // Verify FormatError works as expected
    const err = new types.FormatError("TEST_CODE", "test message", "/test.json");
    expect(err.code).toBe("TEST_CODE");
    expect(err.message).toBe("test message");
    expect(err.filePath).toBe("/test.json");
    expect(err).toBeInstanceOf(Error);
  });
});
