/**
 * Shared types for the schema registry subsystem.
 */

import type { ZodTypeAny } from "zod";

/** A schema stored in the registry with metadata. */
export interface RegisteredSchema {
  /** Namespaced name, e.g. "skill-name/schemaExport" */
  name: string;
  /** The runtime Zod validator */
  zodSchema: ZodTypeAny;
  /** How the schema was added */
  source: "discovered" | "registered";
  /** Number of top-level fields (for object schemas) */
  fieldCount: number;
  /** Parent schema name if composed via extends */
  extends?: string;
}

/** Configuration for schema discovery. */
export interface SchemaRegistryConfig {
  /** Paths to skill directories to scan for schemas */
  skillPaths: string[];
}

/** Re-export healing types for external consumers. */
export type { HealFix, HealResult } from "./healer";

/** Error class for schema registry operations. */
export class SchemaRegistryError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = "SchemaRegistryError";
    this.code = code;
  }
}
