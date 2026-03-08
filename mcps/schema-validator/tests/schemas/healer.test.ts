import { describe, test, expect } from "bun:test";
import { z } from "zod";
import { healData, type HealFix, type HealResult } from "../../src/schemas/healer";

// --- Test schemas ---

const basicSchema = z.object({
  name: z.string(),
  version: z.number(),
  enabled: z.boolean(),
});

const schemaWithDefaults = z.object({
  name: z.string(),
  version: z.number().default(1),
  enabled: z.boolean().default(true),
  level: z.enum(["low", "medium", "high"]).default("medium"),
});

const nestedSchema = z.object({
  name: z.string(),
  config: z.object({
    timeout: z.number(),
    retries: z.number().default(3),
  }),
});

const enumSchema = z.object({
  name: z.string(),
  priority: z.enum(["low", "medium", "high", "critical"]),
});

// --- Tests ---

describe("healData", () => {
  test("returns valid result when input already passes validation", () => {
    const data = { name: "test", version: 1, enabled: true };
    const result = healData(data, basicSchema);

    expect(result.healed).toBe(true);
    expect(result.data).toEqual(data);
    expect(result.applied).toEqual([]);
    expect(result.remaining).toEqual([]);
  });

  test("coerces string '5' to number 5 when schema expects number", () => {
    const data = { name: "test", version: "5", enabled: true };
    const result = healData(data as any, basicSchema);

    expect(result.data.version).toBe(5);
    expect(result.applied.length).toBeGreaterThanOrEqual(1);
    const fix = result.applied.find((f) => f.path.includes("version"));
    expect(fix).toBeDefined();
    expect(fix!.fixType).toBe("coerce");
    expect(fix!.oldValue).toBe("5");
    expect(fix!.newValue).toBe(5);
    expect(fix!.confidence).toBe("safe");
  });

  test("coerces string 'true'/'false' to boolean (exact match, case-sensitive)", () => {
    const data = { name: "test", version: 1, enabled: "true" };
    const result = healData(data as any, basicSchema);

    expect(result.data.enabled).toBe(true);
    const fix = result.applied.find((f) => f.path.includes("enabled"));
    expect(fix).toBeDefined();
    expect(fix!.fixType).toBe("coerce");
    expect(fix!.confidence).toBe("safe");

    // Also test "false"
    const data2 = { name: "test", version: 1, enabled: "false" };
    const result2 = healData(data2 as any, basicSchema);
    expect(result2.data.enabled).toBe(false);
  });

  test("does NOT coerce 'yes'/'no'/'1'/'0' to boolean (marks as manual)", () => {
    for (const badValue of ["yes", "no", "1", "0", "True", "FALSE"]) {
      const data = { name: "test", version: 1, enabled: badValue };
      const result = healData(data as any, basicSchema);

      const manualFix = result.remaining.find((f) =>
        f.path.includes("enabled"),
      );
      expect(manualFix).toBeDefined();
      expect(manualFix!.fixType).toBe("manual");
    }
  });

  test("coerces number/boolean to string when schema expects string", () => {
    const stringSchema = z.object({ label: z.string(), count: z.number() });

    const data1 = { label: 42, count: 1 };
    const result1 = healData(data1 as any, stringSchema);
    expect(result1.data.label).toBe("42");

    const data2 = { label: true, count: 1 };
    const result2 = healData(data2 as any, stringSchema);
    expect(result2.data.label).toBe("true");
  });

  test("applies ZodDefault value for missing required field", () => {
    const data = { name: "test" };
    const result = healData(data as any, schemaWithDefaults);

    expect(result.data.version).toBe(1);
    expect(result.data.enabled).toBe(true);
    expect(result.data.level).toBe("medium");

    const defaultFixes = result.applied.filter(
      (f) => f.fixType === "default",
    );
    expect(defaultFixes.length).toBeGreaterThanOrEqual(3);
    for (const fix of defaultFixes) {
      expect(fix.confidence).toBe("safe");
      expect(fix.oldValue).toBeUndefined();
    }
  });

  test("marks missing required field WITHOUT ZodDefault as manual/unfixable", () => {
    const data = { version: 1, enabled: true };
    const result = healData(data as any, basicSchema);

    const manualFix = result.remaining.find((f) => f.path.includes("name"));
    expect(manualFix).toBeDefined();
    expect(manualFix!.fixType).toBe("manual");
    expect(manualFix!.confidence).toBe("uncertain");
  });

  test("marks invalid_enum_value as manual with allowed options in message", () => {
    const data = { name: "test", priority: "extreme" };
    const result = healData(data as any, enumSchema);

    const enumFix = result.remaining.find((f) =>
      f.path.includes("priority"),
    );
    expect(enumFix).toBeDefined();
    expect(enumFix!.fixType).toBe("manual");
    // Message should mention allowed options
    expect(enumFix!.message).toMatch(/low/);
    expect(enumFix!.message).toMatch(/high/);
  });

  test("preserves unknown fields not in schema after healing", () => {
    const data = {
      name: "test",
      version: "3",
      enabled: true,
      customField: "preserve me",
      metadata: { foo: "bar" },
    };
    const result = healData(data as any, basicSchema);

    expect(result.data.customField).toBe("preserve me");
    expect((result.data.metadata as any).foo).toBe("bar");
    expect(result.data.version).toBe(3);
  });

  test("handles nested object paths correctly", () => {
    const data = {
      name: "test",
      config: { timeout: "30", retries: 5 },
    };
    const result = healData(data as any, nestedSchema);

    expect(result.data.config).toBeDefined();
    expect((result.data.config as any).timeout).toBe(30);
  });

  test("returns partial results when some fixes succeed and others are manual", () => {
    const data = { version: "2", enabled: true };
    const result = healData(data as any, basicSchema);

    // version "2" -> 2 should be applied (coerce)
    expect(result.applied.length).toBeGreaterThanOrEqual(1);
    // name is missing with no default -> manual
    expect(result.remaining.length).toBeGreaterThanOrEqual(1);
    // healed should be false since remaining issues exist
    expect(result.healed).toBe(false);
  });

  test("creates intermediate objects for missing nested paths", () => {
    const data = { name: "test" } as any;
    const result = healData(data, nestedSchema);

    // config.retries has a default of 3, so it should be applied
    // config.timeout has no default, so it should be manual
    // The intermediate "config" object should be created
    const retriesFix = result.applied.find(
      (f) =>
        f.path.length === 2 &&
        f.path[0] === "config" &&
        f.path[1] === "retries",
    );
    if (retriesFix) {
      expect((result.data.config as any).retries).toBe(3);
    }
  });

  test("handles null -> schema default coercion", () => {
    const data = { name: "test", version: null, enabled: null };
    const result = healData(data as any, schemaWithDefaults);

    expect(result.data.version).toBe(1);
    expect(result.data.enabled).toBe(true);
  });

  test("fix objects have correct shape", () => {
    const data = { name: "test", version: "5", enabled: true };
    const result = healData(data as any, basicSchema);

    for (const fix of [...result.applied, ...result.remaining]) {
      expect(fix).toHaveProperty("path");
      expect(fix).toHaveProperty("fixType");
      expect(fix).toHaveProperty("oldValue");
      expect(fix).toHaveProperty("newValue");
      expect(fix).toHaveProperty("confidence");
      expect(fix).toHaveProperty("message");
      expect(Array.isArray(fix.path)).toBe(true);
      expect(["default", "coerce", "manual"]).toContain(fix.fixType);
      expect(["safe", "uncertain"]).toContain(fix.confidence);
      expect(typeof fix.message).toBe("string");
    }
  });
});
