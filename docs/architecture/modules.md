# Architecture — Modules

> The platform is composed of self-contained modules. Adding a new module = registering a manifest and adding code under `apps/api/modules/<name>` and `apps/worker/modules/<name>`.

## Module manifest (planned shape)

Each module declares itself via a Python dataclass (api side) and a TS object (web side):

```python
# apps/api/modules/sharepoint/manifest.py (illustrative)
ModuleManifest(
    key="sharepoint",
    display_name="SharePoint Online",
    icon="library",
    requires_permissions=["Sites.Read.All", "Files.Read.All"],
    required_roles=[],
    license_dependencies=["SharePoint Online (Plan 1+)"],
    collectors=[SiteInventoryCollector, DriveCollector, PermissionsCollector, ...],
    reports=[...],
    rules=[...],
)
```

The web app consumes a `/api/modules` index and renders navigation from it. RBAC and permission gaps gate visibility.

## Module inventory

### 1. Core platform
- Authentication, sessions, CSRF
- Authorization (RBAC dependency)
- Tenant settings
- User profile
- Technician audit trail
- Job scheduler API
- Notification engine
- Report engine (definition, builder, execution)
- Export engine (CSV / XLSX / PDF / HTML, streaming)
- Search engine wrapper (OpenSearch)
- Secrets / token-cache provider

### 2. Microsoft Graph connector
- Central Graph client (`apps/api/graph/client.py`)
- Token handling, retry, throttling (429 + `Retry-After`)
- Pagination, delta queries, change notifications
- Permission inventory, gap detector
- API capability registry (sourced from `docs/microsoft-graph/capability-matrix.md`)

### 3. Entra ID
- Collectors: users, groups, memberships, roles, role assignments, licenses, sign-ins, directory audits, applications/service principals
- Reports: see [ROADMAP](../../ROADMAP.md#phase-5)
- Rules: failed sign-in patterns, admin role changes, risky app consent

### 4. Exchange Online
- Collectors: mailboxes, mailbox permissions, mailbox audit events, forwarding rules (via mailbox settings where available)
- Reports: mailbox inventory, shared, permissions, delegation, forwarding, audits, OWA activity
- Rules: external forwarding, mass mailbox-rule changes

### 5. SharePoint Online
- Collectors: site inventory, lists/libraries, drives, sharing permissions, sharing links, site activity
- Permission inheritance scanner (deep)
- Reports: site/owner/inactive/external/anonymous/broken-inheritance/orphaned/large lists
- Rules: anonymous-link creation, mass-download, mass-delete, external sharing spike

### 6. OneDrive
- Collectors: OneDrive accounts, storage, sharing, activity
- Reports: inventory, storage, external sharing, anonymous links, inactive accounts

### 7. Teams
- Collectors: teams, channels, members, owners, activity, device usage
- Reports: inventory, owners, guests, activity
- Rules: guest in private channel, team creation spike

### 8. Power BI & Compliance
- Collectors: Power BI activity (Activity log API where licensed), eDiscovery audit, DLP audit, EOP audit, Purview audit search
- Reports: feature-by-feature; many gated by license/role

### 9. Security operations
- Security dashboard
- Rule engine (DSL → SQL+OpenSearch query → match)
- Alert profiles, severities (Info/Attention/Trouble/Critical), suppression, dedup
- Investigation case workflow
- Entity profile pages
- Microsoft Graph Security API + Defender XDR advanced hunting integration
- Auto-remediation hooks (Phase 9, opt-in)

### 10. Content search
- Saved profiles, scheduled runs
- Regex/pattern, sensitive-info patterns
- Metadata-first results, raw content opt-in only
- Strict RBAC, legal/compliance gate
- Full audit trail

### 11. Report builder
- Source registry: tables, joined views, OpenSearch indices
- Column chooser, filter chips, date range, group-by, sort, search
- Saved views; scheduled delivery; CSV/XLSX/PDF/HTML
- Run history, ACL per report

### 12. Delegation / RBAC admin
- Role builder, scope builder, role import/export
- Built-in roles seeded read-only
- Technician activity logs

## Module lifecycle

- **Disabled**: present but feature flag off; navigation hidden.
- **Available**: flag on, permission scopes not yet granted by tenant. UI shows a "Connect" call-to-action.
- **Connected**: scopes granted, last-collection successful. Normal operation.
- **Degraded**: throttled, partial data, or downstream API outage. Banner + reduced-fidelity reports.

## Adding a new module (checklist for future contributors)

1. Create `apps/api/modules/<name>/manifest.py` with a `ModuleManifest` instance.
2. Add collectors under `apps/worker/modules/<name>/collectors/`.
3. Add API routes under `apps/api/modules/<name>/routes.py`.
4. Add report definitions under `apps/api/modules/<name>/reports/`.
5. Add rule definitions under `apps/api/modules/<name>/rules/`.
6. Update `docs/microsoft-graph/capability-matrix.md` and `required-permissions.md`.
7. Add Alembic migration for any new tables.
8. Add tests under `tests/unit/modules/<name>/`.
9. Update `ROADMAP.md` if the module changes the user-visible roadmap.
