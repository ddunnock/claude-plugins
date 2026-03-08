/**
 * YAML format handler.
 * Parses and serializes YAML files using js-yaml with CORE_SCHEMA defaults.
 */

import yaml from "js-yaml";
import type { FormatHandler } from "./types.ts";
import { FormatError } from "./types.ts";

export const yamlHandler: FormatHandler = {
  extensions: [".yaml", ".yml"],

  parse(content: string): unknown {
    try {
      return yaml.load(content);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      const yamlErr = err as { mark?: { line?: number; column?: number } };
      throw new FormatError("PARSE_ERROR", `Invalid YAML: ${msg}`, "", {
        line: yamlErr.mark?.line != null ? yamlErr.mark.line + 1 : undefined,
        column: yamlErr.mark?.column != null ? yamlErr.mark.column + 1 : undefined,
        suggestedFix: "Check indentation and YAML syntax",
      });
    }
  },

  serialize(data: unknown): string {
    return yaml.dump(data, { lineWidth: -1, noRefs: true, sortKeys: false });
  },
};
