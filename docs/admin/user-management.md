# Admin guide — User management

This is the operator-facing guide for adding, removing, and configuring
platform users.

## Auth methods

A platform user picks **one** of three:

| Method | When to use | Required setup |
|---|---|---|
| **Entra SSO** (`auth_method=entra`) | Production. Single sign-on against the tenant directory. | `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_CLIENT_SECRET`, redirect URI on the app registration. |
| **Local password + TOTP** (`auth_method=local`) | Break-glass only. A single emergency admin who can sign in if Entra is down. | Password set via `POST /api/settings/users/{id}/password`. TOTP enrolled via `POST /api/settings/users/{id}/totp/enroll`. |
| **Mock** (`auth_method=mock`) | Local development only. | `AUTH_MODE=mock` and a non-production environment. |

The platform refuses to start when `ENVIRONMENT=production` and
`AUTH_MODE=mock`.

## Creating a user

```bash
curl -X POST $API/api/settings/users \
  -H 'Content-Type: application/json' \
  --cookie 'tg365_session=…' \
  -d '{
    "email": "alice@example.com",
    "display_name": "Alice Admin",
    "auth_method": "entra",
    "require_totp": false,
    "role_keys": ["platform_admin"]
  }'
```

For local + TOTP:

```bash
# 1. Create the user (require_totp=true marks the account as needing enrolment).
# 2. Set a password.
curl -X POST $API/api/settings/users/$ID/password \
  -d '{"password": "a-long-passphrase-12chars-min"}'

# 3. Enrol TOTP. Open the otpauth URI or scan the qr_svg_base64 from the response.
curl -X POST $API/api/settings/users/$ID/totp/enroll
```

The UI walks the operator through these steps under
**Settings → Platform users → New user → Enrol TOTP**.

## Disabling a user

Set `is_active=false` on the platform_users row. The session store
invalidates on next request. Entra users that are disabled upstream stop
working as soon as the OIDC callback re-fetches the directory.

## Roles

See `docs/admin/rbac.md`. Each user is one or more role assignments
scoped to: nothing (`""`), `tenant:<uuid>`, `site:<id>`, or
`department:<name>`.

## Audit

Every user-management action goes through `AuditLogger` and shows up at
`/audit` in the UI. Search by action: `settings.user.created`,
`settings.user.password.set`, `settings.user.totp.enrolled`,
`settings.user.totp.verified`.
