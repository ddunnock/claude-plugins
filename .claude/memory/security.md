# Security Standards

> **Applies to**: All code, infrastructure, and processes  
> **Parent**: `constitution.md`

---

## 1. Dependency Management

### 1.1 Requirements

| Rule | Enforcement |
|------|-------------|
| Pin versions | All dependencies **MUST** be pinned to exact versions |
| Security scanning | **MUST** run on every PR |
| Critical vulnerabilities | **MUST** be patched within 24 hours |
| High vulnerabilities | **MUST** be patched within 7 days |
| Medium vulnerabilities | **SHOULD** be patched within 30 days |

### 1.2 Scanning Tools

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: "0 0 * * *"  # Daily

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Node.js
      - run: pnpm audit --audit-level=high
      
      # Python
      - run: pip-audit --strict
      
      # Rust
      - run: cargo audit

  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript, python
      - uses: github/codeql-action/analyze@v3
```

### 1.3 Automated Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    groups:
      production:
        patterns: ["*"]
        exclude-patterns: ["@types/*", "eslint*", "prettier*"]

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "cargo"
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

| Rule | Enforcement |
|------|-------------|
| No secrets in code | Secrets **MUST NOT** be committed to version control |
| Environment variables | Configuration **MUST** use environment variables |
| Secrets manager | Production secrets **MUST** use a secrets manager |
| Key rotation | API keys **MUST** be rotated every 90 days |
| Least privilege | Secrets **MUST** have minimum required permissions |

### 2.2 Environment Variables

```bash
# .env.example (committed - no real values)
DATABASE_URL=postgresql://user:password@localhost:5432/db
API_KEY=your-api-key-here
JWT_SECRET=your-jwt-secret-here

# .env.local (not committed)
DATABASE_URL=postgresql://real:password@prod-db:5432/db
API_KEY=real-api-key
JWT_SECRET=real-jwt-secret
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

### 2.4 Pre-commit Hook

```bash
#!/bin/bash
# .husky/pre-commit

# Check for potential secrets
if git diff --cached --name-only | xargs grep -l -E "(api[_-]?key|secret|password|token)" 2>/dev/null; then
  echo "Warning: Possible secrets detected in staged files"
  echo "Please review before committing"
  exit 1
fi
```

### 2.5 AWS Secrets Manager (GovCloud)

```typescript
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({ region: "us-gov-west-1" });

export async function getSecret(secretId: string): Promise<string> {
  const command = new GetSecretValueCommand({ SecretId: secretId });
  const response = await client.send(command);
  
  if (!response.SecretString) {
    throw new Error(`Secret ${secretId} not found`);
  }
  
  return response.SecretString;
}
```

---

## 3. Input Validation

### 3.1 Rules

| Rule | Enforcement |
|------|-------------|
| All external input | **MUST** be validated |
| SQL queries | **MUST** use parameterized statements |
| HTML output | **MUST** be escaped |
| File uploads | **MUST** be scanned and size-limited |
| API requests | **MUST** validate request body and params |

### 3.2 Validation Examples

**TypeScript (Zod):**

```typescript
import { z } from "zod";

const createUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
  age: z.number().int().min(0).max(150).optional(),
});

function validateInput<T>(schema: z.ZodSchema<T>, data: unknown): T {
  return schema.parse(data);
}
```

**Python (Pydantic):**

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class CreateUser(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int | None = Field(None, ge=0, le=150)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z\s]+$", v):
            raise ValueError("Name must contain only letters and spaces")
        return v
```

### 3.3 SQL Injection Prevention

```typescript
// ❌ Bad - SQL injection vulnerability
const query = `SELECT * FROM users WHERE id = '${userId}'`;

// ✅ Good - Parameterized query
const user = await db.user.findUnique({
  where: { id: userId },
});

// ✅ Good - Raw query with parameters
const users = await db.$queryRaw`
  SELECT * FROM users WHERE email = ${email}
`;
```

```python
# ❌ Bad - SQL injection vulnerability
cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# ✅ Good - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ✅ Good - ORM
user = session.query(User).filter(User.id == user_id).first()
```

### 3.4 XSS Prevention

```typescript
// React automatically escapes by default
<div>{userInput}</div>  // Safe

// ❌ Dangerous - bypasses escaping
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// ✅ If HTML is needed, sanitize first
import DOMPurify from "dompurify";
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />
```

---

## 4. Authentication & Authorization

### 4.1 Password Requirements

| Requirement | Value |
|-------------|-------|
| Minimum length | 12 characters |
| Complexity | At least 3 of: uppercase, lowercase, number, symbol |
| History | Cannot reuse last 5 passwords |
| Expiration | 90 days for privileged accounts |

### 4.2 Session Management

```typescript
// next-auth configuration
export const authOptions: NextAuthOptions = {
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  jwt: {
    maxAge: 30 * 24 * 60 * 60,
  },
  callbacks: {
    jwt: async ({ token, user }) => {
      if (user) {
        token.id = user.id;
        token.role = user.role;
      }
      return token;
    },
    session: async ({ session, token }) => {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
};
```

### 4.3 Authorization Patterns

```typescript
// Middleware-based authorization
export async function authorize(
  request: NextRequest,
  requiredRole: string
): Promise<boolean> {
  const session = await auth();
  
  if (!session?.user) {
    return false;
  }
  
  return session.user.role === requiredRole;
}

// Usage in API route
export async function GET(request: NextRequest) {
  if (!await authorize(request, "admin")) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }
  
  // Handle authorized request
}
```

---

## 5. HTTPS & Transport Security

### 5.1 Requirements

| Rule | Enforcement |
|------|-------------|
| HTTPS only | All production traffic **MUST** use HTTPS |
| TLS version | **MUST** use TLS 1.2 or higher |
| HSTS | **MUST** be enabled with 1-year max-age |
| Certificate | **MUST** use certificates from trusted CA |

### 5.2 Security Headers

```typescript
// next.config.ts
const securityHeaders = [
  {
    key: "Strict-Transport-Security",
    value: "max-age=31536000; includeSubDomains",
  },
  {
    key: "X-Frame-Options",
    value: "DENY",
  },
  {
    key: "X-Content-Type-Options",
    value: "nosniff",
  },
  {
    key: "Referrer-Policy",
    value: "strict-origin-when-cross-origin",
  },
  {
    key: "Content-Security-Policy",
    value: "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
  },
];

export default {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## 6. File Upload Security

### 6.1 Requirements

| Rule | Value |
|------|-------|
| Max size | 10MB (configurable per use case) |
| Allowed types | Explicit allowlist only |
| Storage | External storage (S3), never local filesystem |
| Scanning | Virus scan before processing |

### 6.2 Implementation

```typescript
import { z } from "zod";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

const fileSchema = z.object({
  name: z.string(),
  type: z.enum(ALLOWED_TYPES as [string, ...string[]]),
  size: z.number().max(MAX_SIZE),
});

export async function handleUpload(file: File) {
  // Validate
  fileSchema.parse({
    name: file.name,
    type: file.type,
    size: file.size,
  });

  // Check magic bytes (not just extension)
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer.slice(0, 4));
  
  if (!isValidMagicBytes(bytes, file.type)) {
    throw new Error("File type mismatch");
  }

  // Upload to S3 with random filename
  const key = `uploads/${crypto.randomUUID()}${getExtension(file.type)}`;
  await s3.upload({ Key: key, Body: buffer });
  
  return key;
}
```

---

## 7. Logging & Monitoring

### 7.1 Security Logging

| Event | Log Level | Required Fields |
|-------|-----------|-----------------|
| Authentication success | INFO | userId, timestamp, IP |
| Authentication failure | WARN | attemptedUser, timestamp, IP |
| Authorization failure | WARN | userId, resource, action, timestamp |
| Sensitive data access | INFO | userId, resource, timestamp |
| Configuration change | INFO | userId, change, timestamp |

### 7.2 Never Log

- Passwords (even hashed)
- API keys/tokens
- Credit card numbers
- Social security numbers
- Full session tokens

```typescript
// ❌ Bad
logger.info(`User login: ${email}, password: ${password}`);

// ✅ Good
logger.info("User login attempt", { email, success: true, ip: request.ip });
```

---

## 8. AWS GovCloud Considerations

### 8.1 Compliance Requirements

| Requirement | Implementation |
|-------------|----------------|
| Region isolation | All resources in `us-gov-west-1` or `us-gov-east-1` |
| Encryption at rest | KMS encryption for all data stores |
| Encryption in transit | TLS 1.2+ for all connections |
| Access logging | CloudTrail enabled for all accounts |
| Compliance tags | Required on all resources |

### 8.2 Required Tags

```typescript
const complianceTags = {
  Environment: "production",
  DataClassification: "CUI",
  Compliance: "FedRAMP-High",
  Owner: "team@example.com",
  Project: "ProjectName",
};
```
