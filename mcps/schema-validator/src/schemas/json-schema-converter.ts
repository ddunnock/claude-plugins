/**
 * JSON Schema to Zod runtime conversion.
 * Uses zod-from-json-schema for safe, eval-free conversion.
 */

import type { ZodTypeAny } from "zod";
import { convertJsonSchemaToZod } from "zod-from-json-schema";
import { SchemaRegistryError } from "./types.ts";

/**
 * Convert a JSON Schema object to a Zod schema at runtime.
 *
 * @param jsonSchema - A JSON Schema object (draft-07 compatible)
 * @returns A Zod schema instance
 * @throws SchemaRegistryError with code INVALID_JSON_SCHEMA on conversion failure
 */
export function jsonSchemaToZod(
  jsonSchema: Record<string, unknown>,
): ZodTypeAny {
  try {
    return convertJsonSchemaToZod(jsonSchema as any) as unknown as ZodTypeAny;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new SchemaRegistryError(
      "INVALID_JSON_SCHEMA",
      `Failed to convert JSON Schema to Zod: ${msg}`,
    );
  }
}
