# Security Standards

> **Applies to**: All code, infrastructure, and processes in Knowledge MCP
> **Parent**: `constitution.md`

---

## 1. Dependency Management

### 1.1 Requirements

| Rule                     | Enforcement                                         |
|--------------------------|-----------------------------------------------------|
| Pin versions             | All dependencies **MUST** be pinned via poetry.lock |
| Security scanning        | **MUST** run on every PR                            |
| Critical vulnerabilities | **MUST** be patched within 24 hours                 |
| High vulnerabilities     | **MUST** be patched within 7 days                   |
| Medium vulnerabilities   | **SHOULD** be patched within 30 days                |

### 1.2 Scanning Commands

```bash
# Install pip-audit (already in dev dependencies)
poetry add --group dev pip-audit

# Run security scan
poetry run pip-audit --strict

# Check for outdated packages
poetry show --outdated
```

### 1.3 GitHub Actions Integration

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 0 * * *"  # Daily

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pip-audit --strict
```

---

## 2. Secrets Management

### 2.1 Rules

| Rule                  | Enforcement                                          |
|-----------------------|------------------------------------------------------|
| No secrets in code    | Secrets **MUST NOT** be committed to version control |
| Environment variables | Configuration **MUST** use environment variables     |
| .env files            | Local development **MUST** use .env (gitignored)     |
| API keys              | **MUST** be loaded from environment at runtime       |

### 2.2 Required Environment Variables

```bash
# .env.example (committed - no real values)
OPENAI_API_KEY=your-openai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Optional
COHERE_API_KEY=your-cohere-key-for-reranking
```

### 2.3 Loading Configuration

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    cohere_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### 2.4 Git Ignore

Already configured in .gitignore:

```gitignore
# Environment & Secrets
.env
.env.local
.env.*.local
```

---

## 3. Input Validation

### 3.1 Rules

| Rule               | Enforcement                          |
|--------------------|--------------------------------------|
| All external input | **MUST** be validated                |
| File paths         | **MUST** be sanitized                |
| User queries       | **MUST** be length-limited           |
| Metadata           | **MUST** be validated before storage |

### 3.2 Pydantic Validation

```python
from pydantic import BaseModel, Field, field_validator
import re


class SearchRequest(BaseModel):
    """Validated search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=5, ge=1, le=100)
    document_type: str | None = Field(default=None, max_length=50)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Remove potentially dangerous characters."""
        # Remove control characters
        return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", v)


class IngestRequest(BaseModel):
    """Validated ingestion request."""

    file_path: str = Field(..., max_length=500)
    document_type: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")

    @field_validator("file_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Prevent path traversal."""
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid file path")
        return v
```

### 3.3 File Path Security

```python
from pathlib import Path


def safe_path(base_dir: Path, user_path: str) -> Path:
    """
    Safely resolve a user-provided path within a base directory.

    Prevents path traversal attacks.
    """
    # Resolve to absolute path
    resolved = (base_dir / user_path).resolve()

    # Ensure it's within base directory
    if not str(resolved).startswith(str(base_dir.resolve())):
        raise ValueError(f"Path traversal detected: {user_path}")

    return resolved
```

---

## 4. API Security

### 4.1 MCP Tool Input Validation

```python
from mcp.types import Tool, TextContent


def validate_tool_input(
    tool_name: str,
    arguments: dict,
) -> dict:
    """Validate MCP tool arguments."""
    schemas = {
        "knowledge_search": SearchRequest,
        "knowledge_ingest": IngestRequest,
    }

    schema = schemas.get(tool_name)
    if not schema:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Pydantic validation
    validated = schema(**arguments)
    return validated.model_dump()
```

### 4.2 Rate Limiting Considerations

For production deployments:

```python
from functools import lru_cache
from datetime import datetime, timedelta


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: dict[str, list[datetime]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        cutoff = now - self.window

        # Clean old requests
        self.requests[client_id] = [
            t for t in self.requests.get(client_id, [])
            if t > cutoff
        ]

        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(now)
        return True
```

---

## 5. Data Security

### 5.1 Embedding Storage

| Rule              | Enforcement                              |
|-------------------|------------------------------------------|
| Qdrant Cloud      | **MUST** use TLS for connections         |
| API keys          | **MUST** be stored securely              |
| Collection access | **SHOULD** use collection-level API keys |

### 5.2 Document Handling

```python
async def process_document(path: Path) -> list[Chunk]:
    """Process document with security considerations."""
    # Validate file type
    if path.suffix.lower() not in [".pdf", ".docx", ".md"]:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    # Check file size (max 50MB)
    if path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("File too large (max 50MB)")

    # Process with appropriate handler
    return await ingest(path)
```

---

## 6. Logging Security

### 6.1 What to Log

| Event                | Log Level  | Required Fields                  |
|----------------------|------------|----------------------------------|
| Search request       | INFO       | query_hash, n_results, timestamp |
| Ingestion start      | INFO       | file_type, file_size, timestamp  |
| Error                | ERROR      | error_type, message, timestamp   |
| Configuration loaded | INFO       | config_source, timestamp         |

### 6.2 Never Log

- API keys or tokens
- Full user queries (use hashes)
- Embedding vectors
- Document contents
- Full file paths (use relative)

```python
import hashlib
import logging

logger = logging.getLogger(__name__)


def log_search(query: str, n_results: int) -> None:
    """Log search request safely."""
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
    logger.info(
        "Search request",
        extra={
            "query_hash": query_hash,
            "n_results": n_results,
        }
    )
```

---

## 7. Security Checklist

### 7.1 Before Commit

- [ ] No secrets in code or comments
- [ ] Input validation for all external data
- [ ] File paths sanitized
- [ ] Error messages don't leak sensitive info
- [ ] Logging follows guidelines

### 7.2 Before Release

- [ ] Dependencies scanned (`pip-audit`)
- [ ] Environment variables documented
- [ ] API keys rotated
- [ ] Access controls reviewed