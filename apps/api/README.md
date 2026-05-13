# apps/api — FastAPI backend

> **Phase 0**: placeholder. The container in `docker-compose.yml` prints a banner and sleeps.
> **Phase 1**: this folder ships a real FastAPI service.

## Planned layout (Phase 1)

```
apps/api/
├── pyproject.toml
├── poetry.lock        (or requirements.lock with uv)
├── Dockerfile
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
│   ├── main.py                  # FastAPI app factory
│   ├── config.py                # Pydantic Settings, env-driven
│   ├── logging.py               # JSON logger, scrubber
│   ├── deps.py                  # FastAPI dependencies (db, current_user, require)
│   ├── auth/
│   │   ├── oidc.py              # Entra OIDC handler
│   │   ├── sessions.py
│   │   ├── csrf.py
│   │   ├── permissions.py
│   │   └── mock.py              # local-dev mock auth (refuses ENVIRONMENT=production)
│   ├── audit/
│   │   └── logger.py            # AuditLogger service — only insert path
│   ├── graph/
│   │   ├── client.py            # central Graph client wrapper
│   │   ├── token_cache.py       # AES-GCM encrypted cache
│   │   ├── retry.py
│   │   └── pagination.py
│   ├── modules/
│   │   ├── entra/
│   │   ├── exchange/
│   │   ├── sharepoint/
│   │   ├── onedrive/
│   │   ├── teams/
│   │   ├── security/
│   │   └── content_search/
│   ├── reports/
│   │   ├── engine.py
│   │   ├── export/
│   │   │   ├── csv.py
│   │   │   ├── xlsx.py
│   │   │   ├── pdf.py
│   │   │   └── html.py
│   │   └── schedule.py
│   ├── notifications/
│   ├── remediation/
│   ├── db/
│   │   ├── base.py              # SQLAlchemy 2.x declarative base
│   │   ├── session.py
│   │   └── models/...
│   └── health.py                # /healthz, /readyz
└── tests/
    ├── unit/
    └── integration/
```

## Local development (Phase 1+)

```bash
# from repo root
docker compose --profile app up -d api
docker compose exec api alembic upgrade head
docker compose exec api pytest -q
curl http://localhost:8000/healthz
```

## Coding standards (Phase 1+)

- Python 3.12
- Ruff (lint + format), mypy (`strict`)
- 100% type-annotated public surface
- Pytest, pytest-asyncio, httpx test client
- Every route uses `Depends(require(...))` for RBAC — checked by a custom linter
- Every audited action goes through `AuditLogger` — no raw inserts allowed
