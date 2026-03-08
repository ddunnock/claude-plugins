/**
 * Schema discovery: scans skill paths for schemas/*.ts files,
 * dynamically imports them, and registers Zod exports.
 */

import path from "node:path";
import fs from "node:fs";
import { z } from "zod";
import type { SchemaRegistry } from "./registry.ts";
import { validateSchemaFile } from "../security/schema-loader.ts";

/**
 * Discover Zod schemas from skill directory schemas/ folders.
 * Each named export that is a ZodType instance gets registered
 * as "skillDirName/exportName" with source "discovered".
 *
 * Invalid files (syntax errors, no Zod exports) are skipped with
 * a warning logged to stderr -- discovery never throws.
 *
 * @param skillPaths - Array of absolute paths to skill directories
 * @param registry - The SchemaRegistry to register discovered schemas into
 */
export async function discoverSchemas(
  skillPaths: string[],
  registry: SchemaRegistry,
): Promise<void> {
  for (const skillPath of skillPaths) {
    const absPath = path.resolve(skillPath);
    const schemasDir = path.join(absPath, "schemas");

    // Skip if schemas directory doesn't exist
    if (!fs.existsSync(schemasDir)) {
      continue;
    }

    const skillName = path.basename(absPath);
    let files: string[];
    try {
      files = fs
        .readdirSync(schemasDir)
        .filter((f) => f.endsWith(".ts"))
        .map((f) => path.join(schemasDir, f));
    } catch (err) {
      console.error(
        `[schema-discovery] Error reading ${schemasDir}: ${err instanceof Error ? err.message : err}`,
      );
      continue;
    }

    for (const filePath of files) {
      try {
        // SEC-03 pre-flight validation
        await validateSchemaFile(filePath);

        // Dynamic import
        const mod = await import(path.resolve(filePath));

        // Extract Zod schema exports
        for (const [exportName, value] of Object.entries(mod)) {
          if (exportName === "default") continue;
          if (value instanceof z.ZodType) {
            const schemaName = `${skillName}/${exportName}`;
            try {
              registry.register(schemaName, value, "discovered");
            } catch (regErr) {
              console.error(
                `[schema-discovery] Failed to register ${schemaName}: ${regErr instanceof Error ? regErr.message : regErr}`,
              );
            }
          }
        }
      } catch (err) {
        console.error(
          `[schema-discovery] Skipping ${filePath}: ${err instanceof Error ? err.message : err}`,
        );
        continue;
      }
    }
  }
}
