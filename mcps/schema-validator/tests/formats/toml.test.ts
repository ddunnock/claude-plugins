import { test, expect, describe } from "bun:test";
import { tomlHandler } from "../../src/formats/toml.ts";
import { FormatError } from "../../src/formats/types.ts";

describe("tomlHandler", () => {
  test("has correct extensions", () => {
    expect(tomlHandler.extensions).toEqual([".toml"]);
  });

  test("parses simple key-value", () => {
    expect(tomlHandler.parse("a = 1")).toEqual({ a: 1 });
  });

  test("serializes simple object", () => {
    const result = tomlHandler.serialize({ a: 1 });
    expect(result).toContain("a");
  });

  test("round-trips tables", () => {
    const toml = `[server]\nhost = "localhost"\nport = 8080\n`;
    const parsed = tomlHandler.parse(toml);
    const roundTripped = tomlHandler.parse(tomlHandler.serialize(parsed));
    expect(roundTripped).toEqual(parsed);
  });

  test("round-trips arrays", () => {
    const data = { items: ["one", "two", "three"] };
    const roundTripped = tomlHandler.parse(tomlHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("round-trips array of tables", () => {
    const toml = `[[products]]\nname = "Hammer"\n\n[[products]]\nname = "Nail"\n`;
    const parsed = tomlHandler.parse(toml);
    const roundTripped = tomlHandler.parse(tomlHandler.serialize(parsed));
    expect(roundTripped).toEqual(parsed);
  });

  test("handles strings with special characters", () => {
    const data = { greeting: 'Hello "world"' };
    const roundTripped = tomlHandler.parse(tomlHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("throws FormatError on malformed input", () => {
    expect(() => tomlHandler.parse("= invalid")).toThrow(FormatError);
  });

  test("FormatError has PARSE_ERROR code", () => {
    try {
      tomlHandler.parse("[invalid\nbad");
      expect(true).toBe(false);
    } catch (e) {
      expect(e).toBeInstanceOf(FormatError);
      expect((e as FormatError).code).toBe("PARSE_ERROR");
    }
  });
});
