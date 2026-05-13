# tests

Test layout for the platform.

## Layout

```
tests/
├── unit/             # fast in-process tests (mostly under apps/api/tests/unit/)
├── integration/      # services up: DB, Redis, OpenSearch
├── e2e/              # Playwright; web + api + worker; mocked Graph
├── security/         # OWASP-style checks: CSRF, RBAC bypass, header presence
└── load/             # k6 / locust scenarios — report tables, audit ingestion
```

## Mocked Microsoft Graph

A `tests/integration/fixtures/graph/` directory ships a mock Graph server (FastAPI app behind `pytest_httpx` or a real `httpserver`) so the entire collection pipeline can be exercised without hitting Microsoft. Fixtures include:

- Tenant with 1 000 users, 200 groups, 50 SharePoint sites, 10 OneDrives
- Sample audit events with realistic shapes
- 429 / `Retry-After` scenarios
- Delta link issuance and expiry

## Targets

- Unit: < 1 minute on a laptop. Run on every commit.
- Integration: < 5 minutes. Run in CI per PR.
- E2E: < 15 minutes. Run on merge to main.
- Security: < 5 minutes. Run per PR.
- Load: on demand; not in CI gate.
