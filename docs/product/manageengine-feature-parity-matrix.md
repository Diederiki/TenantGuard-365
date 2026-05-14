# ManageEngine feature-parity matrix

> Inspired by the public capability sets of M365 Manager Plus,
> M365 Security Plus, and SharePoint Manager Plus. **No
> ManageEngine source code, branding, or copyrighted text is
> used.** The goal is parity of enterprise capability, not
> replication of UI or copy.

**Total features:** 72.

**Source of truth:** `apps/api/app/registry/features.py`.
**Live mirror:** `GET /api/catalog/features` and the
`/catalog` page in the web app.

## Status overview

| Status | Count |
|---|---|
| `needs_graph_permission` | 29 |
| `framework_ready` | 13 |
| `implemented_real_api` | 12 |
| `needs_exchange_powershell` | 8 |
| `needs_sharepoint_api_validation` | 4 |
| `implemented_mock_only` | 2 |
| `needs_defender` | 2 |
| `needs_purview` | 2 |

## By module

| Module | Count |
|---|---|
| `entra` | 12 |
| `exchange` | 11 |
| `management` | 10 |
| `audit` | 8 |
| `platform` | 6 |
| `sharepoint` | 6 |
| `security` | 4 |
| `service_health` | 2 |
| `reports` | 2 |
| `onedrive` | 2 |
| `teams` | 2 |
| `powerbi` | 2 |
| `delegation` | 1 |
| `content_search` | 1 |
| `remediation` | 1 |
| `compliance` | 1 |
| `yammer` | 1 |


## MVP priority

- **Platform — Central overview dashboard** (`platform.dashboard.overview`) · status `implemented_real_api`
- **Platform — Technician audit trail** (`platform.audit.technician`) · status `implemented_real_api`
- **Platform — Built-in roles** (`platform.rbac.builtin`) · status `implemented_real_api`
- **Platform — System health page** (`platform.health.system`) · status `implemented_real_api`
- **Platform — Export framework (CSV/XLSX/PDF/HTML)** (`platform.export.framework`) · status `implemented_real_api`
- **Platform — Scheduled reports + email delivery** (`platform.scheduled.reports`) · status `implemented_real_api`
- **Entra ID — Users — All users report** (`entra.users.all`) · status `implemented_real_api`
- **Entra ID — Users — Guest users report** (`entra.users.guests`) · status `implemented_real_api`
- **Entra ID — Groups — Group inventory** (`entra.groups.inventory`) · status `implemented_mock_only`
- **Entra ID — Roles — Directory role assignments** (`entra.roles.assignments`) · status `needs_graph_permission`
- **Entra ID — Licenses — License usage** (`entra.licenses.usage`) · status `implemented_real_api`
- **Entra ID — Sign-ins — Recent sign-ins + risk** (`entra.signins.recent`) · status `needs_graph_permission`
- **Entra ID — Audit — Directory audit** (`entra.audit.directory`) · status `needs_graph_permission`
- **Exchange — Mailboxes — Mailbox inventory** (`exchange.mailboxes.inventory`) · status `needs_graph_permission`
- **Exchange — Mailboxes — Mailbox size vs quota** (`exchange.mailboxes.size_quota`) · status `needs_graph_permission`
- **Exchange — Permissions — Mailbox FullAccess / SendAs / SendOnBehalfOf** (`exchange.permissions.full_access`) · status `needs_exchange_powershell`
- **Exchange — Risk — External forwarding rules** (`exchange.forwarding.external`) · status `needs_graph_permission`
- **Exchange — Audit — Mailbox owner / non-owner / delegate access** (`exchange.audit.owner`) · status `needs_graph_permission`
- **Exchange — Audit — Exchange admin activities** (`exchange.audit.admin`) · status `needs_graph_permission`
- **OneDrive — Inventory — OneDrive accounts** (`onedrive.accounts`) · status `needs_graph_permission`
- **OneDrive — Sharing — OneDrive sharing audit** (`onedrive.sharing`) · status `needs_graph_permission`
- **OneDrive — Audit — File create / modify / delete / move / rename / restore** (`onedrive.audit.files`) · status `needs_graph_permission`
- **SharePoint — Sites — Site inventory** (`sharepoint.sites.inventory`) · status `implemented_real_api`
- **SharePoint — Sharing — External-sharing-enabled sites** (`sharepoint.sites.external_sharing`) · status `needs_sharepoint_api_validation`
- **SharePoint — Permissions — Permission matrix (effective)** (`sharepoint.permissions.matrix`) · status `implemented_mock_only`
- **SharePoint — Sharing — Sharing links** (`sharepoint.sharing.links`) · status `needs_sharepoint_api_validation`
- **SharePoint — Sharing — External users + last access** (`sharepoint.external.users`) · status `needs_sharepoint_api_validation`
- **SharePoint — Permissions — Broken-inheritance items** (`sharepoint.broken_inheritance`) · status `needs_sharepoint_api_validation`
- **SharePoint — Audit — File access / modify / delete / move / rename / restore** (`sharepoint.audit.file_ops`) · status `needs_graph_permission`
- **SharePoint — Audit — Sharing invitation / link create / accept / revoke** (`sharepoint.audit.sharing_ops`) · status `needs_graph_permission`
- **Teams — Inventory — Team + channel inventory** (`teams.inventory`) · status `needs_graph_permission`
- **Teams — Audit — Team / channel create / delete / setting change** (`teams.audit.lifecycle`) · status `needs_graph_permission`
- **Service health — Service health overview + incidents** (`service_health.overview`) · status `implemented_real_api`
- **Security — Alerts — Security alerts** (`security.alerts.list`) · status `needs_graph_permission`
- **Security — Rules — Internal rule engine** (`security.rules.internal`) · status `implemented_real_api`

## Phase 2 priority

- **Platform — Add reports as dashboard widgets** (`platform.dashboard.widgets`) · status `framework_ready`
- **Platform — Custom roles + permission matrix UI** (`platform.rbac.custom`) · status `framework_ready`
- **Platform — Domain / attribute / virtual-tenant delegation** (`platform.delegation.scoped`) · status `framework_ready`
- **Platform — Notification routing** (`platform.notifications.framework`) · status `framework_ready`
- **Platform — Data retention policy** (`platform.retention.policy`) · status `framework_ready`
- **Entra ID — Users — Inactive users** (`entra.users.inactive`) · status `needs_graph_permission`
- **Entra ID — Users — Deleted users** (`entra.users.deleted`) · status `needs_graph_permission`
- **Entra ID — Groups — Empty groups** (`entra.groups.empty`) · status `needs_graph_permission`
- **Entra ID — Security — MFA / authentication method registration** (`entra.users.mfa`) · status `needs_graph_permission`
- **Entra ID — Security — Password expiry status** (`entra.password.status`) · status `needs_graph_permission`
- **Exchange — Mailboxes — Inactive mailboxes consuming licenses** (`exchange.mailboxes.inactive`) · status `needs_graph_permission`
- **Exchange — Mail traffic — Mail traffic + top senders/recipients** (`exchange.mail.traffic`) · status `needs_graph_permission`
- **Exchange — Threat — Spam / malware detection** (`exchange.mail.spam_malware`) · status `needs_defender`
- **Exchange — Mobile — Mobile / ActiveSync device inventory** (`exchange.mobile.devices`) · status `needs_exchange_powershell`
- **Exchange — Compliance — Litigation + in-place hold reports** (`exchange.litigation_hold`) · status `needs_exchange_powershell`
- **OneDrive — Audit — Sync device events** (`onedrive.audit.sync`) · status `needs_graph_permission`
- **SharePoint — Management — Add / remove / modify site permissions (dry-run)** (`sharepoint.mgmt.permissions`) · status `framework_ready`
- **Teams — Usage — Activity / device usage** (`teams.usage`) · status `needs_graph_permission`
- **Security — Investigations — Investigation cases** (`security.investigations.cases`) · status `framework_ready`
- **Compliance — DLP — DLP alerts** (`security.dlp.alerts`) · status `needs_purview`
- **Management — Entra — Reset password (dry-run)** (`management.entra.password_reset`) · status `framework_ready`
- **Management — Entra — Block / unblock user (dry-run)** (`management.entra.block_user`) · status `framework_ready`
- **Management — Entra — Assign / remove licenses (dry-run)** (`management.entra.licenses`) · status `framework_ready`

## Phase 3 priority

- **Exchange — OWA — OWA mailbox policies + logon** (`exchange.owa.policies`) · status `needs_exchange_powershell`
- **Exchange — Public folders — Public folder reports** (`exchange.public_folders`) · status `needs_exchange_powershell`
- **SharePoint — Management — Manage site groups (create / delete / membership)** (`sharepoint.mgmt.groups`) · status `framework_ready`
- **Teams — Management — Create / update / delete teams (dry-run)** (`teams.mgmt.create_team`) · status `framework_ready`
- **Security — Content search — Content search profiles + scheduled runs** (`security.content_search.profiles`) · status `needs_purview`
- **Security — Remediation — Auto-remediation policies (dry-run)** (`security.remediation.policies`) · status `framework_ready`
- **Security — Defender — Defender advanced hunting** (`security.defender.hunting`) · status `needs_defender`
- **Power BI — Audit — Dashboard / report lifecycle audit** (`powerbi.audit.dashboards`) · status `needs_graph_permission`
- **Power BI — Audit — Trial subscriptions, content packs, admin portal** (`powerbi.audit.subscriptions`) · status `needs_graph_permission`
- **Management — Exchange — Modify mailbox attributes (dry-run)** (`management.exchange.mailbox_attrs`) · status `needs_exchange_powershell`
- **Management — Exchange — Configure mail forwarding (dry-run)** (`management.exchange.forwarding`) · status `needs_exchange_powershell`
- **Management — Exchange — Configure internal / external auto-reply** (`management.exchange.auto_reply`) · status `needs_graph_permission`
- **Management — Exchange — Activate litigation hold** (`management.exchange.litigation_hold`) · status `needs_exchange_powershell`

## Future priority

- **Viva Engage — Usage — Viva Engage usage + audit** (`yammer.usage`) · status `needs_graph_permission`

## Full matrix

| Key | Area / Feature | Status | Priority | Source | Endpoint | App scopes | License | Risk | UI | Approval | Dry-run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `platform.dashboard.overview` | **Platform** — Central overview dashboard | `implemented_real_api` | MVP | — | — | — | — | low | [/](/) | no | no |
| `platform.dashboard.widgets` | **Platform** — Add reports as dashboard widgets | `framework_ready` | Phase 2 | — | — | — | — | low | [/](/) | no | no |
| `platform.audit.technician` | **Platform** — Technician audit trail | `implemented_real_api` | MVP | — | — | — | — | low | [/audit](/audit) | no | no |
| `platform.rbac.builtin` | **Platform** — Built-in roles | `implemented_real_api` | MVP | — | — | — | — | low | [/delegation](/delegation) | no | no |
| `platform.rbac.custom` | **Platform** — Custom roles + permission matrix UI | `framework_ready` | Phase 2 | — | — | — | — | low | [/delegation](/delegation) | no | no |
| `platform.delegation.scoped` | **Platform** — Domain / attribute / virtual-tenant delegation | `framework_ready` | Phase 2 | — | — | — | — | low | — | no | no |
| `platform.health.system` | **Platform** — System health page | `implemented_real_api` | MVP | — | — | — | — | low | [/system-health](/system-health) | no | no |
| `platform.notifications.framework` | **Platform** — Notification routing | `framework_ready` | Phase 2 | — | — | — | — | low | [/notifications](/notifications) | no | no |
| `platform.retention.policy` | **Platform** — Data retention policy | `framework_ready` | Phase 2 | — | — | — | — | low | [/settings/retention](/settings/retention) | no | no |
| `platform.export.framework` | **Platform** — Export framework (CSV/XLSX/PDF/HTML) | `implemented_real_api` | MVP | — | — | — | — | medium | [/exports](/exports) | no | no |
| `platform.scheduled.reports` | **Platform** — Scheduled reports + email delivery | `implemented_real_api` | MVP | — | — | — | — | low | [/reports/scheduled](/reports/scheduled) | no | no |
| `entra.users.all` | **Entra ID — Users** — All users report | `implemented_real_api` | MVP | Graph v1.0 | `/users` | `User.Read.All` | — | low | [/entra/users](/entra/users) | no | no |
| `entra.users.guests` | **Entra ID — Users** — Guest users report | `implemented_real_api` | MVP | Graph v1.0 | `/users?$filter=userType eq 'Guest'` | `User.Read.All` | — | low | [/entra/users](/entra/users) | no | no |
| `entra.users.inactive` | **Entra ID — Users** — Inactive users | `needs_graph_permission` | Phase 2 | Graph beta | `/users + /reports/getOffice365ActiveUserDetail` | `AuditLog.Read.All` | Entra ID P1 | low | — | no | no |
| `entra.users.deleted` | **Entra ID — Users** — Deleted users | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/directory/deletedItems/microsoft.graph.user` | `User.Read.All` | — | low | — | no | no |
| `entra.groups.inventory` | **Entra ID — Groups** — Group inventory | `implemented_mock_only` | MVP | Graph v1.0 | `/groups` | `Group.Read.All` | — | low | [/entra/groups](/entra/groups) | no | no |
| `entra.groups.empty` | **Entra ID — Groups** — Empty groups | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/groups + /groups/{id}/members/$count` | `Group.Read.All` | — | low | — | no | no |
| `entra.roles.assignments` | **Entra ID — Roles** — Directory role assignments | `needs_graph_permission` | MVP | Graph v1.0 | `/directoryRoles` | `RoleManagement.Read.Directory` | — | low | [/entra/roles](/entra/roles) | no | no |
| `entra.licenses.usage` | **Entra ID — Licenses** — License usage | `implemented_real_api` | MVP | Graph v1.0 | `/subscribedSkus` | `Organization.Read.All` | — | low | [/entra/licenses](/entra/licenses) | no | no |
| `entra.signins.recent` | **Entra ID — Sign-ins** — Recent sign-ins + risk | `needs_graph_permission` | MVP | Graph beta | `/auditLogs/signIns` | `AuditLog.Read.All` | Entra ID P1 (for risk fields) | low | [/entra/signins](/entra/signins) | no | no |
| `entra.audit.directory` | **Entra ID — Audit** — Directory audit | `needs_graph_permission` | MVP | Graph beta | `/auditLogs/directoryAudits` | `AuditLog.Read.All` | — | low | [/entra/audit](/entra/audit) | no | no |
| `entra.users.mfa` | **Entra ID — Security** — MFA / authentication method registration | `needs_graph_permission` | Phase 2 | Graph beta | `/reports/authenticationMethods/userRegistrationDetails` | `AuditLog.Read.All, UserAuthenticationMethod.Read.All` | — | low | — | no | no |
| `entra.password.status` | **Entra ID — Security** — Password expiry status | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/users?$select=passwordPolicies,lastPasswordChangeDateTime` | `User.Read.All` | — | low | — | no | no |
| `exchange.mailboxes.inventory` | **Exchange — Mailboxes** — Mailbox inventory | `needs_graph_permission` | MVP | Graph v1.0 + /reports | `/users/{id}/mailboxSettings + /reports/getMailboxUsageDetail` | `MailboxSettings.Read, Reports.Read.All` | — | low | [/exchange/mailboxes](/exchange/mailboxes) | no | no |
| `exchange.mailboxes.size_quota` | **Exchange — Mailboxes** — Mailbox size vs quota | `needs_graph_permission` | MVP | Graph v1.0 | `/reports/getMailboxUsageQuotaStatusMailboxCounts` | `Reports.Read.All` | — | low | — | no | no |
| `exchange.mailboxes.inactive` | **Exchange — Mailboxes** — Inactive mailboxes consuming licenses | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/reports/getOffice365ActiveUserDetail` | `Reports.Read.All` | — | low | — | no | no |
| `exchange.mail.traffic` | **Exchange — Mail traffic** — Mail traffic + top senders/recipients | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/reports/getEmailActivityCounts + getMailboxUsageDetail` | `Reports.Read.All` | — | low | — | no | no |
| `exchange.mail.spam_malware` | **Exchange — Threat** — Spam / malware detection | `needs_defender` | Phase 2 | Defender / Graph beta | `/security/threatSubmissions` | `ThreatSubmission.Read.All` | Defender for Office 365 | low | — | no | no |
| `exchange.permissions.full_access` | **Exchange — Permissions** — Mailbox FullAccess / SendAs / SendOnBehalfOf | `needs_exchange_powershell` | MVP | Exchange Online PowerShell | `Get-MailboxPermission / Get-RecipientPermission` | — | — | high | [/exchange/permissions](/exchange/permissions) | no | no |
| `exchange.forwarding.external` | **Exchange — Risk** — External forwarding rules | `needs_graph_permission` | MVP | Graph v1.0 | `/users/{id}/messageRules` | `MailboxSettings.Read` | — | critical | [/exchange/forwarding-risk](/exchange/forwarding-risk) | no | no |
| `exchange.mobile.devices` | **Exchange — Mobile** — Mobile / ActiveSync device inventory | `needs_exchange_powershell` | Phase 2 | Exchange Online PowerShell | `Get-MobileDevice` | — | — | low | — | no | no |
| `exchange.litigation_hold` | **Exchange — Compliance** — Litigation + in-place hold reports | `needs_exchange_powershell` | Phase 2 | Exchange Online PowerShell | `Get-Mailbox (LitigationHoldEnabled)` | — | Exchange Plan 2 / E5 | low | — | no | no |
| `exchange.owa.policies` | **Exchange — OWA** — OWA mailbox policies + logon | `needs_exchange_powershell` | Phase 3 | Exchange Online PowerShell | `Get-OwaMailboxPolicy` | — | — | low | — | no | no |
| `exchange.public_folders` | **Exchange — Public folders** — Public folder reports | `needs_exchange_powershell` | Phase 3 | Exchange Online PowerShell | `Get-PublicFolder / Get-MailPublicFolder` | — | — | low | — | no | no |
| `exchange.audit.owner` | **Exchange — Audit** — Mailbox owner / non-owner / delegate access | `needs_graph_permission` | MVP | Graph beta | `/auditLogs/directoryAudits + /security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `exchange.audit.admin` | **Exchange — Audit** — Exchange admin activities | `needs_graph_permission` | MVP | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `onedrive.accounts` | **OneDrive — Inventory** — OneDrive accounts | `needs_graph_permission` | MVP | Graph v1.0 | `/reports/getOneDriveUsageAccountDetail` | `Reports.Read.All` | — | low | [/onedrive/accounts](/onedrive/accounts) | no | no |
| `onedrive.sharing` | **OneDrive — Sharing** — OneDrive sharing audit | `needs_graph_permission` | MVP | Graph v1.0 | `/drives/{id}/items + /permissions` | `Files.Read.All` | — | high | [/onedrive/sharing](/onedrive/sharing) | no | no |
| `onedrive.audit.files` | **OneDrive — Audit** — File create / modify / delete / move / rename / restore | `needs_graph_permission` | MVP | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `onedrive.audit.sync` | **OneDrive — Audit** — Sync device events | `needs_graph_permission` | Phase 2 | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `sharepoint.sites.inventory` | **SharePoint — Sites** — Site inventory | `implemented_real_api` | MVP | Graph v1.0 + /reports | `/sites + /reports/getSharePointSiteUsageDetail` | `Sites.Read.All, Reports.Read.All` | — | low | [/sharepoint/sites](/sharepoint/sites) | no | no |
| `sharepoint.sites.external_sharing` | **SharePoint — Sharing** — External-sharing-enabled sites | `needs_sharepoint_api_validation` | MVP | SharePoint REST + Graph | `/sites/{id}/settings` | `Sites.FullControl.All` | — | high | — | no | no |
| `sharepoint.permissions.matrix` | **SharePoint — Permissions** — Permission matrix (effective) | `implemented_mock_only` | MVP | Graph v1.0 | `/sites/{id}/permissions + lists/{id}/items?$expand=fields,hasUniqueRoleAssignments` | `Sites.FullControl.All` | — | high | [/sharepoint/permissions](/sharepoint/permissions) | no | no |
| `sharepoint.sharing.links` | **SharePoint — Sharing** — Sharing links | `needs_sharepoint_api_validation` | MVP | Graph beta | `/sites/{id}/lists/{id}/items/{id}/permissions` | `Sites.FullControl.All` | — | critical | [/sharepoint/sharing-links](/sharepoint/sharing-links) | no | no |
| `sharepoint.external.users` | **SharePoint — Sharing** — External users + last access | `needs_sharepoint_api_validation` | MVP | Graph v1.0 | `/sites/{id}/permissions + invitedUser` | `Sites.FullControl.All` | — | high | [/sharepoint/external-users](/sharepoint/external-users) | no | no |
| `sharepoint.broken_inheritance` | **SharePoint — Permissions** — Broken-inheritance items | `needs_sharepoint_api_validation` | MVP | Graph v1.0 | `/sites/{id}/lists/{id}/items?$filter=hasUniqueRoleAssignments eq true` | `Sites.FullControl.All` | — | low | [/sharepoint/broken-inheritance](/sharepoint/broken-inheritance) | no | no |
| `sharepoint.audit.file_ops` | **SharePoint — Audit** — File access / modify / delete / move / rename / restore | `needs_graph_permission` | MVP | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `sharepoint.audit.sharing_ops` | **SharePoint — Audit** — Sharing invitation / link create / accept / revoke | `needs_graph_permission` | MVP | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `sharepoint.mgmt.permissions` | **SharePoint — Management** — Add / remove / modify site permissions (dry-run) | `framework_ready` | Phase 2 | Graph v1.0 | `POST /sites/{id}/permissions` | `Sites.FullControl.All` | — | critical | — | yes | yes |
| `sharepoint.mgmt.groups` | **SharePoint — Management** — Manage site groups (create / delete / membership) | `framework_ready` | Phase 3 | SharePoint REST | `/web/sitegroups` | — | — | critical | — | yes | yes |
| `teams.inventory` | **Teams — Inventory** — Team + channel inventory | `needs_graph_permission` | MVP | Graph v1.0 | `/teams + /teams/{id}/channels + /teams/{id}/members` | `Team.ReadBasic.All, Channel.ReadBasic.All, TeamMember.Read.All` | — | low | [/teams/inventory](/teams/inventory) | no | no |
| `teams.usage` | **Teams — Usage** — Activity / device usage | `needs_graph_permission` | Phase 2 | Graph v1.0 | `/reports/getTeamsUserActivityUserDetail` | `Reports.Read.All` | — | low | — | no | no |
| `teams.audit.lifecycle` | **Teams — Audit** — Team / channel create / delete / setting change | `needs_graph_permission` | MVP | Graph beta | `/security/auditLog/queries` | `AuditLog.Read.All` | — | low | — | no | no |
| `teams.mgmt.create_team` | **Teams — Management** — Create / update / delete teams (dry-run) | `framework_ready` | Phase 3 | Graph v1.0 | `POST /teams` | `Team.Create, TeamSettings.ReadWrite.All` | — | high | — | yes | yes |
| `service_health.overview` | **Service health** — Service health overview + incidents | `implemented_real_api` | MVP | Graph v1.0 | `/admin/serviceAnnouncement/healthOverviews + /issues + /messages` | `ServiceHealth.Read.All, ServiceMessage.Read.All` | — | low | [/service-health](/service-health) | no | no |
| `security.alerts.list` | **Security — Alerts** — Security alerts | `needs_graph_permission` | MVP | Graph v1.0 | `/security/alerts_v2` | `SecurityEvents.Read.All, SecurityAlert.Read.All` | — | low | [/security/alerts](/security/alerts) | no | no |
| `security.rules.internal` | **Security — Rules** — Internal rule engine | `implemented_real_api` | MVP | — | — | — | — | low | [/security/rules](/security/rules) | no | no |
| `security.investigations.cases` | **Security — Investigations** — Investigation cases | `framework_ready` | Phase 2 | — | — | — | — | low | [/security/investigations](/security/investigations) | no | no |
| `security.content_search.profiles` | **Security — Content search** — Content search profiles + scheduled runs | `needs_purview` | Phase 3 | Purview eDiscovery (Graph beta) | `/security/cases/ediscoveryCases` | `eDiscovery.Read.All` | Purview / E5 Compliance | critical | [/content-search](/content-search) | yes | no |
| `security.remediation.policies` | **Security — Remediation** — Auto-remediation policies (dry-run) | `framework_ready` | Phase 3 | — | — | — | — | critical | [/remediation](/remediation) | yes | yes |
| `security.dlp.alerts` | **Compliance — DLP** — DLP alerts | `needs_purview` | Phase 2 | Purview / Graph beta | `/security/dataLossPrevention` | — | Purview DLP | low | — | no | no |
| `security.defender.hunting` | **Security — Defender** — Defender advanced hunting | `needs_defender` | Phase 3 | Defender API | `/api/advancedhunting/run` | — | Defender for Endpoint / O365 P2 | low | — | no | no |
| `powerbi.audit.dashboards` | **Power BI — Audit** — Dashboard / report lifecycle audit | `needs_graph_permission` | Phase 3 | Graph beta | `/security/auditLog/queries (Power BI workload)` | `AuditLog.Read.All` | Power BI Pro | low | — | no | no |
| `yammer.usage` | **Viva Engage — Usage** — Viva Engage usage + audit | `needs_graph_permission` | Future | Graph beta (limited) | `/reports/getYammerActivityUserDetail (deprecated)` | — | — | low | — | no | no |
| `powerbi.audit.subscriptions` | **Power BI — Audit** — Trial subscriptions, content packs, admin portal | `needs_graph_permission` | Phase 3 | Graph beta | `/security/auditLog/queries` | — | Power BI Pro | low | — | no | no |
| `management.entra.password_reset` | **Management — Entra** — Reset password (dry-run) | `framework_ready` | Phase 2 | Graph v1.0 | `POST /users/{id}/authentication/methods/{id}/resetPassword` | `UserAuthenticationMethod.ReadWrite.All` | — | high | — | yes | yes |
| `management.entra.block_user` | **Management — Entra** — Block / unblock user (dry-run) | `framework_ready` | Phase 2 | Graph v1.0 | `PATCH /users/{id} {accountEnabled:false}` | `User.ReadWrite.All` | — | high | — | yes | yes |
| `management.entra.licenses` | **Management — Entra** — Assign / remove licenses (dry-run) | `framework_ready` | Phase 2 | Graph v1.0 | `POST /users/{id}/assignLicense` | `User.ReadWrite.All` | — | medium | — | yes | yes |
| `management.exchange.mailbox_attrs` | **Management — Exchange** — Modify mailbox attributes (dry-run) | `needs_exchange_powershell` | Phase 3 | Exchange Online PowerShell | `Set-Mailbox / Set-CASMailbox` | — | — | high | — | yes | yes |
| `management.exchange.forwarding` | **Management — Exchange** — Configure mail forwarding (dry-run) | `needs_exchange_powershell` | Phase 3 | Exchange Online PowerShell | `Set-Mailbox -ForwardingSmtpAddress` | — | — | critical | — | yes | yes |
| `management.exchange.auto_reply` | **Management — Exchange** — Configure internal / external auto-reply | `needs_graph_permission` | Phase 3 | Graph v1.0 | `PATCH /users/{id}/mailboxSettings/automaticRepliesSetting` | `MailboxSettings.ReadWrite` | — | medium | — | yes | yes |
| `management.exchange.litigation_hold` | **Management — Exchange** — Activate litigation hold | `needs_exchange_powershell` | Phase 3 | Exchange Online PowerShell | `Set-Mailbox -LitigationHoldEnabled` | — | Exchange Plan 2 / E5 | high | — | yes | yes |
## Next implementation steps

1. Light up the **needs_graph_permission** entries by configuring
   an app registration with the listed `App scopes`. Most are
   read-only (`User.Read.All`, `Group.Read.All`,
   `MailboxSettings.Read`, `Files.Read.All`, etc.).
2. Validate the **needs_sharepoint_api_validation** entries
   against a dev tenant. Microsoft has changed sharing-link
   surface area twice in 2024–2025.
3. Schedule a Purview eDiscovery validation pass before
   promoting `security.content_search.*` past framework.
4. Wire `app.management.*` actions to the real Graph + Exchange
   PowerShell paths. They are framework-ready with audit +
   approval + dry-run gates already in place.
5. Implement the four "framework" settings pages (general,
   security, retention, notifications) with their backing
   tables in Phase 29.
