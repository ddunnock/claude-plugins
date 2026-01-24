# Security Standards

> **Applies to**: All code, infrastructure, and processes
> **Parent**: `constitution.md`

---

## 1. Dependency Management

### 1.1 Requirements

| Rule                     | Enforcement                                                           |
|--------------------------|-----------------------------------------------------------------------|
| Pin versions             | All dependencies **MUST** be pinned to exact versions via poetry.lock |
| Security scanning        | **MUST** run on every PR                                              |
| Critical vulnerabilities | **MUST** be patched within 24 hours                                   |
| High vulnerabilities     | **MUST** be patched within 7 days                                     |
| Medium vulnerabilities   | **SHOULD** be patched within 30 days                                  |

### 1.2 Scanning Commands

```bash
# Python - Install and run pip-audit
pip install pip-audit
pip-audit --strict

# Or with Poetry
poetry run pip-audit --strict
```

### 1.3 Automated Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 2. Secrets Management

### 2.1 Rules

| Rule                  | Enforcement                                          |
|-----------------------|------------------------------------------------------|
| No secrets in code    | Secrets **MUST NOT** be committed to version control |
| Environment variables | Configuration **MUST** use environment variables     |
| Key rotation          | API keys **MUST** be rotated every 90 days           |
| Least privilege       | Secrets **MUST** have minimum required permissions   |

### 2.2 Environment Variables

```bash
# .env.example (committed - no real values)
OPENAI_API_KEY=your-openai-api-key-here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here

# .env (not committed)
OPENAI_API_KEY=sk-real-api-key
QDRANT_URL=https://real-cluster.qdrant.io
QDRANT_API_KEY=real-qdrant-key
```

### 2.3 Git Ignore

```gitignore
# .gitignore
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

### 2.4 Secret Loading Pattern

```python
"""Configuration loading with validation."""

from functools import lru_cache
import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment."""

    openai_api_key: str = Field(..., description="OpenAI API key for embeddings")
    qdrant_url: str = Field(..., description="Qdrant Cloud cluster URL")
    qdrant_api_key: str = Field(..., description="Qdrant Cloud API key")

    class Config:
        frozen = True


@lru_cache
def get_settings() -> Settings:
    """
    Load and validate settings from environment.

    Returns:
        Validated Settings instance.

    Raises:
        ValidationError: When required environment variables are missing.
    """
    return Settings(
        openai_api_key=os.environ["OPENAI_API_KEY"],
        qdrant_url=os.environ["QDRANT_URL"],
        qdrant_api_key=os.environ["QDRANT_API_KEY"],
    )
```

---

## 3. Input Validation

### 3.1 Rules

| Rule               | Enforcement                               |
|--------------------|-------------------------------------------|
| All external input | **MUST** be validated                     |
| File uploads       | **MUST** be scanned and size-limited      |
| API requests       | **MUST** validate request body and params |

### 3.2 Validation Examples (Pydantic)

```python
from pydantic import BaseModel, Field, field_validator
import re


class SearchQuery(BaseModel):
    """Validated search query from MCP client."""

    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(default=5, ge=1, le=100)
    document_type: str | None = Field(default=None, max_length=50)

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        """Remove potentially dangerous characters."""
        # Allow alphanumeric, spaces, and common punctuation
        sanitized = re.sub(r'[^\w\s\-.,?!\'"]', '', v)
        return sanitized.strip()


class IngestRequest(BaseModel):
    """Validated document ingestion request."""

    file_path: str = Field(..., max_length=500)
    document_type: str = Field(..., pattern=r'^(pdf|docx|md)$')

    @field_validator("file_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Prevent path traversal attacks."""
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid file path")
        return v
```

### 3.3 Path Traversal Prevention

```python
from pathlib import Path


def safe_read_file(base_dir: Path, user_filename: str) -> str:
    """
    Read file safely, preventing directory traversal.

    Args:
        base_dir: Allowed directory (must be absolute)
        user_filename: User-provided filename

    Returns:
        File contents

    Raises:
        ValueError: If path would escape base_dir
    """
    # Resolve to absolute path
    target = (base_dir / user_filename).resolve()

    # MUST verify path is within base_dir
    if not target.is_relative_to(base_dir.resolve()):
        raise ValueError(f"Path traversal attempt: {user_filename}")

    return target.read_text()
```

---

## 4. Logging & Monitoring

### 4.1 Security Logging

| Event                 | Log Level  | Required Fields                        |
|-----------------------|------------|----------------------------------------|
| Search query          | INFO       | query_hash, timestamp, n_results       |
| Document ingestion    | INFO       | document_type, size, timestamp         |
| Configuration change  | INFO       | change, timestamp                      |
| Error with user input | WARN       | error_type, sanitized_input, timestamp |

### 4.2 Never Log

- API keys/tokens
- Full file paths from user input
- Full query text (use hash instead for privacy)
- Embedding vectors

```python
import logging
import hashlib

logger = logging.getLogger(__name__)


def log_search(query: str, n_results: int) -> None:
    """Log search request with privacy protection."""
    # Hash query for logging (don't log actual content)
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]

    # Good: Log hash, not content
    logger.info("Search request", extra={
        "query_hash": query_hash,
        "n_results": n_results,
    })
```

---

## 5. MCP-Specific Security

### 5.1 Tool Input Validation

All MCP tool inputs **MUST** be validated:

```python
from mcp.types import Tool
from pydantic import ValidationError


async def handle_search_tool(arguments: dict) -> list[TextContent]:
    """Handle search tool with validation."""
    try:
        # Validate with Pydantic
        request = SearchQuery(**arguments)
    except ValidationError as e:
        return [TextContent(type="text", text=json.dumps({
            "error": "Invalid input",
            "details": str(e),
        }))]

    # Proceed with validated input
    results = await perform_search(request)
    return [TextContent(type="text", text=json.dumps(results))]
```

### 5.2 Rate Limiting Considerations

For production deployments, consider:

```python
from functools import lru_cache
from datetime import datetime, timedelta


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: list[datetime] = []

    def allow_request(self) -> bool:
        """Check if request is allowed under rate limit."""
        now = datetime.now()
        cutoff = now - self.window

        # Remove old requests
        self.requests = [r for r in self.requests if r > cutoff]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)
        return True
```

---

## 6. Embedding Security

### 6.1 API Key Protection

```python
import os


class OpenAIEmbedder:
    """OpenAI embedder with secure key handling."""

    def __init__(self) -> None:
        # Load key from environment, never hardcode
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        # Never log or expose the key
        self._client = OpenAI(api_key=api_key)

    def __repr__(self) -> str:
        # Never include key in repr
        return "OpenAIEmbedder(api_key=***)"
```

### 6.2 Vector Store Authentication

```python
from qdrant_client import QdrantClient


def create_qdrant_client() -> QdrantClient:
    """Create Qdrant client with secure authentication."""
    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")

    if not url or not api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY required")

    return QdrantClient(
        url=url,
        api_key=api_key,
        https=True,  # Always use HTTPS
    )
```