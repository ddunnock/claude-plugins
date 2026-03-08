/**
 * Path traversal prevention for the schema-validator MCP server.
 * Validates file paths against allowed directories before any file I/O.
 */

import path from "node:path";

/** Error thrown when a file path fails validation. */
export class PathValidationError extends Error {
  code: string;
  rejectedPath: string;

  constructor(code: string, message: string, rejectedPath: string) {
    super(message);
    this.name = "PathValidationError";
    this.code = code;
    this.rejectedPath = rejectedPath;
  }
}

/**
 * Validate that a file path is within one of the allowed directories.
 * Rejects null bytes and path traversal attempts.
 *
 * @param filePath - The path to validate
 * @param allowedDirs - Directories the path must be within (defaults to [cwd])
 * @returns The resolved absolute path
 * @throws PathValidationError if the path is unsafe
 */
export function validatePath(
  filePath: string,
  allowedDirs?: string[],
): string {
  const dirs = allowedDirs ?? [process.cwd()];

  if (dirs.length === 0) {
    throw new PathValidationError(
      "ERR_NO_ALLOWED_DIRS",
      "No allowed directories configured",
      filePath,
    );
  }

  // Reject null bytes
  if (filePath.includes("\0")) {
    throw new PathValidationError(
      "ERR_NULL_BYTE",
      `Path contains null byte: '${filePath.replace(/\0/g, "\\0")}'`,
      filePath,
    );
  }

  const resolved = path.resolve(filePath);

  const isAllowed = dirs.some((dir) => {
    const normalizedDir = path.resolve(dir);
    const dirPrefix = normalizedDir + path.sep;
    return resolved.startsWith(dirPrefix) || resolved === normalizedDir;
  });

  if (!isAllowed) {
    throw new PathValidationError(
      "ERR_PATH_TRAVERSAL",
      `Path '${filePath}' is outside allowed directories`,
      filePath,
    );
  }

  return resolved;
}
