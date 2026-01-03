# Testing Standards

> **Applies to**: All automated tests  
> **Parent**: `constitution.md`

---

## 1. Coverage Requirements

All code **MUST** meet or exceed these thresholds:

| Metric | Minimum | Target | Blocking |
|--------|---------|--------|----------|
| Line Coverage | 80% | 90% | Yes |
| Branch Coverage | 75% | 85% | Yes |
| Function Coverage | 85% | 95% | Yes |
| Statement Coverage | 80% | 90% | Yes |

### 1.1 Exclusions

These **MAY** be excluded (with documented rationale):

- Generated code (Prisma client, protobuf, etc.)
- Configuration files
- Type declaration files (`.d.ts`)
- Test fixtures and mocks

---

## 2. Enforcement Commands

### 2.1 Python (pytest-cov)

```bash
# Run with coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Generate HTML report
pytest --cov=src --cov-report=html

# Configuration in pyproject.toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["**/tests/**", "**/__pycache__/**"]
```

### 2.2 TypeScript (Vitest)

```bash
# Run with coverage
pnpm test:coverage

# Configuration in vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 85,
        statements: 80,
      },
    },
  },
});
```

### 2.3 Rust (cargo-llvm-cov)

```bash
# Install
cargo install cargo-llvm-cov

# Run with coverage
cargo llvm-cov --fail-under-lines 80

# Generate HTML report
cargo llvm-cov --html
```

---

## 3. Test Organization

### 3.1 Python

```
tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── __init__.py
│   └── test_api.py
├── e2e/
│   └── test_workflows.py
└── fixtures/
    └── sample_data.json
```

### 3.2 TypeScript

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
e2e/
├── fixtures/
│   └── resource-page.ts
└── specs/
    └── resources.spec.ts
```

### 3.3 Rust

```
crates/core/
├── src/
│   └── lib.rs              # Contains #[cfg(test)] mod tests
└── tests/                  # Integration tests
    └── integration_test.rs
```

---

## 4. Test Naming Conventions

### 4.1 Test Functions

```python
# Python - descriptive snake_case
def test_create_resource_with_valid_data_succeeds():
def test_create_resource_with_empty_name_raises_validation_error():
def test_list_resources_returns_paginated_results():
```

```typescript
// TypeScript - descriptive strings
it("creates resource with valid data")
it("throws validation error when name is empty")
it("returns paginated results")
```

```rust
// Rust - descriptive snake_case
#[test]
fn creates_resource_with_valid_data() {}

#[test]
fn returns_error_for_empty_name() {}
```

### 4.2 Test Classes/Describe Blocks

```python
# Python - Group by method/feature
class TestResourceServiceCreate:
    """Tests for ResourceService.create method."""
```

```typescript
// TypeScript - Nested describes
describe("ResourceService", () => {
  describe("create", () => {
    it("creates resource with valid data", () => {});
  });
});
```

---

## 5. Test Patterns

### 5.1 Arrange-Act-Assert (AAA)

```python
def test_create_resource_success(self, service, mock_repo):
    # Arrange
    create_data = ResourceCreate(name="Test")
    mock_repo.create.return_value = Resource(id=uuid4(), name="Test")

    # Act
    result = await service.create(create_data)

    # Assert
    assert result.name == "Test"
    mock_repo.create.assert_called_once()
```

```typescript
it("creates resource with valid data", async () => {
  // Arrange
  const createData = { name: "Test" };
  mockRepo.create.mockResolvedValue({ id: "123", name: "Test" });

  // Act
  const result = await service.create(createData);

  // Assert
  expect(result.name).toBe("Test");
  expect(mockRepo.create).toHaveBeenCalledOnce();
});
```

### 5.2 Fixtures

```python
# Python - pytest fixtures
@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create a mock repository for testing."""
    return AsyncMock(spec=ResourceRepository)

@pytest.fixture
def service(mock_repository: AsyncMock) -> ResourceService:
    """Create a service instance with mocked dependencies."""
    return ResourceService(repository=mock_repository)
```

```typescript
// TypeScript - beforeEach setup
describe("ResourceService", () => {
  let service: ResourceService;
  let mockRepo: MockProxy<ResourceRepository>;

  beforeEach(() => {
    mockRepo = mock<ResourceRepository>();
    service = new ResourceService(mockRepo);
  });
});
```

```rust
// Rust - test fixtures module
mod fixtures {
    use super::*;

    pub fn sample_config() -> Config {
        Config { max_items: 100, strict: true }
    }

    pub fn sample_data() -> Vec<i32> {
        vec![1, 2, 3, 4, 5]
    }
}
```

---

## 6. Mocking

### 6.1 Python (unittest.mock)

```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=ResourceRepository)

# Patching
@patch("app.services.external_api")
async def test_with_patched_api(mock_api):
    mock_api.fetch.return_value = {"data": "value"}
    # ...
```

### 6.2 TypeScript (vitest)

```typescript
import { vi, Mock } from "vitest";

// Function mock
const mockFn = vi.fn();
mockFn.mockReturnValue("value");
mockFn.mockResolvedValue("async value");

// Module mock
vi.mock("@/lib/api", () => ({
  fetchResource: vi.fn().mockResolvedValue({ id: "123" }),
}));

// Spy
const spy = vi.spyOn(service, "create");
```

### 6.3 Rust

```rust
// Use traits and generics for testability
pub trait Repository {
    fn find(&self, id: &str) -> Option<Resource>;
}

// In tests, create mock implementation
struct MockRepository {
    resources: HashMap<String, Resource>,
}

impl Repository for MockRepository {
    fn find(&self, id: &str) -> Option<Resource> {
        self.resources.get(id).cloned()
    }
}
```

---

## 7. E2E Testing (Playwright)

### 7.1 Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### 7.2 Page Object Pattern

```typescript
// e2e/fixtures/resource-page.ts
import { type Page, type Locator } from "@playwright/test";

export class ResourcePage {
  readonly page: Page;
  readonly nameInput: Locator;
  readonly submitButton: Locator;
  readonly resourceList: Locator;
  readonly successToast: Locator;

  constructor(page: Page) {
    this.page = page;
    this.nameInput = page.getByLabel("Name");
    this.submitButton = page.getByRole("button", { name: "Create" });
    this.resourceList = page.getByRole("list", { name: "Resources" });
    this.successToast = page.getByRole("alert");
  }

  async goto() {
    await this.page.goto("/resources");
  }

  async createResource(data: { name: string; description?: string }) {
    await this.nameInput.fill(data.name);
    if (data.description) {
      await this.page.getByLabel("Description").fill(data.description);
    }
    await this.submitButton.click();
  }
}
```

### 7.3 Test Example

```typescript
// e2e/specs/resources.spec.ts
import { test, expect } from "@playwright/test";
import { ResourcePage } from "../fixtures/resource-page";

test.describe("Resource Management", () => {
  let resourcePage: ResourcePage;

  test.beforeEach(async ({ page }) => {
    resourcePage = new ResourcePage(page);
    await resourcePage.goto();
  });

  test("creates resource with valid data", async () => {
    await resourcePage.createResource({ name: "Test Resource" });
    
    await expect(resourcePage.successToast).toBeVisible();
    await expect(resourcePage.resourceList).toContainText("Test Resource");
  });

  test("shows validation error for empty name", async () => {
    await resourcePage.createResource({ name: "" });
    
    await expect(resourcePage.page.getByText("Name is required")).toBeVisible();
  });
});
```

### 7.4 Accessibility Testing

```typescript
import AxeBuilder from "@axe-core/playwright";

test("passes accessibility audit", async ({ page }) => {
  await page.goto("/resources");
  
  const results = await new AxeBuilder({ page }).analyze();
  
  expect(results.violations).toHaveLength(0);
});
```

---

## 8. CI Integration

### 8.1 GitHub Actions

```yaml
test-typescript:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: pnpm/action-setup@v3
    - uses: actions/setup-node@v4
      with:
        node-version: "20"
        cache: "pnpm"
    - run: pnpm install --frozen-lockfile
    - name: Run tests with coverage
      run: pnpm test:coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v4

test-python:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.13"
    - run: pip install poetry
    - run: poetry install
    - name: Run tests with coverage
      run: poetry run pytest --cov --cov-report=xml --cov-fail-under=80
    - uses: codecov/codecov-action@v4

test-rust:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable
      with:
        components: llvm-tools-preview
    - uses: taiki-e/install-action@cargo-llvm-cov
    - name: Run tests with coverage
      run: cargo llvm-cov --lcov --output-path lcov.info --fail-under-lines 80
    - uses: codecov/codecov-action@v4

e2e:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: pnpm/action-setup@v3
    - uses: actions/setup-node@v4
    - run: pnpm install --frozen-lockfile
    - run: pnpm exec playwright install --with-deps
    - name: Run E2E tests
      run: pnpm test:e2e
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
```
