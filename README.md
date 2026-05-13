# M365 Enterprise Control Center

> Internal codename: **TenantGuard-365**
> Enterprise-grade Microsoft 365 reporting, auditing, monitoring, SharePoint visibility, and security operations platform.

This is a **defensive, read-first** platform for IT administrators of a Microsoft 365 tenant. It centralises reporting, auditing, SharePoint permission visibility, alerting, and security investigations. All destructive or remediation actions are **disabled by default** and live behind approval gates with full audit logging.

---

## Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0** | ✅ In progress | Project blueprint, architecture docs, Microsoft Graph capability matrix, security model, monorepo skeleton, local Docker Compose skeleton |
| Phase 1 | ⏳ Pending | Repo bootstrap (FastAPI + Next.js + Postgres + Redis + OpenSearch + MinIO + Mailhog) |
| Phase 2 | ⏳ Pending | Authentication (Entra OIDC), RBAC, technician audit trail |
| Phase 3 | ⏳ Pending | Microsoft Graph connection center, app registration wizard, permission gap detector |
| Phase 4 | ⏳ Pending | Core data collectors (users, groups, licenses, SharePoint inventory, sharing, sign-ins, audits) |
| Phase 5 | ⏳ Pending | Dashboard and report engine (CSV/XLSX/PDF/HTML export, scheduling) |
| Phase 6 | ⏳ Pending | SharePoint deep audit (inheritance, broken inheritance, sharing, anonymous links, orphans) |
| Phase 7 | ⏳ Pending | Unified audit ingestion + security rule engine + investigation workflow |
| Phase 8 | ⏳ Pending | Content search & investigations (regex/pattern, scheduled, RBAC-gated) |
| Phase 9 | ⏳ Pending | Remediation framework (dry-run, approval workflow, disabled by default) |
| Phase 10 | ⏳ Pending | Enterprise hardening, tests, backup/restore, production VPS deploy |

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
- [docs/security/threat-model.md](docs/security/threat-model.md) — Threat model
- [docs/security/auth-model.md](docs/security/auth-model.md) — Authentication model
- [docs/security/rbac.md](docs/security/rbac.md) — Role-based access control
- [docs/security/audit-model.md](docs/security/audit-model.md) — Technician & data-access audit model
- [docs/deployment/local-dev.md](docs/deployment/local-dev.md) — Local development setup
- [docs/deployment/production-vps.md](docs/deployment/production-vps.md) — Production VPS deployment

---

## Local startup (Phase 0 skeleton)

Phase 0 ships **infrastructure only** so you can validate the stack on your machine before any feature work begins. The `api`, `web`, and `worker` containers are placeholders that print a banner and exit cleanly — they are filled in during Phase 1.

### Prerequisites

- Docker Desktop or Docker Engine **24+** with Compose v2
- 8 GB RAM minimum free for containers (OpenSearch is the heavy one)
- Ports free on host: `5432`, `6379`, `9200`, `9000`, `9001`, `8025`, `1025`

### First-time bootstrap

```bash
git clone https://github.com/Diederiki/TenantGuard-365.git
cd TenantGuard-365
cp .env.example .env
# Edit .env — at minimum, change DEV_SESSION_SECRET and POSTGRES_PASSWORD before any non-dev use.
docker compose up -d postgres redis opensearch minio mailhog
docker compose ps
```

You should see five healthy infrastructure containers.

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
| API (Phase 1+) | http://localhost:8000 | FastAPI backend |
| Web (Phase 1+) | http://localhost:3000 | Next.js frontend |

### Tear down

```bash
docker compose down            # stop containers, keep volumes
docker compose down -v         # stop and wipe all data volumes (destructive)
```

---

## What Phase 0 deliberately does NOT do

- ❌ No Microsoft Graph calls — that begins in Phase 3 after the app registration is documented.
- ❌ No user-facing screens — Phase 5 onward.
- ❌ No remediation, no destructive actions — Phase 9, disabled by default.
- ❌ No production deployment — Phase 10.

---

## Reporting security issues

See [SECURITY.md](SECURITY.md). Do not file Microsoft-tenant–specific security findings as public GitHub issues.

---

## License

To be determined. Treat as internal proprietary code until a license is added.
