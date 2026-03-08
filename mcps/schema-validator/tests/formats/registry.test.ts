import { test, expect, describe } from "bun:test";
import { getHandler, getSupportedExtensions } from "../../src/formats/registry.ts";
import { FormatError } from "../../src/formats/types.ts";

describe("format registry", () => {
  test("resolves .json to jsonHandler", () => {
    const handler = getHandler("config.json");
    expect(handler.extensions).toContain(".json");
  });

  test("resolves .yaml to yamlHandler", () => {
    const handler = getHandler("config.yaml");
    expect(handler.extensions).toContain(".yaml");
  });

  test("resolves .yml to yamlHandler", () => {
    const handler = getHandler("config.yml");
    expect(handler.extensions).toContain(".yaml");
  });

  test("resolves .xml to xmlHandler", () => {
    const handler = getHandler("config.xml");
    expect(handler.extensions).toContain(".xml");
  });

  test("resolves .toml to tomlHandler", () => {
    const handler = getHandler("config.toml");
    expect(handler.extensions).toContain(".toml");
  });

  test("handles full paths", () => {
    const handler = getHandler("/some/path/to/file.json");
    expect(handler.extensions).toContain(".json");
  });

  test("throws FormatError for unknown extension", () => {
    expect(() => getHandler("file.unknown")).toThrow(FormatError);
  });

  test("FormatError has UNSUPPORTED_FORMAT code", () => {
    try {
      getHandler("file.csv");
      expect(true).toBe(false);
    } catch (e) {
      expect(e).toBeInstanceOf(FormatError);
      expect((e as FormatError).code).toBe("UNSUPPORTED_FORMAT");
    }
  });

  test("getSupportedExtensions returns all extensions", () => {
    const exts = getSupportedExtensions();
    expect(exts).toContain(".json");
    expect(exts).toContain(".yaml");
    expect(exts).toContain(".yml");
    expect(exts).toContain(".xml");
    expect(exts).toContain(".toml");
  });
});
