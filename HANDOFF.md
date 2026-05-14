# Session handoff

Concise state-of-the-world for the next session. Read this first.

## Repo

- `C:\tenantguard365` · github.com/Diederiki/TenantGuard-365 · branch `main`
- Last green CI commit: `274ce1a` (Phase 27). All 5 CI jobs (api, worker,
  web, compose, cypress) green.
- All work is pushed.

## What just landed (Phases 25 + 26 + 27)

### Phase 27 — security headers, role-ceiling guard, account lockout, Cypress CI

**Security**
- Full Content-Security-Policy on the web (`next.config.mjs`) and a
  JSON-only CSP on the API (`main.py`). Both apps now also set the
  expanded Permissions-Policy, COOP, CORP, and HSTS.
- Privilege-escalation guard on `POST /api/settings/users`. Caller
  cannot grant a role whose permission set is not a subset of their own
  (`platform.admin` bypass intentional).
- Account lockout on local login. Redis-backed; 10 fails → 15 min lock;
  returns 423 `account_locked`. Counter clears on success.

**Tests**
- Demo-mode short-circuit in `lib/api.ts` so every page renders without
  a live API when the `tg365_demo=1` cookie is set.
- /settings/graph now mounts the GraphForm (Save + Test connection).
- Cypress smoke suite ran locally — 8 / 8 pass.
- New CI job `web · cypress smokes`: builds, runs `next start`, runs the
  spec headless in Electron, uploads screenshots on failure. **Passing.**


### Phase 25 — local auth + TOTP challenge + token-provider DB-first

**Backend**
- `POST /auth/login/local` — email + password (+ optional TOTP code). Returns
  `401 totp_required` when the user has TOTP enrolled but no code was sent.
  Constant-time-ish on unknown emails by always running a bcrypt compare.
- `POST /api/settings/users/{id}/password` — admin sets/resets a local
  password. Min length 12, bcrypt-hashed (`bcrypt==4.2.1`).
- TOTP enroll now also returns `qr_svg_base64` (rendered server-side).
- Rate-limit middleware: extra strict bucket on `/auth/login/local`
  (10 / 5 min) and `*/totp/verify` (5 / min).
- `build_token_provider` reads `tenant_graph_settings` first, env fallback.
- `wrap_app_secret` / `unwrap_app_secret` extracted to the model module
  (shared between `settings_routes` and `token_provider`).

**Web**
- `TotpEnroll` renders the QR inline.
- `Settings → Graph` has a working "Test connection" button hitting
  `serviceHealth.snapshot`.
- `middleware.ts` sets a `tg365_demo=1` cookie when `?demo=1` is in the URL
  so sidebar Links no longer have to propagate the param.

### Phase 26 — MUI-X DataGrid, Cypress, system health, settings framework, full audit

**Frontend (8 new pages + 1 rewrite)**
- `@mui/x-data-grid@7` + `@mui/material@6` + emotion. Wrapper at
  `components/data-grid/TgDataGrid.tsx` with a dark theme provider.
- Rewrites: `/audit` (DataGrid).
- New: `/entra/users`, `/sharepoint/permissions`, `/system-health`,
  `/settings/general`, `/settings/security`, `/settings/retention`,
  `/settings/notifications`.
- Sidebar surfaces the new sub-pages.

**Backend**
- `GET /api/system/health` (admin-only) — aggregates DB / Redis /
  OpenSearch / MinIO health plus recent `GraphSyncJobRun` stats.

**Tests**
- Cypress installed (`devDependencies`). `cypress.config.ts` + 8 smoke
  specs in `cypress/e2e/smoke.cy.ts`. `npm run e2e` to run.

**Docs**
- `docs/security/vulnerability-analysis.md`
- `docs/operations/performance-efficiency-analysis.md`
- `docs/operations/full-platform-verification-report.md`
- `docs/admin/user-management.md`
- `docs/admin/settings.md`

## What is still pending (Phase 28 queue, highest value first)

1. **Nonce-based CSP** — drop `'unsafe-inline'` from script-src + style-src
   via Next middleware injecting a per-request nonce.
2. **DB-backed versions of the four settings framework pages** — General,
   Security, Retention, Notifications. Need a `tg365_site_settings`
   singleton + a `retention_policy` table + an SMTP/webhook config table.
3. **Append-only DB role on `technician_audit_log`** — Postgres RLS / role
   that lacks UPDATE/DELETE.
4. **Stuck-run reaper + cancel** for `GraphSyncJobRun` rows left in
   `running`. Add `cancel_requested_at` column.
5. **OpenTelemetry init** — settings already expose
   `OTEL_EXPORTER_OTLP_ENDPOINT`; wire the SDK in `main.py`.
6. **Brotli** middleware on the `/api/reports/*/export` paths.
7. **Password-strength + breached-password check** on
   `set_user_password`. Use zxcvbn + Pwned Passwords k-anonymity API.
8. **Dependabot / pip-audit** in CI.

## Quick start next session

```bash
cd C:\tenantguard365
git pull
docker compose up -d --build
# Visit http://localhost:3000?demo=1 to bootstrap the demo cookie.
# Visit http://localhost:3000/audit, /entra/users, /sharepoint/permissions,
# /system-health, /settings to verify the new pages render.

# Smoke tests:
cd apps/web
npm run dev &
npx wait-on http://localhost:3000
npm run e2e
```

If CI fails, expected hotspots are noted in the vulnerability + performance
docs.

## Numbers as of this commit

- 27 phases shipped.
- 11 collectors · 16 reports · 8 security rules · 5 remediation policies
  (all off) · 5 SI patterns.
- 57 Postgres tables.
- ~24 frontend pages live (including the 8 added this phase).
- ~6 new API endpoints since the Phase 24 cut.

## Known limitations to mention to user next session

- Cypress smoke suite **8 / 8 green** locally + in CI.
- The four "framework" settings pages are read-only scaffolds. They show
  the effective defaults so they're useful to operators, but submit/save
  is intentionally disabled until the backing tables ship.
- `/entra/users` and `/sharepoint/permissions` only have data in demo
  mode. Real Graph data needs the corresponding collector to run; the
  pages will appear empty otherwise with a clear "configure Graph" hint.
- CSP still allows `'unsafe-inline'` for scripts and styles. Required by
  Next.js hydration JSON + MUI emotion. Phase 28 swaps in a nonce policy.
