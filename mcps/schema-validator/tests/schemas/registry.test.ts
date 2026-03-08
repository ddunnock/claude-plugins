import { test, expect, describe } from "bun:test";
import { z } from "zod";
import { SchemaRegistry } from "../../src/schemas/registry.ts";
import { SchemaRegistryError } from "../../src/schemas/types.ts";

describe("SchemaRegistry", () => {
  test("register and get a schema", () => {
    const registry = new SchemaRegistry();
    const schema = z.object({ name: z.string() });
    registry.register("test/user", schema, "registered");

    const result = registry.get("test/user");
    expect(result).toBeDefined();
    expect(result!.name).toBe("test/user");
    expect(result!.source).toBe("registered");
    expect(result!.fieldCount).toBe(1);
  });

  test("get returns undefined for unknown schema", () => {
    const registry = new SchemaRegistry();
    expect(registry.get("nonexistent")).toBeUndefined();
  });

  test("list returns metadata for all registered schemas", () => {
    const registry = new SchemaRegistry();
    registry.register("a/one", z.object({ x: z.number() }), "registered");
    registry.register("b/two", z.object({ y: z.string(), z: z.boolean() }), "discovered");

    const list = registry.list();
    expect(list).toHaveLength(2);
    expect(list[0]).toEqual({
      name: "a/one",
      source: "registered",
      fieldCount: 1,
    });
    expect(list[1]).toEqual({
      name: "b/two",
      source: "discovered",
      fieldCount: 2,
    });
  });

  test("register duplicate name throws SchemaRegistryError", () => {
    const registry = new SchemaRegistry();
    registry.register("test/dup", z.object({}), "registered");

    expect(() => {
      registry.register("test/dup", z.object({}), "registered");
    }).toThrow(SchemaRegistryError);

    try {
      registry.register("test/dup", z.object({}), "registered");
    } catch (e) {
      expect((e as SchemaRegistryError).code).toBe("SCHEMA_EXISTS");
    }
  });

  test("register with extends merges parent fields", () => {
    const registry = new SchemaRegistry();
    const parent = z.object({ id: z.number() });
    registry.register("base/entity", parent, "registered");

    const child = z.object({ name: z.string() });
    registry.register("ext/user", child, "registered", "base/entity");

    const result = registry.get("ext/user");
    expect(result).toBeDefined();
    expect(result!.extends).toBe("base/entity");
    // merged schema should have both fields
    expect(result!.fieldCount).toBe(2);
    // Validate with merged schema
    const valid = result!.zodSchema.safeParse({ id: 1, name: "Alice" });
    expect(valid.success).toBe(true);
  });

  test("register with extends referencing nonexistent throws", () => {
    const registry = new SchemaRegistry();

    expect(() => {
      registry.register("ext/orphan", z.object({}), "registered", "no/parent");
    }).toThrow(SchemaRegistryError);

    try {
      registry.register("ext/orphan", z.object({}), "registered", "no/parent");
    } catch (e) {
      expect((e as SchemaRegistryError).code).toBe("SCHEMA_NOT_FOUND");
    }
  });

  test("registerFromJsonSchema converts and registers", () => {
    const registry = new SchemaRegistry();
    registry.registerFromJsonSchema("json/test", {
      type: "object",
      properties: {
        name: { type: "string" },
        age: { type: "number" },
      },
      required: ["name"],
    });

    const result = registry.get("json/test");
    expect(result).toBeDefined();
    expect(result!.source).toBe("registered");

    // Validate with the converted schema
    const valid = result!.zodSchema.safeParse({ name: "Bob", age: 30 });
    expect(valid.success).toBe(true);

    const invalid = result!.zodSchema.safeParse({ age: 30 });
    expect(invalid.success).toBe(false);
  });

  test("registerFromJsonSchema with extends merges parent", () => {
    const registry = new SchemaRegistry();
    registry.register("base/item", z.object({ id: z.number() }), "registered");

    registry.registerFromJsonSchema(
      "ext/product",
      {
        type: "object",
        properties: { title: { type: "string" } },
        required: ["title"],
      },
      "base/item",
    );

    const result = registry.get("ext/product");
    expect(result).toBeDefined();
    expect(result!.extends).toBe("base/item");

    const valid = result!.zodSchema.safeParse({ id: 1, title: "Widget" });
    expect(valid.success).toBe(true);
  });
});
