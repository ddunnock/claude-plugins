# PostgreSQL Row-Level Security (RLS) for Multi-Tenancy

**Researched:** 2026-01-27
**Confidence:** HIGH (verified with official PostgreSQL documentation)
**Applicability:** Knowledge MCP v2.0 (foundation) and v3.0 (full implementation)

## Executive Summary

PostgreSQL Row-Level Security (RLS) provides database-enforced tenant isolation without application-level filtering. For Knowledge MCP v2.0's hybrid architecture (PostgreSQL + Qdrant), RLS offers a clean path to multi-tenancy in v3.0 with minimal application code changes.

**Key Recommendations:**
1. Add `tenant_id` columns to all tenant-scoped tables from v2.0 start
2. Use `SET LOCAL` with session variables for transaction-scoped tenant context
3. Create a dedicated `app_user` role (non-superuser) for application connections
4. Index all `tenant_id` columns for RLS performance
5. Design policies with async SQLAlchemy connection pool events

---

## 1. RLS Core Concepts

### 1.1 Enabling RLS

RLS is enabled per-table and is deny-by-default:

```sql
-- Enable RLS on table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Force RLS even for table owner (recommended)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

**Critical Points:**
- Without policies defined, enabled RLS blocks ALL access (except superusers)
- `FORCE` is required to apply policies to the table owner
- Superusers and `BYPASSRLS` roles always bypass RLS

### 1.2 CREATE POLICY Syntax

```sql
CREATE POLICY policy_name ON table_name
    [ TO role_name [, ...] ]
    [ FOR { ALL | SELECT | INSERT | UPDATE | DELETE } ]
    [ AS { PERMISSIVE | RESTRICTIVE } ]
    [ USING ( expression ) ]
    [ WITH CHECK ( expression ) ];
```

**Clause Meanings:**

| Clause | Purpose | Commands |
|--------|---------|----------|
| `USING` | Filters existing rows (visibility) | SELECT, UPDATE, DELETE |
| `WITH CHECK` | Validates new/modified rows | INSERT, UPDATE |

If `WITH CHECK` is omitted, it defaults to the `USING` expression.

### 1.3 Policy Commands

| Command | `USING` | `WITH CHECK` | Notes |
|---------|---------|--------------|-------|
| `SELECT` | Yes | No | Controls row visibility |
| `INSERT` | No | Yes | Controls insertable rows |
| `UPDATE` | Yes | Yes | USING for selection, WITH CHECK for result |
| `DELETE` | Yes | No | Controls deletable rows |
| `ALL` | Yes | Yes | Applies to all commands |

### 1.4 PERMISSIVE vs RESTRICTIVE

```sql
-- PERMISSIVE (default): Combined with OR
CREATE POLICY tenant_access ON documents
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- RESTRICTIVE: Combined with AND
CREATE POLICY require_active ON documents AS RESTRICTIVE
    USING (status = 'active');
```

**Combination Logic:**
- All `PERMISSIVE` policies for a command are OR'd together
- All `RESTRICTIVE` policies are AND'd together
- Final: (any permissive) AND (all restrictive)

---

## 2. Multi-Tenant Policy Patterns

### 2.1 Standard Tenant Isolation Pattern

```sql
-- Table setup
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Performance-critical index
CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);

-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON documents
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

**Note:** The second parameter `true` in `current_setting('app.tenant_id', true)` returns NULL instead of error if the setting doesn't exist.

### 2.2 Admin Bypass Pattern

```sql
-- Create admin role
CREATE ROLE admin_user WITH LOGIN PASSWORD 'secure_password';
GRANT ALL ON documents TO admin_user;

-- Admin bypass policy
CREATE POLICY admin_full_access ON documents TO admin_user
    USING (true)
    WITH CHECK (true);
```

**Alternative: Function-based admin check:**

```sql
CREATE OR REPLACE FUNCTION is_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_setting('app.is_admin', true)::boolean = true;
END;
$$ LANGUAGE plpgsql STABLE;

-- Policy with admin bypass
CREATE POLICY tenant_or_admin ON documents
    USING (
        (SELECT is_admin()) OR
        tenant_id = (SELECT current_setting('app.tenant_id', true))::uuid
    );
```

### 2.3 Cross-Tenant Operations (Migrations)

For migrations and cross-tenant operations, use a privileged role that bypasses RLS:

```sql
-- Migration user (superuser or BYPASSRLS)
CREATE ROLE migration_user WITH LOGIN BYPASSRLS;

-- Or temporarily disable RLS for maintenance
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
-- ... perform migration ...
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

**Best Practice:** Alembic migrations should use a separate connection with a privileged role that bypasses RLS. The application connection uses the restricted `app_user`.

---

## 3. Session Context Patterns

### 3.1 SET vs SET LOCAL

| Command | Scope | Connection Pool Safe |
|---------|-------|---------------------|
| `SET app.tenant_id = '...'` | Session | NO - leaks to other requests |
| `SET LOCAL app.tenant_id = '...'` | Transaction | YES - auto-resets at COMMIT/ROLLBACK |

**Always use `SET LOCAL` within transactions for connection-pooled applications.**

### 3.2 Using set_config()

```sql
-- set_config(name, value, is_local)
-- is_local = true means transaction-scoped (like SET LOCAL)
SELECT set_config('app.tenant_id', '550e8400-e29b-41d4-a716-446655440000', true);

-- Verify
SELECT current_setting('app.tenant_id');
```

**With asyncpg:** Use `set_config()` instead of `SET` for parameterized queries:

```python
# asyncpg doesn't support parameters in SET statements
# This FAILS:
await conn.execute("SET app.tenant_id = $1", tenant_id)  # Error!

# This WORKS:
await conn.execute("SELECT set_config('app.tenant_id', $1, true)", str(tenant_id))
```

---

## 4. SQLAlchemy Async Integration

### 4.1 Basic Pattern with Context Manager

```python
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

engine = create_async_engine(
    "postgresql+asyncpg://app_user:password@localhost/knowledge_mcp",
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

@asynccontextmanager
async def get_tenant_session(tenant_id: str) -> AsyncSession:
    """Get a session with tenant context set."""
    async with async_session_factory() as session:
        async with session.begin():
            # Set tenant context (transaction-scoped)
            await session.execute(
                text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                {"tenant_id": tenant_id}
            )
            yield session
            # Context automatically clears when transaction ends
```

### 4.2 Middleware Pattern (FastAPI Example)

```python
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

class TenantMiddleware:
    """Extract tenant from request and set session context."""

    async def __call__(self, request: Request, call_next):
        # Extract tenant from JWT, header, or subdomain
        tenant_id = self._extract_tenant(request)
        request.state.tenant_id = tenant_id
        return await call_next(request)

    def _extract_tenant(self, request: Request) -> str | None:
        # Implementation depends on your auth strategy
        return request.headers.get("X-Tenant-ID")

async def get_session_with_tenant(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AsyncSession:
    """Dependency that sets tenant context on session."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if tenant_id:
        await session.execute(
            text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
            {"tenant_id": tenant_id}
        )
    return session
```

### 4.3 Connection Pool Event Pattern

For operations outside request context, use SQLAlchemy pool events:

```python
from sqlalchemy import event
from sqlalchemy.pool import Pool

def set_tenant_context(tenant_id: str):
    """Factory for pool event handlers with specific tenant."""
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        cursor = dbapi_conn.cursor()
        cursor.execute(
            "SELECT set_config('app.tenant_id', %s, false)",  # false = session scope
            (tenant_id,)
        )
        cursor.close()
    return on_checkout

def reset_tenant_context(dbapi_conn, connection_record):
    """Reset tenant context on connection return to pool."""
    cursor = dbapi_conn.cursor()
    cursor.execute("RESET app.tenant_id")
    cursor.close()

# Register reset handler on engine
event.listen(engine.sync_engine.pool, "checkin", reset_tenant_context)
```

### 4.4 Async-Safe Pool Events

For async engines, use the sync_engine attribute:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import event

async_engine = create_async_engine("postgresql+asyncpg://...")

# Register event on the underlying sync engine
@event.listens_for(async_engine.sync_engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Called when a new connection is created."""
    # For asyncpg, use run_async for async operations
    pass

@event.listens_for(async_engine.sync_engine.pool, "reset")
def on_reset(dbapi_connection, connection_record, reset_state):
    """Called when connection is returned to pool."""
    if reset_state.asyncio_safe:
        # Safe to run sync operations
        cursor = dbapi_connection.cursor()
        cursor.execute("RESET app.tenant_id")
        cursor.close()
```

---

## 5. Performance Considerations

### 5.1 Index Requirements

**Critical:** Always index columns used in RLS policies:

```sql
-- Required for efficient RLS evaluation
CREATE INDEX idx_documents_tenant_id ON documents(tenant_id);

-- Composite index for common query patterns
CREATE INDEX idx_documents_tenant_created
    ON documents(tenant_id, created_at DESC);
```

Without proper indexes, RLS forces sequential scans on every query.

### 5.2 Function Optimization

**Bad (function called per-row):**

```sql
CREATE POLICY slow_policy ON documents
    USING (tenant_id = get_current_tenant(user_data));  -- Called per row!
```

**Good (function result cached per-transaction):**

```sql
-- Mark function as STABLE (same result within transaction)
CREATE FUNCTION get_tenant_id() RETURNS UUID AS $$
    SELECT current_setting('app.tenant_id', true)::uuid;
$$ LANGUAGE SQL STABLE;

-- Use subselect to cache result
CREATE POLICY fast_policy ON documents
    USING (tenant_id = (SELECT get_tenant_id()));
```

### 5.3 Avoid Subquery Chains

RLS policies can invoke other RLS policies, causing cascading performance issues:

```sql
-- Problematic: may trigger RLS on tenants table
CREATE POLICY chained_policy ON documents
    USING (tenant_id IN (SELECT id FROM tenants WHERE active = true));
```

**Solution:** Use `SECURITY DEFINER` functions to bypass nested RLS:

```sql
CREATE FUNCTION get_active_tenant_ids() RETURNS SETOF UUID AS $$
    SELECT id FROM tenants WHERE active = true;
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

CREATE POLICY optimized_policy ON documents
    USING (tenant_id IN (SELECT get_active_tenant_ids()));
```

### 5.4 Performance Benchmarks

From community benchmarks:

| Scenario | Overhead | Notes |
|----------|----------|-------|
| Simple tenant_id check | ~1-5% | With proper index |
| Function call (STABLE) | ~5-10% | Function cached per-transaction |
| Subquery to other RLS table | ~50-200% | Cascading policy evaluation |
| Missing index | 100x+ | Sequential scan required |

---

## 6. Docker Compose Setup

### 6.1 PostgreSQL Configuration

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: knowledge_mcp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 6.2 Database Initialization Script

```sql
-- init-db/01-create-users.sql

-- Application user (subject to RLS)
CREATE USER app_user WITH PASSWORD 'app_password';

-- Migration user (bypasses RLS)
CREATE USER migration_user WITH PASSWORD 'migration_password' BYPASSRLS;

-- Grant schema access
GRANT USAGE ON SCHEMA public TO app_user, migration_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user, migration_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO app_user, migration_user;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO app_user, migration_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON SEQUENCES TO app_user, migration_user;
```

### 6.3 Alembic Configuration

```python
# alembic/env.py
import os
from sqlalchemy import create_engine

def get_url():
    """Use migration user for Alembic operations."""
    return os.environ.get(
        "DATABASE_URL_MIGRATION",
        "postgresql://migration_user:migration_password@localhost/knowledge_mcp"
    )

def run_migrations_online():
    engine = create_engine(get_url())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### 6.4 Application Configuration

```python
# config.py
import os

# Application connection (subject to RLS)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://app_user:app_password@localhost/knowledge_mcp"
)

# Migration connection (bypasses RLS)
DATABASE_URL_MIGRATION = os.environ.get(
    "DATABASE_URL_MIGRATION",
    "postgresql://migration_user:migration_password@localhost/knowledge_mcp"
)
```

---

## 7. Potential Issues and Limitations

### 7.1 RLS Bypass Risks

| Risk | Mitigation |
|------|------------|
| Superuser bypass | Never use superuser for app connections |
| Table owner bypass | Always use `FORCE ROW LEVEL SECURITY` |
| `BYPASSRLS` role leakage | Audit role grants, use separate migration user |
| Views bypass RLS | Use `security_invoker = true` (PostgreSQL 15+) |

### 7.2 Async-Specific Issues

| Issue | Solution |
|-------|----------|
| Shared session variable | Use `SET LOCAL` within transactions |
| Pool connection reuse | Reset context on checkin event |
| Garbage-collected connections | Use `reset` event with `asyncio_safe` check |
| `asyncio.gather()` safety | One AsyncSession per task |

### 7.3 Operational Challenges

| Challenge | Mitigation |
|-----------|------------|
| Policy debugging | Use `EXPLAIN (ANALYZE, VERBOSE)` to see policy effects |
| Migration complexity | Separate migration user with BYPASSRLS |
| Testing with superuser | Create test user without BYPASSRLS |
| Emergency access | Document admin bypass procedure |

### 7.4 What RLS Cannot Do

- **Column-level security**: RLS is row-only; use views or application logic for columns
- **Complex authorization**: RBAC/ABAC may need application layer (OPA, etc.)
- **Dynamic rules**: Time-based or context-aware rules are difficult
- **Audit logging**: RLS doesn't log denied access; add application logging

---

## 8. Implementation Recommendations for Knowledge MCP

### 8.1 v2.0 Preparation (Now)

1. **Schema Design**: Add `tenant_id UUID` to all tenant-scoped tables
2. **Index Strategy**: Create indexes on `tenant_id` columns from the start
3. **User Separation**: Configure `app_user` and `migration_user` in Docker Compose
4. **Code Pattern**: Use async context managers with transaction-scoped sessions

### 8.2 v3.0 Implementation (Future)

1. **Enable RLS**: Add migration to enable RLS on all tables
2. **Create Policies**: Add tenant isolation policies per table
3. **Middleware**: Add tenant context extraction from JWT/headers
4. **Pool Events**: Register checkin handlers to reset context
5. **Admin Tools**: Create admin bypass mechanism for cross-tenant operations

### 8.3 Example Migration (v3.0)

```python
# alembic/versions/xxx_enable_rls.py
from alembic import op

def upgrade():
    # Enable RLS on all tenant tables
    tables = ['documents', 'chunks', 'projects', 'feedback']

    for table in tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table}
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        """)

def downgrade():
    tables = ['documents', 'chunks', 'projects', 'feedback']

    for table in tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
```

---

## 9. Sources

### Official Documentation
- [PostgreSQL 18: Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) - Authoritative RLS reference

### Best Practices and Patterns
- [Permit.io: Postgres RLS Implementation Guide](https://www.permit.io/blog/postgres-rls-implementation-guide)
- [AWS: Multi-tenant Data Isolation with PostgreSQL RLS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)
- [Crunchy Data: Row Level Security for Tenants](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres)
- [Supabase: Row Level Security Docs](https://supabase.com/docs/guides/database/postgres/row-level-security)

### Performance Optimization
- [Scott Pierce: Optimizing Postgres RLS for Performance](https://scottpierce.dev/posts/optimizing-postgres-rls/)
- [Bytebase: PostgreSQL RLS Limitations and Alternatives](https://www.bytebase.com/blog/postgres-row-level-security-limitations-and-alternatives/)
- [Bytebase: Common Postgres RLS Footguns](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)

### SQLAlchemy Integration
- [SQLAlchemy 2.0: AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLAlchemy 2.0: Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [SQLAlchemy 2.0: Core Events](https://docs.sqlalchemy.org/en/20/core/events.html)

### Multi-Tenant Implementations
- [Nile.dev: Shipping Multi-tenant SaaS with RLS](https://www.thenile.dev/blog/multi-tenant-rls)
- [Simplyblock: PostgreSQL Multi-Tenancy with RLS](https://www.simplyblock.io/blog/underated-postgres-multi-tenancy-with-row-level-security/)

---

*This research document provides the foundation for implementing multi-tenancy in Knowledge MCP v3.0. The patterns documented here are verified against official PostgreSQL 18 documentation and industry best practices.*
