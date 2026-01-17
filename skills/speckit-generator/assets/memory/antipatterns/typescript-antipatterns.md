# TypeScript Anti-Patterns Reference

> **Purpose**: Detailed detection patterns and remediation for TypeScript anti-patterns
> **Parent**: `typescript.md` (Section 10)
> **Usage**: Reference for antipattern-detector agent and /lint command

---

## Detection Patterns

Use these regex/AST patterns to identify anti-patterns in code review:

### AP-TS-01: The `any` Escape Hatch

**Detection**:
```
Pattern: /:\s*any\b/g
Pattern: /as\s+any\b/g
Pattern: /<any>/g
```

**Severity**: HIGH
**Auto-fixable**: No (requires type inference)

**Context**: Acceptable in:
- Type definition files for untyped libraries
- Gradual migration from JavaScript
- Generic constraints where truly any type is valid

**Remediation Steps**:
1. Identify the actual data shape being passed
2. Create an interface or type alias
3. Replace `any` with the specific type
4. If unknown, use `unknown` and narrow with type guards

---

### AP-TS-02: Type Assertion Abuse

**Detection**:
```
Pattern: /as\s+\w+(?!\s*any)/g (followed by property access)
Pattern: /!\./g (non-null assertion before property access)
Pattern: /<[A-Z]\w*>\s*\w+\./g (angle-bracket assertion)
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Red Flags**:
- Chained assertions: `(x as Foo as Bar)`
- Assertion immediately before property access: `(data as User).name`
- Non-null assertion on potentially null values: `user!.profile!.name`

**Remediation Steps**:
1. Add proper null checks with narrowing
2. Use type guards for runtime validation
3. Refactor to return proper types from source functions

---

### AP-TS-03: Stringly-Typed Code

**Detection**:
```
Pattern: /:\s*string\s*[,)=]/ (string as parameter type for finite sets)
Pattern: /['"][a-z]+['"]\s*===?\s*\w+/ (string literal comparisons)
Pattern: /type\s+\w+\s*=\s*string/ (type alias to plain string)
```

**Severity**: MEDIUM
**Auto-fixable**: Partially (can suggest union types)

**Indicators**:
- Functions accepting `string` for status, mode, type parameters
- Switch statements on string values with default cases
- String comparisons for control flow

**Remediation Steps**:
1. Identify all valid string values
2. Create a union type: `type Status = 'active' | 'inactive' | 'pending'`
3. Update function signatures to use the union
4. Remove unnecessary default cases

---

### AP-TS-04: Interface Duplication

**Detection**:
```
Pattern: Similar interface names (e.g., User, UserData, UserInfo, UserDTO)
Pattern: Interfaces with >80% field overlap
Pattern: Multiple files defining same-shaped interfaces
```

**Severity**: LOW
**Auto-fixable**: No (requires architectural decision)

**Indicators**:
- Multiple interfaces with same fields, different names
- Copy-paste interfaces across files
- Interfaces that are subsets of others without using `Pick`/`Omit`

**Remediation Steps**:
1. Identify the canonical interface
2. Use utility types: `Pick<User, 'id' | 'name'>`, `Omit<User, 'password'>`
3. Use `extends` for true inheritance relationships
4. Consolidate into shared types file

---

### AP-TS-05: Type Ignorance (@ts-ignore abuse)

**Detection**:
```
Pattern: /@ts-ignore/g
Pattern: /@ts-expect-error(?!\s+\w)/g (without explanation)
Pattern: /\/\/\s*eslint-disable.*@typescript-eslint/g
```

**Severity**: HIGH
**Auto-fixable**: No

**Acceptable Uses**:
- `@ts-expect-error` with explanation for known library issues
- Temporary during migration with tracking issue
- Test files for intentional type errors

**Remediation Steps**:
1. Investigate the actual type error
2. Fix the underlying type issue
3. If truly unfixable, use `@ts-expect-error` with explanation
4. Track in tech debt backlog

---

### AP-TS-06: Promise Chain Confusion

**Detection**:
```
Pattern: /\.then\(.*\.then\(/g (nested then chains)
Pattern: /await.*\.then\(/g (mixing await and .then)
Pattern: /new Promise.*resolve\(.*await/g (unnecessary Promise wrapper)
```

**Severity**: MEDIUM
**Auto-fixable**: Partially

**Indicators**:
- Mixing `async/await` with `.then()` chains
- Nested `.then()` callbacks
- `new Promise()` wrapping existing promises
- Missing error handling in promise chains

**Remediation Steps**:
1. Convert `.then()` chains to `async/await`
2. Remove unnecessary `new Promise()` wrappers
3. Add proper try/catch blocks
4. Ensure consistent async pattern throughout function

---

### AP-TS-07: Generic Abuse

**Detection**:
```
Pattern: /<T>.*<T>.*<T>/g (excessive generic parameters)
Pattern: /<T extends any>/g
Pattern: /<T, U, V, W>/g (>3 type parameters)
Pattern: /generic.*generic/i in comments
```

**Severity**: LOW
**Auto-fixable**: No

**Indicators**:
- Functions with >3 generic type parameters
- Generic constraints that are always `any` or `unknown`
- Generics that could be concrete types
- Overly clever type gymnastics

**Remediation Steps**:
1. Consider if generics are truly needed
2. Use concrete types when possible
3. Break complex generics into simpler composed types
4. Document why generics are necessary

---

### AP-TS-08: Inconsistent Nullability

**Detection**:
```
Pattern: /\?\.\s*\w+\s*\?\./g (excessive optional chaining)
Pattern: /\|\s*null\s*\|\s*undefined/g
Pattern: /!== null && .* !== undefined/g
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Indicators**:
- Mixed use of `null` and `undefined`
- Excessive optional chaining (`?.?.?.`)
- Inconsistent null checks across codebase
- Properties that are `T | null | undefined`

**Remediation Steps**:
1. Decide on `null` vs `undefined` convention
2. Use `strictNullChecks` compiler option
3. Create type guards for null checking
4. Refactor APIs to be consistent

---

### AP-TS-09: Type Safety Illusion

**Detection**:
```
Pattern: /JSON\.parse\(/g without type validation
Pattern: /as\s+\w+.*JSON\.parse/g
Pattern: /fetch\(.*\).*as\s+\w+/g without validation
```

**Severity**: HIGH
**Auto-fixable**: No

**Indicators**:
- Casting `JSON.parse()` results directly to types
- Trusting external API responses without validation
- Type assertions on `any` from external sources

**Remediation Steps**:
1. Use runtime validation (zod, io-ts, yup)
2. Create type guards for external data
3. Never trust type assertions for external data
4. Add schema validation at system boundaries

---

### AP-TS-10: Inconsistent Naming

**Detection**:
```
Pattern: /^I[A-Z]/ for interfaces (Hungarian notation)
Pattern: Mixed camelCase/PascalCase/snake_case
Pattern: Inconsistent suffix usage (Service, Manager, Handler, Controller)
```

**Severity**: LOW
**Auto-fixable**: Yes (with rename refactoring)

**Conventions**:
- Interfaces: PascalCase without `I` prefix
- Types: PascalCase
- Variables/functions: camelCase
- Constants: SCREAMING_SNAKE_CASE
- Enums: PascalCase with PascalCase members

**Remediation Steps**:
1. Establish naming conventions in style guide
2. Configure ESLint naming-convention rule
3. Use IDE rename refactoring
4. Review in PR process

---

## Quick Reference Table

| Code | Name | Severity | Fixable |
|------|------|----------|---------|
| AP-TS-01 | `any` Escape Hatch | HIGH | No |
| AP-TS-02 | Type Assertion Abuse | MEDIUM | No |
| AP-TS-03 | Stringly-Typed Code | MEDIUM | Partial |
| AP-TS-04 | Interface Duplication | LOW | No |
| AP-TS-05 | Type Ignorance | HIGH | No |
| AP-TS-06 | Promise Chain Confusion | MEDIUM | Partial |
| AP-TS-07 | Generic Abuse | LOW | No |
| AP-TS-08 | Inconsistent Nullability | MEDIUM | No |
| AP-TS-09 | Type Safety Illusion | HIGH | No |
| AP-TS-10 | Inconsistent Naming | LOW | Yes |

---

## ESLint Rules for Detection

```json
{
  "@typescript-eslint/no-explicit-any": "error",
  "@typescript-eslint/no-non-null-assertion": "warn",
  "@typescript-eslint/consistent-type-assertions": "error",
  "@typescript-eslint/no-unnecessary-type-assertion": "error",
  "@typescript-eslint/prefer-nullish-coalescing": "warn",
  "@typescript-eslint/strict-boolean-expressions": "warn",
  "@typescript-eslint/naming-convention": "warn"
}
```
