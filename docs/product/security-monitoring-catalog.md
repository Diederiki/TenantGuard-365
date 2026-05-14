# Security monitoring catalog

## Alert sources

| Source | Status | Endpoint |
|---|---|---|
| Microsoft Graph security alerts | needs `SecurityEvents.Read.All` | `/security/alerts_v2` |
| Internal rule engine | **live** | `app/security/rules/*` |
| DLP alerts | needs Purview | Purview DLP audit |
| Defender Advanced Hunting | needs Defender licence | `/api/advancedhunting/run` |

The internal rule engine evaluates patterns against the data the
platform already collects — guest-user spikes, disabled-user activity,
anonymous SharePoint links, external mailbox forwarding, etc. Today 8
rules ship. Severity palette: `info / attention / trouble / critical`.

## Investigations

Cases live in `investigation_cases` + `investigation_case_events`.
Lifecycle:
1. Create case (manual or auto from a critical alert).
2. Link alerts.
3. Append events (analyst notes, evidence, decisions).
4. Resolve (false-positive / contained / escalated).

Audit log captures every transition.

## Content search

Profiles are pattern-based:
- Common-phrase library (SSN, NIN, IBAN, credit-card, etc.)
- Regex
- Free-text phrase
- Personal-information-phrase detection (Purview SITs)

Every run requires:
- Explicit reason captured in the audit log.
- RBAC permission `security.content_search.run`.
- Approval workflow if `feature_content_search_enabled = true` and the
  scope targets multiple mailboxes.

Output is **metadata-first**. Raw message bodies / file contents only
surface under the secure-mode role flag.

## Auto-remediation

Policies in `remediation_policies`. Every policy ships with:
- `enabled_by_default = false`
- `dry_run_default = true`
- `approval_required = true`

The platform refuses to execute any remediation handler in real mode
without all three flags being explicitly flipped by an operator. Today
5 policies ship (all disabled). Real execution arrives in Phase 3 behind
`FEATURE_REMEDIATION_ENABLED`.

## Monitoring

- Real-time alert dispatch (Phase 2) — alerts severity-routed via
  `notification_events`.
- Historical alert browsing — `/security/alerts` with DataGrid filters.
- Service health monitoring — `/service-health`, sourced from Microsoft.
- System health monitoring — `/system-health`, internal infrastructure
  status.

## Delegation

Security work supports the same RBAC + scoped-assignment model the rest
of the platform uses. A "Security Analyst" role is seeded with read
access to alerts/rules but not to remediation execution.
