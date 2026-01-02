# Rust Standards

> **Applies to**: All Rust code in this project  
> **Version Constraint**: ≥1.75 (stable)  
> **Parent**: `constitution.md`

---

## 1. Version and Toolchain

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Minimum Version | 1.75 | Async trait stability, RPITIT |
| Channel | stable | No nightly features without ADR |
| Edition | 2021 | Current stable edition |

---

## 2. Project Structure

### 2.1 Workspace Layout

```
crates/
├── core/                   # Core domain logic
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── models/
│       │   ├── mod.rs
│       │   └── resource.rs
│       └── services/
│           ├── mod.rs
│           └── resource_service.rs
├── shared/                 # Shared utilities
│   ├── Cargo.toml
│   └── src/
│       └── lib.rs
└── cli/                    # CLI application
    ├── Cargo.toml
    └── src/
        ├── main.rs
        └── commands/
            ├── mod.rs
            └── run.rs
```

### 2.2 Workspace Cargo.toml

```toml
[workspace]
resolver = "2"
members = ["crates/*"]

[workspace.package]
version = "0.1.0"
edition = "2021"
authors = ["Author <author@example.com>"]
license = "MIT"

[workspace.dependencies]
# Shared dependencies with versions
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
thiserror = "1.0"
anyhow = "1.0"

[workspace.lints.rust]
unsafe_code = "forbid"
missing_docs = "warn"

[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
unwrap_used = "deny"
expect_used = "warn"
panic = "deny"
```

### 2.3 Crate Cargo.toml

```toml
[package]
name = "crate-name"
version.workspace = true
edition.workspace = true
authors.workspace = true

[dependencies]
tokio.workspace = true
serde.workspace = true

[lints]
workspace = true
```

---

## 3. Documentation Standards

### 3.1 Module Documentation

Every module **MUST** have module-level documentation:

```rust
//! Module-level documentation describing purpose and contents.
//!
//! This module provides [functionality] for [use case].
//!
//! # Examples
//!
//! ```rust
//! use crate::module::function;
//!
//! let result = function(arg)?;
//! assert_eq!(result, expected);
//! ```
//!
//! # Features
//!
//! - Feature 1: Description
//! - Feature 2: Description
//!
//! # Panics
//!
//! This module does not panic under normal operation.
//!
//! # Safety
//!
//! All public functions in this module are safe to call.
```

### 3.2 Function Documentation

```rust
/// Processes the input data according to the provided configuration.
///
/// This function applies [algorithm] to transform the input data,
/// respecting the constraints specified in `config`.
///
/// # Arguments
///
/// * `data` - A slice of items to process. Can be empty.
/// * `config` - Configuration controlling processing behavior.
///
/// # Returns
///
/// Returns `Ok(ProcessedResult)` containing the transformed data,
/// or `Err(ModuleError)` if processing fails.
///
/// # Errors
///
/// This function returns an error if:
///
/// * The input contains invalid items and `config.strict` is `true`
/// * The operation exceeds `config.timeout_ms`
/// * An I/O error occurs during processing
///
/// # Panics
///
/// This function does not panic.
///
/// # Examples
///
/// ```rust
/// use crate::module::{process_data, Config};
///
/// let config = Config::default();
/// let data = vec![1, 2, 3, 4, 5];
///
/// let result = process_data(&data, &config)?;
/// assert_eq!(result.count, 5);
/// ```
///
/// # Performance
///
/// Time complexity: O(n) where n is the length of `data`.
/// Space complexity: O(n) for the result buffer.
///
/// # See Also
///
/// * [`Config`] - Configuration options
/// * [`ProcessedResult`] - Result structure
pub fn process_data(data: &[i32], config: &Config) -> Result<ProcessedResult, ModuleError> {
    // Implementation
}
```

### 3.3 Struct Documentation

```rust
/// Configuration for the processing pipeline.
///
/// This struct holds all configuration options for [`process_data`].
///
/// # Examples
///
/// ```rust
/// use crate::module::Config;
///
/// let config = Config::builder()
///     .max_items(100)
///     .strict(true)
///     .build()?;
/// ```
///
/// # Default Values
///
/// | Field | Default |
/// |-------|---------|
/// | `max_items` | `1000` |
/// | `strict` | `false` |
/// | `timeout_ms` | `5000` |
#[derive(Debug, Clone, PartialEq)]
pub struct Config {
    /// Maximum number of items to process.
    ///
    /// Must be greater than 0.
    pub max_items: usize,

    /// Enable strict validation mode.
    ///
    /// When `true`, invalid items cause immediate failure.
    /// When `false`, invalid items are skipped with a warning.
    pub strict: bool,

    /// Operation timeout in milliseconds.
    ///
    /// Set to `0` for no timeout.
    pub timeout_ms: u64,
}
```

### 3.4 Enum Documentation

```rust
/// Error type for operations in this module.
///
/// This enum represents all possible errors that can occur
/// during [operations].
///
/// # Examples
///
/// ```rust
/// use crate::module::ModuleError;
///
/// fn fallible_operation() -> Result<(), ModuleError> {
///     Err(ModuleError::InvalidInput("reason".into()))
/// }
/// ```
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ModuleError {
    /// The input provided was invalid.
    ///
    /// Contains a description of why the input was invalid.
    InvalidInput(String),

    /// The requested resource was not found.
    ///
    /// Contains the identifier of the missing resource.
    NotFound(String),

    /// An I/O error occurred.
    Io(String),
}
```

---

## 4. Type Safety and Linting

### 4.1 Clippy Configuration

```toml
# clippy.toml
cognitive-complexity-threshold = 25
too-many-arguments-threshold = 7
```

### 4.2 Required Lints

```toml
# Cargo.toml [workspace.lints.clippy]
[workspace.lints.clippy]
all = "warn"
pedantic = "warn"
nursery = "warn"
cargo = "warn"
unwrap_used = "deny"
expect_used = "warn"
panic = "deny"
todo = "warn"
dbg_macro = "warn"
print_stdout = "warn"
print_stderr = "warn"
```

### 4.3 rustfmt Configuration

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
use_small_heuristics = "Max"
imports_granularity = "Module"
group_imports = "StdExternalCrate"
reorder_imports = true
reorder_modules = true
```

---

## 5. Error Handling

### 5.1 Error Type Pattern

Use `thiserror` for library errors:

```rust
use thiserror::Error;

/// Errors that can occur in this module.
#[derive(Debug, Error)]
pub enum ModuleError {
    /// Invalid input was provided.
    #[error("invalid input: {0}")]
    InvalidInput(String),

    /// The requested resource was not found.
    #[error("resource not found: {0}")]
    NotFound(String),

    /// An I/O error occurred.
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    /// A configuration error occurred.
    #[error("configuration error: {0}")]
    Config(String),
}
```

### 5.2 Result Handling

**MUST NOT** use `.unwrap()` or `.expect()` in library code. Use proper error propagation:

```rust
// ❌ Bad
let value = some_option.unwrap();
let result = fallible_operation().expect("should work");

// ✅ Good
let value = some_option.ok_or(ModuleError::NotFound("value".into()))?;
let result = fallible_operation()?;

// ✅ Also acceptable for truly impossible states (with comment)
let value = some_option.unwrap_or_else(|| {
    // SAFETY: This is guaranteed to be Some by [invariant]
    unreachable!("value is always initialized before this point")
});
```

---

## 6. Testing

### 6.1 Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    /// Test fixtures for common test data.
    mod fixtures {
        use super::*;

        pub fn sample_config() -> Config {
            Config {
                max_items: 100,
                strict: true,
                timeout_ms: 5000,
            }
        }

        pub fn sample_data() -> Vec<i32> {
            vec![1, 2, 3, 4, 5]
        }
    }

    mod process_data_tests {
        use super::*;

        #[test]
        fn processes_valid_data_successfully() {
            // Arrange
            let config = fixtures::sample_config();
            let data = fixtures::sample_data();

            // Act
            let result = process_data(&data, &config);

            // Assert
            assert!(result.is_ok());
            let processed = result.unwrap();
            assert_eq!(processed.count, 5);
        }

        #[test]
        fn handles_empty_input() {
            // Arrange
            let config = fixtures::sample_config();
            let data: Vec<i32> = vec![];

            // Act
            let result = process_data(&data, &config);

            // Assert
            assert!(result.is_ok());
            assert!(result.unwrap().items.is_empty());
        }

        #[test]
        fn returns_error_for_invalid_input_in_strict_mode() {
            // Arrange
            let config = Config {
                strict: true,
                ..fixtures::sample_config()
            };
            let data = vec![-1, 0, 1];

            // Act
            let result = process_data(&data, &config);

            // Assert
            assert!(matches!(result, Err(ModuleError::InvalidInput(_))));
        }
    }
}
```

### 6.2 Integration Tests

```rust
// tests/integration_test.rs
use crate_name::{process_data, Config};

#[tokio::test]
async fn end_to_end_processing_workflow() {
    // Arrange
    let config = Config::default();
    let input_data = generate_test_data(1000);

    // Act
    let result = process_data_async(&input_data, &config).await;

    // Assert
    assert!(result.is_ok());
    let processed = result.unwrap();
    assert_eq!(processed.count, 1000);
}
```

### 6.3 Coverage Enforcement

```bash
# Install cargo-llvm-cov
cargo install cargo-llvm-cov

# Run with coverage
cargo llvm-cov --fail-under-lines 80

# Generate HTML report
cargo llvm-cov --html
```

---

## 7. Async Patterns

### 7.1 Tokio Runtime

```rust
use tokio::runtime::Runtime;

// For library code, don't create runtime - accept executor
pub async fn async_operation() -> Result<(), Error> {
    // Implementation
}

// For binary entry points
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    async_operation().await?;
    Ok(())
}
```

### 7.2 Async Traits

With Rust 1.75+, use native async traits:

```rust
pub trait AsyncService {
    async fn process(&self, input: Input) -> Result<Output, Error>;
}

impl AsyncService for MyService {
    async fn process(&self, input: Input) -> Result<Output, Error> {
        // Implementation
    }
}
```

---

## 8. Tauri Integration

For Tauri desktop applications:

### 8.1 Command Documentation

```rust
/// Fetches a resource by its unique identifier.
///
/// # Arguments
///
/// * `id` - The unique identifier of the resource to fetch.
///
/// # Returns
///
/// Returns the resource if found, or an error if not found.
///
/// # Errors
///
/// Returns `ResourceError::NotFound` if no resource with the given ID exists.
#[tauri::command]
pub async fn get_resource(id: String) -> Result<Resource, ResourceError> {
    // Implementation
}
```

### 8.2 Type Sharing with ts-rs

```rust
use ts_rs::TS;
use serde::{Serialize, Deserialize};

/// A resource entity shared between Rust and TypeScript.
#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct Resource {
    /// Unique identifier.
    pub id: String,
    /// Display name.
    pub name: String,
    /// Creation timestamp (ISO 8601).
    pub created_at: String,
}
```

Generate TypeScript types:

```bash
cargo test  # ts-rs generates on test run
# Or explicitly:
cargo run --bin generate-ts-bindings
```
