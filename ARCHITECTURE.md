# Architecture

> High-level architecture of the M365 Enterprise Control Center.
> Detailed component docs live in `docs/architecture/`.

## 1. Design goals

1. **Read-first, defensive.** Default posture is "observe and report"; any write action toward Microsoft 365 is opt-in, gated, audited, and dry-runnable.
2. **Modular.** Each Microsoft 365 surface (Entra, Exchange, SharePoint, OneDrive, Teams, Security, Compliance) is an independent module with its own collectors, models, reports, and rules.
3. **Scalable to millions of events.** Audit and SharePoint item tables must support millions of rows. Event storage uses time-partitioned Postgres tables for normalized fields and OpenSearch indexes for full-text/structured search.
4. **Graph-API native.** The platform speaks Microsoft Graph as the primary integration. Falls back to the Microsoft 365 Management Activity API or Exchange Online PowerShell only when no Graph endpoint exists.
5. **Least-privilege.** Permission scopes are documented per feature. Optional features that need higher privileges advertise that fact in the UI before they run.
6. **Auditable.** Every action a technician takes inside this platform — reports run, exports downloaded, searches executed, remediations approved — produces an immutable audit record.
7. **Future-ready.** New modules are added by registering a module manifest, not by patching core code.

## 2. Logical components

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              Browser (Admin)                              │
└──────────────────────────────────────────────────────────────────────────┘
                                    │ HTTPS
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  apps/web — Next.js 14 (App Router, TS) + Tailwind + shadcn/ui            │
│  - Entra OIDC sign-in                                                    │
│  - TanStack Query, TanStack Table                                        │
│  - Recharts                                                              │
│  - RBAC-aware navigation                                                 │
└──────────────────────────────────────────────────────────────────────────┘
                                    │ REST (cookie-bound JWT/session)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  apps/api — FastAPI (Python 3.12)                                         │
│  - OIDC verifier, session, CSRF                                          │
│  - RBAC enforcement                                                      │
│  - Report engine, export engine, scheduler                               │
│  - Investigation, alert, search APIs                                     │
│  - Remediation API (dry-run by default)                                  │
│  - Audit log writer                                                      │
└──────────────────────────────────────────────────────────────────────────┘
        │             │              │              │              │
        ▼             ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────────┐ ┌──────────┐ ┌──────────────┐
   │PostgreSQL│  │  Redis   │  │  OpenSearch  │ │  MinIO   │ │   Mailhog    │
   │ primary  │  │ cache+   │  │ audit+search │ │ exports  │ │   dev SMTP   │
   │   DB     │  │  queue   │  │   indices    │ │  bucket  │ │              │
   └──────────┘  └──────────┘  └──────────────┘ └──────────┘ └──────────────┘
        ▲             ▲              ▲              ▲
        │             │              │              │
┌──────────────────────────────────────────────────────────────────────────┐
│  apps/worker — Celery (or Dramatiq) workers + beat scheduler              │
│  - Graph collectors (users, groups, sites, drives, audits)               │
│  - Delta-token managers                                                  │
│  - Scheduled reports                                                     │
│  - Notification senders                                                  │
│  - Remediation executors (gated)                                         │
└──────────────────────────────────────────────────────────────────────────┘
                                    │ HTTPS (cert/secret auth)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              Microsoft Graph + Purview Audit + Defender APIs              │
└──────────────────────────────────────────────────────────────────────────┘
```

## 3. Service responsibilities

### apps/web — Next.js frontend
- Hosts the admin UI only. No direct calls to Microsoft Graph.
- Authenticates via Entra OIDC; sessions backed by HTTP-only, SameSite=Lax cookies.
- All data fetched from `apps/api` over REST. No service-account secrets in the browser.

### apps/api — FastAPI backend
- Single source of truth for authorization. RBAC is enforced on every endpoint, never trusted from the client.
- Hosts the report engine, export engine, scheduler API, alert engine, investigation API, content search API, and remediation API.
- Holds the encrypted Microsoft Graph token cache (per tenant connection).
- Writes structured JSON logs and audit records.

### apps/worker — Background workers + scheduler
- Runs all Microsoft Graph traffic. Web and API never call Graph directly for user-driven requests in a synchronous path — they enqueue a job.
- Hosts delta-token managers, change-notification handlers, and the remediation executor.
- Respects per-tenant concurrency limits and global throttling state held in Redis.

### PostgreSQL
- Primary database for tenant settings, RBAC, normalized M365 entities, sync job state, report metadata, audit logs.
- Time-series tables (`*_audit_events`, `entra_signins`, `sharepoint_audit_events`, etc.) use date partitioning.

### Redis
- Worker broker, cache, rate-limit token buckets, distributed locks.

### OpenSearch
- Full audit/event archive, content-search results, free-text search across SharePoint metadata.
- Indices partitioned by month for retention and rollover.

### MinIO
- Object storage for report exports, evidence bundles, and (later) backups.
- Locally swappable for AWS S3 / Azure Blob in production.

### Mailhog (dev) / SMTP relay (prod)
- Outbound email for scheduled reports, alerts, and notifications.

## 4. Microsoft Graph integration

See [docs/microsoft-graph/capability-matrix.md](docs/microsoft-graph/capability-matrix.md) for the per-feature endpoint and permission map.

The Graph client wrapper is a **single shared module** used by all collectors. It enforces:

- Per-tenant token cache (encrypted at rest).
- Automatic 429 / `Retry-After` handling.
- Exponential backoff with jitter when `Retry-After` is absent.
- Per-host concurrency caps.
- Pagination via `@odata.nextLink`.
- Delta queries via `@odata.deltaLink` where the resource supports them.
- Change notifications (webhooks) where supported, with renewal worker.
- Structured telemetry: requests, retries, throttled events, latencies.
- Hard cap on retries — a job that exceeds it fails to the queue rather than spinning forever.

## 5. Data model overview

See [docs/architecture/data-model.md](docs/architecture/data-model.md) for the full schema.

Key tables:

| Domain | Tables |
|--------|--------|
| Platform | `tenants`, `tenant_connections`, `platform_users`, `platform_roles`, `platform_permissions`, `platform_role_assignments`, `technician_audit_logs` |
| Graph | `graph_permissions`, `app_registrations`, `graph_sync_jobs`, `graph_sync_job_runs`, `graph_delta_tokens`, `graph_webhook_subscriptions` |
| Entra | `m365_users`, `m365_groups`, `m365_group_memberships`, `m365_roles`, `m365_role_assignments`, `m365_licenses`, `entra_signins`, `entra_directory_audits` |
| Exchange | `exchange_mailboxes`, `exchange_mailbox_permissions`, `exchange_mailbox_audit_events` |
| SharePoint | `sharepoint_sites`, `sharepoint_lists`, `sharepoint_drives`, `sharepoint_items`, `sharepoint_permissions`, `sharepoint_sharing_links`, `sharepoint_audit_events` |
| OneDrive | `onedrive_accounts`, `onedrive_audit_events` |
| Teams | `teams`, `teams_channels`, `teams_members`, `teams_audit_events` |
| Service health | `service_health_overviews`, `service_health_issues` |
| Security | `security_alerts`, `security_rules`, `security_rule_matches`, `investigation_cases`, `investigation_case_events` |
| Reporting | `saved_reports`, `report_runs`, `report_exports`, `scheduled_reports` |
| Notifications | `notification_channels`, `notification_events` |
| Content search | `content_search_profiles`, `content_search_runs` |
| Remediation | `remediation_policies`, `remediation_actions`, `remediation_approvals` |

Audit/event tables use `BIGSERIAL` IDs and Postgres `PARTITION BY RANGE (event_time)` monthly partitions.

## 6. Authentication & RBAC

See [docs/security/auth-model.md](docs/security/auth-model.md) and [docs/security/rbac.md](docs/security/rbac.md).

- Production: Entra OIDC only.
- Local dev: optional mock-auth flag (`AUTH_MODE=mock`), refuses to start when `ENVIRONMENT=production`.
- Built-in roles: `Platform Admin`, `Security Analyst`, `SharePoint Auditor`, `Exchange Auditor`, `Helpdesk`, `Read-only Auditor`, `Report-only`.
- All roles can be cloned and edited; permissions are atomic (`reports.run`, `sharepoint.audit.read`, `remediation.approve`, etc.).
- Delegation supports scoping by tenant, domain, SharePoint site, department, or region.

## 7. Auditing

See [docs/security/audit-model.md](docs/security/audit-model.md).

Every privileged action writes a record to `technician_audit_logs`. Records are append-only at the application layer; database-level immutability is enforced via a deny-update/delete policy and offsite log shipping in production.

## 8. Remediation safety

- All remediation actions ship **disabled by default**.
- Each action has an explicit policy (`remediation_policies`) describing what it does, what permission it needs, whether it requires approval, whether it supports rollback, and whether dry-run is the default.
- Approval workflow stored in `remediation_approvals`. A second technician with `remediation.approve` must sign off before any destructive call to Microsoft Graph.
- Every dry-run records what *would* have been changed. Every live run records before/after where safe.

## 9. Observability

- Structured JSON logs with request ID, correlation ID, tenant ID, actor, action.
- OpenTelemetry-ready hooks; OTLP exporter is config-driven (off locally, on in production).
- Worker, API, and Graph client all expose Prometheus-style counters (deferred until Phase 10).

## 10. Deployment shapes

- **Local dev**: Docker Compose, single host, all services on one network.
- **Production VPS**: Docker Compose with a separate `docker-compose.prod.yml` overlay, Caddy or Nginx reverse proxy, Let's Encrypt TLS, encrypted secrets, off-host backups for Postgres + MinIO.

See [docs/deployment/production-vps.md](docs/deployment/production-vps.md).
