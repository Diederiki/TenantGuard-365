# Operational runbooks

> Step-by-step procedures for things that don't happen often enough to memorise but matter when they do.

## R-001 — Rotate Entra app credential

**When:** every 6 months for client secrets, every 12 months for certificates, immediately on suspected compromise.

1. In Entra portal → App registrations → `tg365-collector` (or `tg365-portal`) → Certificates & secrets.
2. Add a **new** credential alongside the existing one. Note the value/thumbprint.
3. Update the secret store entry. Bump the credential's version metadata.
4. Roll restart the worker (and API for portal credential): `docker compose up -d --no-deps --force-recreate worker api`.
5. Watch logs for `graph.token.acquired` events; confirm no failures.
6. In Entra portal, delete the old credential.
7. Write a `technician_audit_logs` entry: `tenant.credential.rotated` with the credential ID being retired.

## R-002 — Reset a collector's delta token

**When:** a delta link returns `410 Gone`, or a sync diverged and you want a clean state.

1. Identify the row in `graph_delta_tokens` (`tenant_id`, `resource`).
2. Mark the collector run as halted via the Jobs UI (Phase 4+).
3. Update the row: set `delta_link = NULL`, `last_full_sync_at = NULL`.
4. Trigger a "Full refresh" run from the Jobs UI.
5. Verify the next scheduled run picks up a new delta link.

## R-003 — Suspend a tenant connection

**When:** offboarding, incident response, or maintenance.

1. UI: Settings → Graph Connection → Suspend.
2. The platform sets `tenant_connections.status = suspended` and pauses all collectors and webhook renewals.
3. Schedules continue to be tracked but no Graph calls are made.
4. To re-enable, re-run the connection wizard.

## R-004 — Force a Graph permission gap re-check

**When:** after granting new scopes via admin consent.

1. UI: Settings → Graph Connection → "Re-detect permissions".
2. The platform fetches `appRoleAssignments` for the collector service principal and reconciles against the platform's required set per enabled module.
3. Output is rendered with red/yellow/green; missing scopes link to the consent URL.

## R-005 — Approve a remediation action

**When:** a technician submits a destructive remediation and you are the second-pair-of-eyes approver.

1. UI: Remediation → Pending Approvals → select the action.
2. Read the policy, target, parameters, and dry-run output (mandatory before approval).
3. Click **Approve**. The platform writes a `remediation_approvals` row containing your user ID, timestamp, and an HMAC over the canonical action payload.
4. The worker picks it up and applies the action; you receive a notification on completion.

## R-006 — Roll back a remediation

**When:** a remediation succeeded but had unintended consequences.

1. UI: Remediation → History → select the action.
2. If the policy has `supports_rollback: true`, click **Rollback**. Read the rollback preview.
3. Approve via the second-technician flow (as above).
4. Worker performs the inverse action and records both records.

## R-007 — Backup verification drill

**When:** quarterly; mandatory before any production change touching storage.

1. Spin up a separate VPS or local docker host.
2. Restore the most recent Postgres dump.
3. Restore the most recent OpenSearch snapshot from the MinIO mirror.
4. Restore the most recent MinIO mirror snapshot.
5. Start the platform pointed at the restored data.
6. Run smoke checks: sign in, open a saved report, view audit log, view alerts.
7. File the drill result in `technician_audit_logs` (`drill.backup.completed`).

## R-008 — Incident response: leaked Graph token

1. Treat the credential as fully compromised.
2. In Entra portal: invalidate the credential.
3. In Entra portal: revoke any sessions and tokens for the service principal where possible.
4. Rotate the credential as in R-001.
5. Search `technician_audit_logs` for any unusual collector activity in the suspected window.
6. Snapshot the relevant log range, store off-host.
7. File an incident under the project's incident-response process.

## R-009 — Audit log offsite shipping is backlogged

**When:** the audit-shipper backlog metric exceeds 1 hour.

1. UI: Settings → System → Audit shipper. Check the last successful high-water mark.
2. View shipper container logs.
3. Common causes: storage credentials expired, off-host endpoint unreachable, rate-limited by destination.
4. Resolve, then restart the shipper. The shipper resumes from the high-water mark.
5. Verify the backlog clears.

## R-010 — Re-encrypt token cache with a new master key

**When:** rotating `TOKEN_CACHE_MASTER_KEY`.

1. Generate a new key. Add as `TOKEN_CACHE_MASTER_KEY_NEXT` alongside the current key (both supported during rotation).
2. Restart the worker. It will decrypt with the old key and re-encrypt with the new key on each refresh.
3. After all tokens have rotated (typically 1 hour or one full token-refresh cycle), promote `TOKEN_CACHE_MASTER_KEY_NEXT` to `TOKEN_CACHE_MASTER_KEY` and drop the old value.
4. Restart workers and API; verify `graph.token.cache.unwrap_failures_total` is 0.

## Conventions

- Every runbook starts with **When** so the operator knows whether this is the right document before reading further.
- Every runbook ends with an audit-log expectation.
- Runbooks are versioned with the repo; never edit live on the server.
