# Audit catalog

Two audit surfaces live in TenantGuard 365:

1. **Technician audit log** — internal append-only log of every privileged
   action on the platform itself. Always-on.
2. **Microsoft 365 audit ingestion** — collectors that read the Unified
   Audit Log (`/security/auditLog/queries`) plus the directory audit
   feed (`/auditLogs/directoryAudits`) and the sign-in feed
   (`/auditLogs/signIns`).

## Audit profile framework

Each ingest profile carries:

- Service (Exchange / Entra / OneDrive / SharePoint / Teams / Power BI /
  Viva Engage)
- Category (file ops, sharing ops, lifecycle, admin, threat)
- Actions (multi-select)
- Filter set (time range, business hours, principal, target, IP,
  application)
- Save filtered view (named saved-search)
- Export (CSV/XLSX/PDF/HTML — sensitive UAL raw is metadata-only by
  default; raw content gated behind explicit secure-mode role)
- Schedule (cron-style)
- Email recipient channel

Profile metadata lives in `audit_profiles` (Phase 2 table). Runs land in
`audit_runs`. Output rows index into OpenSearch for search.

## Services + categories

| Service | Status | Notes |
|---|---|---|
| Exchange Online | needs Graph permission | UAL workload `Exchange`. Owner / non-owner / delegate access + admin activities. |
| Entra ID | needs Graph permission | Combined directory audit + sign-ins. |
| OneDrive | needs Graph permission | UAL workload `OneDrive`. File ops + sync events. |
| SharePoint Online | needs Graph permission | UAL workload `SharePoint`. File + sharing + folder ops. |
| Teams | needs Graph permission | UAL workload `MicrosoftTeams`. Lifecycle + setting changes. |
| Power BI | Phase 3 | UAL workload `PowerBI`. License-gated. |
| Microsoft Forms | Phase 3 | UAL workload `MicrosoftForms`. Mostly compliance use cases. |
| Microsoft Streams | Phase 3 | UAL workload `MicrosoftStream` / Stream-on-SharePoint. |
| Power Apps / Power Automate | Phase 3 | UAL workloads `PowerApp` / `Flow`. |
| Viva Engage | Future | API surface migrating. |
| Microsoft Sway | deprecated | Service deprecated by Microsoft — surfaced for legacy completeness only. |

## Compliance auditing

| Capability | Status | Source |
|---|---|---|
| eDiscovery activity | needs Purview | `/security/cases/ediscoveryCases` |
| DLP rule creation / modification / hits | needs Purview | Purview DLP audit |
| Sensitive-information-type lookup | needs Purview | Purview |
| EOP recipient / group / user object retrieval | Phase 2 | UAL workload `Exchange` admin audit |

## Retention + archive

Audit events land in:

- `technician_audit_log` (platform actions) — retained 365 days by
  default. Append-only DB role planned (Phase 28 OPEN).
- OpenSearch `tg365-audit-*` indices — rolling-30-day ISM policy
  (Phase 2 documentation; index template not yet shipped).
- MinIO `tg365-evidence` bucket — for content-search exports + raw event
  archive when configured.

Retention is policy-driven (`/settings/retention`).
