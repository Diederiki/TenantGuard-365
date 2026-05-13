#!/usr/bin/env bash
# Nightly Postgres backup with checksum + optional off-host mirror.
# Usage: ./backup-postgres.sh [OUT_DIR] [REMOTE_ALIAS]
set -euo pipefail

OUT_DIR="${1:-./backups/postgres}"
REMOTE_ALIAS="${2:-}"
TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$OUT_DIR"

POSTGRES_USER="${POSTGRES_USER:-tg365}"
POSTGRES_DB="${POSTGRES_DB:-tg365}"

OUT_FILE="$OUT_DIR/tg365-${TS}.dump"

echo "[backup] dumping ${POSTGRES_DB} -> ${OUT_FILE}"
docker compose exec -T postgres \
    pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
    --format=custom --compress=9 --no-owner --no-privileges \
    > "$OUT_FILE"

echo "[backup] checksum"
( cd "$OUT_DIR" && sha256sum "$(basename "$OUT_FILE")" ) > "${OUT_FILE}.sha256"

if [[ -n "$REMOTE_ALIAS" ]]; then
    echo "[backup] mirror to $REMOTE_ALIAS"
    mc cp "$OUT_FILE" "$REMOTE_ALIAS/tg365-backups/postgres/"
    mc cp "${OUT_FILE}.sha256" "$REMOTE_ALIAS/tg365-backups/postgres/"
fi

# Retention: keep last 30 daily.
find "$OUT_DIR" -name 'tg365-*.dump' -mtime +30 -delete
find "$OUT_DIR" -name 'tg365-*.dump.sha256' -mtime +30 -delete
echo "[backup] done"
