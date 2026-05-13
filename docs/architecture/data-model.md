# Architecture — Data model

> Logical schema for the M365 Enterprise Control Center.
> The physical schema (Alembic migrations) is generated in Phase 1 from this design.

## Conventions

- Primary keys: `BIGSERIAL` for high-volume tables, `UUID v7` for entities exposed in URLs.
- Tenant scoping: every row in business tables has a non-null `tenant_id` FK to `tenants`.
- Timestamps: `created_at`, `updated_at` (`TIMESTAMPTZ` UTC). Default `now()`.
- Soft-delete: `deleted_at TIMESTAMPTZ NULL` on entities where deletion history matters (users, groups, sites).
- Time-partitioning: audit/event tables use `PARTITION BY RANGE (event_time)` monthly.
- JSONB for Microsoft-specific payload mirrors; normalized columns for indexed fields.

## Domain map

### Platform — auth, RBAC, tenancy

| Table | Purpose |
|-------|---------|
| `tenants` | One row per Microsoft 365 tenant being monitored. |
| `tenant_connections` | Microsoft Graph / Purview / Defender connection state per tenant. |
| `app_registrations` | App registration metadata (client_id, scopes granted, last admin-consent check). |
| `platform_users` | People who can sign into this platform (Entra-mapped). |
| `platform_roles` | Built-in and custom RBAC roles. |
| `platform_permissions` | Atomic permission strings, seeded from code. |
| `platform_role_permissions` | M:N role↔permission. |
| `platform_role_assignments` | platform_user × role, with optional scope (tenant/domain/site/department). |
| `technician_audit_logs` | Append-only audit of every privileged action inside the platform. |

### Graph plumbing

| Table | Purpose |
|-------|---------|
| `graph_permissions` | Catalogue of all Graph scopes the platform may need; describes feature → scope mapping. |
| `graph_sync_jobs` | Definition of a collector (e.g. `entra.users`, `sharepoint.sites`). |
| `graph_sync_job_runs` | One row per execution: status, start, end, rows in/out, error, correlation_id. |
| `graph_delta_tokens` | Stored `@odata.deltaLink` per tenant per resource. |
| `graph_webhook_subscriptions` | Change-notification subscriptions and renewal state. |

### Entra ID

| Table | Purpose |
|-------|---------|
| `m365_users` | Mirror of `/users`. Includes account state, AD properties, last sign-in. |
| `m365_groups` | Mirror of `/groups`. |
| `m365_group_memberships` | user/group ↔ group, with membership type (member/owner). |
| `m365_roles` | Mirror of `/directoryRoles`. |
| `m365_role_assignments` | Principal ↔ role assignments. |
| `m365_licenses` | Per-user license assignments (`/users/{id}/licenseDetails`). |
| `entra_signins` | Partitioned monthly. From `/auditLogs/signIns` (license-dependent). |
| `entra_directory_audits` | Partitioned monthly. From `/auditLogs/directoryAudits`. |

### Exchange Online

| Table | Purpose |
|-------|---------|
| `exchange_mailboxes` | User and shared mailboxes, type, quotas where exposed. |
| `exchange_mailbox_permissions` | FullAccess / SendAs / SendOnBehalf as visible via Graph. |
| `exchange_mailbox_audit_events` | Partitioned monthly. Mailbox audit events. |

### SharePoint Online

| Table | Purpose |
|-------|---------|
| `sharepoint_sites` | Tenant site collections + sub-sites. |
| `sharepoint_lists` | Lists and libraries per site. |
| `sharepoint_drives` | Document drives per site/user. |
| `sharepoint_items` | DriveItems with selected fields (name, path, size, sharing summary). Indexed for permission scans. |
| `sharepoint_permissions` | Item/list/site permission grants (inheritance flag, granted-to). |
| `sharepoint_sharing_links` | Per-item sharing links: scope (anonymous/anyone/company/specific), grantee, expiration. |
| `sharepoint_audit_events` | Partitioned monthly. File/folder/site activity. |

### OneDrive

| Table | Purpose |
|-------|---------|
| `onedrive_accounts` | One row per user OneDrive. |
| `onedrive_audit_events` | Partitioned monthly. |

### Teams

| Table | Purpose |
|-------|---------|
| `teams` | Mirror of `/teams`. |
| `teams_channels` | Channels per team. |
| `teams_members` | Team ↔ user. |
| `teams_audit_events` | Partitioned monthly. |

### Service health

| Table | Purpose |
|-------|---------|
| `service_health_overviews` | Current state per service. |
| `service_health_issues` | Active and historic issues. |

### Security operations

| Table | Purpose |
|-------|---------|
| `security_rules` | Rule definitions (DSL or SQL fragment + parameters). |
| `security_rule_matches` | Each match the engine produced. |
| `security_alerts` | Alert state, severity, assignee, status (new/investigating/resolved/false-positive). |
| `investigation_cases` | Case header, owner, status. |
| `investigation_case_events` | Timeline entries (notes, evidence pointers, linked alerts). |

### Reporting

| Table | Purpose |
|-------|---------|
| `saved_reports` | Definition: source, columns, filters, owner, ACL. |
| `report_runs` | Each manual or scheduled run. |
| `report_exports` | Generated artifacts in MinIO; checksum, format, size, downloader audit. |
| `scheduled_reports` | Schedule expressions + delivery channels. |

### Notifications

| Table | Purpose |
|-------|---------|
| `notification_channels` | Email / webhook / Teams-webhook destinations. |
| `notification_events` | Outbound notification log, success/failure, delivery time. |

### Content search

| Table | Purpose |
|-------|---------|
| `content_search_profiles` | Saved search definition (patterns, scope, RBAC). |
| `content_search_runs` | Execution, matches summary, exports (metadata only by default). |

### Remediation

| Table | Purpose |
|-------|---------|
| `remediation_policies` | Action definition: name, description, required permission, supports rollback, dry-run-only flag, enabled flag (default `false`). |
| `remediation_actions` | Each invocation: target, parameters, status (pending_approval/approved/dry_run_complete/applied/failed/rolled_back). |
| `remediation_approvals` | Approver, approved_at, signed_payload_hash. |

## High-volume partitioning

Tables with `*_audit_events` and `entra_signins` use monthly range partitioning:

```sql
CREATE TABLE entra_signins (
    id BIGSERIAL,
    tenant_id UUID NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    user_id UUID,
    ip_address INET,
    risk_level TEXT,
    payload JSONB NOT NULL,
    PRIMARY KEY (id, event_time)
) PARTITION BY RANGE (event_time);
```

A maintenance worker creates next month's partition, drops partitions older than the retention horizon (default 13 months — configurable per tenant), and snapshots dropped partitions to MinIO before deletion when long-term archive is enabled.

## OpenSearch index plan

| Index pattern | Source table | Retention |
|---------------|--------------|-----------|
| `tg365-entra-signins-YYYY.MM` | entra_signins | 13 months |
| `tg365-entra-directoryaudits-YYYY.MM` | entra_directory_audits | 24 months |
| `tg365-sharepoint-activity-YYYY.MM` | sharepoint_audit_events | 13 months |
| `tg365-exchange-activity-YYYY.MM` | exchange_mailbox_audit_events | 13 months |
| `tg365-teams-activity-YYYY.MM` | teams_audit_events | 13 months |
| `tg365-content-search-results-YYYY.MM` | content_search_runs (results) | 6 months |
| `tg365-alerts-YYYY.MM` | security_alerts | 24 months |

ILM (Index Lifecycle Management) policies handle rollover and deletion. Snapshots go to MinIO before deletion when long-term archive is on.

## Reference: required indexes (initial)

- `m365_users(tenant_id, user_principal_name)` unique
- `sharepoint_items(tenant_id, site_id, drive_id, path)` btree
- `sharepoint_permissions(tenant_id, item_id, principal_id)`
- `sharepoint_sharing_links(tenant_id, scope, expires_at)`
- `entra_signins(tenant_id, event_time DESC, user_id)`
- `technician_audit_logs(tenant_id, created_at DESC, actor_id)`
- `security_alerts(tenant_id, status, severity, created_at DESC)`
