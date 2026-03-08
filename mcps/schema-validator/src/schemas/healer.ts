/**
 * Healing engine: takes raw parsed data + a Zod schema, identifies validation
 * issues, maps them to fix objects, and applies safe corrections while
 * preserving unknown fields.
 */

import type { ZodTypeAny } from "zod";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface HealFix {
  path: (string | number)[];
  fixType: "default" | "coerce" | "manual";
  oldValue: unknown;
  newValue: unknown;
  confidence: "safe" | "uncertain";
  message: string;
}

export interface HealResult {
  healed: boolean;
  data: Record<string, unknown>;
  applied: HealFix[];
  remaining: HealFix[];
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/** Walk a ZodObject shape to find the schema node at a given path. */
function getSchemaAtPath(
  rootSchema: ZodTypeAny,
  path: (string | number)[],
): ZodTypeAny | undefined {
  let current: ZodTypeAny | undefined = rootSchema;
  for (const segment of path) {
    if (!current) return undefined;
    // Unwrap wrappers (ZodDefault, ZodOptional, ZodNullable) to reach the
    // structural type underneath.
    current = unwrap(current);
    if (
      current._def.typeName === "ZodObject" &&
      typeof segment === "string"
    ) {
      current = (current as any).shape?.[segment];
    } else if (
      current._def.typeName === "ZodArray" &&
      typeof segment === "number"
    ) {
      current = current._def.type;
    } else {
      return undefined;
    }
  }
  return current;
}

/** Unwrap ZodDefault / ZodOptional / ZodNullable to get the inner structural type. */
function unwrap(schema: ZodTypeAny): ZodTypeAny {
  let s = schema;
  while (
    s._def.typeName === "ZodDefault" ||
    s._def.typeName === "ZodOptional" ||
    s._def.typeName === "ZodNullable"
  ) {
    s = s._def.innerType;
  }
  return s;
}

/** Check whether a schema node (possibly wrapped) has a ZodDefault and return its value. */
function getDefaultValue(
  schema: ZodTypeAny | undefined,
): { hasDefault: boolean; value?: unknown } {
  if (!schema) return { hasDefault: false };
  // Walk through wrappers looking for ZodDefault
  let s = schema;
  while (s) {
    if (s._def.typeName === "ZodDefault") {
      return { hasDefault: true, value: s._def.defaultValue() };
    }
    if (s._def.innerType) {
      s = s._def.innerType;
    } else {
      break;
    }
  }
  return { hasDefault: false };
}

/** Get the expected type name from a potentially-wrapped schema node. */
function getExpectedTypeName(schema: ZodTypeAny): string {
  const inner = unwrap(schema);
  return inner._def.typeName as string;
}

// --- Coercion helpers (conservative, per CONTEXT.md decisions) ---

function coerceToNumber(value: unknown): { success: boolean; result?: number } {
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed === "") return { success: false };
    const num = Number(trimmed);
    if (!Number.isNaN(num)) {
      return { success: true, result: num };
    }
  }
  return { success: false };
}

function coerceToBoolean(
  value: unknown,
): { success: boolean; result?: boolean } {
  // Exact match only, case-sensitive. "yes"/"no"/"1"/"0"/"True" etc. NOT coerced.
  if (value === "true") return { success: true, result: true };
  if (value === "false") return { success: true, result: false };
  return { success: false };
}

function coerceToString(
  value: unknown,
): { success: boolean; result?: string } {
  if (typeof value === "number" || typeof value === "boolean") {
    return { success: true, result: String(value) };
  }
  return { success: false };
}

// --- Nested value helpers ---

function getNestedValue(
  obj: Record<string, unknown>,
  path: (string | number)[],
): unknown {
  let current: any = obj;
  for (const segment of path) {
    if (current === undefined || current === null) return undefined;
    current = current[segment];
  }
  return current;
}

function setNestedValue(
  obj: Record<string, unknown>,
  path: (string | number)[],
  value: unknown,
): void {
  if (path.length === 0) return;
  let current: any = obj;
  for (let i = 0; i < path.length - 1; i++) {
    const segment = path[i]!;
    const nextSegment = path[i + 1]!;
    if (current[segment] === undefined || current[segment] === null) {
      // Create intermediate: object if next segment is string, array if number
      current[segment] = typeof nextSegment === "number" ? [] : {};
    }
    current = current[segment];
  }
  current[path[path.length - 1]!] = value;
}

/**
 * Walk a ZodObject schema and find fields that are missing from rawData but
 * have ZodDefault wrappers.  Returns HealFix[] for each such field.
 * Recurses into nested ZodObject shapes.
 */
function applyMissingDefaults(
  obj: Record<string, unknown>,
  schema: ZodTypeAny,
  basePath: (string | number)[],
): HealFix[] {
  const fixes: HealFix[] = [];
  const inner = unwrap(schema);
  if (inner._def.typeName !== "ZodObject") return fixes;

  const shape = (inner as any).shape as Record<string, ZodTypeAny>;
  for (const [key, fieldSchema] of Object.entries(shape)) {
    const path = [...basePath, key];
    const value = obj?.[key];

    if (value === undefined) {
      const def = getDefaultValue(fieldSchema);
      if (def.hasDefault) {
        fixes.push({
          path,
          fixType: "default",
          oldValue: undefined,
          newValue: def.value,
          confidence: "safe",
          message: "Applied schema default for missing field",
        });
      }
    } else if (
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value)
    ) {
      // Recurse into nested objects
      const nestedFixes = applyMissingDefaults(
        value as Record<string, unknown>,
        fieldSchema,
        path,
      );
      fixes.push(...nestedFixes);
    }
  }
  return fixes;
}

// ---------------------------------------------------------------------------
// Core healing function
// ---------------------------------------------------------------------------

/**
 * Heal raw parsed data against a Zod schema.
 *
 * 1. Runs safeParse to collect validation issues.
 * 2. Maps each issue to a HealFix (default, coerce, or manual).
 * 3. Applies fixable corrections to the raw data (preserving unknown fields).
 * 4. Re-validates and returns the result.
 */
export function healData(
  rawData: Record<string, unknown>,
  schema: ZodTypeAny,
): HealResult {
  // Check validation
  const firstParse = schema.safeParse(rawData);

  if (firstParse.success) {
    // Even when valid, Zod may have applied defaults internally that the raw
    // data doesn't have.  Detect missing-but-defaulted fields and apply them
    // to the raw data so callers see complete objects.
    const defaultFixes = applyMissingDefaults(rawData, schema, []);
    if (defaultFixes.length === 0) {
      return { healed: true, data: rawData, applied: [], remaining: [] };
    }
    // Apply the default fixes
    for (const fix of defaultFixes) {
      setNestedValue(rawData, fix.path, fix.newValue);
    }
    return { healed: true, data: rawData, applied: defaultFixes, remaining: [] };
  }

  const fixes: HealFix[] = [];

  for (const issue of firstParse.error.issues) {
    const path = issue.path as (string | number)[];
    const oldValue = getNestedValue(rawData, path);
    const schemaAtPath = getSchemaAtPath(schema, path);

    if (issue.code === "invalid_type") {
      const received = (issue as any).received as string;
      const expected = (issue as any).expected as string;

      if (received === "undefined" || oldValue === undefined || oldValue === null) {
        // Missing field (or null) -- try to apply default
        const def = getDefaultValue(schemaAtPath);
        if (def.hasDefault) {
          fixes.push({
            path,
            fixType: "default",
            oldValue,
            newValue: def.value,
            confidence: "safe",
            message: `Applied schema default for missing field`,
          });
        } else {
          fixes.push({
            path,
            fixType: "manual",
            oldValue,
            newValue: undefined,
            confidence: "uncertain",
            message: `Missing required field '${path.join(".")}' with no schema default`,
          });
        }
      } else {
        // Wrong type -- attempt conservative coercion
        const fix = attemptCoercion(path, oldValue, expected, schemaAtPath);
        fixes.push(fix);
      }
    } else if (issue.code === "invalid_enum_value") {
      const options = (issue as any).options as string[] | undefined;
      fixes.push({
        path,
        fixType: "manual",
        oldValue,
        newValue: undefined,
        confidence: "uncertain",
        message: `Invalid enum value '${String(oldValue)}'. Allowed: ${options ? options.join(", ") : "unknown"}`,
      });
    } else {
      // All other issue codes -> manual
      fixes.push({
        path,
        fixType: "manual",
        oldValue,
        newValue: undefined,
        confidence: "uncertain",
        message: `Validation error: ${issue.message}`,
      });
    }
  }

  // Separate applied vs remaining
  const applied = fixes.filter((f) => f.fixType !== "manual");
  const remaining = fixes.filter((f) => f.fixType === "manual");

  // Apply fixes to raw data (mutate in place -- preserves unknown fields)
  for (const fix of applied) {
    setNestedValue(rawData, fix.path, fix.newValue);
  }

  // Re-validate
  const revalidation = schema.safeParse(rawData);
  if (!revalidation.success) {
    // Append new issues as manual remaining fixes
    for (const issue of revalidation.error.issues) {
      const path = issue.path as (string | number)[];
      // Avoid duplicating fixes we already know about
      const alreadyTracked = remaining.some(
        (r) => JSON.stringify(r.path) === JSON.stringify(path),
      );
      if (!alreadyTracked) {
        remaining.push({
          path,
          fixType: "manual",
          oldValue: getNestedValue(rawData, path),
          newValue: undefined,
          confidence: "uncertain",
          message: `Remaining after healing: ${issue.message}`,
        });
      }
    }
  } else {
    // After successful re-validation, apply any missing defaults that Zod
    // handles internally but aren't in rawData yet (same as initial success path)
    const defaultFixes = applyMissingDefaults(rawData, schema, []);
    for (const fix of defaultFixes) {
      setNestedValue(rawData, fix.path, fix.newValue);
      applied.push(fix);
    }
  }

  return {
    healed: revalidation.success,
    data: rawData,
    applied,
    remaining,
  };
}

/** Attempt conservative type coercion. */
function attemptCoercion(
  path: (string | number)[],
  oldValue: unknown,
  expectedType: string,
  schemaAtPath: ZodTypeAny | undefined,
): HealFix {
  // Determine the target type from the schema if possible, fall back to expected
  let targetType = expectedType;
  if (schemaAtPath) {
    const typeName = getExpectedTypeName(schemaAtPath);
    if (typeName === "ZodNumber") targetType = "number";
    else if (typeName === "ZodBoolean") targetType = "boolean";
    else if (typeName === "ZodString") targetType = "string";
  }

  if (targetType === "number") {
    const r = coerceToNumber(oldValue);
    if (r.success) {
      return {
        path,
        fixType: "coerce",
        oldValue,
        newValue: r.result,
        confidence: "safe",
        message: `Coerced ${JSON.stringify(oldValue)} to number ${r.result}`,
      };
    }
  }

  if (targetType === "boolean") {
    const r = coerceToBoolean(oldValue);
    if (r.success) {
      return {
        path,
        fixType: "coerce",
        oldValue,
        newValue: r.result,
        confidence: "safe",
        message: `Coerced ${JSON.stringify(oldValue)} to boolean ${r.result}`,
      };
    }
  }

  if (targetType === "string") {
    const r = coerceToString(oldValue);
    if (r.success) {
      return {
        path,
        fixType: "coerce",
        oldValue,
        newValue: r.result,
        confidence: "safe",
        message: `Coerced ${JSON.stringify(oldValue)} to string "${r.result}"`,
      };
    }
  }

  // Also try default if coercion failed
  if (schemaAtPath) {
    const def = getDefaultValue(schemaAtPath);
    if (def.hasDefault) {
      return {
        path,
        fixType: "default",
        oldValue,
        newValue: def.value,
        confidence: "safe",
        message: `Applied schema default (coercion not possible)`,
      };
    }
  }

  return {
    path,
    fixType: "manual",
    oldValue,
    newValue: undefined,
    confidence: "uncertain",
    message: `Cannot coerce ${typeof oldValue} to ${targetType}`,
  };
}
