# Roadmap

> Phased delivery plan. Phase 0 is "design & blueprint"; Phases 1–10 are implementation.
> Each phase ends with a working, demoable slice and updated documentation.

## Phase 0 — Project blueprint & feasibility (current)

**Goal:** establish architecture, security model, Microsoft API capability matrix, and a runnable infrastructure skeleton.

- [x] `README.md`, `ARCHITECTURE.md`, `SECURITY.md`, `ROADMAP.md`
- [x] `docs/architecture/` (overview, data model, modules)
- [x] `docs/security/` (threat model, auth model, RBAC, audit model)
- [x] `docs/microsoft-graph/` (capability matrix, required permissions, app registration, throttling)
- [x] `docs/deployment/` (local dev, production VPS)
- [x] `docs/operations/` (runbooks, monitoring, backup-restore)
- [x] Monorepo skeleton (`apps/`, `packages/`, `infra/`, `tests/`)
- [x] Docker Compose with Postgres, Redis, OpenSearch, MinIO, Mailhog running
- [x] `.env.example` and `.gitignore`
- [x] Placeholder app images so `docker compose config` validates
- [ ] No risky write/remediation actions implemented (intentional)

**Exit criteria:** `docker compose up -d postgres redis opensearch minio mailhog` brings up all five healthy. All Phase 0 docs reviewed.

---

## Phase 1 — Repo bootstrap

**Goal:** functional FastAPI + Next.js + worker stack with health checks and migrations.

- FastAPI app with `/healthz`, `/readyz`, structured JSON logs
- Next.js app with `/` placeholder, Tailwind, shadcn/ui
- Worker container (Celery or Dramatiq) consuming Redis
- Alembic configured against Postgres with one baseline migration
- Makefile / task runner for `make up`, `make migrate`, `make seed`, `make test`
- Pre-commit (ruff, mypy, eslint, prettier) configured
- Seed data: one tenant, one admin, sample saved report
- CI pipeline scaffold (lint + unit tests)

---

## Phase 2 — Authentication & platform RBAC

- Entra OIDC sign-in (auth-code + PKCE)
- Session middleware, CSRF, CSP, secure cookie defaults
- `platform_users`, `platform_roles`, `platform_permissions`, `platform_role_assignments`
- Built-in roles seeded: Platform Admin, Security Analyst, SharePoint Auditor, Exchange Auditor, Helpdesk, Read-only Auditor, Report-only
- Permission dependency for every API route
- Technician audit log writer + viewer screen
- Dev mock-auth (refuses to run in production)

---

## Phase 3 — Microsoft Graph Connection Center

- Tenant connection wizard (UI + API)
- App registration guide rendered in-app with checklist
- Admin consent status pull
- Permission gap detector — compares granted scopes against `docs/microsoft-graph/required-permissions.md`
- Graph client wrapper with:
  - encrypted per-tenant token cache
  - 429 + `Retry-After` handling
  - exponential backoff with jitter
  - pagination helper
  - delta-token storage
  - concurrency limits per tenant
- "Test connection" diagnostic screen
- API health screen

---

## Phase 4 — Core data collectors

Collectors with manual run, scheduled run, status, last success/failure, logs, retry, metrics, and test coverage:

- Users (`/users` + delta)
- Groups + memberships (`/groups` + delta)
- Licenses (`/subscribedSkus`, `/users/{id}/licenseDetails`)
- Roles + role assignments (`/directoryRoles`, `/roleManagement/directory/roleAssignments`)
- Service health (`/admin/serviceAnnouncement/healthOverviews`, `/issues`)
- Usage reports (`/reports/getOffice365ActiveUserDetail`, etc.)
- SharePoint site inventory (`/sites`, search-based)
- SharePoint drive/list inventory
- Sharing permissions (`/sites/{id}/permissions`, `/drives/{id}/items/{id}/permissions`)
- Sign-ins (`/auditLogs/signIns`) — license-dependent
- Directory audits (`/auditLogs/directoryAudits`)

---

## Phase 5 — Dashboard & report engine

- Global dashboard (M365 overview)
- Per-module dashboards (Entra, SharePoint, Security; Exchange/Teams placeholders)
- Report list, report detail, report builder
- Saved filters, column chooser, advanced filters
- Export engine: CSV, XLSX, PDF, HTML — streaming where size warrants
- Scheduled report engine (daily/weekly/monthly/cron)
- Email delivery via Mailhog locally
- Report run history and access control

---

## Phase 6 — SharePoint deep audit

- SharePoint explorer tree
- Site, library, list detail pages
- Permission inheritance scanner
- Broken inheritance report
- Unique permissions report
- External / anonymous / company-wide sharing reports
- Guest access report
- Orphaned users/groups report
- Large libraries/lists detection
- Inactive sites report
- Exportable SharePoint permission matrix

---

## Phase 7 — Unified audit & security ops

- Audit event ingestion (Graph audit endpoints + Purview Audit Search where licensed)
- Event normalisation
- OpenSearch indexing with monthly rollover
- Security rule engine (DSL → match → alert)
- Alert profiles, severities, suppression, dedup
- Investigation case workflow (create, assign, comment, link evidence)
- Entity profile pages (user, mailbox, site, file, IP, app)
- Microsoft Graph Security API + Defender XDR advanced hunting integration

---

## Phase 8 — Content search & investigations

- Saved search profiles
- Scheduled search jobs
- Regex/pattern matching with sensitive-info pattern library
- Search result metadata + snippets (no raw content by default)
- Alert on match
- Strict RBAC: `content_search.run`, `content_search.export`
- Legal/compliance warning screen before first run
- Full audit trail of every search and export

---

## Phase 9 — Remediation framework (disabled by default)

- Remediation policy table
- Action queue
- Dry-run mode (default)
- Two-person approval workflow
- Action result + rollback notes
- Example policies (placeholders, not active):
  - Disable risky sharing link
  - Remove external guest from group
  - Disable account
  - Revoke sign-in sessions
  - Remove mailbox forwarding rule

No remediation action ships in `enabled` state until the operator explicitly opts in per-policy, with an approval chain configured.

---

## Phase 10 — Enterprise hardening

- Unit, integration, E2E (Playwright), and security tests
- Load tests targeting report tables and OpenSearch
- Dependency scanning + container scanning in CI
- Backup/restore scripts for Postgres + MinIO + OpenSearch snapshots
- Production `docker-compose.prod.yml` overlay
- Caddy + Nginx reference configs
- Let's Encrypt TLS guide
- VPS deployment guide (Ubuntu 24.04)
- Monitoring guide (Prometheus + Grafana suggestions)
- Disaster recovery playbook
- Production security checklist signed off
