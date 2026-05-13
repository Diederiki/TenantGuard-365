# Audit model

## Goals

1. Every privileged action in the platform produces an audit record.
2. Records are append-only at the application layer; tamper-evident in production.
3. Records are queryable and exportable, but exports of audit records are themselves audited.
4. Records help answer the question *"who did what, to what, when, and why?"* in court-defensible detail.

## Audit categories

| Category | Examples |
|----------|----------|
| `auth.*` | sign-in success/failure, session create/expire, role re-issue |
| `rbac.*` | role created, permission added, scope changed, assignment added, denied |
| `tenant.*` | tenant connected, app registration scope change, admin consent recorded |
| `graph.*` | sync job started/finished/failed, delta token reset, webhook subscribed/renewed |
| `report.*` | report run, scheduled report fired, export generated, export downloaded |
| `search.*` | content search created, run, exported |
| `alert.*` | alert created (rule fired), assigned, status changed, resolved |
| `investigation.*` | case created, evidence added, closed |
| `remediation.*` | action submitted, approved, dry-run completed, applied, rolled back, failed |
| `settings.*` | tenant settings changed, retention changed, feature flag toggled |

## Record schema (`technician_audit_logs`)

| Column | Type | Notes |
|--------|------|-------|
| `id` | BIGSERIAL | PK |
| `tenant_id` | UUID | nullable for platform-level events |
| `actor_id` | UUID | `platform_users.id` or `'system'` for worker actions |
| `actor_display` | TEXT | denormalised at write time so deletes don't break history |
| `actor_role_ids` | UUID[] | snapshot at action time |
| `actor_type` | TEXT | `user` | `system` | `service` |
| `action` | TEXT | e.g. `report.export.created` |
| `target_type` | TEXT | e.g. `saved_report` |
| `target_id` | TEXT | string to allow non-UUID targets (e.g. SharePoint site IDs) |
| `target_label` | TEXT | denormalised display name |
| `old_value` | JSONB NULL | for diffs |
| `new_value` | JSONB NULL | for diffs |
| `result` | TEXT | `success` / `failure` |
| `failure_reason` | TEXT NULL | |
| `ip` | INET | |
| `user_agent` | TEXT | |
| `correlation_id` | UUID | one per logical workflow |
| `request_id` | UUID | one per HTTP request |
| `payload_hash` | BYTEA | HMAC-SHA256 over the canonical JSON of the record, with a key from the secret store |
| `event_time` | TIMESTAMPTZ | indexed; partition key |

## Append-only enforcement

**Application layer:**
- A single `AuditLogger` service is the only code path that inserts. No raw `INSERT` against `technician_audit_logs` is allowed; a lint rule enforces this in Phase 10.

**Database layer:**
- Two Postgres roles:
  - `tg365_app` — `INSERT, SELECT` only on `technician_audit_logs`.
  - `tg365_audit_rotation` — `DELETE` only on dropped partitions, never `UPDATE`.
- Trigger denies `UPDATE`:
  ```sql
  CREATE OR REPLACE FUNCTION tg365_audit_immutable() RETURNS trigger AS $$
  BEGIN
      RAISE EXCEPTION 'technician_audit_logs is append-only';
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER tg365_audit_no_update
  BEFORE UPDATE ON technician_audit_logs
  FOR EACH ROW EXECUTE FUNCTION tg365_audit_immutable();
  ```

**Off-host shipping (production):**
- A worker streams new records to an immutable sink (S3 Object Lock, append-only syslog, or SIEM) within seconds of write.
- The shipping worker tracks a high-water mark; failure raises an alert.

## Retention

- Default: 24 months online (Postgres + OpenSearch).
- Configurable per tenant (`tenant_settings.audit_retention_months`, range 12–84).
- Before partition drop, archive to MinIO/S3 with Object Lock. Archive retention default 7 years.

## Export of audit records

- Permission: `audit.read` (browse), `audit.read.raw` (see IP/UA/`payload_hash`), `audit.export` (download).
- Every audit export creates a record in the audit log — `audit.export.created` — including filters, row count, and checksum.

## Sample records

```jsonc
{
  "action": "report.export.created",
  "actor_display": "Anna Admin",
  "actor_role_ids": ["..."],
  "target_type": "saved_report",
  "target_id": "rep_8f...",
  "target_label": "SharePoint External Sharing — Last 30 Days",
  "new_value": {
    "format": "xlsx",
    "filters": {"date_range": "P30D", "tenant_id": "..."},
    "row_count": 1240,
    "checksum_sha256": "..."
  },
  "result": "success",
  "ip": "10.20.30.40",
  "user_agent": "Mozilla/...",
  "correlation_id": "...",
  "request_id": "..."
}
```

```jsonc
{
  "action": "remediation.approved",
  "actor_display": "Ben Approver",
  "target_type": "remediation_action",
  "target_id": "rem_3a...",
  "new_value": {
    "policy": "disable-risky-sharing-link",
    "mode": "live",
    "payload_hash": "..."
  },
  "result": "success"
}
```
