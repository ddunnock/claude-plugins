/**
 * Schema file structure validation before dynamic loading.
 * Pre-flight checks: existence, extension, size, and text content.
 * The actual schema import happens in Phase 2 -- this validates the file is safe to attempt.
 */

import path from "node:path";

const ALLOWED_EXTENSIONS = new Set([".ts", ".js", ".json"]);
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const PROBE_SIZE = 1024; // bytes to check for binary content

/** Error thrown when a schema file fails pre-load validation. */
export class SchemaLoadError extends Error {
  code: string;
  filePath: string;

  constructor(code: string, message: string, filePath: string) {
    super(message);
    this.name = "SchemaLoadError";
    this.code = code;
    this.filePath = filePath;
  }
}

/** Result of schema file validation. */
export interface SchemaFileValidation {
  valid: boolean;
  filePath: string;
  size: number;
  extension: string;
}

/**
 * Validate that a schema file is safe to load.
 * Checks existence, extension, size, and content (no binary/null bytes).
 *
 * @param filePath - Path to the schema file
 * @returns Validation result with file metadata
 * @throws SchemaLoadError if validation fails
 */
export async function validateSchemaFile(
  filePath: string,
): Promise<SchemaFileValidation> {
  const ext = path.extname(filePath).toLowerCase();

  // Check extension
  if (!ALLOWED_EXTENSIONS.has(ext)) {
    throw new SchemaLoadError(
      "INVALID_EXTENSION",
      `Schema file '${filePath}' has unsupported extension '${ext}'. Allowed: ${[...ALLOWED_EXTENSIONS].join(", ")}`,
      filePath,
    );
  }

  // Check existence
  const file = Bun.file(filePath);
  const exists = await file.exists();
  if (!exists) {
    throw new SchemaLoadError(
      "FILE_NOT_FOUND",
      `Schema file not found: '${filePath}'`,
      filePath,
    );
  }

  // Check size
  const size = file.size;
  if (size > MAX_FILE_SIZE) {
    throw new SchemaLoadError(
      "FILE_TOO_LARGE",
      `Schema file '${filePath}' is ${size} bytes, exceeds ${MAX_FILE_SIZE} byte limit`,
      filePath,
    );
  }

  // Check for binary content (null bytes in first 1024 bytes)
  const probe = await file.slice(0, PROBE_SIZE).arrayBuffer();
  const bytes = new Uint8Array(probe);
  for (const byte of bytes) {
    if (byte === 0) {
      throw new SchemaLoadError(
        "BINARY_FILE",
        `Schema file '${filePath}' appears to be binary (contains null bytes)`,
        filePath,
      );
    }
  }

  return {
    valid: true,
    filePath,
    size,
    extension: ext,
  };
}
