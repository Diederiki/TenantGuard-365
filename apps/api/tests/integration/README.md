# Integration tests

Tests in this directory expect a live Postgres + Redis + OpenSearch on the
local Docker Compose network. They are NOT run in the default CI workflow yet
(Phase 10 will add a `service: postgres` matrix job).

To run locally:

```bash
docker compose up -d postgres redis opensearch minio
docker compose exec api alembic upgrade head
docker compose exec api pytest -q tests/integration
```

The unit tests in `tests/unit/` cover the framework primitives. Integration
tests verify wiring: real DB writes, real audit-log append-only trigger,
report engine producing rows against live tables, collector idempotency.
