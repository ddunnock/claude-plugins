import { test, expect, describe } from "bun:test";
import { yamlHandler } from "../../src/formats/yaml.ts";
import { FormatError } from "../../src/formats/types.ts";

describe("yamlHandler", () => {
  test("has correct extensions", () => {
    expect(yamlHandler.extensions).toEqual([".yaml", ".yml"]);
  });

  test("parses simple mapping", () => {
    expect(yamlHandler.parse("a: 1")).toEqual({ a: 1 });
  });

  test("serializes simple object", () => {
    const result = yamlHandler.serialize({ a: 1 });
    expect(result).toContain("a:");
  });

  test("round-trips nested structures", () => {
    const data = {
      name: "test",
      nested: { deep: { value: 42 } },
      array: [1, "two", 3],
    };
    const roundTripped = yamlHandler.parse(yamlHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("handles multi-line strings", () => {
    const yaml = `description: |\n  This is a\n  multi-line string\n`;
    const parsed = yamlHandler.parse(yaml) as { description: string };
    expect(parsed.description).toContain("multi-line");
  });

  test("throws FormatError on malformed input", () => {
    expect(() => yamlHandler.parse(":\n  :\n    - :\n  bad: [")).toThrow(FormatError);
  });

  test("FormatError has descriptive message", () => {
    try {
      yamlHandler.parse("bad: [unterminated");
      expect(true).toBe(false);
    } catch (e) {
      expect(e).toBeInstanceOf(FormatError);
      expect((e as FormatError).code).toBe("PARSE_ERROR");
    }
  });
});
