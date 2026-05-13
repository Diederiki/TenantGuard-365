# RBAC

## Principles

1. **Server-enforced.** Every API route declares the permission(s) it requires via a dependency. Frontend hiding is cosmetic.
2. **Atomic permissions.** Permissions are strings like `sharepoint.sites.read`, never coarse roles.
3. **Scope-aware.** A role assignment can be scoped to tenant, domain, SharePoint site, department, or region.
4. **Least-privilege default.** New users default to `Read-only Auditor`.
5. **No silent escalations.** Role changes audit immediately and re-issue sessions.

## Permission namespace

```
platform.admin                       # full administrative access (rare)
platform.users.read
platform.users.manage
platform.roles.read
platform.roles.manage
platform.audit.read

tenants.connect                      # initiate Graph connection
tenants.disconnect
tenants.settings.read
tenants.settings.manage

entra.users.read
entra.groups.read
entra.signins.read
entra.audits.read
entra.licenses.read
entra.roles.read

exchange.mailboxes.read
exchange.mailbox_permissions.read
exchange.audits.read

sharepoint.sites.read
sharepoint.permissions.read
sharepoint.sharing_links.read
sharepoint.audits.read

onedrive.accounts.read
onedrive.audits.read

teams.read
teams.audits.read

security.alerts.read
security.alerts.assign
security.rules.read
security.rules.manage
security.investigations.read
security.investigations.manage

content_search.run
content_search.export
content_search.manage_profiles

reports.read
reports.run
reports.create
reports.export
reports.schedule

remediation.read
remediation.submit
remediation.approve
remediation.execute                  # only the worker has this, not given to users by default

audit.read                           # technician audit log read
audit.read.raw                       # raw payload + IP/UA — sensitive
```

## Built-in roles

| Role | Permissions (summary) | Default? |
|------|----------------------|----------|
| **Platform Admin** | Everything except `remediation.execute` (worker only) | No — assigned manually to operators |
| **Security Analyst** | Entra/Exchange/SharePoint/OneDrive/Teams `*.read`, `security.*` (read/manage), `content_search.run`, `reports.read/run`, `audit.read` | No |
| **SharePoint Auditor** | `sharepoint.*` read, `reports.read/run/export`, `audit.read` | No |
| **Exchange Auditor** | `exchange.*` read, `reports.read/run/export`, `audit.read` | No |
| **Helpdesk** | `entra.users.read`, `entra.groups.read`, `reports.read/run`, `audit.read` | No |
| **Read-only Auditor** | All `*.read` across modules, `reports.read/run/export`, `audit.read` | Yes — default for new users |
| **Report-only** | `reports.read/run/export` | No |

`remediation.execute` is reserved for the worker process identity. Even a Platform Admin can only `submit` and `approve` — the worker performs the actual call.

## Custom roles

- Built-in roles are seeded as read-only templates.
- A custom role is a named bundle of permissions, optionally scoped.
- Examples:
  - "EU SharePoint Auditor" — `sharepoint.*` read, scoped to sites whose region attribute = `EU`.
  - "Finance Mailbox Auditor" — `exchange.*` read, scoped to mailboxes whose department = `Finance`.

## Scope grammar

```
tenant:<tenant_uuid>
domain:<domain_name>
site:<sharepoint_site_id>
department:<department_string>
region:<region_string>
group:<entra_group_id>            # membership of this group bounds the scope
```

A role assignment may carry zero or more scopes; multiple scopes are OR'd. Empty scope = "no scope restriction".

## Enforcement implementation (Phase 2 plan)

```python
# apps/api/auth/permissions.py (illustrative)
def require(*permissions: str, scope_resolver: ScopeResolver | None = None):
    def dep(user: PlatformUser = Depends(current_user), request: Request = ...) -> None:
        granted = user.effective_permissions()
        for p in permissions:
            if p not in granted:
                raise HTTPException(403, detail=f"missing permission: {p}")
        if scope_resolver is not None:
            scope_resolver.assert_in_scope(user, request)
    return dep
```

Every route uses the dependency:

```python
@router.get("/sharepoint/sites")
def list_sites(_=Depends(require("sharepoint.sites.read", scope_resolver=site_scope))):
    ...
```

A linter (Phase 10) verifies that every route under `apps/api/modules/**` has at least one `require(...)`.

## Audit on RBAC

- Every role create / update / delete: `rbac.role.changed`
- Every assignment add / remove: `rbac.assignment.changed`
- Every failed permission check: `rbac.denied` (rate-limited)
- Every successful sensitive action (`remediation.approve`, `content_search.run`, `audit.read.raw`): logged with full context.
