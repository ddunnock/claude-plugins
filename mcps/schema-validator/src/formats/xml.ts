/**
 * XML format handler.
 * Parses and serializes XML using fast-xml-parser.
 * Configured for prompt markup use case (removeNSPrefix, preserves attributes).
 */

import { XMLParser, XMLBuilder, XMLValidator } from "fast-xml-parser";
import type { FormatHandler } from "./types.ts";
import { FormatError } from "./types.ts";

/** Shared options for parse/serialize symmetry. */
const sharedOptions = {
  ignoreAttributes: false,
  attributeNamePrefix: "@_",
  textNodeName: "#text",
  parseTagValue: false,
  parseAttributeValue: false,
  removeNSPrefix: true,
};

const parser = new XMLParser(sharedOptions);
const builder = new XMLBuilder({
  ...sharedOptions,
  format: true,
  indentBy: "  ",
});

export const xmlHandler: FormatHandler = {
  extensions: [".xml"],

  parse(content: string): unknown {
    const validation = XMLValidator.validate(content);
    if (validation !== true) {
      const err = validation as { err?: { msg?: string; line?: number; col?: number } };
      throw new FormatError(
        "PARSE_ERROR",
        `Invalid XML: ${err.err?.msg ?? "validation failed"}`,
        "",
        {
          line: err.err?.line,
          column: err.err?.col,
          suggestedFix: "Check for unclosed tags or malformed XML",
        },
      );
    }
    return parser.parse(content);
  },

  serialize(data: unknown): string {
    return builder.build(data);
  },
};
