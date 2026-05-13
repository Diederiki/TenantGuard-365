# packages/shared-types

> Single source of truth for cross-cutting types used by both the API (Python) and the web (TypeScript).
>
> **Phase 0**: empty. **Phase 1**: this folder ships a generator pipeline.

## Strategy

- Define canonical models in Python (Pydantic v2) under `apps/api/app/schemas/`.
- A generator emits TypeScript types into `packages/shared-types/dist/` for the web app to import.
- Tooling: `datamodel-code-generator` or `openapi-typescript` driven from `/openapi.json` produced by FastAPI.

## What lives here

- Enums (`Severity`, `RemediationStatus`, `AlertStatus`, ...)
- DTOs returned by the API
- Filter and column-chooser shapes
- Permission strings (constants)

## What does NOT live here

- ORM models — those stay in `apps/api/app/db/models/`.
- UI-only types — those stay in `apps/web/`.

## Build (Phase 1+)

```bash
docker compose exec api python -m app.scripts.export_schema > openapi.json
docker compose exec api pnpm --filter shared-types generate
```
