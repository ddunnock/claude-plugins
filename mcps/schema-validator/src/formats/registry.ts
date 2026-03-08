/**
 * Format registry -- maps file extensions to format handlers.
 * Provides auto-detection from file path and lists supported extensions.
 */

import path from "node:path";
import type { FormatHandler } from "./types.ts";
import { FormatError } from "./types.ts";
import { jsonHandler } from "./json.ts";
import { yamlHandler } from "./yaml.ts";
import { xmlHandler } from "./xml.ts";
import { tomlHandler } from "./toml.ts";

const handlers: FormatHandler[] = [jsonHandler, yamlHandler, xmlHandler, tomlHandler];

const extensionMap = new Map<string, FormatHandler>();
for (const handler of handlers) {
  for (const ext of handler.extensions) {
    extensionMap.set(ext, handler);
  }
}

/**
 * Get the format handler for a file path based on its extension.
 * @throws FormatError with code UNSUPPORTED_FORMAT if extension is not recognized.
 */
export function getHandler(filePath: string): FormatHandler {
  const ext = path.extname(filePath).toLowerCase();
  const handler = extensionMap.get(ext);
  if (!handler) {
    throw new FormatError(
      "UNSUPPORTED_FORMAT",
      `Unsupported file format: "${ext || "(no extension)"}"`,
      filePath,
      {
        suggestedFix: `Supported formats: ${getSupportedExtensions().join(", ")}`,
      },
    );
  }
  return handler;
}

/** Return all registered file extensions. */
export function getSupportedExtensions(): string[] {
  return [...extensionMap.keys()];
}
