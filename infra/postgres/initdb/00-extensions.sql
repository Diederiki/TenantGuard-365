-- Extensions enabled at first Postgres start.
-- Run automatically by the official postgres image because the file lives in
-- /docker-entrypoint-initdb.d. Idempotent so re-runs after volume reset are safe.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- fast text search on names/paths
CREATE EXTENSION IF NOT EXISTS "btree_gin";      -- composite GIN indexes (e.g. JSONB + tenant_id)
CREATE EXTENSION IF NOT EXISTS "pgstattuple";    -- bloat checks (operations)
