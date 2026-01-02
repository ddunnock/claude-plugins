# TypeScript Standards

> **Applies to**: All TypeScript and JavaScript code in this project  
> **Version Constraint**: Node.js ≥20.0 LTS, TypeScript ≥5.0  
> **Parent**: `constitution.md`

---

## 1. Version and Runtime

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Node.js | ≥20.0 LTS | Native fetch, test runner, performance |
| TypeScript | ≥5.0 | Decorators, const type parameters |
| Module System | ESM | Native ES modules, better tree-shaking |

---

## 2. Package Management

### 2.1 pnpm Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```ini
# .npmrc
strict-peer-dependencies=true
auto-install-peers=true
shamefully-hoist=false
```

### 2.2 Package.json Standards

```json
{
  "name": "@project/package-name",
  "version": "0.1.0",
  "type": "module",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js"
    }
  },
  "scripts": {
    "build": "tsc",
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "typecheck": "tsc --noEmit"
  }
}
```

---

## 3. Documentation Standards

### 3.1 Module Documentation

Every file **SHOULD** have a module-level JSDoc:

```typescript
/**
 * Module-level description of file purpose and exports.
 *
 * @module ModuleName
 * @packageDocumentation
 */
```

### 3.2 Interface Documentation

```typescript
/**
 * Configuration options for the component.
 *
 * @interface ComponentConfig
 * @property {string} id - Unique identifier for the component
 * @property {string} [label] - Optional display label
 * @property {boolean} [disabled=false] - Whether the component is disabled
 */
export interface ComponentConfig {
  /** Unique identifier for the component */
  id: string;
  /** Optional display label */
  label?: string;
  /**
   * Whether the component is disabled
   * @default false
   */
  disabled?: boolean;
}
```

### 3.3 Function Documentation

```typescript
/**
 * Processes input data and returns transformed result.
 *
 * This function applies [algorithm/transformation] to the input
 * data, handling edge cases for [scenarios].
 *
 * @template T - The type of items in the input array
 * @param {T[]} items - Array of items to process
 * @param {object} options - Processing options
 * @param {boolean} [options.strict=true] - Enable strict validation
 * @param {number} [options.limit] - Maximum items to process
 * @returns {Promise<ProcessedResult<T>>} The processed result
 * @throws {ValidationError} When items fail validation in strict mode
 * @throws {RangeError} When limit is negative
 *
 * @example
 * // Basic usage
 * const result = await processData([1, 2, 3]);
 *
 * @example
 * // With options
 * const result = await processData(items, {
 *   strict: false,
 *   limit: 100
 * });
 *
 * @since 1.0.0
 * @public
 */
export async function processData<T>(
  items: T[],
  options: { strict?: boolean; limit?: number } = {}
): Promise<ProcessedResult<T>> {
  // Implementation
}
```

### 3.4 React Hook Documentation

```typescript
/**
 * Custom hook for managing component state with persistence.
 *
 * This hook provides [functionality] with automatic persistence
 * to [storage mechanism]. It handles [edge cases].
 *
 * @template T - The type of the state value
 * @param {string} key - Storage key for persistence
 * @param {T} initialValue - Initial state value
 * @returns {readonly [T, (value: T) => void, () => void]} Tuple of [state, setState, resetState]
 *
 * @example
 * const [value, setValue, reset] = usePersistedState("key", defaultValue);
 *
 * @hook
 * @public
 */
export function usePersistedState<T>(
  key: string,
  initialValue: T
): readonly [T, (value: T) => void, () => void] {
  // Implementation
}
```

---

## 4. Type Safety

### 4.1 tsconfig.json

```json
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "jsx": "preserve",
    "incremental": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 4.2 Required Compiler Options

These options **MUST** be enabled:

| Option | Purpose |
|--------|---------|
| `strict` | Enables all strict type checking options |
| `noUncheckedIndexedAccess` | Adds `undefined` to index signatures |
| `noImplicitReturns` | Ensures all code paths return |
| `noFallthroughCasesInSwitch` | Prevents switch fallthrough bugs |
| `noImplicitOverride` | Requires explicit `override` keyword |
| `exactOptionalPropertyTypes` | Distinguishes `undefined` from missing |
| `verbatimModuleSyntax` | Enforces explicit type imports |

---

## 5. Linting and Formatting

### 5.1 Biome Configuration

```json
{
  "$schema": "https://biomejs.dev/schemas/2.3.0/schema.json",
  "organizeImports": {
    "enabled": true
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedImports": "error",
        "noUnusedVariables": "error"
      },
      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      }
    }
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "double",
      "trailingCommas": "es5",
      "semicolons": "always"
    }
  },
  "json": {
    "formatter": {
      "trailingCommas": "none"
    }
  }
}
```

### 5.2 Import Organization

Imports **MUST** be organized in this order:

1. Node.js built-ins
2. External packages
3. Internal packages (`@project/*`)
4. Relative imports (parent directories first)
5. Type imports (at end of each group)

```typescript
import { readFile } from "node:fs/promises";

import { z } from "zod";
import { describe, it, expect } from "vitest";

import { Button } from "@project/ui";
import { cn } from "@project/utils";

import { UserService } from "../services/user-service";
import { validateInput } from "./helpers";

import type { User } from "@project/types";
import type { Config } from "./types";
```

---

## 6. Testing

### 6.1 Test Structure

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx      # Co-located unit tests
├── lib/
│   ├── utils.ts
│   └── utils.test.ts
└── __tests__/               # Integration tests
    └── api.test.ts
```

### 6.2 Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov", "html"],
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 85,
        statements: 80,
      },
      exclude: [
        "node_modules/",
        "**/*.d.ts",
        "**/*.config.*",
        "**/types/**",
      ],
    },
  },
});
```

### 6.3 Test Pattern

```typescript
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Button } from "./Button";

describe("Button", () => {
  describe("rendering", () => {
    it("renders children correctly", () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole("button")).toHaveTextContent("Click me");
    });

    it("applies variant classes", () => {
      render(<Button variant="outline">Outline</Button>);
      expect(screen.getByRole("button")).toHaveClass("border");
    });
  });

  describe("interactions", () => {
    it("calls onClick handler when clicked", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Click me</Button>);
      await user.click(screen.getByRole("button"));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("does not call onClick when disabled", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick} disabled>Disabled</Button>);
      await user.click(screen.getByRole("button"));

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe("accessibility", () => {
    it("is focusable via keyboard", async () => {
      const user = userEvent.setup();
      render(<Button>Focusable</Button>);

      await user.tab();
      expect(screen.getByRole("button")).toHaveFocus();
    });
  });
});
```

---

## 7. Error Handling

### 7.1 Custom Error Classes

```typescript
/**
 * Base error class for application errors.
 */
export class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = "AppError";
  }
}

/**
 * Error thrown when validation fails.
 */
export class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly errors: Record<string, string[]>
  ) {
    super(message, "VALIDATION_ERROR", 400);
    this.name = "ValidationError";
  }
}

/**
 * Error thrown when a resource is not found.
 */
export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id '${id}' not found`, "NOT_FOUND", 404);
    this.name = "NotFoundError";
  }
}
```

### 7.2 Result Pattern (Optional)

For functions that can fail predictably:

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function parseConfig(input: string): Result<Config, ValidationError> {
  try {
    const parsed = JSON.parse(input);
    const validated = configSchema.parse(parsed);
    return { success: true, data: validated };
  } catch (error) {
    return {
      success: false,
      error: new ValidationError("Invalid config", { config: [String(error)] }),
    };
  }
}

// Usage
const result = parseConfig(input);
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error.message);
}
```

---

## 8. Async Patterns

### 8.1 Promise Handling

```typescript
// ❌ Bad - unhandled rejection
async function bad() {
  fetchData(); // Promise not awaited
}

// ✅ Good - properly awaited
async function good() {
  await fetchData();
}

// ✅ Good - explicitly fire-and-forget with error handling
function fireAndForget() {
  void fetchData().catch(console.error);
}
```

### 8.2 Concurrent Operations

```typescript
// ❌ Bad - sequential when could be parallel
async function sequential() {
  const a = await fetchA();
  const b = await fetchB();
  return [a, b];
}

// ✅ Good - parallel execution
async function parallel() {
  const [a, b] = await Promise.all([fetchA(), fetchB()]);
  return [a, b];
}

// ✅ Good - with error handling
async function parallelWithHandling() {
  const results = await Promise.allSettled([fetchA(), fetchB()]);
  return results
    .filter((r): r is PromiseFulfilledResult<Data> => r.status === "fulfilled")
    .map((r) => r.value);
}
```

---

## 9. Zod Schema Patterns

### 9.1 Schema Definition

```typescript
import { z } from "zod";

/**
 * Schema for creating a new resource.
 */
export const createResourceSchema = z.object({
  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be 100 characters or less"),
  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional(),
  tags: z
    .array(z.string())
    .max(10, "Maximum 10 tags allowed")
    .default([]),
});

export type CreateResourceInput = z.infer<typeof createResourceSchema>;

/**
 * Schema for resource response.
 */
export const resourceSchema = createResourceSchema.extend({
  id: z.string().uuid(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

export type Resource = z.infer<typeof resourceSchema>;
```

### 9.2 Validation

```typescript
function validateInput<T>(schema: z.ZodSchema<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    throw new ValidationError(
      "Validation failed",
      result.error.flatten().fieldErrors
    );
  }
  return result.data;
}
```
