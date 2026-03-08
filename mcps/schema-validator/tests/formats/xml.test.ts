import { test, expect, describe } from "bun:test";
import { xmlHandler } from "../../src/formats/xml.ts";
import { FormatError } from "../../src/formats/types.ts";

describe("xmlHandler", () => {
  test("has correct extensions", () => {
    expect(xmlHandler.extensions).toEqual([".xml"]);
  });

  test("parses element with attribute and text", () => {
    const parsed = xmlHandler.parse('<root attr="v">text</root>') as Record<string, unknown>;
    const root = parsed.root as Record<string, unknown>;
    expect(root["@_attr"]).toBe("v");
    expect(root["#text"]).toBe("text");
  });

  test("round-trips attributes and text content", () => {
    const xml = '<root attr="value"><child>text</child></root>';
    const parsed = xmlHandler.parse(xml);
    const serialized = xmlHandler.serialize(parsed);
    const reparsed = xmlHandler.parse(serialized);
    // Check structural equivalence
    expect(reparsed).toEqual(parsed);
  });

  test("handles nested elements", () => {
    const xml = "<root><parent><child>value</child></parent></root>";
    const parsed = xmlHandler.parse(xml) as Record<string, unknown>;
    const root = parsed.root as Record<string, unknown>;
    const parent = root.parent as Record<string, unknown>;
    expect(parent.child).toBe("value");
  });

  test("handles self-closing tags", () => {
    const xml = '<root><empty/></root>';
    const parsed = xmlHandler.parse(xml) as Record<string, unknown>;
    const root = parsed.root as Record<string, unknown>;
    expect(root).toHaveProperty("empty");
  });

  test("throws FormatError on malformed XML", () => {
    expect(() => xmlHandler.parse("<root><unclosed>")).toThrow(FormatError);
  });

  test("FormatError has PARSE_ERROR code", () => {
    try {
      xmlHandler.parse("<root><bad");
      expect(true).toBe(false);
    } catch (e) {
      expect(e).toBeInstanceOf(FormatError);
      expect((e as FormatError).code).toBe("PARSE_ERROR");
    }
  });
});
