/**
 * Shared types for format handlers, parse results, and errors.
 * Used by all format parsers and tool handlers across phases.
 */

/** Interface that each format handler must implement. */
export interface FormatHandler {
  /** File extensions this handler supports (e.g., [".json"]) */
  extensions: string[];
  /** Parse raw file content into a JS object */
  parse(content: string): unknown;
  /** Serialize a JS object back into the format's string representation */
  serialize(data: unknown): string;
}

/** Result of a parse operation, supporting partial/best-effort parsing. */
export interface ParseResult {
  data: unknown;
  errors?: ParseError[];
  partial?: boolean;
}

/** A single parse error with optional location info. */
export interface ParseError {
  message: string;
  line?: number;
  column?: number;
}

/** Structured error for format operations with diagnostic info. */
export class FormatError extends Error {
  code: string;
  filePath: string;
  line?: number;
  column?: number;
  suggestedFix?: string;

  constructor(
    code: string,
    message: string,
    filePath: string,
    options?: {
      line?: number;
      column?: number;
      suggestedFix?: string;
    },
  ) {
    super(message);
    this.name = "FormatError";
    this.code = code;
    this.filePath = filePath;
    this.line = options?.line;
    this.column = options?.column;
    this.suggestedFix = options?.suggestedFix;
  }
}

/** Structured error response returned from tools. */
export interface ToolError {
  error: string;
  message: string;
  filePath?: string;
  details?: unknown;
}
