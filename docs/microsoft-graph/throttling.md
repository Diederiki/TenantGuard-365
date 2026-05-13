# Microsoft Graph throttling & retry strategy

> Microsoft Graph applies multiple overlapping throttling layers (per-app, per-tenant, per-service). The platform must be a well-behaved caller or it will pull every tenant it manages into 429 storms.

## Defaults the Graph client enforces

| Setting | Default | Override |
|---------|---------|---------|
| Per-tenant concurrent in-flight requests | 4 | `GRAPH_PER_TENANT_CONCURRENCY` |
| Per-app global concurrent in-flight | 16 | `GRAPH_GLOBAL_CONCURRENCY` |
| Page size | 100 | `GRAPH_DEFAULT_PAGE_SIZE`, capped at 999 |
| Max retries on transient failure | 8 | `GRAPH_MAX_RETRIES` |
| Backoff base seconds | 1 | `GRAPH_BACKOFF_BASE_SECONDS` |
| Backoff cap seconds | 60 | `GRAPH_BACKOFF_CAP_SECONDS` |
| Hard timeout per request | 60 s | `GRAPH_REQUEST_TIMEOUT_SECONDS` |

## Retry policy

Retry is **opt-out per endpoint** — collectors register endpoints with the client and the client applies the appropriate policy.

```
on response:
  if status == 200: return body
  if status == 429:
      retry_after = response.headers.get("Retry-After")
      if retry_after is integer: sleep(retry_after)
      elif retry_after is HTTP-date: sleep(date - now)
      else: sleep(backoff(attempt))
      attempt += 1
      if attempt > GRAPH_MAX_RETRIES: raise
      continue
  if status in (500, 502, 503, 504):
      sleep(backoff(attempt))
      attempt += 1
      if attempt > GRAPH_MAX_RETRIES: raise
      continue
  if status == 401:
      refresh_token()
      retry once only
  if status == 403:
      no retry — surface permission gap immediately
  else:
      no retry — surface error to caller
```

`backoff(attempt) = min(GRAPH_BACKOFF_CAP_SECONDS, GRAPH_BACKOFF_BASE_SECONDS * 2 ** attempt) + jitter(±25%)`

## Pagination

- Always follow `@odata.nextLink` until absent or until a configured row cap is hit.
- Page size is request-scoped, set via `$top` where the endpoint supports it (most do up to 999; some — sign-ins, audits — cap lower).
- Pagination loop has a **page budget** per job to avoid runaway scans. If a job hits its budget without finishing it is marked `partial` and the next run resumes from the same delta link.

## Delta queries

- Whenever an endpoint exposes `$delta`, the collector stores the `deltaLink` in `graph_delta_tokens` (one row per tenant per resource).
- A scheduled "delta consumer" job uses the saved link.
- A "full refresh" job ignores the delta link and re-bootstraps from scratch (runs weekly by default).
- If a delta link returns `410 Gone`, drop it and re-bootstrap.

## Change notifications (webhooks)

For resources that support them (driveItems, messages, users, groups):

- Subscription rows live in `graph_webhook_subscriptions`.
- A renewal worker re-subscribes at 80% of the expiry window.
- Notifications are validated via `validationToken` on creation and HMAC-verified (where Microsoft signs them) on every delivery.
- Notifications enqueue a tightly-scoped delta fetch — the platform never trusts notification payload as authoritative state.

## Cancellation

- Every Graph call carries a `cancellation_token` linked to the worker job.
- API or operator can mark a job for cancellation; the client checks the flag before every request and on every `Retry-After` sleep.

## Metrics the client emits

- `graph_requests_total{tenant, endpoint, status}`
- `graph_request_duration_seconds_bucket{tenant, endpoint}`
- `graph_retries_total{tenant, endpoint, reason}`
- `graph_throttled_total{tenant, endpoint}`
- `graph_concurrency_inflight{tenant}`
- `graph_token_acquire_duration_seconds{tenant}`
- `graph_token_acquire_failures_total{tenant, reason}`

(Counters wired in Phase 3; Prometheus exporter wired in Phase 10.)

## Endpoint-specific hot spots

| Endpoint | Note |
|----------|------|
| `/auditLogs/signIns` | Strict throttling. Use `$filter` on `createdDateTime` and small windows (≤ 1 hour). |
| `/auditLogs/directoryAudits` | Same as above. |
| `/sites?search=*` | Server-side time limit; iterate by alphabet or by Graph search if your tenant is large. |
| `/drives/{id}/items/{id}/permissions` | Called many times during deep SharePoint scans — cap per-tenant concurrency hard. |
| `/reports/*` | Returns CSV, server-cached. Refresh max once every 30 minutes per report. |

## Surfacing throttling to the UI

- Per-tenant Graph health card shows: requests, throttle rate, average backoff, current concurrency.
- When throttle rate exceeds a threshold (default 5%) the UI shows a warning and recommends a per-tenant concurrency reduction.
