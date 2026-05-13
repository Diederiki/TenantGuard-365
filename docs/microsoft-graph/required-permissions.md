# Required Microsoft permissions

> Consolidated list of every Entra app permission, directory role, and license the platform may request. Per-feature mapping lives in [capability-matrix.md](capability-matrix.md).
>
> When you grant admin consent for the platform's app registration, the *minimum viable* set for Phase 4 is shown first. Optional features add to the list; the platform's "Permission gap detector" (Phase 3) will tell you exactly which scopes are missing for a feature you want to enable.

## Minimum viable Phase 4 set (read-only)

**Microsoft Graph application permissions** (preferred for collectors):

| Scope | Purpose |
|-------|---------|
| `User.Read.All` | User inventory, license details |
| `Group.Read.All` | Group inventory |
| `GroupMember.Read.All` | Group membership |
| `RoleManagement.Read.Directory` | Roles + assignments |
| `Organization.Read.All` | Subscribed SKUs, tenant info |
| `Sites.Read.All` | SharePoint site / list / permission inventory |
| `Files.Read.All` | OneDrive / SharePoint drives + permissions |
| `MailboxSettings.Read` | Mailbox settings, inbox rules, forwarding visibility |
| `Reports.Read.All` | Usage reports (SharePoint/OneDrive/Teams/Exchange/AAD) |
| `ServiceHealth.Read.All` | Service health overviews + issues |
| `ServiceMessage.Read.All` | Service announcements |
| `Team.ReadBasic.All` | Teams inventory |
| `Channel.ReadBasic.All` | Channels |
| `TeamMember.Read.All` | Team members |
| `Application.Read.All` | App registrations + service principals |
| `AuditLog.Read.All` | Sign-ins, directory audits, Purview audit (license-gated) |

Total: 16 application permissions.

## Optional / module-gated permissions

Granted only when the corresponding feature is enabled in the platform:

| Scope | Feature module | Notes |
|-------|----------------|-------|
| `UserAuthenticationMethod.Read.All` | MFA reporting | License: Entra ID P1+ for tenant-wide views |
| `Policy.Read.All` | Conditional Access visibility | License: Entra ID P1+ |
| `IdentityRiskyUser.Read.All` | Risky users reporting | License: Entra ID P2 |
| `IdentityRiskEvent.Read.All` | Risk detections | License: Entra ID P2 |
| `Directory.Read.All` | OAuth consent grants | Read app consents |
| `SharePointTenantSettings.Read.All` | Tenant external sharing posture | Currently beta |
| `SecurityAlert.Read.All` | Security alerts v2 | – |
| `SecurityIncident.Read.All` | Incidents | Defender XDR |
| `ThreatHunting.Read.All` (beta) | Advanced hunting | Defender XDR / E5 Security |
| `eDiscovery.Read.All` | eDiscovery cases (read) | eDiscovery Premium |
| `eDiscovery.ReadWrite.All` | eDiscovery cases (manage) | eDiscovery Premium; only when the platform manages cases (Phase 9+) |

## Permissions for Phase 9 remediation (disabled by default)

These are **never granted by default**. Each is requested by a specific remediation policy, and the policy ships disabled.

| Scope | Used by remediation policy |
|-------|---------------------------|
| `User.EnableDisableAccount.All` | "Disable account" |
| `User.RevokeSessionsAll` | "Revoke sign-in sessions" |
| `Group.ReadWrite.All` | "Remove external guest from group" |
| `Sites.FullControl.All` | "Disable risky sharing link" (least-privilege variant: `Sites.Manage.All` if sufficient — validate) |
| `MailboxSettings.ReadWrite` | "Remove mailbox forwarding rule" |
| `Application.ReadWrite.All` | "Revoke consent for risky app" |

## Microsoft directory roles (assigned to the platform's app, not to scopes)

Some collectors only succeed when the service principal carries a directory role in addition to Graph scopes:

| Role | When required |
|------|---------------|
| **Global Reader** | Useful as a safety net during initial onboarding; not strictly required if scopes above are granted. |
| **Reports Reader** | Some usage reports honour role plus scope. |
| **Security Reader** | Required for Microsoft Graph Security read endpoints in some tenants. |
| **Audit Reader** (Purview) | Required for Purview Audit search where applicable. |
| **eDiscovery Manager** (Purview) | Required for eDiscovery features. |
| **SharePoint Administrator** | Required for tenant-wide SharePoint admin settings endpoints (beta). |

Avoid Global Administrator. The platform must never run as Global Admin.

## License dependencies

| Feature group | License required |
|---------------|------------------|
| Sign-in logs, Conditional Access read, stale-user signInActivity, MFA registration report | **Entra ID P1+** |
| Risky users, risk detections | **Entra ID P2** |
| Purview Audit search (Graph beta or Mgmt Activity API) | **Audit (Standard)**; longer retention + premium search needs **Audit Premium** |
| Defender XDR alerts/incidents | Defender for Office 365 P2 / Defender XDR |
| Advanced hunting | Defender XDR / E5 Security |
| eDiscovery (Premium) | eDiscovery Premium (E5/F5 Compliance) |
| Power BI activity log | Power BI Pro / PPU / Premium |

## Microsoft 365 / Office 365 Management Activity API (legacy)

For unified audit coverage where Graph beta or Purview Audit is not available:

- App permission: `ActivityFeed.Read`
- Webhook + pull architecture; **not** Graph.
- Used as a fallback. The capability matrix flags rows where this is the primary path.

## Exchange Online PowerShell (last resort)

Some mailbox features (mailbox permissions, send-as) still need EXO PowerShell. When ever used, it is run **only** by the worker, with certificate-based app-only authentication, isolated in its own queue, and audited.

See [docs/operations/runbooks.md](../operations/runbooks.md) for EXO certificate rotation procedure.

## Verifying granted permissions

After consent, verify with:

```bash
curl -fsS \
  -H "Authorization: Bearer $TOKEN" \
  "https://graph.microsoft.com/v1.0/servicePrincipals(appId='<APP_ID>')/appRoleAssignments"
```

The Phase 3 connection wizard will do this automatically and flag any missing scopes.
