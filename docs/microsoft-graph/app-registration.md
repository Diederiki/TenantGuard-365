# Entra app registration guide

> How to create the Entra ID application the platform uses to call Microsoft Graph.
> Read **all** of this before clicking around in the Entra portal.
>
> The Phase 3 in-app wizard automates most of this; this document is the source of truth.

## Two-app design

We use **two** app registrations:

1. **`tg365-portal`** — the *web sign-in* app. Delegated permissions only; users authenticate to the platform via Entra OIDC. No app-only access to tenant data.
2. **`tg365-collector`** — the *collector* app. Application permissions only; admin-consent-granted scopes for read-only collection. No interactive sign-in. Used by the worker.

This separation lets you revoke or rotate one without affecting the other.

## A. Create the portal app (`tg365-portal`)

1. Entra portal → **App registrations** → **New registration**.
2. Name: `tg365-portal`
3. Supported account types: **Single tenant**.
4. Redirect URI:
   - Web: `https://<your-public-host>/auth/callback`
   - Local dev: `http://localhost:8000/auth/callback`
5. Register.
6. **Authentication** blade:
   - Add platform → Web → both redirect URIs (prod + dev).
   - Implicit grant: leave both unchecked.
   - Allow public client flows: **No**.
   - Supported account types: **single tenant**.
7. **Certificates & secrets**:
   - Create a client secret with 6-month expiry (prefer certificate auth — see below).
   - Record the value in your secret store as `ENTRA_CLIENT_SECRET`.
8. **API permissions** (delegated only):
   - `openid`, `profile`, `email`, `offline_access` (Graph)
   - `User.Read` (Graph delegated — the signed-in user reading their own profile)
   - Grant admin consent.
9. **Token configuration**:
   - Add optional claim `email` (ID token).
   - Add optional claim `preferred_username` (ID token).
10. Note `Application (client) ID` and `Directory (tenant) ID`. Save as `ENTRA_CLIENT_ID` and `ENTRA_TENANT_ID`.

## B. Create the collector app (`tg365-collector`)

1. Entra portal → **App registrations** → **New registration**.
2. Name: `tg365-collector`
3. Supported account types: **Single tenant**.
4. Redirect URI: leave blank.
5. Register.
6. **API permissions** → **Application** (NOT delegated). Add the Phase 4 minimum set from [required-permissions.md](required-permissions.md#minimum-viable-phase-4-set-read-only):
   - `User.Read.All`
   - `Group.Read.All`
   - `GroupMember.Read.All`
   - `RoleManagement.Read.Directory`
   - `Organization.Read.All`
   - `Sites.Read.All`
   - `Files.Read.All`
   - `MailboxSettings.Read`
   - `Reports.Read.All`
   - `ServiceHealth.Read.All`
   - `ServiceMessage.Read.All`
   - `Team.ReadBasic.All`
   - `Channel.ReadBasic.All`
   - `TeamMember.Read.All`
   - `Application.Read.All`
   - `AuditLog.Read.All`
7. **Grant admin consent** for the tenant.
8. **Certificates & secrets**:
   - **Preferred:** upload a public certificate. Keep the private key in your platform's secret store. Set its expiry to 12 months and put the rotation date on your calendar.
   - Acceptable fallback: client secret with ≤ 6 months expiry.
9. Note the `Application (client) ID` and `Directory (tenant) ID`. Save as `COLLECTOR_CLIENT_ID`, `COLLECTOR_TENANT_ID`, and (depending on auth choice) `COLLECTOR_CLIENT_SECRET` or `COLLECTOR_CERT_THUMBPRINT` + `COLLECTOR_CERT_KEY_PATH`.

## C. (Optional) Assign directory roles to the collector service principal

Some endpoints honour directory roles in addition to scopes. Where required, assign **read-only** roles to the `tg365-collector` service principal:

- **Reports Reader** — for some Graph usage reports.
- **Security Reader** — for Graph Security read endpoints.
- **Audit Reader** (Purview) — for Purview Audit search.

**Do not** assign Global Administrator. Do not assign Global Reader unless you have a specific reason — the scopes above are sufficient for the bulk of collectors.

## D. Conditional Access scope for the platform

It is strongly recommended to scope a Conditional Access policy to **both** apps:

- Require trusted location or specific IP ranges (your office / VPN) for `tg365-portal` sign-in.
- Block legacy auth on both apps.
- Require sign-in frequency = 4 hours for portal users.
- Audit policy assignments quarterly.

## E. Storing secrets in the platform

Local dev:
- Put values in `.env`. **Never commit.**

Production:
- Use a secret store (Azure Key Vault, HashiCorp Vault, Doppler, AWS Secrets Manager). Mount as env vars at process start.
- The `TOKEN_CACHE_MASTER_KEY` must be different from the collector secret and rotated independently.

## F. Verifying the registration

After consent, run from the API container:

```bash
docker compose exec api python -m tg365.tools.verify_consent
```

(Phase 3 will ship this tool. Until then, see the `curl` example in [required-permissions.md](required-permissions.md#verifying-granted-permissions).)

The verifier compares granted `appRoleAssignments` against the platform's required set and prints a coloured gap report.

## G. Rotation runbook (summary)

Full procedure in [docs/operations/runbooks.md](../operations/runbooks.md).

- **30 days before expiry**: generate a new secret/cert as additional credential on the same app registration.
- **Cut over**: update secret store, restart the worker (rolling). Confirm collectors still succeed.
- **Revoke**: delete the old credential from the app registration.
- **Audit**: file the rotation in `technician_audit_logs` (`tenant.credential.rotated`).
