# Data retention policy

> Default retention windows for every data class on the platform. Operators can
> override per tenant in `tenant_settings` (Phase 11+).

## Defaults

| Data class | Source table / store | Default retention | Long-term archive |
|---|---|---|---|
| Technician audit log | `technician_audit_logs` (Postgres + offsite sink) | **24 months** online | 7 years (S3 Object Lock) |
| Entra sign-ins | `entra_signins` (monthly partitioned) | 13 months | Snapshot to MinIO before partition drop |
| Entra directory audits | `entra_directory_audits` | 24 months | Snapshot to MinIO |
| SharePoint activity | `sharepoint_audit_events` | 13 months | Snapshot to MinIO |
| Exchange mailbox audit | `exchange_mailbox_audit_events` | 13 months | Snapshot to MinIO |
| OneDrive activity | `onedrive_audit_events` | 13 months | Snapshot to MinIO |
| Teams activity | `teams_audit_events` | 13 months | Snapshot to MinIO |
| Security alerts | `security_alerts` | 24 months | OpenSearch + Postgres |
| Investigation cases | `investigation_cases` + events | indefinite while open; 7 years after close | Postgres + audit trail |
| Report runs (metadata) | `report_runs` | 12 months | — |
| Report exports (bytes) | `report_exports` + MinIO object | **90 days** then auto-deleted | optional archive on request |
| Content-search runs | `content_search_runs` | 6 months | metadata only |
| Notification events | `notification_events` | 6 months | — |
| Token cache | `graph_token_cache` | per-token TTL (typically 1 hour) | never archived |
| Remediation actions | `remediation_actions` + approvals | 7 years | Postgres + offsite audit shipping |

## Export-specific retention

Beyond the row in `report_exports`, the actual XLSX/CSV/PDF/HTML body in
MinIO is deleted **90 days** after the export was downloaded (or 90 days
after creation if never downloaded). Re-running the report produces a new
export — bytes are not deduplicated.

Sensitive exports (e.g. content-search results) that match the platform's
"sensitive" classification are deleted **30 days** after download by default
and require an operator-supplied `reason` at creation time.

## Implementation surface

- **Postgres monthly partitions** drop on schedule via a maintenance worker.
  Before drop, the worker streams the partition to MinIO if archive is
  enabled.
- **MinIO object lifecycle** rules per bucket enforce the above retention
  windows. See `infra/minio/lifecycle.json` (Phase 10+).
- **OpenSearch ILM** policies handle index rollover and deletion. See
  `infra/opensearch/index-templates.json`.

## Compliance posture

- Audit logs are tamper-evident: every record carries an HMAC payload hash
  signed by the audit signing key. Re-shipped records preserve the same hash.
- Export downloads are themselves audit events; even after the export bytes
  expire, the record of who downloaded what survives at full retention.
- Microsoft tenant data is never deleted by the platform — these windows
  only apply to mirrored copies inside the platform's own database.

## Per-tenant override (Phase 11+)

A future `tenant_settings.retention` JSONB column will hold per-class
overrides. The default `data-retention.json` shape:

```json
{
  "technician_audit_logs_months": 24,
  "entra_signins_months": 13,
  "sharepoint_audit_events_months": 13,
  "exchange_audit_events_months": 13,
  "teams_audit_events_months": 13,
  "onedrive_audit_events_months": 13,
  "report_exports_days": 90,
  "report_exports_sensitive_days": 30,
  "content_search_runs_months": 6,
  "long_term_archive_enabled": false
}
```
