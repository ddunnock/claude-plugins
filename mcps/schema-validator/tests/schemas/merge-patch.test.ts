import { test, expect, describe } from "bun:test";
import { jsonMergePatch } from "../../src/schemas/merge-patch.ts";

describe("jsonMergePatch (RFC 7386)", () => {
  test("merges simple key updates", () => {
    expect(jsonMergePatch({ a: 1, b: 2 }, { b: 3 })).toEqual({ a: 1, b: 3 });
  });

  test("null value deletes key", () => {
    expect(jsonMergePatch({ a: 1, b: 2 }, { b: null })).toEqual({ a: 1 });
  });

  test("deep merges nested objects", () => {
    expect(jsonMergePatch({ a: { x: 1 } }, { a: { y: 2 } })).toEqual({
      a: { x: 1, y: 2 },
    });
  });

  test("arrays are replaced wholesale", () => {
    expect(jsonMergePatch({ a: [1, 2] }, { a: [3] })).toEqual({ a: [3] });
  });

  test("non-object target is replaced", () => {
    expect(jsonMergePatch("old", { a: 1 })).toEqual({ a: 1 });
  });

  test("non-object patch replaces target", () => {
    expect(jsonMergePatch({ a: 1 }, "new")).toBe("new");
  });

  test("adds new keys", () => {
    expect(jsonMergePatch({ a: 1 }, { b: 2 })).toEqual({ a: 1, b: 2 });
  });

  test("empty patch returns copy of target", () => {
    expect(jsonMergePatch({ a: 1 }, {})).toEqual({ a: 1 });
  });

  test("null patch returns null", () => {
    expect(jsonMergePatch({ a: 1 }, null)).toBeNull();
  });
});
