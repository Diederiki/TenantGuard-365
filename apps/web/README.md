# apps/web — Next.js frontend

> **Phase 0**: placeholder. The container in `docker-compose.yml` prints a banner and sleeps.
> **Phase 1**: this folder ships a real Next.js 14 (App Router) frontend.

## Planned layout (Phase 1)

```
apps/web/
├── package.json
├── pnpm-lock.yaml             (pnpm preferred; npm/yarn acceptable)
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.cjs
├── Dockerfile
├── public/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                  # global dashboard
│   ├── (auth)/
│   │   └── sign-in/page.tsx
│   ├── overview/
│   ├── reports/
│   ├── audit-logs/
│   ├── security/
│   │   ├── alerts/
│   │   └── investigations/
│   ├── entra/
│   ├── exchange/
│   ├── sharepoint/
│   ├── onedrive/
│   ├── teams/
│   ├── service-health/
│   ├── content-search/
│   ├── scheduled-reports/
│   ├── jobs/
│   ├── delegation/
│   ├── settings/
│   ├── graph-connection/
│   └── api/                      # Next route handlers (BFF only — auth callbacks, file streams)
├── components/
│   ├── ui/                       # shadcn/ui generated primitives
│   ├── tables/                   # TanStack Table wrappers
│   ├── charts/                   # Recharts wrappers
│   └── layout/                   # sidebar, top bar, breadcrumbs
├── lib/
│   ├── api.ts                    # TanStack Query client
│   ├── auth.ts                   # session helpers (server-side)
│   └── rbac.ts                   # client-side permission check helpers (cosmetic)
└── tests/
    └── e2e/                      # Playwright tests (run from /tests)
```

## Local development (Phase 1+)

```bash
docker compose --profile app up -d web
docker compose logs -f web
open http://localhost:3000
```

## UI principles

- Dark mode by default; light mode available.
- Sidebar navigation with module groups (Overview, Reports, Audit, Security, M365 modules, Admin).
- Top tenant selector, global search, notification bell, job status.
- Large-table support via TanStack Table; virtualisation for > 5 000 rows.
- Filter chips, date range picker, severity badges.
- RBAC-aware navigation: hide what the user can't see; the API will still 403 if bypassed.
- Empty / loading / error states for every screen.
- All data fetch via TanStack Query; no Redux.

## Build & deploy

- Standalone output (`next.config.mjs: output: 'standalone'`).
- Multi-stage Dockerfile (Phase 1).
- No service-account secrets in the browser bundle; all sensitive calls proxied through `apps/api`.
