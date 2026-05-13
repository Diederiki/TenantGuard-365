#!/usr/bin/env bash
# Trigger an OpenSearch snapshot.
# Prerequisite: a snapshot repository named "tg365-snap" pointing at MinIO.
# Usage: ./snapshot-opensearch.sh [OPENSEARCH_URL]
set -euo pipefail

OS_URL="${1:-http://localhost:9200}"
SNAP_NAME="snap-$(date -u +%Y%m%d-%H%M%S)"

echo "[snapshot] creating ${SNAP_NAME}"
curl -fsS -X PUT \
    "${OS_URL}/_snapshot/tg365-snap/${SNAP_NAME}?wait_for_completion=false" \
    -H 'Content-Type: application/json' \
    -d '{"indices": "tg365-*"}'
echo
echo "[snapshot] queued — poll _snapshot/tg365-snap/${SNAP_NAME}/_status"
