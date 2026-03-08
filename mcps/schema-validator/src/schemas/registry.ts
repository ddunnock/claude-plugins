/**
 * Schema Registry: stores, retrieves, and composes Zod schemas.
 * Supports registration from Zod instances or JSON Schema wire format.
 */

import { z, type ZodTypeAny, type ZodObject, type ZodRawShape } from "zod";
import type { RegisteredSchema, SchemaRegistryConfig } from "./types.ts";
import { SchemaRegistryError } from "./types.ts";
import { jsonSchemaToZod } from "./json-schema-converter.ts";
import { discoverSchemas } from "./discovery.ts";

/** Count top-level fields in a Zod schema (object schemas only). */
function countFields(schema: ZodTypeAny): number {
  if (schema instanceof z.ZodObject) {
    return Object.keys(schema.shape).length;
  }
  return 0;
}

/**
 * In-memory schema registry backed by a Map.
 * Schemas are immutable once registered -- duplicate names are rejected.
 */
export class SchemaRegistry {
  private schemas = new Map<string, RegisteredSchema>();

  /**
   * Register a Zod schema by name.
   *
   * @param name - Namespaced schema name (e.g. "skill/export")
   * @param zodSchema - The Zod schema instance
   * @param source - How the schema was added
   * @param extendsName - Optional parent schema to merge with
   * @throws SchemaRegistryError SCHEMA_EXISTS if name already registered
   * @throws SchemaRegistryError SCHEMA_NOT_FOUND if extends references unknown schema
   */
  register(
    name: string,
    zodSchema: ZodTypeAny,
    source: "discovered" | "registered",
    extendsName?: string,
  ): void {
    if (this.schemas.has(name)) {
      throw new SchemaRegistryError(
        "SCHEMA_EXISTS",
        `Schema '${name}' is already registered`,
      );
    }

    let finalSchema = zodSchema;
    if (extendsName) {
      const parent = this.schemas.get(extendsName);
      if (!parent) {
        throw new SchemaRegistryError(
          "SCHEMA_NOT_FOUND",
          `Parent schema '${extendsName}' not found for extends`,
        );
      }
      // Merge parent + child (both must be ZodObject)
      if (
        parent.zodSchema instanceof z.ZodObject &&
        zodSchema instanceof z.ZodObject
      ) {
        finalSchema = parent.zodSchema.merge(zodSchema);
      }
    }

    this.schemas.set(name, {
      name,
      zodSchema: finalSchema,
      source,
      fieldCount: countFields(finalSchema),
      ...(extendsName ? { extends: extendsName } : {}),
    });
  }

  /**
   * Get a registered schema by name.
   * @returns The schema entry or undefined if not found
   */
  get(name: string): RegisteredSchema | undefined {
    return this.schemas.get(name);
  }

  /**
   * List metadata for all registered schemas.
   */
  list(): Array<{
    name: string;
    source: string;
    fieldCount: number;
    extends?: string;
  }> {
    return Array.from(this.schemas.values()).map((s) => ({
      name: s.name,
      source: s.source,
      fieldCount: s.fieldCount,
      ...(s.extends ? { extends: s.extends } : {}),
    }));
  }

  /**
   * Register a schema from JSON Schema wire format.
   * Converts to Zod at runtime, then delegates to register().
   *
   * @param name - Schema name
   * @param jsonSchema - JSON Schema object
   * @param extendsName - Optional parent schema
   */
  registerFromJsonSchema(
    name: string,
    jsonSchema: Record<string, unknown>,
    extendsName?: string,
  ): void {
    const zodSchema = jsonSchemaToZod(jsonSchema);
    this.register(name, zodSchema, "registered", extendsName);
  }

  /**
   * Discover and register schemas from configured skill paths.
   * Delegates to discoverSchemas() for filesystem scanning.
   */
  async discover(config: SchemaRegistryConfig): Promise<void> {
    await discoverSchemas(config.skillPaths, this);
  }
}
