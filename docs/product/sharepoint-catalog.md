# SharePoint catalog

SharePoint visibility + control is one of the platform's top-priority
modules. This file lists every SharePoint-related capability, what
backs it, and what status it ships in today.

## Reporting

| Capability | Status | Source | UI |
|---|---|---|---|
| Site collections / sites | **live** | `/sites` + `/reports/getSharePointSiteUsageDetail` | `/sharepoint/sites` |
| Site owners + admins | needs Graph perm | `/sites/{id}/permissions` + `/sites/{id}/lists/User Information List` | `/sharepoint/sites/[id]` |
| Site storage + object count | live (via report) | `/reports/getSharePointSiteUsageDetail` | `/sharepoint/sites` |
| External user access | needs validation | `/sites/{id}/permissions` (invitedUser) | `/sharepoint/external-users` |
| Site templates | live | `/sites/{id}` webTemplate | `/sharepoint/sites/[id]` |
| Site activity | needs Graph perm | `/reports/getSharePointActivityUserDetail` | — |
| Most viewed sites | needs Graph perm | `/reports/getSharePointSiteUsageDetail` | — |
| External-sharing-enabled sites | needs validation | `/sites/{id}/settings` (SharingCapability) | — |
| Lists + libraries inventory | needs Graph perm | `/sites/{id}/lists` | — |
| Document library inventory | needs Graph perm | `/sites/{id}/drives` | — |
| Large lists / libraries | needs Graph perm | `/sites/{id}/lists/{id}/items/$count` | — |
| Orphaned users / groups | needs validation | Compute from `permissions` minus active Entra principals | — |
| Permissions / users / groups | mock-only today | `/sites/{id}/permissions` + lists/permissions | `/sharepoint/permissions` |
| Site group membership | needs validation | SharePoint REST `/web/sitegroups` | — |
| Broken inheritance / unique permissions | needs validation | `lists/{id}/items?$filter=hasUniqueRoleAssignments eq true` | `/sharepoint/broken-inheritance` |

## Sharing

| Capability | Status | UI |
|---|---|---|
| Anonymous links | needs validation | `/sharepoint/sharing-links` |
| Company-wide links | needs validation | `/sharepoint/sharing-links` |
| Specific-people links | needs validation | `/sharepoint/sharing-links` |
| Sharing policies | needs validation | (Phase 2 settings page) |
| External users + last access | needs validation | `/sharepoint/external-users` |

## Auditing

| Action | Source |
|---|---|
| Accessed / checked-in / checked-out / copied / deleted | UAL workload `SharePoint` |
| Discarded checkouts / downloaded / modified / moved / renamed / restored / uploaded | UAL |
| Sharing invitations: created / accepted / denied / withdrawn / revoked | UAL |
| Anonymous / company links: created / used / removed / updated | UAL |
| Folders: created / deleted / modified / moved / renamed / restored | UAL |
| Created / deleted site collections | UAL |
| Permission changes | UAL |
| Sharing policy changes | UAL |
| Group create / delete / update / member add / remove | UAL |
| Renamed sites | UAL |
| Enabled RSS feeds | UAL |
| Enabled document preview | UAL |
| Site admin add / remove | UAL |

All audited via the unified collector against
`/security/auditLog/queries`, filtered by SharePoint workload.

## Management (dry-run only by default)

| Action | Status | Risk |
|---|---|---|
| Add / remove / modify site permissions | framework-ready | critical |
| Create / delete / modify site groups | framework-ready | critical |
| Bulk membership changes | framework-ready | critical |
| Renamed / restored items (rollback) | framework-ready | high |
| Template-based bulk operations | framework-ready | critical |

Every management action requires the feature flag
`FEATURE_REMEDIATION_ENABLED=true` AND per-policy enable AND analyst
approval. Dry-run is the only mode unless explicitly toggled in
`/settings/security`.

## Monitoring dashboards (Phase 2)

- SharePoint service health (sourced from M365 service health).
- SharePoint security dashboard (anonymous-link count, external-user
  count, FullAccess-style high-risk grants).
- Permission risk dashboard.
- Sharing risk dashboard.
- External access dashboard.

## Hybrid + on-prem (deferred)

| Capability | Status |
|---|---|
| SharePoint on-prem reporting | future_module / on-prem connector |
| Web applications + content databases inventory | future_module |
| SharePoint migration / backup | future_module — partner integration TBD |

The current SharePoint feature set is **online-only**. On-prem is a
deliberate non-goal for the MVP; revisit in Future per customer demand.

## Export formats

SharePoint reports support CSV, XLSX, PDF, HTML.
