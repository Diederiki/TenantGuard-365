# TenantGuard 365 — Performance & Efficiency Analysis

_Last reviewed: 2026-05-13 (Phase 26)._

Where the platform is fast today, where the hotspots are, and what to
measure next. This isn't a load-test report — that lives under
`tests/load/` once we wire k6 scenarios.

## 1. Database

| Concern | Status | Notes |
|---|---|---|
| Indexes on hot filters | **Mostly** | `tenants(id)`, `platform_users(email)` unique, `technician_audit_log(event_time desc)`, `graph_sync_job_runs(started_at desc, status)`, `m365_users(tenant_id, user_principal_name)`. **Open**: composite index on `sharepoint_permissions(site_id, principal_id)` and `security_alerts(tenant_id, status, severity)` for the alert list page. |
| FK indexes | **Closed** | Postgres does not auto-index FKs; Alembic migrations add them where joins exist. |
| Pagination | **Mixed** | Audit uses keyset (`before_id`). Reports + RBAC are `OFFSET` based — fine for small tables, sub-optimal for `m365_users` at scale. Migrate report queries to keyset in Phase 27. |
| `SELECT *` avoided | **Closed** | All queries project explicit columns. |
| N+1 risk in reports | **Partial** | `reports/builtins.py` projects flat tables, no joins on hot path. The SharePoint sharing-link join is `selectinload`-eligible if we add a relationship-style API. |
| Timezone-aware timestamps | **Closed** | `DateTime(timezone=True)` everywhere; ORM uses `UTC`. |

## 2. API

| Concern | Status | Notes |
|---|---|---|
| Async I/O on Graph + Redis | **Closed** | All external I/O uses `httpx.AsyncClient` / `redis.asyncio`. |
| Synchronous collector trigger | **Open** | `POST /api/tenants/{id}/collectors/{key}/run` runs `asyncio.run(run_collector(...))` inside a sync endpoint. Move to a background-job submit when collectors regularly exceed a few seconds. Today it's used only for "Test connection" + small collectors. |
| Response sizes | **Closed** | Audit page returns 25/50 rows by default; reports stream rows server-side. |
| Compression | **Open** | No gzip/br middleware on the API. Add `BrotliMiddleware` in front of `/api/reports` exports. |
| Per-tenant Graph concurrency | **Closed** | Hard cap = 4 (`graph_per_tenant_concurrency`). |
| Rate-limit Redis path | **Closed** | Single `INCR` + conditional `EXPIRE`; O(1). |

## 3. Background work

| Concern | Status | Notes |
|---|---|---|
| Worker decoupled from API | **Closed** | `apps/worker` runs the scheduler + collectors. |
| Cron schedule expressed declaratively | **Closed** | Each collector exposes `schedule_cron`; `croniter` enumerates. |
| Job-run table records `rows_in / rows_out / status / error` | **Closed** | `GraphSyncJobRun`. |
| Delta-query support | **Partial** | `entra.users` collector supports `$delta`. Sharepoint sites and m365 groups still do full scan. |
| Cancellation | **Open** | No way to stop a long-running run from the UI. Add `cancel_requested_at` column in Phase 27. |
| Stuck-run detection | **Open** | If a worker crashes mid-run, the row stays `running`. Reaper task TODO. |

## 4. Microsoft Graph

| Concern | Status | Notes |
|---|---|---|
| 429 / Retry-After | **Closed** | `app/graph/client.py` honours `Retry-After`. |
| Exponential backoff | **Closed** | 1 s base, capped at 60 s, 8 retries. |
| Batch endpoint usage | **Partial** | User + group resolution uses `$batch`. SharePoint permissions still per-resource. |
| `$select` projection | **Closed** | Each collector lists explicit fields. |
| `$top` page size | **Closed** | 100 per page default; bumped to 999 where Microsoft allows. |
| Token cache hit rate | **Closed** | Single token per tenant, refresh on <60 s remaining. |

## 5. Frontend

| Concern | Status | Notes |
|---|---|---|
| Server components for data | **Closed** | All page fetches happen in RSC; client islands only for grids + forms. |
| Bundle size | **Watch** | MUI-X DataGrid + `@mui/material` adds ~140 KB gzipped. Justified by 3+ data-heavy pages. Considering tree-shaking via per-import paths in Phase 27. |
| Demo-mode cookie | **Closed** | Middleware sets `tg365_demo` so sidebar Links don't carry `?demo=1`. |
| Memoisation | **Closed** | Tables don't re-fetch on filter changes (purely client-side filter on the small fixture sets). |
| Recharts lazy load | **Open** | The dashboard imports Recharts up-front. Lazy import on the dashboard alone would save ~60 KB. |

## 6. OpenSearch & object storage

| Concern | Status | Notes |
|---|---|---|
| Index per data class | **Closed** | `tg365-audit`, `tg365-signins`, `tg365-jobruns`. |
| ISM policy templates | **Open** | Document rolling 30-day policy in `docs/operations/runbook.md`. |
| Bulk indexing | **Closed** | `helpers.bulk` with 500-doc batches. |
| Export streaming | **Closed** | `boto3` `upload_fileobj` streams; no in-memory buffer. |

## 7. Caching

| Concern | Status | Notes |
|---|---|---|
| Redis as cache | **Closed** | Rate-limit buckets; session store; Graph delta tokens (encrypted). |
| HTTP caching headers | **Open** | API routes don't set `Cache-Control` / `ETag`. Most are user-specific so private only. |
| Front-end TanStack Query cache | **Closed** | Default 5-minute staleness on side-panel fetches. |

## 8. Observability

| Concern | Status | Notes |
|---|---|---|
| Structured JSON logs | **Closed** | `app/logging_setup.py`. |
| Request-ID propagation | **Closed** | `X-Request-ID` header injected if absent. |
| OpenTelemetry hooks | **Open** | Settings expose `OTEL_EXPORTER_OTLP_ENDPOINT`; SDK not yet initialised. |
| Sentry | **Closed** | Web + edge + server configs in `apps/web/sentry.*.config.ts`. API side TODO. |
| `/api/system/health` aggregated | **Closed** (Phase 26) | Surfaces DB/Redis/OpenSearch/MinIO + recent job stats. |

---

### Headline wins to land next

1. Move synchronous collector run to a background enqueue path.
2. Move report-list endpoints to keyset pagination.
3. Compress export responses.
4. Add OpenTelemetry traces — API + worker + Graph client.
5. Stuck-run reaper + cancel button.

These five take the API p99 from "low millisecond" to "low millisecond under
hostile tenant load" and remove the only known scale cliff (running 50 k+
SharePoint permissions through the OFFSET-based list endpoint).
