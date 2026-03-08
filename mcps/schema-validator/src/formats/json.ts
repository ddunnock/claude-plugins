/**
 * JSON format handler.
 * Parses and serializes JSON files with structured error reporting.
 */

import type { FormatHandler } from "./types.ts";
import { FormatError } from "./types.ts";

export const jsonHandler: FormatHandler = {
  extensions: [".json"],

  parse(content: string): unknown {
    try {
      return JSON.parse(content);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      throw new FormatError("PARSE_ERROR", `Invalid JSON: ${msg}`, "", {
        suggestedFix: "Check for missing commas, brackets, or quotes",
      });
    }
  },

  serialize(data: unknown): string {
    return JSON.stringify(data, null, 2);
  },
};
