# Report catalog

Built from the parity matrix. Reports are the read-only side of the
registry: anything with `status in {implemented_real_api,
implemented_mock_only}` is reachable today; everything else is
configuration- or licence-gated.

> Live data: `GET /api/catalog/features?module=...` or the
> `/catalog?module=...` page in the web app.

## Conventions

- All reports support **CSV** export. Reports flagged with
  `export_formats` additionally support XLSX/PDF/HTML.
- All reports are paginated (keyset where the dataset is large).
- All reports respect RBAC. A user without the report's underlying
  `<module>.<resource>.read` permission cannot run it.
- Sensitive reports (audit raw, content-search, security alerts) require
  a justification reason captured on every run.

## Categories

### Exchange Online
| Report | Status | Source | License |
|---|---|---|---|
| Mailbox inventory | needs Graph permission | `/reports/getMailboxUsageDetail` + `MailboxSettings.Read` | — |
| Mailbox size vs quota | needs Graph permission | `/reports/getMailboxUsageQuotaStatusMailboxCounts` | — |
| Inactive mailboxes (license waste) | Phase 2 | `/reports/getOffice365ActiveUserDetail` | — |
| Mail traffic + top senders / recipients | Phase 2 | `/reports/getEmailActivityCounts` | — |
| Spam / malware detection | Phase 2 | Defender / `/security/threatSubmissions` | Defender for Office 365 |
| FullAccess / SendAs / SendOnBehalfOf | needs Exchange PS | `Get-MailboxPermission` | — |
| External forwarding rules | MVP | `/users/{id}/messageRules` | — |
| Mobile / ActiveSync devices | Phase 2 | `Get-MobileDevice` | — |
| Litigation hold report | Phase 2 | `Get-Mailbox -LitigationHoldEnabled` | Exchange Plan 2 / E5 |
| OWA mailbox policies + logon | Phase 3 | `Get-OwaMailboxPolicy` | — |
| Public folder reports | Phase 3 | `Get-PublicFolder` | — |

### Entra ID
| Report | Status | Source | License |
|---|---|---|---|
| All users | live | `/users` | — |
| Guest users | live | `/users?$filter=userType eq 'Guest'` | — |
| Inactive users | Phase 2 | `/reports/getOffice365ActiveUserDetail` | Entra ID P1 |
| Deleted users | Phase 2 | `/directory/deletedItems` | — |
| Group inventory | mock-only | `/groups` | — |
| Empty groups | Phase 2 | `/groups + members/$count` | — |
| Directory role assignments | MVP | `/directoryRoles` | — |
| License usage | live | `/subscribedSkus` | — |
| Recent sign-ins + risk | MVP | `/auditLogs/signIns` | Entra ID P1 (risk fields) |
| Directory audit | MVP | `/auditLogs/directoryAudits` | — |
| MFA / authentication methods | Phase 2 | `/reports/authenticationMethods` | — |
| Password expiry | Phase 2 | `/users` lastPasswordChangeDateTime | — |

### OneDrive
| Report | Status |
|---|---|
| OneDrive accounts | needs Graph permission |
| OneDrive sharing audit | needs Graph permission |

### SharePoint Online
| Report | Status |
|---|---|
| Site inventory | live |
| External-sharing-enabled sites | needs validation |
| Permission matrix | mock-only |
| Sharing links | needs validation |
| External users + last access | needs validation |
| Broken inheritance | needs validation |

### Teams
| Report | Status |
|---|---|
| Team + channel inventory | needs Graph permission |
| Activity / device usage | Phase 2 |

### Service health
| Report | Status |
|---|---|
| Service health + incidents | live |

## Schedules

Every report listed above can be scheduled. Use `/reports/scheduled` to
configure cron + recipient channels (email / Teams webhook / generic
webhook). Phase-2 work: surface schedule edit UI per report.

## Custom reports

Builder UI is a framework. Today custom reports are defined in
`apps/api/app/reports/builtins.py`. Phase-2 work: surface DDL-style
builder in `/reports/builder`.
