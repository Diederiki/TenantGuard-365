#!/usr/bin/env bash
# Mirror MinIO buckets off-host. Aliases must be pre-configured via `mc alias set`.
# Usage: ./mirror-minio.sh REMOTE_ALIAS
set -euo pipefail

REMOTE_ALIAS="${1:?need remote alias e.g. 'off-host'}"

for bucket in tg365-exports tg365-evidence; do
    echo "[mirror] ${bucket} -> ${REMOTE_ALIAS}"
    mc mirror --overwrite --remove "minio/${bucket}" "${REMOTE_ALIAS}/${bucket}"
done

echo "[mirror] done"
