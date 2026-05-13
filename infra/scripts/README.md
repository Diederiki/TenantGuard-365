# infra/scripts

Operational helper scripts.

| Script (planned) | Phase | Purpose |
|------------------|-------|---------|
| `backup-postgres.sh` | 10 | Nightly `pg_dump` + off-host upload |
| `snapshot-opensearch.sh` | 10 | Trigger and verify OpenSearch snapshot |
| `mirror-minio.sh` | 10 | `mc mirror` to off-host S3 |
| `verify-consent.py` | 3 | Compare granted Graph scopes to required set |
| `seed-demo.py` | 1 | Seed local-dev tenant, admin, sample reports |
| `wal-shipper.sh` | 10 | Ship Postgres WAL files |

Phase 0 ships no scripts beyond `make` targets in the top-level Makefile.
