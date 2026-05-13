# Authentication model

## Identity providers

| Mode | When | Notes |
|------|------|-------|
| `AUTH_MODE=entra` | Production, staging | OIDC against Microsoft Entra ID. Only mode allowed in `ENVIRONMENT=production`. |
| `AUTH_MODE=mock` | Local dev | Fake users (`admin@dev.local`, `analyst@dev.local`). Refuses to start in production. |
| Break-glass local password | Disabled by default | Opt-in via `FEATURE_BREAKGLASS_LOCAL=true`. First sign-in requires WebAuthn or TOTP. Audited heavily; alerts on use. |

## OIDC flow (production)

1. User hits any protected route.
2. Web app (Next.js) detects no session → redirect to `/auth/login`.
3. API generates `state` + `nonce` + PKCE `code_verifier`; stores them in a short-lived signed cookie.
4. Redirect to `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize` with:
   - `client_id`
   - `response_type=code`
   - `scope=openid profile email offline_access User.Read`
   - `redirect_uri=https://<host>/auth/callback`
   - `code_challenge`, `code_challenge_method=S256`
   - `state`, `nonce`
5. User authenticates with Entra. Entra redirects back to `/auth/callback` with `code` and `state`.
6. API validates `state`, exchanges `code` for tokens using `code_verifier`.
7. API validates `id_token` (signature via JWKS, `iss`, `aud`, `nonce`, `exp`).
8. API matches the Entra `oid` to `platform_users.entra_object_id`. If not found and `auto_provision=true`, create a `platform_users` row with default role (Read-only Auditor by default — configurable).
9. API issues a session cookie. Refresh token stored in encrypted token cache.
10. Audit log: `auth.signin.success`.

## Sessions

- Cookie name: `tg365_session`
- `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`
- Server-side session record: id (HMAC of cookie value), user_id, issued_at, last_active_at, ip, user_agent, current_role_assignments_hash.
- **Idle timeout**: `SESSION_IDLE_TIMEOUT_MINUTES` (default 60).
- **Absolute timeout**: `SESSION_ABSOLUTE_TIMEOUT_HOURS` (default 12).
- Session is invalidated on:
  - Manual sign-out
  - Role change (re-issue required to reflect new RBAC scope)
  - Password / authentication-method change at Entra (via Continuous Access Evaluation hint, Phase 7)
  - Detected impossible-travel (Phase 7 rule)

## CSRF

- All state-changing endpoints (POST, PUT, PATCH, DELETE) require a CSRF header (`X-CSRF-Token`) whose value matches the value of the `tg365_csrf` cookie.
- The CSRF cookie is set on first GET; double-submit pattern.
- GraphQL is not used.

## API authentication (machine-to-machine — Phase 10+)

When other systems need to call this platform's API:

- Mint a short-lived JWT signed by the platform's signing key, with `aud=tg365-api`, `sub=<system_identity>`, scope claim restricting to specific permissions.
- Or use OAuth client-credentials backed by a service-principal record in `platform_users` (type=`system`).
- All M2M traffic audited with `actor.type=system`.

## Microsoft Graph token handling

Separate from user sessions. See [docs/microsoft-graph/app-registration.md](../microsoft-graph/app-registration.md).

- Application permissions (client credentials) for tenant-wide collectors.
- Delegated permissions only where a feature is intentionally user-scoped.
- Tokens stored in an encrypted cache (AES-GCM 256, master key from secret store).
- Refresh handled by the Graph client; renewal failures surface as Graph health degradation.
- Tokens never returned to the browser.
- Tokens never logged. Log scrubber asserts this at startup with a self-test.

## Cookie / header policy

| Header | Value |
|--------|-------|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` (prod only) |
| `Content-Security-Policy` | `default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self'; frame-ancestors 'none'` (refined in Phase 1) |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `same-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |
