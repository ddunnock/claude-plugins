# Rust Anti-Patterns Reference

> **Purpose**: Detailed detection patterns and remediation for Rust anti-patterns
> **Parent**: `rust.md` (Section 9)
> **Usage**: Reference for antipattern-detector agent and /lint command

---

## Detection Patterns

Use these patterns to identify anti-patterns in code review:

### AP-RS-01: Using `.unwrap()` in Library Code

**Detection**:
```rust
Pattern: /\.unwrap\(\)/g
Pattern: /\.expect\(/g
```

**Severity**: HIGH
**Auto-fixable**: No

**Acceptable Uses**:
- Tests and examples
- After explicit checks that guarantee success
- `main()` function with explicit error documentation
- Truly impossible states with `unreachable!()` comment

**Remediation**:
```rust
// ❌ Bad - Panics on None/Err
let value = some_option.unwrap();
let result = fallible_op().expect("should work");

// ✅ Good - Propagate errors
let value = some_option.ok_or(MyError::NotFound)?;
let result = fallible_op()?;

// ✅ With context
let result = fallible_op()
    .map_err(|e| MyError::Operation { source: e })?;
```

---

### AP-RS-02: Ignoring Clippy Lints

**Detection**:
```rust
Pattern: /#\[allow\(clippy::all\)\]/g
Pattern: /#\[allow\(clippy::\w+\)\]/ without justification comment
Pattern: /#!\[allow\(clippy::/g (crate-level allows)
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Acceptable Uses**:
- With `// Reason:` comment explaining why
- For specific false positives in context
- Never for `clippy::all` or crate-level

**Remediation**:
```rust
// ❌ Bad - Blanket allow
#[allow(clippy::all)]
fn messy_function() { ... }

// ❌ Bad - No explanation
#[allow(clippy::too_many_arguments)]
fn many_args(a: i32, b: i32, c: i32, d: i32, e: i32) { ... }

// ✅ Good - Justified exception
#[allow(clippy::too_many_arguments)]
// Reason: Builder pattern requires passing all config options
fn build_complex_object(/* ... */) { ... }
```

---

### AP-RS-03: `clone()` to Satisfy Borrow Checker

**Detection**:
```rust
Pattern: /\.clone\(\)/ preceded by borrow error comment
Pattern: Multiple `.clone()` in same function on same value
Pattern: `.clone()` immediately before function that takes reference
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Indicators**:
- Cloning just before passing to function
- Cloning in loops
- Cloning expensive types (Vec, String, HashMap)

**Remediation**:
```rust
// ❌ Bad - Unnecessary clone
let data = expensive_data.clone();
process(&data);
other_process(&expensive_data);

// ✅ Good - Restructure borrows
process(&expensive_data);
other_process(&expensive_data);

// ✅ If shared ownership needed
let data = Arc::new(expensive_data);
let data_clone = Arc::clone(&data);
```

---

### AP-RS-04: Using `String` When `&str` Suffices

**Detection**:
```rust
Pattern: /fn\s+\w+\([^)]*:\s*String[^)]*\)/ (String in parameters)
Pattern: /fn\s+\w+\([^)]*:\s*Vec<\w+>[^)]*\)/ for read-only use
```

**Severity**: LOW
**Auto-fixable**: Yes

**Rule**: Accept borrowed data, return owned data

**Remediation**:
```rust
// ❌ Bad - Forces allocation
fn greet(name: String) {
    println!("Hello, {name}");
}

// ✅ Good - Accepts any string-like
fn greet(name: &str) {
    println!("Hello, {name}");
}

// ✅ For generic string types
fn greet(name: impl AsRef<str>) {
    println!("Hello, {}", name.as_ref());
}
```

---

### AP-RS-05: Manual Error Type Definition

**Detection**:
```rust
Pattern: /impl\s+From<\w+Error>\s+for\s+\w+Error/g
Pattern: /impl\s+std::error::Error\s+for/g
Pattern: /impl\s+Display\s+for.*Error/g
```

**Severity**: LOW
**Auto-fixable**: Yes

**Remediation**:
```rust
// ❌ Bad - Manual boilerplate
enum MyError {
    Io(io::Error),
    Parse(ParseError),
}
impl From<io::Error> for MyError {
    fn from(e: io::Error) -> Self { MyError::Io(e) }
}
impl Display for MyError { ... }
impl Error for MyError { ... }

// ✅ Good - Use thiserror
use thiserror::Error;

#[derive(Debug, Error)]
enum MyError {
    #[error("I/O error: {0}")]
    Io(#[from] io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] ParseError),
}
```

---

### AP-RS-06: `Box<dyn Error>` Everywhere

**Detection**:
```rust
Pattern: /Box<dyn\s+(std::)?error::Error/g
Pattern: /Result<\w+,\s*Box<dyn\s+Error/g
```

**Severity**: MEDIUM
**Auto-fixable**: No

**Why It's Wrong**:
- Loses type information
- Can't match on error variants
- Heap allocation overhead
- Poor API ergonomics

**Remediation**:
```rust
// ❌ Bad - Type erasure
fn process() -> Result<(), Box<dyn Error>> { ... }

// ✅ Good - Library code
fn process() -> Result<(), MyError> { ... }

// ✅ Good - Application code with anyhow
fn process() -> anyhow::Result<()> { ... }
```

---

### AP-RS-07: Blocking in Async Context

**Detection**:
```rust
Pattern: /async\s+fn.*std::fs::/g
Pattern: /async\s+fn.*std::thread::sleep/g
Pattern: /async\s+fn.*\.read\(/ (sync I/O in async)
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Dangerous**:
- Blocks entire async runtime thread
- Causes timeouts and deadlocks
- Defeats purpose of async

**Remediation**:
```rust
// ❌ Bad - Blocks runtime
async fn read_file(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap()
}

// ✅ Good - Async I/O
async fn read_file(path: &Path) -> Result<String, io::Error> {
    tokio::fs::read_to_string(path).await
}

// ✅ For CPU-bound work
async fn heavy_compute(data: Vec<u8>) -> Result<Output, Error> {
    tokio::task::spawn_blocking(move || {
        cpu_intensive_work(&data)
    }).await?
}
```

---

### AP-RS-08: Not Using `?` Operator

**Detection**:
```rust
Pattern: /match.*Ok\(.*\).*Err\(.*return\s+Err/g
Pattern: /if\s+let\s+Err\(e\)\s*=.*return\s+Err/g
```

**Severity**: LOW
**Auto-fixable**: Yes

**Remediation**:
```rust
// ❌ Bad - Verbose
let value = match some_result {
    Ok(v) => v,
    Err(e) => return Err(e.into()),
};

// ✅ Good
let value = some_result?;

// ✅ With context (using anyhow)
let value = some_result.context("failed to get value")?;
```

---

### AP-RS-09: Mutable Global State

**Detection**:
```rust
Pattern: /static\s+mut\s+/g
Pattern: /lazy_static!\s*\{[^}]*Mutex<[^}]*mut/g
```

**Severity**: HIGH
**Auto-fixable**: No

**Why It's Dangerous**:
- Requires `unsafe` to access
- Data races possible
- Hard to test
- Hidden dependencies

**Remediation**:
```rust
// ❌ Bad - Mutable static
static mut COUNTER: i32 = 0;

unsafe {
    COUNTER += 1;  // Data race!
}

// ✅ Good - Atomic
use std::sync::atomic::{AtomicI32, Ordering};
static COUNTER: AtomicI32 = AtomicI32::new(0);
COUNTER.fetch_add(1, Ordering::SeqCst);

// ✅ Good - Thread-local
thread_local! {
    static COUNTER: Cell<i32> = Cell::new(0);
}

// ✅ Good - OnceCell for lazy init
use std::sync::OnceLock;
static CONFIG: OnceLock<Config> = OnceLock::new();
```

---

### AP-RS-10: Ignoring `#[must_use]` Results

**Detection**:
```rust
Pattern: /^\s*\w+\.\w+\([^)]*\);\s*$/g (method call as statement)
Pattern: Compiler warnings about unused Result/Option
```

**Severity**: HIGH
**Auto-fixable**: No

**Common Offenders**:
- `Result` from fallible operations
- `Option` from methods like `HashMap::insert`
- Channel `send` results
- `JoinHandle` from spawned tasks

**Remediation**:
```rust
// ❌ Bad - Silent failure
let _ = channel.send(message);

// ✅ Good - Handle error
channel.send(message).expect("channel closed");

// ✅ Good - Log and continue
if let Err(e) = channel.send(message) {
    tracing::warn!("Failed to send: {e}");
}

// ✅ Good - Explicit ignore with reason
let _ = channel.send(message); // Best effort, receiver may be gone
```

---

## Quick Reference Table

| Code | Name | Severity | Fixable |
|------|------|----------|---------|
| AP-RS-01 | `.unwrap()` in Library Code | HIGH | No |
| AP-RS-02 | Ignoring Clippy Lints | MEDIUM | No |
| AP-RS-03 | `clone()` for Borrow Checker | MEDIUM | No |
| AP-RS-04 | `String` vs `&str` | LOW | Yes |
| AP-RS-05 | Manual Error Types | LOW | Yes |
| AP-RS-06 | `Box<dyn Error>` Everywhere | MEDIUM | No |
| AP-RS-07 | Blocking in Async | HIGH | No |
| AP-RS-08 | Not Using `?` Operator | LOW | Yes |
| AP-RS-09 | Mutable Global State | HIGH | No |
| AP-RS-10 | Ignoring `#[must_use]` | HIGH | No |

---

## Clippy Configuration

```toml
# Cargo.toml
[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
unwrap_used = "deny"
expect_used = "warn"
panic = "deny"
todo = "warn"
dbg_macro = "warn"
```

---

## Cargo.toml Lint Setup

```toml
[lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[lints.clippy]
all = "warn"
pedantic = "warn"
```
