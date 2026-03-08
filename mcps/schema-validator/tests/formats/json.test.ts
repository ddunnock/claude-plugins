import { test, expect, describe } from "bun:test";
import { jsonHandler } from "../../src/formats/json.ts";
import { FormatError } from "../../src/formats/types.ts";

describe("jsonHandler", () => {
  test("has correct extensions", () => {
    expect(jsonHandler.extensions).toEqual([".json"]);
  });

  test("parses simple object", () => {
    expect(jsonHandler.parse('{"a":1}')).toEqual({ a: 1 });
  });

  test("serializes simple object", () => {
    const result = jsonHandler.serialize({ a: 1 });
    expect(JSON.parse(result)).toEqual({ a: 1 });
  });

  test("round-trips nested objects, arrays, nulls, booleans, numbers", () => {
    const data = {
      name: "test",
      nested: { deep: { value: 42 } },
      array: [1, "two", null, true, false],
      nullVal: null,
      bool: true,
      num: 3.14,
    };
    const roundTripped = jsonHandler.parse(jsonHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("handles unicode characters", () => {
    const data = { emoji: "\u{1F600}", cjk: "\u4F60\u597D", accent: "\u00E9\u00E0\u00FC" };
    const roundTripped = jsonHandler.parse(jsonHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("handles large numbers", () => {
    const data = { big: 9007199254740991, negative: -9007199254740991 };
    const roundTripped = jsonHandler.parse(jsonHandler.serialize(data));
    expect(roundTripped).toEqual(data);
  });

  test("throws FormatError on malformed input", () => {
    expect(() => jsonHandler.parse("{invalid}")).toThrow(FormatError);
  });

  test("FormatError has descriptive message", () => {
    try {
      jsonHandler.parse("{bad json");
      expect(true).toBe(false); // should not reach
    } catch (e) {
      expect(e).toBeInstanceOf(FormatError);
      expect((e as FormatError).code).toBe("PARSE_ERROR");
    }
  });
});
