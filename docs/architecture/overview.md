# Architecture — Overview

> Companion to [/ARCHITECTURE.md](../../ARCHITECTURE.md). This file is the longer
> "how the parts fit together" reference.

## Request lifecycle

### Read flow (user opens a report)

```
Browser ──HTTPS──▶ Next.js (web) ──REST──▶ FastAPI (api)
                                              │
                                              ├─▶ Authorize: session cookie → user, RBAC check
                                              │
                                              ├─▶ Postgres: fetch saved report, filters
                                              │
                                              ├─▶ Postgres / OpenSearch: query
                                              │   (collectors have already pre-fetched the data)
                                              │
                                              ├─▶ Build response, paginate
                                              │
                                              └─▶ Audit log: data-access record
```

The API never calls Microsoft Graph in the request path. Graph traffic is owned by the worker.

### Collection flow (Graph data refresh)

```
Worker beat (scheduler) ──▶ Enqueue collector job
                                   │
                                   ▼
Worker process ──▶ GraphClient.acquire_token(tenant)
                       │
                       ├─▶ Redis: per-tenant concurrency semaphore
                       │
                       ├─▶ HTTP request to Graph
                       │   ├─ 200: write to Postgres + OpenSearch
                       │   ├─ 429: parse Retry-After, sleep, retry
                       │   └─ 5xx: exponential backoff with jitter
                       │
                       ├─▶ Delta link saved to graph_delta_tokens
                       │
                       └─▶ graph_sync_job_runs: success / failure / duration / rows
```

### Remediation flow (Phase 9 — opt-in only)

```
Technician submits action ──▶ FastAPI validates RBAC (remediation.submit)
                                   │
                                   ▼
Postgres: remediation_actions (status=pending_approval, mode=dry-run)
                                   │
              (notification to approvers via notification_channels)
                                   ▼
Second technician approves ──▶ remediation_approvals row
                                   │
                                   ▼
Worker picks up the action ──▶ Dry-run by default
                                   │
                                   ├─ Dry-run: record predicted change, no Graph write
                                   └─ Live (only if policy.allow_live=true and approver signed)
```

## Tenancy model

The platform is **single-tenant per deployment** in the v1 sense — one company runs one instance for their own Microsoft 365 tenant. However the data model treats the Microsoft tenant as a first-class entity (`tenants` table), which means:

- A future hosted multi-tenant deployment can scope every query by `tenant_id` without restructuring.
- Reseller / MSP support (managing multiple Microsoft tenants from one console) is a Phase 11+ extension and the schema already accommodates it.

## Process layout

| Process | Container | Description |
|--------|-----------|-------------|
| `tg365-api` | apps/api | Stateless FastAPI service. Horizontal scale-out via reverse proxy. |
| `tg365-web` | apps/web | Stateless Next.js node server (or static export + adapter). |
| `tg365-worker` | apps/worker | Celery/Dramatiq worker pool. Multiple replicas in prod. |
| `tg365-scheduler` | apps/worker (beat) | Single replica. Owns periodic schedules. |
| `tg365-postgres` | infra | Single primary; warm standby in Phase 10. |
| `tg365-redis` | infra | Broker, cache, locks. Persistence AOF on. |
| `tg365-opensearch` | infra | Single-node dev, can scale to small cluster in prod. |
| `tg365-minio` | infra | Object storage; swappable for S3/Azure Blob in prod. |
| `tg365-mailhog` | infra (dev only) | Outbound mail capture. Replaced by real SMTP in prod. |
| `tg365-caddy` | infra (prod only) | TLS + reverse proxy. |

## Network boundaries

```
[ Public Internet ]
        │
        ▼  TCP 443
┌──────────────────┐
│ Caddy / Nginx    │  ◀── only public ingress
└──────────────────┘
        │
        ▼   (Docker bridge network: tg365)
   ┌────┴────┬───────────┬─────────────┐
   ▼         ▼           ▼             ▼
  api       web        worker        scheduler
   │
   ├──▶ postgres, redis, opensearch, minio  (network-internal only)
   │
   └──▶ Microsoft Graph (HTTPS, outbound, certificate-pinned where practical)
```

## Failure modes the platform must survive

| Failure | Behaviour |
|---------|-----------|
| Microsoft Graph 429 | Honour `Retry-After`; downgrade per-tenant concurrency; surface throttling on Graph health screen. |
| Microsoft Graph 5xx | Exponential backoff, retry up to cap, then fail job to queue. |
| Worker crash mid-collection | Job state in Postgres marks run as `failed`; next schedule resumes from saved delta token. |
| Postgres restart | API returns 503 from `/readyz` until DB reconnects; in-flight requests fail loudly, not silently. |
| OpenSearch unhealthy | Reports that need OS degrade with a banner; collectors continue and buffer audit events to Postgres "overflow" table for replay. |
| Redis unhealthy | Workers pause; API blocks routes that require rate-limit tokens; surface on system status page. |
| MinIO unhealthy | Exports fail with a clear error; API does not return partially-uploaded files. |
| Network partition to Graph | Collectors back off; UI shows last-successful-collection timestamp prominently. |
