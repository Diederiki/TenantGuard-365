# M365 Enterprise Control Center

> Internal codename: **TenantGuard-365**
> Enterprise-grade Microsoft 365 reporting, auditing, monitoring, SharePoint visibility, and security operations platform.

This is a **defensive, read-first** platform for IT administrators of a Microsoft 365 tenant. It centralises reporting, auditing, SharePoint permission visibility, alerting, and security investigations. All destructive or remediation actions are **disabled by default** and live behind approval gates with full audit logging.

---

## Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0** | ✅ Done | Project blueprint, architecture docs, Microsoft Graph capability matrix, security model, monorepo skeleton, local Docker Compose skeleton |
| **Phase 1** | ✅ Done | FastAPI + Alembic baseline + Dramatiq worker + Next.js 14 dashboard + full Docker Compose + Makefile + CI |
| **Phase 2** | ✅ Done | Entra OIDC + mock auth, Redis-backed sessions, CSRF, RBAC `require()` dependency, technician audit log + viewer |
| **Phase 3** | ✅ Done | Encrypted Graph token cache (AES-GCM + tenant-bound HMAC), async Graph client with 429/Retry-After + exponential backoff + pagination + per-tenant concurrency |
| **Phase 4** | ✅ Done | Collector framework + entra.users, sharepoint.sites, serviceHealth collectors + GraphSyncJob run tracking |
| **Phase 5** | ✅ Done | Report engine + built-in reports + CSV / HTML / XLSX / PDF exporters (stdlib only) + ReportRun + ReportExport tables |
| **Phase 6** | ✅ Done | SharePoint inventory + permissions + sharing-links models and `sharepoint.sites.inventory` / `sharepoint.sharing.anonymous_links` reports |
| **Phase 7** | ✅ Done | Security rule engine + alerts (dedup + occurrence count) + investigation cases + 2 built-in rules (anonymous-link, active-guest) |
| **Phase 8** | ✅ Done | Content search framework + sensitive-info pattern library (email, IBAN, Visa, US SSN, AWS key) — feature flag gated |
| **Phase 9** | ✅ Done | Remediation framework + 5 policies (sharing-link, guest-from-group, disable-account, revoke-sessions, mailbox-forwarding) — all ship `enabled=false`, apply handlers stubbed |
| **Phase 10** | ✅ Done | Backup scripts (Postgres, OpenSearch snapshot, MinIO mirror), consent verifier, security-posture self-tests, integration test scaffold, production compose overlay |

See [ROADMAP.md](ROADMAP.md) for the detailed plan.

---

## Documentation Index

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture overview
- [SECURITY.md](SECURITY.md) — Security model, RBAC, audit, threat model
- [ROADMAP.md](ROADMAP.md) — Phased build plan
- [docs/architecture/overview.md](docs/architecture/overview.md) — Component diagram, dataflow
- [docs/architecture/data-model.md](docs/architecture/data-model.md) — Database schema
- [docs/architecture/modules.md](docs/architecture/modules.md) — Module breakdown
- [docs/microsoft-graph/capability-matrix.md](docs/microsoft-graph/capability-matrix.md) — Microsoft API capability matrix
- [docs/microsoft-graph/required-permissions.md](docs/microsoft-graph/required-permissions.md) — Required Graph / Purview / Defender permissions
- [docs/microsoft-graph/app-registration.md](docs/microsoft-graph/app-registration.md) — Entra app registration guide
- [docs/microsoft-graph/throttling.md](docs/microsoft-graph/throttling.md) — Graph throttling & retry strategy
- [docs/product/manageengine-feature-parity-matrix.md](docs/product/manageengine-feature-parity-matrix.md) — **Feature parity matrix** (72 entries · live status)
- [docs/product/tenantguard-feature-roadmap.md](docs/product/tenantguard-feature-roadmap.md) — Phased delivery plan (MVP / P2 / P3 / Future)
- [docs/product/report-catalog.md](docs/product/report-catalog.md) — Report catalog
- [docs/product/audit-catalog.md](docs/product/audit-catalog.md) — Audit catalog
- [docs/product/security-monitoring-catalog.md](docs/product/security-monitoring-catalog.md) — Security monitoring catalog
- [docs/product/sharepoint-catalog.md](docs/product/sharepoint-catalog.md) — SharePoint capability catalog
- [docs/product/unsupported-or-needs-validation.md](docs/product/unsupported-or-needs-validation.md) — Honest gap list
- [docs/operations/full-platform-verification-report.md](docs/operations/full-platform-verification-report.md) — Latest autonomous-run audit
- [docs/security/vulnerability-analysis.md](docs/security/vulnerability-analysis.md) — Running internal-security review
- [docs/operations/performance-efficiency-analysis.md](docs/operations/performance-efficiency-analysis.md) — Hot spots + headline wins
- [docs/admin/user-management.md](docs/admin/user-management.md) — Admin guide: user management
- [docs/admin/settings.md](docs/admin/settings.md) — Admin guide: settings
- [docs/security/threat-model.md](docs/security/threat-model.md) — Threat model
- [docs/security/auth-model.md](docs/security/auth-model.md) — Authentication model
- [docs/security/rbac.md](docs/security/rbac.md) — Role-based access control
- [docs/security/audit-model.md](docs/security/audit-model.md) — Technician & data-access audit model
- [docs/deployment/local-dev.md](docs/deployment/local-dev.md) — Local development setup
- [docs/deployment/production-vps.md](docs/deployment/production-vps.md) — Production VPS deployment

---

## Local startup

### Prerequisites

- Docker Desktop or Docker Engine **24+** with Compose v2
- 8 GB RAM minimum free for containers (OpenSearch is the heavy one)
- Ports free on host: `3000`, `5432`, `6379`, `8000`, `8025`, `9000`, `9001`, `9200`, `1025`

### First-time bootstrap

```bash
git clone https://github.com/Diederiki/TenantGuard-365.git
cd TenantGuard-365
cp .env.example .env
# Edit .env — change DEV_SESSION_SECRET, POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD before non-trivial use.

# Bring up the full stack (api/web/worker + infra)
make bootstrap        # = docker compose up -d  +  alembic upgrade head  +  seed

# Or step-by-step:
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed
```

Open http://localhost:3000 — the dashboard renders dark-mode by default and shows API + dependency health.

### Service URLs (local)

| Service | URL | Purpose |
|---------|-----|---------|
| Postgres | `localhost:5432` | Primary database |
| Redis | `localhost:6379` | Cache, queue broker, rate-coordination |
| OpenSearch | http://localhost:9200 | Audit/event/content search index |
| MinIO console | http://localhost:9001 | Object storage for exports |
| MinIO S3 API | http://localhost:9000 | S3-compatible API |
| Mailhog UI | http://localhost:8025 | Captures outbound dev email |
| Mailhog SMTP | `localhost:1025` | SMTP relay for dev |
| API | http://localhost:8000 | FastAPI backend (`/healthz`, `/readyz`, `/docs`) |
| Web | http://localhost:3000 | Next.js dashboard |

### Tear down

```bash
docker compose down            # stop containers, keep volumes
docker compose down -v         # stop and wipe all data volumes (destructive)
```

---

## What this currently does NOT do (by design)

- ❌ No Microsoft Graph calls yet — that begins in Phase 3 after the app registration is documented.
- ❌ No real authentication yet — mock-auth scaffolding in Phase 2.
- ❌ No remediation, no destructive actions — Phase 9, disabled by default.
- ❌ No production deployment yet — Phase 10.

---

## Reporting security issues

See [SECURITY.md](SECURITY.md). Do not file Microsoft-tenant–specific security findings as public GitHub issues.

---

## License

To be determined. Treat as internal proprietary code until a license is added.
