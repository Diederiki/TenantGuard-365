# Backup & restore

> Backup strategy. Verified quarterly via R-007 in [runbooks.md](runbooks.md).

## What we back up

| Data | Strategy | Default retention |
|------|----------|-------------------|
| Postgres (`tg365` database) | Nightly `pg_dump --format=custom` + continuous WAL archiving in production | 30 daily, 12 monthly |
| OpenSearch indices | Daily snapshot to MinIO repository | 30 daily |
| MinIO buckets (`tg365-exports`, `tg365-evidence`) | `mc mirror` to off-host S3-compatible target with object-lock | 90 days, then archived |
| Configuration (`.env`, Caddyfile) | Tracked in secret store / config repo (out-of-band) | Versioned indefinitely |
| Container images | Pulled from a pinned registry digest; no local backup needed | – |

We **do not** back up Redis. Redis holds ephemeral state (queues, cache). A Redis loss means in-flight jobs are re-queued from Postgres on restart.

## Postgres — nightly dump

```bash
# /opt/tg365/backups/postgres/run.sh
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/opt/tg365/backups/postgres/tg365-${TS}.dump
docker compose exec -T postgres \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  --format=custom --compress=9 --no-owner --no-privileges \
  > "$OUT"
sha256sum "$OUT" > "${OUT}.sha256"

# Off-host
mc cp "$OUT" off-host/tg365-backups/postgres/
mc cp "${OUT}.sha256" off-host/tg365-backups/postgres/
```

Run from cron at 02:00 local. Retention pruning by `find -mtime +30` for daily, monthly-pin one file.

## Postgres — restore

```bash
# Stop apps (keep DB up if you're restoring to it; otherwise spin up a clean Postgres).
docker compose stop api worker

# Drop and recreate the schema (DESTRUCTIVE — verify the dump first).
docker compose exec -T postgres \
  psql -U "$POSTGRES_USER" -d postgres \
  -c "DROP DATABASE IF EXISTS $POSTGRES_DB; CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;"

# Restore
docker compose exec -T postgres \
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges \
  < /opt/tg365/backups/postgres/tg365-YYYYMMDDTHHMMSSZ.dump

# Bring apps back
docker compose start api worker
docker compose exec api alembic current
```

## Postgres — WAL archive (production)

Set in `docker-compose.prod.yml` for the `postgres` service:

```yaml
command: >
  postgres
  -c wal_level=replica
  -c archive_mode=on
  -c "archive_command=test ! -f /backups/wal/%f && cp %p /backups/wal/%f"
  -c archive_timeout=300
volumes:
  - postgres-data:/var/lib/postgresql/data
  - ./backups/postgres:/backups
```

A sidecar `wal-shipper` periodically `mc cp`'s the WAL files off-host.

PITR (point-in-time recovery) procedure: base backup + WAL replay to a target timestamp. Documented in Phase 10.

## OpenSearch — snapshots

1. Register a snapshot repository pointed at MinIO (one-time):

```bash
curl -X PUT http://opensearch:9200/_snapshot/tg365-snap \
  -H 'Content-Type: application/json' \
  -d '{
        "type": "s3",
        "settings": {
          "bucket": "tg365-os-snapshots",
          "endpoint": "minio:9000",
          "protocol": "http",
          "path_style_access": true
        }
      }'
```

2. Daily snapshot:

```bash
SNAP=$(date -u +%Y%m%d)
curl -X PUT "http://opensearch:9200/_snapshot/tg365-snap/snap-${SNAP}?wait_for_completion=false"
```

3. Restore (target index pattern only):

```bash
curl -X POST "http://opensearch:9200/_snapshot/tg365-snap/snap-YYYYMMDD/_restore" \
  -H 'Content-Type: application/json' \
  -d '{ "indices": "tg365-entra-signins-*" }'
```

## MinIO — mirror

```bash
mc alias set off-host https://<offsite-endpoint> <key> <secret>
mc mirror --overwrite --remove minio/tg365-exports   off-host/tg365-exports
mc mirror --overwrite --remove minio/tg365-evidence  off-host/tg365-evidence
```

The off-host bucket should have object-lock enabled (compliance mode) for tamper-evident retention of evidence and audit archives.

## Verification (mandatory quarterly drill)

Walk R-007 end-to-end on a non-production host. File the result with the date and a screenshot of the restored audit log search.

## Disaster recovery RTO/RPO targets

| Disaster | RPO | RTO |
|----------|-----|-----|
| Single container crash | 0 | < 5 min (auto-restart) |
| Single host failure | < 1 h (last dump) + WAL | 2 h (provision + restore) |
| Region failure (if off-host is region-redundant) | < 24 h | 8 h (provision + restore + reconnect Entra) |
| Tenant disconnection (Microsoft side) | – | depends on Microsoft incident; platform continues to serve cached data and reports |
