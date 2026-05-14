# Admin guide — Settings

The settings area is at `/settings` once you sign in. It lists eight
cards; each links to a sub-page.

| Card | Status | Backing |
|---|---|---|
| Microsoft Graph connection | live | `tenant_graph_settings` row per tenant; secrets AES-GCM-sealed. |
| Platform users | live | `platform_users`; CRUD via `/api/settings/users`. |
| Delegation / RBAC | live | `platform_roles`, `platform_role_assignments`. |
| Audit trail | live | `technician_audit_log`. |
| General site settings | **framework** | Phase 27 will add a `tg365_site_settings` singleton row. |
| Security policy | **framework** | Read-only view of effective defaults (env + code). Editable copy lands Phase 27. |
| Data retention | **framework** | Phase 27 adds `retention_policy` table + nightly cleanup jobs. |
| Notifications | **framework** | SMTP via env. UI for severity routing + webhook config in Phase 27. |

## Microsoft Graph connection

`Settings → Graph` lets a platform admin paste:

- Entra tenant ID
- Portal app registration: client ID + client secret
- Collector app registration: client ID + client secret
- "Require TOTP 2FA for non-Entra users" toggle
- "Allow local password sign-in" toggle (off in production)

Secrets are encrypted-at-rest before the row is inserted; the API never
returns the plaintext back. The "Test connection" button on the form
fires a real Graph call against `serviceHealth.snapshot` and reports
row counts.

## Permissions

All settings routes require the `platform.admin` permission, except
user-management routes which need `platform.users.manage`. Front-end
nav still surfaces the cards to every signed-in admin; the API enforces.

## Environment variables that matter most

| Var | Purpose |
|---|---|
| `ENVIRONMENT` | `development` / `staging` / `production`. Gates mock auth and dev secret defaults. |
| `AUTH_MODE` | `mock` (dev) or `entra` (prod). |
| `DEV_SESSION_SECRET` | Cookie signer. Must be ≥ 16 chars and not the default in prod. |
| `TOKEN_CACHE_MASTER_KEY` | AES-GCM key for token + secret blobs. Required in prod. |
| `ENTRA_TENANT_ID` / `ENTRA_CLIENT_ID` / `ENTRA_CLIENT_SECRET` | Fallback Graph credentials when `tenant_graph_settings` has no row for the tenant. |
| `DATABASE_URL`, `REDIS_URL`, `OPENSEARCH_URL`, `MINIO_*` | Service endpoints. |
| `FEATURE_REMEDIATION_ENABLED` | Off by default. When true, individual policies still need to be enabled. |

See `.env.example` for the full list.
