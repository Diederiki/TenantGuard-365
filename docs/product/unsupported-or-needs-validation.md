# Unsupported / Needs validation

The honest list of capabilities that either don't have a clean
Microsoft API today, require a licence we haven't validated against,
or were deprecated by Microsoft. **No item in here is a placeholder
pretending to work.** Every page that depends on one of these carries
the `needs-tenant`, `needs-purview`, `needs-defender`, or `framework`
status badge.

## Deprecated by Microsoft

| Capability | Why deprecated | Replacement |
|---|---|---|
| Yammer audit endpoints | Service rebranded as Viva Engage; old `/reports/getYammerActivityUserDetail` shape changed and may return null. | Viva Engage admin centre + Graph workload (in flux). |
| Microsoft Sway | Service deprecated in 2024. | None — surfaced for legacy reporting only. |
| Clutter | Replaced by Focused Inbox. | None. |

## Needs Microsoft licence

| Capability | Licence |
|---|---|
| Risk fields on sign-in events | Entra ID P1 (Risk) |
| Identity Protection signals | Entra ID P2 |
| Defender for Office 365 detections + safe attachments / links | Defender for Office 365 P1+ |
| Defender Advanced Hunting (KQL) | Defender for Endpoint Plan 2 or Defender for O365 Plan 2 |
| Litigation hold + in-place hold | Exchange Plan 2 / E5 |
| Content search / eDiscovery | Purview (E5 Compliance) |
| DLP rule reporting | Purview DLP |
| Insider Risk signals | Purview IRM |

## Needs tenant validation

These have a known endpoint but Microsoft has reshaped the surface area
in 2024–2025 — code is framework-ready, validation against a live tenant
is the gating step.

| Capability | Endpoint | What to validate |
|---|---|---|
| SharePoint sharing links | `/sites/{id}/lists/{id}/items/{id}/permissions` | Returned `link` object shape; expiry semantics. |
| SharePoint external users | `/sites/{id}/permissions` | Whether `invitedUser` is consistently present. |
| SharePoint broken inheritance | `/sites/{id}/lists/{id}/items?$filter=hasUniqueRoleAssignments eq true` | Throughput vs page size at 10k+ items. |
| Site-level sharing capability | `/sites/{id}/settings` | Field availability + SharePoint REST fallback. |
| Power BI workload audit | `/security/auditLog/queries` | Whether RBAC scopes apply at workload level. |

## Needs Exchange PowerShell

The PowerShell-only surface is wrapped behind a worker job that
imports the `ExchangeOnlineManagement` module and runs cmdlets via a
service principal with certificate auth.

| Cmdlet | Used for |
|---|---|
| `Get-MailboxPermission` / `Get-RecipientPermission` | FullAccess / SendAs / SendOnBehalfOf |
| `Get-Mailbox` | LitigationHoldEnabled + audit settings |
| `Get-MobileDevice` | ActiveSync inventory |
| `Get-OwaMailboxPolicy` | OWA policy / logon |
| `Get-PublicFolder` / `Get-MailPublicFolder` | Public folder inventory |
| `Set-Mailbox -ForwardingSmtpAddress` | Forwarding management (dry-run) |
| `Set-Mailbox -LitigationHoldEnabled` | Hold management (dry-run) |
| `Set-CASMailbox` | IMAP/MAPI/POP/OWA/EWS toggles (dry-run) |

Not yet shipped — PowerShell tooling lands in Phase 3.

## Not in scope

| Capability | Why |
|---|---|
| SharePoint on-prem | Different connector model. Skip unless a paying customer asks. |
| SharePoint Online backup / restore | Acquire via partner (e.g. Microsoft 365 Backup). Building our own snapshot service is out of scope. |
| Email body content rendering | Treat as PII; never surface in the UI. Content-search exports include metadata only by default. |
| Real-time stream of every Graph change | `change notifications` exist but require a public webhook endpoint; deferred until production deployment story is finalised. |
