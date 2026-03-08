/**
 * TOML format handler.
 * Parses and serializes TOML files using smol-toml.
 */

import { parse, stringify } from "smol-toml";
import type { FormatHandler } from "./types.ts";
import { FormatError } from "./types.ts";

export const tomlHandler: FormatHandler = {
  extensions: [".toml"],

  parse(content: string): unknown {
    try {
      return parse(content);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      throw new FormatError("PARSE_ERROR", `Invalid TOML: ${msg}`, "", {
        suggestedFix: "Check TOML syntax: tables use [name], values use key = value",
      });
    }
  },

  serialize(data: unknown): string {
    return stringify(data as Record<string, unknown>);
  },
};
