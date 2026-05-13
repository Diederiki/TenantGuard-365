# Monitoring

> Monitoring strategy. Wired in Phase 10; documented here so we don't paint ourselves into a corner.

## Layers

1. **Container liveness** — Docker / orchestrator's health checks.
2. **Application health** — `/healthz` (process up), `/readyz` (dependencies up).
3. **Domain metrics** — Graph error rate, collector lag, audit-shipper backlog, queue depth.
4. **External probes** — Hit the public URL from a third-party check (UptimeRobot, healthchecks.io, internal nagios).
5. **Logs** — Structured JSON; shipped to a SIEM in production.
6. **Audit** — Already covered in [docs/security/audit-model.md](../security/audit-model.md).

## Endpoints

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `GET /healthz` | Process is alive (no dependency checks). Returns 200 if running. | none |
| `GET /readyz` | Dependencies reachable (DB, Redis, OpenSearch, MinIO). 503 if any down. | none, rate-limited |
| `GET /metrics` | Prometheus-format metrics. | bearer token (`METRICS_TOKEN`) |
| `GET /api/system/status` | Rich JSON: per-collector last success, Graph error rate, queue depth, audit backlog. | RBAC `platform.status.read` |

## Metrics catalogue (initial)

### API
- `http_requests_total{route, method, status}`
- `http_request_duration_seconds_bucket{route, method}`
- `rbac_denied_total{permission}`
- `report_runs_total{report_id, format, result}`
- `report_export_bytes_total{format}`
- `audit_records_written_total{category, result}`

### Worker / Graph
- `graph_requests_total{tenant, endpoint, status}`
- `graph_request_duration_seconds_bucket{tenant, endpoint}`
- `graph_retries_total{tenant, endpoint, reason}`
- `graph_throttled_total{tenant, endpoint}`
- `graph_concurrency_inflight{tenant}`
- `graph_token_acquire_failures_total{tenant, reason}`
- `collector_runs_total{module, collector, result}`
- `collector_lag_seconds{module, collector}`
- `webhook_subscriptions_expiring_total`

### Audit shipper
- `audit_shipper_high_water_mark` (gauge: epoch seconds of most recently shipped record)
- `audit_shipper_backlog_seconds` (gauge: now − high water)
- `audit_shipper_failures_total{reason}`

### Queues
- `queue_depth{queue}`
- `queue_in_flight{queue}`
- `queue_dead_letters_total{queue}`

## Alerts (suggested thresholds)

| Alert | Condition | Severity |
|-------|-----------|----------|
| API readyz failing | `/readyz` non-200 for > 2 min | Critical |
| Postgres unreachable | API or worker logs DB connect error > 1/min | Critical |
| OpenSearch yellow > 1h | `_cluster/health.status != green` for > 1 h | Trouble |
| Graph throttle rate high | `graph_throttled_total / graph_requests_total > 0.05` over 15 min | Trouble |
| Collector lag | `collector_lag_seconds > 3 * scheduled_interval` | Attention |
| Audit shipper backlog | `audit_shipper_backlog_seconds > 3600` | Trouble |
| Dead-letter queue | `increase(queue_dead_letters_total[15m]) > 0` | Attention |
| Disk usage | `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.15` | Trouble |

## Log shipping

- Containers log to stdout/stderr in JSON.
- Caddy logs in JSON.
- Suggested ship targets:
  - Elastic Stack (Filebeat → Elastic).
  - Loki (Promtail → Loki).
  - SIEM (e.g. Sentinel via syslog forwarder).

## Tracing

- OpenTelemetry SDK hooked in API and worker; OTLP exporter disabled locally.
- Suggested back-end: Honeycomb, Tempo, Jaeger.

## Dashboards (suggested)

Provided as Grafana JSON in `infra/grafana/` in Phase 10:

- **Platform overview** — request rates, latencies, error rate, active sessions.
- **Graph health** — per-tenant request volume, throttle rate, average backoff.
- **Collectors** — runs/min, success rate, lag.
- **Audit & remediation** — audit writes/min, shipper backlog, pending approvals.
- **Infra** — Postgres connections, Redis ops/sec, OpenSearch heap, MinIO IOPS.
