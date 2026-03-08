import { test, expect, describe } from "bun:test";
import {
  validatePath,
  PathValidationError,
} from "../../src/security/path-validator.ts";
import path from "node:path";

describe("validatePath", () => {
  const testDir = path.resolve("/tmp/sv-test-path-validator");

  test("valid path within allowed dir returns resolved absolute path", () => {
    const result = validatePath("/tmp/sv-test-path-validator/file.json", [
      testDir,
    ]);
    expect(result).toBe(path.resolve("/tmp/sv-test-path-validator/file.json"));
  });

  test("relative path within allowed dir resolves correctly", () => {
    // Use cwd as allowed dir so a relative path inside it works
    const cwd = process.cwd();
    const result = validatePath("./package.json", [cwd]);
    expect(result).toBe(path.resolve(cwd, "package.json"));
  });

  test("path with ../ traversal throws ERR_PATH_TRAVERSAL", () => {
    expect(() =>
      validatePath("../../../etc/passwd", [testDir]),
    ).toThrow(PathValidationError);

    try {
      validatePath("../../../etc/passwd", [testDir]);
    } catch (err) {
      expect(err).toBeInstanceOf(PathValidationError);
      expect((err as PathValidationError).code).toBe("ERR_PATH_TRAVERSAL");
    }
  });

  test("path with null byte throws ERR_NULL_BYTE", () => {
    expect(() =>
      validatePath("file\0.json", [testDir]),
    ).toThrow(PathValidationError);

    try {
      validatePath("file\0.json", [testDir]);
    } catch (err) {
      expect(err).toBeInstanceOf(PathValidationError);
      expect((err as PathValidationError).code).toBe("ERR_NULL_BYTE");
    }
  });

  test("path outside allowed dirs throws ERR_PATH_TRAVERSAL", () => {
    expect(() =>
      validatePath("/outside/file.json", [testDir]),
    ).toThrow(PathValidationError);

    try {
      validatePath("/outside/file.json", [testDir]);
    } catch (err) {
      expect(err).toBeInstanceOf(PathValidationError);
      expect((err as PathValidationError).code).toBe("ERR_PATH_TRAVERSAL");
    }
  });

  test("error message includes the rejected path", () => {
    try {
      validatePath("/evil/path.json", [testDir]);
    } catch (err) {
      expect((err as PathValidationError).message).toContain("/evil/path.json");
      expect((err as PathValidationError).rejectedPath).toBe("/evil/path.json");
    }
  });

  test("multiple allowed dirs: path valid in second dir succeeds", () => {
    const result = validatePath("/tmp/sv-test-path-validator/file.json", [
      "/some/other/dir",
      testDir,
    ]);
    expect(result).toBe(path.resolve("/tmp/sv-test-path-validator/file.json"));
  });

  test("default allowed dir is process.cwd()", () => {
    const cwd = process.cwd();
    const result = validatePath("./package.json");
    expect(result).toBe(path.resolve(cwd, "package.json"));
  });

  test("empty allowedDirs array throws", () => {
    expect(() => validatePath("/any/file.json", [])).toThrow();
  });
});
