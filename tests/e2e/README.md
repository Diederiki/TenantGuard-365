# tests/e2e

Playwright end-to-end tests. Drive the live `apps/web` against a mock Microsoft
Graph (see `apps/api/tests/integration/fixtures/graph/`).

Run locally with:

```bash
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed
cd tests/e2e && npm install && npx playwright test
```

Phase 10+ wires this into a CI matrix job with a Postgres/Redis/OpenSearch
service container.

Planned scenarios:
- Mock-auth sign-in → land on overview → see health badges
- Run a report → download CSV → checksum recorded in audit log
- Open audit viewer → entries paginate
- Trigger collector → job status updates on /jobs
- File a remediation action → see it queued in dry-run mode
