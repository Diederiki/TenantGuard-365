# Microsoft API capability matrix

> Per-feature mapping to Microsoft APIs. Authoritative source for what the platform can deliver against real Microsoft endpoints, what permissions and licenses are required, and which features are placeholders pending API support.
>
> **Verify each row against current Microsoft documentation before implementing.** Microsoft Graph evolves; some `beta` endpoints listed below should be re-checked for GA status when picked up.

## Column legend

| Column | Meaning |
|--------|---------|
| **Source** | Graph v1.0 / Graph beta / Purview / Defender / Mgmt Activity API / Exchange PS |
| **Endpoint family** | Primary HTTP path family |
| **Delegated** | Scope(s) when called on behalf of a signed-in user |
| **Application** | Scope(s) when called as the app (client credentials) — preferred for collectors |
| **Role** | Entra/Purview/Defender directory role required, where applicable |
| **License** | License dependency (skip = none beyond standard) |
| **Delta** | Whether the endpoint supports `$delta` |
| **Webhook** | Whether the resource supports change notifications |
| **Latency** | Typical data latency from event to API |
| **Rate** | Throttling notes |
| **MVP status** | `confirmed` / `needs-validation` / `placeholder` |

## Status definitions

- **confirmed** — Endpoint and permission documented by Microsoft; we can implement now.
- **needs-validation** — Endpoint exists but specific behaviour (e.g. exact field set, throttling, license) must be tested in our tenant before relying on it.
- **placeholder** — Microsoft does not expose an API for this feature, or only via deprecated/PowerShell-only paths. Will ship a placeholder module documenting the gap.

---

## 1. Entra ID

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| User inventory | Graph v1.0 | `/users` | `User.Read.All` | `User.Read.All` | Directory Readers | – | yes | yes | seconds | standard | confirmed |
| Group inventory | Graph v1.0 | `/groups` | `Group.Read.All` | `Group.Read.All` | Directory Readers | – | yes | yes | seconds | standard | confirmed |
| Group membership | Graph v1.0 | `/groups/{id}/members` | `GroupMember.Read.All` | `GroupMember.Read.All` | Directory Readers | – | partial (group delta only) | yes | seconds | standard | confirmed |
| Directory roles + assignments | Graph v1.0 | `/directoryRoles`, `/roleManagement/directory/roleAssignments` | `RoleManagement.Read.Directory` | `RoleManagement.Read.Directory` | Directory Readers | – | no | no | seconds | standard | confirmed |
| Licenses assigned (per user) | Graph v1.0 | `/users/{id}/licenseDetails` | `User.Read.All` | `User.Read.All` | Directory Readers | – | no | no | minutes | standard | confirmed |
| Subscribed SKUs | Graph v1.0 | `/subscribedSkus` | `Organization.Read.All` | `Organization.Read.All` | Global Reader | – | no | no | minutes | standard | confirmed |
| Sign-in logs | Graph v1.0 | `/auditLogs/signIns` | `AuditLog.Read.All` | `AuditLog.Read.All` | Reports Reader / Security Reader | **Entra ID P1+** | no | no | minutes | strict | confirmed (license-gated) |
| Directory audit logs | Graph v1.0 | `/auditLogs/directoryAudits` | `AuditLog.Read.All` | `AuditLog.Read.All` | Reports Reader / Security Reader | – | no | no | minutes | strict | confirmed |
| Risky users / risk detections | Graph v1.0 | `/identityProtection/riskyUsers`, `/riskDetections` | `IdentityRiskyUser.Read.All`, `IdentityRiskEvent.Read.All` | same | Security Reader | **Entra ID P2** | no | no | minutes | strict | confirmed (license-gated) |
| Authentication methods (per user) | Graph v1.0 | `/users/{id}/authentication/methods` | `UserAuthenticationMethod.Read.All` | `UserAuthenticationMethod.Read.All` | Authentication Administrator (read) | – | no | no | minutes | standard | confirmed |
| MFA registration (tenant-wide report) | Graph v1.0 | `/reports/authenticationMethods/userRegistrationDetails` | `AuditLog.Read.All`, `UserAuthenticationMethod.Read.All` | same | Reports Reader | **Entra ID P1+** | no | no | up to 48h | standard | confirmed (license-gated) |
| Conditional Access policies | Graph v1.0 | `/identity/conditionalAccess/policies` | `Policy.Read.All` | `Policy.Read.All` | Security Reader | **Entra ID P1+** | no | no | seconds | standard | confirmed |
| Applications / service principals | Graph v1.0 | `/applications`, `/servicePrincipals` | `Application.Read.All` | `Application.Read.All` | Cloud Application Administrator (read sufficient) | – | partial | yes | seconds | standard | confirmed |
| Application consent (OAuth2PermissionGrants) | Graph v1.0 | `/oauth2PermissionGrants` | `Directory.Read.All` | `Directory.Read.All` | Cloud Application Administrator (read) | – | no | no | seconds | standard | confirmed |
| Stale users (last sign-in) | Graph v1.0 | `/users` with `signInActivity` select | `AuditLog.Read.All` + `User.Read.All` | same | Reports Reader | **Entra ID P1+** | no | no | up to 24h | standard | confirmed (license-gated) |
| Guest users | Graph v1.0 | `/users` filter `userType eq 'Guest'` | `User.Read.All` | same | Directory Readers | – | yes | – | seconds | standard | confirmed |

## 2. Exchange Online

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mailbox inventory (user mailboxes) | Graph v1.0 | `/users` filter `assignedPlans` for Exchange | as above | as above | – | Exchange license | – | – | – | – | confirmed (indirect) |
| Mailbox settings | Graph v1.0 | `/users/{id}/mailboxSettings` | `MailboxSettings.Read` | `MailboxSettings.Read` | – | Exchange | no | no | seconds | standard | confirmed |
| Inbox rules (per mailbox) | Graph v1.0 | `/users/{id}/mailFolders/inbox/messageRules` | `MailboxSettings.Read` (some flows need `Mail.Read`) | `MailboxSettings.Read` | – | Exchange | no | no | seconds | standard | needs-validation |
| Mailbox forwarding (settings) | Graph v1.0 | `/users/{id}/mailboxSettings` (forwardingAddress) + inbox rules | `MailboxSettings.Read` | `MailboxSettings.Read` | – | Exchange | no | no | seconds | standard | confirmed |
| Mailbox permissions (FullAccess/SendAs/SendOnBehalf) | Exchange Online PowerShell | `Get-MailboxPermission`, `Get-RecipientPermission` | – (app-only via Exchange Online cert auth) | – | Exchange Recipient Reader | Exchange | no | no | minutes | EXO-specific | needs-validation (no native Graph equivalent) |
| Shared mailbox inventory | Graph v1.0 | `/users` filter recipientType + Exchange PS for `recipientTypeDetails` | as above | as above | – | Exchange | – | – | – | – | needs-validation |
| Mailbox usage reports | Graph v1.0 | `/reports/getMailboxUsageDetail(period='D7')` | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | Exchange | no | no | up to 48h | standard | confirmed |
| Mail traffic / message trace | Reporting Web Service / Defender | Exchange Reporting API; not in Graph | – | – | – | Exchange / Defender for O365 | – | – | – | – | needs-validation (use Defender where licensed) |
| Mailbox audit events | Purview Audit Search | `/security/auditLog/queries` (Graph beta) **or** Mgmt Activity API | `AuditLog.Read.All` | `AuditLog.Read.All` | eDiscovery Manager or Audit Reader (Purview) | Audit (Standard/Premium) | no | no | minutes–hours | strict | confirmed (Purview), needs-validation (Graph beta GA status) |

## 3. SharePoint Online

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Site inventory (root + sub) | Graph v1.0 | `/sites?search=*` | `Sites.Read.All` | `Sites.Read.All` | – | SharePoint Plan 1+ | no (search) | – | seconds | strict | confirmed |
| Site details / settings | Graph v1.0 | `/sites/{id}` | `Sites.Read.All` | `Sites.Read.All` | – | SP P1+ | no | no | seconds | strict | confirmed |
| Lists / libraries | Graph v1.0 | `/sites/{id}/lists` | `Sites.Read.All` | `Sites.Read.All` | – | SP P1+ | no | no | seconds | strict | confirmed |
| List items | Graph v1.0 | `/sites/{id}/lists/{id}/items` | `Sites.Read.All` | `Sites.Read.All` | – | SP P1+ | yes | – | seconds | strict | confirmed |
| Drives / driveItems | Graph v1.0 | `/sites/{id}/drives`, `/drives/{id}/root/children` | `Files.Read.All` | `Files.Read.All` | – | SP P1+ | yes | yes | seconds | strict | confirmed |
| Item permissions (inheritance) | Graph v1.0 | `/drives/{id}/items/{id}/permissions`, `/sites/{id}/permissions` | `Sites.FullControl.All` to read on some scenarios; `Sites.Read.All` works for many | `Sites.Read.All` (minimum), `Sites.FullControl.All` (full) | – | SP P1+ | no | no | seconds | strict | confirmed (least-privilege noted) |
| Sharing links | Graph v1.0 | `/drives/{id}/items/{id}/permissions` (link permissions) | `Sites.Read.All` | `Sites.Read.All` | – | SP P1+ | no | no | seconds | strict | confirmed |
| Tenant external sharing settings | Graph beta | `/admin/sharepoint/settings` | `SharePointTenantSettings.Read.All` (beta) | same | SharePoint Administrator | SP P1+ | no | no | seconds | strict | needs-validation (beta) |
| Storage usage per site | Graph v1.0 | `/reports/getSharePointSiteUsageDetail(period='D7')` | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | SP P1+ | no | no | up to 48h | standard | confirmed |
| Site activity (file/folder events) | Purview Audit Search | as Exchange audit row | as Exchange audit | as Exchange audit | as Exchange audit | Audit (Standard/Premium) | no | no | minutes–hours | strict | confirmed (Purview) |
| SharePoint groups + members | Graph v1.0 | `/sites/{id}/permissions` plus SharePoint REST `/_api/web/sitegroups` | `Sites.Read.All` | `Sites.Read.All` (Graph), `Sites.Read.All` (REST app) | – | SP P1+ | no | no | seconds | strict | needs-validation (SP REST fallback) |
| Permission inheritance scanner | Composed | Drive/item permissions + `inheritedFrom` field | as above | as above | – | SP P1+ | no | no | varies (large tenants slow) | strict | confirmed (composition) |
| Anonymous / anyone link inventory | Composed | Item permissions filtered by `link.scope` | as above | as above | – | SP P1+ | no | no | varies | strict | confirmed |
| Sync activity / sync devices | Purview Audit | events of type `FileSyncDownloadedFull` etc. | as Purview audit | as Purview audit | as Purview audit | Audit | no | no | hours | strict | needs-validation |

## 4. OneDrive for Business

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OneDrive inventory (per user) | Graph v1.0 | `/users/{id}/drive` | `Files.Read.All` | `Files.Read.All` | – | OneDrive license | no | – | seconds | strict | confirmed |
| Storage usage | Graph v1.0 | `/reports/getOneDriveUsageAccountDetail(period='D7')` | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | OneDrive | no | no | up to 48h | standard | confirmed |
| Sharing links | Graph v1.0 | `/drives/{id}/items/{id}/permissions` | `Files.Read.All` | `Files.Read.All` | – | OneDrive | no | no | seconds | strict | confirmed |
| Activity (file ops) | Purview Audit | as Purview audit | as Purview audit | as Purview audit | as Purview audit | Audit | no | no | minutes–hours | strict | confirmed (Purview) |
| Inactive OneDrive accounts | Composed | Usage report + last activity field | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | OneDrive | no | no | up to 48h | standard | confirmed |

## 5. Teams

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Teams inventory | Graph v1.0 | `/teams`, `/groups` (groups backing teams) | `Team.ReadBasic.All` | `Team.ReadBasic.All` | – | Teams | no | no | seconds | strict | confirmed |
| Channels per team | Graph v1.0 | `/teams/{id}/channels` | `Channel.ReadBasic.All` | `Channel.ReadBasic.All` | – | Teams | no | yes (messages, not channel meta) | seconds | strict | confirmed |
| Members / owners | Graph v1.0 | `/teams/{id}/members` | `TeamMember.Read.All` | `TeamMember.Read.All` | – | Teams | no | no | seconds | strict | confirmed |
| Teams usage report | Graph v1.0 | `/reports/getTeamsUserActivityUserDetail(period='D7')` | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | Teams | no | no | up to 48h | standard | confirmed |
| Teams device usage | Graph v1.0 | `/reports/getTeamsDeviceUsageUserDetail(period='D7')` | `Reports.Read.All` | `Reports.Read.All` | Reports Reader | Teams | no | no | up to 48h | standard | confirmed |
| Teams audit events | Purview Audit | as Purview audit | as Purview audit | as Purview audit | as Purview audit | Audit | no | no | minutes–hours | strict | confirmed (Purview) |

## 6. Service health

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Service health overviews | Graph v1.0 | `/admin/serviceAnnouncement/healthOverviews` | `ServiceHealth.Read.All` | `ServiceHealth.Read.All` | Service Support Administrator (read) | – | no | no | seconds | standard | confirmed |
| Service health issues | Graph v1.0 | `/admin/serviceAnnouncement/issues` | `ServiceHealth.Read.All` | `ServiceHealth.Read.All` | as above | – | no | no | seconds | standard | confirmed |
| Service messages (announcements) | Graph v1.0 | `/admin/serviceAnnouncement/messages` | `ServiceMessage.Read.All` | `ServiceMessage.Read.All` | as above | – | no | no | seconds | standard | confirmed |

## 7. Security & compliance

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Microsoft Graph Security: alerts v2 | Graph v1.0 | `/security/alerts_v2` | `SecurityAlert.Read.All` | `SecurityAlert.Read.All` | Security Reader | – | no | yes | minutes | standard | confirmed |
| Incidents | Graph v1.0 | `/security/incidents` | `SecurityIncident.Read.All` | `SecurityIncident.Read.All` | Security Reader | Defender XDR | no | yes | minutes | standard | confirmed |
| Advanced hunting | Graph beta | `/security/runHuntingQuery` (beta) | `ThreatHunting.Read.All` (beta) | same | Security Reader | **Defender XDR / E5 Security** | no | no | seconds | strict | needs-validation (beta + license) |
| Purview Audit search | Graph beta | `/security/auditLog/queries` (beta) | `AuditLog.Read.All` | `AuditLog.Read.All` | Audit Reader / eDiscovery Manager | **Audit (Standard/Premium)** | no | no | minutes–hours | strict | needs-validation (beta) |
| Mgmt Activity API (fallback unified audit) | Office 365 Mgmt Activity | `https://manage.office.com/api/v1.0/{tenantId}/activity/feed/subscriptions` | – | `ActivityFeed.Read` | Security Reader | Audit | no | no | up to 24h | webhook+pull | confirmed (legacy but available) |
| DLP policy audit | Purview Audit | events of category DLP | as Purview | as Purview | as Purview | DLP/E5 Compliance | no | no | minutes–hours | strict | needs-validation |
| eDiscovery activity | Purview Audit | events of category eDiscovery | as Purview | as Purview | as Purview | eDiscovery | no | no | minutes–hours | strict | needs-validation |

## 8. Power BI

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Power BI activity log | Power BI REST API | `https://api.powerbi.com/v1.0/myorg/admin/activityevents` | `Tenant.Read.All` (PBI) | – (delegated only) | Power BI Service Administrator | Power BI Pro / PPU / Premium | no | no | up to 30 minutes | strict | needs-validation (PBI uses its own auth model) |
| Workspaces | Power BI REST API | `/admin/groups` | `Tenant.Read.All` (PBI) | – | PBI Admin | PBI | no | no | minutes | strict | needs-validation |

## 9. Content search

| Feature | Source | Endpoint family | Delegated | Application | Role | License | Delta | Webhook | Latency | Rate | MVP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| eDiscovery (Premium) — custodians, holds, searches | Graph v1.0 | `/security/cases/ediscoveryCases` | `eDiscovery.Read.All`, `eDiscovery.ReadWrite.All` | same | eDiscovery Manager + Compliance Admin | **eDiscovery Premium (E5/F5 Compliance)** | no | no | minutes–hours | strict | needs-validation (license-gated) |
| Compliance search (Standard) | Purview portal + Security & Compliance PowerShell | `New-ComplianceSearch` etc. | – | – | eDiscovery Manager | Compliance | no | no | hours | strict | placeholder (no Graph parity) |

---

## Features without Microsoft APIs (placeholders)

The following ManageEngine-style reports do not map cleanly to a Microsoft API and will ship as documented placeholders:

| Feature | Reason | Possible alternative | Required license/role |
|---------|--------|----------------------|----------------------|
| Per-mailbox login (OWA) history | Not exposed via Graph; partial via Purview audit `MailboxLogin` | Purview audit search filter | Audit Standard+ |
| Real-time mailbox auditing toggle per user | Audit is tenant-wide in modern Exchange | – | Exchange admin |
| Detailed message trace beyond 10 days | Exchange Reporting Web Service / Defender required | Defender for O365 P2 | Defender for O365 |
| Bulk Exchange Online mailbox property edits | Requires Exchange PowerShell, not Graph | EXO PowerShell module run by worker (Phase 9, opt-in) | Exchange Admin |
| File classification (sensitivity labels at rest) inventory | Partial via Purview labels API | `/informationProtection/policy/labels` | E5 Compliance |
| Endpoint isolation / device actions | Defender for Endpoint API (separate from Graph) | Defender for Endpoint API integration | Defender for Endpoint |
| "Block user" tenant-wide | Composite: disable account + revoke sessions; not a single API | Compose with `User.EnableDisableAccount.All` + `User.RevokeSessions.All` (Phase 9, opt-in) | Cloud Application/User Admin |

These appear in the UI with an "API unavailable" badge and a link to this document.

---

## Throttling notes

See [throttling.md](throttling.md). Notable hot spots:

- `/auditLogs/signIns` and `/auditLogs/directoryAudits` have stricter limits than the rest of Graph. Use bounded windows and avoid wide unfiltered queries.
- SharePoint endpoints share per-tenant + per-app + per-application-identity limits. Sustain a per-tenant concurrency ≤ 4 by default.
- `/reports/*` endpoints cache server-side; refresh latency up to 48 hours. Do not poll faster than every 30 minutes.

## Implementation order in collectors (Phase 4)

1. Users, groups, memberships (foundation)
2. Subscribed SKUs + license details
3. Directory roles + assignments
4. Service health
5. Sign-ins + directory audits (license-permitting)
6. SharePoint site inventory
7. SharePoint drives/lists
8. Sharing permissions + sharing links
9. Mailbox settings + inbox rules
10. Teams inventory + members
11. Purview audit search (license-permitting)
