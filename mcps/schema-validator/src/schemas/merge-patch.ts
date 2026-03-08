/**
 * RFC 7386 JSON Merge Patch implementation.
 * Merges a patch into a target value following the merge-patch semantics:
 * - null in patch deletes the key
 * - arrays are replaced wholesale (not merged)
 * - objects are recursively merged
 * - non-object patch replaces target entirely
 */

function isObject(val: unknown): val is Record<string, unknown> {
  return val !== null && typeof val === "object" && !Array.isArray(val);
}

/**
 * Apply a JSON Merge Patch (RFC 7386) to a target value.
 *
 * @param target - The original value
 * @param patch - The patch to apply
 * @returns The merged result
 */
export function jsonMergePatch(target: unknown, patch: unknown): unknown {
  if (!isObject(patch)) {
    return patch;
  }

  // If target is not an object, start with empty object
  const result: Record<string, unknown> = isObject(target)
    ? { ...target }
    : {};

  for (const [key, value] of Object.entries(patch)) {
    if (value === null) {
      delete result[key];
    } else if (isObject(value) && isObject(result[key])) {
      result[key] = jsonMergePatch(result[key], value);
    } else {
      result[key] = value;
    }
  }

  return result;
}
