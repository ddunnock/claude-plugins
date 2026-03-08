/**
 * Atomic file write wrapper using write-file-atomic.
 * Ensures no partial files on crash (temp file + rename pattern).
 */

import writeFileAtomic from "write-file-atomic";

/**
 * Write content to a file atomically (temp file then rename).
 * Prevents partial writes on crash or interruption.
 *
 * @param filePath - Absolute path to write to
 * @param content - String content to write
 * @param options - Optional encoding (defaults to utf8)
 */
export async function atomicWrite(
  filePath: string,
  content: string,
  options?: { encoding?: string },
): Promise<void> {
  try {
    await writeFileAtomic(filePath, content, {
      encoding: (options?.encoding ?? "utf8") as BufferEncoding,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(`Atomic write failed for '${filePath}': ${msg}`);
  }
}
