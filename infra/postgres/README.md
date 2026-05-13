# infra/postgres

Init scripts mounted into the Postgres container at first start.

- `initdb/00-extensions.sql` — enables `uuid-ossp`, `pgcrypto`, `pg_trgm`, `btree_gin`, `pgstattuple`.

Anything in `initdb/` runs once, on a fresh data volume. To re-run after the volume already exists, you must wipe the volume (`make nuke`) or apply the SQL manually with `psql`.

Phase 1+ adds:
- `initdb/10-roles.sql` — creates `tg365_app` and `tg365_audit_rotation` Postgres roles.
- `initdb/20-audit-immutable.sql` — append-only trigger on `technician_audit_logs`.

Schema migrations are owned by **Alembic** (`apps/api/alembic/`), not by these init scripts.
