# apps/worker — background workers + scheduler

> **Phase 0**: placeholder. The container in `docker-compose.yml` prints a banner and sleeps.
> **Phase 1**: this folder ships real Celery (or Dramatiq) workers and a beat scheduler.

## Planned layout (Phase 1)

```
apps/worker/
├── pyproject.toml
├── Dockerfile
├── app/
│   ├── main.py                   # Celery / Dramatiq app
│   ├── beat.py                   # periodic schedule
│   ├── config.py
│   ├── graph/                    # shared with apps/api via packages/shared-graph (TBD)
│   ├── modules/
│   │   ├── entra/
│   │   │   └── collectors/
│   │   ├── exchange/collectors/
│   │   ├── sharepoint/collectors/
│   │   ├── onedrive/collectors/
│   │   ├── teams/collectors/
│   │   └── security/collectors/
│   ├── audit_shipper.py          # ships technician_audit_logs to immutable sink
│   ├── remediation_executor.py   # consumes approved remediation_actions
│   └── webhooks_renewer.py       # renews graph_webhook_subscriptions
└── tests/
```

## Why split worker from api?

- The API path must be fast and not blocked by long Graph calls.
- Workers can scale horizontally without touching the API.
- Different credentials: the worker holds the Graph token cache key; the API holds the session signing key.
- Different RBAC: only the worker has `remediation.execute`.

## Queues (Phase 1+)

| Queue | Concurrency | Purpose |
|-------|-------------|---------|
| `collect.entra` | 4 | Entra ID collectors |
| `collect.sharepoint` | 4 | SharePoint deep scans |
| `collect.exchange` | 2 | Mailbox settings, audit fetches |
| `collect.teams` | 2 | Teams collectors |
| `audit.ship` | 1 | Audit shipper |
| `reports` | 4 | Report runs + exports |
| `notify` | 2 | Email/webhook delivery |
| `remediation` | 1 | Approved remediation actions |
| `webhooks` | 2 | Subscription renewal, change-notification handlers |

Per-tenant concurrency is enforced via a Redis-backed semaphore independent of per-queue concurrency.

## Local development (Phase 1+)

```bash
docker compose --profile app up -d worker
docker compose logs -f worker
docker compose exec worker python -m app.scripts.enqueue collect.entra.users <tenant_id>
```
