# TenantGuard 365 — Feature Roadmap

_Read the parity matrix first:_
[`manageengine-feature-parity-matrix.md`](./manageengine-feature-parity-matrix.md).

This file collapses the 72-entry matrix into a phased delivery plan.

## Phase guarantees

| Phase | Definition |
|---|---|
| **MVP** | Hits the floor of "useful out of the box with read-only Graph creds." Pages render, exports work, audit + RBAC enforce, no destructive actions. |
| **Phase 2** | Adds the read-side breadth a CISO expects: sign-in risk, license usage, DLP alerts, mailbox usage, Teams + OneDrive usage. Dry-run user-management actions enabled. |
| **Phase 3** | Tenant-changing actions move from framework-ready to live execution, gated behind feature flags + approval workflow. Exchange PowerShell-backed reporting comes online. |
| **Future** | Power BI tenant analytics, Viva Engage as Microsoft re-stabilises its APIs, on-prem SharePoint connector if there is demand. |

## MVP delivery (current sprint)

Read-only Graph collectors:
- `entra.users.all` / `entra.users.guests` / `entra.licenses.usage` —
  **live**.
- `sharepoint.sites.inventory` — **live**.
- `service_health.overview` — **live**.
- `entra.roles.assignments` — needs `RoleManagement.Read.Directory`.
- `entra.signins.recent` + `entra.audit.directory` — need
  `AuditLog.Read.All` plus Entra ID P1 for risk fields.
- `exchange.mailboxes.inventory` + `exchange.mailboxes.size_quota` — need
  `Reports.Read.All` + `MailboxSettings.Read`.
- `exchange.forwarding.external` — `MailboxSettings.Read` only.
- `sharepoint.permissions.matrix` + `sharepoint.sharing.links` +
  `sharepoint.external.users` + `sharepoint.broken_inheritance` —
  need `Sites.FullControl.All` and tenant validation.
- `onedrive.accounts` + `onedrive.sharing` — `Reports.Read.All` +
  `Files.Read.All`.
- `teams.inventory` — `Team.ReadBasic.All` family.
- Audit feeds: `*.audit.*` entries — single shared collector against
  `/security/auditLog/queries`.

Platform features:
- Technician audit trail, RBAC, exports, scheduled reports, system health,
  notifications framework, retention framework — **all shipping**.

## Phase 2

- Inactive mailboxes / inactive OneDrive accounts (license waste).
- Mail traffic + top senders / recipients.
- Teams usage + device usage.
- Spam / malware / phishing detection — needs Defender for Office 365.
- Internal-rule alerts (live engine + ruleset growing).
- DLP alerts — needs Purview.
- Dry-run management:
  `management.entra.password_reset`,
  `management.entra.block_user`,
  `management.entra.licenses`.
- Investigation cases workflow.
- Notification send pipeline + history table.
- DB-backed settings pages (general / security / retention / notifications).

## Phase 3

- Exchange PowerShell-backed reports + management
  (`management.exchange.*`, `exchange.mobile.devices`,
  `exchange.litigation_hold`, `exchange.owa.policies`,
  `exchange.public_folders`).
- SharePoint management actions (`sharepoint.mgmt.permissions`,
  `sharepoint.mgmt.groups`).
- Teams management (`teams.mgmt.create_team`).
- Content-search profiles (Purview licence + eDiscovery role).
- Auto-remediation policy execution (dry-run → live behind feature flag).
- Defender advanced hunting (KQL).
- Power BI workload audit.
- OpenTelemetry + audit-log RLS + Brotli compression on exports.

## Future modules

- Viva Engage usage + audit (waiting on Microsoft API stability).
- SharePoint on-prem connector (only if a real customer requests it).
- SharePoint backup / migration (acquire via partner or skip).
- Yammer (deprecated by Microsoft, replaced by Viva Engage).

## Exact next implementation steps

1. Land `app.registry` + `/api/catalog/*` + `/catalog` UI **(this phase)**.
2. Wire `entra.signins.recent` + `entra.audit.directory` collectors against
   a real tenant; both already framework-ready.
3. Implement the four DB-backed settings pages.
4. Implement the notification send pipeline.
5. Phase-3 prep: package Exchange Online PowerShell into the worker
   container (PowerShell 7 + ExchangeOnlineManagement module).
